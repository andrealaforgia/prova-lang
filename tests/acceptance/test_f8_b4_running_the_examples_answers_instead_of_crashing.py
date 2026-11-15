"""Acceptance test for F8 criterion 3, read from the other side: asking
a program's examples to run must answer, whatever the examples say.

An example that writes fewer arguments than its function takes used to
end the command while its examples ran. A rule that refuses the program
at check time removes that ending: the command answers with the refusal.

This is the feature's crash case, proved from the outside through what
the command's process reports: the exit status and the JSON on standard
output, not an internal signal.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the command answered this one program by chance. The
control below asks the same operation for a program whose examples are
about their own function and requires the example outcomes back, so
"answered" means more than "did not crash".
"""

from __future__ import annotations

from _f8_example_subject_fixtures import (
    AN_EXAMPLE_WITH_NO_ARGUMENT_AT_ALL,
    A_LONE_FUNCTION_WITH_ITS_OWN_EXAMPLE,
    ARITY_MISMATCH_CATEGORY,
    assert_answered,
    categories,
    examples,
)


def test_asking_for_the_examples_of_a_program_with_too_few_arguments_is_answered():
    """Given `double`, which takes 1 argument, whose example is
    `(example (double) => 4)`, when its declared examples are asked to
    run, then the command exits 0 with one JSON answer saying the
    program is invalid, and reports no example outcome."""
    run = examples(AN_EXAMPLE_WITH_NO_ARGUMENT_AT_ALL)

    response = assert_answered(
        run, "a request for the examples of a program whose example writes 0 arguments"
    )
    assert response.get("status") == "invalid_program", (
        f"the examples of a program whose example cannot be run against its own "
        f"function were not refused: {response}. Answer with the refusal the check "
        "gives; do not try to run the example."
    )
    assert ARITY_MISMATCH_CATEGORY in categories(response), (
        f"the answer does not say what is wrong with the program, only "
        f"{categories(response)}: {response}. Carry the same refusal `check` gives."
    )
    assert not response.get("result", {}).get("examples"), (
        f"a refused program still reported example results: {response}. Report no "
        "example outcome for a program the tool refuses."
    )


def test_the_examples_of_a_program_whose_example_fits_its_function_still_run():
    """Control: given `double` whose example is `(example (double 2) => 4)`,
    when its declared examples are asked to run, then 1 example outcome
    comes back and it passed."""
    response = assert_answered(
        examples(A_LONE_FUNCTION_WITH_ITS_OWN_EXAMPLE),
        "a request for the examples of a program whose example fits its function",
    )

    results = response.get("result", {}).get("examples", [])
    assert len(results) == 1 and results[0].get("passed"), (
        f"the 1 declared example of `double` did not come back as passing: "
        f"{response}. A program whose examples are about their own functions still "
        "has its examples run."
    )
