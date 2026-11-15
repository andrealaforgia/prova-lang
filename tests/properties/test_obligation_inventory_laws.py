"""Laws the obligation inventory obeys for any program, not only the two
examples this repository ships.

Each program is built from a plan written here first -- how many functions,
which contracts each declares, how many examples, and where each call sits.
The plan is the oracle: it says which obligations are owed and under which
condition, independently of how the tool works them out.

LAW1 every function owes one contract-definedness, one body-to-postcondition
     and one structural-termination entry, every declared example owes a
     validity entry, and every call owes a precondition entry. The
     structural-termination entry counts the calls that function makes.
LAW2 no obligation is ever reported as anything but `not_attempted`, the
     counts partition the list, and no word in the answer reports work done.
LAW3 the same source always owes exactly the same list, in the same order.
LAW4 putting a call behind a condition that can never hold keeps the
     obligation and changes only the condition reported for it.

Drives the `prova` command over its JSON stdin/stdout surface, as the other
property tests here do. No imports from src/prova.
"""

from __future__ import annotations

import dataclasses
import json
import re
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

CLAIM_WORD = re.compile(
    r"\b(verified|verifies|verification|proved|proven|proves|proof|"
    r"discharged|guaranteed|sound|correct|holds|built)\b",
    re.IGNORECASE,
)

PER_FUNCTION_KINDS = ("contract_definedness", "body_postcondition", "structural_termination")

# Where a call sits in each body shape, and the condition that reaches it
# there. `None` means the shape places no call at all. Every position a
# core-0 body can put a call in appears here, so a position that stopped
# being walked would take its obligation out of the answer.
BODY_SHAPES = {
    "plain": None,
    "call": ("body", "true"),
    "unreachable": ("body/then", "false"),
    "guarded": ("body/then", "(> n 0)"),
    "else-arm": ("body/else", "(not (> n 0))"),
    "matched": ("body/case[0]", "(matches (> n 0) true)"),
    "scrutinee": ("body/scrutinee", "true"),
    "let-bound": ("body/bind[0]", "true"),
    "if-condition": ("body/cond/arg[0]", "true"),
    "field-target": ("body/target/arg[0]", "true"),
}

# The record the `field-target` shape reads a field of. Declared only by the
# programs that need it, so every other generated program is unchanged.
POINT_DECLARATION = "(deftype Point (record (x Int)))"

# One function per body shape, in a single program, so that every call
# position is exercised whatever the generator happens to draw.
EVERY_BODY_SHAPE = ("plain",) + tuple(
    shape for shape in sorted(BODY_SHAPES) if BODY_SHAPES[shape] is not None
)


@dataclasses.dataclass(frozen=True)
class FunctionPlan:
    """One function of a generated program: what it declares and where it
    calls the function declared before it."""

    requires: str  # "none", "plain", or "call"
    declares_postcondition: bool
    example_count: int
    body_shape: str

    def settled(self, is_first: bool) -> "FunctionPlan":
        """The same plan with every call removed when there is no earlier
        function to call."""
        if not is_first:
            return self
        return dataclasses.replace(
            self,
            requires="plain" if self.requires == "call" else self.requires,
            body_shape="plain" if BODY_SHAPES[self.body_shape] else self.body_shape,
        )


_plans = st.lists(
    st.builds(
        FunctionPlan,
        requires=st.sampled_from(["none", "plain", "call"]),
        declares_postcondition=st.booleans(),
        example_count=st.integers(min_value=1, max_value=3),
        body_shape=st.sampled_from(sorted(BODY_SHAPES)),
    ),
    min_size=1,
    max_size=3,
).map(lambda plans: tuple(plan.settled(index == 0) for index, plan in enumerate(plans)))

_plans_with_a_call = st.lists(
    st.builds(
        FunctionPlan,
        requires=st.sampled_from(["none", "plain"]),
        declares_postcondition=st.booleans(),
        example_count=st.integers(min_value=1, max_value=2),
        body_shape=st.just("plain"),
    ),
    min_size=2,
    max_size=2,
)


def _name(index: int) -> str:
    return f"f{index}"


def _body_text(plan: FunctionPlan, index: int) -> str:
    called = _name(index - 1)
    return {
        "plain": "n",
        "call": f"({called} n)",
        "unreachable": f"(if false ({called} n) n)",
        "guarded": f"(if (> n 0) ({called} n) n)",
        "else-arm": f"(if (> n 0) n ({called} n))",
        "matched": f"(match (> n 0)\n    (true ({called} n))\n    (false n))",
        "scrutinee": f"(match ({called} n)\n    (0 n)\n    (_ n))",
        "let-bound": f"(let ((m ({called} n))) m)",
        "if-condition": f"(if (> ({called} n) 0) n n)",
        "field-target": f"(.x (Point ({called} n)))",
    }[plan.body_shape]


