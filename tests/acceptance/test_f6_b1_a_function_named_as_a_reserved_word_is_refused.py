"""Acceptance test for F6 criterion 1: a function declared with a word the
language reserves is refused, and the refusal names that word.

SPEC.md lines 65-74: keywords, builtin operator names and `result` are
reserved, so no declaration may use one as its name.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The control below runs
the same program with an unreserved name and requires it to be accepted.
"""

from __future__ import annotations

from _f6_spelling_fixtures import (
    RESERVED_WORDS,
    UNRESERVED_FUNCTION_NAME,
    assert_accepted,
    assert_refused_naming,
    check,
    program_with_function_named,
)


def test_a_function_named_let_is_refused_and_the_refusal_names_let():
    """Given a function named `let`, when the program is checked, then it
    is invalid and the refusal names `let` as a reserved word."""
    run = check(program_with_function_named("let"))

    assert_refused_naming(
        run, naming=["'let'", "reserved"], why="a function named 'let'"
    )


def test_a_function_named_if_or_match_is_refused_naming_the_word():
    """Given a function named `if`, and one named `match`, when each
    program is checked, then each is invalid and names its own word."""
    for word in ("if", "match"):
        assert_refused_naming(
            check(program_with_function_named(word)),
            naming=[repr(word), "reserved"],
            why=f"a function named {word!r}",
        )


def test_every_word_the_language_reserves_is_refused_as_a_function_name():
    """Given each word the language reserves, when a program declares a
    function of that name, then every one of them is invalid and names
    the word a reader must change.

    The reserved words are a closed list, so this walks all of them
    instead of sampling."""
    refused = [
        word
        for word in RESERVED_WORDS
        if assert_refused_naming(
            check(program_with_function_named(word)),
            naming=[repr(word), "reserved"],
            why=f"a function named {word!r}",
        )
    ]
    assert len(refused) == len(RESERVED_WORDS), (
        f"{len(refused)} of the {len(RESERVED_WORDS)} reserved words were refused "
        "as a function name. Every word the language reserves must be refused as a "
        "declared name."
    )


def test_the_same_program_with_an_unreserved_name_is_accepted():
    """Control: the same program named `step-one`, a name the language
    reserves nowhere, is accepted -- so the refusals above are about the
    reserved words and not about the program."""
    assert_accepted(
        check(program_with_function_named(UNRESERVED_FUNCTION_NAME)),
        f"a function named {UNRESERVED_FUNCTION_NAME!r}",
    )
