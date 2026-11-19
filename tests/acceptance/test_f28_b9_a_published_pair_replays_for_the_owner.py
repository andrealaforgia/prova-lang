"""F28 repair -- the Owner replays the published witness independently.
A disproof is believable only if the pair the answer names really makes
the transition the answer states, so these tests take the state and the
event out of the answer and run admissibility, the step and the
projection over them through the tool's own evaluation operation,
comparing the state that comes back with the one published.

The law: the published pair, run through the public port, reaches the
published state. An answer that named a different event -- one whose step
leads somewhere else, or somewhere inside the invariant -- is caught
here, where reading the published state alone would not catch it.

And the other way round: a machine whose initialiser answers a state its
own invariant refuses has no reachable counterexample at all, whatever
its step does there, because only a validated initial state begins one.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool published no witness at all. The first test
requires preservation disproved for every counter it asks about.
"""

from __future__ import annotations

import pytest

import _f28_broken_guard_fixtures as broken
import _f28_repair_fixtures as repair

# Three counters whose step has no guarantee of its own, so the Owner can
# run the step through the public port and read the outcome it answers:
# the machines on which the whole replay can be reproduced from outside.
THE_COUNTERS = ((1, 1), (10, 3), (4, 2))


def _value_of(answered: dict) -> str:
    return (answered.get("result") or {}).get("value")


@pytest.mark.parametrize("ceiling,by", THE_COUNTERS)
def test_the_published_pair_reaches_the_published_state_when_the_owner_runs_it(
    ceiling, by
):
    """Given a counter capped at a ceiling whose step adds a fixed amount
    with no guard, when the Owner takes the state and the event from the
    disproof of preservation and runs admissibility, the step and the
    projection over them through the evaluation operation, then
    admissibility answers true, the projection of what the step answers
    is the state the witness published, and the invariant answers true of
    the state and false of that one."""
    source, descriptor = broken.a_counter_whose_step_has_no_guard(ceiling, by)
    roles = descriptor["roles"]

    answered = broken.ask_to_verify(source, descriptor)

    entry = broken.the_three_obligations(answered).get(broken.PRESERVATION) or {}
    assert entry.get("result") == broken.DISPROVED, (
        f"WHAT: preservation of a counter capped at {ceiling} whose step "
        f"adds {by} stands as {entry.get('result')!r}: {entry}. "
        "WHY: this test replays a disproof; with none there is nothing to "
        "replay. HOW: see test_f28_b1."
    )
    witness = broken.the_witness_of(entry)
    state, event = witness.get("state"), witness.get("event")
    admits = _value_of(broken.ask_to_evaluate(source, roles["admissible"], [state, event]))
    assert admits == "true", (
        f"WHAT: running {roles['admissible']!r} on the published pair "
        f"{state!r}, {event!r} answers {admits!r}. "
        "WHY: the obligation is written over an admitted transition; a pair "
        "the machine does not admit breaks nothing, so a witness naming one "
        "would be no counterexample. HOW: publish the pair the replay ran."
    )
    outcome = _value_of(broken.ask_to_evaluate(source, roles["step"], [state, event]))
    assert outcome, (
        f"WHAT: running {roles['step']!r} on the published pair answers no "
        f"value: {broken.ask_to_evaluate(source, roles['step'], [state, event])}. "
        "WHY: the Owner reproduces a disproof by running it; a pair the step "
        "cannot be run on is not the pair the answer should have published. "
        "HOW: publish the pair the replay ran."
    )
    reached = _value_of(broken.ask_to_evaluate(source, roles["state-of"], [outcome]))
    assert reached == witness.get("state_after_the_step"), (
        f"WHAT: running the step on {state!r} and {event!r} and reading the "
        f"state of what it answers gives {reached!r}, and the witness "
        f"publishes {witness.get('state_after_the_step')!r}. "
        "WHY: a witness whose event does not lead to the state it names is "
        "fabricated evidence: an Owner replaying it would reach another "
        "state, and the obligation it claims to break would not be broken. "
        "HOW: publish the event the replay actually ran the step on."
    )
    assert _value_of(
        broken.ask_to_evaluate(source, roles["invariant"], [state])
    ) == "true", (
        f"WHAT: the invariant does not hold of the published state {state!r}. "
        "WHY: the obligation assumes it. HOW: publish a state it admits."
    )
    assert _value_of(broken.ask_to_evaluate(source, roles["invariant"], [reached])) == (
        "false"
    ), (
        f"WHAT: the invariant holds of the state {reached!r} the published "
        "pair really reaches. "
        "WHY: then the pair breaks nothing and the disproof is not one. "
        "HOW: confirm the invariant on the state the step leads to before "
        "reporting a disproof."
    )


def test_the_witness_says_what_the_steps_own_contract_did_with_the_pair():
    """Given the reservation component with no upper capacity guard,
    whose step keeps a guarantee of its own that the pair breaks, when
    the Owner reads the witness, then it says what the step's own
    contract did with the pair, and the evaluation operation shows the
    same refusal."""
    source, descriptor = broken.without_the_upper_guard()

    answered = broken.ask_to_verify(source, descriptor)

    witness = broken.the_witness_of(
        broken.the_three_obligations(answered)[broken.PRESERVATION]
    )
    said = witness.get("the_step_own_contract") or ""
    assert "postcondition" in said, (
        f"WHAT: the witness does not say what the step's own contract did "
        f"with the pair: {said!r}. "
        "WHY: a reader told only that the invariant fails afterwards cannot "
        "tell whether the step would even accept the pair, and running it "
        "through the evaluation operation gives a refusal they were not "
        "warned about. HOW: run the contract-checked call and say what it "
        "did."
    )
    ran = broken.ask_to_evaluate(
        source, descriptor["roles"]["step"], [witness.get("state"), witness.get("event")]
    )
    categories = {
        diagnostic.get("category") for diagnostic in (ran.get("diagnostics") or [])
    }
    assert "postcondition_violation" in categories, (
        f"WHAT: running the step on the published pair reports "
        f"{sorted(categories)} and the witness says {said!r}. "
        "WHY: the disclosure on the witness must be what the Owner really "
        "meets at the public port. HOW: read the disclosure from a run of "
        "the contract-checked call."
    )


def test_a_machine_that_starts_outside_its_invariant_has_no_reachable_trace():
    """Given a reservation whose initialiser answers a state its own
    invariant refuses, and whose first declared transition from there the
    step answers against, when the Owner asks the tool to verify it with
    its descriptor, then the answer carries no reachable counterexample
    and the initialisation obligation is the one that is not proved."""
    source, descriptor = (
        repair.a_machine_whose_initialiser_starts_outside_the_invariant()
    )

    answered = repair.ask_to_verify(source, descriptor)

    assert repair.reachable_counterexample_of(answered) is None, (
        f"WHAT: the answer carries a reachable counterexample beginning at a "
        f"state the invariant refuses: "
        f"{repair.reachable_counterexample_of(answered)}. "
        "WHY: only a validated initial state may begin one; a trace from a "
        "state the machine's own invariant excludes says nothing about what "
        "a run reaches. HOW: run the invariant on the state the initialiser "
        "answers and build no trace when it answers false."
    )
    standing = repair.how_the_three_stand(answered)
    assert standing.get("machine_initialisation") != repair.PROVED, (
        f"WHAT: the three obligations stand as {standing} for a machine "
        "whose initialiser answers a state the invariant refuses. "
        "WHY: that is exactly what the initialisation obligation is about, "
        "and it is where the Owner must be sent. "
        "HOW: report the initialisation obligation as not proved."
    )
