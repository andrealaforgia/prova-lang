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

    assert_refused(run, SHADOWED_BINDING_CATEGORY, ["cents", "parameter"])


def test_the_same_program_whose_let_uses_a_free_name_is_accepted():
    """Control: the same 1-parameter function whose `let` binds `raised`
    instead of `cents` is accepted, so the refusal above is about the
    hidden parameter and not about the `let`."""
    assert_accepted(
        check(LET_WITH_ITS_OWN_NAME), "a let binding one name of its own"
    )