def render_program(plans: tuple[FunctionPlan, ...]) -> str:
    """The source text of the program the plan describes."""
    blocks = []
    if any(plan.body_shape == "field-target" for plan in plans):
        blocks.append(POINT_DECLARATION)
    for index, plan in enumerate(plans):
        name = _name(index)
        lines = [f"(defn {name}", "  (sig ((n Int)) -> Int ! pure)"]
        if plan.requires == "plain":
            lines.append("  (requires (> n 0))")
        elif plan.requires == "call":
            lines.append(f"  (requires (> ({_name(index - 1)} n) 0))")
        if plan.declares_postcondition:
            lines.append("  (ensures (>= result 0))")
        examples = " ".join(
            f"(example ({name} {ordinal + 1}) => 0)" for ordinal in range(plan.example_count)
        )
        lines.append(f"  (examples {examples})")
        lines.append(f"  {_body_text(plan, index)})")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"


def owed_identities(plans: tuple[FunctionPlan, ...]) -> set[str]:
    """Every obligation the plan says the program owes, by identity."""
    owed = set()
    for index, plan in enumerate(plans):
        name = _name(index)
        owed.add(f"contract_definedness:{name}:contract")
        owed.add(f"body_postcondition:{name}:body")
        owed.add(f"structural_termination:{name}:calls")
        for ordinal in range(plan.example_count):
            owed.add(f"example_validity:{name}:example[{ordinal}]")
        if plan.requires == "call":
            owed.add(f"call_precondition:{name}:requires[0]/arg[0]")
        placed = BODY_SHAPES[plan.body_shape]
        if placed is not None:
            owed.add(f"call_precondition:{name}:{placed[0]}")
    return owed


def owed_direct_calls(plans: tuple[FunctionPlan, ...]) -> dict[str, int]:
    """How many calls the plan says each function makes, by function name."""
    counted = {}
    for index, plan in enumerate(plans):
        made = 1 if plan.requires == "call" else 0
        if BODY_SHAPES[plan.body_shape] is not None:
            made += 1
        counted[_name(index)] = made
    return counted


def owed_precondition_clauses(plan: FunctionPlan, index: int) -> tuple[str, ...]:
    """The clauses of the function's own precondition, as the plan writes
    them. A call in the body is reached only when they hold: the body
    answers the postcondition for every input that meets the precondition
    (SPEC.md, "Meaning of a claim"). A call in the precondition itself is
    not: a precondition must be defined for every typed input and cannot
    assume itself true."""
    if plan.requires == "plain":
        return ("(> n 0)",)
    if plan.requires == "call":
        return (f"(> ({_name(index - 1)} n) 0)",)
    return ()


def joined(clauses: tuple[str, ...]) -> str:
    """The clauses as the one condition the answer reports."""
    if not clauses:
        return "true"
    if len(clauses) == 1:
        return clauses[0]
    return "(and " + " ".join(clauses) + ")"


def owed_call_conditions(plans: tuple[FunctionPlan, ...]) -> dict[str, str]:
    """The condition the plan says reaches each call, by obligation identity."""
    conditions = {}
    for index, plan in enumerate(plans):
        name = _name(index)
        if plan.requires == "call":
            conditions[f"call_precondition:{name}:requires[0]/arg[0]"] = "true"
        placed = BODY_SHAPES[plan.body_shape]
        if placed is not None:
            site, condition = placed
            reached = owed_precondition_clauses(plan, index) + (
                () if condition == "true" else (condition,)
            )
            conditions[f"call_precondition:{name}:{site}"] = joined(reached)
    return conditions


def ask_what_is_owed(source: str) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"prova": "i1", "operation": "verify", "source": source}),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON answer: {proc.stdout!r}")


def _obligations(response: dict, source: str) -> list[dict]:
    assert response.get("status") == "completed", (
        f"WHAT: the program was answered with {response.get('status')!r} instead of an "
        f"inventory. WHY: it reads and checks, so the Owner is owed the list. "
        f"HOW: the program was:\n{source}\nthe answer was: {response}"
    )
    return response["result"]["inventory"]["obligations"]


def _claim_words(value) -> list[str]:
    hits: list[str] = []

    def walk(node):
        if isinstance(node, str):
            hits.extend(match.group(0) for match in CLAIM_WORD.finditer(node))
        elif isinstance(node, dict):
            for key, child in node.items():
                walk(key)
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return hits


