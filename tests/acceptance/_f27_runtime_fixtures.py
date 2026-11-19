"""Shared fixtures for F27's acceptance tests: the machines this
repository ships, two machines written here to reach the cases the
shipped ones cannot, and the request the Owner sends to drive a machine
event by event.

Not itself a test module; imported by the F27 acceptance tests.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova: the promises below are about what an
Owner reads from the tool.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"

# The operation the Owner drives a machine with, and the four fields the
# request carries.
THE_OPERATION = "step"

MACHINES = ("hour-clock", "reservation")

# The words one attempted transition is published under, and the two
# words that say why a sequence stopped early.
A_TRANSITION = "transition"
A_BOUNDARY_REJECTION = "boundary_rejection"
A_STATE_OUTSIDE_THE_INVARIANT = "state_outside_invariant"


def machine_source(machine: str) -> str:
    return _read(EXAMPLES / f"{machine}.machine.prova")


def machine_descriptor(machine: str) -> dict:
    return json.loads(_read(EXAMPLES / f"{machine}.machine.json"))


def shipped_machine(machine: str) -> tuple[str, dict]:
    return machine_source(machine), machine_descriptor(machine)


# --- the two machines written here -----------------------------------------
#
# The shipped machines admit every typed event, so neither of them can
# show a boundary rejection. The first machine below is the shipped
# reservation with one function changed: its admissibility predicate
# answers what the component's own guards answer, so a reserve at the
# capacity and a release at zero are outside the admissible domain
# instead of being admitted and rejected by the business rule.

THE_SHIPPED_ADMISSIBILITY = """(defn admissible
  (sig ((current Reservation) (event Event)) -> Bool ! pure)
  (examples
    (example (admissible (Reservation 0) (Reserve)) => true)
    (example (admissible (Reservation 2) (Release)) => true))
  true)"""

A_NARROWER_ADMISSIBILITY = """(defn admissible
  (sig ((current Reservation) (event Event)) -> Bool ! pure)
  (examples
    (example (admissible (Reservation 0) (Reserve)) => true)
    (example (admissible (Reservation 2) (Reserve)) => false))
  (match event
    ((Reserve) (< (.reserved current) 2))
    ((Release) (> (.reserved current) 0))))"""


def reservation_that_admits_less() -> tuple[str, dict]:
    """The shipped reservation machine with one function changed: the
    events it admits are the ones its own guards accept."""
    shipped = machine_source("reservation")
    assert THE_SHIPPED_ADMISSIBILITY in shipped, (
        "WHAT: examples/reservation.machine.prova no longer declares the "
        "admissibility predicate these tests narrow. "
        "WHY: the boundary rejection is shown on the shipped reservation "
        "with one function replaced, so that the machine the Owner reads "
        "about is the shipped one. "
        "HOW: update A_NARROWER_ADMISSIBILITY in this file against the "
        "shipped program."
    )
    return (
        shipped.replace(THE_SHIPPED_ADMISSIBILITY, A_NARROWER_ADMISSIBILITY),
        machine_descriptor("reservation"),
    )


# A clock whose step adds an hour without ever wrapping, so the state it
# publishes at twelve o'clock is outside the invariant its own descriptor
# names. Written here and shipped nowhere: it is a machine the Owner may
# well write, and the runtime must stop at it rather than drive a
# transition from a state the machine is not defined at.
A_CLOCK_THAT_LEAVES_ITS_INVARIANT_SOURCE = """(deftype Clock (record (hr Int)))
(deftype Event (union (Tick)))
(deftype Outcome (record (state Clock) (accepted Bool)))

(defn valid-state
  (sig ((current Clock)) -> Bool ! pure)
  (examples
    (example (valid-state (Clock 1)) => true)
    (example (valid-state (Clock 13)) => false))
  (and (>= (.hr current) 1) (<= (.hr current) 12)))

(defn initial
  (sig () -> Clock ! pure)
  (examples (example (initial) => (Clock 1)))
  (Clock 1))

(defn step
  (sig ((current Clock) (event Event)) -> Outcome ! pure)
  (examples
    (example (step (Clock 1) (Tick)) => (Outcome (Clock 2) true))
    (example (step (Clock 12) (Tick)) => (Outcome (Clock 13) true)))
  (match event
    ((Tick) (Outcome (Clock (+ (.hr current) 1)) true))))

(defn state-of
  (sig ((produced Outcome)) -> Clock ! pure)
  (examples (example (state-of (Outcome (Clock 3) true)) => (Clock 3)))
  (.state produced))

(defn admissible
  (sig ((current Clock) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Clock 1) (Tick)) => true))
  true)
"""

A_CLOCK_DESCRIPTOR = {
    "schema": "machine-descriptor/1",
    "types": {"state": "Clock", "event": "Event", "outcome": "Outcome"},
    "roles": {
        "init": "initial",
        "step": "step",
        "state-of": "state-of",
        "admissible": "admissible",
        "invariant": "valid-state",
    },
    "assumptions": ["One tick at a time over one authoritative clock state."],
}


def clock_that_leaves_its_invariant() -> tuple[str, dict]:
    return A_CLOCK_THAT_LEAVES_ITS_INVARIANT_SOURCE, dict(A_CLOCK_DESCRIPTOR)


# A clock whose invariant is weaker than what its step asks for: the
# invariant admits any hour from 1 upwards, and the step requires an hour
# between 1 and 12. SPEC.md lines 360-361 let the step require an
# invariant state, and nothing makes a descriptor name an invariant
# strong enough for it, so the second tick from 12 o'clock reaches a
# contract the values do not satisfy. Written here and shipped nowhere.
A_CLOCK_WHOSE_STEP_ASKS_FOR_MORE_SOURCE = """(deftype Clock (record (hr Int)))
(deftype Event (union (Tick)))
(deftype Outcome (record (state Clock) (accepted Bool)))

