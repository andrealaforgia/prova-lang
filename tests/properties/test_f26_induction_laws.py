"""Laws the three inductive obligations of a machine obey for any
machine, not only the ones F26's acceptance tests send.

LAW1 a machine whose invariant is inductive is answered with all three
     obligations proved, whatever the dial it counts on: for any modulus,
     a clock that wraps at it keeps an invariant admitting 1 to that
     modulus.
LAW2 a machine whose step can leave its invariant never has preservation
     proved, whatever the ceiling: for any ceiling, a counter that adds
     one with nothing stopping it leaves an invariant admitting at most
     that ceiling.
LAW3 the obligations of a machine are three, whatever its event type
     holds: for any number of event values, the answer lists the same
     three obligations and proves them for a machine that keeps its
     invariant whatever event arrives.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova.

Derandomised with a bounded example count: each case asks the real tool,
with the pinned solver behind it, so the cases are few and fixed rather
than many and drawn.
"""

from __future__ import annotations

import json
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

INITIALISATION = "machine_initialisation"
STEP_ENABLEDNESS = "machine_step_enabledness"
PRESERVATION = "machine_preservation"
THE_THREE = (INITIALISATION, STEP_ENABLEDNESS, PRESERVATION)
PROVED = "proved"

THE_SCHEMA_VERSION = "machine-descriptor/1"


def a_descriptor_naming(state_type: str, event_type: str = "Event") -> dict:
    return {
        "schema": THE_SCHEMA_VERSION,
        "types": {"state": state_type, "event": event_type, "outcome": "Outcome"},
        "roles": {
            "init": "initial",
            "step": "step",
            "state-of": "state-of",
            "admissible": "admissible",
            "invariant": "valid-state",
        },
        "assumptions": ["One event at a time over one authoritative state."],
    }


def a_clock_wrapping_at(modulus: int) -> str:
    """A clock whose invariant admits 1 to `modulus` and whose step wraps
    there: inductive by construction, for any modulus at all."""
    return f"""\
(deftype Clock (record (hr Int)))
(deftype Event (union (Tick)))
(deftype Outcome (record (state Clock) (accepted Bool)))

(defn valid-state
  (sig ((current Clock)) -> Bool ! pure)
  (examples (example (valid-state (Clock 1)) => true))
  (and (>= (.hr current) 1) (<= (.hr current) {modulus})))

(defn initial
  (sig () -> Clock ! pure)
  (examples (example (initial) => (Clock {modulus})))
  (Clock {modulus}))

(defn step
  (sig ((current Clock) (event Event)) -> Outcome ! pure)
  (requires (valid-state current))
  (examples
    (example (step (Clock {modulus}) (Tick)) => (Outcome (Clock 1) true)))
  (match event
    ((Tick)
      (Outcome
        (Clock (if (= (.hr current) {modulus}) 1 (+ (.hr current) 1)))
        true))))

(defn state-of
  (sig ((produced Outcome)) -> Clock ! pure)
  (examples (example (state-of (Outcome (Clock 1) true)) => (Clock 1)))
  (.state produced))

(defn admissible
  (sig ((current Clock) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Clock 1) (Tick)) => true))
  true)
"""


def a_counter_rising_past(ceiling: int) -> str:
    """A counter whose invariant admits at most `ceiling` and whose step
    adds one with nothing stopping it: not inductive, for any ceiling."""
    return f"""\
(deftype Counter (record (n Int)))
(deftype Event (union (Bump)))
(deftype Outcome (record (state Counter) (accepted Bool)))

(defn valid-state
  (sig ((current Counter)) -> Bool ! pure)
  (examples (example (valid-state (Counter 0)) => true))
  (<= (.n current) {ceiling}))

(defn initial
  (sig () -> Counter ! pure)
  (examples (example (initial) => (Counter 0)))
  (Counter 0))

(defn step
  (sig ((current Counter) (event Event)) -> Outcome ! pure)
  (examples (example (step (Counter 0) (Bump)) => (Outcome (Counter 1) true)))
  (Outcome (Counter (+ (.n current) 1)) true))

(defn state-of
  (sig ((produced Outcome)) -> Counter ! pure)
  (examples (example (state-of (Outcome (Counter 1) true)) => (Counter 1)))
  (.state produced))

(defn admissible
  (sig ((current Counter) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Counter 0) (Bump)) => true))
  true)
"""


