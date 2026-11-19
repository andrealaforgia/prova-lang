"""F25 criterion 3 behind a call, and every text a descriptor carries.

Two laws the other F25 files leave out:

- a role that must hold for every input of its declared types is refused
  when the functions it reaches ask something of their input, not only
  when its own requires clause does: a clause behind a call binds the
  role as much as one in front of it, and this case shows the refusal
  beside the precondition violation the same program answers when the
  role is run over an input that clause refuses;
- every text a descriptor carries is read before the program is: a text
  this tool cannot write is refused by the name of the field it stands
  in, and no rule of core-0 is read over the source for it.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused every descriptor. The last case sends
the same program with the projection naming a function that reaches
nothing asking anything, and requires it to be accepted.
"""

from __future__ import annotations

import copy
import json
import subprocess

import pytest

import _f25_machine_fixtures as machines

# A machine whose projection asks nothing of its input and reaches a
# helper that does: `guarded` is defined only where the outcome was
# accepted. Written here so the case does not depend on anything this
# repository ships.
A_MACHINE_WITH_A_GUARDED_HELPER = """\
(deftype Position (record (step-count Int)))
(deftype Event (union (Tick)))
(deftype Outcome (record (state Position) (accepted Bool)))

(defn sane
  (sig ((current Position)) -> Bool ! pure)
  (examples (example (sane (Position 0)) => true))
  (>= (.step-count current) 0))

(defn guarded-state
  (sig ((produced Outcome)) -> Position ! pure)
  (requires (.accepted produced))
  (examples (example (guarded-state (Outcome (Position 1) true)) => (Position 1)))
  (.state produced))

(defn projection-over-the-guard
  (sig ((produced Outcome)) -> Position ! pure)
  (examples
    (example (projection-over-the-guard (Outcome (Position 1) true)) => (Position 1)))
  (guarded-state produced))

(defn plain-projection
  (sig ((produced Outcome)) -> Position ! pure)
  (examples (example (plain-projection (Outcome (Position 1) false)) => (Position 1)))
  (.state produced))

(defn start
  (sig () -> Position ! pure)
  (examples (example (start) => (Position 0)))
  (Position 0))

(defn advance
  (sig ((current Position) (event Event)) -> Outcome ! pure)
  (examples
    (example (advance (Position 0) (Tick)) => (Outcome (Position 1) true)))
  (match event
    ((Tick) (Outcome (Position (+ (.step-count current) 1)) true))))

(defn allowed
  (sig ((current Position) (event Event)) -> Bool ! pure)
  (examples (example (allowed (Position 0) (Tick)) => true))
  true)
"""

A_DESCRIPTOR_OVER_THE_GUARD = {
    "schema": machines.THE_SCHEMA_VERSION,
    "types": {"state": "Position", "event": "Event", "outcome": "Outcome"},
    "roles": {
        "init": "start",
        "step": "advance",
        "state-of": "projection-over-the-guard",
        "admissible": "allowed",
        "invariant": "sane",
    },
    "assumptions": ["One tick at a time over one authoritative position."],
}

# An outcome the guarded helper is not defined for: it was not accepted.
AN_OUTCOME_THE_GUARD_REFUSES = "(Outcome (Position 0) false)"

# Every text a descriptor carries, as the field name the refusal must
# name and the path to it in the document.
EVERY_TEXT_OF_A_DESCRIPTOR = [
    pytest.param("descriptor.schema", ("schema",), id="the-version"),
    pytest.param("descriptor.types.state", ("types", "state"), id="the-state-type"),
    pytest.param("descriptor.types.event", ("types", "event"), id="the-event-type"),
    pytest.param("descriptor.types.outcome", ("types", "outcome"), id="the-outcome-type"),
    pytest.param("descriptor.roles.init", ("roles", "init"), id="the-initialiser"),
    pytest.param("descriptor.roles.step", ("roles", "step"), id="the-step"),
    pytest.param("descriptor.roles.state-of", ("roles", "state-of"), id="the-projection"),
    pytest.param(
        "descriptor.roles.admissible", ("roles", "admissible"), id="the-admissibility"
    ),
    pytest.param("descriptor.roles.invariant", ("roles", "invariant"), id="the-invariant"),
    pytest.param(
        "descriptor.assumptions[0]", ("assumptions", 0), id="the-first-assumption"
    ),
]

