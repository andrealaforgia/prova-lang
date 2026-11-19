"""F26, the published surface -- an agent reads from `discover` that
`verify` takes a descriptor and may leave it out, and reads there the
three obligations the answer lists. A request that leaves the descriptor
out is answered exactly as before. A descriptor field holding something
else is refused by name and never ends in a traceback.

The law: what the tool emits about a machine is what it publishes, the
descriptor is optional for `verify`, and a descriptor the tool cannot
read or cannot resolve leaves the Owner with a refusal naming what to
repair and with no result at all.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool published the field and ignored it. The first
test below requires the published shape to say the field may be left
out, and the third requires the three obligations to appear when it is
sent and to be absent when it is not. Byte-for-byte equality of the
answers this tool gave before is held by the rest of the suite, which
asks for verify answers without a descriptor throughout.
"""

from __future__ import annotations

import pytest

import _f26_induction_fixtures as induction

# What a descriptor field may not hold: values of other kinds, nothing at
# all, and documents this tool does not read.
NOT_A_DESCRIPTOR_THIS_TOOL_READS = (
    7,
    "machine-descriptor/1",
    [],
    None,
    True,
    {},
    {"schema": "machine-descriptor/2"},
    {"schema": "machine-descriptor/1", "types": {}, "roles": {}, "assumptions": []},
    {
        "schema": "machine-descriptor/1",
        "types": {"state": "Clock", "event": "Event", "outcome": "Outcome"},
        "roles": {
            "init": "initial",
            "step": "step",
            "state-of": "state-of",
            "admissible": "admissible",
            "invariant": "valid-state",
        },
        "assumptions": ["One tick at a time."],
        "and-also": {"nested": [{"deeper": 1}]},
    },
)


def test_the_published_shape_of_verify_offers_the_descriptor_and_may_leave_it_out():
    """Given the manifest, when an agent reads the shape of `verify`,
    then the request shape names the descriptor field, says it may be
    left out, and says what it is for."""
    shape = induction.published_verify_shape()

    described = ((shape.get("request") or {}).get("fields") or {}).get("descriptor")

    assert described is not None, (
        f"WHAT: the published request shape of 'verify' names no descriptor "
        f"field: {(shape.get('request') or {}).get('fields')}. "
        "WHY: an agent reads from the manifest which fields an operation "
        "takes; a field it must guess is an undocumented API (SPEC.md line "
        "475). HOW: publish the descriptor among the fields of 'verify'."
    )
    assert described.get("presence") == "optional", (
        f"WHAT: the descriptor field of 'verify' is published as "
        f"{described.get('presence')!r}. "
        "WHY: a verify request without a descriptor is answered about the "
        "program alone, as it always was; a field published as required "
        "would tell every agent that every verify request must carry one. "
        "HOW: publish it as optional."
    )
    assert (described.get("what") or "").strip(), (
        f"WHAT: the descriptor field of 'verify' says nothing about what it "
        f"is for: {described}. "
        "WHY: a client reads what to send there. HOW: say what it carries."
    )


def test_every_machine_obligation_the_answer_lists_is_published():
    """Given the hour clock verified with its descriptor, when an agent
    reads the published answer shape of `verify`, then every machine
    obligation the answer lists is named there."""
    source, descriptor = induction.shipped_machine("hour-clock")
    emitted = sorted(
        induction.the_three_obligations(induction.ask_to_verify(source, descriptor))
    )

    published = str(
        ((induction.published_verify_shape().get("response") or {}).get("fields"))
        or {}
    )

    assert emitted, (
        "WHAT: the answer lists no machine obligation at all, so there is "
        "nothing to read against the manifest. "
        "WHY: this test is about the published names being the answered "
        "ones. HOW: list the three machine obligations."
    )
    for kind in emitted:
        assert kind in published, (
            f"WHAT: the answer lists an obligation of the kind {kind!r} and "
            f"the manifest publishes {published}. "
            "WHY: what an agent reads from the manifest must be what the "
            "answer carries; a kind it meets in an answer and cannot look up "
            "tells it nothing. HOW: name the kind in the published answer "
            "shape of 'verify'."
        )


