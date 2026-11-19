"""What a machine obligation must not claim: that a statement holding
over an empty domain is a proof, that a solution nobody can write is a
counterexample, that a step refusing an event is anything but a
counterexample, and that an invariant is preserved when the event it
depends on was never ranged over.

The laws:
- a claim valid only because nothing satisfies what it assumes does not
  certify a machine (SPEC.md lines 406-407);
- a solution carrying a number past the digits this tool writes leaves
  its obligation unsettled and the inventory standing;
- an event the step refuses is reported as the counterexample it is,
  replayed through the evaluator;
- preservation is withheld wherever some admitted event breaks the
  invariant, whatever the events the examples name, and is disproved
  wherever replaying the whole transition confirms the pair.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool withheld every word from everything. The other
F26 checks require all three obligations proved for both shipped
machines and for a dial whose events have no bound, and the first test
below requires the two shipped machines to have something to range over,
so a tool that withholds everywhere fails there.
"""

from __future__ import annotations

import json

import pytest

import _f26_induction_fixtures as induction

# A machine of the smallest shape the roles need, so each case below
# differs from the next in one condition only: its invariant, its
# admissibility predicate, what its step requires and what its step
# answers.
A_MACHINE_WITH = """\
(deftype State (record (n Int)))
(deftype Event (record (by Int)))
(deftype Outcome (record (state State) (accepted Bool)))

(defn valid-state
  (sig ((current State)) -> Bool ! pure)
  (examples (example (valid-state (State 0)) => {invariant_of_zero}))
  {invariant})

(defn initial
  (sig () -> State ! pure)
  (examples (example (initial) => (State 0)))
  (State 0))

(defn admissible
  (sig ((current State) (event Event)) -> Bool ! pure)
  (examples (example (admissible (State 0) (Event 0)) => {admits_zero}))
  {admissible})

(defn step
  (sig ((current State) (event Event)) -> Outcome ! pure)
  (requires {step_requires})
  (examples (example (step (State 0) (Event 0)) => (Outcome {after_zero} true)))
  (Outcome {answers} true))

(defn state-of
  (sig ((produced Outcome)) -> State ! pure)
  (examples (example (state-of (Outcome (State 0) true)) => (State 0)))
  (.state produced))
"""


def a_machine(
    invariant: str,
    admissible: str,
    step_requires: str = "true",
    answers: str = "current",
    invariant_of_zero: str = "true",
    admits_zero: str = "true",
    after_zero: str = "(State 0)",
) -> tuple[str, dict]:
    return (
        A_MACHINE_WITH.format(
            invariant=invariant,
            admissible=admissible,
            step_requires=step_requires,
            answers=answers,
            invariant_of_zero=invariant_of_zero,
            admits_zero=admits_zero,
            after_zero=after_zero,
        ),
        induction.a_descriptor_naming("State"),
    )


def _a_number_too_large_to_write() -> str:
    """Six factors of nine hundred nines each, multiplied one pair at a
    time: a whole number of 5400 digits, past the 4000 this tool writes
    an integer with, built from literals the reader accepts."""
    nines = "9" * 900
    written = nines
    for _ in range(5):
        written = f"(* {nines} {written})"
    return written


A_NUMBER_TOO_LARGE_TO_WRITE = _a_number_too_large_to_write()


