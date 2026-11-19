"""The machines the F28 repair is about: a reservation whose step calls a
helper, the edits that change what a helper or a type requires, a machine
whose evidence is longer than this tool writes, and one whose initialiser
starts outside its own invariant.

Not itself a test module; imported by the F28 repair tests.

Drives only the installed `prova` command over its JSON stdin/stdout
surface, through the F28 fixtures that already own that one call. No
imports from src/prova.
"""

from __future__ import annotations

import _f28_broken_guard_fixtures as broken

ask_to_verify = broken.ask_to_verify
ask_to_evaluate = broken.ask_to_evaluate
machine_block_of = broken.machine_block_of
aggregate_of = broken.aggregate_of
the_three_obligations = broken.the_three_obligations
how_the_three_stand = broken.how_the_three_stand
contracts_digest_of = broken.contracts_digest_of
reachable_counterexample_of = broken.reachable_counterexample_of
the_witness_of = broken.the_witness_of
as_text = broken.as_text
a_descriptor_naming = broken.a_descriptor_naming

PRESERVATION = broken.PRESERVATION
DISPROVED = broken.DISPROVED
UNKNOWN = broken.UNKNOWN
PROVED = broken.PROVED
VERIFIED = broken.VERIFIED
NOT_VERIFIED = broken.NOT_VERIFIED

# Where a machine answer says it established something it will not write.
THE_UNWRITTEN_FIELD = "evidence_not_written"

# The longest integer this tool writes into an answer, as the manifest
# publishes it: the fixture below has to compute a longer one, and a
# fixture that hard-coded the number would stop proving anything the day
# the limit moved.
def the_digits_an_answer_writes() -> int:
    result = broken.ask_for_the_manifest().get("result") or {}
    limits = result.get("resource_limits") or {}
    for named, says in limits.items():
        if "digit" in named and isinstance(says, dict):
            for key, value in says.items():
                if isinstance(value, int) and value > 0:
                    return value
    return 4000


# --- a reservation whose step calls a helper ------------------------------

A_RESERVATION_WHOSE_STEP_CALLS_A_HELPER = """\
(deftype Reservation (record (reserved Int)))
(deftype Event (union (Reserve) (Release)))
(deftype Outcome (record (state Reservation) (accepted Bool)))

(defn valid-state
  (sig ((current Reservation)) -> Bool ! pure)
  (examples
    (example (valid-state (Reservation 0)) => true)
    (example (valid-state (Reservation 3)) => false))
  (and (>= (.reserved current) 0) (<= (.reserved current) 2)))

(defn initial
  (sig () -> Reservation ! pure)
  (examples (example (initial) => (Reservation 0)))
  (Reservation 0))

(defn increment
  (sig ((n Int)) -> Int ! pure)
  (ensures (= result (+ n 2)))
  (examples (example (increment 0) => 1))
  (+ n 1))

(defn step
  (sig ((current Reservation) (event Event)) -> Outcome ! pure)
  (requires (valid-state current))
  (ensures (valid-state (.state result)))
  (examples
    (example (step (Reservation 0) (Reserve)) => (Outcome (Reservation 1) true))
    (example (step (Reservation 1) (Release)) => (Outcome (Reservation 0) true)))
  (match event
    ((Reserve)
      (if (< (.reserved current) 2)
          (Outcome (Reservation (increment (.reserved current))) true)
          (Outcome current false)))
    ((Release)
      (if (> (.reserved current) 0)
          (Outcome (Reservation (- (.reserved current) 1)) true)
          (Outcome current false)))))

(defn state-of
  (sig ((produced Outcome)) -> Reservation ! pure)
  (examples (example (state-of (Outcome (Reservation 1) true)) => (Reservation 1)))
  (.state produced))

(defn admissible
  (sig ((current Reservation) (event Event)) -> Bool ! pure)
  (examples
    (example (admissible (Reservation 0) (Reserve)) => true)
    (example (admissible (Reservation 2) (Release)) => true))
  true)
"""

# The helper's broken guarantee, its failing example, the event type and
# one body, each as the source writes it.
THE_HELPERS_GUARANTEE = "  (ensures (= result (+ n 2)))\n"
THE_HELPERS_EXAMPLE = "  (examples (example (increment 0) => 1))\n"
THE_HELPERS_EXAMPLE_REPLACED = "  (examples (example (increment 5) => 6))\n"
THE_EVENT_TYPE = "(deftype Event (union (Reserve) (Release)))"
THE_EVENT_TYPE_WIDENED = "(deftype Event (union (Reserve) (Release) (Hold)))"
THE_RELEASE_CLAUSE_OF_THE_BODY = """    ((Release)
      (if (> (.reserved current) 0)
          (Outcome (Reservation (- (.reserved current) 1)) true)
          (Outcome current false)))))"""
