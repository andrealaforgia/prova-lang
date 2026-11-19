"""F28 criteria 1 and 4 -- the Owner removes the upper capacity guard
from the reservation component's step and asks the tool to verify it with
the descriptor this repository ships. Preservation is disproved by proof,
although no declared example of that source visits a full reservation,
and the disproof is called an induction-step witness and never a
reachable run.

The laws:
- a missing upper guard is caught by proof, not by running examples
  (SPEC.md lines 580-587);
- an induction-step witness and a reachable execution trace are
  different evidence types, and only a validated initial state with a
  sequence of transitions may be called a reachable counterexample
  (SPEC.md lines 307-311).

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool reported every preservation obligation
disproved. test_f28_b6 requires preservation proved for both shipped
machines and for the two body faults that do keep the invariant, so a
tool that disproves it everywhere fails there.
"""

from __future__ import annotations

import _f28_broken_guard_fixtures as broken


def test_the_missing_upper_guard_disproves_preservation():
    """Given the reservation component with the upper capacity guard
    removed from its step and no declared example visiting a full
    reservation, when the Owner asks the tool to verify it with the
    descriptor this repository ships, then preservation stands as
    'disproved'."""
    source, descriptor = broken.without_the_upper_guard()
    assert "(step (Reservation 2)" not in source, (
        f"WHAT: the source this test is about still declares an example of "
        f"the step at a full reservation. "
        "WHY: criterion 1 is that the missing guard is caught although no "
        "example visits a full state; with such an example the fault is "
        "caught by running it, which is the claim about three inputs this "
        "feature replaces. HOW: remove that example from the fixture."
    )

    answered = broken.ask_to_verify(source, descriptor)

    entry = broken.the_three_obligations(answered).get(broken.PRESERVATION)
    assert entry is not None, (
        f"WHAT: the answer lists no preservation obligation at all: "
        f"{[e.get('kind') for e in broken.listed_obligations(answered)]}. "
        "WHY: the one obligation that catches a missing guard is the one "
        "that says the invariant holds again after the step. "
        "HOW: list the preservation obligation and say what became of it."
    )
    assert entry.get("result") == broken.DISPROVED, (
        f"WHAT: preservation of a reservation component that steps from a "
        f"full reservation to three stands as {entry.get('result')!r}: "
        f"{entry}. "
        "WHY: criterion 1 promises the missing upper guard is caught by "
        "proof; the state 2 with a reserve leaves the invariant, and a "
        "witness of that which the evaluator confirms is a disproof. "
        "HOW: replay the whole transition on the witness -- the invariant on "
        "the state, admissibility there, the step and the invariant on the "
        "state it answers -- and report the disproof it confirms."
    )


def test_the_disproof_of_preservation_is_called_an_induction_step_witness():
    """Given that same disproof, when the Owner reads the counterexample
    beside it, then it is named an induction-step witness, it carries the
    state and the event the invariant and the admissibility predicate
    admit, it says the invariant is false of the state the step answers,
    and it says it is not a reachable trace."""
    source, descriptor = broken.without_the_upper_guard()

    answered = broken.ask_to_verify(source, descriptor)

    entry = broken.the_three_obligations(answered)[broken.PRESERVATION]
    witness = broken.the_witness_of(entry)
    assert witness.get("kind") == broken.AN_INDUCTION_STEP_WITNESS, (
        f"WHAT: the disproof of preservation carries "
        f"{witness.get('kind')!r} as its kind of evidence: {witness}. "
        f"WHY: SPEC.md lines 307-311 keep an induction-step witness and a "
        "reachable execution trace apart as different evidence types; a "
        "witness that does not say which it is leaves the Owner to guess "
        "whether a run of the component can reach it. "
        f"HOW: name the kind {broken.AN_INDUCTION_STEP_WITNESS!r}."
    )
    assert witness.get("invariant_of_the_state") is True, (
        f"WHAT: the witness does not say the invariant holds of the state it "
        f"names: {witness}. "
        "WHY: a witness of this obligation is a counterexample only if it "
        "satisfies what the obligation assumes; a state the invariant does "
        "not admit breaks nothing. HOW: run the invariant on the witness "
        "state and carry what it answered."
    )
    assert witness.get("admissible_there") is True, (
        f"WHAT: the witness does not say the event is admissible in that "
        f"state: {witness}. "
        "WHY: the obligation is written over an admitted transition; an "
        "inadmissible event is outside the domain and breaks nothing. "
        "HOW: run the admissibility predicate and carry what it answered."
    )
    assert witness.get("invariant_after_the_step") is False, (
        f"WHAT: the witness does not say the invariant is false of the state "
        f"after the step: {witness}. "
        "WHY: that is the whole of the disproof -- the conclusion the "
        "obligation states, observed false by the reference semantics. "
        "HOW: run the invariant on the state the step answers, read through "
        "the projection the descriptor names, and carry what it answered."
    )
    said = str(witness)
    assert "not a reachable" in said or "no reachable" in said, (
        f"WHAT: the induction-step witness never says it is not a reachable "
        f"trace: {witness}. "
        "WHY: criterion 4 promises the answer does not call an induction "
        "witness a reachable run; a reader told only that the invariant "
        "fails after a step may take the pair for a run the component can "
        "reach. HOW: say beside the witness that nothing here shows the "
        "state is reachable from the initialiser."
    )
    assert broken.reachable_counterexample_of(answered) is None, (
        f"WHAT: the answer carries a reachable counterexample for a source "
        f"every declared example of which replays: "
        f"{broken.reachable_counterexample_of(answered)}. "
        "WHY: criterion 5 reserves that name for a validated initial state "
        "with a sequence of transitions; nothing here was replayed from the "
        "initialiser. HOW: carry none unless one was built by replay."
    )


def test_the_witness_of_the_missing_guard_replays_for_the_owner():
    """Given the induction-step witness the answer names, when the Owner
    runs the invariant on its state and on the state after the step
    through the tool's own evaluation operation, then the invariant
    answers true before the step and false after it."""
    source, descriptor = broken.without_the_upper_guard()

    answered = broken.ask_to_verify(source, descriptor)

    witness = broken.the_witness_of(
        broken.the_three_obligations(answered)[broken.PRESERVATION]
    )
    invariant = descriptor["roles"]["invariant"]
    before = broken.ask_to_evaluate(source, invariant, [witness.get("state")])
    after = broken.ask_to_evaluate(
        source, invariant, [witness.get("state_after_the_step")]
    )
    assert (before.get("result") or {}).get("value") == "true", (
        f"WHAT: running {invariant!r} on the witness state "
        f"{witness.get('state')!r} answers "
        f"{(before.get('result') or {}).get('value')!r}: {before}. "
        "WHY: the Owner checks a disproof by running it; a witness state the "
        "invariant does not admit is no counterexample to an obligation "
        "assuming it does. HOW: name a state the invariant really admits."
    )
    assert (after.get("result") or {}).get("value") == "false", (
        f"WHAT: running {invariant!r} on the state after the step "
        f"{witness.get('state_after_the_step')!r} answers "
        f"{(after.get('result') or {}).get('value')!r}: {after}. "
        "WHY: a disproof the Owner cannot reproduce by running the program "
        "is the worst thing this tool can say; the state after the step must "
        "really leave the invariant. HOW: carry the state the step's body "
        "answered on the witness."
    )
