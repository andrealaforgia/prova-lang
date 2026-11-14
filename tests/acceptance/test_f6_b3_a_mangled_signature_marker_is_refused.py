"""Acceptance test for F6 criterion 3: a signature whose arrow or effect
marker is anything other than `->` and `! pure` is refused, at the line
the signature stands on -- including the signature that leaves the arrow
out altogether, which used to end the command in a crash instead of an
answer.

SPEC.md line 92: `signature ::= (sig (parameter*) -> type ! pure)`, and
lines 73-74: `->`, `!` and `=>` are reserved marker tokens used only at
their grammar positions.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every signature. The control runs the
same program with `-> Int ! pure` and requires it to be accepted.
"""

from __future__ import annotations

from _f6_spelling_fixtures import (
    SIGNATURE_WITHOUT_AN_ARROW,
    SIGNATURE_WITH_AN_UNDECLARED_EFFECT,
    SIGNATURE_WITH_A_MANGLED_EFFECT_MARKER,
    SIGNATURE_WITH_THE_EXAMPLE_ARROW,
    WELL_SPELLED,
    assert_accepted,
    assert_refused_at,
    assert_refused_naming,
    check,
)


def test_a_signature_with_no_arrow_is_refused_instead_of_crashing():
    """Given the signature `(sig ((n Int)) Int)`, which leaves out the
    arrow and the effect marker, when the program is checked, then the
    command answers with one refusal that names the `->` the signature
    must carry -- it does not crash."""
    run = check(SIGNATURE_WITHOUT_AN_ARROW)

    assert_refused_naming(
        run, naming=["->"], why="the signature '(sig ((n Int)) Int)'"
    )
    assert run.exit_code == 0, (
        f"the command exited {run.exit_code} and said {run.stderr[-600:]!r} on "
        "standard error for a signature with no arrow. A program the tool cannot "
        "read is an answer, not a crash: exit 0 with one refusal."
    )


def test_a_signature_whose_arrow_is_the_example_arrow_is_refused():
    """Given a signature written `(sig ((n Int)) => Int ! pure)`, when
    the program is checked, then it is invalid and the refusal names the
    `->` it must use instead."""
    assert_refused_naming(
        check(SIGNATURE_WITH_THE_EXAMPLE_ARROW),
        naming=["->", "'=>'"],
        why="a signature whose arrow is '=>'",
    )


def test_a_signature_whose_effect_marker_is_not_the_bang_is_refused():
    """Given a signature written `-> Int ? pure`, when the program is
    checked, then it is invalid and the refusal names the `!` the
    signature must carry."""
    assert_refused_naming(
        check(SIGNATURE_WITH_A_MANGLED_EFFECT_MARKER),
        naming=["!", "'?'"],
        why="a signature whose effect marker is '?'",
    )


def test_a_signature_declaring_an_effect_other_than_pure_is_refused():
    """Given a signature written `-> Int ! impure`, when the program is
    checked, then it is invalid and the refusal names `pure`, the only
    effect this profile declares."""
    assert_refused_naming(
        check(SIGNATURE_WITH_AN_UNDECLARED_EFFECT),
        naming=["pure", "'impure'"],
        why="a signature declaring the effect 'impure'",
    )


def test_the_refused_signature_is_placed_on_the_line_it_stands_on():
    """Given a program whose signature on line 2 carries the arrow `=>`,
    when it is checked, then the refusal is placed on line 2, so a reader
    is sent to the misspelling and not to the start of the file."""
    assert_refused_at(
        check(SIGNATURE_WITH_THE_EXAMPLE_ARROW),
        line=2,
        why="a signature whose arrow is '=>' on line 2",
    )


def test_the_same_program_with_the_defined_markers_is_accepted():
    """Control: the same program with `-> Int ! pure` is accepted, so the
    refusals above are about the markers and not about the signature."""
    assert_accepted(check(WELL_SPELLED), "a signature written '-> Int ! pure'")