THE_RELEASE_CLAUSE_WITH_A_HOLD = """    ((Release)
      (if (> (.reserved current) 0)
          (Outcome (Reservation (- (.reserved current) 1)) true)
          (Outcome current false)))
    ((Hold) (Outcome current false))))"""
THE_HELPERS_PARAMETER = "  (sig ((n Int)) -> Int ! pure)"
THE_HELPERS_PARAMETER_RENAMED = "  (sig ((count Int)) -> Int ! pure)"
THE_RELEASE_BODY = "          (Outcome (Reservation (- (.reserved current) 1)) true)"
THE_RELEASE_BODY_REWRITTEN = (
    "          (Outcome (Reservation (+ (.reserved current) -1)) true)"
)


def _replacing(source: str, old: str, new: str, what: str) -> str:
    found = source.count(old)
    assert found == 1, (
        f"WHAT: the text this fixture replaces to make {what} stands {found} "
        f"times, not once. WHY: a fixture that changed nothing would make "
        "the test read the same answer twice and call it a difference. "
        "HOW: write the piece as the source above writes it."
    )
    return source.replace(old, new, 1)


def the_reservation_with_a_helper() -> tuple[str, dict]:
    return A_RESERVATION_WHOSE_STEP_CALLS_A_HELPER, a_descriptor_naming("Reservation")


def with_the_helpers_guarantee_deleted() -> tuple[str, dict]:
    """The same machine with the helper's broken guarantee deleted: the
    obligation it failed is gone and no role function changed."""
    source, descriptor = the_reservation_with_a_helper()
    return (
        _replacing(
            source, THE_HELPERS_GUARANTEE, "", "the helper's guarantee deleted"
        ),
        descriptor,
    )


def with_the_helpers_example_replaced() -> tuple[str, dict]:
    """The same machine with the helper's failing example replaced by one
    that holds."""
    source, descriptor = the_reservation_with_a_helper()
    return (
        _replacing(
            source,
            THE_HELPERS_EXAMPLE,
            THE_HELPERS_EXAMPLE_REPLACED,
            "the helper's example replaced",
        ),
        descriptor,
    )


def with_the_event_type_widened() -> tuple[str, dict]:
    """The same machine with a third event variant: every obligation
    about events now ranges over a wider domain."""
    source, descriptor = the_reservation_with_a_helper()
    source = _replacing(
        source, THE_EVENT_TYPE, THE_EVENT_TYPE_WIDENED, "a third event variant"
    )
    source = _replacing(
        source,
        THE_RELEASE_CLAUSE_OF_THE_BODY,
        THE_RELEASE_CLAUSE_WITH_A_HOLD,
        "a body that answers the third variant too",
    )
    source = source.replace(
        "((Release) (> (.reserved current) 0))",
        "((Release) (> (.reserved current) 0)) ((Hold) false)",
    )
    return source, descriptor


def with_the_helpers_parameter_renamed() -> tuple[str, dict]:
    """The same machine with the helper's parameter renamed: what the
    contract is written over is named differently."""
    source, descriptor = the_reservation_with_a_helper()
    source = _replacing(
        source,
        THE_HELPERS_PARAMETER,
        THE_HELPERS_PARAMETER_RENAMED,
        "the helper's parameter renamed",
    )
    source = source.replace("(= result (+ n 2))", "(= result (+ count 2))")
    source = source.replace("  (+ n 1))", "  (+ count 1))")
    return source, a_descriptor_naming("Reservation")


def with_a_body_rewritten() -> tuple[str, dict]:
    """The same machine with one body written differently and every
    contract, example and type exactly as it was."""
    source, descriptor = the_reservation_with_a_helper()
    return (
        _replacing(
            source,
            THE_RELEASE_BODY,
            THE_RELEASE_BODY_REWRITTEN,
            "a body rewritten",
        ),
        descriptor,
    )


