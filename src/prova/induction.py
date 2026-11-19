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

from prova import encoding, machine, obligations, provenance, replay, syntax
from prova.values import render

# Where the obligations of a machine stand. A site is a structural path,
# never a line number, so these three identities are the same for any
# program the same descriptor is read against.
MACHINE = "machine"
INITIALISATION = "initialisation"
STEP_ENABLEDNESS = "step-enabledness"
PRESERVATION = "preservation"

# Where the two things an answer says about a machine beside its roles
# stand. Named here because this module composes that answer.
CONTRACTS_THE_PROOFS_REST_ON = "contracts_the_proofs_rest_on"
REACHABLE_COUNTEREXAMPLE = "reachable_counterexample"


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


# What a solution the solver finds can and cannot become, said beside
# the obligation it was found for. Two obligations of a machine answer
# this differently, so each says its own sentence rather than sharing one
# that has to hedge.
#
# The initialisation obligation is about no variable at all: the
# initialiser takes nothing, so there is no solution to read and nothing
# to replay, whatever this obligation declared.
NOTHING_IS_THERE_TO_REPLAY = (
    "no solution the solver finds for the denial of this obligation can be "
    "replayed: the claim is about no variable at all, because the "
    "initialiser takes nothing, so there is no input to run the program "
    "over. An obligation the solver refutes here is reported as unsettled "
    "with that reason and not as a counterexample, and no weaker condition "
    "is put in the invariant's place"
)

# The preservation obligation is about an admitted transition, and the
# whole of that transition can be run. A pair the solver finds refuses
# nothing by itself -- the step answers a state, and the state is simply
# outside the invariant -- so the obligation runs the three roles its
# claim composes and reads what each answered.
THE_REPLAY_THAT_CONFIRMS_A_STEP_WITNESS = (
    "a pair the solver finds for the denial of this obligation is confirmed "
    "by replaying the whole transition: the invariant is run on the state, "
    "the admissibility predicate is run on the state and the event, the "
    "body of the step is run over the pair and the invariant is run again "
    "on the state the projection reads from what it answered. Only the "
    "first two answering true and the last answering false confirm the "
    "pair, and then it is reported as the counterexample it is, named an "
    "induction-step witness and never a reachable trace. Any other outcome "
    "-- a run the budget stopped, a value of the wrong type, a call the "
    "program refuses, or an invariant that holds after all -- confirms "
    "nothing, and the obligation is left unsettled with that reason rather "
    "than reported as broken; no weaker condition is put in the "
    "invariant\'s place (SPEC.md lines 307-309, 403-406)"
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

    def nothing_satisfies_it(self) -> encoding.Claim:
        """The claim that no state and event satisfy the invariant and
        the admissibility predicate together.

        It is the two assumptions with `false` to be shown, so a solver
        that finds no solution for its denial is saying exactly that
        nothing satisfies them: the machine then has no transition to
        reason about, and the two obligations written over this pair hold
        for an empty domain (SPEC.md lines 406-407). Asked through the
        one port the obligations are asked through, so no second notion
        of a solver lives here.
        """
        return self._claim(encoding.Term.falsity())

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

    That the word 'disproved' can never be reported for it is structural
    and not a choice of this class: a claim with no variable has no
    solution to read, so the replay gate has nothing to run and cannot
    confirm a witness whatever this obligation declares. It assumes
    nothing either, so it cannot hold over an empty domain and asks no
    question about one.
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
            "witness_replay": NOTHING_IS_THERE_TO_REPLAY,
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

    def nothing_satisfies_it_in(self, program: syntax.Program):
        return _nothing_admits_a_transition_in(self.roles, program)


@dataclass(frozen=True)
class Preservation(obligations.Obligation):
    """The invariant holds again of the state the step leads to
    (SPEC.md line 400).

    An invariant that is not inductive on its own is refuted here, and
    this is the obligation whose witness nothing refuses: a step that
    answers a state outside the invariant breaks no contract of its own.
    So the pair is confirmed by replaying the whole transition instead --
    the invariant of the state, the event admissible there, the step over
    the pair and the invariant of the state it leads to -- and a pair the
    reference semantics confirms that way is reported as the
    counterexample it is. A pair it does not confirm leaves the
    obligation unsettled with that reason, and nothing weaker than the
    invariant the descriptor names is ever shown in its place (SPEC.md
    lines 307-309, 403-406).

    Its witness is an induction-step witness and says so: one step out of
    the invariant is what it shows, and nothing here says a run of the
    machine reaches the state it names.
    """

    roles: TheRolesOfAMachine

    kind = "machine_preservation"
    confirmed_by = obligations.BY_THE_INVARIANT_AFTER_THE_STEP

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
            "witness_replay": THE_REPLAY_THAT_CONFIRMS_A_STEP_WITNESS,
        }

    def _claim(self, program: syntax.Program):
        return AnAdmittedTransition(
            self.roles, program
        ).the_invariant_holds_after_it()

    def nothing_satisfies_it_in(self, program: syntax.Program):
        return _nothing_admits_a_transition_in(self.roles, program)

    def confirmed_by_replaying(self, program: syntax.Program, claim, texts, args):
        """The witness the machine's own functions confirm for the
        solution the solver found, or `None` when they confirm none.

        The claim's variables are the parameters the step declares, so
        which of them is the state and which the event is read from the
        step itself rather than from the order a solution happened to
        arrive in.
        """
        step = program.functions.get(self.roles.step)
        if step is None or len(step.signature.params) != 2:
            return None
        named = {name: value for (name, _), value in zip(claim.variables, args)}
        written = {name: text for (name, _), text in zip(claim.variables, texts)}
        state, event = (parameter.name for parameter in step.signature.params)
        if state not in named or event not in named:
            return None
        return replay.TheTransition(self.roles, program).confirmed_witness(
            (written[state], written[event]), (named[state], named[event])
        )


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


