"""I1.S1.P1 and I1.S1.P2: `step` matches SPEC.md's six-row transition table.

Given the reservation source and the complete six-element (state, event)
domain, when each pair is submitted to the real `evaluate` operation on the
protected `step` function, then the returned state and acceptance flag match
the independently recorded table (P1), and separately satisfy the general
before/accepted/after transition rule the table encodes (P2), without either
check deriving its expected values from the other or from production code.
"""

from __future__ import annotations

import itertools

import pytest

from _prova_client import load_reservation_source, parse_value, run_prova

# The independent oracle: SPEC.md's six-row transition table, copied by hand.
TABLE = [
    (0, "Reserve", 1, True),
    (1, "Reserve", 2, True),
    (2, "Reserve", 2, False),
    (0, "Release", 0, False),
    (1, "Release", 0, True),
    (2, "Release", 1, True),
]


def _evaluate_step(before: int, event: str):
    source = load_reservation_source()
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": "step",
        "arguments": [f"(Reservation {before})", f"({event})"],
    }
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0, f"tool failure evaluating step({before}, {event}): stderr={stderr!r}"
    assert response is not None, f"non-JSON response evaluating step({before}, {event}): {stdout!r}"
    assert response.get("operation") == "evaluate", response
    assert response.get("status") == "completed", response
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text, f"no result value for step({before}, {event}): {response}"
    ctor, args = parse_value(value_text)
    assert ctor == "Outcome" and len(args) == 2, f"unexpected result shape: {value_text!r}"
    state_value, accepted_value = args
    state_ctor, state_args = state_value
    assert state_ctor == "Reservation" and len(state_args) == 1, f"unexpected state shape: {value_text!r}"
    after = state_args[0]
    return after, accepted_value, response


assert {(before, event) for before, event, _, _ in TABLE} == {
    (0, "Reserve"), (1, "Reserve"), (2, "Reserve"),
    (0, "Release"), (1, "Release"), (2, "Release"),
}, "TABLE must cover the complete six-pair domain, including (1, Reserve) and (2, Release)"


@pytest.mark.parametrize("before,event,expected_after,expected_accepted", TABLE)
def test_p1_step_matches_table_row(before, event, expected_after, expected_accepted):
    after, accepted, response = _evaluate_step(before, event)
    assert (after, accepted) == (expected_after, expected_accepted), (
        f"step({before}, {event}) expected (after={expected_after}, accepted={expected_accepted}), "
        f"got (after={after}, accepted={accepted}); full response={response}"
    )


@pytest.mark.parametrize(
    "before,event_name,delta",
    [
        (before, event_name, delta)
        for before, (event_name, delta) in itertools.product(
            (0, 1, 2), (("Reserve", 1), ("Release", -1))
        )
    ],
)
def test_p2_transition_rule_holds(before, event_name, delta):
    expected_accepted = (before < 2) if event_name == "Reserve" else (before > 0)
    expected_after = before + delta if expected_accepted else before

    after, accepted, response = _evaluate_step(before, event_name)

    assert 0 <= after <= 2, f"state left the valid range: {response}"
    assert accepted == expected_accepted, (
        f"step({before}, {event_name}) accepted flag: expected {expected_accepted}, got {accepted}"
    )
    assert after == expected_after, (
        f"step({before}, {event_name}) after-state: expected {expected_after}, got {after}"
    )
    if not expected_accepted:
        assert after == before, (
            f"rejected step({before}, {event_name}) changed state to {after}, expected unchanged {before}"
        )
