"""Acceptance test for F3 criterion 1: a program that declares two
functions with the same name is refused, instead of silently keeping the
last one, and the refusal names the function and both places.

SPEC.md lines 137-143: top-level function and type names are unique
within their namespaces.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The control in
test_f3_b6_programs_that_declare_each_name_once_are_accepted.py runs the
same program with the second function renamed and requires it to be
accepted, so a tool that refuses everything fails there.
"""

from __future__ import annotations

from _f3_duplicate_fixtures import (
    TWO_FUNCTIONS_NAMED_TOTAL,
    assert_refused_naming,
    check,
    declaration_places,
)


def test_two_functions_with_one_name_are_refused_and_both_places_are_named():
    """Given a program that declares `total` at two places, when the
    program is checked, then it is invalid and the refusal names `total`
    and both places it was declared."""
    places = declaration_places(TWO_FUNCTIONS_NAMED_TOTAL, "defn", "total")
    assert len(places) == 2, (
        f"the fixture should declare `total` exactly 2 times, it declares it at "
        f"{places}; the scenario is about a name declared twice -- restore the "
        "second declaration in the fixture"
    )

    run = check(TWO_FUNCTIONS_NAMED_TOTAL)

    assert_refused_naming(run, "total", places)