def with_a_comment_and_blank_lines_added() -> tuple[str, dict]:
    """The same machine with a comment and blank lines added and nothing
    else."""
    source, descriptor = the_reservation_with_a_helper()
    return (
        "; a comment the digest must not see\n\n"
        + source.replace("(defn state-of", "\n; and another one\n(defn state-of", 1),
        descriptor,
    )


THE_REQUIREMENT_EDITS = (
    ("the helper's guarantee deleted", with_the_helpers_guarantee_deleted),
    ("the helper's failing example replaced", with_the_helpers_example_replaced),
    ("a third event variant", with_the_event_type_widened),
    ("the helper's parameter renamed", with_the_helpers_parameter_renamed),
)

THE_EDITS_THAT_REQUIRE_NOTHING_NEW = (
    ("a body rewritten", with_a_body_rewritten),
    ("a comment and blank lines added", with_a_comment_and_blank_lines_added),
)


# --- a machine whose evidence is longer than this tool writes -------------

_A_THOUSAND_NINES = "9" * 1000


def _multiplied(times: int) -> str:
    written = "(.n current)"
    for _ in range(times):
        written = f"(* {_A_THOUSAND_NINES} {written})"
    return written


def a_machine_whose_evidence_is_too_large_to_write() -> tuple[str, dict]:
    """A counter whose invariant admits only 0 and 1 and whose step
    multiplies the count by a thousand nines five times over.

    From the state 1 -- which the invariant admits and the initialiser
    answers -- the step leads to a number of about five thousand digits,
    longer than this tool writes into an answer. Everything else about
    the machine is ordinary: the state 0 steps to 0, which the one
    declared example states, and the invariant holds of it.
    """
    source = f"""\
(deftype Counter (record (n Int)))
(deftype Event (union (Bump)))
(deftype Outcome (record (state Counter) (accepted Bool)))

(defn valid-state
  (sig ((current Counter)) -> Bool ! pure)
  (examples
    (example (valid-state (Counter 0)) => true)
    (example (valid-state (Counter 2)) => false))
  (<= (.n current) 1))

(defn initial
  (sig () -> Counter ! pure)
  (examples (example (initial) => (Counter 1)))
  (Counter 1))

(defn admissible
  (sig ((current Counter) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Counter 0) (Bump)) => true))
  true)

(defn step
  (sig ((current Counter) (event Event)) -> Outcome ! pure)
  (examples (example (step (Counter 1) (Bump)) => (Outcome (Counter 0) true)))
  (Outcome (Counter {_multiplied(5)}) true))

(defn state-of
  (sig ((produced Outcome)) -> Counter ! pure)
  (examples (example (state-of (Outcome (Counter 1) true)) => (Counter 1)))
  (.state produced))
"""
    return source, a_descriptor_naming("Counter")


# --- a machine that starts outside its own invariant ---------------------

def a_machine_whose_initialiser_starts_outside_the_invariant() -> tuple[str, dict]:
    """A reservation whose initialiser answers a full-and-then-some state
    the invariant refuses, and whose first declared transition from there
    the step refuses.

    Nothing reachable can be said about such a machine: the state it
    starts in is not one the invariant admits, so no trace from it is a
    reachable counterexample however the step behaves there.
    """
    source = """\
(deftype Reservation (record (reserved Int)))
(deftype Event (union (Reserve) (Release)))
(deftype Outcome (record (state Reservation) (accepted Bool)))

(defn valid-state
  (sig ((current Reservation)) -> Bool ! pure)
  (examples
    (example (valid-state (Reservation 0)) => true)
    (example (valid-state (Reservation 5)) => false))
  (and (>= (.reserved current) 0) (<= (.reserved current) 2)))

(defn initial
  (sig () -> Reservation ! pure)
  (examples (example (initial) => (Reservation 5)))
  (Reservation 5))

(defn step
  (sig ((current Reservation) (event Event)) -> Outcome ! pure)
  (ensures (= (.accepted result) false))
  (examples
    (example (step (Reservation 5) (Reserve)) => (Outcome (Reservation 6) true)))
  (Outcome current false))

(defn state-of
  (sig ((produced Outcome)) -> Reservation ! pure)
  (examples (example (state-of (Outcome (Reservation 1) true)) => (Reservation 1)))
  (.state produced))

(defn admissible
  (sig ((current Reservation) (event Event)) -> Bool ! pure)
  (examples (example (admissible (Reservation 0) (Reserve)) => true))
  true)
"""
    return source, a_descriptor_naming("Reservation")
