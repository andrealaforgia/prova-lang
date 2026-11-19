"""Shared fixtures for F25's acceptance tests: the two machines this
repository ships, the request the tests send about one of them, and the
small edits that break exactly one part of a descriptor.

Not itself a test module; imported by the F25 acceptance tests.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova: the promises below are about what an
Owner reads from the tool.
"""

from __future__ import annotations

import copy
import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"

# The descriptor shape version the two shipped descriptors are written in.
THE_SCHEMA_VERSION = "machine-descriptor/1"

# What the descriptor names, as the Owner reads the eight parts of it:
# three types the program must declare, and five functions it must
# declare with the shape its role needs.
THE_TYPE_ROLES = ("state", "event", "outcome")
THE_FUNCTION_ROLES = ("init", "step", "state-of", "admissible", "invariant")
THE_ROLES = THE_TYPE_ROLES + THE_FUNCTION_ROLES

# The four roles SPEC.md lines 359-360 require to be valid for every
# input of their declared types; the step is allowed to ask for an
# invariant state, so it is not one of them.
THE_ROLES_VALID_EVERYWHERE = ("init", "state-of", "admissible", "invariant")

MACHINES = ("hour-clock", "reservation")


def machine_source(machine: str) -> str:
    """The program the shipped descriptor for `machine` is about."""
    return _read(EXAMPLES / f"{machine}.machine.prova")


def machine_descriptor(machine: str) -> dict:
    """The descriptor this repository ships for `machine`."""
    return json.loads(_read(EXAMPLES / f"{machine}.machine.json"))


def shipped_machine(machine: str) -> tuple[str, dict]:
    return machine_source(machine), machine_descriptor(machine)


def shipped_hour_clock_source() -> str:
    """The hour clock this repository ships, which the machine program
    for the hour clock must carry unchanged."""
    return _read(EXAMPLES / "hour-clock.prova")


def spec_reservation_source() -> str:
    """SPEC.md's core conformance example, which the machine program for
    the reservation must carry unchanged."""
    text = _read(REPO_ROOT / "SPEC.md")
    start = text.index("## Core conformance example")
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def ask_about_a_machine(source: str, descriptor: object) -> dict:
    """What the tool answers when it is handed `source` and `descriptor`."""
    return run({"operation": "machine", "source": source, "descriptor": descriptor})


def ask_to_check(source: str) -> dict:
    return run({"operation": "check", "source": source})


def ask_for_the_manifest() -> dict:
    return run({"operation": "discover"})


def published_descriptor_schema() -> dict:
    """The descriptor shape the tool publishes, as an agent reads it."""
    result = ask_for_the_manifest().get("result") or {}
    return result.get("machine_descriptor_schema") or {}


def run(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=20.0,
    )
    assert proc.returncode == 0, (
        f"WHAT: the tool exited {proc.returncode} on a "
        f"{request.get('operation')!r} request: stderr={proc.stderr!r}. "
        "WHY: the tool answers every request it is sent and never ends in a "
        "traceback. HOW: read the standard error above."
    )
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(
            f"WHAT: the answer was not one JSON object: {proc.stdout!r}. "
            "WHY: a caller reads one JSON answer per request. "
            "HOW: read the output above."
        )


# --- the edits that break exactly one part of a descriptor -----------------


def naming(descriptor: dict, role: str, named: str) -> dict:
    """`descriptor` with one role naming `named` and nothing else
    changed."""
    changed = copy.deepcopy(descriptor)
    group = "types" if role in THE_TYPE_ROLES else "roles"
    assert role in changed[group], f"{role!r} is not a role of {sorted(changed[group])}"
    changed[group][role] = named
    return changed


def without(descriptor: dict, role: str) -> dict:
    """`descriptor` with one role left out and nothing else changed."""
    changed = copy.deepcopy(descriptor)
    group = "types" if role in THE_TYPE_ROLES else "roles"
    del changed[group][role]
    return changed


