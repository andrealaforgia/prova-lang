"""I1.S3.P5 / I1.S3.B4, I1.S3.CHAR1: all six valid Reservation/Event pairs
succeed with exactly the table's Outcome, distinguishing a successful
Outcome with accepted=false from a failed operation.

Given each of the six pairs the reservation source's finite domain admits
(reserved in {0, 1, 2} crossed with event in {Reserve, Release}), when
`step` is evaluated directly, then the operation succeeds and returns
exactly the independently recorded resulting count and accepted flag, with
the resulting count staying within [0, 2].
"""

from __future__ import annotations

import pytest

from _i1_s3_fixtures import TABLE, assert_success_outcome, evaluate_step


@pytest.mark.parametrize("before,event,after,accepted", TABLE, ids=[f"{b}-{e}" for b, e, _, _ in TABLE])
def test_p5_valid_pair_succeeds_with_exact_table_outcome(before, event, after, accepted):
    returncode, response, stdout, stderr = evaluate_step(f"(Reservation {before})", event)
    assert_success_outcome(
        returncode, response, stdout, stderr,
        expected_state=after, expected_accepted=accepted,
    )
    assert 0 <= after <= 2


def test_p5_boundary_rejection_cases_are_not_successes_with_accepted_false():
    # A success carrying accepted=false ((2,Reserve) and (0,Release)) must
    # not be confusable with the invalid-entry rejections at 3 and -1: the
    # former is a completed Outcome, the latter has no result at all.
    for before, event in [(2, "Reserve"), (0, "Release")]:
        returncode, response, stdout, stderr = evaluate_step(f"(Reservation {before})", event)
        assert response.get("status") == "completed", (
            f"expected a completed (accepted=false) Outcome for ({before}, {event}): {response}"
        )
        result = response.get("result") or {}
        assert result.get("value"), (
            f"boundary case ({before}, {event}) has accepted=false but must still carry "
            f"a successful result value, not be mistaken for a rejection: {response}"
        )
