"""Shared fixtures for F28's acceptance tests: the three deliberately
broken copies of the reservation component SPEC.md's conformance section
names, the three attempts to pass by changing a requirement, and the
small readers that pick the new parts of a verify answer out.

Not itself a test module; imported by the F28 acceptance tests and by
F28's property tests.

Every broken source below is derived from the reservation machine this
repository ships (`examples/reservation.machine.prova`) by replacing one
named piece of its text, and every replacement asserts that it found
exactly one occurrence: a fixture that silently changed nothing, or
changed two places, would make the tests below say nothing.

Drives only the installed `prova` command over its JSON stdin/stdout
surface, through the F25 fixtures that already own that one call. No
imports from src/prova: the promises below are about what an Owner reads
from the tool.
"""

from __future__ import annotations

import copy
import json

import _f25_machine_fixtures as machines
import _f26_induction_fixtures as induction

MACHINES = machines.MACHINES
THE_SCHEMA_VERSION = machines.THE_SCHEMA_VERSION

INITIALISATION = induction.INITIALISATION
STEP_ENABLEDNESS = induction.STEP_ENABLEDNESS
PRESERVATION = induction.PRESERVATION
THE_THREE = induction.THE_THREE

PROVED = induction.PROVED
DISPROVED = "disproved"
UNKNOWN = "unknown"
VERIFIED = induction.VERIFIED
NOT_VERIFIED = induction.NOT_VERIFIED

# The two kinds of evidence SPEC.md lines 307-311 keep apart, as an
# answer names them, and the one it reserves for a validated initial
# state with a sequence of transitions.
AN_INDUCTION_STEP_WITNESS = "induction_step_witness"
A_REACHABLE_COUNTEREXAMPLE = "reachable_counterexample"

# Where the new parts of an answer about a machine stand.
THE_REACHABLE_FIELD = "reachable_counterexample"
THE_CONTRACTS_FIELD = "contracts_the_proofs_rest_on"
THE_DIGEST_FIELD = "digest"

# Where the tool publishes the kinds of evidence it emits and what it
# says about a proof taken over a contract that changed.
THE_PUBLISHED_KINDS = "witness_kinds"
THE_PUBLISHED_INTEGRITY = "requirement_integrity"


def ask_to_verify(source: str, descriptor: object = None) -> dict:
    return induction.ask_to_verify(source, descriptor)


def ask_for_the_manifest() -> dict:
    return machines.ask_for_the_manifest()


def ask_to_evaluate(source: str, function: str, arguments: list) -> dict:
    """What the tool answers when it is asked to run `function` of
    `source` over `arguments`, as the Owner replays a witness by hand."""
    return machines.run(
        {
            "operation": "evaluate",
            "source": source,
            "function": function,
            "arguments": list(arguments),
        }
    )


# --- reading a verify answer ------------------------------------------------

the_three_obligations = induction.the_three_obligations
how_the_three_stand = induction.how_the_three_stand
machine_block_of = induction.machine_block_of
aggregate_of = induction.aggregate_of
listed_obligations = induction.listed_obligations
text_of = induction.text_of


def shipped_reservation() -> tuple[str, dict]:
    return machines.shipped_machine("reservation")


def shipped_machine(machine: str) -> tuple[str, dict]:
    return machines.shipped_machine(machine)


def the_witness_of(entry: dict) -> dict:
    return entry.get("counterexample") or {}


def disproved_obligations(answer: dict) -> list:
    """Every obligation of the answer that stands as disproved."""
    return [
        entry
        for entry in listed_obligations(answer)
        if entry.get("result") == DISPROVED
    ]


def reachable_counterexample_of(answer: dict) -> dict | None:
    """What the answer carries as a reachable counterexample, or nothing
    at all when it carries none."""
    return machine_block_of(answer).get(THE_REACHABLE_FIELD)


def contracts_digest_of(answer: dict) -> str | None:
    rested_on = machine_block_of(answer).get(THE_CONTRACTS_FIELD) or {}
    return rested_on.get(THE_DIGEST_FIELD)


def published_witness_kinds() -> dict:
    result = ask_for_the_manifest().get("result") or {}
    return result.get(THE_PUBLISHED_KINDS) or {}


def published_requirement_integrity() -> dict:
    result = ask_for_the_manifest().get("result") or {}
    return result.get(THE_PUBLISHED_INTEGRITY) or {}


