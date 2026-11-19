"""F25 -- a descriptor the tool cannot read is refused by the name of the
field that could not be read, before any role is resolved, and two fields
written wrongly are both named in one answer.

The law: the descriptor is read once, by name, through the same reader
that reads every other field of a request; a field of the wrong kind, an
unknown field, a missing role or a version the tool does not read is a
request to repair and never a refusal about the program.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused every descriptor with one sentence
naming nothing. Each case below reads back the field the answer names.
"""

from __future__ import annotations

import copy

import pytest

import _f25_machine_fixtures as machines

A_MACHINE = "hour-clock"
MALFORMED_REQUEST = "malformed_request"


def _without(key: str) -> dict:
    document = machines.machine_descriptor(A_MACHINE)
    del document[key]
    return document


def _with(key: str, value: object) -> dict:
    document = machines.machine_descriptor(A_MACHINE)
    document[key] = value
    return document


def _roles_with(key: str, value: object) -> dict:
    document = machines.machine_descriptor(A_MACHINE)
    document["roles"][key] = value
    return document


# Each case: what is wrong with the descriptor, written as the edit that
# breaks it, and the name the answer must send the Owner to. The edits
# are run inside each case, so a case says what it sends even where the
# shipped descriptor it starts from is not in the tree.
UNREADABLE_DESCRIPTORS = [
    pytest.param(lambda: None, "descriptor", id="no-descriptor-at-all"),
    pytest.param(lambda: "machine-descriptor/1", "descriptor", id="a-text-not-a-document"),
    pytest.param(lambda: [], "descriptor", id="a-list-not-a-document"),
    pytest.param(lambda: 7, "descriptor", id="a-number-not-a-document"),
    pytest.param(lambda: _without("schema"), "descriptor.schema", id="no-version"),
    pytest.param(
        lambda: _with("schema", "machine-descriptor/99"),
        "descriptor.schema",
        id="a-version-this-tool-does-not-read",
    ),
    pytest.param(lambda: _without("roles"), "descriptor.roles", id="no-roles"),
    pytest.param(lambda: _without("types"), "descriptor.types", id="no-types"),
    pytest.param(
        lambda: _without("assumptions"), "descriptor.assumptions", id="no-assumptions"
    ),
    pytest.param(
        lambda: _with("assumptions", "one at a time"),
        "descriptor.assumptions",
        id="assumptions-as-one-text",
    ),
    pytest.param(
        lambda: _with("assumptions", []),
        "descriptor.assumptions",
        id="assumptions-stated-as-none",
    ),
    pytest.param(
        lambda: _with("machine", "the hour clock"),
        "descriptor.machine",
        id="a-field-this-tool-does-not-read",
    ),
    pytest.param(
        lambda: machines.without(machines.machine_descriptor(A_MACHINE), "step"),
        "descriptor.roles.step",
        id="a-role-left-out",
    ),
    pytest.param(
        lambda: machines.without(machines.machine_descriptor(A_MACHINE), "state"),
        "descriptor.types.state",
        id="a-type-left-out",
    ),
    pytest.param(
        lambda: _roles_with("step", 12), "descriptor.roles.step", id="a-role-as-a-number"
    ),
    pytest.param(
        lambda: _roles_with("transition", "step"),
        "descriptor.roles.transition",
        id="a-role-this-tool-does-not-read",
    ),
]


@pytest.mark.parametrize("broken,field", UNREADABLE_DESCRIPTORS)
def test_a_descriptor_this_tool_cannot_read_names_the_field_to_repair(broken, field):
    """Given a descriptor with one part the tool cannot read -- no
    document at all, a document of the wrong kind, a missing or unknown
    field, a role of the wrong kind or a version the tool does not read
    -- when the Owner asks the tool about it, then the answer refuses the
    request and names that field."""
    descriptor = broken()
    request = {"operation": "machine", "source": machines.machine_source(A_MACHINE)}
    if descriptor is not None:
        request["descriptor"] = descriptor

    answer = machines.run(request)

    assert answer.get("status") == "invalid_input", (
        f"WHAT: a descriptor the tool cannot read was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: a field of a request the tool cannot read is a request to "
        "repair, which this tool answers 'invalid_input'. "
        "HOW: read the descriptor through the reader of the request."
    )
    assert MALFORMED_REQUEST in machines.categories_of(answer), (
        f"WHAT: the answer carries {machines.categories_of(answer)}, not a "
        f"{MALFORMED_REQUEST!r} refusal: {answer}. "
        "WHY: the descriptor is a field of the request; a refusal of another "
        "category reads as a refusal about the program. "
        "HOW: refuse it as the other fields of a request are refused."
    )
    assert field in machines.fields_the_refusal_names(answer), (
        f"WHAT: the answer names {machines.fields_the_refusal_names(answer)}, "
        f"not {field!r}: {answer}. "
        "WHY: the name a refusal sends an Owner to is the name the Owner "
        "repairs in the document. HOW: name the field that could not be read."
    )
    assert answer.get("result") is None, (
        f"WHAT: a request the tool could not read still carries a result: "
        f"{answer}. "
        "WHY: nothing was resolved, so there is nothing to report. "
        "HOW: answer the refusal alone."
    )


def test_two_fields_written_wrongly_are_both_named_in_one_answer():
    """Given a descriptor with an unknown field and a role of the wrong
    kind, when the Owner asks the tool about it, then both are named in
    the one answer, so the Owner repairs both rather than meeting the
    second after repairing the first."""
    document = machines.machine_descriptor(A_MACHINE)
    document["machine"] = "the hour clock"
    document["roles"]["step"] = 12

    named = machines.fields_the_refusal_names(
        machines.ask_about_a_machine(machines.machine_source(A_MACHINE), document)
    )

    assert {"descriptor.machine", "descriptor.roles.step"} <= set(named), (
        f"WHAT: the answer names {named}, not both the unknown field and the "
        "role of the wrong kind. "
        "WHY: the fields are independent, so an Owner who wrote two of them "
        "wrongly learns about both at once. "
        "HOW: collect every field that could not be read and answer them "
        "together."
    )


def test_a_descriptor_that_cannot_be_read_is_refused_before_the_program_is_read():
    """Given a source that is not a core-0 program at all and a
    descriptor the tool cannot read, when the Owner asks the tool about
    them, then the answer is about the descriptor: a request the tool
    cannot read is refused before any rule of core-0 is read over the
    source."""
    answer = machines.ask_about_a_machine("(defn", copy.deepcopy([]))

    assert machines.categories_of(answer) == [MALFORMED_REQUEST], (
        f"WHAT: the answer carries {machines.categories_of(answer)}: {answer}. "
        "WHY: the request could not be read, so no rule of core-0 was read "
        "over the source and nothing about the program can be reported. "
        "HOW: read the fields of the request before the program."
    )
