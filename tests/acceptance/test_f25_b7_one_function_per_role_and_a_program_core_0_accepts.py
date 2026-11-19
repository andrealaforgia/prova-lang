"""F25 criteria 2 and 5, over two cases the other F25 files leave out: a
descriptor that gives one function two roles, and a machine program that
declares an effect core-0 does not have.

The laws: a role is confirmed only by the shape its own role needs, so one
function cannot fill two roles whose shapes differ; and the source of a
machine request is read by the rules of core-0, so a program outside the
profile is refused there exactly as it is refused anywhere else.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused every descriptor and every program. The
first case reads back the role the refusal names, and the second requires
the two operations to refuse the same source with the same category, which
a tool refusing everything for one reason fails.
"""

from __future__ import annotations

import _f25_machine_fixtures as machines

A_MACHINE = "hour-clock"

# The effect core-0 does not have. SPEC.md lines 96-99 fix the effect a
# signature may declare, and `pure` is the only one, so a program writing
# this one is outside the profile whichever operation reads it.
AN_EFFECT_CORE_0_DOES_NOT_HAVE = "! io"
THE_ONE_EFFECT_CORE_0_HAS = "! pure"


def test_one_function_cannot_fill_two_roles_whose_shapes_differ():
    """Given the hour clock's descriptor with the projection naming
    `initial`, the function the initialiser already names, when the Owner
    asks the tool about it, then it is refused and the refusal names the
    projection: the two roles need different shapes, and one function has
    one shape."""
    source, descriptor = machines.shipped_machine(A_MACHINE)
    both = machines.naming(descriptor, "state-of", machines.named_by(descriptor, "init"))

    answer = machines.ask_about_a_machine(source, both)

    assert answer.get("status") != "completed", (
        f"WHAT: a descriptor naming one function for both the initialiser "
        f"and the projection was accepted: {answer}. "
        "WHY: the initialiser answers a state from nothing and the "
        "projection answers a state from an outcome, so one function cannot "
        "have both shapes; accepting it would confirm a machine whose "
        "projection ignores the outcome it is given. "
        "HOW: resolve each role against the shape that role needs."
    )
    assert "state-of" in machines.roles_the_refusal_names(answer), (
        f"WHAT: the refusal names {machines.roles_the_refusal_names(answer)}, "
        f"not the projection: {answer}. "
        "WHY: the Owner must be sent to the role to repair, and the "
        "initialiser is the one role of the two that resolves. "
        "HOW: carry the role in the refusal."
    )
    assert answer.get("result") is None, (
        f"WHAT: a refused descriptor still carries a result: {answer}. "
        "WHY: a result beside a refusal reads as a machine the tool "
        "confirmed. HOW: answer a refusal with its refusals alone."
    )


def test_a_machine_program_declaring_an_effect_core_0_lacks_is_refused():
    """Given a machine program whose projection declares the effect `io`,
    which core-0 does not have, and the descriptor that names it, when the
    Owner asks the tool about them, then the program is refused exactly as
    a check refuses it, with no result and with the same refusal
    category."""
    source, descriptor = machines.shipped_machine(A_MACHINE)
    with_an_effect = source.replace(
        f"(sig ((produced Outcome)) -> Clock {THE_ONE_EFFECT_CORE_0_HAS})",
        f"(sig ((produced Outcome)) -> Clock {AN_EFFECT_CORE_0_DOES_NOT_HAVE})",
    )
    assert with_an_effect != source, (
        "WHAT: the program this case sends is the shipped machine program "
        "unchanged. WHY: without the effect the case would prove nothing. "
        "HOW: read the projection's signature in "
        "examples/hour-clock.machine.prova."
    )

    about_the_machine = machines.ask_about_a_machine(with_an_effect, descriptor)
    checked = machines.ask_to_check(with_an_effect)

    assert about_the_machine.get("status") == checked.get("status") != "completed", (
        f"WHAT: the program was answered {about_the_machine.get('status')!r} "
        f"about its machine and {checked.get('status')!r} when checked. "
        "WHY: the source of a machine request is read by the rules of "
        "core-0, as every other operation reads it, so one source gets one "
        "answer. HOW: read the source through the rule the operations share."
    )
    assert machines.categories_of(about_the_machine) == machines.categories_of(checked), (
        f"WHAT: the machine request refused the source with "
        f"{machines.categories_of(about_the_machine)} and the check with "
        f"{machines.categories_of(checked)}. "
        "WHY: two refusals for one source send an Owner to two different "
        "repairs. HOW: refuse through the rule the operations share."
    )
    assert about_the_machine.get("result") is None, (
        f"WHAT: a refused source still carries a result: {about_the_machine}. "
        "WHY: a result beside a refusal reads as a machine this tool "
        "confirmed. HOW: answer a refusal with its refusals alone."
    )


def test_the_shipped_program_the_two_cases_start_from_is_accepted():
    """Given the shipped machine program and its descriptor, unchanged,
    when the Owner asks the tool about them, then they are accepted: the
    two refusals above are the one edit each case makes and not the
    program they start from."""
    source, descriptor = machines.shipped_machine(A_MACHINE)

    answer = machines.ask_about_a_machine(source, descriptor)

    assert answer.get("status") == "completed", (
        f"WHAT: the shipped machine was answered {answer.get('status')!r}: "
        f"{answer}. "
        "WHY: without this control a refusal above could be the program the "
        "case starts from rather than the edit it makes. "
        "HOW: read the refusals above."
    )
