"""The three obligations a machine owes for its candidate inductive
invariant, and the claim each one states.

SPEC.md lines 395-401 name them for a candidate invariant `Inv`:
initialisation (`Init(s) => Inv(s)`), step-enabledness
(`Inv(s) and admissible(s, e) => Pre_step(s, e)`) and preservation
(`Inv(s) and admissible(s, e) => Inv(state-of(step(s, e)))`). This module
owns those three rules and nothing else: it reads no file, no field of a
request and no descriptor document, asks no solver and settles nothing.
It states what has to be shown, as obligations of the same inventory the
program's own obligations stand in, so one loop settles all of them and
one word is computed over all of them.

The two obligations about events are stated over the parameters the step
itself declares, which become one symbolic value of the state type and
one of the event type. Nothing here reads the values an event type holds,
so an event type with no bound is stated exactly as one with two values:
SPEC.md lines 384-386 require the obligations to range symbolically over
typed events and forbid enumerating an unbounded event type as though it
were finite.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import encoding, machine, obligations, syntax

# Where the obligations of a machine stand. A site is a structural path,
# never a line number, so these three identities are the same for any
# program the same descriptor is read against.
MACHINE = "machine"
INITIALISATION = "initialisation"
STEP_ENABLEDNESS = "step-enabledness"
PRESERVATION = "preservation"


def _over_every_typed_event(event_type: str) -> str:
    """What an obligation about events says it was shown over.

    One sentence for both of them, naming the type and not its values: a
    reader of either entry is told the domain the statement covers, and
    neither can say it was shown over a list of events.
    """
    return (
        f"one value of the type {event_type!r}, read as a single symbolic "
        "value of that type: the statement covers every value the type has, "
        "no event of it is listed, and a type with no bound is read exactly "
        "as a type with two values (SPEC.md lines 384-386)"
    )


# What the replay gate of this tool can and cannot confirm for an
# obligation of a machine, said beside the two it cannot. The gate
# confirms a solution the solver found by running the role function over
# it and seeing the reference semantics refuse it; a state that leaves
# the invariant after the step is no refusal of the step, so a solution
# for the denial of these two leaves them unsettled with their reason
# rather than reported as broken, and nothing weaker is put in their
# place.
NO_REFUSAL_CONFIRMS_A_WITNESS = (
    "a solution the solver finds for the denial of this obligation is "
    "reported as unsettled and not as a counterexample: this tool confirms "
    "a witness by running the role function over it and seeing the "
    "reference semantics refuse it, and neither the initialiser answering "
    "a state outside the invariant nor a step leaving it is such a "
    "refusal. The obligation is then left unsettled with that reason, and "
    "no weaker condition is put in the invariant's place"
)


@dataclass(frozen=True)
class TheRolesOfAMachine:
    """The function each role of one machine resolved to, and the name of
    its event type.

    Read from the witness that resolved the descriptor, so the names an
    obligation is written over are the ones the answer reports for the
    roles.
    """

    init: str
    step: str
    state_of: str
    admissible: str
    invariant: str
    event_type: str

    @classmethod
    def of(cls, resolved: machine.ResolvedMachine) -> "TheRolesOfAMachine":
        return cls(
            resolved.named_for(machine.INIT),
            resolved.named_for(machine.STEP),
            resolved.named_for(machine.STATE_OF),
            resolved.named_for(machine.ADMISSIBLE),
            resolved.named_for(machine.INVARIANT),
            resolved.named_for(machine.EVENT),
        )

    def published(self, *roles: str) -> dict:
        """The roles an obligation is written over, each beside the
        function that filled it, so a reader can look the obligation up
        against the descriptor that was sent."""
        named = {
            machine.INIT: self.init,
            machine.STEP: self.step,
            machine.STATE_OF: self.state_of,
            machine.ADMISSIBLE: self.admissible,
            machine.INVARIANT: self.invariant,
        }
        return {role: named[role] for role in roles}


class TheStateAMachineStartsIn:
    """The state the initialiser answers: the one state the
    initialisation obligation is stated over.

    It is a state and not a transition, so it stands beside the pair
    below rather than inside it: the initialiser takes nothing, so the
    claim it builds is about no variable at all and assumes nothing. Both
    of these own how a claim about one machine is built, and the three
    obligations only say what has to be shown.
    """

    def __init__(self, roles: TheRolesOfAMachine, program: syntax.Program) -> None:
        self._roles = roles
        self._program = program
        self._translation = encoding.Translation(program)

    def the_invariant_holds_of_it(self) -> encoding.Claim:
        """The claim that the state the initialiser answers satisfies the
        invariant (SPEC.md line 398)."""
        return encoding.Claim(
            encoding.Shapes.of(self._program),
            (),
            (),
            self._translation.term_of(
                _applied(
                    self._roles.invariant, (_applied(self._roles.init, ()),)
                ),
                {},
            ),
        )


class AnAdmittedTransition:
    """A state the invariant admits together with an event the machine
    admits there: the one pair both obligations about events are stated
    over.

    It holds the two assumptions in one place -- that the invariant holds
    of the state and that the event is admissible there -- so the two
    obligations cannot be shown over different domains. The variables of
    every claim it builds are the parameters the step declares, which is
    what makes the statement symbolic over the typed event: no value of
    the event type is read here.

    One of these is built per claim, because a translation spends an
    expansion budget as it inlines calls and no claim may be shortened by
    what another one spent.
    """

    def __init__(self, roles: TheRolesOfAMachine, program: syntax.Program) -> None:
        self._roles = roles
        self._program = program
        self._step = program.functions[roles.step]
        self._translation = encoding.Translation(program)
        self._bound = self._translation.parameters_of(self._step)

    def the_step_is_defined(self) -> encoding.Claim:
        """The claim that the step's own precondition holds of every
        admitted transition (SPEC.md line 399)."""
        return self._claim(
            self._translation.conjunction_of(self._step.requires, self._bound)
        )

    def the_invariant_holds_after_it(self) -> encoding.Claim:
        """The claim that the state the step leads to satisfies the
        invariant again (SPEC.md line 400)."""
        return self._claim(
            self._term(
                _applied(
                    self._roles.invariant,
                    (
                        _applied(
                            self._roles.state_of,
                            (_applied(self._roles.step, self._state_and_event()),),
                        ),
                    ),
                )
            )
        )

    def _claim(self, conclusion: encoding.Term) -> encoding.Claim:
        return encoding.Claim(
            encoding.Shapes.of(self._program),
            encoding.variables_of(self._step),
            (
                self._term(_applied(self._roles.invariant, (self._state(),))),
                self._term(
                    _applied(self._roles.admissible, self._state_and_event())
                ),
            ),
            conclusion,
        )

    def _state_and_event(self) -> tuple:
        return (self._state(), self._event())

    def _state(self) -> syntax.NameRef:
        return _named(self._step.signature.params[0].name)

    def _event(self) -> syntax.NameRef:
        return _named(self._step.signature.params[1].name)

    def _term(self, expression: object) -> encoding.Term:
        return self._translation.term_of(expression, self._bound)


@dataclass(frozen=True)
class Initialisation(obligations.Obligation):
    """The state the initialiser answers satisfies the invariant
    (SPEC.md line 398).

    Its claim is about no variable at all: the initialiser takes nothing,
    so the state it answers is one value and the statement is about that
    value. An initial condition nothing satisfies is caught here and
    nowhere else, which is what SPEC.md lines 406-407 ask for.
    """

    roles: TheRolesOfAMachine

    kind = "machine_initialisation"
    confirmed_by = obligations.BY_NOTHING

    def to_show(self) -> str:
        return (
            f"the state the initialiser '{self.roles.init}' answers satisfies "
            f"the invariant '{self.roles.invariant}'"
        )

    def detail(self) -> dict:
        return {
            "machine_roles": self.roles.published(machine.INIT, machine.INVARIANT),
            "witness_replay": NO_REFUSAL_CONFIRMS_A_WITNESS,
        }

    def _claim(self, program: syntax.Program):
        return TheStateAMachineStartsIn(
            self.roles, program
        ).the_invariant_holds_of_it()


@dataclass(frozen=True)
class StepEnabledness(obligations.Obligation):
    """The step is defined for every event the machine admits in a state
    the invariant admits (SPEC.md line 399).

    The one of the three whose witness the replay gate of this tool can
    confirm: the step refusing its own precondition over the solution the
    solver found is exactly what this obligation denies, so it declares
    itself confirmed by a precondition and a confirmed solution is
    reported as the counterexample it is.
    """

    roles: TheRolesOfAMachine

    kind = "machine_step_enabledness"
    confirmed_by = obligations.BY_A_PRECONDITION

    def to_show(self) -> str:
        return (
            f"the step '{self.roles.step}' is defined -- its own precondition "
            f"holds -- in every state the invariant '{self.roles.invariant}' "
            f"admits, for every event '{self.roles.admissible}' admits there"
        )

    def detail(self) -> dict:
        return {
            "machine_roles": self.roles.published(
                machine.STEP, machine.INVARIANT, machine.ADMISSIBLE
            ),
            "shown_over": _over_every_typed_event(self.roles.event_type),
        }

    def _claim(self, program: syntax.Program):
        return AnAdmittedTransition(self.roles, program).the_step_is_defined()


@dataclass(frozen=True)
class Preservation(obligations.Obligation):
    """The invariant holds again of the state the step leads to
    (SPEC.md line 400).

    An invariant that is not inductive on its own is refuted here. The
    replay gate confirms no witness of it -- a step that answers a state
    outside the invariant refuses nothing -- so a solution the solver
    finds leaves this obligation unsettled with that reason rather than
    reported as broken, and nothing weaker than the invariant the
    descriptor names is ever shown in its place (SPEC.md lines 403-406).
    """

    roles: TheRolesOfAMachine

    kind = "machine_preservation"
    confirmed_by = obligations.BY_NOTHING

    def to_show(self) -> str:
        return (
            f"the state after the step '{self.roles.step}', read through "
            f"'{self.roles.state_of}', satisfies the invariant "
            f"'{self.roles.invariant}' again, in every state that invariant "
            f"admits and for every event '{self.roles.admissible}' admits "
            "there"
        )

    def detail(self) -> dict:
        return {
            "machine_roles": self.roles.published(
                machine.STEP,
                machine.STATE_OF,
                machine.INVARIANT,
                machine.ADMISSIBLE,
            ),
            "shown_over": _over_every_typed_event(self.roles.event_type),
            "witness_replay": NO_REFUSAL_CONFIRMS_A_WITNESS,
        }

    def _claim(self, program: syntax.Program):
        return AnAdmittedTransition(
            self.roles, program
        ).the_invariant_holds_after_it()


def the_obligations_of(
    resolved: machine.ResolvedMachine,
) -> tuple[obligations.Obligation, ...]:
    """The three obligations the machine `resolved` describes owes, in
    the order SPEC.md states them.

    The one place they are built, so no answer can carry a fourth, drop
    one or name one differently: a reader comparing two answers about one
    machine reads the same three entries.
    """
    roles = TheRolesOfAMachine.of(resolved)
    return (
        Initialisation(roles.init, _site(INITIALISATION), roles),
        StepEnabledness(roles.step, _site(STEP_ENABLEDNESS), roles),
        Preservation(roles.step, _site(PRESERVATION), roles),
    )


def _site(which: str) -> obligations.Site:
    return obligations.Site((MACHINE, which))


def _applied(name: str, arguments: tuple) -> syntax.Call:
    """A call to one of the role functions, as the program would write
    it: the translation of a call is the callee's body over its
    arguments, which is how a role reaches the solver at all."""
    return syntax.Call(name, tuple(arguments))


def _named(name: str) -> syntax.NameRef:
    return syntax.NameRef(name)