def test_a_machine_with_no_state_and_event_to_range_over_is_not_certified():
    """Given a machine whose invariant admits only the state 0 and whose
    admissibility predicate admits only the state 1, so that no state and
    event satisfy both, when the Owner asks the tool to verify it with
    its descriptor, then the two obligations written over that pair are
    not proved, each says the domain is empty, and the whole is not
    verified."""
    source, descriptor = a_machine(
        invariant="(= (.n current) 0)",
        admissible="(= (.n current) 1)",
        admits_zero="false",
    )

    answered = induction.ask_to_verify(source, descriptor)

    standing = induction.how_the_three_stand(answered)
    assert sorted(standing) == sorted(induction.THE_THREE), (
        f"WHAT: the answer lists {sorted(standing)}, not the three "
        f"{sorted(induction.THE_THREE)}. "
        "WHY: an empty domain withholds words; it adds and removes no "
        "obligation. HOW: list exactly the three."
    )
    for kind in (induction.STEP_ENABLEDNESS, induction.PRESERVATION):
        entry = induction.the_three_obligations(answered)[kind]
        assert entry.get("result") != induction.PROVED, (
            f"WHAT: {kind!r} stands as {entry.get('result')!r} for a machine "
            f"in which no state and event satisfy the invariant and the "
            f"admissibility predicate together: {entry}. "
            "WHY: SPEC.md lines 406-407 say an unsatisfiable required domain "
            "must not silently certify a useful machine; the statement is "
            "valid for want of anything to range over and says nothing about "
            "the machine. HOW: ask whether anything satisfies what the "
            "obligation assumes before taking the word."
        )
        assert entry.get("counterexample") is None, (
            f"WHAT: {kind!r} carries a counterexample: {entry}. "
            "WHY: nothing was shown to be wrong with the program; the word is "
            "withheld, which is not a disproof. HOW: report it unsettled."
        )
        assert "empty domain" in (entry.get("reason") or ""), (
            f"WHAT: {kind!r} is unsettled and its reason does not name the "
            f"empty domain: {entry.get('reason')!r}. "
            "WHY: the Owner must be told what to repair -- an invariant and "
            "an admissibility predicate nothing satisfies together. "
            "HOW: name the empty domain in the reason."
        )
    aggregate = induction.aggregate_of(answered)
    assert aggregate.get("result") == induction.NOT_VERIFIED, (
        f"WHAT: a machine with nothing to range over stands as "
        f"{aggregate.get('result')!r}: {aggregate}. "
        "WHY: a machine certified on an empty domain is the one answer "
        "SPEC.md lines 406-407 forbid. HOW: withhold the word over the whole."
    )
    assert any(
        induction.PRESERVATION in str(left) or induction.STEP_ENABLEDNESS in str(left)
        for left in (aggregate.get("obligations") or {}).get("undischarged") or []
    ), (
        f"WHAT: the word is withheld and names "
        f"{(aggregate.get('obligations') or {}).get('undischarged')}. "
        "WHY: the Owner must be sent to the obligations the empty domain "
        "withheld. HOW: name them among the undischarged."
    )


@pytest.mark.parametrize("machine", induction.MACHINES)
def test_a_shipped_machine_has_something_to_range_over(machine):
    """Given the hour clock or the reservation component, when the Owner
    asks the tool to verify it with its descriptor, then all three
    obligations are still proved: their invariant and admissibility
    predicate are satisfiable together, so the new rule withholds
    nothing from them."""
    source, descriptor = induction.shipped_machine(machine)

    answered = induction.ask_to_verify(source, descriptor)

    assert induction.how_the_three_stand(answered) == {
        kind: induction.PROVED for kind in induction.THE_THREE
    }, (
        f"WHAT: the {machine} now stands as "
        f"{induction.how_the_three_stand(answered)}. "
        "WHY: its invariant and its admissibility predicate are satisfiable "
        "together -- the clock admits every hour from 1 to 12 and the "
        "reservation every count from 0 to 2 -- so the rule about an empty "
        "domain must withhold nothing here. HOW: read the reason beside each "
        "entry that is not proved."
    )
    assert induction.aggregate_of(answered).get("result") == induction.VERIFIED, (
        f"WHAT: the {machine} as a whole stands as "
        f"{induction.aggregate_of(answered).get('result')!r}. "
        "WHY: nothing about it changed. HOW: read the reason it gives."
    )


def test_the_rule_about_an_empty_domain_is_published():
    """Given the manifest, when an agent reads the answer shape of
    `verify`, then it says that an obligation holding only because
    nothing satisfies what it assumes is not proved."""
    published = str(
        ((induction.published_verify_shape().get("response") or {}).get("fields"))
        or {}
    )

    assert "empty domain" in published, (
        f"WHAT: the published answer shape of 'verify' does not say what an "
        f"empty domain does to an obligation: {published[:600]}... "
        "WHY: an agent reads from the manifest why a word was withheld; a "
        "rule it meets in an answer and cannot look up tells it nothing. "
        "HOW: publish the rule beside the obligations it governs."
    )


