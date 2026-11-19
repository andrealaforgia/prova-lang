"""Shared fixtures for F26's acceptance tests: the machines whose three
inductive obligations the Owner asks about, and the small readers that
pick those three obligations out of a verify answer.

Not itself a test module; imported by the F26 acceptance tests.

Drives only the installed `prova` command over its JSON stdin/stdout
surface, through the F25 fixtures that already own that one call. No
imports from src/prova: the promises below are about what an Owner reads
from the tool.
"""

from __future__ import annotations

import json

import _f25_machine_fixtures as machines

MACHINES = machines.MACHINES
THE_SCHEMA_VERSION = machines.THE_SCHEMA_VERSION

# The three obligations SPEC.md lines 395-401 state for a candidate
# inductive invariant, as the answer names them. These three names are
# the machine contract an agent reads entries by.
INITIALISATION = "machine_initialisation"
STEP_ENABLEDNESS = "machine_step_enabledness"
PRESERVATION = "machine_preservation"
THE_THREE = (INITIALISATION, STEP_ENABLEDNESS, PRESERVATION)

PROVED = "proved"
NOT_VERIFIED = "not_verified"
VERIFIED = "verified"


def shipped_machine(machine: str) -> tuple[str, dict]:
    """The program and the descriptor this repository ships for
    `machine`."""
    return machines.shipped_machine(machine)


def ask_to_verify(source: str, descriptor: object = None) -> dict:
    """What the tool answers when it is asked to verify `source`, with
    `descriptor` sent when one is given and the field left out when it is
    not."""
    request = {"operation": "verify", "source": source}
    if descriptor is not None:
        request["descriptor"] = descriptor
    return machines.run(request)


def ask_to_verify_sending(source: str, descriptor_field: object) -> dict:
    """What the tool answers when the descriptor field of a verify
    request carries `descriptor_field`, whatever kind of value that is --
    including nothing at all."""
    return machines.run(
        {"operation": "verify", "source": source, "descriptor": descriptor_field}
    )


def ask_for_the_manifest() -> dict:
    return machines.ask_for_the_manifest()


def published_verify_shape() -> dict:
    """The request and answer shape the tool publishes for `verify`."""
    result = ask_for_the_manifest().get("result") or {}
    schemas = result.get("operation_schemas") or {}
    return schemas.get("verify") or {}


# --- reading a verify answer ------------------------------------------------


def inventory_of(answer: dict) -> dict:
    return ((answer.get("result") or {}).get("inventory")) or {}


def listed_obligations(answer: dict) -> list:
    return inventory_of(answer).get("obligations") or []


def the_three_obligations(answer: dict) -> dict:
    """The entries of the three machine obligations, by the kind each one
    carries."""
    return {
        entry.get("kind"): entry
        for entry in listed_obligations(answer)
        if entry.get("kind") in THE_THREE
    }


def how_the_three_stand(answer: dict) -> dict:
    return {
        kind: entry.get("result")
        for kind, entry in the_three_obligations(answer).items()
    }


def machine_block_of(answer: dict) -> dict:
    """What the answer says about the descriptor it read."""
    return ((answer.get("result") or {}).get("machine")) or {}


def aggregate_of(answer: dict) -> dict:
    return answer.get("aggregate") or {}


def text_of(answer: dict) -> str:
    """The whole answer as one text, for reading what it does and does
    not say."""
    return json.dumps(answer, sort_keys=True)


def text_of_the_three(answer: dict) -> str:
    return json.dumps(the_three_obligations(answer), sort_keys=True)


def diagnostics_of(answer: dict) -> list:
    return machines.diagnostics_of(answer)


def fields_the_refusal_names(answer: dict) -> list:
    return machines.fields_the_refusal_names(answer)


# --- the machines the F26 tests are about ----------------------------------


def a_descriptor_naming(state_type: str) -> dict:
    """The descriptor of a machine written below: they all name their
    roles the way the two shipped machines do, so only the state type
    differs."""
    return {
        "schema": THE_SCHEMA_VERSION,
        "types": {"state": state_type, "event": "Event", "outcome": "Outcome"},
        "roles": {
            "init": "initial",
            "step": "step",
            "state-of": "state-of",
            "admissible": "admissible",
            "invariant": "valid-state",
        },
        "assumptions": [
            "The runtime applies one event at a time over one authoritative state."
        ],
    }


# A dimmer whose event carries a whole number: the event type has no
# bound, so no run of this tool could list its values. Its invariant
# holds after the step only because admissibility keeps the new level
# inside the dial, which is a statement about every whole number.
A_MACHINE_WHOSE_EVENTS_HAVE_NO_BOUND = """\
(deftype Level (record (at Int)))
(deftype Event (record (by Int)))
(deftype Outcome (record (state Level) (accepted Bool)))

(defn valid-state
  (sig ((current Level)) -> Bool ! pure)
  (examples
    (example (valid-state (Level 0)) => true)
    (example (valid-state (Level 10)) => true)
    (example (valid-state (Level 11)) => false))
  (and (>= (.at current) 0) (<= (.at current) 10)))

(defn initial
  (sig () -> Level ! pure)
  (examples (example (initial) => (Level 0)))
  (Level 0))

(defn admissible
  (sig ((current Level) (event Event)) -> Bool ! pure)
  (examples
    (example (admissible (Level 0) (Event 3)) => true)
    (example (admissible (Level 0) (Event 11)) => false))
  (and (>= (+ (.at current) (.by event)) 0)
       (<= (+ (.at current) (.by event)) 10)))

(defn step
  (sig ((current Level) (event Event)) -> Outcome ! pure)
  (requires (valid-state current))
  (examples (example (step (Level 0) (Event 3)) => (Outcome (Level 3) true)))
  (Outcome (Level (+ (.at current) (.by event))) true))

(defn state-of
  (sig ((produced Outcome)) -> Level ! pure)
  (examples (example (state-of (Outcome (Level 1) true)) => (Level 1)))
  (.state produced))
"""

