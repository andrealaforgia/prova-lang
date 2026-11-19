"""F25 criterion 1 and criterion 4 -- the Owner hands the tool a
descriptor naming the initialiser, the step, the projection, the
admissibility predicate and the invariant of a program, and is told that
each of them resolves to a checked function of the shape its role needs,
beside the version of the descriptor shape that was read.

The law: a descriptor is confirmed only when every one of its eight
parts -- the three types and the five functions -- resolves in the
submitted program, and the answer says what each one resolved to.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool answered 'completed' for every descriptor it is
sent. test_f25_b2 and test_f25_b3 send descriptors with one part broken
at a time and require each of them to be refused, so a tool that accepts
everything fails there.
"""

from __future__ import annotations

import pytest

import _f25_machine_fixtures as machines


@pytest.mark.parametrize("machine", machines.MACHINES)
def test_a_descriptor_whose_eight_parts_resolve_is_accepted(machine):
    """Given the descriptor this repository ships for a machine and the
    program it is about, when the Owner asks the tool about them, then
    the answer is completed with no refusal at all, and every one of the
    eight parts is reported with the name it resolved to."""
    source, descriptor = machines.shipped_machine(machine)

    answer = machines.ask_about_a_machine(source, descriptor)

    assert answer.get("status") == "completed", (
        f"WHAT: the descriptor for the {machine} was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: criterion 1 promises that a descriptor whose five roles "
        "resolve to checked functions of the right shapes is accepted. "
        f"HOW: read the refusals above against examples/{machine}.machine.json "
        f"and examples/{machine}.machine.prova."
    )
    assert machines.diagnostics_of(answer) == [], (
        f"WHAT: the accepted descriptor still carries "
        f"{machines.diagnostics_of(answer)}. "
        "WHY: an accepted descriptor is one with nothing left to repair. "
        "HOW: read the refusals above."
    )
    reported = machines.roles_of(answer)
    assert sorted(reported) == sorted(machines.THE_ROLES), (
        f"WHAT: the answer reports the roles {sorted(reported)}, not the "
        f"{len(machines.THE_ROLES)} the descriptor names: "
        f"{sorted(machines.THE_ROLES)}. "
        "WHY: the Owner asked whether the five roles and the three types "
        "resolve; a role missing from the answer is one nothing was said "
        "about. HOW: report one entry per part of the descriptor."
    )
    for role in machines.THE_ROLES:
        assert reported[role].get("named") == machines.named_by(descriptor, role), (
            f"WHAT: the answer says the {role!r} role resolved "
            f"{reported[role].get('named')!r}, and the descriptor names "
            f"{machines.named_by(descriptor, role)!r}. "
            "WHY: the Owner reads the answer against the descriptor "
            "written; a different name there is an answer about another "
            "machine. HOW: report the name the descriptor gave the role."
        )
        assert reported[role].get("shape"), (
            f"WHAT: the answer says nothing about the shape the {role!r} "
            f"role resolved to: {reported[role]}. "
            "WHY: criterion 1 is about functions of the right shapes, so "
            "the shape read is what the Owner needs to see. "
            "HOW: report the shape beside the name."
        )


@pytest.mark.parametrize("machine", machines.MACHINES)
def test_the_answer_records_the_schema_version_the_descriptor_was_read_in(machine):
    """Given a descriptor written in version `machine-descriptor/1`, when
    the Owner asks the tool about it, then the answer records that
    version."""
    source, descriptor = machines.shipped_machine(machine)

    recorded = (machines.ask_about_a_machine(source, descriptor).get("result") or {}).get(
        "schema"
    )

    assert recorded == machines.THE_SCHEMA_VERSION, (
        f"WHAT: the answer records the descriptor version {recorded!r}, not "
        f"{machines.THE_SCHEMA_VERSION!r}. "
        "WHY: criterion 4 promises that the schema version of the descriptor "
        "is recorded in the answer: an answer kept beside a descriptor of "
        "another version says which shape it was read in. "
        f"HOW: record the version read from the descriptor's 'schema' field."
    )


@pytest.mark.parametrize("machine", machines.MACHINES)
def test_the_answer_repeats_the_assumptions_the_descriptor_states(machine):
    """Given a descriptor stating the runtime assumptions of its machine,
    when the Owner asks the tool about it, then the answer carries those
    same sentences, as stated by the descriptor and not as anything the
    tool established."""
    source, descriptor = machines.shipped_machine(machine)

    result = machines.ask_about_a_machine(source, descriptor).get("result") or {}

    assert result.get("assumptions_stated") == descriptor["assumptions"], (
        f"WHAT: the answer carries the assumptions "
        f"{result.get('assumptions_stated')!r}, and the descriptor states "
        f"{descriptor['assumptions']!r}. "
        "WHY: the assumptions are the conditions the machine's evidence is "
        "conditional on; an answer that drops or rewrites them hides what "
        "the confirmation rests on. "
        "HOW: carry the stated sentences through unchanged."
    )
    assert "assumptions" not in result, (
        f"WHAT: the answer carries a field named 'assumptions': {result}. "
        "WHY: the tool checks none of them, so a field that reads as a "
        "property of the machine would be read as a checked one; the field "
        "says that they are stated. "
        "HOW: carry them under 'assumptions_stated' alone."
    )


def test_the_two_machines_are_answered_about_apart():
    """Given the two machines this repository ships, when each descriptor
    is sent with the other machine's program, then both are refused: an
    accepted answer is about the one program it was sent."""
    clock_source, clock_descriptor = machines.shipped_machine("hour-clock")
    reservation_source, reservation_descriptor = machines.shipped_machine("reservation")

    crossed = (
        machines.ask_about_a_machine(clock_source, reservation_descriptor),
        machines.ask_about_a_machine(reservation_source, clock_descriptor),
    )

    for answer in crossed:
        assert answer.get("status") != "completed", (
            f"WHAT: a descriptor sent with the other machine's program was "
            f"accepted: {answer}. "
            "WHY: the two machines declare different state types, so a "
            "descriptor confirmed against either program would be "
            "confirming a machine that is not there. "
            "HOW: resolve every role against the submitted program."
        )
        assert answer.get("result") is None, (
            f"WHAT: a refused descriptor still carries a result: {answer}. "
            "WHY: a result beside a refusal reads as a machine the tool "
            "confirmed. HOW: answer a refusal with its refusals alone."
        )
        assert "state" in machines.roles_the_refusal_names(answer), (
            f"WHAT: the refusal names "
            f"{machines.roles_the_refusal_names(answer)}, and the part that "
            "does not resolve is the state type the other machine declares. "
            "WHY: the Owner must be sent to the part of the descriptor to "
            "repair. HOW: name the role whose name the program does not "
            "declare."
        )
