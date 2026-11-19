"""F27, the failure point the request does not name -- a role function
whose own contract refuses while the run is asking it.

The law: a run that meets a refused contract stops there and publishes
what did run -- the transitions before it, the state they left and a stop
naming the position -- beside the refusal that says which function
refused and which of its two contracts it was.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused the whole request before driving
anything -- the status is asserted to be 'completed' and the transitions
that ran before the refused event are asserted whole; or the tool named
the wrong contract or the wrong event, which the kind and the position
are asserted against in both cases here.
"""

from __future__ import annotations

import _f27_runtime_fixtures as machines


def test_a_refused_precondition_stops_the_run_and_publishes_what_ran():
    """Given a clock whose invariant admits 13 o'clock while its step
    requires an hour on the dial, at 12 o'clock, when the Owner sends
    three ticks, then the first tick is published as a transition to 13,
    the run stops at the second with the reason 'contract_refused', and
    the refusal names the step function and its precondition."""
    source, descriptor = machines.clock_whose_step_asks_for_more()

    answer = machines.drive(
        source, descriptor, "(Clock 12)", ["(Tick)", "(Tick)", "(Tick)"]
    )

    assert answer.get("status") == "completed", (
        f"WHAT: the run was answered {answer.get('status')!r}: {answer}. "
        "WHY: the request was readable and the machine resolved, so the run "
        "happened: what it met is the program's own contract refusing, which "
        "this tool answers as it answers the same refusal of an evaluation. "
        "HOW: read the refusal above."
    )
    assert machines.categories_of(answer) == ["precondition_violation"], (
        f"WHAT: the run carries {machines.categories_of(answer)}: {answer}. "
        "WHY: the step of this clock requires an hour on the dial and the "
        "second tick would run it at 13, so what refused is a precondition "
        "and not a promise the step failed to keep. "
        "HOW: answer the category of the contract that refused."
    )
    refusal = machines.diagnostics_of(answer)[0]
    assert refusal.get("symbol") == descriptor["roles"]["step"], (
        f"WHAT: the refusal names {refusal.get('symbol')!r}, and the function "
        f"whose contract refused is {descriptor['roles']['step']!r}: "
        f"{refusal}. "
        "WHY: the Owner is sent to the function to read. "
        "HOW: name the function."
    )
    assert "position 2" in refusal.get("reason", ""), (
        f"WHAT: the refusal says {refusal.get('reason')!r}, which does not "
        "name position 2. "
        "WHY: the first tick ran and the second reached the refused "
        "contract; an Owner told only the function cannot tell which of the "
        "three events sent to look at. HOW: name the position, counted "
        "from 1."
    )
    assert refusal.get("location", {}).get("line"), (
        f"WHAT: the refusal says nowhere to open: {refusal}. "
        "WHY: it is about a function the submitted program declares, so it "
        "stands at that declaration. HOW: carry the line and the column."
    )

    ran = machines.transitions_of(answer)
    assert [
        (entry.get("position"), entry.get("result"), entry.get("state_after"))
        for entry in ran
    ] == [(1, machines.A_TRANSITION, "(Clock 13)")], (
        f"WHAT: the run published {ran}. "
        "WHY: the first tick did run, and a refusal that threw it away would "
        "leave the Owner driving the sequence again to find out where the "
        "machine stood. HOW: publish the transitions that ran before the "
        "refused event, and none for the refused event itself."
    )
    assert machines.state_now_of(answer) == "(Clock 13)", (
        f"WHAT: the run says the clock now stands at "
        f"{machines.state_now_of(answer)!r}. "
        "WHY: the Owner resumes from the state the last transition "
        "published. HOW: publish that state."
    )
    stopped = machines.stopped_at_of(answer) or {}
    assert stopped.get("position") == 2 and stopped.get("reason") == (
        machines.A_CONTRACT_REFUSAL
    ), (
        f"WHAT: the run says it stopped at {stopped!r}. "
        "WHY: a refused contract stops the sequence as an event outside the "
        "admissible domain does, and the Owner reads the position and the "
        "reason the same way. HOW: name both."
    )
    assert stopped.get("events_not_run") == 1, (
        f"WHAT: the stop says {stopped.get('events_not_run')!r} events were "
        f"not run, and 1 of the 3 sent stands after the second: {stopped}. "
        "WHY: an Owner who cannot count what was left behind cannot send the "
        "rest again. HOW: count the events after the stop."
    )


