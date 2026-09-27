"""I1.S3.P2 / I1.S3.B2: (Reservation -1) is rejected for both events on the
entry precondition, with no successful Outcome.

Given current (Reservation -1) -- one below the lower valid boundary zero --
for each of (Reserve) and (Release), then the response reports a
`precondition_violation` diagnostic and no successful result. (Reserve)'s
body would move the count from -1 to 0, back inside the valid range; the
precondition must still reject before that body ever runs, so a returned
in-range state does not count as rejection here. The matched (Reservation 0)
control must succeed per the six-row table.
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
def test_p2_reservation_minus_one_rejects_on_entry_precondition(event):
    returncode, response, stdout, stderr = evaluate_step("(Reservation -1)", event)
    assert_rejected(returncode, response, stdout, stderr, category=PRECONDITION_CATEGORY)

    result = (response or {}).get("result") or {}
    assert not result.get("value"), (
        f"(Reservation -1)/{event} returned a result value despite rejection "
        f"(Reserve's body would land in-range; rejection must precede it): {response}"
    )


@pytest.mark.parametrize("event", ["Reserve", "Release"])
def test_p2_matched_reservation_zero_control_succeeds(event):
    before, expected_after, expected_accepted = next(
        (b, a, acc) for (b, ev, a, acc) in TABLE if b == 0 and ev == event
    )
    returncode, response, stdout, stderr = evaluate_step(f"(Reservation {before})", event)
    assert_success_outcome(
        returncode, response, stdout, stderr,
        expected_state=expected_after, expected_accepted=expected_accepted,
    )
