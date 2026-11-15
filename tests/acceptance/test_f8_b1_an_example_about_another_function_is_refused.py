"""Acceptance test for F8 criterion 1: a function whose only example
calls a different function is refused, and the refusal names both the
function that declares the example and the function the example calls.

SPEC.md lines 228-234: every function needs an example directly calling
that same function, and an unrelated expression cannot stand in for an
example of the function. A program whose example of `double` calls
`triple` leaves `double` with no example at all.

This is also the feature's walking skeleton: the thinnest real path from
the `prova` command's real JSON surface to the refusal a reader gets.
Drives only that surface. No imports from src/prova.

still passes if: the tool refused every program. The controls below run
the same two functions with each example about its own function and
require that program to be accepted.
"""

from __future__ import annotations

from _f8_example_subject_fixtures import (
    AN_EXAMPLE_ABOUT_ANOTHER_FUNCTION,
    EVERY_EXAMPLE_ABOUT_ITS_OWN_FUNCTION,
    TWO_EXAMPLES_BOTH_ABOUT_ANOTHER_FUNCTION,
    assert_accepted,
    assert_refused_as_an_example_of_another_function,
    check,
    examples,
)


def test_an_example_calling_a_different_function_is_refused_naming_both():
    """Given `double`, whose only example is `(example (triple 2) => 6)`,
    and `triple`, which answers 6 for 2, when the program is checked,
    then it is invalid and the refusal names `double` and `triple`."""
    run = check(AN_EXAMPLE_ABOUT_ANOTHER_FUNCTION)

    assert_refused_as_an_example_of_another_function(run, owner="double", called="triple")


def test_the_same_two_functions_with_their_own_examples_are_accepted():
    """Control: the same two functions, with `double`'s example written
    as `(example (double 2) => 4)`, are accepted, so the refusal above is
    about whose example it is and not about the program around it."""
    assert_accepted(
        check(EVERY_EXAMPLE_ABOUT_ITS_OWN_FUNCTION),
        "a program whose two functions each have an example of their own",
    )


def test_two_examples_about_another_function_are_both_reported():
    """Given `double`, whose 2 declared examples both call `triple`, when
    the program is checked, then it is invalid with 2 refusals, so a
    reader sees every example that must be repaired, not only the
    first."""
    run = check(TWO_EXAMPLES_BOTH_ABOUT_ANOTHER_FUNCTION)

    assert_refused_as_an_example_of_another_function(
        run, owner="double", called="triple", occurrences=2
    )


def test_running_the_examples_refuses_the_same_program():
    """Given the same program whose example of `double` calls `triple`,
    when its declared examples are asked to run, then the program is
    invalid and no example is reported as passing: an example about
    another function is not evidence about `double`."""
    response = examples(AN_EXAMPLE_ABOUT_ANOTHER_FUNCTION).response()

    assert response.get("status") == "invalid_program", (
        f"the examples of a program refused by `check` still ran: {response}. An "
        "example that calls another function demonstrates nothing about the function "
        "that declares it; refuse the program instead of reporting its examples as "
        "passing."
    )
    assert not response.get("result", {}).get("examples"), (
        f"a refused program still reported example results: {response}. Report no "
        "example outcome for a program the tool refuses."
    )
