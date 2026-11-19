"""F25 criterion 3 -- a descriptor whose initialiser, projection,
invariant or admissibility function asks for something of its input is
refused: SPEC.md lines 358-360 require those four to be valid for every
input of their declared types, and this tool establishes that for a
clause that asks for nothing and for no other.

The law: those four roles are confirmed only where nothing narrows their
declared input; the step, which SPEC.md line 360 allows to require an
invariant state, is confirmed with its precondition.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused every function that writes a requires
clause at all, which would also refuse a clause asking for nothing. The
second test sends a role whose clause asks for nothing and requires it
to be accepted.
"""

from __future__ import annotations

import pytest

import _f25_machine_fixtures as machines


@pytest.mark.parametrize("role", machines.THE_ROLES_VALID_EVERYWHERE)
def test_a_role_asking_something_of_its_input_is_refused_naming_the_role(role):
    """Given a program whose candidate for the initialiser, the
    projection, the admissibility predicate or the invariant asks
    something of its input, and a descriptor naming that candidate for
    the role, when the Owner asks the tool about it, then it is refused
    and the refusal names that role."""
    source = machines.clock_with_guarded_candidates()
    descriptor = machines.naming(
        machines.machine_descriptor("hour-clock"),
        role,
        machines.A_GUARDED_CANDIDATE_FOR[role],
    )

    answer = machines.ask_about_a_machine(source, descriptor)

    assert answer.get("status") != "completed", (
        f"WHAT: a descriptor whose {role!r} role names a function with a "
        f"precondition was accepted: {answer}. "
        "WHY: criterion 3 promises that a descriptor whose initialiser, "
        "projection, invariant or admissibility function has a precondition "
        "that is not valid for every input of its type is refused. "
        "HOW: read what the named function asks for."
    )
    assert role in machines.roles_the_refusal_names(answer), (
        f"WHAT: the refusal names "
        f"{machines.roles_the_refusal_names(answer)}, not {role!r}: {answer}. "
        "WHY: the Owner must know which of the roles to repair. "
        "HOW: carry the role in the refusal."
    )
    assert answer.get("result") is None, (
        f"WHAT: a refused descriptor still carries a result: {answer}. "
        "WHY: a result beside a refusal reads as a machine the tool "
        "confirmed. HOW: answer a refusal with its refusals alone."
    )
    reason = (machines.diagnostics_of(answer)[0] or {}).get("reason") or ""
    assert "every input" in reason, (
        f"WHAT: the refusal about the {role!r} role says {reason!r}, and does "
        "not say that the role needs a precondition valid for every input of "
        "its declared types. "
        "WHY: an Owner told only that a clause is in the way does not learn "
        "what the role requires. HOW: say it in the refusal."
    )


def test_a_role_whose_clause_asks_for_nothing_is_accepted():
    """Given a program whose candidate for the invariant writes a
    precondition that asks for nothing, and a descriptor naming it, when
    the Owner asks the tool about it, then the descriptor is accepted: a
    clause that asks for nothing is valid for every input."""
    source = machines.clock_with_guarded_candidates()
    descriptor = machines.naming(
        machines.machine_descriptor("hour-clock"), "invariant", "tolerant-invariant"
    )

    answer = machines.ask_about_a_machine(source, descriptor)

    assert answer.get("status") == "completed", (
        f"WHAT: a descriptor whose invariant writes a clause asking for "
        f"nothing was answered {answer.get('status')!r}: {answer}. "
        "WHY: a precondition that asks for nothing is valid for every input "
        "of the declared type, so refusing it would refuse a machine that "
        "meets SPEC.md lines 358-360. "
        "HOW: read what the clause asks for, not whether it is written."
    )
    assert machines.roles_of(answer)["invariant"]["named"] == "tolerant-invariant"


def test_the_step_is_accepted_with_the_precondition_it_declares():
    """Given the shipped hour clock machine, whose step asks for a valid
    state, when the Owner asks the tool about its descriptor, then it is
    accepted: SPEC.md line 360 allows the step to require an invariant
    state."""
    source, descriptor = machines.shipped_machine("hour-clock")

    answer = machines.ask_about_a_machine(source, descriptor)

    assert answer.get("status") == "completed", (
        f"WHAT: the shipped hour clock machine was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: its step asks for a valid state, which SPEC.md line 360 "
        "allows; a tool that refused it would refuse every real machine. "
        "HOW: apply the rule about preconditions to the four roles SPEC.md "
        "names, and not to the step."
    )
    assert "step" not in machines.roles_the_refusal_names(answer)


def test_the_program_with_a_guarded_candidate_is_itself_a_valid_program():
    """Given the program the two tests above send, when it is checked on
    its own, then it is a valid core-0 program with no diagnostic: the
    refusals above are about the descriptor, not about the program."""
    checked = machines.ask_to_check(machines.clock_with_guarded_candidates())

    assert checked.get("status") == "completed" and machines.diagnostics_of(checked) == [], (
        f"WHAT: the program these cases send is not checked clean: {checked}. "
        "WHY: without this control a refusal above could be the program "
        "breaking a rule of core-0 rather than the role being refused. "
        "HOW: repair the program in tests/acceptance/_f25_machine_fixtures.py."
    )
