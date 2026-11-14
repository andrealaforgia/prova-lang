"""Acceptance test for F3 criterion 4: a record, or a union variant, that
declares the same field name twice is refused, and the refusal names the
field and both places.

SPEC.md lines 137-143: fields are unique within each record or variant.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program with a field called
`amount`. The control in
test_f3_b6_programs_that_declare_each_name_once_are_accepted.py checks a
program whose two records each declare `amount` once and requires it to
be accepted.
"""

from __future__ import annotations

from _f3_duplicate_fixtures import (
    RECORD_WITH_THE_FIELD_AMOUNT_TWICE,
    VARIANT_WITH_THE_FIELD_AMOUNT_TWICE,
    assert_refused_naming,
    check,
    member_places,
)


def test_a_record_that_declares_one_field_twice_is_refused_naming_both_places():
    """Given a record `Money` that declares the field `amount` twice,
    when the program is checked, then it is invalid and the refusal names
    `amount` and both places it was declared."""
    places = member_places(RECORD_WITH_THE_FIELD_AMOUNT_TWICE, "amount")
    assert len(places) == 2, (
        f"the fixture should declare the field `amount` exactly 2 times in one "
        f"record, it declares it at {places}"
    )

    run = check(RECORD_WITH_THE_FIELD_AMOUNT_TWICE)

    assert_refused_naming(run, "amount", places)


def test_a_variant_that_declares_one_field_twice_is_refused_naming_both_places():
    """Given a union variant `Transfer` that declares the field `amount`
    twice, when the program is checked, then it is invalid and the
    refusal names `amount` and both places it was declared."""
    places = member_places(VARIANT_WITH_THE_FIELD_AMOUNT_TWICE, "amount")
    assert len(places) == 2, (
        f"the fixture should declare the field `amount` exactly 2 times in one "
        f"variant, it declares it at {places}"
    )

    run = check(VARIANT_WITH_THE_FIELD_AMOUNT_TWICE)

    assert_refused_naming(run, "amount", places)
