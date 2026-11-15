"""Acceptance test for F7 criterion 3: every builtin operator - the four
comparisons, equality, the three boolean operators and the three
arithmetic ones - is refused when it is written with one argument fewer
or one more than SPEC.md gives it, and each refusal carries its own two
counts.

SPEC.md lines 178-189 fix the number of arguments of all eleven
operators and state that they have no variable arity. The table the test
reads them from is written beside the fixtures, from SPEC.md.

One program holds all twenty-two wrong calls and is checked once: a
reader who writes several of them must be told about every one of them,
not only the first.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. Its companion test file
checks the same eleven operators applied correctly and requires them to
be accepted.

still passes if: the tool answered one refusal for the whole program.
The count below is compared with the number of wrong calls written, and
each call's own place and counts are looked for.
"""

from __future__ import annotations

from _f7_operator_arity_fixtures import (
    ARITY_MISMATCH_CATEGORY,
    THE_OPERATORS_AND_THEIR_ARITIES,
    categories,
    check,
    every_operator_with_a_wrong_count,
    of_category,
)


def test_each_operator_written_with_a_wrong_number_of_arguments_is_refused():
    """Given a program that writes each of the eleven operators once
    with one argument too few and once with one too many, when the
    program is checked, then it is invalid and every one of those calls
    is refused where it stands, saying how many arguments the operator
    takes and how many it was given."""
    source, wrong_calls = every_operator_with_a_wrong_count()

    run = check(source)

    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"a program in which all {len(wrong_calls)} operator calls have the wrong "
        f"number of arguments was not refused: {response}. An operator takes "
        "exactly the number of arguments the language gives it; report a program "
        "that breaks that as invalid."
    )
    refusals = of_category(response, ARITY_MISMATCH_CATEGORY)
    assert len(refusals) == len(wrong_calls), (
        f"the program writes {len(wrong_calls)} calls with the wrong number of "
        f"arguments, one for each of the {len(THE_OPERATORS_AND_THEIR_ARITIES)} "
        f"operators with one argument too few and one too many, but the tool "
        f"answered {len(refusals)} refusal(s) of that kind out of "
        f"{categories(response)}. Every wrong call is a separate repair; report "
        "them all in one pass."
    )
    for wrong in wrong_calls:
        here = [
            refusal
            for refusal in refusals
            if (refusal.get("location") or {}).get("line") == wrong.at[0]
            and (refusal.get("location") or {}).get("column") == wrong.at[1]
        ]
        assert len(here) == 1, (
            f"expected exactly one refusal at line {wrong.at[0]} column "
            f"{wrong.at[1]}, where {wrong.operator!r} is written with {wrong.got} "
            f"argument(s), got {len(here)}: {refusals}. Report each wrong call once, "
            "at its own place."
        )
        reason = here[0].get("reason", "")
        assert wrong.operator in reason, (
            f"the refusal at line {wrong.at[0]} does not name the operator "
            f"{wrong.operator!r}, so a reader cannot tell which call to repair: "
            f"{reason!r}."
        )
        assert f"takes exactly {wrong.takes}" in reason, (
            f"the refusal for {wrong.operator!r} does not say it takes exactly "
            f"{wrong.takes} argument(s), so a reader does not learn how many to "
            f"write: {reason!r}."
        )
        assert f"got {wrong.got}" in reason, (
            f"the refusal for {wrong.operator!r} does not say the program gave "
            f"{wrong.got} argument(s), so a reader cannot see what is wrong with "
            f"the call as written: {reason!r}."
        )


def test_nothing_but_the_wrong_counts_is_held_against_that_program():
    """The same program again: every operand it writes has the type its
    operator reads, so the number of arguments is the only thing the
    tool holds against it. A wrong count must not be reported as an
    operand of the wrong type as well."""
    source, wrong_calls = every_operator_with_a_wrong_count()

    response = check(source).response()

    assert set(categories(response)) == {ARITY_MISMATCH_CATEGORY}, (
        f"the program's only defect is the number of arguments of each call, but "
        f"the tool also answered {sorted(set(categories(response)) - {ARITY_MISMATCH_CATEGORY})}: "
        f"{response}. Say what is wrong, and nothing else."
    )
