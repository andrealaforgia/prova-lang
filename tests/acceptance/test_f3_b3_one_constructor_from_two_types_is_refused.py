"""Acceptance test for F3 criterion 3: one constructor name introduced by
two different types is refused, and the refusal names the constructor and
both places.

SPEC.md lines 137-143: types and constructors have separate namespaces,
but constructor names must be unique across the program. A record
introduces a constructor with its type's name; a union variant introduces
its own.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The control in
test_f3_b6_programs_that_declare_each_name_once_are_accepted.py runs the
same program with the variant renamed and requires it to be accepted.
"""

from __future__ import annotations

from _f3_duplicate_fixtures import (
    ONE_CONSTRUCTOR_FROM_TWO_TYPES,
    assert_refused_naming,
    check,
    declaration_places,
    member_places,
)


def test_one_constructor_name_from_two_types_is_refused_and_both_places_are_named():
    """Given a record type `Money` and a union whose variant is also
    called `Money`, when the program is checked, then it is invalid and
    the refusal names `Money` and both places the constructor was
    introduced."""
    places = (
        declaration_places(ONE_CONSTRUCTOR_FROM_TWO_TYPES, "deftype", "Money")
        + member_places(ONE_CONSTRUCTOR_FROM_TWO_TYPES, "Money")
    )
    assert len(places) == 2, (
        f"the fixture should introduce the constructor `Money` exactly 2 times, "
        f"from two different types; it introduces it at {places}"
    )

    run = check(ONE_CONSTRUCTOR_FROM_TWO_TYPES)

    assert_refused_naming(run, "Money", places)
