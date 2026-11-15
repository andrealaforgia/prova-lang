"""F9.B1 -- a program that divides, and a program declared with a word
`core-0` does not have, are refused as outside this profile, and the
refusal names the construct.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program as unsupported. Each
test below also runs the same program with the one out-of-profile
construct replaced by one `core-0` has, and requires that one to be
accepted.
"""

from __future__ import annotations

from _f9_profile_fixtures import (
    OUT_OF_PROFILE,
    assert_answered_without_the_unsupported_status,
    assert_refused_at,
    assert_unsupported_naming,
    check,
)

DIVISION = OUT_OF_PROFILE["division"]
DEFSPEC = OUT_OF_PROFILE["the declaration word 'defspec'"]


def test_a_program_that_divides_is_refused_as_outside_this_profile():
    """Given a function whose body is `(/ n 1)`, when it is checked,
    then it is refused as unsupported, the refusal names division and
    the division sign and points at line 4, and the same function
    written with `(* n 1)` is accepted."""
    refusal = check(DIVISION.source)

    reason = assert_unsupported_naming(
        refusal, naming=DIVISION.naming, why="a function whose body divides"
    )
    assert_refused_at(refusal, line=DIVISION.line, why="a function whose body divides")
    assert "unbound" not in reason, (
        f"the refusal calls division an unbound name: {reason!r}. core-0 has no "
        "division at all, so the tool must say the construct is outside the "
        "profile rather than report a name it could not resolve."
    )

    assert_answered_without_the_unsupported_status(
        check(DIVISION.twin),
        expected_status=DIVISION.twin_status,
        why="the same function written with the multiplication core-0 has",
    )


def test_a_declaration_word_core_0_does_not_have_is_refused_as_outside_this_profile():
    """Given a declaration written `(defspec f ...)`, when it is
    checked, then it is refused as unsupported, the refusal names
    `defspec` and says it is a declaration form, and the identical
    declaration written `(defn f ...)` is accepted."""
    refusal = check(DEFSPEC.source)

    assert_unsupported_naming(
        refusal, naming=DEFSPEC.naming, why="a declaration written with 'defspec'"
    )
    assert_refused_at(
        refusal, line=DEFSPEC.line, why="a declaration written with 'defspec'"
    )

    assert_answered_without_the_unsupported_status(
        check(DEFSPEC.twin),
        expected_status=DEFSPEC.twin_status,
        why="the same declaration written with the 'defn' core-0 has",
    )
