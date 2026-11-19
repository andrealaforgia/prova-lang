"""F25 criterion 2 -- a descriptor naming a function the program does not
declare, or one whose arguments or result are not the ones its role
needs, is refused, and the refusal names the role so the Owner knows
which of the five to repair.

The law: a part of the descriptor that does not resolve is refused by
name; the answer never reports a machine it could not resolve.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused every descriptor, whatever it named.
test_f25_b1 sends the two shipped descriptors and requires both to be
accepted, so a tool that refuses everything fails there.
"""

from __future__ import annotations

import pytest

import _f25_machine_fixtures as machines

A_MACHINE = "hour-clock"


@pytest.mark.parametrize("role", machines.THE_FUNCTION_ROLES)
def test_a_role_naming_a_function_the_program_does_not_declare_is_refused(role):
    """Given the hour clock's descriptor with one role naming
    `no-such-function`, a name the program does not declare, when the
    Owner asks the tool about it, then it is refused and a refusal names
    that role."""
    source, descriptor = machines.shipped_machine(A_MACHINE)
    broken = machines.naming(descriptor, role, machines.A_NAME_NO_PROGRAM_DECLARES)

    answer = machines.ask_about_a_machine(source, broken)

    _assert_refused_naming(answer, role, machines.A_NAME_NO_PROGRAM_DECLARES)


@pytest.mark.parametrize("role", machines.THE_FUNCTION_ROLES)
def test_a_role_naming_a_function_of_another_shape_is_refused(role):
    """Given the hour clock's descriptor with one role naming a function
    the program does declare but whose arguments or result are not the
    ones that role needs -- the initialiser naming `valid-state`, which
    takes a clock and answers a Bool, and so on -- when the Owner asks
    the tool about it, then it is refused and a refusal names that
    role."""
    source, descriptor = machines.shipped_machine(A_MACHINE)
    wrongly_shaped = machines.A_WRONGLY_SHAPED_NAME_FOR[role]
    broken = machines.naming(descriptor, role, wrongly_shaped)

    answer = machines.ask_about_a_machine(source, broken)

    _assert_refused_naming(answer, role, wrongly_shaped)


@pytest.mark.parametrize("role", machines.THE_TYPE_ROLES)
def test_a_type_the_program_does_not_declare_is_refused_naming_its_role(role):
    """Given the hour clock's descriptor with the state, the event or the
    outcome naming `NoSuchType`, which the program does not declare, when
    the Owner asks the tool about it, then it is refused and a refusal
    names that part of the descriptor."""
    source, descriptor = machines.shipped_machine(A_MACHINE)
    broken = machines.naming(descriptor, role, machines.A_TYPE_NO_PROGRAM_DECLARES)

    answer = machines.ask_about_a_machine(source, broken)

    _assert_refused_naming(answer, role, machines.A_TYPE_NO_PROGRAM_DECLARES)


def test_a_refusal_says_which_revision_of_the_source_it_is_about():
    """Given a descriptor naming a function the program does not declare,
    when it is refused, then every refusal says which revision of the
    submitted source it was read against."""
    source, descriptor = machines.shipped_machine(A_MACHINE)
    broken = machines.naming(descriptor, "step", machines.A_NAME_NO_PROGRAM_DECLARES)

    answer = machines.ask_about_a_machine(source, broken)

    for diagnostic in machines.diagnostics_of(answer):
        assert diagnostic.get("source_revision"), (
            f"WHAT: a refusal about the machine says nothing about which "
            f"source it is about: {diagnostic}. "
            "WHY: a refusal kept beside a program the Owner has since "
            "edited says which text it was read against. "
            "HOW: carry the revision of the submitted source."
        )


def test_the_program_a_refused_descriptor_was_sent_with_is_left_as_it_was():
    """Given a descriptor the tool refuses, when the Owner then checks
    the same program, then the program is still checked clean: a refused
    descriptor changes nothing about the program it was sent with."""
    source, descriptor = machines.shipped_machine(A_MACHINE)
    broken = machines.naming(descriptor, "invariant", machines.A_NAME_NO_PROGRAM_DECLARES)

    refused = machines.ask_about_a_machine(source, broken)
    checked_after = machines.ask_to_check(source)

    assert "invariant" in machines.roles_the_refusal_names(refused), (
        f"WHAT: the refusal names {machines.roles_the_refusal_names(refused)}, "
        "not the invariant, which is the role that does not resolve. "
        "WHY: without this the case below would hold for a tool that refuses "
        "every descriptor for any reason. HOW: name the role in the refusal."
    )
    assert checked_after.get("status") == "completed", (
        f"WHAT: after a refused descriptor the program itself was answered "
        f"{checked_after.get('status')!r}: {checked_after}. "
        "WHY: the descriptor is a separate document; a refusal about it says "
        "nothing about the program and must leave it as it was. "
        "HOW: read the check above."
    )
    assert machines.diagnostics_of(checked_after) == [], (
        f"WHAT: the program carries {machines.diagnostics_of(checked_after)} "
        "after a descriptor about it was refused. "
        "WHY: a refused descriptor leaves the program exactly as it was. "
        "HOW: read the refusals above."
    )


def test_a_descriptor_with_two_roles_broken_names_both_of_them():
    """Given a descriptor with two roles naming functions the program
    does not declare, when the Owner asks the tool about it, then both
    roles are named in the one answer, so the Owner repairs both at once
    rather than meeting the second only after repairing the first."""
    source, descriptor = machines.shipped_machine(A_MACHINE)
    broken = machines.naming(
        machines.naming(descriptor, "init", machines.A_NAME_NO_PROGRAM_DECLARES),
        "invariant",
        machines.A_NAME_NO_PROGRAM_DECLARES,
    )

    named = machines.roles_the_refusal_names(machines.ask_about_a_machine(source, broken))

    assert {"init", "invariant"} <= set(named), (
        f"WHAT: the answer names the roles {named}, not both 'init' and "
        "'invariant'. "
        "WHY: the roles are independent, so an Owner who wrote two of them "
        "wrongly is told about both in one answer. "
        "HOW: resolve every role and report every one that did not."
    )


def _assert_refused_naming(answer: dict, role: str, named: str) -> None:
    assert answer.get("status") != "completed", (
        f"WHAT: a descriptor whose {role!r} role names {named!r} was "
        f"accepted: {answer}. "
        "WHY: criterion 2 promises that a descriptor naming a function that "
        "does not exist, or one with the wrong argument or result types, is "
        "refused. HOW: resolve the role against the submitted program and "
        "refuse when it does not."
    )
    assert role in machines.roles_the_refusal_names(answer), (
        f"WHAT: the refusal names the roles "
        f"{machines.roles_the_refusal_names(answer)}, not {role!r}: {answer}. "
        "WHY: criterion 2 promises that the diagnostic names the role, so "
        "the Owner knows which of the eight parts of the descriptor to "
        "repair. HOW: carry the role in the refusal."
    )
    assert answer.get("result") is None, (
        f"WHAT: a refused descriptor still carries a result: {answer}. "
        "WHY: a result beside a refusal reads as a machine the tool "
        "confirmed. HOW: answer a refusal with its refusals alone."
    )
    for diagnostic in machines.diagnostics_of(answer):
        reason = diagnostic.get("reason") or ""
        assert len(reason) > 30, (
            f"WHAT: a refusal about the {role!r} role says {reason!r}. "
            "WHY: every refusal of this tool says what failed, why and how "
            "to repair it. HOW: write the sentence."
        )
