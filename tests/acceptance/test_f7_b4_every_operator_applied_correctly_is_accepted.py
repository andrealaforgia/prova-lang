"""Acceptance test for F7 criterion 4: every builtin operator applied to
the number of arguments SPEC.md gives it is accepted, and still answers
what SPEC.md says it answers.

SPEC.md lines 178-189: the eleven operators, their arguments and their
meanings. A rule about counting arguments must leave every correctly
written program exactly as it was.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool accepted every program. Its companion test
file checks the same eleven operators written with one argument too few
and one too many and requires every one of them to be refused.

still passes if: the tool stopped doing arithmetic at all. The second
test below runs the declared examples and requires each operator to
answer the value SPEC.md's meaning gives.
"""

from __future__ import annotations

from _f7_operator_arity_fixtures import (
    THE_OPERATORS_AND_THEIR_ARITIES,
    assert_accepted,
    check,
    every_operator_applied_correctly,
    examples,
)


def test_a_program_using_all_eleven_operators_correctly_is_accepted():
    """Given a program with one function per operator, each applying its
    operator to the number of arguments the language gives it, when the
    program is checked, then it is accepted with nothing held against
    it."""
    assert_accepted(
        check(every_operator_applied_correctly()),
        f"a program applying each of the {len(THE_OPERATORS_AND_THEIR_ARITIES)} "
        "operators to the number of arguments it takes",
    )


def test_those_operators_still_answer_what_the_language_says_they_answer():
    """Given the same program, when its declared examples are run, then
    every one of them passes: counting arguments changed nothing about
    what a correctly written operator computes."""
    source = every_operator_applied_correctly()

    response = examples(source).response()

    assert response.get("status") == "completed", (
        f"the examples of a program whose operators are all written correctly were "
        f"not run: {response}. Only a wrongly written operator call may make a "
        "program invalid."
    )
    results = (response.get("result") or {}).get("examples") or []
    assert len(results) == len(THE_OPERATORS_AND_THEIR_ARITIES), (
        f"the program declares one example for each of the "
        f"{len(THE_OPERATORS_AND_THEIR_ARITIES)} operators, but "
        f"{len(results)} example result(s) came back: {response}. Run every "
        "declared example."
    )
    failed = [entry for entry in results if not entry.get("passed")]
    assert not failed, (
        f"{len(failed)} of the {len(results)} operator examples did not answer the "
        f"value the language gives for its arguments: {failed}. A rule about the "
        "number of arguments must not change what an operator computes."
    )
