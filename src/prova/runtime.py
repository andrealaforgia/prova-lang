"""Driving a machine whose roles resolved, one event at a time.

SPEC.md lines 404-409 describe the first runtime: it executes transitions
sequentially over one authoritative state, validates the event data and
the admissibility, and then publishes the returned state and outcome
together. Lines 409-411 say that an event outside the admissible domain
receives an explicit boundary rejection with the state unchanged, and
that this differs from an admissible event whose business result is a
rejection. Lines 415-418 say that the evidence is conditional on the
model: function proofs alone establish nothing about a host.

This module owns the order of a run and nothing else. It reads no field
of a request, opens no file, reads no clock and writes no answer: it is
handed a machine whose eight roles already resolved (prova.machine) and
the values the request carried, it asks prova.evaluator to run a role's
function, and it answers what the run published or the one thing that
stopped it. The words it publishes are written here once, so what the
manifest documents and what an answer carries cannot be two spellings.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import evaluator, machine, syntax
from prova.values import render

# The three words one attempted event is published under: the step ran
# for it, the machine does not admit it there, or the state it would run
# from is outside the invariant the descriptor names.
TRANSITION = "transition"
BOUNDARY_REJECTION = "boundary_rejection"
STATE_OUTSIDE_INVARIANT = "state_outside_invariant"
THE_RESULTS = (TRANSITION, BOUNDARY_REJECTION, STATE_OUTSIDE_INVARIANT)

# The word a stop carries when a role's own contract refused the values
# the run called it with. It is a reason a run stopped and never the
# result of an attempt: no attempt was published for the event that
# reached it, because nothing of the machine was decided there.
CONTRACT_REFUSED = "contract_refused"
THE_STOP_REASONS = (
    BOUNDARY_REJECTION,
    STATE_OUTSIDE_INVARIANT,
    CONTRACT_REFUSED,
)

# The two results that end a run, each beside the role of the descriptor
# that decided it: a reader of a stop is sent to the part of their own
# machine that answered, and not to this tool. A refused contract names
# the role the run was asking, which the refusal itself carries.
THE_ROLE_THAT_DECIDES = {
    BOUNDARY_REJECTION: machine.ADMISSIBLE,
    STATE_OUTSIDE_INVARIANT: machine.INVARIANT,
}

# What one contract of a role function can refuse during a run, read
# from the two refusals the evaluator raises.
PRECONDITION_VIOLATION = "precondition_violation"
POSTCONDITION_VIOLATION = "postcondition_violation"

# What an answer about a run says it settles, and what it says it
# settles nothing about. Written here, beside the run it is about, and
# published both in the answer and in what the manifest documents for
# the operation, so an Owner reads the same sentence in both places.
WHAT_A_RUN_SAYS = (
    "These are the values the functions the descriptor names answered, in "
    "the submitted revision of the submitted program, for the state and "
    "the events this request carried: the invariant role was asked before "
    "each event, the admissibility role was asked next, the step ran only "
    "where it answered true, and every later event ran from the state the "
    "projection read off the outcome before it. It settles nothing further "
    "about the machine: no obligation of the program was put to a solver, "
    "no declared example was run, and the invariant was read at the states "
    "this run reached and at no other. It settles nothing about a host "
    "that would carry these events either: not that a transition is "
    "atomic, not that an event ever reaches the machine, not any order "
    "between several hosts, and not that anything happens in the end. The "
    "sentences under 'assumptions_stated' are the descriptor's own, read "
    "here and checked by nothing."
)


@dataclass(frozen=True)
class Attempted:
    """One event the run attempted: where it stood in the request, the
    event itself, the state it was attempted from, the word it is
    published under, the state after it and the outcome the step
    answered.

    Built only through the three constructors below, so an attempt that
    ran no step cannot carry an outcome and cannot publish a state other
    than the one it came in with.
    """

    position: int
    event: object
    state_before: object
    state_after: object
    outcome: object | None
    result: str

    @classmethod
    def transition(
        cls, position: int, event: object, before: object, outcome: object, after: object
    ) -> "Attempted":
        return cls(position, event, before, after, outcome, TRANSITION)

    @classmethod
    def refused_at_the_boundary(
        cls, position: int, event: object, state: object
    ) -> "Attempted":
        return cls(position, event, state, state, None, BOUNDARY_REJECTION)

    @classmethod
    def outside_the_invariant(
        cls, position: int, event: object, state: object
    ) -> "Attempted":
        return cls(position, event, state, state, None, STATE_OUTSIDE_INVARIANT)

    def ran_the_step(self) -> bool:
        return self.result == TRANSITION

    def stopped_the_run(self) -> bool:
        return not self.ran_the_step()

    def published(self) -> dict:
        entry = {
            "position": self.position,
            "event": render(self.event),
            "result": self.result,
            "state_before": render(self.state_before),
            "state_after": render(self.state_after),
        }
        if self.outcome is None:
            return entry
        entry["outcome"] = render(self.outcome)
        return entry


@dataclass(frozen=True)
class Stopped:
    """Why a run stopped before its last event: the position it stopped
    at, the word that says why, the role of the descriptor that decided
    it and how many events were never attempted."""

    position: int
    reason: str
    role: str
    events_not_run: int

    @classmethod
    def at(cls, attempt: "Attempted", events: int) -> "Stopped":
        """The stop a published attempt stands for: the attempt that ran
        no step, out of `events` events.

        Built from that attempt rather than by reaching for the last of
        a list, so a run cannot publish a stop that disagrees with the
        entry it stands at.
        """
        return cls(
            attempt.position,
            attempt.result,
            THE_ROLE_THAT_DECIDES[attempt.result],
            events - attempt.position,
        )

    @classmethod
    def refusing_a_contract(
        cls, refused: "ContractRefused", events: int
    ) -> "Stopped":
        """The stop a refused contract stands for: the position the run
        was driving, out of `events` events.

        No attempt is published for that event -- nothing of the machine
        was decided there -- so the count of the events left behind is
        read from the position, exactly as it is for an attempt.
        """
        return cls(refused.position, CONTRACT_REFUSED, refused.role, events - refused.position)

    def published(self) -> dict:
        return {
            "position": self.position,
            "reason": self.reason,
            "role": self.role,
            "events_not_run": self.events_not_run,
        }


@dataclass(frozen=True)
class Driven:
    """What one run published: the state it was given, the events it
    attempted in order, the stop when one event was not run, and the
    assumptions the descriptor states.

    The only value an answer about a run reports from. The run reads no
    clock, writes no file and keeps nothing, so the same request
    published twice says the same thing.
    """

    state_given: object
    attempted: tuple[Attempted, ...]
    stop: "Stopped | None"
    assumptions: machine.StatedAssumptions
    refused: "ContractRefused | None" = None

    def state_now(self) -> object:
        """The state the run left the machine at: the one its last
        attempt published, or the state it was given when no attempt was
        published at all -- which is a run stopped at its first event by
        a contract of one of the roles.
        """
        if not self.attempted:
            return self.state_given
        return self.attempted[-1].state_after

    def published(self) -> dict:
        published = {
            "state_given": render(self.state_given),
            "transitions": [attempt.published() for attempt in self.attempted],
            "state_now": render(self.state_now()),
            "assumptions_stated": self.assumptions.published(),
            "what_this_says": WHAT_A_RUN_SAYS,
        }
        if self.stop is None:
            return published
        published["stopped_at"] = self.stop.published()
        return published


@dataclass(frozen=True)
class StateRefused:
    """The state the request sent, which the invariant role excludes.

    A machine is defined from the states its invariant holds at, so this
    is refused before anything runs. It carries the role and the name
    the descriptor gave it, which is what the Owner repairs; the
    sentence belongs to the answer and is written where every refusal of
    this tool is written.
    """

    role: str
    named: str


@dataclass(frozen=True)
class ContractRefused:
    """A contract of one role's function that was broken while the run
    was asking it: which of the two contracts, the role the run was
    asking, the function that broke it and the event the run was
    attempting.

    The role and the function are both carried: the role says which part
    of the descriptor the run was reading, and the function is the one
    whose contract refused, which may be a function the role's own body
    reaches.
    """

    category: str
    role: str
    function_name: str
    position: int


class _RoleRefused(Exception):
    """A contract refused while one role was being run, carried out of
    the one place a role is run so that the role is known where the
    refusal is built."""

    def __init__(self, category: str, role: str, function_name: str) -> None:
        super().__init__(f"{function_name}: {category}")
        self.category = category
        self.role = role
        self.function_name = function_name


class MachineRuntime:
    """A machine whose eight roles resolved, ready to be driven.

    It answers one question -- what a state and a sequence of events
    published -- and keeps nothing between two answers. The roles are
    asked by the name the descriptor gave them, so the one resolution
    this tool does is the one the run uses.
    """

    def __init__(self, roles: machine.ResolvedMachine, program: syntax.Program) -> None:
        self._roles = roles
        self._program = program

    @classmethod
    def of(
        cls, roles: machine.ResolvedMachine, program: syntax.Program
    ) -> "MachineRuntime":
        return cls(roles, program)

    def type_of(self, role: str) -> str:
        """The name the descriptor gave one of its three types, which is
        the type a value sent for that role must have."""
        return self._roles.named_for(role)

    def driven(
        self,
        state: object,
        events: tuple[object, ...],
        between_events=lambda: None,
    ) -> "Driven | StateRefused":
        """What driving `events` from `state` published, or the refusal
        of the state the run was given.

        Each event is attempted from the state the one before it
        published, in the order the request wrote them. The run stops at
        the first event it does not drive -- one outside the admissible
        domain, one whose state the invariant excludes, or one that
        reached a refused contract of a role -- and the events after it
        are not attempted at all. What did run is published either way.

        `between_events()` is the caller's rule about how much work this
        run may still do, asked once before each event and once more
        after the last transition, before a run is published as one that
        finished: driving a sequence is the work of the operation, and
        the budgets that measure it belong to the caller that owns them.
        The last transition is work like any other, and asking only
        before each event left whatever it spent unmeasured -- a single
        event could spend any amount of time and still be answered, and
        what it spent appeared only at the next boundary, in the next
        event's reading. A run that stopped early is published as it
        stands: what it did run is an answer about the machine, and the
        caller reads how far it got.
        """
        if not events:
            raise ValueError(
                "WHAT: a machine was asked to be driven through no event at "
                "all: the 'events' sequence handed to this run is empty. "
                "WHY: a run publishes one attempt per event, and a run with "
                "no event would publish the state it was handed as though a "
                "transition had left it there, which is a machine nothing "
                "moved. HOW: hand this run at least one event; the reader of "
                "a request refuses an empty 'events' field by name, so a "
                "caller reaching here has built the sequence itself."
            )
        attempted: list[Attempted] = []
        standing = state
        for position, event in enumerate(events, start=1):
            between_events()
            attempt = self._attempted(position, standing, event)
            if isinstance(attempt, ContractRefused):
                return Driven(
                    state,
                    tuple(attempted),
                    Stopped.refusing_a_contract(attempt, len(events)),
                    self._roles.assumptions,
                    attempt,
                )
            if attempt.result == STATE_OUTSIDE_INVARIANT and position == 1:
                return StateRefused(machine.INVARIANT, self.type_of(machine.INVARIANT))
            attempted.append(attempt)
            if attempt.stopped_the_run():
                return Driven(
                    state,
                    tuple(attempted),
                    Stopped.at(attempt, len(events)),
                    self._roles.assumptions,
                )
            standing = attempt.state_after
        between_events()
        return Driven(state, tuple(attempted), None, self._roles.assumptions)

    def _attempted(
        self, position: int, state: object, event: object
    ) -> "Attempted | ContractRefused":
        try:
            return self._attempt(position, state, event)
        except _RoleRefused as refused:
            return ContractRefused(
                refused.category, refused.role, refused.function_name, position
            )

    def _attempt(self, position: int, state: object, event: object) -> Attempted:
        """One event attempted from one state.

        The invariant is asked first, at every event and not only at the
        first: a transition from a state the machine's own invariant
        excludes is one the machine does not define, whoever sent that
        state. The admissibility is asked next, and the step runs only
        where it answered true.
        """
        if self._answered(machine.INVARIANT, (state,)) is not True:
            return Attempted.outside_the_invariant(position, event, state)
        if self._answered(machine.ADMISSIBLE, (state, event)) is not True:
            return Attempted.refused_at_the_boundary(position, event, state)
        outcome = self._answered(machine.STEP, (state, event))
        return Attempted.transition(
            position,
            event,
            state,
            outcome,
            self._answered(machine.STATE_OF, (outcome,)),
        )

    def _answered(self, role: str, args: tuple[object, ...]) -> object:
        """What the function standing in `role` answers for `args`.

        The one place a role is run, so every call of every role has its
        contracts checked by the evaluator in the same way, and a run
        that breaks one is refused in one place.
        """
        function = self._program.functions[self._roles.named_for(role)]
        try:
            return evaluator.call_function(function, args, self._program)
        except evaluator.PreconditionViolation as violation:
            raise _RoleRefused(
                PRECONDITION_VIOLATION, role, violation.function_name
            ) from None
        except evaluator.PostconditionViolation as violation:
            raise _RoleRefused(
                POSTCONDITION_VIOLATION, role, violation.function_name
            ) from None
