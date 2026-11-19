"""F28 criterion 5 -- what this tool is willing to call a reachable
counterexample, and what it refuses to call one: a validated initial
state with a sequence of transitions replayed from the initialiser, and
nothing else.

The law: an induction-step witness and a reachable execution trace are
different evidence types; only a validated initial state and transition
sequence may be called a reachable counterexample (SPEC.md lines
307-311).

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool never emitted a reachable counterexample at
all. test_f28_b2 and test_f28_b3 require one for the two sources whose
first transition is refused.
"""

from __future__ import annotations

import pytest

import _f28_broken_guard_fixtures as broken


def test_a_disproof_that_was_not_replayed_from_the_initialiser_is_not_reachable():
    """Given the source whose upper guard is missing, whose preservation
    is disproved by an induction-step witness and every declared
    transition of which replays, when the Owner reads the answer, then
    nothing in it is called a reachable counterexample."""
    source, descriptor = broken.without_the_upper_guard()

    answered = broken.ask_to_verify(source, descriptor)

    assert broken.how_the_three_stand(answered).get(broken.PRESERVATION) == (
        broken.DISPROVED
    ), (
        f"WHAT: preservation stands as "
        f"{broken.how_the_three_stand(answered).get(broken.PRESERVATION)!r}, "
        "so this test does not read a disproof at all. "
        "WHY: the promise is about a disproof that is not reachable; with no "
        "disproof the reading below says nothing. "
        "HOW: see test_f28_b1 for the disproof this test depends on."
    )
    named = broken.every_kind_named_in(answered)
    assert broken.A_REACHABLE_COUNTEREXAMPLE not in named, (
        f"WHAT: the answer about a disproof established by one step from an "
        f"arbitrary admitted state names the kinds {sorted(named)}. "
        "WHY: criterion 4 promises the answer does not call an induction "
        "witness a reachable run; nothing here replayed the component from "
        "its initialiser. HOW: name that kind only for a trace that was."
    )
    assert broken.AN_INDUCTION_STEP_WITNESS in named, (
        f"WHAT: the answer names the kinds {sorted(named)} and not "
        f"{broken.AN_INDUCTION_STEP_WITNESS!r}. "
        "WHY: the evidence must say which type it is, not merely which type "
        "it is not. HOW: name the kind on the witness."
    )


def test_a_reachable_counterexample_is_a_validated_initial_state_and_transitions():
    """Given the source that always rejects, whose first transition from
    its initialiser is refused, when the Owner reads the trace the answer
    carries, then it names the state the initialiser answers, that state
    satisfies the invariant when the Owner runs it, and the trace carries
    the transitions that were replayed."""
    source, descriptor = broken.that_always_rejects()

    answered = broken.ask_to_verify(source, descriptor)

    reachable = broken.reachable_counterexample_of(answered)
    assert reachable is not None, (
        f"WHAT: no reachable counterexample to read: "
        f"{broken.machine_block_of(answered)}. "
        "WHY: this test reads what makes a trace reachable; with no trace it "
        "says nothing. HOW: see test_f28_b3."
    )
    initial = broken.ask_to_evaluate(source, descriptor["roles"]["init"], [])
    start = reachable.get("initial_state")
    assert start == (initial.get("result") or {}).get("value"), (
        f"WHAT: the trace starts at {start!r} and the initialiser answers "
        f"{(initial.get('result') or {}).get('value')!r}. "
        "WHY: a trace from a state no initialiser answers is not reachable. "
        "HOW: start at the state the initialiser answers."
    )
    admits = broken.ask_to_evaluate(source, descriptor["roles"]["invariant"], [start])
    assert (admits.get("result") or {}).get("value") == "true", (
        f"WHAT: running the invariant on the state the trace starts at "
        f"answers {(admits.get('result') or {}).get('value')!r}: {admits}. "
        "WHY: only a validated initial state may begin a reachable "
        "counterexample; a start the invariant refuses is not validated. "
        "HOW: check the initial state against the invariant before calling "
        "the trace reachable."
    )
    assert len(reachable.get("transitions") or []) >= 1, (
        f"WHAT: the trace carries {len(reachable.get('transitions') or [])} "
        f"transitions: {reachable}. "
        "WHY: a state with no transition is not an execution. "
        "HOW: carry the sequence that was replayed."
    )


@pytest.mark.parametrize("machine", broken.MACHINES)
def test_a_machine_this_repository_ships_is_called_no_counterexample_at_all(machine):
    """Given one of the two machines this repository ships, when the
    Owner asks the tool to verify it with its own descriptor, then the
    answer names neither kind of counterexample."""
    source, descriptor = broken.shipped_machine(machine)

    answered = broken.ask_to_verify(source, descriptor)

    named = broken.every_kind_named_in(answered)
    assert named == set(), (
        f"WHAT: the answer about the {machine} names the kinds of "
        f"counterexample {sorted(named)}. "
        "WHY: a sound machine has no counterexample of either kind; a name "
        "published where nothing was found would make both names worthless. "
        "HOW: carry a witness only where one was confirmed."
    )
    assert broken.reachable_counterexample_of(answered) is None, (
        f"WHAT: the answer about the {machine} carries "
        f"{broken.reachable_counterexample_of(answered)!r} as a reachable "
        "counterexample. "
        "WHY: every declared transition of a shipped machine replays. "
        "HOW: carry the field only when a trace was built."
    )