# Half of a character: one end of a surrogate pair, which has no bytes of
# its own, so no text this tool answers with can carry it.
HALF_A_CHARACTER = "\ud800"

A_SOURCE_THAT_IS_NOT_A_PROGRAM = "(defn"


def test_a_projection_that_reaches_a_guarded_helper_is_refused_naming_the_role():
    """Given a machine whose projection asks nothing of its input and
    calls a helper defined only for an accepted outcome, when the Owner
    asks the tool about its descriptor, then it is refused, the refusal
    names the projection and says which function asks something, and the
    answer carries no result."""
    answer = machines.ask_about_a_machine(
        A_MACHINE_WITH_A_GUARDED_HELPER, A_DESCRIPTOR_OVER_THE_GUARD
    )

    assert answer.get("status") != "completed", (
        f"WHAT: a descriptor whose projection reaches a guarded helper was "
        f"accepted: {answer}. "
        "WHY: the projection must be valid for every outcome of its "
        "declared type, and running it over an outcome the helper refuses "
        "refuses inside the role, so accepting it would confirm a machine "
        "whose projection is undefined for an outcome the step can answer. "
        "HOW: read what the role's function reaches, not only its own "
        "requires clause."
    )
    assert "state-of" in machines.roles_the_refusal_names(answer), (
        f"WHAT: the refusal names {machines.roles_the_refusal_names(answer)}, "
        f"not the projection: {answer}. "
        "WHY: the Owner must be sent to the role to repair. "
        "HOW: carry the role in the refusal."
    )
    reason = (machines.diagnostics_of(answer)[0] or {}).get("reason") or ""
    assert "guarded-state" in reason, (
        f"WHAT: the refusal says {reason!r} and does not name the function "
        "that asks something of its input. "
        "WHY: the Owner reads the role from the refusal and then has to "
        "find the clause; the refusal already knows which function carries "
        "it. HOW: name that function and the line it stands at."
    )
    assert answer.get("result") is None


def test_the_same_program_refuses_that_projection_when_it_is_run():
    """Given the same machine, when the Owner runs the projection over an
    outcome that was not accepted, then the run reports a precondition
    violation: the refusal above is about a clause that really bites, not
    about a clause nothing could reach."""
    answer = machines.run(
        {
            "operation": "evaluate",
            "source": A_MACHINE_WITH_A_GUARDED_HELPER,
            "function": "projection-over-the-guard",
            "arguments": [AN_OUTCOME_THE_GUARD_REFUSES],
        }
    )

    assert "precondition_violation" in machines.categories_of(answer), (
        f"WHAT: running the projection over {AN_OUTCOME_THE_GUARD_REFUSES} "
        f"reported {machines.categories_of(answer)}: {answer}. "
        "WHY: this case is the reason the descriptor above is refused; "
        "without it the refusal could be refusing a machine that works. "
        "HOW: read the requires clause of the guarded helper."
    )


def test_a_projection_that_reaches_nothing_guarded_is_accepted():
    """Given the same machine and a descriptor naming the projection that
    reads the outcome's state directly, when the Owner asks the tool
    about it, then it is accepted: the rule refuses what a role reaches,
    not every role of this program."""
    descriptor = machines.naming(
        A_DESCRIPTOR_OVER_THE_GUARD, "state-of", "plain-projection"
    )

    answer = machines.ask_about_a_machine(A_MACHINE_WITH_A_GUARDED_HELPER, descriptor)

    assert answer.get("status") == "completed", (
        f"WHAT: the projection that reads the state directly was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: it asks nothing of its input and reaches nothing that does, "
        "so refusing it would refuse a machine that meets SPEC.md lines "
        "359-362. HOW: read what the role's function reaches."
    )


