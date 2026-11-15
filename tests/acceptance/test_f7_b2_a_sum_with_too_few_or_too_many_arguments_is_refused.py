"""Acceptance test for F7 criterion 2: `+` written with one argument,
and `+` written with three, are both refused, each refusal giving the
number of arguments `+` takes and the number the program gave.

SPEC.md lines 178-189: `+` takes two `Int` arguments, and operators have
no variable arity. Too few is as wrong as too many: a missing operand
must not be read as a shorter sum.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The control below runs
the same program with two arguments and requires it to be accepted.

still passes if: the tool reported the same count for both programs. The
two cases below ask for 1 and for 3, so a refusal that always says the
same number fails one of them.
"""

from __future__ import annotations

from _f7_operator_arity_fixtures import (
    SUM_WITH_ONE_ARGUMENT,
    SUM_WITH_THREE_ARGUMENTS,
    SUM_WITH_TWO_ARGUMENTS,
    assert_accepted,
    assert_refused_for_its_count,
    check,
)


def test_a_sum_written_with_one_argument_is_refused_with_both_counts():
    """Given the function `total` whose body is `(+ cents)`, when the
    program is checked, then it is invalid and the refusal says `+`
    takes exactly 2 arguments and the program gave 1."""
    run = check(SUM_WITH_ONE_ARGUMENT)

    assert_refused_for_its_count(run, "+", takes=2, got=1)


def test_a_sum_written_with_three_arguments_is_refused_with_both_counts():
    """Given the same function whose body is `(+ cents cents cents)`,
    when the program is checked, then it is invalid and the refusal says
    `+` takes exactly 2 arguments and the program gave 3."""
    run = check(SUM_WITH_THREE_ARGUMENTS)

    assert_refused_for_its_count(run, "+", takes=2, got=3)


def test_the_same_program_with_two_arguments_is_accepted():
    """Control: the same function whose body is `(+ cents cents)` is
    accepted, so the two refusals above are about the count and not
    about `+`."""
    assert_accepted(
        check(SUM_WITH_TWO_ARGUMENTS), "a program whose `+` has two arguments"
    )
