"""Acceptance test for F5's third hiding case: a binding spelled like a
builtin operator is refused.

SPEC.md lines 145-147: a binding must not shadow a visible value
binding, function or builtin. The builtin operators are the builtins a
value binding can reach: a program that bound `not` would leave a
reader unable to tell the operator from the binding.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every `let`. The control below runs
the same program with the binder renamed and requires it to be
accepted.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    LET_HIDING_A_BUILTIN_OPERATOR,
    LET_NOT_HIDING_A_BUILTIN_OPERATOR,
    SHADOWED_BINDING_CATEGORY,
    assert_accepted,
    assert_refused,
    check,
)


def test_a_let_spelled_like_a_builtin_operator_is_refused():
    """Given a function whose body is `(let ((not (+ n 5))) not)`, when
    the program is checked, then it is invalid and the refusal names the
    binding `not` and the builtin operator it hides."""
    run = check(LET_HIDING_A_BUILTIN_OPERATOR)

    assert_refused(
        run,
        SHADOWED_BINDING_CATEGORY,
        ["not", "builtin operator"],
        at=(4, 3),
        saying=(
            "the let binding 'not' introduced by the 'let' at line 4 column 3 hides "
            "the builtin operator 'not'"
        ),
    )


def test_the_same_program_with_another_binder_is_accepted():
    """Control: the same function whose `let` binds `bumped` instead of
    `not` is accepted, so the refusal above is about the builtin and not
    about the `let`."""
    assert_accepted(
        check(LET_NOT_HIDING_A_BUILTIN_OPERATOR),
        "a let binding that hides no builtin",
    )
