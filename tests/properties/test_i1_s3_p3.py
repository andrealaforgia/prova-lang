"""I1.S3.P3 / I1.S3.B3: malformed argument text is rejected distinctly from
an entry-precondition violation.

Given a request whose `current` argument text is not a well-formed closed
value at all (empty/whitespace, a truncated constructor, unmatched
parentheses, or multiple values where one is expected), when `step` is
evaluated with a valid Event, then the response reports a `malformed_value`
diagnostic, carries no successful result, and never reports
`precondition_violation` for a request that never decoded to a value.
Replacing the malformed text with (Reservation 0) must succeed.

Derandomized with a fixed seed and bounded example counts per family, plus
one explicit representative of every listed family, so the verdict does not
depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s3_fixtures import (
    EVENTS,
    MALFORMED_CATEGORY,
    PRECONDITION_CATEGORY,
    assert_rejected,
    assert_success_outcome,
    evaluate_step,
)

# Family: empty or whitespace-only text.
_empty_or_whitespace = st.sampled_from(["", " ", "\t", "\n", "   "])

# Family: truncated constructors -- an opening paren and constructor name
# (optionally a partial field) with no closing paren.
_truncated = st.sampled_from(
    [
        "(Reservation",
        "(Reservation 1",
        "(Reservation ",
        "(",
        "(Res",
    ]
)

# Family: unmatched parentheses (extra open or extra close around an
# otherwise well-formed value).
_unmatched_parens = st.sampled_from(
    [
        "(Reservation 0))",
        "((Reservation 0)",
        "(Reservation (0)",
        ")",
        "(Reservation 0",
    ]
)

# Family: multiple closed values where exactly one is required.
_multiple_values = st.sampled_from(
    [
        "(Reservation 0) (Reservation 1)",
        "1 2",
        "(Reservation 0) 1",
        "true false",
    ]
)

_malformed_text = st.one_of(
    _empty_or_whitespace, _truncated, _unmatched_parens, _multiple_values
)


@settings(derandomize=True, max_examples=25, deadline=None)
@given(text=_malformed_text, event=st.sampled_from(EVENTS))
@example(text="", event="Reserve")
@example(text="   ", event="Release")
@example(text="(Reservation", event="Reserve")
@example(text="(Reservation 1", event="Release")
@example(text="(Reservation 0))", event="Reserve")
@example(text=")", event="Release")
@example(text="(Reservation 0) (Reservation 1)", event="Reserve")
@example(text="1 2", event="Release")
def test_p3_malformed_current_text_is_rejected_distinctly(text, event):
    returncode, response, stdout, stderr = evaluate_step(text, event)
    assert returncode == 0, f"tool crashed on malformed text {text!r}/{event}: stderr={stderr!r}"
    assert_rejected(
        returncode, response, stdout, stderr,
        category=MALFORMED_CATEGORY,
        forbidden=(PRECONDITION_CATEGORY,),
    )


def test_p3_matched_zero_control_succeeds_for_each_event():
    for event in EVENTS:
        returncode, response, stdout, stderr = evaluate_step("(Reservation 0)", event)
        expected_state, expected_accepted = (1, True) if event == "Reserve" else (0, False)
        assert_success_outcome(
            returncode, response, stdout, stderr,
            expected_state=expected_state, expected_accepted=expected_accepted,
        )