def a_machine_with_event_values(how_many: int) -> str:
    """A machine whose event type holds `how_many` values and whose step
    keeps the state whatever event arrives."""
    variants = " ".join(f"(E{place})" for place in range(how_many))
    return f"""\
(deftype Held (record (n Int)))
(deftype Event (union {variants}))
(deftype Outcome (record (state Held) (accepted Bool)))

(defn valid-state
  (sig ((current Held)) -> Bool ! pure)
  (examples (example (valid-state (Held 0)) => true))
  (>= (.n current) 0))

(defn initial
  (sig () -> Held ! pure)
  (examples (example (initial) => (Held 0)))
  (Held 0))

(defn step
  (sig ((current Held) (event Event)) -> Outcome ! pure)
  (examples (example (step (Held 0) (E0)) => (Outcome (Held 0) true)))
  (Outcome current true))

(defn state-of
  (sig ((produced Outcome)) -> Held ! pure)
  (examples (example (state-of (Outcome (Held 1) true)) => (Held 1)))
  (.state produced))

(defn admissible
  (sig ((current Held) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Held 0) (E0)) => true))
  true)
"""


def how_the_three_stand(source: str, descriptor: dict) -> dict:
    answer = ask({"operation": "verify", "source": source, "descriptor": descriptor})
    assert answer.get("status") == "completed", (
        f"the tool answered {answer.get('status')!r} for a program it is "
        f"promised to verify: {answer}"
    )
    listed = (((answer.get("result") or {}).get("inventory")) or {}).get(
        "obligations"
    ) or []
    return {
        entry.get("kind"): entry.get("result")
        for entry in listed
        if entry.get("kind") in THE_THREE
    }


def ask(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=30.0,
    )
    assert proc.returncode == 0, (
        f"the tool exited {proc.returncode} rather than answering: "
        f"{proc.stderr[-800:]!r}"
    )
    return json.loads(proc.stdout)


@given(modulus=st.integers(min_value=2, max_value=24))
@settings(max_examples=6, deadline=None, derandomize=True)
def test_an_inductive_invariant_is_proved_whatever_the_dial(modulus):
    """LAW1 -- a clock that wraps at its modulus keeps an invariant
    admitting 1 to that modulus, and all three obligations are proved."""
    standing = how_the_three_stand(
        a_clock_wrapping_at(modulus), a_descriptor_naming("Clock")
    )

    assert standing == {kind: PROVED for kind in THE_THREE}, (
        f"WHAT: a clock wrapping at {modulus} stands as {standing}. "
        "WHY: it starts inside its invariant, its step is defined wherever "
        "the invariant holds, and wrapping keeps the dial between 1 and the "
        f"modulus; LAW1 says all three are proved. "
        f"HOW: read the entries for the clock of modulus {modulus}."
    )


@given(ceiling=st.integers(min_value=0, max_value=40))
@settings(max_examples=6, deadline=None, derandomize=True)
def test_a_step_that_can_leave_the_invariant_is_never_proved_preserved(ceiling):
    """LAW2 -- a counter that adds one with nothing stopping it leaves an
    invariant admitting at most its ceiling, so preservation is never
    proved."""
    standing = how_the_three_stand(
        a_counter_rising_past(ceiling), a_descriptor_naming("Counter")
    )

    assert standing.get(PRESERVATION) != PROVED, (
        f"WHAT: a counter whose invariant admits at most {ceiling} and whose "
        f"step adds one stands as {standing}. "
        "WHY: the state after one step from the ceiling does not satisfy the "
        "invariant, so LAW2 says preservation is not proved for any ceiling. "
        f"HOW: read the preservation entry for the ceiling {ceiling}."
    )
    assert standing.get(INITIALISATION) == PROVED, (
        f"WHAT: the same counter's initialisation stands as "
        f"{standing.get(INITIALISATION)!r}. "
        "WHY: it starts at 0, which the invariant admits for every ceiling "
        "at or above 0; one obligation withheld must not withhold another. "
        "HOW: settle each of the three on its own."
    )


@given(how_many=st.integers(min_value=1, max_value=5))
@settings(max_examples=5, deadline=None, derandomize=True)
def test_the_obligations_are_three_whatever_the_event_type_holds(how_many):
    """LAW3 -- a machine that keeps its invariant whatever event arrives
    is answered with the same three obligations, whether its event type
    holds one value or five."""
    standing = how_the_three_stand(
        a_machine_with_event_values(how_many), a_descriptor_naming("Held")
    )

    assert standing == {kind: PROVED for kind in THE_THREE}, (
        f"WHAT: a machine with {how_many} event values stands as {standing}. "
        "WHY: LAW3 says the three obligations are stated over the typed "
        "event and not over its values, so their number and their result do "
        "not follow how many values the type holds (SPEC.md lines 384-386). "
        f"HOW: read the entries for the machine with {how_many} event values."
    )
