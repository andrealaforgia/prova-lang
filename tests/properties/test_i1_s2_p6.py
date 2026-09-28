"""I1.S2.P6 / I1.S2.CHAR1: direct evaluation reproduces the whole six-row
transition table, including the two rows absent from `step`'s own examples.

Given the unchanged protected `step` function at the pinned oracle source,
when every one of the six (reserved-count, event) pairs is submitted to the
real direct-evaluation operation, then the returned state and accepted flag
match the independently recorded table for all six rows, the resulting
count always stays within zero and two, and a rejected event leaves the
state unchanged.
"""

from __future__ import annotations

import pytest

from _i1_s2_fixtures import protected_source
from _prova_client import parse_value, run_prova

# Independent oracle: SPEC.md's six-row transition table, copied by hand
# from the pinned oracle commit -- not derived from step's four declared
# examples, which cover only four of these six rows.
TABLE = [
    (0, "Reserve", 1, True),
    (1, "Reserve", 2, True),
    (2, "Reserve", 2, False),
    (0, "Release", 0, False),
    (1, "Release", 0, True),
    (2, "Release", 1, True),
]

assert {(before, event) for before, event, _, _ in TABLE} == {
    (0, "Reserve"), (1, "Reserve"), (2, "Reserve"),
    (0, "Release"), (1, "Release"), (2, "Release"),
}, "TABLE must cover the complete six-pair domain"


def _evaluate_step(before: int, event: str):
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": protected_source(),
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
    return state_args[0], accepted_value, response


@pytest.mark.parametrize("before,event,expected_after,expected_accepted", TABLE)
def test_p6_step_reproduces_every_table_row(before, event, expected_after, expected_accepted):
    after, accepted, response = _evaluate_step(before, event)

    assert 0 <= after <= 2, f"step({before}, {event}) left the valid range: {response}"
    assert (after, accepted) == (expected_after, expected_accepted), (
        f"step({before}, {event}) expected (after={expected_after}, accepted={expected_accepted}), "
        f"got (after={after}, accepted={accepted}); full response={response}"
    )
    if not expected_accepted:
        assert after == before, (
            f"rejected step({before}, {event}) changed state to {after}, expected unchanged {before}"
        )


def test_p6_initial_evaluates_to_empty_reservation():
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": protected_source(),
        "function": "initial",
        "arguments": [],
    }
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0, f"tool failure evaluating initial(): stderr={stderr!r}"
    assert response is not None, f"non-JSON response evaluating initial(): {stdout!r}"
    assert response.get("operation") == "evaluate", response
    assert response.get("status") == "completed", response
    value_text = (response.get("result") or {}).get("value")
    assert value_text, f"no result value for initial(): {response}"
    assert parse_value(value_text) == ("Reservation", (0,)), (
        f"initial() expected Reservation 0, got {value_text!r}; full response={response}"
    )
