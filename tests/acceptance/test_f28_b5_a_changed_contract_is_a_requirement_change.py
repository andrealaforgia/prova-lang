"""F28 criterion 6 -- the Owner tries to make the reservation component
pass by weakening a guarantee, by strengthening a precondition and by
deleting a declared example. Two of the three attempts do reach the word
'verified'. What the answer reports is that the proofs rest on contracts
that are not the ones they rested on before: a requirement change, not an
implementation repair.

The law: weakening a guarantee, strengthening a precondition or deleting
an example cannot count as an implementation repair under the unchanged
claim version (SPEC.md lines 307-318). The mechanism is modest and is not
a diff tool: every machine answer carries a digest of the contracts its
proofs rest on, so two runs can be compared, and says that a proof over a
changed contract certifies the changed contract.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the digest were taken over the whole source, which would
move for every edit. The second test below requires it to stand still for
two faults that change a body alone.
"""

from __future__ import annotations

import pytest

import _f28_broken_guard_fixtures as broken


@pytest.mark.parametrize("label,make", broken.THE_THREE_ATTEMPTS)
def test_an_attempt_to_pass_by_changing_a_requirement_moves_the_digest(label, make):
    """Given the reservation component with a guarantee weakened, a
    precondition strengthened or a declared example deleted, when the
    Owner asks the tool to verify it with the descriptor this repository
    ships, then the digest of the contracts the proofs rest on is not the
    digest the unchanged component answers."""
    changed_source, descriptor = make()
    shipped_source, _ = broken.shipped_reservation()

    changed = broken.contracts_digest_of(
        broken.ask_to_verify(changed_source, descriptor)
    )
    shipped = broken.contracts_digest_of(
        broken.ask_to_verify(shipped_source, descriptor)
    )

    assert shipped, (
        "WHAT: the answer about the unchanged reservation component carries "
        "no digest of the contracts its proofs rest on. "
        "WHY: two runs can be compared only if both say what they rested on; "
        "with nothing to compare, a requirement change passes as a repair. "
        f"HOW: carry the digest under {broken.THE_CONTRACTS_FIELD!r}."
    )
    assert changed, (
        f"WHAT: the answer about the component with {label} carries no "
        "digest of the contracts its proofs rest on. "
        "WHY: the attempt to pass is exactly the run whose contracts the "
        "Owner must be able to compare. "
        f"HOW: carry the digest under {broken.THE_CONTRACTS_FIELD!r}."
    )
    assert changed != shipped, (
        f"WHAT: the component with {label} answers the same contracts "
        f"digest {changed!r} as the unchanged component. "
        "WHY: SPEC.md lines 307-318 forbid counting a weakened guarantee, a "
        "strengthened precondition or a deleted example as an "
        "implementation repair; a digest that does not move lets the Owner "
        "read the second run as the first one repaired. "
        "HOW: take the digest over the signatures, the preconditions, the "
        "guarantees and the declared examples of the functions the "
        "descriptor's roles name."
    )


@pytest.mark.parametrize("label,make", broken.THE_FAULTS_OF_A_BODY_ALONE)
def test_a_fault_of_a_body_alone_leaves_the_digest_where_it_was(label, make):
    """Given a fault that changes a body and no contract -- the
    acceptance flag flipped, or a body that always rejects -- when the
    Owner asks the tool to verify it, then the digest of the contracts
    the proofs rest on is the one the unchanged component answers."""
    faulty_source, descriptor = make()
    shipped_source, _ = broken.shipped_reservation()

    faulty = broken.contracts_digest_of(
        broken.ask_to_verify(faulty_source, descriptor)
    )
    shipped = broken.contracts_digest_of(
        broken.ask_to_verify(shipped_source, descriptor)
    )

    assert faulty == shipped and shipped, (
        f"WHAT: the component with {label}, whose contracts are the shipped "
        f"ones, answers the digest {faulty!r} and the unchanged component "
        f"answers {shipped!r}. "
        "WHY: the digest is what tells a requirement change from an "
        "implementation fault; one that moves for a body makes every "
        "comparison say 'changed' and tells the Owner nothing. "
        "HOW: take the digest over the contracts alone -- signatures, "
        "preconditions, guarantees and declared examples -- and never over "
        "a body."
    )


def test_the_answer_says_a_proof_over_a_changed_contract_certifies_that_contract():
    """Given an attempt that reaches 'verified' by weakening a guarantee,
    when the Owner reads what the answer says about the contracts its
    proofs rest on, then it says the proof certifies the contracts as
    they now stand, and the tool publishes that a weakened guarantee, a
    strengthened precondition or a deleted example is a requirement
    change and not an implementation repair."""
    source, descriptor = broken.with_a_weakened_guarantee()

    answered = broken.ask_to_verify(source, descriptor)

    rested_on = broken.machine_block_of(answered).get(broken.THE_CONTRACTS_FIELD) or {}
    said = broken.as_text(rested_on)
    assert "certif" in said, (
        f"WHAT: what the answer says about the contracts its proofs rest on "
        f"never says what the proof certifies: {rested_on}. "
        "WHY: an Owner reading 'verified' beside a weakened guarantee must "
        "be told that the proof is about the contract as it now stands, not "
        "about the one that was approved. "
        "HOW: say beside the digest that a proof over a changed contract "
        "certifies the changed contract."
    )
    published = broken.published_requirement_integrity()
    whole = broken.as_text(published)
    for attempt in ("guarantee", "precondition", "example"):
        assert attempt in whole, (
            f"WHAT: the tool publishes nothing about {attempt!r} under "
            f"{broken.THE_PUBLISHED_INTEGRITY!r}: {published}. "
            "WHY: an agent reads what this tool promises from the manifest; "
            "the three attempts SPEC.md lines 313-316 name must be named "
            "there as requirement changes. HOW: publish the rule."
        )
    assert "repair" in whole, (
        f"WHAT: what the tool publishes about requirement integrity never "
        f"says these are not implementation repairs: {published}. "
        "WHY: that is the distinction criterion 6 is about. "
        "HOW: say it in the published rule."
    )
