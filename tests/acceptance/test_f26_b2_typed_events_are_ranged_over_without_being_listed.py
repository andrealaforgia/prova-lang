"""F26 criterion 4 -- the Owner's machine takes events of a type with no
bound: an event carrying a whole number. The two obligations that range
over events range over the type itself, and the answer neither lists an
event nor says it did.

The law: the obligations of a machine are three whatever its event type
holds -- one event value, two, or more than any run could list -- and
what they state is read over the typed event, not over a list of events
(SPEC.md lines 384-386).

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool listed the events of a finite type and only
happened to answer the unbounded one symbolically. The first test below
proves preservation for a dial whose events are the whole numbers, which
no listing of events reaches, and the second reads the same three
obligations off machines with one and with two event values.
"""

from __future__ import annotations

import re

import _f26_induction_fixtures as induction


def test_a_machine_whose_events_have_no_bound_is_answered_about_all_of_them():
    """Given a dimmer whose event carries a whole number, so that its
    event type has no bound, and whose invariant holds after the step
    only because admissibility keeps the new level between 0 and 10, when
    the Owner asks the tool to verify it with its descriptor, then all
    three obligations are proved."""
    source, descriptor = induction.THE_UNBOUNDED_EVENT_MACHINE

    answered = induction.ask_to_verify(source, descriptor)

    assert answered.get("status") == "completed", (
        f"WHAT: the dimmer was answered {answered.get('status')!r}: "
        f"{answered}. "
        "WHY: criterion 4 is about a machine with an unbounded event type "
        "being answered at all. HOW: read the refusals above."
    )
    standing = induction.how_the_three_stand(answered)
    assert standing == {kind: induction.PROVED for kind in induction.THE_THREE}, (
        f"WHAT: the three obligations of the dimmer stand as {standing}. "
        "WHY: its invariant is preserved for every whole number an event can "
        "carry, which is a statement about a domain no run can list; "
        "answering it requires reading the obligations over the typed event "
        "itself. HOW: state the obligations over a value of the event type "
        "and put that to the solver."
    )


def test_the_number_of_obligations_does_not_follow_the_number_of_events():
    """Given three machines whose event types hold one value, two values
    and more values than any run could list, when each is verified with
    its descriptor, then each answer carries the same three machine
    obligations."""
    machines = {
        "hour clock, one event value": induction.shipped_machine("hour-clock"),
        "reservation, two event values": induction.shipped_machine("reservation"),
        "dimmer, events without a bound": induction.THE_UNBOUNDED_EVENT_MACHINE,
    }

    listed = {
        named: sorted(
            induction.the_three_obligations(
                induction.ask_to_verify(source, descriptor)
            )
        )
        for named, (source, descriptor) in machines.items()
    }

    for named, kinds in listed.items():
        assert kinds == sorted(induction.THE_THREE), (
            f"WHAT: the {named} carries the machine obligations {kinds}, not "
            f"the three {sorted(induction.THE_THREE)}. "
            "WHY: SPEC.md lines 384-386 say the obligations range "
            "symbolically over typed events and an unbounded event type must "
            "not be enumerated as though finite; a count that followed the "
            "event values would be that enumeration. "
            "HOW: state one obligation per rule of SPEC.md lines 395-401, "
            "over a typed event."
        )


def test_the_obligations_say_what_they_range_over_and_name_no_single_event():
    """Given a machine with two event values, when the Owner reads the
    two obligations that range over events, then each says it is about
    the event type and neither names an event value of the program."""
    source, descriptor = induction.shipped_machine("reservation")

    answered = induction.ask_to_verify(source, descriptor)

    said = induction.text_of_the_three(answered)
    for event_value in induction.EVENT_VALUES:
        assert not re.search(rf"\b{event_value}\b", said), (
            f"WHAT: the three machine obligations name the event value "
            f"{event_value!r}: {said}. "
            "WHY: an answer that reasoned by listing the events would have to "
            "name them, and SPEC.md lines 384-386 forbid treating an event "
            "type as finite; naming one event value in an obligation about "
            "all of them tells the Owner something the obligation does not "
            "say. HOW: state the obligation over the event type the "
            "descriptor names."
        )
    event_type = descriptor["types"]["event"]
    ranging = [
        induction.STEP_ENABLEDNESS,
        induction.PRESERVATION,
    ]
    entries = induction.the_three_obligations(answered)
    for kind in ranging:
        entry = entries.get(kind) or {}
        assert event_type in str(entry), (
            f"WHAT: the {kind!r} obligation never names the event type "
            f"{event_type!r}: {entry}. "
            "WHY: the Owner must read what the obligation ranges over; an "
            "obligation about events that does not name their type leaves "
            "the reader to guess the domain it was shown over. "
            "HOW: name the event type the descriptor gave."
        )
