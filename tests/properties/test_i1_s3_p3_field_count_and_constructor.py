"""I1.S3.P3 / I1.S3.B3: near-valid malformed forms -- wrong field counts and
unknown constructor names -- are rejected as input failures, never as an
entry-precondition violation, and never with a successful result.

The malformed-vs-ill-typed split for these shapes is deliberately not
prescribed: either input-value category satisfies the question, provided it
is distinct from `precondition_violation`.
"""

from __future__ import annotations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s3_fixtures import (
    EVENTS,
    ILL_TYPED_CATEGORY,
    MALFORMED_CATEGORY,
    PRECONDITION_CATEGORY,
    diagnostic_categories,
    evaluate_step,
)

_field_counts = st.builds(
    lambda n, k: "(Reservation" + "".join(f" {n}" for _ in range(k)) + ")",
    st.integers(min_value=-1, max_value=3),
    st.sampled_from([0, 2, 3, 4]),
)
_unknown_ctor = st.builds(
    lambda name, n: f"({name} {n})",
    st.sampled_from(["Bogus", "reservation", "RESERVATION", "Reserv", "Outcome2", "Reserve1", "X"]),
    st.integers(min_value=-1, max_value=3),
)


@settings(derandomize=True, max_examples=40, deadline=None)
@given(text=st.one_of(_field_counts, _unknown_ctor), event=st.sampled_from(EVENTS))
@example(text="(Reservation)", event="Reserve")
@example(text="(Reservation)", event="Release")
@example(text="(Reservation 0 1)", event="Reserve")
@example(text="(Reservation 0 1)", event="Release")
@example(text="(Reservation 0", event="Reserve")
@example(text="(Reservation 0", event="Release")
@example(text="(Bogus 0)", event="Reserve")
def test_p3_field_count_and_unknown_constructor_rejected_as_input_failure(text, event):
    returncode, response, stdout, stderr = evaluate_step(text, event)
    assert returncode == 0, f"tool crashed on {text!r}/{event}: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert not (response.get("result") or {}).get("value"), f"successful result for {text!r}: {response}"
    categories = diagnostic_categories(response)
    assert categories & {MALFORMED_CATEGORY, ILL_TYPED_CATEGORY}, f"no input-value category: {response}"
    assert PRECONDITION_CATEGORY not in categories, f"conflated with precondition: {response}"


def test_p3_input_failure_differs_from_known_precondition_failure():
    for event in EVENTS:
        _, bad, _, _ = evaluate_step("(Reservation 0 1)", event)
        _, pre, _, _ = evaluate_step("(Reservation 3)", event)
        assert diagnostic_categories(bad) != diagnostic_categories(pre)
        assert PRECONDITION_CATEGORY in diagnostic_categories(pre)