THE_UNBOUNDED_EVENT_MACHINE = (
    A_MACHINE_WHOSE_EVENTS_HAVE_NO_BOUND,
    a_descriptor_naming("Level"),
)

# A counter whose invariant is not inductive on its own: nothing stops
# the step at the ceiling, so a counter already at it leaves the
# invariant. The weaker safety predicate a tool might substitute here --
# that the counter is nonnegative -- is true of this machine and is not
# the invariant the descriptor names.
A_MACHINE_WHOSE_INVARIANT_IS_NOT_INDUCTIVE = """\
(deftype Counter (record (n Int)))
(deftype Event (union (Bump)))
(deftype Outcome (record (state Counter) (accepted Bool)))

(defn valid-state
  (sig ((current Counter)) -> Bool ! pure)
  (examples
    (example (valid-state (Counter 0)) => true)
    (example (valid-state (Counter 11)) => false))
  (<= (.n current) 10))

(defn initial
  (sig () -> Counter ! pure)
  (examples (example (initial) => (Counter 0)))
  (Counter 0))

(defn admissible
  (sig ((current Counter) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Counter 0) (Bump)) => true))
  true)

(defn step
  (sig ((current Counter) (event Event)) -> Outcome ! pure)
  (examples (example (step (Counter 0) (Bump)) => (Outcome (Counter 1) true)))
  (Outcome (Counter (+ (.n current) 1)) true))

(defn state-of
  (sig ((produced Outcome)) -> Counter ! pure)
  (examples (example (state-of (Outcome (Counter 1) true)) => (Counter 1)))
  (.state produced))
"""

THE_MACHINE_THAT_IS_NOT_INDUCTIVE = (
    A_MACHINE_WHOSE_INVARIANT_IS_NOT_INDUCTIVE,
    a_descriptor_naming("Counter"),
)

# The weaker safety predicate this machine does satisfy, which no answer
# may put in the place of the invariant the descriptor names.
THE_WEAKER_PREDICATE_OF_THAT_MACHINE = "(>= (.n current) 0)"

# An hour clock whose initialiser starts the dial outside the invariant:
# the state it answers is not one the invariant admits, so the machine
# has no initial state to reason from. Every function of it keeps its own
# contract, so nothing but the initialisation obligation catches this.
A_MACHINE_THAT_CANNOT_START = """\
(deftype Clock (record (hr Int)))
(deftype Event (union (Tick)))
(deftype Outcome (record (state Clock) (accepted Bool)))

(defn valid-state
  (sig ((current Clock)) -> Bool ! pure)
  (examples
    (example (valid-state (Clock 1)) => true)
    (example (valid-state (Clock 0)) => false))
  (and (>= (.hr current) 1) (<= (.hr current) 12)))

(defn initial
  (sig () -> Clock ! pure)
  (examples (example (initial) => (Clock 0)))
  (Clock 0))

(defn step
  (sig ((current Clock) (event Event)) -> Outcome ! pure)
  (requires (valid-state current))
  (examples (example (step (Clock 1) (Tick)) => (Outcome (Clock 2) true)))
  (match event
    ((Tick)
      (Outcome (Clock (if (= (.hr current) 12) 1 (+ (.hr current) 1))) true))))

(defn state-of
  (sig ((produced Outcome)) -> Clock ! pure)
  (examples (example (state-of (Outcome (Clock 3) true)) => (Clock 3)))
  (.state produced))

(defn admissible
  (sig ((current Clock) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Clock 1) (Tick)) => true))
  true)
"""

THE_MACHINE_THAT_CANNOT_START = (
    A_MACHINE_THAT_CANNOT_START,
    a_descriptor_naming("Clock"),
)

# A machine whose invariant no state satisfies at all: the condition it
# states is inconsistent. Preservation is then true of it for an empty
# reason -- there is no state to step from -- so a machine certified on
# preservation alone would be certified here.
A_MACHINE_NO_STATE_SATISFIES = """\
(deftype Clock (record (hr Int)))
(deftype Event (union (Tick)))
(deftype Outcome (record (state Clock) (accepted Bool)))

(defn valid-state
  (sig ((current Clock)) -> Bool ! pure)
  (examples
    (example (valid-state (Clock 1)) => false)
    (example (valid-state (Clock 12)) => false))
  (and (>= (.hr current) 1) (<= (.hr current) 0)))

(defn initial
  (sig () -> Clock ! pure)
  (examples (example (initial) => (Clock 12)))
  (Clock 12))

(defn step
  (sig ((current Clock) (event Event)) -> Outcome ! pure)
  (examples (example (step (Clock 1) (Tick)) => (Outcome (Clock 2) true)))
  (Outcome (Clock (+ (.hr current) 1)) true))

(defn state-of
  (sig ((produced Outcome)) -> Clock ! pure)
  (examples (example (state-of (Outcome (Clock 3) true)) => (Clock 3)))
  (.state produced))

(defn admissible
  (sig ((current Clock) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Clock 1) (Tick)) => true))
  true)
"""

THE_MACHINE_NO_STATE_SATISFIES = (
    A_MACHINE_NO_STATE_SATISFIES,
    a_descriptor_naming("Clock"),
)

# The event values the machines of this feature declare. An answer that
# reasoned by listing the events would have to name them inside the
# obligations it reports.
EVENT_VALUES = ("Tick", "Reserve", "Release", "Bump")
