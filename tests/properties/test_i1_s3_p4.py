"""I1.S3.P4 / I1.S3.B3: syntactically well-formed values of the wrong type
are rejected distinctly from an entry-precondition violation, without
coercion into a valid Reservation.

Given a `current` argument that parses as a closed value but is not of the
declared Reservation type -- a bare integer, a Boolean, Unit, an Event or
Outcome constructor, an unknown constructor name, or a Reservation
constructor with the wrong field count or a field of the wrong type,
including the accidental-Boolean-coercion cases (Reservation true) and
(Reservation false) -- when `step` is evaluated with a valid Event, then the
response reports `malformed_value` or `ill_typed_value` (never
`precondition_violation`) and no successful result. Correcting the value to
(Reservation 0), (Reservation 1) or (Reservation 2) must succeed.

Derandomized with a fixed seed and bounded example counts, plus an explicit
representative of every listed family.
"""

from __future__ import annotations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s3_fixtures import (
    EVENTS,
    ILL_TYPED_CATEGORY,
    MALFORMED_CATEGORY,
    PRECONDITION_CATEGORY,
    assert_success_outcome,
    diagnostic_categories,
    evaluate_step,
)

_ill_typed_text = st.one_of(
    st.integers(min_value=-1000, max_value=1000).map(str),  # bare Int
    st.sampled_from(["true", "false", "()"]),                # Bool, Unit
    st.sampled_from(["(Reserve)", "(Release)"]),              # Event constructors
    st.sampled_from(["(Outcome (Reservation 0) true)"]),      # Outcome value
    st.sampled_from(["(NoSuchThing)", "(NoSuchThing 1)"]),   # unknown constructor
    st.sampled_from(["(Reservation)", "(Reservation 1 2)"]), # wrong arity
    st.sampled_from(["(Reservation true)", "(Reservation false)"]),   # Bool payload
    st.sampled_from(["(Reservation ())"]),                    # Unit payload
    st.sampled_from(["(Reservation (Reserve))"]),             # constructor payload
)


@settings(derandomize=True, max_examples=30, deadline=None)
@given(text=_ill_typed_text, event=st.sampled_from(EVENTS))
@example(text="0", event="Reserve")
@example(text="true", event="Release")
@example(text="false", event="Reserve")
@example(text="()", event="Release")
@example(text="(Reserve)", event="Reserve")
@example(text="(Release)", event="Release")
@example(text="(Outcome (Reservation 0) true)", event="Reserve")
@example(text="(NoSuchThing)", event="Release")
@example(text="(Reservation)", event="Reserve")
@example(text="(Reservation 1 2)", event="Release")
@example(text="(Reservation true)", event="Reserve")
@example(text="(Reservation false)", event="Release")
@example(text="(Reservation ())", event="Reserve")
@example(text="(Reservation (Reserve))", event="Release")
def test_p4_ill_typed_current_is_rejected_distinctly(text, event):
    returncode, response, stdout, stderr = evaluate_step(text, event)
    assert returncode == 0, f"tool crashed on ill-typed text {text!r}/{event}: stderr={stderr!r}"
    assert response is not None, f"non-JSON response for {text!r}/{event}: {stdout!r}"
    assert response.get("status") != "completed", (
        f"expected a rejection for ill-typed value {text!r}/{event}, got: {response}"
    )
    assert not response.get("result"), (
        f"ill-typed value {text!r}/{event} carried a successful result: {response}"
    )
    categories = diagnostic_categories(response)
    assert categories & {MALFORMED_CATEGORY, ILL_TYPED_CATEGORY}, (
        f"expected a malformed_value or ill_typed_value diagnostic for {text!r}/{event}, "
        f"got categories={categories}: {response}"
    )
    assert PRECONDITION_CATEGORY not in categories, (
        f"ill-typed value {text!r}/{event} was reported as a precondition violation "
        f"instead of a value-classification error: {response}"
    )


def test_p4_corrected_controls_succeed():
    for current, event in [
        ("(Reservation 0)", "Reserve"),
        ("(Reservation 1)", "Reserve"),
        ("(Reservation 2)", "Release"),
    ]:
        returncode, response, stdout, stderr = evaluate_step(current, event)
        before = int(current.split()[-1].rstrip(")"))
        expected_state, expected_accepted = {
            (0, "Reserve"): (1, True),
            (1, "Reserve"): (2, True),
            (2, "Release"): (1, True),
        }[(before, event)]
        assert_success_outcome(
            returncode, response, stdout, stderr,
            expected_state=expected_state, expected_accepted=expected_accepted,
        )
