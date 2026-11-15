"""F9.B2 -- a decimal literal and a text literal are refused as outside
this profile, not as a name the tool could not resolve and not as a
value it could not read.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every literal it does not know. Each
test also runs the same program with a whole number in that position
and requires it to be accepted.
"""

from __future__ import annotations

from _f9_profile_fixtures import (
    OUT_OF_PROFILE,
    assert_answered_without_the_unsupported_status,
    assert_refused_at,
    assert_unsupported_naming,
    check,
)

DECIMAL = OUT_OF_PROFILE["a decimal literal"]
DECIMAL_IN_AN_EXAMPLE = OUT_OF_PROFILE["a decimal literal in an example"]
TEXT = OUT_OF_PROFILE["a text literal"]


def test_a_decimal_literal_is_refused_as_outside_this_profile():
    """Given a function whose body is `1.5`, when it is checked, then it
    is refused as unsupported naming the decimal literal `1.5` at line
    4, never as an unbound name, and the same function whose body is `1`
    is accepted."""
    refusal = check(DECIMAL.source)

    reason = assert_unsupported_naming(
        refusal, naming=DECIMAL.naming, why="a function whose body is 1.5"
    )
    assert_refused_at(refusal, line=DECIMAL.line, why="a function whose body is 1.5")
    assert "unbound" not in reason, (
        f"the refusal calls the decimal literal an unbound name: {reason!r}. "
        "A reader who wrote 1.5 did not misspell a name: core-0 has no decimal "
        "values at all, and the refusal must say so."
    )

    assert_answered_without_the_unsupported_status(
        check(DECIMAL.twin),
        expected_status=DECIMAL.twin_status,
        why="the same function whose body is the whole number 1",
    )


def test_a_decimal_literal_in_a_declared_example_is_refused_as_outside_this_profile():
    """Given a declared example whose expected value is `1.0`, when the
    program is checked, then it is refused as unsupported naming `1.0`
    at line 3, and the same program expecting `1` is accepted."""
    refusal = check(DECIMAL_IN_AN_EXAMPLE.source)

    reason = assert_unsupported_naming(
        refusal,
        naming=DECIMAL_IN_AN_EXAMPLE.naming,
        why="an example expecting the decimal 1.0",
    )
    assert_refused_at(
        refusal,
        line=DECIMAL_IN_AN_EXAMPLE.line,
        why="an example expecting the decimal 1.0",
    )
    assert "not a value" not in reason, (
        f"the refusal reports the decimal literal as a value it cannot read: "
        f"{reason!r}. The tool reads it well enough to name it; what it has is "
        "no decimal arithmetic, which is a profile boundary and not a misread "
        "value."
    )

    assert_answered_without_the_unsupported_status(
        check(DECIMAL_IN_AN_EXAMPLE.twin),
        expected_status=DECIMAL_IN_AN_EXAMPLE.twin_status,
        why="the same example expecting the whole number 1",
    )


def test_a_text_literal_is_refused_as_outside_this_profile():
    """Given a function whose body is `"ok"`, when it is checked, then
    it is refused as unsupported naming the text literal at line 4,
    never as an unbound name, and the same function whose body is `1` is
    accepted."""
    refusal = check(TEXT.source)

    reason = assert_unsupported_naming(
        refusal, naming=TEXT.naming, why='a function whose body is "ok"'
    )
    assert_refused_at(refusal, line=TEXT.line, why='a function whose body is "ok"')
    assert "unbound" not in reason, (
        f"the refusal calls the text literal an unbound name: {reason!r}. core-0 "
        "has no text values at all, and the refusal must say so."
    )

    assert_answered_without_the_unsupported_status(
        check(TEXT.twin),
        expected_status=TEXT.twin_status,
        why="the same function whose body is the whole number 1",
    )
