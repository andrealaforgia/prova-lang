"""I1.S3.P6 / I1.S3.B1, I1.S3.B2, I1.S3.B4: equivalent textual spellings of a
count preserve that count's outcome.

Given the five semantic counts {-1, 0, 1, 2, 3} and both events, when the
count is spelled with extra leading zeros, an optional leading plus for
nonnegative counts, `-0` for zero, or extra internal whitespace, then -1 and
3 still reject on the entry precondition with no successful result, and 0,
1 and 2 still succeed with exactly the table's Outcome. SPEC.md defines
these spellings as denoting the same mathematical integer, so the tool must
not treat them differently from the canonical spelling.

Derandomized with a fixed seed and bounded example counts, plus one
explicit representative per count/spelling family.
"""

from __future__ import annotations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s3_fixtures import (
    PRECONDITION_CATEGORY,
    TABLE,
    assert_rejected,
    assert_success_outcome,
    evaluate_step,
)

TABLE_BY_BEFORE_EVENT = {(b, e): (a, acc) for b, e, a, acc in TABLE}

_extra_padding = st.integers(min_value=0, max_value=3)
_whitespace_run = st.sampled_from(["", " ", "  ", "\t"])


def _digits_spelling(n: int, padding: int) -> str:
    sign = "-" if n < 0 else ""
    digits = str(abs(n)).rjust(1 + padding, "0")
    return f"{sign}{digits}"


@st.composite
def _spelling(draw, n: int) -> str:
    padding = draw(_extra_padding)
    digits = _digits_spelling(n, padding)
    if n == 0 and draw(st.booleans()):
        digits = "-" + "0" * (1 + padding)  # "-0", "-00", ...
    elif n >= 0 and draw(st.booleans()):
        digits = "+" + digits.lstrip("+")  # optional leading plus
    ws_open = draw(_whitespace_run)
    ws_before_close = draw(_whitespace_run)
    return f"(Reservation {ws_open}{digits}{ws_before_close})"


def _check(n: int, event: str, text: str):
    returncode, response, stdout, stderr = evaluate_step(text, event)
    if n in (-1, 3):
        assert_rejected(returncode, response, stdout, stderr, category=PRECONDITION_CATEGORY)
    else:
        after, accepted = TABLE_BY_BEFORE_EVENT[(n, event)]
        assert_success_outcome(
            returncode, response, stdout, stderr,
            expected_state=after, expected_accepted=accepted,
        )


@settings(derandomize=True, max_examples=10, deadline=None)
@given(text=_spelling(-1))
@example(text="(Reservation -01)")
@example(text="(Reservation  -1)")
def test_p6_minus_one_spellings_reject(text):
    _check(-1, "Reserve", text)
    _check(-1, "Release", text)


@settings(derandomize=True, max_examples=10, deadline=None)
@given(text=_spelling(0))
@example(text="(Reservation 00)")
@example(text="(Reservation -0)")
@example(text="(Reservation +0)")
@example(text="(Reservation  0 )")
def test_p6_zero_spellings_succeed(text):
    _check(0, "Reserve", text)
    _check(0, "Release", text)


@settings(derandomize=True, max_examples=10, deadline=None)
@given(text=_spelling(1))
@example(text="(Reservation 01)")
@example(text="(Reservation +1)")
def test_p6_one_spellings_succeed(text):
    _check(1, "Reserve", text)
    _check(1, "Release", text)


@settings(derandomize=True, max_examples=10, deadline=None)
@given(text=_spelling(2))
@example(text="(Reservation 002)")
@example(text="(Reservation +2)")
def test_p6_two_spellings_succeed(text):
    _check(2, "Reserve", text)
    _check(2, "Release", text)


@settings(derandomize=True, max_examples=10, deadline=None)
@given(text=_spelling(3))
@example(text="(Reservation 03)")
@example(text="(Reservation +3)")
def test_p6_three_spellings_reject(text):
    _check(3, "Reserve", text)
    _check(3, "Release", text)