def test_a_solution_too_large_to_write_leaves_the_inventory_standing():
    """Given a machine whose step is defined only below a number of 5400
    digits, which is more than this tool writes, when the Owner asks the
    tool to verify it with its descriptor, then the answer is completed
    with its whole inventory, the obligation whose solution could not be
    written is unsettled naming the limit, and nothing is claimed about
    the machine."""
    source, descriptor = a_machine(
        invariant="true",
        admissible="true",
        step_requires=f"(< (.by event) {A_NUMBER_TOO_LARGE_TO_WRITE})",
    )

    answered = induction.ask_to_verify(source, descriptor)

    assert answered.get("status") == "completed", (
        f"WHAT: a machine whose step names a number of 5400 digits was "
        f"answered {answered.get('status')!r}: "
        f"{json.dumps(answered)[:600]}. "
        "WHY: every literal of the program is one this tool reads, and a "
        "failure of this tool is never a statement about a program: the Owner "
        "must still get the inventory. HOW: bound the writing of a solution "
        "and leave that obligation unsettled."
    )
    assert induction.listed_obligations(answered), (
        f"WHAT: the answer carries no inventory at all: {answered}. "
        "WHY: the inventory is what the Owner asked for. "
        "HOW: keep it when one obligation cannot be settled."
    )
    entry = induction.the_three_obligations(answered)[induction.STEP_ENABLEDNESS]
    assert entry.get("result") == "unknown", (
        f"WHAT: the obligation whose solution could not be written stands as "
        f"{entry.get('result')!r}: {entry}. "
        "WHY: a solution nobody can write is neither a proof nor a "
        "counterexample. HOW: leave it unsettled."
    )
    assert "digits" in (entry.get("reason") or ""), (
        f"WHAT: the unsettled obligation does not name the limit it met: "
        f"{entry.get('reason')!r}. "
        "WHY: the Owner is told what stopped the answer, not merely that "
        "something did. HOW: name the digits this tool writes."
    )


def test_a_program_alone_whose_solution_is_too_large_is_answered_too():
    """Given a program with no machine at all whose promise is broken
    only by a number of 5400 digits, when the Owner asks the tool to
    verify it, then the answer is completed with its inventory and that
    obligation is unsettled naming the limit."""
    source = (
        "(defn next-one\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        f"  (ensures (< result {A_NUMBER_TOO_LARGE_TO_WRITE}))\n"
        "  (examples (example (next-one 1) => 2))\n"
        "  (+ n 1))\n"
    )

    answered = induction.ask_to_verify(source)

    assert answered.get("status") == "completed", (
        f"WHAT: a program with no descriptor was answered "
        f"{answered.get('status')!r}: {json.dumps(answered)[:500]}. "
        "WHY: the same bound protects the answers that name no machine; a "
        "solution this tool cannot write must not cost the Owner the "
        "inventory there either. HOW: bound the writing of a solution in the "
        "one place a solution is read."
    )
    unsettled = [
        entry
        for entry in induction.listed_obligations(answered)
        if entry.get("result") == "unknown" and "digits" in (entry.get("reason") or "")
    ]
    assert unsettled, (
        f"WHAT: no obligation of this program says a solution was too large "
        f"to write: "
        f"{[(e['id'], e['result']) for e in induction.listed_obligations(answered)]}. "
        "WHY: the obligation whose solution could not be written is the one "
        "that must say so. HOW: name the limit in its reason."
    )


