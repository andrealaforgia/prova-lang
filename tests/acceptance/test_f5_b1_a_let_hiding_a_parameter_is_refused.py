"""Acceptance test for F5 criterion 1: a `let` that binds a name already
bound as a parameter is refused, and the refusal names the binding it
would hide.

SPEC.md lines 145-147: parameters and sequential `let` bindings
introduce lexical value bindings, and a binding must not shadow a
visible value binding.

This is also the feature's walking skeleton: the thinnest real path from
the `prova` command's real JSON surface to the refusal a reader gets.
Drives only that surface. No imports from src/prova.

still passes if: the tool refused every program. The control below runs
the same program with the `let` binder renamed and requires it to be
accepted.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    LET_HIDING_A_PARAMETER,
    LET_HIDING_A_PARAMETER_INSIDE_AN_ARGUMENT,
    LET_INSIDE_AN_ARGUMENT_WITH_ITS_OWN_NAME,
    LET_WITH_ITS_OWN_NAME,
    SHADOWED_BINDING_CATEGORY,
    assert_accepted,
    assert_refused,
    check,
)


def test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it():
    """Given the function `fare` whose parameter is `cents` and whose
    body binds `cents` again in a `let`, when the program is checked,
    then it is invalid and the refusal names both the `let` binding
    `cents` and the parameter `cents` it hides."""
    run = check(LET_HIDING_A_PARAMETER)

    assert_refused(
        run,
        SHADOWED_BINDING_CATEGORY,
        ["cents", "parameter"],
        at=(4, 3),
        saying=(
            "the let binding 'cents' introduced by the 'let' at line 4 column 3 "
            "hides the parameter 'cents' of the same function"
        ),
    )


def test_the_same_program_whose_let_uses_a_free_name_is_accepted():
    """Control: the same 1-parameter function whose `let` binds `raised`
    instead of `cents` is accepted, so the refusal above is about the
    hidden parameter and not about the `let`."""
    assert_accepted(
        check(LET_WITH_ITS_OWN_NAME), "a let binding one name of its own"
    )


def test_a_let_written_inside_an_argument_is_refused_as_well():
    """Given the same parameter `cents` and a `let` written inside the
    first argument of `+`, when the program is checked, then it is
    invalid: a binding is read wherever it stands, not only when it is
    the whole body."""
    run = check(LET_HIDING_A_PARAMETER_INSIDE_AN_ARGUMENT)

    assert_refused(run, SHADOWED_BINDING_CATEGORY, ["cents"], at=(4, 6))


def test_the_same_argument_with_a_free_binder_is_accepted():
    """Control: the same expression whose inner `let` binds `one` is
    accepted, so the refusal above is about the hidden parameter and not
    about binding inside an argument."""
    assert_accepted(
        check(LET_INSIDE_AN_ARGUMENT_WITH_ITS_OWN_NAME),
        "a let inside an argument binding a name of its own",
    )