def test_a_request_that_leaves_the_descriptor_out_is_answered_as_before():
    """Given the hour clock's machine program, when the Owner asks to
    verify it without a descriptor and then with one, then the answer
    without it carries the program's obligations alone, and the answer
    with it carries those same entries in the same order plus exactly
    three more."""
    source, descriptor = induction.shipped_machine("hour-clock")

    without = induction.ask_to_verify(source)
    with_descriptor = induction.ask_to_verify(source, descriptor)

    assert induction.the_three_obligations(without) == {}, (
        f"WHAT: a verify request with no descriptor was answered with "
        f"machine obligations: {sorted(induction.the_three_obligations(without))}. "
        "WHY: without a descriptor there is no machine named, so an entry "
        "about one would be an answer about something nobody sent. "
        "HOW: list them only when a descriptor is read."
    )
    assert "machine" not in (without.get("result") or {}), (
        f"WHAT: a verify answer with no descriptor carries a machine block: "
        f"{(without.get('result') or {}).get('machine')}. "
        "WHY: the answers this tool gave before this feature must stay as "
        "they were. HOW: add the block only when a descriptor is read."
    )
    assert sorted(without) == sorted(with_descriptor), (
        f"WHAT: the answer without a descriptor carries {sorted(without)} and "
        f"the answer with one carries {sorted(with_descriptor)}. "
        "WHY: a descriptor adds obligations inside the inventory, not fields "
        "to the answer: an agent reads one shape for both. "
        "HOW: carry the machine's part inside the published result."
    )
    for part in ("status", "claim", "source_digest", "stands_on", "trust"):
        assert without.get(part) == with_descriptor.get(part), (
            f"WHAT: the {part!r} of the answer changed when a descriptor was "
            f"sent: {without.get(part)!r} became {with_descriptor.get(part)!r}. "
            "WHY: the two answers are about one revision of one program "
            "settled by one solver; a part that moved would say the "
            "descriptor changed what the answer stands on. "
            "HOW: leave that part as it was."
        )
    own = [
        entry
        for entry in induction.listed_obligations(with_descriptor)
        if entry.get("kind") not in induction.THE_THREE
    ]
    assert own == induction.listed_obligations(without), (
        "WHAT: the obligations the program itself owes are not the same "
        "entries, in the same order, in the two answers. "
        "WHY: the Owner compares two answers about one program entry by "
        "entry. HOW: leave the program's own inventory untouched."
    )
    added = len(induction.listed_obligations(with_descriptor)) - len(
        induction.listed_obligations(without)
    )
    assert added == len(induction.THE_THREE), (
        f"WHAT: sending a descriptor added {added} obligations, not "
        f"{len(induction.THE_THREE)}. "
        "WHY: a machine owes the three obligations of SPEC.md lines 395-401 "
        "and no others. HOW: add exactly those three."
    )


@pytest.mark.parametrize("sent", NOT_A_DESCRIPTOR_THIS_TOOL_READS)
def test_a_descriptor_field_this_tool_cannot_read_is_refused_by_name(sent):
    """Given a verify request whose descriptor field holds something
    that is not a descriptor this tool reads, when it is sent, then the
    tool answers a refusal naming the field to repair, carries no result
    and does not end in a traceback."""
    source, _ = induction.shipped_machine("hour-clock")

    answered = induction.ask_to_verify_sending(source, sent)

    assert answered.get("status") != "completed", (
        f"WHAT: a verify request whose descriptor field holds {sent!r} was "
        f"answered {answered.get('status')!r}: {answered}. "
        "WHY: a field this tool cannot read is refused by name before any "
        "work starts; an answer that completed would have read a machine "
        "nobody described. HOW: refuse the field."
    )
    named = induction.fields_the_refusal_names(answered)
    assert any(str(field).startswith("descriptor") for field in named), (
        f"WHAT: the refusal names the fields {named}, none of them the "
        f"descriptor, for a request whose descriptor field holds {sent!r}. "
        "WHY: the Owner must be sent to the place to repair. "
        "HOW: name the field of the document that could not be read."
    )
    assert answered.get("result") is None, (
        f"WHAT: a refused verify request still carries a result: {answered}. "
        "WHY: a result beside a refusal reads as an inventory this tool "
        "settled. HOW: answer a refusal with its refusals alone."
    )
    assert answered.get("aggregate") is None, (
        f"WHAT: a refused verify request still carries a word over the "
        f"whole: {answered.get('aggregate')}. "
        "WHY: a word over a program whose request was not read would rest on "
        "nothing. HOW: carry no aggregate in a refusal."
    )


def test_a_descriptor_whose_roles_do_not_resolve_leaves_no_inventory():
    """Given the reservation's descriptor sent with the hour clock's
    program, so that its state type names nothing the program declares,
    when the Owner asks to verify, then the answer refuses, names the
    role that did not resolve and carries no inventory."""
    clock_source, _ = induction.shipped_machine("hour-clock")
    _, reservation_descriptor = induction.shipped_machine("reservation")

    answered = induction.ask_to_verify(clock_source, reservation_descriptor)

    assert answered.get("status") != "completed", (
        f"WHAT: a descriptor sent with another machine's program was "
        f"answered {answered.get('status')!r}: {answered}. "
        "WHY: the obligations of a machine are stated over the functions its "
        "roles resolve to; a role that resolves to nothing leaves them "
        "unstatable, and an inventory beside that would read as a machine "
        "this tool reasoned about. HOW: refuse the descriptor."
    )
    assert answered.get("result") is None, (
        f"WHAT: the refusal still carries a result: {answered}. "
        "WHY: a result beside a refusal reads as a machine confirmed. "
        "HOW: answer with the refusals alone."
    )
    assert induction.diagnostics_of(answered), (
        f"WHAT: the answer refuses and says nothing about why: {answered}. "
        "WHY: every refusal names what to repair. HOW: carry the refusals of "
        "the roles that did not resolve."
    )
