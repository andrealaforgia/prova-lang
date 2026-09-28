"""I1.S3.P5 / I1.S3.B1-B4, CHAR1: valid and invalid requests interleaved in
one sequence of independent invocations each keep their own verdict. No
session is assumed: every request is a fresh process, and each response is
checked against its own oracle, so a rejection never bleeds into the next
valid request and a successful accepted=false never turns into a rejection.
"""

from __future__ import annotations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s3_fixtures import (
    ILL_TYPED_CATEGORY,
    MALFORMED_CATEGORY,
    PRECONDITION_CATEGORY,
    TABLE,
    assert_rejected,
    assert_success_outcome,
    evaluate_step,
)

_BY_KEY = {(b, e): (a, acc) for b, e, a, acc in TABLE}

VALID = [(b, e) for b, e, _, _ in TABLE]
REQUESTS = (
    [("valid", f"(Reservation {b})", e, (b, e)) for b, e in VALID]
    + [("pre", f"(Reservation {n})", e, None) for n in (-1, 3) for e in ("Reserve", "Release")]
    + [("malformed", t, e, None) for t in ("(Reservation", "", "(Reservation 0 1)") for e in ("Reserve", "Release")]
    + [("illtyped", t, e, None) for t in ("(Reservation true)", "7", "(Reserve)") for e in ("Reserve", "Release")]
)


def _run(request):
    kind, text, event, key = request
    rc, resp, out, err = evaluate_step(text, event)
    if kind == "valid":
        after, accepted = _BY_KEY[key]
        assert_success_outcome(rc, resp, out, err, expected_state=after, expected_accepted=accepted)
        assert 0 <= after <= 2
    elif kind == "pre":
        assert_rejected(rc, resp, out, err, category=PRECONDITION_CATEGORY,
                        forbidden=(MALFORMED_CATEGORY, ILL_TYPED_CATEGORY))
    elif kind == "malformed":
        assert_rejected(rc, resp, out, err, category=MALFORMED_CATEGORY, forbidden=(PRECONDITION_CATEGORY,))
    else:
        assert_rejected(rc, resp, out, err, category=ILL_TYPED_CATEGORY, forbidden=(PRECONDITION_CATEGORY,))


def test_p5_valid_request_follows_every_rejection_family():
    valid = REQUESTS[0]
    for rejecting in [r for r in REQUESTS if r[0] != "valid"]:
        _run(rejecting)
        _run(valid)
        _run(REQUESTS[2])  # (2, Reserve): successful domain refusal after a rejection


@settings(derandomize=True, max_examples=25, deadline=None)
@given(seq=st.lists(st.sampled_from(REQUESTS), min_size=2, max_size=6))
@example(seq=[REQUESTS[2], REQUESTS[6], REQUESTS[2]])
def test_p5_interleaved_sequences_keep_per_request_verdicts(seq):
    for request in seq:
        _run(request)
