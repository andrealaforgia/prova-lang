"""Driving a machine is measured against the operation-time budget after
its last event as well as before each one.

The budget was read once before every event and never again, so the
transition that followed the last reading was free: a run whose single
event spent many times the time the caller allowed answered `completed`,
and the same run sent two identical events refused at the second
boundary and reported an elapsed time far past the budget -- the time
the first transition had already spent unmeasured.

Every case drives the real command with the budget lowered the way the
manifest publishes, and pairs the refusal with the same machine inside
the declared budget, which must still be driven and answered.
"""

from __future__ import annotations

from _f14_budget_fixtures import (
    ACTUAL,
    CATEGORY_OF,
    EXPECTED,
    OPERATION_TIME,
    RESOURCE_EXHAUSTED,
    SEMANTIC_KEYS,
    variable_for,
)
from _f27_runtime_fixtures import (
    A_TRANSITION,
    drive,
    machine_descriptor,
    machine_source,
    transitions_of,
)


def hour_clock_machine_source() -> str:
    return machine_source("hour-clock")


def hour_clock_machine_descriptor() -> dict:
    return machine_descriptor("hour-clock")

# A clock whose one transition costs real time: the step doubles a
# number through a chain of helpers, each of which calls the one below
# it twice, so the work of one transition is 2^LEVELS additions. The
# chain is ordinary core-0 -- no recursion, every call acyclic -- and
# nothing but its cost matters here.
LEVELS = 20

A = "=>"


def _burning_helpers(levels: int) -> str:
    written = [
        "(defn burn-0\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        f"  (examples (example (burn-0 1) {A} 2))\n"
        "  (+ n n))"
    ]
    for level in range(1, levels + 1):
        written.append(
            f"(defn burn-{level}\n"
            "  (sig ((n Int)) -> Int ! pure)\n"
            f"  (examples (example (burn-{level} 0) {A} 0))\n"
            f"  (+ (burn-{level - 1} n) (burn-{level - 1} n)))"
        )
    return "\n".join(written)


A_COSTLY_CLOCK_SOURCE = f"""(deftype Clock (record (hr Int)))
(deftype Event (union (Tick)))
(deftype Outcome (record (state Clock) (accepted Bool)))

{_burning_helpers(LEVELS)}

(defn valid-state
  (sig ((current Clock)) -> Bool ! pure)
  (examples (example (valid-state (Clock 0)) {A} true))
  (>= (.hr current) 0))

(defn initial
  (sig () -> Clock ! pure)
  (examples (example (initial) {A} (Clock 0)))
  (Clock 0))

(defn state-of
  (sig ((produced Outcome)) -> Clock ! pure)
  (examples (example (state-of (Outcome (Clock 0) true)) {A} (Clock 0)))
  (.state produced))

(defn admissible
  (sig ((current Clock) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Clock 0) (Tick)) {A} true))
  true)

(defn step
  (sig ((current Clock) (event Event)) -> Outcome ! pure)
  (requires (valid-state current))
  (examples (example (step (Clock 0) (Tick)) {A} (Outcome (Clock 1) true)))
  (match event
    ((Tick)
      (Outcome
        (Clock (+ (.hr current) (if (= (burn-{LEVELS} (.hr current)) 0) 1 1)))
        true))))
"""

A_COSTLY_CLOCK_DESCRIPTOR = {
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

# A budget a reading of the clock alone stays inside and one transition
# of this machine does not: the request is read and the program checked
# in a few milliseconds, and the transition costs seconds.
A_SECOND = {variable_for(OPERATION_TIME): "1000"}

A_CLOCK_AT_ZERO = "(Clock 0)"


def _driven(events: list[str], lowering: dict | None = None) -> dict:
    return drive(
        A_COSTLY_CLOCK_SOURCE,
        A_COSTLY_CLOCK_DESCRIPTOR,
        A_CLOCK_AT_ZERO,
        events,
        lowering,
    )


def test_a_single_transition_past_the_budget_is_refused_not_answered():
    answer = _driven(["(Tick)"], A_SECOND)

    assert answer["status"] == RESOURCE_EXHAUSTED, answer
    refusal = answer["diagnostics"][0]
    assert refusal["category"] == CATEGORY_OF[OPERATION_TIME], refusal
    assert refusal[EXPECTED] == 1000, refusal
    assert refusal[ACTUAL] > 1000, refusal
    for key in SEMANTIC_KEYS:
        assert key not in answer, (key, answer)


def test_a_machine_that_stays_inside_the_same_lowered_budget_is_driven():
    """The refusal above is about the time the transition spent, not
    about the lowered budget on its own: the clock this repository ships
    is driven through the same lowered budget and answered."""
    answer = drive(
        hour_clock_machine_source(),
        hour_clock_machine_descriptor(),
        "(Clock 12)",
        ["(Tick)"],
        A_SECOND,
    )

    assert answer["status"] == "completed", answer
    assert transitions_of(answer)[0]["state_after"] == "(Clock 1)", answer


def test_the_same_machine_inside_the_declared_budget_is_still_driven():
    answer = _driven(["(Tick)"])

    assert answer["status"] == "completed", answer
    transitions = transitions_of(answer)
    assert len(transitions) == 1, answer
    assert transitions[0]["result"] == A_TRANSITION, transitions
    assert transitions[0]["state_after"] == "(Clock 1)", transitions
