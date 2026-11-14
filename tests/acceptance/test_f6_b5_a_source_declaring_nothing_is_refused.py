"""Acceptance test for F6 criteria 5 and 6: a source with no declaration
at all is refused, and so is a function whose `(examples)` block declares
no example.

SPEC.md line 92 and the core grammar: `program ::= declaration+` and
`examples ::= (examples example+)`, so both need at least one member.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The controls require the
same source with one declaration, and the same function with one
example, to be accepted.
"""

from __future__ import annotations

from _f6_spelling_fixtures import (
    EMPTY_EXAMPLES_BLOCK,
    NOTHING_AT_ALL,
    ONLY_SPACE_AND_A_COMMENT,
    WELL_SPELLED,
    assert_accepted,
    assert_refused_naming,
    check,
)


def test_a_source_with_no_text_at_all_is_refused():
    """Given a source that is the empty text, when it is checked, then it
    is invalid and the refusal says a program must declare at least one
    type or function."""
    assert_refused_naming(
        check(NOTHING_AT_ALL),
        naming=["at least one", "deftype", "defn"],
        why="a source with no text at all",
    )


def test_a_source_of_only_a_comment_is_refused():
    """Given a source holding one comment line and blank space and no
    declaration, when it is checked, then it is invalid for the same
    reason: a comment declares nothing."""
    assert_refused_naming(
        check(ONLY_SPACE_AND_A_COMMENT),
        naming=["at least one", "deftype", "defn"],
        why="a source of one comment and blank space",
    )


def test_a_function_whose_examples_block_is_empty_is_refused():
    """Given a function whose clause is written `(examples)` with no
    example in it, when the program is checked, then it is invalid and
    the refusal names the function and asks for at least one example."""
    assert_refused_naming(
        check(EMPTY_EXAMPLES_BLOCK),
        naming=["'add-one'", "at least one example"],
        why="a function whose examples block is empty",
    )


def test_one_declaration_and_one_example_are_enough_to_be_accepted():
    """Control: the smallest well spelled program -- one function with
    one example -- is accepted, so the refusals above are about the
    missing members and not about the program."""
    assert_accepted(check(WELL_SPELLED), "one function declaring one example")