@settings(derandomize=True, max_examples=25, deadline=None)
@given(plans=_plans)
def test_every_function_example_and_call_owes_its_entry(plans):
    """LAW1. Given any program, when the Owner asks what must be shown, then
    the answer owes exactly what the program declares: one contract, body
    and ending entry per function, one entry per declared example, and one
    per call under the condition that reaches it."""
    source = render_program(plans)
    entries = _obligations(ask_what_is_owed(source), source)

    identities = [entry["id"] for entry in entries]
    assert sorted(identities) == sorted(set(identities)), (
        f"WHAT: {len(identities) - len(set(identities))} identities repeat. "
        "WHY: one identity names one obligation. "
        f"HOW: the program was:\n{source}\nidentities: {sorted(identities)}"
    )
    expected = owed_identities(plans)
    assert set(identities) == expected, (
        f"WHAT: missing {sorted(expected - set(identities))}, unexpected "
        f"{sorted(set(identities) - expected)}. "
        "WHY: every declaration, example and call of the program owes its entry, and "
        "nothing else is owed. "
        f"HOW: the program was:\n{source}"
    )

    reported = {
        entry["id"]: entry["path_condition"]
        for entry in entries
        if entry["kind"] == "call_precondition"
    }
    assert reported == owed_call_conditions(plans), (
        f"WHAT: the conditions reaching the calls are {reported}, not "
        f"{owed_call_conditions(plans)}. "
        "WHY: a call's obligation is owed under the condition that reaches it. "
        f"HOW: the program was:\n{source}"
    )
    counted = {
        entry["function"]: entry["direct_calls"]
        for entry in entries
        if entry["kind"] == "structural_termination"
    }
    assert counted == owed_direct_calls(plans), (
        f"WHAT: the ending entries say the functions make {counted} calls, not "
        f"{owed_direct_calls(plans)}. "
        "WHY: a function ends because the calls it makes are acyclic, so the entry "
        "must count the calls the program actually writes. "
        f"HOW: the program was:\n{source}"
    )
    for kind in PER_FUNCTION_KINDS:
        owners = [entry["function"] for entry in entries if entry["kind"] == kind]
        assert sorted(owners) == sorted(_name(i) for i in range(len(plans))), (
            f"WHAT: {kind} is owed by {sorted(owners)}. "
            f"WHY: each of the {len(plans)} functions owes it exactly once, whether or "
            "not it declares a contract. "
            f"HOW: the program was:\n{source}"
        )


def test_a_call_in_every_position_a_body_can_hold_owes_its_entry():
    """LAW1, every position at once. Given one program that puts a call in
    each position a body can hold -- both arms of an `if` and its condition,
    a let binding, a match scrutinee, a match clause and the target of a
    field read -- when the Owner asks what must be shown, then every one of
    those calls owes its own entry under the condition that reaches it, and
    the program owes nothing else.

    The generator above draws these shapes too, but it draws only some of
    them in any one run; this program holds all of them at once, so a
    position the tool stopped walking cannot slip through unseen.

    still passes if: the tool reported only the first call it found inside a
    function -- every function here makes at most one call. The program in
    tests/acceptance/test_verify_lists_the_obligations_owed.py that makes
    four calls from one function closes that.
    """
    plans = tuple(
        FunctionPlan(
            requires="none",
            declares_postcondition=False,
            example_count=1,
            body_shape=shape,
        )
        for shape in EVERY_BODY_SHAPE
    )
    source = render_program(plans)
    entries = _obligations(ask_what_is_owed(source), source)

    identities = {entry["id"] for entry in entries}
    expected = owed_identities(plans)
    assert identities == expected, (
        f"WHAT: missing {sorted(expected - identities)}, unexpected "
        f"{sorted(identities - expected)}. "
        "WHY: a call owes its precondition entry wherever in the body it sits; a "
        "position that is not walked drops real work out of the list. "
        f"HOW: the program was:\n{source}"
    )

    reported = {
        entry["id"]: entry["path_condition"]
        for entry in entries
        if entry["kind"] == "call_precondition"
    }
    assert reported == owed_call_conditions(plans), (
        f"WHAT: the conditions reaching the calls are {reported}, not "
        f"{owed_call_conditions(plans)}. "
        "WHY: each of these calls is reached under the condition its own position "
        "puts in front of it. "
        f"HOW: the program was:\n{source}"
    )

    counted = {
        entry["function"]: entry["direct_calls"]
        for entry in entries
        if entry["kind"] == "structural_termination"
    }
    assert counted == owed_direct_calls(plans), (
        f"WHAT: the ending entries say the functions make {counted} calls, not "
        f"{owed_direct_calls(plans)}. "
        "WHY: a call in a condition, a binding or a scrutinee is as much a call as "
        "one in a branch. "
        f"HOW: the program was:\n{source}"
    )


