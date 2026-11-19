"""What running a machine's own functions shows about a candidate.

SPEC.md lines 307-309 let a disproof carry only a validated witness, and
require a function witness to replay against the reference semantics
inside a declared replay budget. For an obligation about one function
that replay is one call, and `discharge` owns it: it runs the function
and reads whether it was refused. The two questions below are not that
one.

A pair the solver found for the denial of preservation refuses nothing:
the step answers a state, and the state is simply outside the invariant.
Confirming it is therefore a composition -- the invariant on the state,
the admissibility predicate there, the step over the pair, and the
invariant on the state the projection reads from what it answered -- and
only the last of those answering false confirms anything. A run from the
initialiser is a second question again: it begins at the one state the
machine starts in and walks the transitions the program itself declares.

Both own the same discipline: every answer below is something the
reference semantics really said, nothing is inferred from the shape of a
program, and anything that cannot be run -- a value of the wrong type, a
run past the depth budget, a call the program refuses -- confirms
nothing. The roles are taken as a value that answers to the five names,
so this module states no second table of which function fills which
role.
"""

from __future__ import annotations

from prova import evaluator, witnesses
from prova.values import render

# The budget a confirmation stands inside, said the way the obligations
# say it: read from the limit itself, so an answer and the manifest
# cannot carry two numbers.
THE_REPLAY_BUDGET = {
    "limit": evaluator.EVALUATION_LIMIT.name,
    "maximum": evaluator.EVALUATION_LIMIT.maximum,
}

# What stops a run without saying anything about the program.
_NOTHING_WAS_SHOWN = (
    evaluator.EvaluationTooDeep,
    evaluator.MalformedValue,
    evaluator.IllTypedValue,
)
_THE_PROGRAM_REFUSED = (
    evaluator.PreconditionViolation,
    evaluator.PostconditionViolation,
)


class _RunningTheRoles:
    """The roles of one machine over one program, run.

    Shared by the two questions below so that both call the reference
    semantics the one way: arguments checked against the declared types
    first, every refusal and every budget read as 'nothing was shown'.
    """

    def __init__(self, roles, program) -> None:
        self._roles = roles
        self._program = program

    def answered(self, named: str, args: tuple) -> object:
        """What `named` answers over `args`, or `None` when the run said
        nothing: a value of the wrong type, a refusal of the program, or
        a run past the depth budget."""
        function = self._program.functions.get(named)
        if function is None or len(function.signature.params) != len(args):
            return None
        try:
            for argument, parameter in zip(args, function.signature.params):
                evaluator.check_value_type(
                    argument, parameter.type_name, self._program, "argument"
                )
            return evaluator.call_function(function, args, self._program)
        except (*_NOTHING_WAS_SHOWN, *_THE_PROGRAM_REFUSED):
            return None

    def answered_true(self, named: str, args: tuple) -> bool:
        return self.answered(named, args) is True

    def answered_false(self, named: str, args: tuple) -> bool:
        return self.answered(named, args) is False

    def the_state_the_step_leads_to(self, state, event) -> object:
        """The state the machine's transition leads to, or `None` when
        the run said nothing.

        The transition of SPEC.md lines 372-376 is `state-of(step(s, e))`,
        and the step's own body is what the model means by the step: the
        body is run here and the step's postcondition is not asked,
        because whether the step keeps its own promise is a separate
        obligation of the same inventory, listed and settled on its own.
        The witness says this, so nothing reading it can take the state
        below for one the step's contract accepted.
        """
        step = self._program.functions.get(self._roles.step)
        if step is None or len(step.signature.params) != 2:
            return None
        bound = dict(zip((p.name for p in step.signature.params), (state, event)))
        try:
            for argument, parameter in zip(
                (state, event), step.signature.params
            ):
                evaluator.check_value_type(
                    argument, parameter.type_name, self._program, "argument"
                )
            answered = evaluator.eval_expr(step.body, bound, self._program)
        except (*_NOTHING_WAS_SHOWN, *_THE_PROGRAM_REFUSED):
            return None
        return self.answered(self._roles.state_of, (answered,))