def test_a_broken_promise_stops_the_run_at_the_event_that_broke_it():
    """Given a clock whose step promises the hour it answers is on the
    dial, at 11 o'clock, when the Owner sends three ticks, then the first
    is published as a transition to 12, the run stops at the second, and
    the refusal is about a promise and not a precondition."""
    source, descriptor = machines.clock_whose_step_promises_more()

    answer = machines.drive(
        source, descriptor, "(Clock 11)", ["(Tick)", "(Tick)", "(Tick)"]
    )

    assert answer.get("status") == "completed", (
        f"WHAT: the run was answered {answer.get('status')!r}: {answer}. "
        "WHY: the run happened and met the program's own promise failing. "
        "HOW: read the refusal above."
    )
    assert machines.categories_of(answer) == ["postcondition_violation"], (
        f"WHAT: the run carries {machines.categories_of(answer)}: {answer}. "
        "WHY: this step asks nothing of its input and promises the hour it "
        "answers is on the dial, which it does not keep at 12 o'clock: the "
        "two contracts are told apart, or an Owner reads the wrong half of "
        "the function. HOW: answer the category of the contract that "
        "refused."
    )
    refusal = machines.diagnostics_of(answer)[0]
    assert "position 2" in refusal.get("reason", ""), (
        f"WHAT: the refusal says {refusal.get('reason')!r}, which does not "
        "name position 2. "
        "WHY: the promise held for the first tick, at 11 o'clock, and broke "
        "at the second. HOW: name the position, counted from 1."
    )
    ran = machines.transitions_of(answer)
    assert [
        (entry.get("position"), entry.get("state_after")) for entry in ran
    ] == [(1, "(Clock 12)")], (
        f"WHAT: the run published {ran}. "
        "WHY: the tick to 12 o'clock kept the promise and did run. "
        "HOW: publish the transitions before the refused event."
    )
    stopped = machines.stopped_at_of(answer) or {}
    assert stopped.get("reason") == machines.A_CONTRACT_REFUSAL, (
        f"WHAT: the run says it stopped at {stopped!r}. "
        "WHY: a refused contract of either kind stops the sequence under one "
        "word, and which contract it was stands in the refusal. "
        "HOW: name the reason."
    )


def test_a_refused_contract_at_the_first_event_publishes_no_transition():
    """Given the same clock whose step requires an hour on the dial, at
    13 o'clock -- a state its invariant admits -- when the Owner sends
    one tick, then no transition is published, the state published is the
    state sent, and the stop names position 1."""
    source, descriptor = machines.clock_whose_step_asks_for_more()

    answer = machines.drive(source, descriptor, "(Clock 13)", ["(Tick)"])

    assert machines.transitions_of(answer) == [], (
        f"WHAT: the run published {machines.transitions_of(answer)}. "
        "WHY: the one event sent reached a refused precondition, so no "
        "transition ran at all. HOW: publish none."
    )
    assert machines.state_now_of(answer) == "(Clock 13)", (
        f"WHAT: the run says the clock stands at "
        f"{machines.state_now_of(answer)!r}, and nothing ran. "
        "WHY: a run that drove nothing leaves the machine at the state it "
        "was sent, and an empty run must not be read as a machine that "
        "moved. HOW: publish the state the request carried."
    )
    stopped = machines.stopped_at_of(answer) or {}
    assert stopped.get("position") == 1 and stopped.get("events_not_run") == 0, (
        f"WHAT: the run says it stopped at {stopped!r}. "
        "WHY: the first of the one event sent is where it stopped, and "
        "nothing stands after it. HOW: name the position and the count."
    )
