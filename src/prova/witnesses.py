"""The kinds of evidence a disproof may carry, and the two kinds this
tool builds for a machine.

SPEC.md lines 307-311: a disproof requires a validated source-level
witness satisfying the claim's assumptions and violating its conclusion,
function witnesses must replay against the reference semantics, and an
induction-step witness and a reachable execution trace are different
evidence types -- only a validated initial state and transition sequence
may be called a reachable counterexample.

So the two are types here, not two readings of one shape: each says in
the answer which kind it is and whether anything shows that a run of the
program reaches it. One table names them, the manifest publishes that
table and an answer carries nothing the table does not name, so a reader
who meets a kind can look it up and a reader who looks one up will meet
it.

The older shape, an input of the declared types that the reference
semantics refuses when it is run, carries no kind: it was published
before either of these existed and is left character for character as it
was, so an answer about a program that names no machine is the text it
has always been. Nothing here reads a file, asks a solver or runs a
program: these are values, built by the two owners in `replay` that have
really run something.
"""

from __future__ import annotations

from dataclasses import dataclass

AN_INDUCTION_STEP_WITNESS = "induction_step_witness"
A_REACHABLE_COUNTEREXAMPLE = "reachable_counterexample"

# What an induction-step witness refuses to let a reader believe. Said on
# the witness itself rather than in a document, because the pair it names
# reads exactly like a run of the machine and nothing else in the entry
# would tell the reader it is not one.
NOT_A_REACHABLE_TRACE = (
    "this is not a reachable trace: the state below was found by the solver "
    "among the states the invariant admits, and nothing here shows that any "
    "run of this machine from its initialiser reaches it. One step out of "
    "the invariant is what it shows, and that is what breaks the "
    "preservation obligation (SPEC.md lines 307-311)"
)

# Why a trace built from the initialiser may carry the other name.
WHAT_A_REACHABLE_TRACE_SHOWS = (
    "this is a reachable counterexample: it begins at the state the "
    "initialiser answers, which the invariant admits, and every transition "
    "below was run through the reference semantics from there. Only a "
    "validated initial state with a sequence of transitions is called this "
    "(SPEC.md lines 307-311)"
)

THE_KINDS = {
    AN_INDUCTION_STEP_WITNESS: {
        "what_it_is": (
            "a state the invariant admits together with an event the machine "
            "admits there, whose step leaves the invariant: the invariant was "
            "run on the state and answered true, the admissibility predicate "
            "was run there and answered true, and the invariant was run on "
            "the state the step answers and answered false"
        ),
        "carried_in": "the 'counterexample' of a machine obligation entry",
        "claims_reachability": False,
    },
    A_REACHABLE_COUNTEREXAMPLE: {
        "what_it_is": (
            "the state the machine's initialiser answers, which the invariant "
            "admits, followed by the first failing declared transition from "
            "that state: the transitions the program's own examples declare "
            "are replayed from it through the reference semantics, and the "
            "first one the program refuses or answers against its approved "
            "example is carried, with the transitions replayed before it"
        ),
        "carried_in": (
            "the 'reachable_counterexample' of the machine block of a verify "
            "answer, and absent wherever every declared transition from the "
            "initial state replays"
        ),
        "claims_reachability": True,
    },
}

# What a reader is told about an answer that carries no kind at all.
WHAT_A_WITNESS_WITHOUT_A_KIND_IS = (
    "A counterexample carrying no kind is an input of the declared types "
    "that the reference semantics refuses when it is run: the shape this "
    "tool published before either kind above existed, kept character for "
    "character so that an answer about a program that names no machine is "
    "the text it was. It is not a reachable trace either: it names an input, "
    "not a run from the initialiser."
)


@dataclass(frozen=True)
class EvidenceTooLargeToWrite:
    """Evidence a run established and this tool will not write.

    The reference semantics can compute a number past the digits this
    tool writes into an answer. The run itself finished, so something was
    established; the evidence cannot be shown, and evidence a reader
    cannot see is no evidence at all. So the obligation is left unsettled
    naming the limit, rather than reported broken on a counterexample
    nobody can read -- and rather than letting the limit end the whole
    answer, which would lose the inventory the reader came for.
    """

    what_could_not_be_written: str
    limit: str
    digits_reached: int
    maximum: int

    def because(self) -> str:
        return (
            f"the solver found an input where the denial of this obligation "
            f"has a solution, and replaying it computed {self.what_could_not_be_written} "
            f"of {self.digits_reached} digits, which this tool will not write "
            f"into an answer: the limit {self.limit!r} allows at most "
            f"{self.maximum} digits. Evidence a reader cannot be shown is no "
            "counterexample, so this obligation is left unsettled rather than "
            "reported as broken, and nothing about the program is claimed "
            "either way. The rest of the inventory stands"
        )

    def published(self) -> dict:
        return {
            "what_could_not_be_written": self.what_could_not_be_written,
            "digits_reached": self.digits_reached,
            "limit": self.limit,
            "maximum": self.maximum,
            "what_this_says": (
                "a run from the initial state established something this tool "
                "will not write: the number it computed is longer than the "
                "digits an answer carries, so no trace is shown here. Nothing "
                "about the machine is claimed either way, and every "
                "obligation of the inventory stands as it was settled"
            ),
        }


