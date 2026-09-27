"""I1.S6.P7 / I1.S6.CHAR1: the candidate preserves every protected
reservation transition and declared example, including both the returned
reservation count and accepted flag, while retaining the invariant that
every valid transition returns a count between zero and two.

Hand-derived independently of I1.S3's own six-row table and of the
mutation matrix used elsewhere: (before, event, after, accepted). Exercises
both (1, Reserve) and (2, Release), which the declared step examples omit.
"""

from __future__ import annotations

import pytest

from _i1_s6_fixtures import load_reservation_source, parse_value, run_prova

TRANSITIONS = [
    (0, "Reserve", 1, True),
    (1, "Reserve", 2, True),
    (2, "Reserve", 2, False),
    (0, "Release", 0, False),
    (1, "Release", 0, True),
    (2, "Release", 1, True),
]

DECLARED_EXAMPLES = [
    {"function": "valid-state", "arguments": ["(Reservation 0)"], "expected": True},
    {"function": "valid-state", "arguments": ["(Reservation 3)"], "expected": False},
    {"function": "initial", "arguments": [], "expected": ("Reservation", (0,))},
    {
        "function": "step",
        "arguments": ["(Reservation 0)", "(Reserve)"],
        "expected": ("Outcome", (("Reservation", (1,)), True)),
    },
    {
        "function": "step",
        "arguments": ["(Reservation 2)", "(Reserve)"],
        "expected": ("Outcome", (("Reservation", (2,)), False)),
    },
    {
        "function": "step",
        "arguments": ["(Reservation 1)", "(Release)"],
        "expected": ("Outcome", (("Reservation", (0,)), True)),
    },
    {
        "function": "step",
        "arguments": ["(Reservation 0)", "(Release)"],
        "expected": ("Outcome", (("Reservation", (0,)), False)),
    },
]


def _evaluate(function: str, arguments: list[str]):
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": load_reservation_source(),
        "function": function,
        "arguments": arguments,
    }
    return run_prova(request)


@pytest.mark.parametrize("before,event,after,accepted", TRANSITIONS)
def test_p7_every_transition_matches_the_protected_table(before, event, after, accepted):
    returncode, response, stdout, stderr = _evaluate("step", [f"(Reservation {before})", f"({event})"])
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") == "completed", f"expected success, got: {response}"
    result = response.get("result") or {}
    ctor, args = parse_value(result.get("value"))
    assert ctor == "Outcome" and len(args) == 2, f"unexpected result shape: {result.get('value')!r}"
    state_value, accepted_value = args
    state_ctor, state_args = state_value
    assert state_ctor == "Reservation"
    assert 0 <= state_args[0] <= 2, f"resulting count {state_args[0]} violates valid-state invariant"
    assert state_args[0] == after, f"expected count {after}, got {state_args[0]}"
    assert accepted_value is accepted, f"expected accepted={accepted}, got {accepted_value}"


@pytest.mark.parametrize(
    "case",
    DECLARED_EXAMPLES,
    ids=[f"{c['function']}{tuple(c['arguments'])}" for c in DECLARED_EXAMPLES],
)
def test_p7_every_declared_example_evaluates_to_its_declared_result(case):
    returncode, response, stdout, stderr = _evaluate(case["function"], case["arguments"])
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") == "completed", f"expected success, got: {response}"
    result = response.get("result") or {}
    value_text = result.get("value")
    assert parse_value(value_text) == case["expected"], (
        f"declared example {case['function']}{tuple(case['arguments'])} expected "
        f"{case['expected']}, got {value_text!r}"
    )
