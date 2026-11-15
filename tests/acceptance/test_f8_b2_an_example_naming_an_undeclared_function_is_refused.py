"""Acceptance test for F8 criterion 2: an example calling a function
that does not exist is refused.

SPEC.md lines 228-234: an example must directly call the function that
declares it. A name the program never declares is not that function, so
the program is invalid, and the refusal says both which function is left
without an example and which name its example calls.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The control below runs
the same lone function with its own example and requires acceptance.
"""

from __future__ import annotations

from _f8_example_subject_fixtures import (
    AN_EXAMPLE_NAMING_A_FUNCTION_THE_PROGRAM_DOES_NOT_DECLARE,
    A_LONE_FUNCTION_WITH_ITS_OWN_EXAMPLE,
    assert_accepted,
    assert_refused_as_an_example_of_another_function,
    check,
)


def test_an_example_naming_a_function_that_does_not_exist_is_refused():
    """Given `double`, whose only example is `(example (treble 2) => 4)`
    while the program declares no `treble`, when the program is checked,
    then it is invalid and the refusal names `double` and `treble`."""
    run = check(AN_EXAMPLE_NAMING_A_FUNCTION_THE_PROGRAM_DOES_NOT_DECLARE)

    assert_refused_as_an_example_of_another_function(run, owner="double", called="treble")


def test_the_same_function_whose_example_calls_itself_is_accepted():
    """Control: the same function whose example is
    `(example (double 2) => 4)` is accepted, so the refusal above is
    about the name the example calls and not about a function standing
    alone in a program."""
    assert_accepted(
        check(A_LONE_FUNCTION_WITH_ITS_OWN_EXAMPLE),
        "a lone function whose example calls itself",
    )
