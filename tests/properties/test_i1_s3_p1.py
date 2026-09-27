"""I1.S3.P1 / I1.S3.B1: (Reservation 3) is rejected for both events on the
entry precondition, with no successful Outcome.

Given the reservation source unchanged, when `step` is evaluated directly at
current (Reservation 3) -- one above the declared capacity two -- for each
of (Reserve) and (Release), then the response reports a `precondition_violation`
diagnostic and no successful result, distinct from the matched (Reservation 2)
control which must succeed per the six-row table.
"""

from __future__ import annotations

import pytest

from _i1_s3_fixtures import (
    PRECONDITION_CATEGORY,
    TABLE,
    assert_rejected,
    assert_success_outcome,
    evaluate_step,
)


@pytest.mark.parametrize("event", ["Reserve", "Release"])
def test_p1_reservation_three_rejects_on_entry_precondition(event):
    returncode, response, stdout, stderr = evaluate_step("(Reservation 3)", event)
    assert_rejected(returncode, response, stdout, stderr, category=PRECONDITION_CATEGORY)


@pytest.mark.parametrize("event", ["Reserve", "Release"])
def test_p1_matched_reservation_two_control_succeeds(event):
    before, expected_after, expected_accepted = next(
        (b, a, acc) for (b, ev, a, acc) in TABLE if b == 2 and ev == event
    )
    returncode, response, stdout, stderr = evaluate_step(f"(Reservation {before})", event)
    assert_success_outcome(
        returncode, response, stdout, stderr,
        expected_state=expected_after, expected_accepted=expected_accepted,
    )