(defn one-or-more
  (sig ((current Clock)) -> Bool ! pure)
  (examples
    (example (one-or-more (Clock 1)) => true)
    (example (one-or-more (Clock 13)) => true)
    (example (one-or-more (Clock 0)) => false))
  (>= (.hr current) 1))

(defn on-the-dial
  (sig ((current Clock)) -> Bool ! pure)
  (examples
    (example (on-the-dial (Clock 12)) => true)
    (example (on-the-dial (Clock 13)) => false))
  (and (>= (.hr current) 1) (<= (.hr current) 12)))

(defn initial
  (sig () -> Clock ! pure)
  (examples (example (initial) => (Clock 1)))
  (Clock 1))

(defn step
  (sig ((current Clock) (event Event)) -> Outcome ! pure)
  (requires (on-the-dial current))
  (examples
    (example (step (Clock 1) (Tick)) => (Outcome (Clock 2) true))
    (example (step (Clock 12) (Tick)) => (Outcome (Clock 13) true)))
  (match event
    ((Tick) (Outcome (Clock (+ (.hr current) 1)) true))))

(defn state-of
  (sig ((produced Outcome)) -> Clock ! pure)
  (examples (example (state-of (Outcome (Clock 3) true)) => (Clock 3)))
  (.state produced))

(defn admissible
  (sig ((current Clock) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Clock 1) (Tick)) => true))
  true)
"""


def clock_whose_step_asks_for_more() -> tuple[str, dict]:
    """A machine whose step requires more than its invariant promises, so
    a run reaches a contract the values do not satisfy."""
    descriptor = dict(A_CLOCK_DESCRIPTOR)
    descriptor["roles"] = dict(descriptor["roles"], invariant="one-or-more")
    return A_CLOCK_WHOSE_STEP_ASKS_FOR_MORE_SOURCE, descriptor


# --- the six rows SPEC.md's reservation table defines -----------------------


def the_spec_table() -> tuple[tuple[int, str, int, str], ...]:
    """The transition table SPEC.md writes for its reservation example:
    the state before, the event, the state after and the acceptance
    result, as the Owner reads them in the document."""
    text = _read(REPO_ROOT / "SPEC.md")
    heading = "| Before | Event | After | Accepted |"
    assert heading in text, (
        "WHAT: SPEC.md no longer writes the reservation transition table. "
        "WHY: the Owner is promised that the six rows of that table run "
        "through the runtime and match it exactly, so the table is read "
        "from the document rather than copied here. "
        "HOW: read SPEC.md around the core conformance example."
    )
    rows: list[tuple[int, str, int, str]] = []
    for line in text[text.index(heading) :].splitlines()[2:]:
        if not line.startswith("|"):
            break
        before, event, after, accepted = (
            cell.strip() for cell in line.strip("|").split("|")
        )
        rows.append((int(before), event, int(after), accepted))
    return tuple(rows)


# --- the request and the answer --------------------------------------------


def drive(source: str, descriptor: object, state: object, events: object) -> dict:
    """What the tool answers when the Owner drives `source` from `state`
    through `events`."""
    return run(
        {
            "operation": THE_OPERATION,
            "source": source,
            "descriptor": descriptor,
            "state": state,
            "events": events,
        }
    )


def ask_for_the_manifest() -> dict:
    return run({"operation": "discover"})


def run(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=30.0,
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


def result_of(answer: dict) -> dict:
    return answer.get("result") or {}


def transitions_of(answer: dict) -> list:
    return result_of(answer).get("transitions") or []


def state_now_of(answer: dict) -> object:
    return result_of(answer).get("state_now")


def stopped_at_of(answer: dict) -> object:
    return result_of(answer).get("stopped_at")


def diagnostics_of(answer: dict) -> list:
    return answer.get("diagnostics") or []


def categories_of(answer: dict) -> list:
    return [diagnostic.get("category") for diagnostic in diagnostics_of(answer)]


def fields_the_refusal_names(answer: dict) -> list:
    return [
        diagnostic.get("symbol")
        for diagnostic in diagnostics_of(answer)
        if diagnostic.get("symbol") is not None
    ]


def roles_the_refusal_names(answer: dict) -> list:
    return [
        diagnostic.get("role")
        for diagnostic in diagnostics_of(answer)
        if diagnostic.get("role") is not None
    ]


def _read(path: pathlib.Path) -> str:
    assert path.exists(), (
        f"WHAT: {path} is not in this tree. "
        "WHY: the Owner drives the machines this repository ships, so the "
        "program and the descriptor must be there to send. "
        f"HOW: ship {path}."
    )
    return path.read_text(encoding="utf-8")
