"""F27 criterion 5 and the invariant rule -- text the tool cannot read as
a value, a value the machine's types do not take, and a state the
machine's own invariant excludes are all refused before any event is
driven, each naming the field or the role to repair, and none of them
ends in a traceback.

The law: nothing is driven from input the runtime cannot use, and a
refusal carries no transition and no state at all.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused everything it was sent -- the other
F27 tests drive the same machines with readable input and require the
transitions; or the tool refused after driving the first event, which
the two-event cases here catch by requiring no result at all.
"""

from __future__ import annotations

import _f27_runtime_fixtures as machines


def _clock() -> tuple[str, dict]:
    return machines.shipped_machine("hour-clock")


def _refused(answer: dict, what: str) -> None:
    assert answer.get("status") == "invalid_input", (
        f"WHAT: {what} was answered {answer.get('status')!r}: {answer}. "
        "WHY: criterion 5 promises that input the runtime cannot use is "
        "refused, and the refusal of a field of a request is "
        "'invalid_input'. HOW: refuse it by name."
    )
    assert answer.get("result") is None, (
        f"WHAT: the refusal of {what} still carries a result: {answer}. "
        "WHY: a result beside a refusal reads as a run that happened; "
        "criterion 5 promises the refusal comes before any transition. "
        "HOW: answer the refusal alone."
    )
    assert machines.diagnostics_of(answer), (
        f"WHAT: the refusal of {what} carries no refusal to read: {answer}. "
        "WHY: an Owner is told what to repair. HOW: carry the refusal."
    )


def test_a_state_the_tool_cannot_read_as_a_value_is_refused_where_it_stops():
    """Given the hour clock and the state text '(Clock 11' with its
    bracket missing, when the Owner drives one tick, then the answer is
    refused, names the 'state' field and says where in that text the
    reader stopped."""
    source, descriptor = _clock()

    answer = machines.drive(source, descriptor, "(Clock 11", ["(Tick)"])

    _refused(answer, "a state whose bracket is missing")
    assert "state" in machines.fields_the_refusal_names(answer), (
        f"WHAT: the refusal names "
        f"{machines.fields_the_refusal_names(answer)}, and the field to "
        f"repair is 'state': {answer}. "
        "WHY: the Owner must be sent to the field of the request that "
        "carries the text. HOW: name that field."
    )
    refusal = machines.diagnostics_of(answer)[0]
    assert refusal.get("location", {}).get("line"), (
        f"WHAT: the refusal says nowhere in the text it stopped: {refusal}. "
        "WHY: the state is a text the Owner wrote, and a reader refusal of "
        "this tool always says where. HOW: carry the line and the column."
    )
    assert refusal.get("points_into") == "state", (
        f"WHAT: the refusal says its place stands in "
        f"{refusal.get('points_into')!r}: {refusal}. "
        "WHY: a request carries several texts, and an Owner who is not told "
        "which one cannot open it. HOW: say which text the place is in."
    )


def test_an_event_the_tool_cannot_read_is_refused_before_the_first_event_runs():
    """Given the hour clock at 11 o'clock and two events, the first a
    readable tick and the second the text 'Tick)', when the Owner drives
    them, then nothing ran at all and the refusal names the second event
    by its place in the list."""
    source, descriptor = _clock()

    answer = machines.drive(source, descriptor, "(Clock 11)", ["(Tick)", "Tick)"])

    _refused(answer, "an event the reader cannot read")
    assert machines.transitions_of(answer) == [], (
        f"WHAT: the refusal carries the transitions "
        f"{machines.transitions_of(answer)}. "
        "WHY: criterion 5 promises the refusal comes before any "
        "transition, so the readable first event must not have been "
        "driven. HOW: read every event before driving the first."
    )
    named = machines.fields_the_refusal_names(answer)
    assert "events[1]" in named, (
        f"WHAT: the refusal names {named}, and the event to repair is the "
        f"second of the list: {answer}. "
        "WHY: a list of events needs the place in it, or the Owner must "
        "guess which text to repair. HOW: name the field with its place."
    )


