"""Acceptance test for F7's two-defects case, and for the names the
rule must not take over.

SPEC.md lines 178-189: `+` takes two `Int` arguments. A program that
writes three arguments, one of them a flag, breaks two independent
rules, and a reader repairing the program needs to be told both in one
pass. A name that is not one of the eleven operators is still an
undeclared function, and an unclosed call is still unreadable text: the
new rule must take neither of those over.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered every program with every category it
knows. Each test below names the exact set of categories it expects, so
an extra one fails.
"""

from __future__ import annotations

from _f7_operator_arity_fixtures import (
    ARITY_MISMATCH_CATEGORY,
    AN_UNCLOSED_OPERATOR_CALL,
    AN_UNKNOWN_OPERATOR_LIKE_NAME,
    A_PROGRAM_WITH_NO_OPERATOR_IN_IT,
    SUM_WITH_THREE_ARGUMENTS_ONE_OF_THEM_A_FLAG,
    TYPE_MISMATCH_CATEGORY,
    assert_accepted,
    assert_refused_for_its_count,
    categories,
    check,
)


def test_a_sum_with_three_arguments_one_of_them_a_flag_is_told_both_things():
    """Given the function `total` whose body is `(+ cents cents flag)`,
    when the program is checked, then it is invalid, the refusal about
    the number of arguments says `+` takes exactly 2 and got 3, and the
    answer also says the flag is not a number."""
    run = check(SUM_WITH_THREE_ARGUMENTS_ONE_OF_THEM_A_FLAG)

    assert_refused_for_its_count(run, "+", takes=2, got=3, alone=False)
    assert TYPE_MISMATCH_CATEGORY in categories(run.response()), (
        f"the operand that is a flag where a number belongs was not reported: "
        f"{run.response()}. Two independent defects in one expression are two "
        "repairs; report them both in one pass."
    )


def test_a_name_that_is_not_an_operator_is_still_an_undeclared_function():
    """Given the function `total` whose body is `(mod cents cents)`,
    when the program is checked, then it is invalid because nothing
    declares `mod`, and nothing is said about how many arguments it was
    given."""
    response = check(AN_UNKNOWN_OPERATOR_LIKE_NAME).response()

    assert response.get("status") == "invalid_program", (
        f"a program calling the undeclared `mod` was not refused: {response}."
    )
    assert ARITY_MISMATCH_CATEGORY not in categories(response), (
        f"a name the program never declares was answered with a count refusal: "
        f"{response}. Counting arguments is for the eleven builtin operators; a "
        "name nothing declares is an undeclared name."
    )


def test_an_unclosed_call_is_still_unreadable_text():
    """Given a program whose `(+ cents cents)` is never closed, when the
    program is checked, then it is refused as text the tool cannot read,
    not as a call with the wrong number of arguments."""
    response = check(AN_UNCLOSED_OPERATOR_CALL).response()

    assert response.get("status") == "invalid_program", (
        f"a program with an unclosed call was not refused: {response}."
    )
    assert ARITY_MISMATCH_CATEGORY not in categories(response), (
        f"text the tool cannot read was answered with a count refusal: "
        f"{response}. Nothing can be counted in a call that was never closed."
    )


def test_a_program_that_writes_no_operator_at_all_is_still_accepted():
    """Given the function `fare` whose body is the parameter `cents`
    and which writes no operator anywhere, when it is checked, then it
    is accepted: a program with no operator in it breaks no rule about
    operators."""
    assert_accepted(
        check(A_PROGRAM_WITH_NO_OPERATOR_IN_IT),
        "a program that writes no operator at all",
    )