@pytest.mark.parametrize("field,path", EVERY_TEXT_OF_A_DESCRIPTOR)
def test_a_text_this_tool_cannot_write_is_refused_by_the_field_it_stands_in(field, path):
    """Given a descriptor one of whose texts carries half of a character,
    sent with a source that is not a program at all, when the Owner asks
    the tool about them, then the answer refuses the request by the name
    of that field, reads no rule of core-0 over the source, and reports
    nothing about the program."""
    descriptor = copy.deepcopy(machines.machine_descriptor("hour-clock"))
    _written_into(descriptor, path, f"half{HALF_A_CHARACTER}a-character")

    answer = machines.run(
        {
            "operation": "machine",
            "source": A_SOURCE_THAT_IS_NOT_A_PROGRAM,
            "descriptor": descriptor,
        }
    )

    assert answer.get("status") == "invalid_input", (
        f"WHAT: a descriptor whose {field} cannot be written was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: a field of a request this tool cannot read is a request to "
        "repair, and this tool writes every text a request carries back "
        "into its answer. HOW: read every text of the descriptor before "
        "the program."
    )
    assert machines.categories_of(answer) == ["malformed_request"], (
        f"WHAT: the answer carries {machines.categories_of(answer)}: "
        f"{answer}. "
        "WHY: the request could not be read, so no rule of core-0 was read "
        "over the source -- which is not a program at all here -- and "
        "nothing about the program can be reported. "
        "HOW: read the texts of the descriptor before the source."
    )
    assert machines.fields_the_refusal_names(answer) == [field], (
        f"WHAT: the answer names {machines.fields_the_refusal_names(answer)}, "
        f"not {field!r}: {answer}. "
        "WHY: the name a refusal sends an Owner to is the field to repair "
        "in the document; a refusal naming the request as a whole leaves "
        "the Owner looking for it. HOW: name the field the text stands in."
    )
    assert answer.get("result") is None


def test_a_descriptor_whose_texts_can_all_be_written_is_read_as_before():
    """Given the shipped descriptor for the hour clock, unchanged, and
    the program it ships beside, when the Owner asks the tool about them,
    then it is accepted: reading every text of the document refuses no
    descriptor that was accepted before."""
    source, descriptor = machines.shipped_machine("hour-clock")

    answer = machines.ask_about_a_machine(source, descriptor)

    assert answer.get("status") == "completed", (
        f"WHAT: the shipped hour clock machine was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: every text of its descriptor can be written, so the rule "
        "above must leave it exactly as it was. HOW: read the refusals."
    )


def _written_into(descriptor: dict, path: tuple, text: str) -> None:
    """`text` written into `descriptor` at `path`, which names a field of
    the document and, for the assumptions, a place in the list."""
    node = descriptor
    for step in path[:-1]:
        node = node[step]
    node[path[-1]] = text


def test_the_command_answers_one_json_object_for_every_one_of_those_texts():
    """Given each of the texts above carrying half of a character, when
    the request is sent, then the command exits 0 and writes one JSON
    object: no text of a descriptor ends a run in a traceback."""
    for field, path in [(case.values[0], case.values[1]) for case in EVERY_TEXT_OF_A_DESCRIPTOR]:
        descriptor = copy.deepcopy(machines.machine_descriptor("hour-clock"))
        _written_into(descriptor, path, HALF_A_CHARACTER)
        proc = subprocess.run(
            ["prova"],
            input=json.dumps(
                {
                    "operation": "machine",
                    "source": A_SOURCE_THAT_IS_NOT_A_PROGRAM,
                    "descriptor": descriptor,
                }
            ),
            capture_output=True,
            text=True,
            timeout=20.0,
        )

        assert proc.returncode == 0, (
            f"WHAT: with {field} carrying half a character the command "
            f"exited {proc.returncode}: stderr={proc.stderr[-400:]!r}. "
            "WHY: the tool answers every request it is sent and never ends "
            "in a traceback. HOW: read the standard error above."
        )
        assert json.loads(proc.stdout).get("status") == "invalid_input", (
            f"WHAT: with {field} carrying half a character the answer was "
            f"{proc.stdout[:300]!r}. "
            "WHY: one JSON answer per request, and this one is a request to "
            "repair. HOW: read the answer above."
        )
