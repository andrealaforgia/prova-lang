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

Four of the nine families below are real generators rather than fixed lists,
closing a gap a validation run found: the previous version only ever tried
arity 0/2, one constructor payload, two unknown-constructor strings and one
Outcome literal, so it could not support the verification's claim of
"generated, bounded payload and arity variations". Each generated family
tags its own output with its family name; `test_p4_generated_families_were_exercised`
runs its own derandomized, bounded Hypothesis draw (200 examples) over the
tagged strategies and asserts every family appears, so the generation cannot
silently collapse back to a single repeated value. That draw happens inside
the test itself, self-contained, rather than observing a record left by
another test, so it passes or fails the same way regardless of test order
or selection.
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

_KNOWN_CONSTRUCTOR_NAMES = {"Reservation", "Reserve", "Release", "Outcome"}

# Generated family: an unknown constructor name (never one of the four
# declared names) with a generated arity of integer fields.
_unknown_constructor_name = st.from_regex(
    r"[A-Z][A-Za-z]{0,7}", fullmatch=True
).filter(lambda name: name not in _KNOWN_CONSTRUCTOR_NAMES)
_unknown_constructor_tagged = st.builds(
    lambda name, fields: (
        "unknown_constructor",
        f"({name}{' ' + ' '.join(str(f) for f in fields) if fields else ''})",
    ),
    _unknown_constructor_name,
    st.lists(st.integers(min_value=-5, max_value=5), min_size=0, max_size=3),
)

# Generated family: Reservation with a generated arity other than 1 (the
# declared arity), each field a generated integer.
_reservation_wrong_arity_tagged = st.builds(
    lambda fields: (
        "reservation_wrong_arity",
        f"(Reservation{' ' + ' '.join(str(f) for f in fields) if fields else ''})",
    ),
    st.integers(min_value=0, max_value=4)
    .filter(lambda n: n != 1)
    .flatmap(lambda n: st.lists(st.integers(min_value=-5, max_value=5), min_size=n, max_size=n)),
)

# Generated family: Outcome with a generated reservation count and boolean,
# still the wrong nominal type for `current`.
_outcome_value_tagged = st.builds(
    lambda n, accepted: ("outcome_value", f"(Outcome (Reservation {n}) {accepted})"),
    st.integers(min_value=-3, max_value=3),
    st.sampled_from(["true", "false"]),
)

# Generated family: Reservation whose sole field is itself a constructor
# value, at a generated nesting depth (Reservation, Outcome or an unknown
# constructor at the leaf). The outer wrap is mandatory: the base case of
# `_constructor_leaf` already includes "(Reservation N)" with a plain
# integer field, which by itself is a VALID Reservation, not an ill-typed
# one, so it must never be handed out unwrapped -- always nest it inside at
# least one more "(Reservation ...)" whose field is that constructor value.
_constructor_leaf = st.one_of(
    st.builds(lambda n: f"(Reservation {n})", st.integers(min_value=-3, max_value=3)),
    st.builds(
        lambda n, accepted: f"(Outcome (Reservation {n}) {accepted})",
        st.integers(min_value=-3, max_value=3),
        st.sampled_from(["true", "false"]),
    ),
    st.builds(lambda n: f"(NoSuchThing {n})", st.integers(min_value=-3, max_value=3)),
)
_reservation_constructor_payload_tagged = st.builds(
    lambda c: ("reservation_constructor_payload", f"(Reservation {c})"),
    st.recursive(
        _constructor_leaf,
        lambda children: st.builds(lambda c: f"(Reservation {c})", children),
        max_leaves=3,
    ),
)

_generated_families_tagged = st.one_of(
    _unknown_constructor_tagged,
    _reservation_wrong_arity_tagged,
    _outcome_value_tagged,
    _reservation_constructor_payload_tagged,
)

_ill_typed_text = st.one_of(
    st.integers(min_value=-1000, max_value=1000).map(str),  # bare Int
    st.sampled_from(["true", "false", "()"]),                # Bool, Unit
    st.sampled_from(["(Reserve)", "(Release)"]),              # Event constructors
    _generated_families_tagged,                                 # the four generated families, tagged
    st.sampled_from(["(Reservation true)", "(Reservation false)"]),   # Bool payload
    st.sampled_from(["(Reservation ())"]),                    # Unit payload
).map(lambda value: value[1] if isinstance(value, tuple) else value)


@settings(derandomize=True, max_examples=60, deadline=None)
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


def test_p4_generated_families_were_exercised():
    expected_families = {
        "unknown_constructor",
        "reservation_wrong_arity",
        "outcome_value",
        "reservation_constructor_payload",
    }
    hit_families: set[str] = set()

    @settings(derandomize=True, max_examples=200, deadline=None)
    @given(pair=_generated_families_tagged)
    def _draw(pair):
        family, _text = pair
        hit_families.add(family)

    _draw()

    missing = expected_families - hit_families
    assert not missing, (
        f"generated families never produced a case in 200 examples: {missing} "
        f"(hit: {hit_families})"
    )
