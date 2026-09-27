"""I1.S6.P8: supporting large integers in the separate add-one program
leaves reservation `step`'s entry contract intact, so well-typed
Reservation counts below zero or above two are rejected for violating the
precondition, with no successful return value for either event -- at any
magnitude, including magnitudes that only large-integer support makes
reachable.

Finite evidence domain: generated invalid counts in [-2^256, 2^256], always
including -1, 3, 2^53+1, -2^53-1, 2^63, -2^63-1, and the approved
large-integer examples 9223372036854775808 and -9223372036854775810.
Boundary controls are counts 0 and 2 with both events, which must still
succeed per the protected six-row table.
"""

from __future__ import annotations

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s6_fixtures import load_reservation_source, parse_value, run_prova

EVENTS = ["Reserve", "Release"]

_invalid_domain = st.one_of(
    st.integers(min_value=-(2**256), max_value=-1),
    st.integers(min_value=3, max_value=2**256),
)


def _evaluate_step(count: int, event: str):
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": load_reservation_source(),
        "function": "step",
        "arguments": [f"(Reservation {count})", f"({event})"],
    }
    return run_prova(request)


@settings(derandomize=True, max_examples=16, deadline=None)
@given(count=_invalid_domain, event=st.sampled_from(EVENTS))
@example(count=-1, event="Reserve")
@example(count=3, event="Release")
@example(count=2**53 + 1, event="Reserve")
@example(count=-(2**53) - 1, event="Release")
@example(count=2**63, event="Reserve")
@example(count=-(2**63) - 1, event="Release")
@example(count=9223372036854775808, event="Release")
@example(count=-9223372036854775810, event="Reserve")
def test_p8_invalid_counts_rejected_on_entry_precondition_at_any_magnitude(count, event):
    returncode, response, stdout, stderr = _evaluate_step(count, event)
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") != "completed", f"expected a rejection, got: {response}"
    assert not response.get("result"), f"rejection carried a successful result: {response}"
    categories = {d.get("category") for d in (response.get("diagnostics") or [])}
    assert "precondition_violation" in categories, (
        f"expected precondition_violation among {categories}: {response}"
    )


@pytest.mark.parametrize(
    "count,event,expected_after,expected_accepted",
    [
        (0, "Reserve", 1, True),
        (0, "Release", 0, False),
        (2, "Reserve", 2, False),
        (2, "Release", 1, True),
    ],
)
def test_p8_boundary_valid_counts_still_succeed(count, event, expected_after, expected_accepted):
    returncode, response, stdout, stderr = _evaluate_step(count, event)
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") == "completed", f"expected success, got: {response}"
    result = response.get("result") or {}
    ctor, args = parse_value(result.get("value"))
    assert ctor == "Outcome"
    state_value, accepted_value = args
    state_ctor, state_args = state_value
    assert state_args[0] == expected_after
    assert accepted_value is expected_accepted
