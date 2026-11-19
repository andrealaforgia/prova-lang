"""F27 criterion 4 -- the Owner sends several events in one request and
each transition runs from the state the one before it published, in
order, and the run stops at the first event the machine does not admit.

The law: the events of one request are driven in the order they were
sent, each from the state its predecessor published, and no event after
a stop is run at all.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the runtime drove every event from the state the
request carried and the machine happened to answer the same states --
the clock below moves to a different hour at every event, so a run that
never carried the state forward answers 12 three times; and the stopped
sequence asserts that the event after the boundary has no entry at all.
"""

from __future__ import annotations

import _f27_runtime_fixtures as machines


def test_three_ticks_in_one_request_walk_the_dial_in_order():
    """Given the shipped hour clock at 11 o'clock, when the Owner sends
    three ticks in one request, then the answer walks 12, 1, 2 -- each
    tick running from the hour the one before it published."""
    source, descriptor = machines.shipped_machine("hour-clock")

    answer = machines.drive(
        source, descriptor, "(Clock 11)", ["(Tick)", "(Tick)", "(Tick)"]
    )

    ran = machines.transitions_of(answer)
    assert [entry.get("position") for entry in ran] == [1, 2, 3], (
        f"WHAT: the answer reports the positions "
        f"{[entry.get('position') for entry in ran]} for the 3 ticks sent: "
        f"{ran}. "
        "WHY: criterion 4 promises the events are driven in order, and the "
        "Owner reads that order off the positions. "
        "HOW: number the events from 1 in the order they were sent."
    )
    assert [entry.get("state_after") for entry in ran] == [
        "(Clock 12)",
        "(Clock 1)",
        "(Clock 2)",
    ], (
        f"WHAT: the three ticks published the hours "
        f"{[entry.get('state_after') for entry in ran]}, and a clock ticked "
        "three times from 11 o'clock stands at 12, then 1, then 2. "
        "WHY: criterion 4 promises each transition uses the state the "
        "previous one published; a run that drove every tick from 11 "
        "o'clock would answer 12 three times. "
        "HOW: carry the published state into the next event."
    )
    assert [entry.get("state_before") for entry in ran] == [
        "(Clock 11)",
        "(Clock 12)",
        "(Clock 1)",
    ], (
        f"WHAT: the three ticks ran from the hours "
        f"{[entry.get('state_before') for entry in ran]}. "
        "WHY: each entry says which state it ran from, and that state is "
        "the one its predecessor published. "
        "HOW: carry the published state into the next event."
    )
    assert machines.state_now_of(answer) == "(Clock 2)", (
        f"WHAT: after three ticks from 11 o'clock the answer says the "
        f"clock stands at {machines.state_now_of(answer)!r}. "
        "WHY: the Owner drives the next event from the state the last "
        "transition published. HOW: publish that state."
    )


