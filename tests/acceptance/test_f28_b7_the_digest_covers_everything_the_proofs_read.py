"""F28 repair -- what the digest of the contracts a machine's proofs rest
on has to cover. A proof about a role function is a proof over the
contracts of every function it calls and over the types its signatures
name, so an edit to any of those is a requirement change and must be
visible as one; an edit to a body or a comment is not.

The law: the digest moves when and only when what is required of the
machine moves. Deleting a called helper's guarantee, replacing its
failing example, widening the event type and renaming a parameter of a
contract all move it; rewriting a body and adding comments do not.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the digest were taken over the whole source, which
moves for everything. The second test below requires it to stand still
for a rewritten body and for added comments.
"""

from __future__ import annotations

import pytest

import _f28_repair_fixtures as repair


def _digest_of(made) -> str:
    source, descriptor = made()
    return repair.contracts_digest_of(repair.ask_to_verify(source, descriptor))


@pytest.mark.parametrize("label,make", repair.THE_REQUIREMENT_EDITS)
def test_an_edit_to_anything_the_proofs_read_moves_the_digest(label, make):
    """Given the reservation component whose step calls a helper, when
    the Owner deletes the helper's guarantee, replaces its failing
    example, adds a third event variant or renames a parameter the
    helper's contract is written over, then the digest of the contracts
    the proofs rest on is not the one the unedited machine answers."""
    unedited = _digest_of(repair.the_reservation_with_a_helper)

    edited = _digest_of(make)

    assert unedited, (
        "WHAT: the unedited machine answers no contracts digest. "
        "WHY: two runs can be compared only if both say what they rested on. "
        "HOW: carry the digest in every machine answer."
    )
    assert edited != unedited, (
        f"WHAT: the machine with {label} answers the same digest {edited!r} "
        f"as the unedited one. "
        "WHY: a proof about the step is a proof over the contracts of every "
        "function it calls and over the types its signature names; an edit "
        "to one of those changes what is required of the machine, and a "
        "digest that does not move lets it read as an implementation repair "
        "(SPEC.md lines 313-316). HOW: cover every function reachable from "
        "the roles through a call, and every type a covered signature names."
    )


@pytest.mark.parametrize("label,make", repair.THE_EDITS_THAT_REQUIRE_NOTHING_NEW)
def test_an_edit_that_requires_nothing_new_leaves_the_digest_where_it_was(
    label, make
):
    """Given the same machine, when the Owner rewrites one body or adds
    comments and blank lines, then the digest of the contracts the proofs
    rest on is exactly the one the unedited machine answers."""
    unedited = _digest_of(repair.the_reservation_with_a_helper)

    edited = _digest_of(make)

    assert edited == unedited and unedited, (
        f"WHAT: the machine with {label} answers the digest {edited!r} and "
        f"the unedited one answers {unedited!r}. "
        "WHY: the digest is what tells a requirement change from an "
        "implementation fault; one that moves for a body or a comment says "
        "'changed' for every edit and so says nothing. "
        "HOW: cover contracts, examples and type declarations, and never a "
        "body, a comment or whitespace."
    )


def test_the_answer_says_which_functions_the_digest_covered():
    """Given the machine whose step calls a helper, when the Owner reads
    what the answer says about the contracts its proofs rest on, then the
    helper is named among the functions reached and the covering says
    that parameter names and type declarations are part of it."""
    source, descriptor = repair.the_reservation_with_a_helper()

    answered = repair.ask_to_verify(source, descriptor)

    rested_on = (
        repair.machine_block_of(answered).get("contracts_the_proofs_rest_on") or {}
    )
    assert "increment" in (rested_on.get("reaches") or []), (
        f"WHAT: the answer says the digest reaches "
        f"{rested_on.get('reaches')!r}, which does not name the helper the "
        "step calls. "
        "WHY: an Owner comparing two digests must know what a moved digest "
        "could be about; a digest whose reach is not stated cannot be acted "
        "on. HOW: publish the functions the walk reached."
    )
    covered = str(rested_on.get("what_is_covered") or "")
    for named in ("parameter", "variant"):
        assert named in covered, (
            f"WHAT: what the answer says is covered does not mention "
            f"{named!r}: {covered!r}. "
            "WHY: a reader has to know that renaming a parameter or adding a "
            "variant moves the digest, or they will read a moved digest as "
            "something else. HOW: say what the signature and the type "
            "declarations contribute."
        )
