"""Independent, structure-aware oracle for I1.S4 (version 4 questions).

Not a test module. Contains a small s-expression reader and a mini-evaluator
for the `core-0` subset the reservation source uses. It shares nothing with
`src/prova`; it lets tests locate `step`'s body structurally, derive each
submitted body's result over the six valid inputs, and evaluate `step`'s
three `ensures` clauses on those results from the *submitted* text, rather
than from a helper labelled with the mutation's name.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field

from _i1_s4_fixtures import COUNTS, EVENTS, MUTANTS, evaluate_step, mutated_source, protected_source
from _prova_client import SPEC_ORACLE_SHA, run_prova

ALL_SIX = [(count, event) for count in COUNTS for event in EVENTS]

# Independently transcribed, pinned six-row table from SPEC.md (Before, Event,
# After, Accepted). Not derived from any fixture or tool output.
PINNED_TABLE = {
    (0, "Reserve"): (1, True),
    (1, "Reserve"): (2, True),
    (2, "Reserve"): (2, False),
    (0, "Release"): (0, False),
    (1, "Release"): (0, True),
    (2, "Release"): (1, True),
}
ACCEPTED_ROWS = [k for k, v in PINNED_TABLE.items() if v[1]]
REJECTED_ROWS = [k for k, v in PINNED_TABLE.items() if not v[1]]
assert len(PINNED_TABLE) == 6 and len(ACCEPTED_ROWS) == 4 and len(REJECTED_ROWS) == 2


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- reader

def read_forms(text: str) -> list:
    tokens = re.findall(r"\(|\)|;[^\n]*|[^\s()]+", text)
    tokens = [t for t in tokens if not t.startswith(";")]
    pos = 0

    def one():
        nonlocal pos
        tok = tokens[pos]
        pos += 1
        if tok == "(":
            items = []
            while tokens[pos] != ")":
                items.append(one())
            pos += 1
            return items
        assert tok != ")", "unbalanced source"
        return tok

    forms = []
    while pos < len(tokens):
        forms.append(one())
    return forms


def top_forms_by_name(forms: list) -> dict:
    return {f[1]: f for f in forms}


def step_form(forms: list) -> list:
    steps = [f for f in forms if isinstance(f, list) and f[:2] == ["defn", "step"]]
    assert len(steps) == 1, f"expected exactly one step declaration, found {len(steps)}"
    return steps[0]


def step_body(forms: list):
    return step_form(forms)[-1]


def non_body_nodes(forms: list) -> list:
    """Every top-level node with step's final (body) element removed."""
    out = []
    for form in forms:
        if isinstance(form, list) and form[:2] == ["defn", "step"]:
            out.append(form[:-1])
        else:
            out.append(form)
    return out


def changed_nodes(reference: list, candidate: list) -> list[str]:
    """Names of top-level forms (and 'step-body') whose trees differ."""
    diffs = []
    if len(reference) != len(candidate):
        return ["top-level-form-count"]
    for ref, cand in zip(reference, candidate):
        if ref == cand:
            continue
        is_step = isinstance(ref, list) and ref[:2] == ["defn", "step"]
        if is_step and ref[:-1] == cand[:-1]:
            diffs.append("step-body")
        else:
            diffs.append(f"other:{ref[1] if len(ref) > 1 else ref}")
    return diffs


# ------------------------------------------------------------- evaluator

class Interp:
    def __init__(self, forms: list):
        self.funcs = {}
        self.ctors = {}
        self.fields = {}
        for form in forms:
            if form[0] == "deftype":
                self._declare(form)
            elif form[0] == "defn":
                self.funcs[form[1]] = form

    def _declare(self, form):
        kind = form[2]
        if kind[0] == "record":
            name = form[1]
            self.ctors[name] = len(kind) - 1
            for idx, (fname, _ftype) in enumerate(kind[1:]):
                self.fields[fname] = idx
        elif kind[0] == "union":
            for variant in kind[1:]:
                self.ctors[variant[0]] = len(variant) - 1

    def ev(self, node, env):
        if isinstance(node, str):
            if node == "true":
                return True
            if node == "false":
                return False
            if re.fullmatch(r"[+-]?\d+", node):
                return int(node)
            return env[node]
        head, *args = node
        if head == "match":
            scrutinee = self.ev(args[0], env)
            for pattern, body in args[1:]:
                if pattern[0] == scrutinee[0]:
                    return self.ev(body, env)
            raise AssertionError(f"non-exhaustive match on {scrutinee}")
        if head == "if":
            return self.ev(args[1] if self.ev(args[0], env) else args[2], env)
        if head == "and":
            return all(self.ev(a, env) for a in args)
        if head.startswith("."):
            return self.ev(args[0], env)[1 + self.fields[head[1:]]]
        if head in self.ctors:
            return (head, *[self.ev(a, env) for a in args])
        vals = [self.ev(a, env) for a in args]
        if head == "<":
            return vals[0] < vals[1]
        if head == ">":
            return vals[0] > vals[1]
        if head == "<=":
            return vals[0] <= vals[1]
        if head == ">=":
            return vals[0] >= vals[1]
        if head == "=":
            return vals[0] == vals[1]
        if head == "+":
            return sum(vals)
        if head == "-":
            return vals[0] - vals[1]
        if head in self.funcs:
            return self.call(head, vals)
        raise AssertionError(f"unsupported form {head!r}")

    def call(self, name, values):
        fn = self.funcs[name]
        params = [p[0] for p in fn[2][1]]
        return self.ev(fn[-1], dict(zip(params, values)))

    def ensures(self, name):
        for clause in self.funcs[name]:
            if isinstance(clause, list) and clause and clause[0] == "ensures":
                return clause[1:]
        return []

    def step_verdict(self, count: int, event: str) -> "Derivation":
        current, ev = ("Reservation", count), (event,)
        result = self.call("step", [current, ev])
        env = {"current": current, "event": ev, "result": result}
        clauses = [self.ev(c, env) for c in self.ensures("step")]
        assert len(clauses) == 3, "step must carry exactly three postcondition clauses"
        return Derivation(count, event, result[1][1], result[2], clauses)


