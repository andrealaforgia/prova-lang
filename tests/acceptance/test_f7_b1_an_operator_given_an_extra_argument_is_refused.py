"""Acceptance test for F7 criterion 1: `not` written with two arguments
is refused, and the refusal gives the number of arguments `not` takes
and the number the program gave.

SPEC.md lines 178-189: `not` takes one `Bool` argument, and operators
have no variable arity. A program that writes a second argument is not a
program that may quietly ignore it.

This is also the feature's walking skeleton: the thinnest real path from
the `prova` command's real JSON surface to the refusal a reader gets.
Drives only that surface. No imports from src/prova.

still passes if: the tool refused every program. The controls below run
the same programs with the extra argument removed and require them to be
accepted.
"""

from __future__ import annotations

from _f7_operator_arity_fixtures import (
    NOT_WITH_ONE_ARGUMENT,
    NOT_WITH_ONE_ARGUMENT_INSIDE_AN_ARGUMENT,
    NOT_WITH_TWO_ARGUMENTS,
    NOT_WITH_TWO_ARGUMENTS_INSIDE_AN_ARGUMENT,
    THE_INNER_OPERATOR_CALL_SITE,
    assert_accepted,
    assert_refused_for_its_count,
    check,
)


def test_negation_written_with_two_arguments_is_refused_with_both_counts():
    """Given the function `unflagged?` whose body is `(not flag flag)`,
    when the program is checked, then it is invalid and the refusal says
    `not` takes exactly 1 argument and the program gave 2."""
    run = check(NOT_WITH_TWO_ARGUMENTS)

    assert_refused_for_its_count(run, "not", takes=1, got=2)


def test_the_same_program_with_one_argument_is_accepted():
    """Control: the same function whose body is `(not flag)` is
    accepted, so the refusal above is about the second argument and not
    about `not`."""
    assert_accepted(
        check(NOT_WITH_ONE_ARGUMENT), "a program whose `not` has one argument"
    )


def test_an_extra_argument_written_inside_another_expression_is_refused_too():
    """Given the same function whose `(not flag flag)` stands inside the
    second argument of `and`, when the program is checked, then it is
    invalid: the number of arguments is read wherever the call stands,
    not only when the call is the whole body."""
    run = check(NOT_WITH_TWO_ARGUMENTS_INSIDE_AN_ARGUMENT)

    assert_refused_for_its_count(
        run, "not", takes=1, got=2, at=THE_INNER_OPERATOR_CALL_SITE
    )


def test_the_same_inner_expression_with_one_argument_is_accepted():
    """Control: the same program whose inner call is `(not flag)` is
    accepted, so the refusal above is about the extra argument and not
    about writing an operator inside another operator's argument."""
    assert_accepted(
        check(NOT_WITH_ONE_ARGUMENT_INSIDE_AN_ARGUMENT),
        "a program whose inner `not` has one argument",
    )
