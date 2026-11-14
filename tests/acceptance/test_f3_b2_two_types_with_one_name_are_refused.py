"""Acceptance test for F3 criterion 2: a program that declares two types
with the same name is refused, and the refusal names the type and both
places.

SPEC.md lines 137-143: top-level function and type names are unique
within their namespaces.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The control in
test_f3_b6_programs_that_declare_each_name_once_are_accepted.py runs the
same program with the second type renamed and requires it to be
accepted.
"""

from __future__ import annotations

from _f3_duplicate_fixtures import (
    TWO_TYPES_NAMED_MONEY,
    assert_refused_naming,
    check,
    declaration_places,
)


def test_two_types_with_one_name_are_refused_and_both_places_are_named():
    """Given a program that declares the record type `Money` at two
    places, when the program is checked, then it is invalid and the
    refusal names `Money` and both places it was declared."""
    places = declaration_places(TWO_TYPES_NAMED_MONEY, "deftype", "Money")
    assert len(places) == 2, (
        f"the fixture should declare the type `Money` exactly 2 times, it declares "
        f"it at {places}; restore the second declaration in the fixture"
    )

    run = check(TWO_TYPES_NAMED_MONEY)

    assert_refused_naming(run, "Money", places)
