"""Acceptance test for F5 criterion 2: a pattern variable that hides a
declared function name is refused, and the refusal names the function it
would hide.

SPEC.md lines 145-147: pattern variables introduce lexical value
bindings, and a binding must not shadow a visible value binding,
function or builtin.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program with a `match`. The
control below runs the same program with the pattern variable renamed
and requires it to be accepted.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    PATTERN_VARIABLE_HIDING_A_FUNCTION,
    PATTERN_VARIABLE_WITH_ITS_OWN_NAME,
    SHADOWED_BINDING_CATEGORY,
    assert_accepted,
    assert_refused,
    check,
)


def test_a_pattern_variable_spelled_like_a_declared_function_is_refused():
    """Given a program that declares the function `offset` and a 1-clause
    `match` whose pattern variable is also `offset`, when the program is
    checked, then it is invalid and the refusal names the pattern
    variable `offset` and the function it hides."""
    run = check(PATTERN_VARIABLE_HIDING_A_FUNCTION)

    assert_refused(run, SHADOWED_BINDING_CATEGORY, ["offset", "function"])


def test_the_same_program_whose_pattern_variable_is_free_is_accepted():
    """Control: the same program whose single clause binds `hour`
    instead of `offset` is accepted, so the refusal above is about the
    hidden function and not about the pattern."""
    assert_accepted(
        check(PATTERN_VARIABLE_WITH_ITS_OWN_NAME),
        "a clause binding one name of its own",
    )
