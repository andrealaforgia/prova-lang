"""Acceptance test for F6 criterion 2: a function or parameter name that
starts with a capital is refused, and so is a type or constructor name
that starts lower-case.

SPEC.md lines 65-74: value and function names match `[a-z][a-z0-9-]*[?!]?`
and type and constructor names match `[A-Z][A-Za-z0-9]*`, so the first
letter of a name says what kind of thing it names.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program containing a capital
letter anywhere. Each refusal below is paired with a control that keeps
the other names and changes only the first letter under observation.
"""

from __future__ import annotations

from _f6_spelling_fixtures import (
    CONSTRUCTOR_NAME_STARTING_LOWER_CASE,
    CONSTRUCTOR_NAME_STARTING_UPPER_CASE,
    FUNCTION_NAME_STARTING_WITH_A_CAPITAL,
    PARAMETER_NAME_STARTING_WITH_A_CAPITAL,
    TYPE_NAME_STARTING_LOWER_CASE,
    TYPE_NAME_STARTING_UPPER_CASE,
    WELL_SPELLED,
    assert_accepted,
    assert_refused_naming,
    check,
)


def test_a_function_named_with_a_capital_first_letter_is_refused():
    """Given a function named `Add-one`, when the program is checked,
    then it is invalid and the refusal names `Add-one`."""
    assert_refused_naming(
        check(FUNCTION_NAME_STARTING_WITH_A_CAPITAL),
        naming=["'Add-one'"],
        why="a function named 'Add-one'",
    )


def test_a_parameter_named_with_a_capital_first_letter_is_refused():
    """Given a function whose parameter is named `N`, when the program is
    checked, then it is invalid and the refusal names `N`."""
    assert_refused_naming(
        check(PARAMETER_NAME_STARTING_WITH_A_CAPITAL),
        naming=["'N'"],
        why="a parameter named 'N'",
    )


def test_a_type_named_with_a_lower_case_first_letter_is_refused():
    """Given a declared type named `point`, when the program is checked,
    then it is invalid and the refusal names `point`."""
    assert_refused_naming(
        check(TYPE_NAME_STARTING_LOWER_CASE),
        naming=["'point'"],
        why="a type named 'point'",
    )


def test_a_constructor_named_with_a_lower_case_first_letter_is_refused():
    """Given a union variant named `red`, when the program is checked,
    then it is invalid and the refusal names `red`."""
    assert_refused_naming(
        check(CONSTRUCTOR_NAME_STARTING_LOWER_CASE),
        naming=["'red'"],
        why="a union variant named 'red'",
    )


def test_the_same_programs_with_the_defined_first_letters_are_accepted():
    """Control: the three programs above, each with only the first letter
    of the name under observation changed to the one the language
    defines, are accepted."""
    assert_accepted(check(WELL_SPELLED), "a function named 'add-one' taking 'n'")
    assert_accepted(check(TYPE_NAME_STARTING_UPPER_CASE), "a type named 'Point'")
    assert_accepted(
        check(CONSTRUCTOR_NAME_STARTING_UPPER_CASE), "a union variant named 'Red'"
    )
