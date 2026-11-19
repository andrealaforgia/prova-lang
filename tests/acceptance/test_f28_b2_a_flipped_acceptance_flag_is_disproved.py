"""F28 criterion 2 -- the Owner flips the acceptance flag of the
reservation component's Reserve branch and leaves its arithmetic alone.
The invariant still holds of every state the component reaches, and an
obligation about the outcome its contract promises is disproved; the
first transition of the component from its own initial state is already
refused, so the answer carries a reachable counterexample.

The law: a changed acceptance flag fails the contract even when the
invariant holds (SPEC.md lines 580-587), and a counterexample built by
replaying from the initialiser is the one thing called reachable
(SPEC.md lines 307-311).

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool called every disproof reachable.
test_f28_b1 requires the missing-guard answer to carry no reachable
counterexample, and test_f28_b4 requires a sound machine to carry none.
"""

from __future__ import annotations

import _f28_broken_guard_fixtures as broken


def test_the_flipped_flag_is_disproved_while_the_invariant_still_holds():
    """Given the reservation component whose Reserve branch answers the
    opposite acceptance flag and keeps its arithmetic, when the Owner
    asks the tool to verify it with the descriptor this repository ships,
    then an obligation about the outcome the contract promises is
    disproved, preservation of the invariant still stands as proved, and
    the whole is not verified."""
    source, descriptor = broken.with_the_acceptance_flag_flipped()

    answered = broken.ask_to_verify(source, descriptor)

    disproved = broken.disproved_obligations(answered)
    assert any(entry.get("function") == "step" for entry in disproved), (
        f"WHAT: nothing about the step is disproved: the disproved "
        f"obligations are "
        f"{[(e.get('kind'), e.get('function')) for e in disproved]}. "
        "WHY: criterion 2 promises the flipped acceptance flag is caught; "
        "the step tells the caller the opposite of what its own guarantee "
        "states. HOW: report the obligation about what the step answers."
    )
    assert broken.how_the_three_stand(answered).get(broken.PRESERVATION) == (
        broken.PROVED
    ), (
        f"WHAT: preservation stands as "
        f"{broken.how_the_three_stand(answered).get(broken.PRESERVATION)!r} "
        "for a source whose state arithmetic was not touched. "
        "WHY: criterion 2 is about a fault the invariant does not see; an "
        "answer that withholds preservation here would hide which part of "
        "the component is broken. HOW: keep the two obligations apart."
    )
    assert broken.aggregate_of(answered).get("result") == broken.NOT_VERIFIED, (
        f"WHAT: a component that tells the caller the opposite of its "
        f"guarantee stands as "
        f"{broken.aggregate_of(answered).get('result')!r}. "
        "WHY: the word over the whole is said only when every obligation is "
        "proved. HOW: account for the disproved obligation in that word."
    )
    shipped_source, _ = broken.shipped_reservation()
    faulty = broken.contracts_digest_of(answered)
    shipped = broken.contracts_digest_of(
        broken.ask_to_verify(shipped_source, descriptor)
    )
    assert faulty and faulty == shipped, (
        f"WHAT: the answer about the flipped body says its proofs rest on the "
        f"contracts {faulty!r} and the "
        "unchanged component says they rest on "
        f"{shipped!r}. "
        "WHY: the obligation this fault breaks is one whose text comes from "
        "the component's own guarantee, and that guarantee was not touched: "
        "an Owner comparing the two runs must see the same contracts, so "
        "this reads as an implementation fault and not as a requirement "
        "change. HOW: take the digest over the contracts of the role "
        "functions alone."
    )


def test_the_first_transition_of_the_component_is_a_reachable_counterexample():
    """Given that same source, whose step already refuses the first
    transition from the state its own initialiser answers, when the Owner
    reads the answer, then it carries a reachable counterexample naming
    that initial state and at least one transition replayed from it."""
    source, descriptor = broken.with_the_acceptance_flag_flipped()

    answered = broken.ask_to_verify(source, descriptor)

    reachable = broken.reachable_counterexample_of(answered)
    assert reachable is not None, (
        f"WHAT: the answer carries no reachable counterexample although the "
        f"component's first transition from its initial state is refused: "
        f"{broken.machine_block_of(answered)}. "
        "WHY: criterion 5 promises a validated initial state with a sequence "
        "of transitions is called a reachable counterexample, and this is "
        "one; the Owner reading only an obligation entry cannot tell that a "
        "run of the component reaches the fault. HOW: replay the declared "
        "transitions from the initialiser and report the one that is "
        "refused."
    )
    assert reachable.get("kind") == broken.A_REACHABLE_COUNTEREXAMPLE, (
        f"WHAT: the trace names its kind of evidence "
        f"{reachable.get('kind')!r}: {reachable}. "
        f"WHY: the two kinds of witness evidence are told apart by the name "
        "each carries. "
        f"HOW: name the kind {broken.A_REACHABLE_COUNTEREXAMPLE!r}."
    )
    initial = broken.ask_to_evaluate(source, descriptor["roles"]["init"], [])
    assert reachable.get("initial_state") == (initial.get("result") or {}).get(
        "value"
    ), (
        f"WHAT: the trace starts at {reachable.get('initial_state')!r} and "
        f"the initialiser answers "
        f"{(initial.get('result') or {}).get('value')!r}. "
        "WHY: only a validated initial state begins a reachable "
        "counterexample; a trace from any other state says nothing about "
        "what a run reaches. HOW: start the replay at the state the "
        "initialiser answers."
    )
    assert reachable.get("transitions"), (
        f"WHAT: the trace carries no transition at all: {reachable}. "
        "WHY: an initial state alone is not a counterexample; the sequence "
        "of transitions is what makes it reachable. HOW: carry the "
        "transitions that were replayed."
    )
