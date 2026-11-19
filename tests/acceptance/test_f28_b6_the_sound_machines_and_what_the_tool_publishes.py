"""F28's two promises that nothing else moved and that nothing is
emitted unpublished: the hour clock and the reservation component as this
repository ships them stay proved and verified with the new replay in
place, and every kind of witness evidence the tool emits is published in
the manifest.

The laws:
- a replay that confirms a disproof confirms none for a machine that is
  sound: both shipped machines keep all three obligations proved and the
  word over the whole;
- published equals emitted: the kinds of evidence an answer names are
  exactly the kinds the manifest lists.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool published a kind it never emits and emitted
none at all. The set below is compared in both directions and the other
F28 tests require both new kinds to be emitted.
"""

from __future__ import annotations

import pytest

import _f28_broken_guard_fixtures as broken


@pytest.mark.parametrize("machine", broken.MACHINES)
def test_a_machine_this_repository_ships_stays_proved_and_verified(machine):
    """Given one of the two machines this repository ships, when the
    Owner asks the tool to verify it with its own descriptor, then all
    three inductive obligations stand as proved and the whole is
    verified, as they were before a disproof could be confirmed."""
    source, descriptor = broken.shipped_machine(machine)

    answered = broken.ask_to_verify(source, descriptor)

    standing = broken.how_the_three_stand(answered)
    assert standing == {kind: broken.PROVED for kind in broken.THE_THREE}, (
        f"WHAT: the three obligations of the {machine} stand as {standing}. "
        "WHY: a replay that turns a refuted obligation into a disproof must "
        "leave a sound machine exactly where it was. "
        "HOW: read the reason beside each entry that is not proved."
    )
    assert broken.aggregate_of(answered).get("result") == broken.VERIFIED, (
        f"WHAT: the {machine} stands as "
        f"{broken.aggregate_of(answered).get('result')!r}. "
        "WHY: both shipped machines were verified before this feature and "
        "neither was changed. HOW: read the obligations left undischarged."
    )
    assert broken.contracts_digest_of(answered), (
        f"WHAT: the verified answer about the {machine} does not say which "
        f"contracts its proofs rest on: {broken.machine_block_of(answered)}. "
        "WHY: the word 'verified' is the one an Owner keeps and compares "
        "later; an answer that does not say what it certified cannot be "
        "compared with the next run at all. "
        f"HOW: carry the digest under {broken.THE_CONTRACTS_FIELD!r} in "
        "every machine answer, proved or not."
    )


def test_the_preservation_entry_of_a_sound_machine_says_what_a_replay_confirms():
    """Given the reservation component as this repository ships it, when
    the Owner reads its preservation entry, then it stands as proved and
    says that a witness of this obligation is confirmed by replaying the
    whole transition, and that a witness it cannot confirm leaves the
    obligation unsettled."""
    source, descriptor = broken.shipped_reservation()

    answered = broken.ask_to_verify(source, descriptor)

    entry = broken.the_three_obligations(answered)[broken.PRESERVATION]
    said = broken.as_text(entry)
    assert "replay" in said, (
        f"WHAT: the preservation entry never says what a replay of a witness "
        f"would do: {entry}. "
        "WHY: F26 published beside this obligation that this tool confirms no "
        "witness for it, and that is no longer true; an entry that keeps the "
        "old sentence tells the Owner a disproof cannot be reported when it "
        "can. HOW: say that a witness is confirmed by replaying the "
        "invariant, the admissibility predicate and the step."
    )
    assert "confirms no witness" not in said and "confirms a witness by" not in said, (
        f"WHAT: the preservation entry still carries the sentence F26 "
        f"published, that this tool confirms no witness for this obligation: "
        f"{entry}. "
        "WHY: that sentence is no longer true -- a witness of preservation "
        "is now confirmed by replaying the whole transition -- and an entry "
        "that keeps it tells the Owner a disproof cannot be reported when it "
        "can. HOW: replace the sentence with the one that says what the "
        "replay of this obligation does."
    )
    assert "unsettled" in said or "unknown" in said, (
        f"WHAT: the preservation entry does not say what becomes of a "
        f"witness the replay does not confirm: {entry}. "
        "WHY: the Owner must know the word is withheld rather than turned "
        "into a disproof when the replay says nothing. "
        "HOW: say that an unconfirmed witness leaves the obligation "
        "unsettled."
    )


def test_every_kind_of_witness_evidence_the_tool_emits_is_published():
    """Given the three faulty copies of the reservation component, when
    the Owner reads every kind of witness evidence their answers name and
    the kinds the manifest publishes, then the two sets are the same and
    each published kind says whether it claims a run can reach it."""
    emitted = set()
    for _, make in broken.THE_THREE_FAULTS:
        source, descriptor = make()
        emitted |= broken.every_kind_named_in(broken.ask_to_verify(source, descriptor))

    published = broken.published_witness_kinds()

    assert emitted, (
        "WHAT: the three faulty copies of the reservation component name no "
        "kind of witness evidence at all. "
        "WHY: this test compares what is published with what is emitted; "
        "with nothing emitted it would pass against a tool that publishes "
        "anything. HOW: see test_f28_b1 and test_f28_b3."
    )
    assert emitted <= set(published), (
        f"WHAT: the answers name the kinds {sorted(emitted)} and the "
        f"manifest publishes {sorted(published)}. "
        "WHY: an agent reads what a kind means from the manifest; a kind "
        "emitted and not published is a word the reader cannot look up. "
        f"HOW: publish every kind under {broken.THE_PUBLISHED_KINDS!r}."
    )
    assert set(published) <= emitted | {broken.A_REACHABLE_COUNTEREXAMPLE}, (
        f"WHAT: the manifest publishes {sorted(published)} and the answers "
        f"name {sorted(emitted)}. "
        "WHY: published equals emitted; a kind published and never emitted "
        "is a promise nothing keeps. HOW: publish the kinds this tool "
        "really carries."
    )
    for kind, says in published.items():
        assert "claims_reachability" in says, (
            f"WHAT: the published kind {kind!r} does not say whether it "
            f"claims a run can reach it: {says}. "
            "WHY: that is the one thing SPEC.md lines 307-311 keep the two "
            "kinds apart by. HOW: publish it for every kind."
        )
    reachable = published.get(broken.A_REACHABLE_COUNTEREXAMPLE) or {}
    witness = published.get(broken.AN_INDUCTION_STEP_WITNESS) or {}
    assert reachable.get("claims_reachability") is True, (
        f"WHAT: the published {broken.A_REACHABLE_COUNTEREXAMPLE!r} says "
        f"{reachable.get('claims_reachability')!r} about reachability: "
        f"{reachable}. "
        "WHY: that kind is the only one this tool may claim reachability "
        "for. HOW: publish it as claiming reachability."
    )
    assert witness.get("claims_reachability") is False, (
        f"WHAT: the published {broken.AN_INDUCTION_STEP_WITNESS!r} says "
        f"{witness.get('claims_reachability')!r} about reachability: "
        f"{witness}. "
        "WHY: an induction-step witness is not a reachable trace and must "
        "not be published as one. HOW: publish it as claiming none."
    )
