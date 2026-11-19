"""F25 criterion 5 -- the descriptor adds nothing to the language: the
program it is about is ordinary core-0, and a source that writes a
machine form of its own is refused exactly as every other operation
refuses it.

The law: the machine lives in the descriptor document, never in the
source; the source a machine request carries is read by the same rules of
core-0 as a check.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused every source it was handed. The first
test checks the two shipped machine programs as ordinary core-0 and
requires both to be accepted.
"""

from __future__ import annotations

import json

import pytest

import _f25_machine_fixtures as machines

# A source that writes the machine into the program instead of into the
# descriptor. SPEC.md lines 91-118 fix the declarations of core-0 and
# line 350 says machine-0 adds no new temporal syntax, so this is not a
# program of this profile.
A_SOURCE_WRITING_A_MACHINE_FORM = """\
(deftype Clock (record (hr Int)))

(defmachine clock
  (state Clock)
  (init initial)
  (step step))
"""


@pytest.mark.parametrize("machine", machines.MACHINES)
def test_the_program_a_descriptor_is_about_is_ordinary_core_0(machine):
    """Given the program this repository ships for a machine, when it is
    checked as an ordinary program, then it is valid core-0 with no
    diagnostic: the descriptor asked nothing of the language."""
    checked = machines.ask_to_check(machines.machine_source(machine))

    assert checked.get("status") == "completed", (
        f"WHAT: the {machine} machine program was checked "
        f"{checked.get('status')!r}: {checked}. "
        "WHY: criterion 5 promises that the source a descriptor refers to is "
        "ordinary core-0, which is what checking it says. "
        f"HOW: repair examples/{machine}.machine.prova."
    )
    assert machines.diagnostics_of(checked) == [], (
        f"WHAT: checking the {machine} machine program reported "
        f"{machines.diagnostics_of(checked)}. "
        "WHY: an ordinary core-0 program carries no diagnostic. "
        f"HOW: repair examples/{machine}.machine.prova."
    )


def test_a_source_writing_a_machine_form_is_refused():
    """Given a source that writes a `defmachine` form of its own, when
    the Owner asks the tool about it with a descriptor, then the source
    is refused as it is by any other operation: the descriptor adds no
    form to the language."""
    descriptor = machines.machine_descriptor("hour-clock")

    about_the_machine = machines.ask_about_a_machine(
        A_SOURCE_WRITING_A_MACHINE_FORM, descriptor
    )
    checked = machines.ask_to_check(A_SOURCE_WRITING_A_MACHINE_FORM)

    assert about_the_machine.get("status") == checked.get("status"), (
        f"WHAT: a source writing a machine form was answered "
        f"{about_the_machine.get('status')!r} about its machine and "
        f"{checked.get('status')!r} when checked. "
        "WHY: criterion 5 promises that a descriptor adds no syntax, so the "
        "source is read by the rules of core-0 whichever operation reads it. "
        "HOW: read the source through the same rule the other operations use."
    )
    assert about_the_machine.get("status") != "completed", (
        f"WHAT: a source writing a `defmachine` form was accepted: "
        f"{about_the_machine}. "
        "WHY: SPEC.md line 350 says machine-0 adds no new syntax, so no "
        "program of this profile writes that form. "
        "HOW: leave the reading of the source to the rules of core-0."
    )
    assert machines.categories_of(about_the_machine) == machines.categories_of(checked), (
        f"WHAT: the machine request refused the source with "
        f"{machines.categories_of(about_the_machine)} and the check with "
        f"{machines.categories_of(checked)}. "
        "WHY: one source gets one answer; two refusals for one source send "
        "an Owner to two different repairs. "
        "HOW: refuse through the rule the operations share."
    )


def test_the_descriptor_itself_is_not_a_program():
    """Given the descriptor document sent as the source, when the Owner
    asks the tool about it, then it is refused as a source that is not a
    core-0 program: the descriptor travels as its own document."""
    descriptor = machines.machine_descriptor("hour-clock")

    answer = machines.ask_about_a_machine(json.dumps(descriptor), descriptor)
    checked = machines.ask_to_check(json.dumps(descriptor))

    assert answer.get("status") == checked.get("status") != "completed", (
        f"WHAT: the descriptor sent as the program was answered "
        f"{answer.get('status')!r} about its machine and "
        f"{checked.get('status')!r} when checked. "
        "WHY: the source of a machine request is read by the rules of "
        "core-0, as every other operation reads it. "
        "HOW: read the source through the rule the operations share."
    )
    assert answer.get("status") != "completed", (
        f"WHAT: the descriptor document sent as the program was accepted: "
        f"{answer}. "
        "WHY: the descriptor is a separate versioned document, not source; "
        "reading it as a program would make the tool answer about a machine "
        "no program declares. "
        "HOW: read the source by the rules of core-0."
    )
