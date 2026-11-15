"""Acceptance test for F8 criterion 2: an example calling a function
that does not exist is refused, and so is an example whose call names
something that is not a function at all.

SPEC.md lines 228-234: an example must directly call the function that
declares it. A name the program never declares is not that function, so
the program is invalid, and the refusal says both which function is left
without an example and which name its example calls. A declared
constructor and a builtin operator are not functions either: the refusal
says so of each, and offers no repair that would send a reader to a
function that is not there.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The control below runs
the same lone function with its own example and requires acceptance.
"""

from __future__ import annotations

from _f8_example_subject_fixtures import (
    AN_EXAMPLE_NAMING_A_FUNCTION_THE_PROGRAM_DOES_NOT_DECLARE,
    AN_EXAMPLE_WHOSE_CALL_IS_AN_OPERATOR,
    AN_EXAMPLE_WHOSE_CALL_IS_A_CONSTRUCTOR,
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

    assert_refused_as_an_example_of_another_function(
        run, owner="double", called="treble", calls_a_declared_function=False
    )


def test_the_same_function_whose_example_calls_itself_is_accepted():
    """Control: the same function whose example is
    `(example (double 2) => 4)` is accepted, so the refusal above is
    about the name the example calls and not about a function standing
    alone in a program."""
    assert_accepted(
        check(A_LONE_FUNCTION_WITH_ITS_OWN_EXAMPLE),
        "a lone function whose example calls itself",
    )


def test_an_example_calling_a_declared_constructor_is_refused_the_same_way():
    """Given `double`, whose example is `(example (Box 3) => 4)` while
    `Box` is a declared constructor and not a function, when the program
    is checked, then it is invalid and the refusal says `Box` is no
    function this program declares, so a reader is not sent to look for
    a function `Box`."""
    run = check(AN_EXAMPLE_WHOSE_CALL_IS_A_CONSTRUCTOR)

    assert_refused_as_an_example_of_another_function(
        run, owner="double", called="Box", calls_a_declared_function=False
    )


def test_an_example_whose_call_is_a_builtin_operator_is_refused_the_same_way():
    """Given `double`, whose example is `(example (+ 2 2) => 4)`, when
    the program is checked, then it is invalid: `+` is a builtin
    operator, not a function of this program, and an expression that is
    not a call of `double` cannot stand in for its example."""
    run = check(AN_EXAMPLE_WHOSE_CALL_IS_AN_OPERATOR)

    assert_refused_as_an_example_of_another_function(
        run, owner="double", called="+", calls_a_declared_function=False
    )
