"""Acceptance test for F7 wherever an expression may stand: a wrong
number of arguments is refused in a precondition, in a postcondition and
in the body of a `match` clause, not only in the body of a function.

SPEC.md lines 178-189 give every operator a fixed number of arguments,
and lines 198-210 let a precondition and a postcondition hold any
Boolean expression. A reader who writes `(< cents)` in a precondition
has made the same mistake as one who writes it in the body, and must be
sent to the same place.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program that has a contract or a
`match` in it. The last test runs one program with correct operators in
all three of those positions and requires it to be accepted.
"""

from __future__ import annotations

from _f7_operator_arity_fixtures import (
    A_MATCH_CLAUSE_WITH_A_WRONG_COUNT,
    A_POSTCONDITION_WITH_A_WRONG_COUNT,
    A_PRECONDITION_WITH_A_WRONG_COUNT,
    CORRECT_OPERATORS_IN_A_CONTRACT_AND_A_MATCH,
    assert_accepted,
    assert_refused_for_its_count,
    check,
    examples,
    site_of,
)


def test_a_wrong_count_in_a_precondition_is_refused_with_both_counts():
    """Given the function `fare` whose precondition is `(< cents)`, when
    the program is checked, then it is invalid and the refusal says `<`
    takes exactly 2 arguments, the program gave 1, and points at the
    precondition's own line."""
    run = check(A_PRECONDITION_WITH_A_WRONG_COUNT)

    assert_refused_for_its_count(
        run,
        "<",
        takes=2,
        got=1,
        at=site_of(A_PRECONDITION_WITH_A_WRONG_COUNT, "(< cents)"),
    )


def test_a_wrong_count_in_a_postcondition_is_refused_with_both_counts():
    """Given the same function whose postcondition is `(= result)`, when
    the program is checked, then it is invalid and the refusal says `=`
    takes exactly 2 arguments, the program gave 1, and points at the
    postcondition's own line."""
    run = check(A_POSTCONDITION_WITH_A_WRONG_COUNT)

    assert_refused_for_its_count(
        run,
        "=",
        takes=2,
        got=1,
        at=site_of(A_POSTCONDITION_WITH_A_WRONG_COUNT, "(= result)"),
    )


def test_a_wrong_count_in_a_match_clause_body_is_refused_with_both_counts():
    """Given `shade-of`, which answers a colour's shade and whose first
    clause body is `(+ tone)`, when the program is checked, then it is
    invalid and the refusal says `+` takes exactly 2 arguments, the
    program gave 1, and points at that clause."""
    run = check(A_MATCH_CLAUSE_WITH_A_WRONG_COUNT)

    assert_refused_for_its_count(
        run,
        "+",
        takes=2,
        got=1,
        at=site_of(A_MATCH_CLAUSE_WITH_A_WRONG_COUNT, "(+ tone)"),
    )


def test_correct_operators_in_all_three_of_those_places_are_accepted():
    """Control: one program whose precondition, postcondition and both
    `match` clause bodies write their operators with the number of
    arguments the language gives them - including operators nested
    inside one another - is accepted, and its example answers 4."""
    assert_accepted(
        check(CORRECT_OPERATORS_IN_A_CONTRACT_AND_A_MATCH),
        "a program with correct operators in a precondition, a postcondition and "
        "two match clause bodies",
    )


def test_that_accepted_program_still_runs_its_example():
    """The same program again: its declared example is run and passes,
    so the contract and the clauses it accepts are the ones that
    actually answer for a colour."""
    response = examples(CORRECT_OPERATORS_IN_A_CONTRACT_AND_A_MATCH).response()

    assert response.get("status") == "completed", (
        f"the example of a program whose operators are all written correctly was "
        f"not run: {response}. Only a wrongly written operator call may make a "
        "program invalid."
    )
    results = (response.get("result") or {}).get("examples") or []
    failed = [entry for entry in results if not entry.get("passed")]
    assert len(results) == 1 and not failed, (
        f"the program declares 1 example and {len(results)} result(s) came back, "
        f"{len(failed)} of them failing: {response}. Counting arguments must not "
        "change what a correctly written operator computes."
    )
