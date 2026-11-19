"""F27 criterion 1 -- the Owner drives a machine at a valid state with an
admissible event and reads the new state and the outcome in one answer.

The law: an admitted event publishes the state the machine moved to and
the outcome the step answered, together, in the one answer about that
event.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool published the outcome and left the state out,
or published the state and left the outcome out -- both are asserted
here; or the tool published a state it did not compute, which
test_f27_b2 catches by reading the six rows SPEC.md defines.
"""

from __future__ import annotations

import _f27_runtime_fixtures as machines


def test_an_admissible_tick_publishes_the_hour_after_it_and_the_outcome():
    """Given the shipped hour clock at 11 o'clock, when the Owner sends
    one tick, then the answer carries the state 12 o'clock and the
    outcome the step answered, in the one transition it ran."""
    source, descriptor = machines.shipped_machine("hour-clock")

    answer = machines.drive(source, descriptor, "(Clock 11)", ["(Tick)"])

    assert answer.get("status") == "completed", (
        f"WHAT: driving one admissible tick was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: criterion 1 promises that an admissible event at a valid "
        "state is answered with the new state and the outcome. "
        "HOW: read the refusals above."
    )
    assert machines.diagnostics_of(answer) == [], (
        f"WHAT: the answer still carries {machines.diagnostics_of(answer)}. "
        "WHY: nothing was wrong with this request. HOW: read them above."
    )
    ran = machines.transitions_of(answer)
    assert len(ran) == 1, (
        f"WHAT: the answer reports {len(ran)} transitions for the 1 event "
        f"sent: {ran}. "
        "WHY: the Owner reads one entry per event sent, so a missing or an "
        "extra entry is an event nothing was said about. "
        "HOW: report one entry per event, in order."
    )
    assert ran[0].get("position") == 1, (
        f"WHAT: the one transition stands at position "
        f"{ran[0].get('position')!r}, not 1: {ran[0]}. "
        "WHY: the Owner reads the position to say which event an entry is "
        "about. HOW: number the events from 1."
    )
    assert ran[0].get("result") == machines.A_TRANSITION, (
        f"WHAT: the admissible tick was published as "
        f"{ran[0].get('result')!r}, not {machines.A_TRANSITION!r}: {ran[0]}. "
        "WHY: criterion 1 is about an event the machine admits and runs. "
        "HOW: publish an admitted event as a transition."
    )
    assert ran[0].get("event") == "(Tick)", (
        f"WHAT: the entry says it is about the event "
        f"{ran[0].get('event')!r}, and the Owner sent '(Tick)': {ran[0]}. "
        "WHY: an entry naming another event is an answer about another "
        "request. HOW: carry the event the request sent."
    )
    assert ran[0].get("outcome") == "(Outcome (Clock 12) true)", (
        f"WHAT: the entry publishes the outcome "
        f"{ran[0].get('outcome')!r}, and the clock's step answers "
        f"'(Outcome (Clock 12) true)' for a tick at 11 o'clock: {ran[0]}. "
        "WHY: criterion 1 promises the outcome beside the new state: it is "
        "where the machine's own result stands. "
        "HOW: publish the value the step answered, written as a program "
        "writes it."
    )
    assert ran[0].get("state_after") == "(Clock 12)", (
        f"WHAT: the entry publishes the state "
        f"{ran[0].get('state_after')!r} after the tick, and the clock's "
        f"projection answers '(Clock 12)': {ran[0]}. "
        "WHY: criterion 1 promises the new state beside the outcome. "
        "HOW: publish the state the projection read off the outcome."
    )
    assert ran[0].get("state_before") == "(Clock 11)", (
        f"WHAT: the entry says the state before the tick was "
        f"{ran[0].get('state_before')!r}, and the Owner sent '(Clock 11)': "
        f"{ran[0]}. "
        "WHY: the state before is what makes an unchanged state readable "
        "beside a changed one. HOW: publish the state the transition ran "
        "from."
    )
    assert machines.state_now_of(answer) == "(Clock 12)", (
        f"WHAT: the answer says the machine now stands at "
        f"{machines.state_now_of(answer)!r}, and the one transition it ran "
        f"published '(Clock 12)': {machines.result_of(answer)}. "
        "WHY: the Owner drives the next event from the state this answer "
        "published. HOW: publish the state the last transition left."
    )
    assert machines.stopped_at_of(answer) is None, (
        f"WHAT: the answer says the run stopped at "
        f"{machines.stopped_at_of(answer)!r}, and every event sent ran. "
        "WHY: a stop the Owner reads where nothing stopped sends them "
        "looking for an event that was never refused. "
        "HOW: carry a stop only when one event was not run."
    )


def test_the_state_the_owner_sent_is_published_beside_the_state_it_reached():
    """Given the shipped reservation at 1 unit reserved, when the Owner
    sends one reserve, then the answer repeats the state it was sent and
    publishes the state 2 it reached."""
    source, descriptor = machines.shipped_machine("reservation")

    answer = machines.drive(source, descriptor, "(Reservation 1)", ["(Reserve)"])

    published = machines.result_of(answer)
    assert published.get("state_given") == "(Reservation 1)", (
        f"WHAT: the answer says it was sent the state "
        f"{published.get('state_given')!r}, and the Owner sent "
        f"'(Reservation 1)': {published}. "
        "WHY: an answer kept beside the request is read against the state "
        "it was about. HOW: repeat the state the request carried."
    )
    assert machines.state_now_of(answer) == "(Reservation 2)", (
        f"WHAT: the answer says the component now holds "
        f"{machines.state_now_of(answer)!r}, and reserving one more unit "
        f"from 1 reaches '(Reservation 2)': {published}. "
        "WHY: the Owner drives the next event from that state. "
        "HOW: publish the state the transition published."
    )
    assert published.get("assumptions_stated") == descriptor["assumptions"], (
        f"WHAT: the answer carries the assumptions "
        f"{published.get('assumptions_stated')!r}, and the descriptor "
        f"states {descriptor['assumptions']!r}. "
        "WHY: what the Owner may conclude from a run is conditional on the "
        "assumptions their descriptor states, so the answer carries them as "
        "stated. HOW: carry the stated sentences through unchanged."
    )
    assert answer.get("source_digest"), (
        f"WHAT: the answer carries no revision of the program it drove: "
        f"{answer}. "
        "WHY: an answer kept beside a source says which text it is about, "
        "as every other completed answer of this tool does. "
        "HOW: carry the revision of the submitted source."
    )
    assert answer.get("stands_on"), (
        f"WHAT: the answer says nothing about what it stands on: {answer}. "
        "WHY: every completed answer of an operation of this tool says "
        "which tool and which language read it. "
        "HOW: carry the same block the other operations carry."
    )
