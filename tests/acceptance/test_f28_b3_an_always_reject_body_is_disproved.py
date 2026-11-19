"""F28 criterion 3 -- the Owner replaces the reservation component's step
body with one that rejects every event in every state. Every obligation
about safety stands proved, because a component that never changes its
state never leaves its invariant, and the whole is still not verified:
an obligation about acceptance is disproved.

The law: safety alone does not make a machine pass. The three inductive
obligations of SPEC.md lines 395-401 say nothing about what the component
accepts, and a component that accepts nothing fails the contract that
says when it must.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool withheld the word from everything.
test_f28_b6 requires the shipped machines proved and verified.
"""

from __future__ import annotations

import _f28_broken_guard_fixtures as broken


def test_safety_alone_does_not_verify_a_body_that_always_rejects():
    """Given the reservation component whose step rejects every event,
    when the Owner asks the tool to verify it with the descriptor this
    repository ships, then all three inductive obligations stand as
    proved, an obligation about what the step accepts is disproved, and
    the whole is not verified."""
    source, descriptor = broken.that_always_rejects()

    answered = broken.ask_to_verify(source, descriptor)

    standing = broken.how_the_three_stand(answered)
    assert set(standing.values()) == {broken.PROVED}, (
        f"WHAT: the three inductive obligations of a component that never "
        f"changes its state stand as {standing}. "
        "WHY: this test is about a fault safety cannot see; if safety itself "
        "were withheld here the test would prove nothing about acceptance. "
        "HOW: read the reason beside each entry that is not proved."
    )
    about_the_step = [
        entry
        for entry in broken.disproved_obligations(answered)
        if entry.get("function") == "step"
    ]
    assert about_the_step, (
        f"WHAT: nothing about the step is disproved although it rejects "
        f"every event: the disproved obligations are "
        f"{[(e.get('kind'), e.get('function')) for e in broken.disproved_obligations(answered)]}. "
        "WHY: criterion 3 promises an obligation about acceptance is "
        "disproved; the step's own guarantee says when it must accept. "
        "HOW: report the obligation about what the step answers."
    )
    assert broken.aggregate_of(answered).get("result") == broken.NOT_VERIFIED, (
        f"WHAT: a component that accepts nothing stands as "
        f"{broken.aggregate_of(answered).get('result')!r} with all three "
        f"inductive obligations proved. "
        "WHY: criterion 3 promises safety alone does not make it pass. "
        "HOW: account for every obligation in the word over the whole."
    )
    shipped_source, _ = broken.shipped_reservation()
    faulty = broken.contracts_digest_of(answered)
    shipped = broken.contracts_digest_of(
        broken.ask_to_verify(shipped_source, descriptor)
    )
    assert faulty and faulty == shipped, (
        f"WHAT: the answer about the body that always rejects says its "
        f"proofs rest on the contracts "
        f"{faulty!r} and the unchanged "
        "component says they rest on "
        f"{shipped!r}. "
        "WHY: the obligation about acceptance is one whose text comes from "
        "the component's own guarantee, and this fault changed no contract: "
        "the two runs must be comparable, so that deleting the guarantee "
        "instead of repairing the body cannot read as the same change. "
        "HOW: take the digest over the contracts of the role functions "
        "alone."
    )


def test_the_component_that_accepts_nothing_carries_a_reachable_counterexample():
    """Given that same source, when the Owner reads the answer, then it
    carries a reachable counterexample: the state the initialiser answers
    and the reserve the component refuses there, replayed through the
    evaluator."""
    source, descriptor = broken.that_always_rejects()

    answered = broken.ask_to_verify(source, descriptor)

    reachable = broken.reachable_counterexample_of(answered)
    assert reachable is not None, (
        f"WHAT: the answer carries no reachable counterexample although the "
        f"very first reserve of a fresh component is refused: "
        f"{broken.machine_block_of(answered)}. "
        "WHY: criterion 3 is about a fault a run reaches at once, and "
        "criterion 5 promises such a trace is the one thing called "
        "reachable. HOW: replay the declared transitions from the "
        "initialiser and report the one that is refused."
    )
    said = broken.as_text(reachable)
    assert "Reserve" in said, (
        f"WHAT: the trace names no reserve: {reachable}. "
        "WHY: the first transition a fresh reservation owes is a reserve, "
        "and that is the one this component refuses; a trace naming "
        "something else sends the Owner to the wrong event. "
        "HOW: carry the event that was replayed."
    )
    assert all(
        transition.get("what_the_run_did")
        for transition in reachable.get("transitions") or []
    ), (
        f"WHAT: a transition of the trace does not say what the run did: "
        f"{reachable}. "
        "WHY: a trace is a counterexample only because the reference "
        "semantics did something with it; a reader given only the event "
        "cannot tell what the component answered or refused. "
        "HOW: carry what running the step on that event did."
    )
