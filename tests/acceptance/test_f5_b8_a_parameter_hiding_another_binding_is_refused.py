"""Acceptance test for the owner's reading of SPEC.md line 145: a
parameter is a binding too, so a parameter may hide neither a declared
function nor an earlier parameter of its own signature.

SPEC.md lines 145-147: parameters, sequential `let` bindings and pattern
variables introduce lexical value bindings, and a binding must not
shadow a visible value binding, function or builtin.

Recorded as the owner's answer on this delivery: the hiding rule governs
parameters as well, not only `let` bindings and pattern variables.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program with a parameter. Each
refused program below has a twin that differs only in that parameter's
name and is required to be accepted.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    PARAMETER_HIDING_A_FUNCTION,
    PARAMETER_WITH_ITS_OWN_NAME,
    SHADOWED_BINDING_CATEGORY,
    TWO_PARAMETERS_WITH_ONE_NAME,
    TWO_PARAMETERS_WITH_TWO_NAMES,
    assert_accepted,
    assert_refused,
    check,
)


def test_a_parameter_spelled_like_a_declared_function_is_refused():
    """Given a program that declares the function `offset` and a second
    function whose 1 parameter is also `offset`, when the program is
    checked, then it is invalid and the refusal names the parameter
    `offset` and the function it hides."""
    run = check(PARAMETER_HIDING_A_FUNCTION)

    assert_refused(
        run,
        SHADOWED_BINDING_CATEGORY,
        ["offset", "function"],
        at=(6, 7),
        saying=(
            "the parameter 'offset' of the function declared at line 6 column 7 "
            "hides the declared function 'offset'"
        ),
    )


def test_the_same_program_whose_parameter_is_free_is_accepted():
    """Control: the same program whose parameter is `amount` instead of
    `offset` is accepted, so the refusal above is about the hidden
    function and not about the parameter."""
    assert_accepted(
        check(PARAMETER_WITH_ITS_OWN_NAME), "a parameter with a name of its own"
    )


def test_a_signature_whose_second_parameter_repeats_the_first_is_refused():
    """Given the function `gap` whose 2 parameters are both named
    `edge`, when the program is checked, then it is invalid and the
    refusal names the parameter `edge`."""
    run = check(TWO_PARAMETERS_WITH_ONE_NAME)

    assert_refused(
        run,
        SHADOWED_BINDING_CATEGORY,
        ["edge", "parameter"],
        at=(1, 7),
        saying=(
            "the parameter 'edge' of the function declared at line 1 column 7 hides "
            "the parameter 'edge' of the same function"
        ),
    )


def test_the_same_signature_with_two_names_is_accepted():
    """Control: the same 2-parameter function whose parameters are
    `edge` and `other` is accepted, so the refusal above is about the
    repeated spelling and not about having 2 parameters."""
    assert_accepted(
        check(TWO_PARAMETERS_WITH_TWO_NAMES), "a signature of two named parameters"
    )