@settings(derandomize=True, max_examples=25, deadline=None)
@given(plans=_plans)
def test_no_obligation_is_ever_answered_as_attempted(plans):
    """LAW2. Given any program, when the Owner reads the answer, then every
    obligation is `not_attempted`, the counts add up to the list, and no
    word in the answer reports work the tool did not do."""
    source = render_program(plans)
    response = ask_what_is_owed(source)
    entries = _obligations(response, source)
    inventory = response["result"]["inventory"]

    results = {entry["result"] for entry in entries}
    assert results == {"not_attempted"}, (
        f"WHAT: obligations are reported as {sorted(results)}. "
        "WHY: nothing ran, and a check that never ran is `not_attempted`. "
        f"HOW: the program was:\n{source}"
    )

    totals = inventory["totals"]
    assert totals["obligations"] == len(entries), (totals, len(entries), source)
    assert totals["attempted"] == 0, (totals, source)
    assert totals["attempted"] + totals["not_attempted"] == len(entries), (totals, source)
    assert sum(totals["by_kind"].values()) == len(entries), (
        f"WHAT: the per-kind counts {totals['by_kind']} do not add up to the "
        f"{len(entries)} obligations listed. "
        "WHY: every obligation falls under exactly one kind. "
        f"HOW: the program was:\n{source}"
    )

    hits = _claim_words(response)
    assert not hits, (
        f"WHAT: the answer contains {sorted(set(hits))}. "
        "WHY: no obligation was attempted, so the answer may report no outcome. "
        f"HOW: the program was:\n{source}\nthe answer was: {response}"
    )


@settings(derandomize=True, max_examples=15, deadline=None)
@given(plans=_plans)
def test_the_same_program_always_owes_the_same_list(plans):
    """LAW3. Given any program asked about twice, when the Owner compares
    the two answers, then they list the same obligations with the same
    identities in the same order."""
    source = render_program(plans)
    first = ask_what_is_owed(source)["result"]
    second = ask_what_is_owed(source)["result"]

    assert first == second, (
        "WHAT: two answers about the same program differ. "
        "WHY: the Owner compares answers to see real change; drift makes that useless. "
        f"HOW: the program was:\n{source}\nfirst={first}\nsecond={second}"
    )


@settings(derandomize=True, max_examples=15, deadline=None)
@given(plans=_plans_with_a_call)
def test_putting_a_call_out_of_reach_keeps_what_it_owes(plans):
    """LAW4. Given a program whose call is moved into a branch that can
    never be taken, when the Owner asks what must be shown, then the same
    obligation is still owed and only the condition reaching it changes."""
    reachable = tuple(
        dataclasses.replace(plan, body_shape="call" if index else "plain")
        for index, plan in enumerate(plans)
    )
    out_of_reach = tuple(
        dataclasses.replace(plan, body_shape="unreachable" if index else "plain")
        for index, plan in enumerate(plans)
    )

    before_source, after_source = render_program(reachable), render_program(out_of_reach)
    before = _obligations(ask_what_is_owed(before_source), before_source)
    after = _obligations(ask_what_is_owed(after_source), after_source)

    assert len(before) == len(after), (
        f"WHAT: the program owes {len(before)} obligations while the call can run and "
        f"{len(after)} once it cannot. "
        "WHY: an unreachable path can make an obligation vacuous; it does not remove it. "
        f"HOW: the programs were:\n{before_source}\n---\n{after_source}"
    )
    called_before = [e for e in before if e["kind"] == "call_precondition"]
    called_after = [e for e in after if e["kind"] == "call_precondition"]
    assert len(called_before) == len(called_after) == 1, (called_before, called_after)
    assert called_before[0]["callee"] == called_after[0]["callee"] == _name(0), (
        called_before,
        called_after,
    )
    seeded = owed_precondition_clauses(reachable[1], 1)
    assert called_before[0]["path_condition"] == joined(seeded), called_before
    assert called_after[0]["path_condition"] == joined(seeded + ("false",)), (
        f"WHAT: the call that can never run is reported as reached under "
        f"{called_after[0]['path_condition']!r}. "
        "WHY: the obligation is owed under the condition that reaches it, and here that "
        "condition never holds. "
        f"HOW: the program was:\n{after_source}"
    )
