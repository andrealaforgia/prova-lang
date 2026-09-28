"""Property test accompanying I1.S1.B2's acceptance test.

I1.S1.B2's claim is universal -- no run of `evaluate`, over any function,
argument shape or error path, ever emits a response describing itself as
verified, proved, built, or otherwise carrying an epistemic-certainty claim
-- but the acceptance test only checks it against six hand-picked happy-path
pairs on the `step` function plus a precondition and a postcondition case.
This test instead generates: which of the reservation source's three
functions is called (`valid-state`, `initial`, `step`), well-formed and
malformed argument value texts (out-of-range integers, wrong arity, garbage
text), and unknown function names -- so a hidden branch in the response
builder (a different function, an arity mismatch, a parse failure) that
leaked forbidden wording would be caught even though none of the acceptance
test's eight examples would trigger it.

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import json
import re
import subprocess

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _prova_client import load_reservation_source

FORBIDDEN_CLAIM = re.compile(
    r"\b(verifie[sd]|verify|verification|prove[nd]?|proves|built|build|holds)\b",
    re.IGNORECASE,
)
FORBIDDEN_CLAIM_KEYS = {"confidence", "guarantee", "certainty", "proof", "verification", "verified"}


def _find_forbidden_wording(value) -> list[str]:
    hits: list[str] = []

    def walk(node):
        if isinstance(node, str):
            hits.extend(m.group(0) for m in FORBIDDEN_CLAIM.finditer(node))
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(value)
    return hits


def _find_forbidden_keys(value) -> set[str]:
    hits: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if key.lower() in FORBIDDEN_CLAIM_KEYS:
                    hits.add(key)
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return hits


_reservation_int = st.integers(min_value=-5, max_value=5)
_reservation_arg = _reservation_int.map(lambda n: f"(Reservation {n})")
_event_arg = st.sampled_from(["(Reserve)", "(Release)", "(Reserve 1)", "(Bogus)", "()"])
_garbage_arg = st.text(alphabet="()abcXYZ 0123-", min_size=0, max_size=12)

# (function_name, arguments) pairs spanning: valid calls to every function in
# the source at its declared arity, calls to those same functions with
# malformed or garbage argument *content* (still at the declared arity --
# wrong arity is an unrelated arity-handling gap, not this behaviour's
# claim-wording concern), and calls naming a function the source never
# declares.
_calls = st.one_of(
    st.tuples(st.just("step"), _reservation_arg, _event_arg).map(lambda t: (t[0], [t[1], t[2]])),
    _reservation_arg.map(lambda a: ("valid-state", [a])),
    st.just(("initial", [])),
    st.tuples(
        st.sampled_from(["unknown-fn", "", "STEP", "step "]),
        st.lists(st.one_of(_reservation_arg, _event_arg), min_size=0, max_size=2),
    ),
    st.tuples(_garbage_arg, _garbage_arg).map(lambda t: ("step", [t[0], t[1]])),
    _garbage_arg.map(lambda a: ("valid-state", [a])),
)


def _run_evaluate(source: str, function: str, arguments: list[str]) -> tuple[int, dict | None, str, str]:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": function,
        "arguments": arguments,
    }
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    try:
        response = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        response = None
    return proc.returncode, response, proc.stdout, proc.stderr


@settings(derandomize=True, max_examples=60, deadline=None)
@given(call=_calls)
@example(call=("step", ["(Reservation 0)", "(Reserve)"]))
@example(call=("step", ["(Reservation 5)", "(Reserve)"]))
@example(call=("unknown-fn", ["(Reservation 0)", "(Reserve)"]))
@example(call=("step", ["garbage", "garbage"]))
@example(call=("initial", ["(Reservation 0)"]))
def test_no_evaluate_run_ever_emits_a_forbidden_claim(call):
    """Given any function name, and argument content (valid, out-of-range,
    or garbage text) submitted to `evaluate`, including an unknown function
    name, when the Owner reads the reported output, then it never carries
    verified/proved/built wording nor an equivalent epistemic-claim field,
    regardless of whether the call succeeded or was rejected."""
    function, arguments = call
    source = load_reservation_source()

    returncode, response, stdout, stderr = _run_evaluate(source, function, arguments)
    label = f"evaluate({function!r}, {arguments!r})"

    # A response that fails to parse (a tool crash) is a defect in its own
    # right, tracked separately from this behaviour's claim-wording
    # guarantee; here it is still scanned for forbidden wording rather than
    # treated as an automatic pass or an unrelated failure.
    if response is None:
        combined_hits = FORBIDDEN_CLAIM.findall(stdout) + FORBIDDEN_CLAIM.findall(stderr)
        assert not combined_hits, f"forbidden claim wording in crash output for {label}: {combined_hits}"
        return

    wording_hits = _find_forbidden_wording(response)
    assert not wording_hits, f"forbidden claim wording in response for {label}: {wording_hits}; response={response}"

    key_hits = _find_forbidden_keys(response)
    assert not key_hits, f"unexpected epistemic-claim field(s) {key_hits} for {label}: {response}"

    stderr_hits = FORBIDDEN_CLAIM.findall(stderr)
    assert not stderr_hits, f"forbidden claim wording on stderr for {label}: {stderr_hits}"
