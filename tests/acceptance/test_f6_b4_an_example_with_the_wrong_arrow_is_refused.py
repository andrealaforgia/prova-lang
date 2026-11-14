"""Acceptance test for F6 criterion 4: a declared example whose arrow is
not `=>` is refused, at the line the example stands on.

SPEC.md lines 99-106: `example ::= (example (name value*) => value)`, and
lines 73-74: `=>` is a reserved marker token used only at that position.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every example block. The control runs
the same program with `=>` and requires it to be accepted.
"""

from __future__ import annotations

from _f6_spelling_fixtures import (
    EXAMPLE_WITH_THE_SIGNATURE_ARROW,
    WELL_SPELLED,
    assert_accepted,
    assert_refused_at,
    assert_refused_naming,
    check,
)


def test_an_example_whose_arrow_is_the_signature_arrow_is_refused():
    """Given the example `(example (add-one 41) -> 42)`, when the program
    is checked, then it is invalid and the refusal names the `=>` an
    example must use."""
    run = check(EXAMPLE_WITH_THE_SIGNATURE_ARROW)

    assert_refused_naming(
        run, naming=["=>", "'->'"], why="an example whose arrow is '->'"
    )


def test_the_refused_example_is_placed_on_its_own_line():
    """Given the same program, whose examples clause stands on line 3,
    when it is checked, then the refusal is placed on line 3."""
    assert_refused_at(
        check(EXAMPLE_WITH_THE_SIGNATURE_ARROW),
        line=3,
        why="an example whose arrow is '->' on line 3",
    )


def test_the_same_program_with_the_example_arrow_is_accepted():
    """Control: the same program with `(example (add-one 41) => 42)` is
    accepted, so the refusal above is about the arrow."""
    assert_accepted(check(WELL_SPELLED), "an example written with '=>'")