def test_a_state_of_another_type_is_refused_naming_the_type_the_machine_takes():
    """Given the hour clock and the state '(Reservation 0)', which the
    clock's program does not declare, when the Owner drives one tick,
    then the answer is refused and nothing is driven."""
    source, descriptor = _clock()

    answer = machines.drive(source, descriptor, "(Reservation 0)", ["(Tick)"])

    _refused(answer, "a state of another machine's type")
    assert machines.categories_of(answer) in (
        ["malformed_value"],
        ["ill_typed_value"],
    ), (
        f"WHAT: the refusal carries the categories "
        f"{machines.categories_of(answer)}: {answer}. "
        "WHY: a value whose constructor the program does not declare is "
        "refused as the tool refuses an argument of the same kind, in the "
        "words the manifest publishes. "
        "HOW: refuse it in one of those categories."
    )


def test_an_event_of_the_state_type_is_refused_rather_than_driven():
    """Given the hour clock at 11 o'clock and the event '(Clock 1)',
    which is a state and not an event, when the Owner drives it, then the
    answer is refused and nothing is driven."""
    source, descriptor = _clock()

    answer = machines.drive(source, descriptor, "(Clock 11)", ["(Clock 1)"])

    _refused(answer, "an event that is a state")
    assert machines.categories_of(answer) == ["ill_typed_value"], (
        f"WHAT: the refusal carries {machines.categories_of(answer)}: "
        f"{answer}. "
        "WHY: a '(Clock 1)' is a value the program declares, of the type "
        "the machine keeps as its state and not of the type it takes as "
        "its events. HOW: refuse it as a value of the wrong type."
    )


def test_a_state_the_invariant_excludes_is_refused_naming_the_invariant_role():
    """Given the shipped hour clock and the state '(Clock 0)', which its
    invariant excludes, when the Owner drives one tick, then the answer
    is refused, names the invariant role and the function standing in it,
    and drives nothing."""
    source, descriptor = _clock()

    answer = machines.drive(source, descriptor, "(Clock 0)", ["(Tick)"])

    _refused(answer, "a state the invariant excludes")
    assert machines.categories_of(answer) == ["state_outside_invariant"], (
        f"WHAT: the refusal carries {machines.categories_of(answer)}: "
        f"{answer}. "
        "WHY: the machine is defined from the states its invariant holds "
        "at, so a state it excludes is refused in a word of its own that "
        "the manifest publishes. HOW: refuse it under that category."
    )
    assert machines.roles_the_refusal_names(answer) == ["invariant"], (
        f"WHAT: the refusal names the roles "
        f"{machines.roles_the_refusal_names(answer)}: {answer}. "
        "WHY: the Owner is sent to the part of the descriptor that decided "
        "it. HOW: name the invariant role."
    )
    refusal = machines.diagnostics_of(answer)[0]
    assert refusal.get("named") == descriptor["roles"]["invariant"], (
        f"WHAT: the refusal says the role is filled by "
        f"{refusal.get('named')!r}, and the descriptor names "
        f"{descriptor['roles']['invariant']!r}: {refusal}. "
        "WHY: the Owner reads which function answered false. "
        "HOW: name the function the descriptor gave the role."
    )


def test_a_request_with_no_events_at_all_is_refused_naming_the_field():
    """Given the hour clock at 11 o'clock and an empty list of events,
    when the Owner sends it, then the answer is refused naming the
    'events' field, and no state is published as though something had
    run."""
    source, descriptor = _clock()

    answer = machines.drive(source, descriptor, "(Clock 11)", [])

    _refused(answer, "a request carrying no event")
    assert "events" in machines.fields_the_refusal_names(answer), (
        f"WHAT: the refusal names "
        f"{machines.fields_the_refusal_names(answer)}: {answer}. "
        "WHY: an Owner who sent an empty list is told which field to fill. "
        "HOW: name that field."
    )


def test_fields_of_another_kind_are_refused_by_name_in_one_answer():
    """Given a request whose state is the number 11 and whose events are
    the text '(Tick)' rather than a list, when the Owner sends it, then
    both fields are named in the one answer."""
    source, descriptor = _clock()

    answer = machines.drive(source, descriptor, 11, "(Tick)")

    _refused(answer, "a state and an events field of another kind")
    named = machines.fields_the_refusal_names(answer)
    assert "state" in named and "events" in named, (
        f"WHAT: the refusal names {named}, and both fields were written "
        f"wrongly: {answer}. "
        "WHY: the two fields are independent, and an Owner who wrote both "
        "wrongly learns about both at once rather than repairing one and "
        "meeting the next. HOW: read both fields in one pass."
    )