def every_kind_named_in(answer: dict) -> set:
    """Every value the answer carries under a 'kind' key that names one
    of the two kinds of witness evidence."""
    named = set()

    def walk(value: object) -> None:
        if isinstance(value, dict):
            spelled = value.get("kind")
            if spelled in (AN_INDUCTION_STEP_WITNESS, A_REACHABLE_COUNTEREXAMPLE):
                named.add(spelled)
            for inside in value.values():
                walk(inside)
        elif isinstance(value, list):
            for inside in value:
                walk(inside)

    walk(answer)
    return named


# --- the three deliberate faults of the reservation component --------------


def _replacing(source: str, old: str, new: str, what: str) -> str:
    found = source.count(old)
    assert found == 1, (
        f"WHAT: the text this fixture replaces to make {what} stands "
        f"{found} times in the shipped reservation machine, not once. "
        "WHY: a fixture that changed nothing, or changed two places, would "
        "make the test that reads it say nothing about the fault it names. "
        "HOW: read examples/reservation.machine.prova and write the piece "
        "below as it stands there."
    )
    return source.replace(old, new, 1)


# The Reserve branch of the step as the shipped reservation writes it:
# the upper capacity guard, the increment it protects and the rejection
# it falls back to.
THE_GUARDED_RESERVE_BRANCH = (
    "      (if (< (.reserved current) 2)\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) true)\n"
    "          (Outcome current false)))"
)

# The same branch with no guard at all: every reserve increments.
THE_UNGUARDED_RESERVE_BRANCH = (
    "      (Outcome (Reservation (+ (.reserved current) 1)) true))"
)

# The same branch with the acceptance flag of both its answers flipped,
# and the state arithmetic left exactly as it was: the reservation count
# still stays inside the invariant, and what the component tells the
# caller is now the opposite of what its contract promises.
THE_FLIPPED_RESERVE_BRANCH = (
    "      (if (< (.reserved current) 2)\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) false)\n"
    "          (Outcome current true)))"
)

# The whole body of the step as the shipped reservation writes it.
THE_WHOLE_STEP_BODY = (
    "  (match event\n"
    "    ((Reserve)\n"
    "      (if (< (.reserved current) 2)\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) true)\n"
    "          (Outcome current false)))\n"
    "    ((Release)\n"
    "      (if (> (.reserved current) 0)\n"
    "          (Outcome (Reservation (- (.reserved current) 1)) true)\n"
    "          (Outcome current false)))))"
)

# A body that rejects every event it is given, whatever the state.
THE_ALWAYS_REJECTING_BODY = "  (Outcome current false))"

# The one declared example of the step that visits a full reservation.
# SPEC.md lines 580-587 ask for the missing guard to be detected despite
# examples visiting only non-full states, so the source that drops the
# guard drops this example too: with it in place the fault is caught by
# running an example, which is the claim about three inputs this feature
# replaces.
THE_EXAMPLE_AT_A_FULL_RESERVATION = (
    "    (example (step (Reservation 2) (Reserve)) => (Outcome (Reservation 2) false))\n"
)

# What the step promises about the state it answers, and about what it
# tells the caller.
THE_GUARANTEE_ABOUT_THE_STATE = "    (valid-state (.state result))\n"
THE_PRECONDITION_OF_THE_STEP = "  (requires (valid-state current))\n"
A_STRONGER_PRECONDITION_OF_THE_STEP = (
    "  (requires (valid-state current) (= (.reserved current) 0))\n"
)


def without_the_upper_guard() -> tuple[str, dict]:
    """The reservation component with the upper capacity guard removed
    from the step's body, and with the one example that visits a full
    reservation removed as well, so that no example of it visits a state
    the missing guard would have protected."""
    source, descriptor = shipped_reservation()
    source = _replacing(
        source,
        THE_GUARDED_RESERVE_BRANCH,
        THE_UNGUARDED_RESERVE_BRANCH,
        "the source with no upper capacity guard",
    )
    source = _replacing(
        source,
        THE_EXAMPLE_AT_A_FULL_RESERVATION,
        "",
        "a source no example of which visits a full reservation",
    )
    return source, descriptor