class TheTransition:
    """One candidate pair, asked whether the machine's own functions
    confirm it as a witness that the step leaves the invariant.

    The one place a witness of preservation is built, so a pair the
    reference semantics did not refute cannot be reported as a
    counterexample. Three things must hold, each of them something a run
    answered: the invariant holds of the state, the event is admissible
    there, and the invariant does not hold of the state the transition
    leads to. Anything else -- including a run that could not finish --
    confirms nothing and leaves the obligation unsettled.
    """

    def __init__(self, roles, program) -> None:
        self._roles = roles
        self._running = _RunningTheRoles(roles, program)

    def confirmed_witness(self, texts: tuple, args: tuple):
        """The witness the machine's functions confirm for `args`, or
        `None` when they confirm none."""
        if len(args) != 2 or len(texts) != 2:
            return None
        state, event = args
        if not self._running.answered_true(self._roles.invariant, (state,)):
            return None
        if not self._running.answered_true(
            self._roles.admissible, (state, event)
        ):
            return None
        after = self._running.the_state_the_step_leads_to(state, event)
        if after is None:
            return None
        if not self._running.answered_false(self._roles.invariant, (after,)):
            return None
        return witnesses.AnInductionStepWitness(
            texts[0],
            texts[1],
            render(after),
            self._roles.step,
            self._roles.state_of,
            self._roles.invariant,
            self._roles.admissible,
            THE_REPLAY_BUDGET,
        )


class ATraceFromTheInitialState:
    """One machine, asked for a counterexample its own declared
    transitions reach from the state it starts in.

    The one place a reachable counterexample is built. It walks only what
    the program itself declares -- the examples of the step, which are
    the transitions the Owner approved -- from the state the initialiser
    answers, and it reports the first of them the program refuses or
    answers against. It searches nothing: a fault no declared transition
    from the initial state reaches is left to the obligations, which say
    what they say without claiming a run reaches it.
    """

    def __init__(self, roles, program) -> None:
        self._roles = roles
        self._program = program
        self._running = _RunningTheRoles(roles, program)

    def built(self):
        """The trace this machine reaches from its initial state, or
        `None` when every declared transition from there replays."""
        initial = self._running.answered(self._roles.init, ())
        if initial is None:
            return None
        if not self._running.answered_true(self._roles.invariant, (initial,)):
            return None
        step = self._program.functions.get(self._roles.step)
        if step is None or len(step.signature.params) != 2:
            return None
        for declared in step.examples:
            if len(declared.args) != 2:
                continue
            state, event = declared.args
            if not evaluator.values_equal(state, initial):
                continue
            if not self._running.answered_true(
                self._roles.admissible, (state, event)
            ):
                continue
            did = self._what_the_run_did(step, (state, event), declared.expected)
            if did is None:
                continue
            return witnesses.AReachableCounterexample(
                render(initial),
                (witnesses.ATransitionReplayed(render(event), did),),
                self._roles.init,
                self._roles.invariant,
                THE_REPLAY_BUDGET,
            )
        return None

    def _what_the_run_did(self, step, args: tuple, expected) -> str | None:
        """What running the step on one transition did, where what it did
        is a counterexample, and `None` where the transition replayed.

        Two things make it one: the program refusing the transition its
        own approved example declares, and the program answering a value
        that example does not state. Both are read from a run; neither is
        read off the text of the program.
        """
        try:
            answered = evaluator.call_function(step, args, self._program)
        except _THE_PROGRAM_REFUSED as refusal:
            return (
                f"running the step from the initial state refused it: "
                f"{refusal}"
            )
        except _NOTHING_WAS_SHOWN:
            return None
        if evaluator.values_equal(answered, expected):
            return None
        return (
            f"running the step from the initial state answers "
            f"{render(answered)} and the approved example of this machine "
            f"states {render(expected)}"
        )
