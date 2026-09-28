"""I1.S3.P6 / I1.S3.B1, B2, B4: the named boundary spellings '-01', '+000',
'-0', '+002' and '0003' classify exactly like their canonical counts, for
both events. SPEC.md: '+002, 2 and 0002 denote the same integer; -0 denotes
zero.'
"""

from __future__ import annotations

import pytest

from _i1_s3_fixtures import PRECONDITION_CATEGORY, TABLE, assert_rejected, assert_success_outcome, evaluate_step

_BY_KEY = {(b, e): (a, acc) for b, e, a, acc in TABLE}

SPELLINGS = [
    ("-01", -1), ("-1", -1), ("+000", 0), ("-0", 0), ("0", 0), ("+0", 0),
    ("+001", 1), ("1", 1), ("+002", 2), ("0002", 2), ("2", 2),
    ("0003", 3), ("+3", 3), ("3", 3),
]


@pytest.mark.parametrize("event", ["Reserve", "Release"])
@pytest.mark.parametrize("digits,count", SPELLINGS, ids=[s for s, _ in SPELLINGS])
def test_p6_named_spelling_matches_semantic_oracle(digits, count, event):
    text = f"(Reservation {digits})"
    returncode, response, stdout, stderr = evaluate_step(text, event)
    if count in (-1, 3):
        assert_rejected(returncode, response, stdout, stderr, category=PRECONDITION_CATEGORY)
    else:
        after, accepted = _BY_KEY[(count, event)]
        assert_success_outcome(returncode, response, stdout, stderr, expected_state=after, expected_accepted=accepted)