@dataclass
class Derivation:
    count: int
    event: str
    result_count: int
    accepted: bool
    clauses: list

    @property
    def postcondition_holds(self) -> bool:
        return all(self.clauses)

    @property
    def invariant_holds(self) -> bool:
        return self.clauses[0]

    @property
    def outcome(self):
        return (self.result_count, self.accepted)


def derive_all(source: str) -> dict:
    interp = Interp(read_forms(source))
    return {(c, e): interp.step_verdict(c, e) for c, e in ALL_SIX}


# -------------------------------------------------------------- campaign

@dataclass
class Call:
    label: str
    source_id: str
    source_digest: str
    count: int
    event: str
    request: dict
    returncode: int
    response: dict | None
    stdout: str
    stderr: str


def sources() -> dict:
    out = {"protected": protected_source()}
    for m in MUTANTS:
        out[m.id] = mutated_source(m)
    return out


def call(label: str, source_id: str, source: str, count: int, event: str) -> Call:
    request = {
        "prova": "i1", "operation": "evaluate", "source": source, "function": "step",
        "arguments": [f"(Reservation {count})", f"({event})"],
    }
    rc, resp, out, err = run_prova(request)
    return Call(label, source_id, sha256(source), count, event, request, rc, resp, out, err)


def run_campaign() -> list[Call]:
    """Control battery, all three mutation batteries, control battery again."""
    srcs = sources()
    calls: list[Call] = []
    for phase in ("before",):
        for c, e in ALL_SIX:
            calls.append(call(f"control-{phase}", "protected", srcs["protected"], c, e))
    for m in MUTANTS:
        for c, e in ALL_SIX:
            calls.append(call("mutant", m.id, srcs[m.id], c, e))
    for c, e in ALL_SIX:
        calls.append(call("control-after", "protected", srcs["protected"], c, e))
    return calls


_CACHE: list[Call] | None = None


def campaign() -> list[Call]:
    global _CACHE
    if _CACHE is None:
        _CACHE = run_campaign()
    return _CACHE


def select(label: str | None = None, source_id: str | None = None) -> list[Call]:
    return [c for c in campaign()
            if (label is None or c.label == label) and (source_id is None or c.source_id == source_id)]


# ------------------------------------------------------------- assertions

def categories(resp: dict) -> list[str]:
    return [d.get("category") for d in (resp.get("diagnostics") or [])]


def assert_runtime_postcondition_violation(c: Call) -> None:
    where = f"{c.source_id} at ({c.count}, {c.event})"
    assert c.returncode == 0, f"tool failure at {where}: {c.stderr!r}"
    assert c.response is not None, f"unparseable response at {where}: {c.stdout!r}"
    r = c.response
    assert r.get("operation") == "evaluate", f"wrong operation at {where}: {r}"
    assert r.get("status") == "completed", f"not a completed evaluation at {where}: {r}"
    assert r.get("source_digest") == c.source_digest, f"response is not bound to the submitted source at {where}"
    assert "result" not in r or not r["result"], f"successful result reported at {where}: {r}"
    assert categories(r) == ["postcondition_violation"], (
        f"expected exactly one postcondition_violation at {where}, got {categories(r)}: {r}"
    )
    reason = r["diagnostics"][0].get("reason", "")
    assert "step" in reason, f"diagnostic does not attribute the violation to step at {where}: {reason!r}"


def assert_success_with_outcome(c: Call, expected: tuple[int, bool]) -> None:
    from _prova_client import parse_value

    where = f"{c.source_id} at ({c.count}, {c.event})"
    assert c.returncode == 0, f"tool failure at {where}: {c.stderr!r}"
    assert c.response is not None, f"unparseable response at {where}: {c.stdout!r}"
    r = c.response
    assert r.get("status") == "completed" and categories(r) == [], f"not a clean success at {where}: {r}"
    assert r.get("source_digest") == c.source_digest, f"response is not bound to the submitted source at {where}"
    assert (r.get("claim") or {}).get("kind") == "evaluation", f"claim kind at {where}: {r.get('claim')}"
    ctor, (state, accepted) = parse_value(r["result"]["value"])
    assert ctor == "Outcome" and state[0] == "Reservation" and isinstance(accepted, bool)
    assert (state[1][0], accepted) == expected, f"wrong outcome at {where}: {r['result']}"