def test_a_sequence_stops_at_the_first_event_outside_the_domain():
    """Given a reservation component at 1 unit whose admissibility
    predicate refuses a reserve at capacity, when the Owner sends
    reserve, reserve, release in one request, then the second reserve is
    a boundary rejection at position 2 and the release is never run."""
    source, descriptor = machines.reservation_that_admits_less()

    answer = machines.drive(
        source,
        descriptor,
        "(Reservation 1)",
        ["(Reserve)", "(Reserve)", "(Release)"],
    )

    ran = machines.transitions_of(answer)
    assert [entry.get("result") for entry in ran] == [
        machines.A_TRANSITION,
        machines.A_BOUNDARY_REJECTION,
    ], (
        f"WHAT: the three events sent were answered "
        f"{[entry.get('result') for entry in ran]}: {ran}. "
        "WHY: the chosen behaviour is to stop at a boundary rejection with "
        "the position named, so the first event runs, the second is "
        "refused and the third is not run at all. "
        "HOW: stop the sequence at the refused event."
    )
    assert [entry.get("position") for entry in ran] == [1, 2], (
        f"WHAT: the entries stand at the positions "
        f"{[entry.get('position') for entry in ran]}. "
        "WHY: the Owner reads which of the three events was refused. "
        "HOW: number the events from 1."
    )
    stopped = machines.stopped_at_of(answer) or {}
    assert stopped.get("position") == 2, (
        f"WHAT: the answer says the run stopped at {stopped!r}, and the "
        "event refused was the second of the three sent. "
        "WHY: the Owner is promised the position of the event that stopped "
        "the run, so that they know which events to send again. "
        "HOW: name that position."
    )
    assert stopped.get("events_not_run") == 1, (
        f"WHAT: the stop says {stopped.get('events_not_run')!r} events "
        f"were not run, and 1 of the 3 sent stands after the refused one: "
        f"{stopped}. "
        "WHY: an Owner who cannot see how many events were left behind "
        "cannot tell a stop from a sequence that ended. "
        "HOW: count the events after the stop."
    )
    assert machines.state_now_of(answer) == "(Reservation 2)", (
        f"WHAT: after the stop the answer says the component holds "
        f"{machines.state_now_of(answer)!r}, and the one transition that "
        "ran moved it from 1 unit to 2. "
        "WHY: the Owner resumes from the state the run reached, which is "
        "the state the refused event was refused at. "
        "HOW: publish the state the last transition published."
    )


def test_a_sequence_stops_when_the_machine_leaves_its_own_invariant():
    """Given a clock whose step adds an hour without wrapping, at 12
    o'clock, when the Owner sends two ticks, then the first publishes 13
    and the second is not run: the state it would run from is outside the
    invariant the descriptor names."""
    source, descriptor = machines.clock_that_leaves_its_invariant()

    answer = machines.drive(source, descriptor, "(Clock 12)", ["(Tick)", "(Tick)"])

    ran = machines.transitions_of(answer)
    assert [entry.get("result") for entry in ran] == [
        machines.A_TRANSITION,
        machines.A_STATE_OUTSIDE_THE_INVARIANT,
    ], (
        f"WHAT: the two ticks were answered "
        f"{[entry.get('result') for entry in ran]}: {ran}. "
        "WHY: a machine is defined from the states its invariant holds at, "
        "so a transition from the state 13 -- which this clock's own "
        "invariant excludes -- is one the machine does not define. "
        "HOW: stop the sequence there and say so."
    )
    assert ran[0].get("state_after") == "(Clock 13)", (
        f"WHAT: the first tick published {ran[0].get('state_after')!r}, and "
        "this clock's step adds an hour to 12 without wrapping. "
        "WHY: the transition the machine does define is published as it "
        "ran. HOW: publish the state the projection read."
    )
    assert "outcome" not in ran[1], (
        f"WHAT: the stopped entry carries an outcome: {ran[1]}. "
        "WHY: the step was never run from that state. "
        "HOW: publish no outcome where nothing ran."
    )
    stopped = machines.stopped_at_of(answer) or {}
    assert stopped.get("position") == 2 and stopped.get("reason") == (
        machines.A_STATE_OUTSIDE_THE_INVARIANT
    ), (
        f"WHAT: the answer says the run stopped at {stopped!r}. "
        "WHY: the Owner reads which event was not run and why. "
        "HOW: name the position and the reason."
    )
    assert stopped.get("role") == "invariant", (
        f"WHAT: the stop names the role {stopped.get('role')!r}: {stopped}. "
        "WHY: the Owner is sent to the part of their machine that decided "
        "it, which is the invariant role of the descriptor. "
        "HOW: name that role."
    )
    assert machines.state_now_of(answer) == "(Clock 13)", (
        f"WHAT: the answer says the clock now stands at "
        f"{machines.state_now_of(answer)!r}. "
        "WHY: the state the run reached is the one the first tick "
        "published, and the Owner must see it to repair their machine. "
        "HOW: publish the state the last transition published."
    )
