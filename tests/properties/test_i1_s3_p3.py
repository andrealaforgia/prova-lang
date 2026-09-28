"""I1.S3.P3 / I1.S3.B3: malformed argument text is rejected distinctly from
an entry-precondition violation.

Given a request whose `current` argument text is not a well-formed closed
value at all (empty/whitespace, a truncated constructor, unmatched
parentheses, a value wrapped in one or more extra enclosing parentheses so
its head is itself a list rather than a name, or multiple values where one
is expected), when `step` is evaluated with a valid Event, then the response
reports a `malformed_value` diagnostic, carries no successful result, and
never reports `precondition_violation` for a request that never decoded to
a value. Replacing the malformed text with (Reservation 0) must succeed.

Derandomized with a fixed seed and bounded example counts per family, plus
one explicit representative of every listed family, so the verdict does not
depend on which cases Hypothesis happens to draw.

The wrapped-head family is a real generator, not a fixed list: it draws a
random wrap depth and a random inner value/text and builds the string
programmatically, so the space it covers is not limited to hand-picked
strings. It replaces reliance on hand-picked lists alone for this specific
malformation shape, after a validation run found that fixed lists missed it:
`((Reservation 1))`, `((Reservation))`, `((1))` and `(())` each crashed the
tool (`AttributeError` in `syntax.parse_value`, exit status 1, no JSON
response) instead of being rejected. Those four are pinned below as
permanent regression examples.
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

# Family: a value (or empty text) wrapped in a balanced but excessive number
# of enclosing parentheses, so the outermost list's head is itself a list
# rather than a constructor name. Generated, not enumerated: depth and inner
# text are both drawn.
_wrap_inner = st.one_of(
    st.just(""),
    st.integers(min_value=-3, max_value=3).map(str),
    st.builds(lambda n: f"(Reservation {n})", st.integers(min_value=-3, max_value=3)),
    st.sampled_from(["(Reserve)", "(Release)"]),
)
_wrap_depth = st.integers(min_value=1, max_value=3)
_wrapped_head = st.builds(
    lambda inner, depth: "(" * depth + inner + ")" * depth, _wrap_inner, _wrap_depth
)

_malformed_text = st.one_of(
    _empty_or_whitespace, _truncated, _unmatched_parens, _multiple_values, _wrapped_head
)


@settings(derandomize=True, max_examples=40, deadline=None)
@given(text=_malformed_text, event=st.sampled_from(EVENTS))
@example(text="", event="Reserve")
@example(text="   ", event="Release")
@example(text="(Reservation", event="Reserve")
@example(text="(Reservation 1", event="Release")
@example(text="(Reservation 0))", event="Reserve")
@example(text=")", event="Release")
@example(text="(Reservation 0) (Reservation 1)", event="Reserve")
@example(text="1 2", event="Release")
@example(text="((Reservation 1))", event="Reserve")
@example(text="((Reservation))", event="Release")
@example(text="((1))", event="Reserve")
@example(text="(())", event="Release")
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