# What a reader of a machine answer is told about the contracts its
# proofs rest on, and what SPEC.md lines 313-318 refuse to call an
# implementation repair. Published beside the digest and in the manifest,
# from this one place.
THE_REQUIREMENT_INTEGRITY_RULE = (
    "Every proof above is a proof over the contracts these functions state "
    "now: their signatures, their preconditions, their guarantees and their "
    "declared examples. A proof over a changed contract certifies the "
    "changed contract and nothing else. SPEC.md lines 313-316: weakening a "
    "guarantee, strengthening a precondition or deleting an example cannot "
    "count as an implementation repair under the unchanged claim version, so "
    "a run whose digest below differs from an earlier run's has changed what "
    "is required of this machine and must be read as a requirement change "
    "and not as a repair. The digest covers no body: two runs over the same "
    "contracts carry the same digest however their bodies differ, which is "
    "what makes a moved digest mean something. This tool compares nothing "
    "for you and keeps no earlier run: it states what this one rests on."
)


@dataclass(frozen=True)
class TheContractsTheProofsRestOn:
    """The requirement surface the obligations of one machine were
    settled over, as one digest.

    The signature, the preconditions, the guarantees and the declared
    examples of the five functions the descriptor's roles name -- and no
    body, so that the digest moves when and only when what is required
    of the machine moves. An Owner comparing two runs then reads one
    thing: the same digest means the same requirements, and a different
    digest means a requirement change, whatever the answer says about the
    bodies.

    The hashing itself belongs to `provenance.Digest`, which this asks,
    so a client recomputing it reads the one algorithm this tool
    publishes.
    """

    roles: TheRolesOfAMachine
    program: syntax.Program

    def published(self) -> dict:
        return {
            "digest": provenance.Digest.of(self._written()).rendered(),
            "covers": self.roles.published(
                machine.INIT,
                machine.STEP,
                machine.STATE_OF,
                machine.ADMISSIBLE,
                machine.INVARIANT,
            ),
            "what_is_covered": (
                "the signature, the preconditions, the guarantees and the "
                "declared examples of each function named above, in the "
                "order the roles are named, and no body"
            ),
            "what_this_says": THE_REQUIREMENT_INTEGRITY_RULE,
        }

    def _written(self) -> str:
        """The requirement surface as one text, written the way the
        program writes it.

        Built from the parsed program rather than from the characters
        submitted, so that reformatting a contract, renaming nothing and
        moving a clause's whitespace leave the digest where it is, while
        deleting a clause or an example moves it.
        """
        return "\n".join(
            self._contract_of(role, named)
            for role, named in sorted(self._named().items())
        )

    def _named(self) -> dict:
        return self.roles.published(
            machine.INIT,
            machine.STEP,
            machine.STATE_OF,
            machine.ADMISSIBLE,
            machine.INVARIANT,
        )

    def _contract_of(self, role: str, named: str) -> str:
        function = self.program.functions.get(named)
        if function is None:
            return f"{role}={named}:absent"
        parameters = " ".join(
            f"({parameter.name} {parameter.type_name})"
            for parameter in function.signature.params
        )
        parts = [
            f"{role}={named}",
            f"sig=({parameters}) -> {function.signature.return_type}",
            "requires="
            + ";".join(obligations.text_of(clause) for clause in function.requires),
            "ensures="
            + ";".join(obligations.text_of(clause) for clause in function.ensures),
            "examples="
            + ";".join(
                "(" + " ".join(render(argument) for argument in declared.args) + ")=>"
                + render(declared.expected)
                for declared in function.examples
            ),
        ]
        return "|".join(parts)


def the_machine_answer(resolved: machine.ResolvedMachine, program: syntax.Program) -> dict:
    """What an answer says about the machine whose obligations it
    settled.

    The roles and the assumptions the descriptor states, which the
    witness of the descriptor owns; the contracts the proofs rest on,
    which this module owns because the proofs are the obligations it
    builds; and the trace the machine's own declared transitions reach
    from its initial state, where there is one. The last is absent rather
    than present and empty: an answer that carried a reachable
    counterexample saying none was found would read as a claim about
    every run, and this tool searched nothing.
    """
    roles = TheRolesOfAMachine.of(resolved)
    said = dict(resolved.published_beside_its_obligations())
    said[CONTRACTS_THE_PROOFS_REST_ON] = TheContractsTheProofsRestOn(
        roles, program
    ).published()
    trace = replay.ATraceFromTheInitialState(roles, program).built()
    if trace is not None:
        said[REACHABLE_COUNTEREXAMPLE] = trace.published()
    return said


def _nothing_admits_a_transition_in(
    roles: TheRolesOfAMachine, program: syntax.Program
):
    """The claim that no state and event of this machine satisfy the
    invariant and the admissibility predicate together, or the reason
    this translation could not state it.

    Both obligations written over an admitted transition answer this one
    question, in the one place it is stated: they range over the same
    pair, so a domain empty for one is empty for the other.
    """
    return encoding.attempted(
        lambda: AnAdmittedTransition(roles, program).nothing_satisfies_it()
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