def test_an_event_the_step_refuses_is_reported_as_the_counterexample_it_is():
    """Given a machine that admits every event while its step is defined
    only for an event at or above zero, when the Owner asks the tool to
    verify it with its descriptor, then step-enabledness is disproved and
    carries the event the step refuses, replayed through the program."""
    source, descriptor = a_machine(
        invariant="true", admissible="true", step_requires="(>= (.by event) 0)"
    )

    answered = induction.ask_to_verify(source, descriptor)

    entry = induction.the_three_obligations(answered)[induction.STEP_ENABLEDNESS]
    assert entry.get("result") == "disproved", (
        f"WHAT: step-enabledness of a machine admitting every event while its "
        f"step needs a non-negative one stands as {entry.get('result')!r}: "
        f"{entry}. "
        "WHY: a negative event is admissible and the step is not defined for "
        "it, which is exactly what this obligation denies; an answer that "
        "withheld the disproof would leave the Owner to find it. "
        "HOW: report the solution the solver found, replayed."
    )
    witness = entry.get("counterexample") or {}
    assert any(
        "-" in str(argument) for argument in (witness.get("arguments") or [])
    ), (
        f"WHAT: the counterexample carries {witness.get('arguments')}, none of "
        "them an event the step refuses. "
        "WHY: the Owner runs the witness; an event the step accepts proves "
        "nothing. HOW: carry the solution the solver found."
    )
    assert "precondition" in str(witness.get("refused_when_run") or ""), (
        f"WHAT: the counterexample does not say the program refused it: "
        f"{witness}. "
        "WHY: a witness is a counterexample only because the reference "
        "semantics refuses it. HOW: say how it was refused."
    )


def test_preservation_is_withheld_for_an_event_no_example_names():
    """Given a machine whose invariant admits counts up to 10 and whose
    step adds the event's own number, with every example naming the event
    0, when the Owner asks the tool to verify it with its descriptor,
    then preservation is not proved: the state 10 and the event 1 leave
    the invariant."""
    source, descriptor = a_machine(
        invariant="(<= (.n current) 10)",
        admissible="true",
        answers="(State (+ (.n current) (.by event)))",
    )

    answered = induction.ask_to_verify(source, descriptor)

    entry = induction.the_three_obligations(answered)[induction.PRESERVATION]
    assert entry.get("result") != induction.PROVED, (
        f"WHAT: preservation stands as {entry.get('result')!r} for a machine "
        f"whose step adds the event's number to a count capped at 10: {entry}. "
        "WHY: the obligation ranges over every event of the type, not over "
        "the events the examples name; the state 10 with the event 1 leaves "
        "the invariant. HOW: state the obligation over a value of the event "
        "type."
    )


def test_preservation_names_the_counterexample_its_replay_confirms():
    """Given a machine whose step requires an invariant state and whose
    invariant is not inductive, when the Owner asks the tool to verify it
    with its descriptor, then preservation is disproved and carries the
    pair the reference semantics confirmed, which is not called a
    reachable trace."""
    source, descriptor = a_machine(
        invariant="(<= (.n current) 10)",
        admissible="true",
        step_requires="(valid-state current)",
        answers="(State (+ (.n current) 1))",
        after_zero="(State 1)",
    )

    answered = induction.ask_to_verify(source, descriptor)

    entry = induction.the_three_obligations(answered)[induction.PRESERVATION]
    assert entry.get("result") == "disproved", (
        f"WHAT: preservation stands as {entry.get('result')!r}: {entry}. "
        "WHY: the replay of this obligation runs the invariant on the state, "
        "the admissibility predicate there and the step over the pair, and "
        "the invariant answers false of the state it leads to; a tool that "
        "withheld the word there would leave the Owner to find by hand what "
        "it had already run, and 'proved' would certify an invariant that is "
        "not inductive. HOW: report the disproof the replay confirms."
    )
    witness = entry.get("counterexample") or {}
    assert witness.get("invariant_after_the_step") is False, (
        f"WHAT: the disproof does not say the invariant is false after the "
        f"step: {entry}. "
        "WHY: that is the only thing that makes the pair a counterexample; "
        "a disproof resting on anything else would name a pair this tool did "
        "not establish. HOW: run the invariant on the state the step leads "
        "to and carry what it answered."
    )
    assert "not a reachable" in str(witness), (
        f"WHAT: the witness does not say it is not a reachable trace: "
        f"{witness}. "
        "WHY: SPEC.md lines 307-311 keep the two evidence types apart, and "
        "nothing here shows a run reaches the state. "
        "HOW: say so beside the witness."
    )