def with_the_acceptance_flag_flipped() -> tuple[str, dict]:
    """The reservation component with the acceptance flag of both
    answers of its Reserve branch flipped and its state arithmetic
    untouched."""
    source, descriptor = shipped_reservation()
    return (
        _replacing(
            source,
            THE_GUARDED_RESERVE_BRANCH,
            THE_FLIPPED_RESERVE_BRANCH,
            "the source whose acceptance flag is flipped",
        ),
        descriptor,
    )


def that_always_rejects() -> tuple[str, dict]:
    """The reservation component whose step rejects every event in every
    state and leaves the reservation count where it was."""
    source, descriptor = shipped_reservation()
    return (
        _replacing(
            source,
            THE_WHOLE_STEP_BODY,
            THE_ALWAYS_REJECTING_BODY,
            "the source that always rejects",
        ),
        descriptor,
    )


THE_THREE_FAULTS = (
    ("the upper capacity guard removed", without_the_upper_guard),
    ("the acceptance flag flipped", with_the_acceptance_flag_flipped),
    ("a body that always rejects", that_always_rejects),
)

# The three faults whose edit is to a body alone: neither of these
# touches a signature, a precondition, a guarantee or a declared
# example, so neither is a requirement change.
THE_FAULTS_OF_A_BODY_ALONE = (
    ("the acceptance flag flipped", with_the_acceptance_flag_flipped),
    ("a body that always rejects", that_always_rejects),
)


# --- the three attempts to pass by changing a requirement ------------------


def with_a_weakened_guarantee() -> tuple[str, dict]:
    """The reservation component with the step's guarantee about the
    state it answers deleted: the invariant is no longer promised of the
    result."""
    source, descriptor = shipped_reservation()
    return (
        _replacing(
            source,
            THE_GUARANTEE_ABOUT_THE_STATE,
            "",
            "a source whose guarantee about the state was weakened",
        ),
        descriptor,
    )


def with_a_strengthened_precondition() -> tuple[str, dict]:
    """The reservation component whose step now asks for an empty
    reservation as well as a valid one: a precondition that removes
    transitions the component owed."""
    source, descriptor = shipped_reservation()
    return (
        _replacing(
            source,
            THE_PRECONDITION_OF_THE_STEP,
            A_STRONGER_PRECONDITION_OF_THE_STEP,
            "a source whose precondition was strengthened",
        ),
        descriptor,
    )


def with_an_example_deleted() -> tuple[str, dict]:
    """The reservation component with the declared example that visits a
    full reservation deleted."""
    source, descriptor = shipped_reservation()
    return (
        _replacing(
            source,
            THE_EXAMPLE_AT_A_FULL_RESERVATION,
            "",
            "a source with a declared example deleted",
        ),
        descriptor,
    )


THE_THREE_ATTEMPTS = (
    ("a guarantee weakened", with_a_weakened_guarantee),
    ("a precondition strengthened", with_a_strengthened_precondition),
    ("an example deleted", with_an_example_deleted),
)


# --- a family of machines whose step has no guard at all -------------------


def a_counter_whose_step_has_no_guard(ceiling: int, by: int) -> tuple[str, dict]:
    """A counter whose invariant is that it stays at or below `ceiling`
    and whose step adds `by` whatever the state: an invariant that is not
    inductive, with no example anywhere near the ceiling.

    Written here so a property can generate the family and read the same
    answer shape the three faults above are read through.
    """
    source = f"""\
(deftype Counter (record (n Int)))
(deftype Event (union (Bump)))
(deftype Outcome (record (state Counter) (accepted Bool)))

(defn valid-state
  (sig ((current Counter)) -> Bool ! pure)
  (examples
    (example (valid-state (Counter 0)) => true)
    (example (valid-state (Counter {ceiling + by})) => false))
  (<= (.n current) {ceiling}))

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
  (examples (example (step (Counter 0) (Bump)) => (Outcome (Counter {by}) true)))
  (Outcome (Counter (+ (.n current) {by})) true))

(defn state-of
  (sig ((produced Outcome)) -> Counter ! pure)
  (examples (example (state-of (Outcome (Counter {by}) true)) => (Counter {by})))
  (.state produced))
"""
    return source, induction.a_descriptor_naming("Counter")


def a_descriptor_naming(state_type: str) -> dict:
    return induction.a_descriptor_naming(state_type)


def copied(value: object) -> object:
    return copy.deepcopy(value)


def as_text(value: object) -> str:
    return json.dumps(value, sort_keys=True)