def named_by(descriptor: dict, role: str) -> str:
    group = "types" if role in THE_TYPE_ROLES else "roles"
    return descriptor[group][role]


# A name no program in this repository declares, spelled the way core-0
# spells a function name, so a refusal about it is about the name being
# absent and not about how it is written.
A_NAME_NO_PROGRAM_DECLARES = "no-such-function"
A_TYPE_NO_PROGRAM_DECLARES = "NoSuchType"

# For each role, a name the shipped programs do declare whose shape is
# not the one that role needs. Read off the two programs: `valid-state`
# takes a state and answers a Bool, `initial` takes nothing, `step`
# takes a state and an event and answers an Outcome, `state-of` takes an
# Outcome, `admissible` takes a state and an event.
A_WRONGLY_SHAPED_NAME_FOR = {
    "init": "valid-state",
    "step": "state-of",
    "state-of": "initial",
    "admissible": "step",
    "invariant": "state-of",
}


# The hour clock's machine program with one more candidate for each role
# that SPEC.md requires to be valid for every input of its declared
# types: one that asks for something of its input, and one whose clause
# asks for nothing at all. The two are read against each other, so the
# refusal below is about what the clause demands and not about the clause
# being written.
A_CLOCK_WITH_GUARDED_CANDIDATES = """
(defn careful-initial
  (sig () -> Clock ! pure)
  (requires (= 1 1))
  (examples (example (careful-initial) => (Clock 12)))
  (Clock 12))

(defn careful-state-of
  (sig ((produced Outcome)) -> Clock ! pure)
  (requires (valid-state (.state produced)))
  (examples (example (careful-state-of (Outcome (Clock 3) true)) => (Clock 3)))
  (.state produced))

(defn careful-admissible
  (sig ((current Clock) (event Event)) -> Bool ! pure)
  (requires (valid-state current))
  (examples (example (careful-admissible (Clock 1) (Tick)) => true))
  true)

(defn careful-invariant
  (sig ((current Clock)) -> Bool ! pure)
  (requires (>= (.hr current) 1))
  (examples (example (careful-invariant (Clock 1)) => true))
  (<= (.hr current) 12))

(defn tolerant-invariant
  (sig ((current Clock)) -> Bool ! pure)
  (requires true)
  (examples (example (tolerant-invariant (Clock 1)) => true))
  (and (>= (.hr current) 1) (<= (.hr current) 12)))
"""

# For each role whose function must be valid for every input of its
# declared types, the candidate above that asks for something of its
# input instead.
A_GUARDED_CANDIDATE_FOR = {
    "init": "careful-initial",
    "state-of": "careful-state-of",
    "admissible": "careful-admissible",
    "invariant": "careful-invariant",
}


def clock_with_guarded_candidates() -> str:
    return machine_source("hour-clock") + A_CLOCK_WITH_GUARDED_CANDIDATES


def roles_of(answer: dict) -> dict:
    return ((answer.get("result") or {}).get("roles")) or {}


def diagnostics_of(answer: dict) -> list:
    return answer.get("diagnostics") or []


def roles_the_refusal_names(answer: dict) -> list:
    return [
        diagnostic.get("role")
        for diagnostic in diagnostics_of(answer)
        if diagnostic.get("role") is not None
    ]


def categories_of(answer: dict) -> list:
    return [diagnostic.get("category") for diagnostic in diagnostics_of(answer)]


def fields_the_refusal_names(answer: dict) -> list:
    return [
        diagnostic.get("symbol")
        for diagnostic in diagnostics_of(answer)
        if diagnostic.get("symbol") is not None
    ]


def _read(path: pathlib.Path) -> str:
    assert path.exists(), (
        f"WHAT: {path.relative_to(REPO_ROOT)} is not in this tree. "
        "WHY: the Owner is promised a descriptor for the hour clock and for "
        "the reservation component, shipped beside the program each one is "
        "about; with the file absent the Owner has no descriptor to hand the "
        f"tool. HOW: ship {path.relative_to(REPO_ROOT)}."
    )
    return path.read_text(encoding="utf-8")
