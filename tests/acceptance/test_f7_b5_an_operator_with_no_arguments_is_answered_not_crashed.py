"""Acceptance test for F7's edge case: an operator written with no
arguments at all.

SPEC.md lines 178-189: `not` takes one `Bool` argument. A program that
writes `(not)` has nothing for the operator to work on, so asking the
tool to run that program must come back as a refusal with the two
counts, not as a command that stops without an answer.

Drives only the `prova` command's real JSON stdin/stdout surface, and
reads the command's exit status and standard error, so a crash stays
visible. No imports from src/prova.

still passes if: the tool refused every program. The companion test file
for correctly applied operators requires `(not flag)` to be accepted and
its examples to run.
"""

from __future__ import annotations

from _f7_operator_arity_fixtures import (
    ARITY_MISMATCH_CATEGORY,
    NOT_WITH_NO_ARGUMENTS,
    assert_refused_for_its_count,
    categories,
    check,
    evaluate,
    examples,
    of_category,
)


def test_a_program_whose_operator_has_no_arguments_is_refused_with_both_counts():
    """Given the function `unflagged?` whose body is `(not)`, when the
    program is checked, then it is invalid and the refusal says `not`
    takes exactly 1 argument and the program gave 0."""
    run = check(NOT_WITH_NO_ARGUMENTS)

    assert_refused_for_its_count(run, "not", takes=1, got=0)


def test_running_that_program_answers_a_refusal_instead_of_stopping():
    """Given the same program, when the user asks for `unflagged?` to be
    evaluated for `true`, then the command answers one refusal naming
    the operator and the two counts, and exits as it does for any other
    refused program."""
    run = evaluate(NOT_WITH_NO_ARGUMENTS, "unflagged?", ["true"])

    assert run.exit_code == 0, (
        "asking to run a program whose operator has no arguments stopped the "
        f"command: it exited {run.exit_code} and said {run.stderr[-400:]!r} on "
        "standard error. A program the tool will not run must come back as a "
        "refusal the caller can read, never as a crash."
    )
    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"running a program whose operator has no arguments was not refused: "
        f"{response}. A program that cannot be checked cannot be run."
    )
    refusals = of_category(response, ARITY_MISMATCH_CATEGORY)
    assert len(refusals) == 1, (
        f"expected exactly 1 refusal about the number of arguments, got "
        f"{len(refusals)} in {categories(response)}: {response}."
    )
    assert "not" in refusals[0].get("reason", ""), (
        f"the refusal does not name the operator whose arguments are missing: "
        f"{refusals[0]}."
    )


def test_asking_for_its_examples_answers_a_refusal_instead_of_stopping():
    """Given the same program, when the user asks for its declared
    examples, then the command answers the same refusal and does not
    stop: every way into the program reports the operator, not a
    crash."""
    run = examples(NOT_WITH_NO_ARGUMENTS)

    assert run.exit_code == 0, (
        "asking for the examples of a program whose operator has no arguments "
        f"stopped the command: it exited {run.exit_code} and said "
        f"{run.stderr[-400:]!r} on standard error. Answer every request with one "
        "readable response."
    )
    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"the examples of a program whose operator has no arguments were not "
        f"refused: {response}. A program that cannot be checked cannot have its "
        "examples run."
    )
    assert categories(response) == [ARITY_MISMATCH_CATEGORY], (
        f"the refusal is reported as {categories(response)}: {response}. The "
        "program's defect is the number of arguments its operator was given."
    )
