"""Acceptance test for F8 criterion 3: an example whose number of
arguments is not the number its function takes is refused when the
program is checked, not only when the examples run.

SPEC.md lines 228-234: an example's arguments must be closed values of
the declared types, one for each parameter the function declares. A
program whose example writes another number of arguments cannot be run
against that function at all, so `check` answers about it.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. Each case below is
paired with the same function whose example writes the number of
arguments it takes, and that twin must be accepted.
"""

from __future__ import annotations

from _f8_example_subject_fixtures import (
    AN_EXAMPLE_WITH_NO_ARGUMENT_AT_ALL,
    AN_EXAMPLE_WITH_ONE_ARGUMENT_TOO_MANY,
    A_FUNCTION_THAT_TAKES_NO_ARGUMENT,
    A_LONE_FUNCTION_WITH_ITS_OWN_EXAMPLE,
    A_TWO_PARAMETER_FUNCTION_GIVEN_BOTH_ARGUMENTS,
    A_TWO_PARAMETER_FUNCTION_GIVEN_ONE_ARGUMENT,
    assert_accepted,
    assert_refused_for_its_argument_count,
    check,
)


def test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked():
    """Given `double`, which takes 1 argument, whose example is
    `(example (double 2 3) => 4)`, when the program is checked, then it
    is invalid and the refusal says the example passes 2 arguments and 1
    was expected."""
    run = check(AN_EXAMPLE_WITH_ONE_ARGUMENT_TOO_MANY)

    assert_refused_for_its_argument_count(run, "double", takes=1, got=2)


def test_an_example_with_no_argument_for_a_function_that_takes_one_is_refused():
    """Given the same `double` whose example is `(example (double) => 4)`,
    when the program is checked, then it is invalid and the refusal says
    the example passes 0 arguments and 1 was expected."""
    run = check(AN_EXAMPLE_WITH_NO_ARGUMENT_AT_ALL)

    assert_refused_for_its_argument_count(run, "double", takes=1, got=0)


def test_an_example_leaving_out_the_second_argument_is_refused():
    """Given `fare`, which takes 2 arguments, whose example is
    `(example (fare 100) => 110)`, when the program is checked, then it
    is invalid and the refusal says the example passes 1 argument and 2
    were expected."""
    run = check(A_TWO_PARAMETER_FUNCTION_GIVEN_ONE_ARGUMENT)

    assert_refused_for_its_argument_count(run, "fare", takes=2, got=1)


def test_the_same_function_given_both_its_arguments_is_accepted():
    """Control: the same `fare` whose example is
    `(example (fare 100 true) => 110)` is accepted, so the refusal above
    is about the missing argument and not about the function."""
    assert_accepted(
        check(A_TWO_PARAMETER_FUNCTION_GIVEN_BOTH_ARGUMENTS),
        "a function of 2 parameters whose example writes both arguments",
    )


def test_the_same_function_given_its_one_argument_is_accepted():
    """Control: `double` whose example is `(example (double 2) => 4)` is
    accepted, so the refusals above are about the count alone."""
    assert_accepted(
        check(A_LONE_FUNCTION_WITH_ITS_OWN_EXAMPLE),
        "a function of 1 parameter whose example writes 1 argument",
    )


def test_a_function_that_takes_nothing_and_writes_nothing_is_accepted():
    """Control: `standard-fare`, which takes 0 arguments, whose example
    is `(example (standard-fare) => 110)`, is accepted: writing no
    argument is the right count for a function that takes none."""
    assert_accepted(
        check(A_FUNCTION_THAT_TAKES_NO_ARGUMENT),
        "a function of 0 parameters whose example writes no argument",
    )