def published_kinds() -> dict:
    """The kinds of witness evidence an answer of this tool names, each
    with what it is, where it is carried and whether it claims that a run
    reaches it.

    Read from the one table above, so a kind an agent looks up here is
    one an answer can carry and a kind an answer carries is one it can
    look up.
    """
    return {kind: dict(says) for kind, says in THE_KINDS.items()}


@dataclass(frozen=True)
class AnInductionStepWitness:
    """One admitted transition whose step leaves the invariant, with what
    each role answered when it was run.

    Built only by `replay.TheTransition`, which has run all three, so a
    pair nothing confirmed cannot be reported as one. The three booleans
    are not a caller's claim: each is what a run answered.
    """

    state: str
    event: str
    state_after_the_step: str
    invariant_of_the_state: bool
    admissible_there: bool
    invariant_after_the_step: bool
    the_step_contract_said: str
    step: str
    state_of: str
    invariant: str
    admissible: str
    replayed_within: dict

    kind = AN_INDUCTION_STEP_WITNESS

    def because(self) -> str:
        """The reason the obligation carries beside the word
        'disproved'."""
        return (
            "the solver found a state and an event of the declared types that "
            f"break this obligation, and running '{self.invariant}' on the "
            f"state the step '{self.step}' answers there refuses it: the "
            "invariant holds of the state, the event is admissible in it and "
            "the invariant does not hold afterwards"
        )

    def published(self) -> dict:
        return {
            "kind": self.kind,
            "state": self.state,
            "event": self.event,
            "invariant_of_the_state": self.invariant_of_the_state,
            "admissible_there": self.admissible_there,
            "state_after_the_step": self.state_after_the_step,
            "invariant_after_the_step": self.invariant_after_the_step,
            "read_by": {
                "invariant": self.invariant,
                "admissible": self.admissible,
                "step": self.step,
                "state-of": self.state_of,
            },
            "what_was_run": (
                f"'{self.invariant}' on the state, '{self.admissible}' on the "
                f"state and the event, the body of '{self.step}' over the "
                f"pair, and '{self.invariant}' on the state "
                f"'{self.state_of}' reads from what it answered. The body is "
                "what the machine's transition is defined as; whether the "
                "step also keeps its own postcondition is a separate "
                "obligation of this same inventory"
            ),
            "the_step_own_contract": self.the_step_contract_said,
            "reachability": NOT_A_REACHABLE_TRACE,
            "replayed_within": dict(self.replayed_within),
        }


@dataclass(frozen=True)
class ATransitionReplayed:
    """One transition of a trace: the event it took, and what running the
    step on it did."""

    event: str
    what_the_run_did: str

    def published(self) -> dict:
        return {"event": self.event, "what_the_run_did": self.what_the_run_did}


@dataclass(frozen=True)
class AReachableCounterexample:
    """A validated initial state and the transitions replayed from it.

    Built only by `replay.ATraceFromTheInitialState`, which has run the
    initialiser, checked the invariant of what it answered and run every
    transition it carries, so the one name SPEC.md reserves cannot be
    given to anything else.
    """

    initial_state: str
    invariant_of_the_initial_state: bool
    transitions: tuple[ATransitionReplayed, ...]
    init: str
    invariant: str
    replayed_within: dict

    kind = A_REACHABLE_COUNTEREXAMPLE

    def published(self) -> dict:
        return {
            "kind": self.kind,
            "initial_state": self.initial_state,
            "invariant_of_the_initial_state": self.invariant_of_the_initial_state,
            "transitions": [
                transition.published() for transition in self.transitions
            ],
            "read_by": {"init": self.init, "invariant": self.invariant},
            "reachability": WHAT_A_REACHABLE_TRACE_SHOWS,
            "replayed_within": dict(self.replayed_within),
        }
