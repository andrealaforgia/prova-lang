"""What became of each obligation, and why a reader may believe it.

One place decides the three answers. A claim the translation covers goes
to the solver port; a claim it does not is unsettled with the reason; an
obligation a rule of `core-0` settles is answered from that rule and no
solver is asked about it at all.

SPEC.md, "Results and evidence scope": only a completed justified result
may be `proved`, and disproof requires a validated source-level witness
satisfying the claim's assumptions and violating its conclusion, which
must replay against the reference semantics -- a failed validation
yields unknown, not an invented disproof. So a solution the solver finds
is only ever a candidate here: it is written back as values of the
program and run through the evaluator, and only a refusal the evaluator
really makes turns it into a disproof.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import (
    encoding,
    evaluator,
    obligations,
    provenance,
    solving,
    syntax,
    witnesses,
)
from prova.reader import ReaderError, read_program
from prova.values import WRITTEN_DIGITS, TooLargeToWrite, render

# The four words a logical result may carry (SPEC.md lines 270-284).
# The last of them is read from the module that lists what a program
# owes, which has carried that word since before anything could settle
# one: two spellings of it would let an entry nothing attempted and an
# entry counted as attempted disagree.
PROVED = "proved"
DISPROVED = "disproved"
UNKNOWN = "unknown"
NOT_ATTEMPTED = obligations.NOT_ATTEMPTED

# What settled an obligation: a solver that was asked, or a rule of the
# profile that needs none.
BY_THE_SOLVER = "solver"
BY_A_RULE_OF_THE_PROFILE = "structure"

# What an attempt that finished says about itself, spelled as the word
# over the whole program spells it.
COMPLETED = "completed"

# Why the word is withheld from a claim that is valid only because
# nothing satisfies what it assumes, and from one whose domain could not
# be shown inhabited at all.
NOTHING_TO_RANGE_OVER = (
    "this obligation is valid for want of anything to range over: the solver "
    "answered that nothing at all satisfies what it assumes, so the statement "
    "holds over an empty domain and says nothing about the program. SPEC.md "
    "lines 406-407 forbid certifying a useful machine on an unsatisfiable "
    "required domain, so the word is withheld. Nothing here says the program "
    "is wrong: repair the conditions that leave the domain empty -- for a "
    "machine, an invariant and an admissibility predicate no state and event "
    "satisfy together -- and ask again"
)
COULD_NOT_TELL_WHETHER_IT_RANGES_OVER_ANYTHING = (
    "this obligation was not proved because it could not be shown to range "
    "over anything at all: a claim whose assumptions nothing satisfies is "
    "valid over an empty domain, and that question was not settled here, so "
    "the word is withheld (SPEC.md lines 406-407). What the attempt said:"
)

# What this tool says about the word it takes from the solver. One
# sentence, in one place, carried by every answer that asked one.
THE_TRUST_IT_DISCLOSES = (
    "Every obligation answered 'proved' by the solver is proved on the "
    "solver's word. This tool asks the solver whether the denial of the "
    "obligation has a solution and reports 'proved' when it answers that it "
    "has none. It keeps no proof certificate, runs no checking kernel of its "
    "own and does not check that answer again, so a defect in the solver or "
    "in the translation named beside it would reach you as a 'proved'. The "
    "obligations answered from a rule of core-0 instead carry 'structure' and "
    "rest on that rule, which is written out in the document this tool names."
)


@dataclass(frozen=True)
class TheRunCouldNotFinish:
    """A replay the reference semantics could not carry to the end: a
    value of the wrong shape for the types it was handed to, or a run
    that nested deeper than this tool runs.

    Kept apart from a run that finished and refuted nothing. Both leave
    an obligation unsettled when a candidate was being confirmed, but
    where nothing was being confirmed -- where the solver found nothing
    and the run is the whole evidence -- the difference is the
    difference between a proof and an unanswered question.
    """

    reason: str


@dataclass(frozen=True)
class ValidatedWitness:
    """An input the reference semantics really refuses.

    The only thing a disproof may carry. Built by `validated` below and
    nowhere else, so a candidate the solver found but the evaluator
    accepted can never be reported as a counterexample.
    """

    function: str
    arguments: tuple[str, ...]
    refused_with: str

    def because(self) -> str:
        """The reason the obligation carries beside the word
        'disproved'.

        Said by the witness and not by the finding, because what makes a
        disproof believable differs with the evidence: an input the
        program refuses is one thing, and a transition whose invariant
        fails afterwards is another. One sentence per kind of evidence,
        beside the kind that earned it.
        """
        return (
            "the solver found an input of the declared types that breaks "
            "this obligation, and running the program over that input "
            "refuses it for the same reason"
        )

    def published(self) -> dict:
        """The input, and the budget the run that confirmed it stood
        inside.

        SPEC.md: a function witness must replay against the reference
        semantics "within a declared replay budget". The run that
        confirms a candidate is bounded by the one limit this tool
        declares on how far a run may nest, and a reader looking at a
        counterexample is told which that was and what it allowed --
        otherwise they cannot tell a confirmation that finished from one
        that was cut short. The number is read from the limit itself, so
        the answer and the manifest cannot say two different things.
        """
        return {
            "function": self.function,
            "arguments": list(self.arguments),
            "refused_when_run": self.refused_with,
            "replayed_within": {
                "limit": evaluator.EVALUATION_LIMIT.name,
                "maximum": evaluator.EVALUATION_LIMIT.maximum,
            },
        }


@dataclass(frozen=True)
class Finding:
    """What became of one obligation: where it stands as a statement,
    what happened to the attempt, and what that rests on.

    Built only by the five constructors below, each of which fixes both
    words together. A caller cannot pair a logical result with an
    execution status of its own, so `proved` beside a timed-out attempt,
    or an unsettled entry with no reason, cannot be built at all.
    """

    result: str
    execution_status: str
    reason: str | None = None
    discharged_by: str | None = None
    rule: str | None = None
    witness: object = None

    @classmethod
    def proved_by_the_solver(cls) -> "Finding":
        return cls(PROVED, "completed", discharged_by=BY_THE_SOLVER)

    @classmethod
    def proved_by_a_rule(cls, rule: str) -> "Finding":
        return cls(
            PROVED,
            "completed",
            rule=rule,
            discharged_by=BY_A_RULE_OF_THE_PROFILE,
        )

    @classmethod
    def disproved_with(cls, witness) -> "Finding":
        """The word 'disproved' with the witness that earned it and the
        reason that witness gives.

        Any confirmed witness may stand here: the two owners that build
        one have each run the reference semantics, and each says in its
        own words what it ran. The finding keeps no sentence of its own,
        so a kind of evidence cannot be reported under another kind's
        reason.
        """
        return cls(DISPROVED, "completed", reason=witness.because(), witness=witness)

    @classmethod
    def unknown_because(cls, reason: str, execution_status: str) -> "Finding":
        return cls(UNKNOWN, execution_status, reason=reason)

    @classmethod
    def not_attempted_because(cls, reason: str) -> "Finding":
        return cls(NOT_ATTEMPTED, "unsupported", reason=reason)

    def written_into(self, entry: dict) -> None:
        entry["result"] = self.result
        entry["execution_status"] = self.execution_status
        if self.reason is not None:
            entry["reason"] = self.reason
        if self.discharged_by is not None:
            entry["discharged_by"] = self.discharged_by
        if self.rule is not None:
            entry["rule"] = self.rule
        if self.witness is not None:
            entry["counterexample"] = self.witness.published()


@dataclass(frozen=True)
class Settlement:
    """Every obligation of one program beside what became of it, and the
    solver that stands behind the answer."""

    findings: dict
    standing: object

    def inventory_of(self, inventory: obligations.Inventory) -> dict:
        return inventory.as_dict(self.findings)

    def disclosure(self) -> dict | None:
        """What a reader is told about the word this answer takes from
        the solver, or nothing at all when no solver was asked."""
        named = self.standing.text()
        if named is None:
            return None
        return {
            "trusted_from": "solver",
            "solver": named,
            "encoding": f"core-0-to-smt {encoding.VERSION}",
            "rechecked_by_this_tool": False,
            "statement": THE_TRUST_IT_DISCLOSES,
        }


class Discharge:
    """The obligations of one program, settled one at a time.

    Holds the program, the solver port it asks and the run whose time
    budget bounds every question. It keeps no answer between obligations:
    each one is settled from its own claim.
    """

    def __init__(self, program: syntax.Program, solver, run):
        self._program = program
        self._solver = solver
        self._run = run
        self._asked_a_solver = False

    def settle(self, inventory: obligations.Inventory) -> Settlement:
        """Every obligation of the inventory beside what became of it.

        An obligation settled from others is settled after them, in a
        second round over the same list: it is listed where it was
        listed and reported in the same place, and the fact it shares
        with them is decided once.
        """
        findings = {}
        settled_from_others = []
        for obligation in inventory.obligations:
            self._run.stop_if_exhausted()
            if obligation.rests_on():
                settled_from_others.append(obligation)
                continue
            findings[obligation.identity] = self._finding_for(obligation)
        for obligation in settled_from_others:
            self._run.stop_if_exhausted()
            findings[obligation.identity] = self._from_what_it_rests_on(
                obligation, findings
            )
        return Settlement(findings, self._what_it_stands_on())

    def _from_what_it_rests_on(self, obligation, findings: dict) -> Finding:
        """What became of an obligation whose answer is the answer to
        others.

        It is settled where every one of them was settled proved, broken
        where one of them was broken -- the input that breaks the other
        breaks this one, and the same confirmed witness says so -- and
        unsettled while any of them is, naming the ones that are. A
        reader is never told that a contract is defined everywhere while
        a call inside it is reported unsettled or broken two lines
        below.
        """
        resting = [findings[name] for name in obligation.rests_on()]
        broken = [finding for finding in resting if finding.result == DISPROVED]
        if broken:
            return Finding.disproved_with(broken[0].witness)
        unsettled = [
            name
            for name, finding in zip(obligation.rests_on(), resting)
            if finding.result != PROVED
        ]
        if unsettled:
            return Finding.unknown_because(
                "this obligation is settled from the calls the contract "
                f"makes, and {', '.join(unsettled)} "
                + ("is" if len(unsettled) == 1 else "are")
                + " not settled: a contract whose own calls were not shown "
                "to be met cannot be said to be defined for every input, so "
                "the word is withheld rather than taken from the totality of "
                "the primitives alone. Nothing here says the contract is "
                "wrong: settle those entries and ask again",
                COMPLETED,
            )
        return self._finding_for(obligation)

    def _finding_for(self, obligation) -> Finding:
        stated = obligation.claim_in(self._program)
        if isinstance(stated, encoding.ByRuleOfTheProfile):
            return Finding.proved_by_a_rule(stated.rule)
        if isinstance(stated, encoding.OutsideTheFragment):
            return Finding.unknown_because(
                f"this obligation was not put to the solver: {stated.reason}",
                "unsupported",
            )
        return self._asked_about(obligation, stated)

    def _asked_about(self, obligation, claim: encoding.Claim) -> Finding:
        self._asked_a_solver = True
        verdict = self._solver.asked(claim, self._run.milliseconds_left())
        if isinstance(verdict, solving.Unrefutable):
            return self._unless_a_run_refutes_it(
                obligation, claim, self._if_it_ranges_over_anything(obligation)
            )
        if isinstance(verdict, solving.SolverUnavailable):
            return Finding.unknown_because(verdict.reason, "tool_failure")
        if isinstance(verdict, solving.Undecided):
            return Finding.unknown_because(
                verdict.reason, verdict.execution_status
            )
        return self._candidate(obligation, claim, verdict)

    def _unless_a_run_refutes_it(self, obligation, claim, taken: Finding) -> Finding:
        """The word the solver's silence would earn, withheld where a run
        of the program says otherwise.

        An obligation whose input is written in the program itself --
        a declared example -- is about one run and no range of inputs,
        so the reference semantics decides it outright and the solver's
        word is not the last one. The formula the solver is asked reads
        the bodies of the functions a call reaches and not the contracts
        they keep, so it can be valid while the run it is about is
        refused by a precondition inside it, or ends in the function
        breaking its own promise. SPEC.md lines 307-309 make the
        reference semantics the authority, so the run is made and its
        answer stands: it confirms the word, breaks it with the refusal
        it really met, or leaves the obligation unsettled when it could
        not be carried to the end.

        Every other kind ranges over inputs no single run exhausts, and
        nothing is run for it here.
        """
        if taken.result != PROVED or not obligation.settled_by_running:
            return taken
        said = self._validated(obligation, claim, None)
        if isinstance(said, witnesses.EvidenceTooLargeToWrite):
            return Finding.unknown_because(said.because(), COMPLETED)
        if isinstance(said, TheRunCouldNotFinish):
            return Finding.unknown_because(
                "nothing the solver found refutes this obligation, and "
                f"running the program over the input it is about {said.reason}. "
                "What this obligation states is about that one run, so it is "
                "left unsettled rather than proved from a formula no run "
                "confirmed",
                COMPLETED,
            )
        if said is not None:
            return Finding.disproved_with(said)
        return taken

    def _if_it_ranges_over_anything(self, obligation) -> Finding:
        """Proved, where the obligation ranges over something; unsettled
        with its reason, where nothing satisfies what it assumes or the
        solver could not tell.

        A claim whose assumptions are contradictory is valid for want of
        anything to range over, and that is no statement about the
        program. SPEC.md lines 406-407 forbid certifying a useful machine
        on an unsatisfiable required domain, so the word is withheld
        here rather than taken from an empty domain -- and withheld,
        not turned into a disproof: nothing about the program was shown
        to be wrong.
        """
        asked = obligation.nothing_satisfies_it_in(self._program)
        if asked is None:
            return Finding.proved_by_the_solver()
        if isinstance(asked, encoding.OutsideTheFragment):
            return self._could_not_tell(asked.reason, "unsupported")
        answer = self._solver.asked(asked, self._run.milliseconds_left())
        if isinstance(answer, solving.Refuted):
            return Finding.proved_by_the_solver()
        if isinstance(answer, solving.Unrefutable):
            return Finding.unknown_because(NOTHING_TO_RANGE_OVER, COMPLETED)
        return self._could_not_tell(
            answer.reason, getattr(answer, "execution_status", COMPLETED)
        )

    @staticmethod
    def _could_not_tell(reason: str, execution_status: str) -> Finding:
        """The obligation left unsettled because whether it ranges over
        anything was not settled, whatever stopped that question.

        One place composes that reason, so the two ways the question can
        go unanswered -- a construct the translation does not cover and a
        solver that could not tell -- say the same thing about the word
        being withheld and differ only in what they report of the
        attempt.
        """
        return Finding.unknown_because(
            f"{COULD_NOT_TELL_WHETHER_IT_RANGES_OVER_ANYTHING} {reason}",
            execution_status,
        )

    def _candidate(self, obligation, claim, refuted: solving.Refuted) -> Finding:
        """A solution the solver found, which is a counterexample only if
        the reference semantics refuses it."""
        confirmed = self._validated(obligation, claim, refuted)
        if isinstance(confirmed, witnesses.EvidenceTooLargeToWrite):
            return Finding.unknown_because(confirmed.because(), COMPLETED)
        if confirmed is not None and not isinstance(confirmed, TheRunCouldNotFinish):
            return Finding.disproved_with(confirmed)
        return Finding.unknown_because(
            "the solver found an input where the denial of this obligation "
            "has a solution, and running the program over that input is not "
            "refused for it. A witness that does not replay against the "
            "reference semantics is not a counterexample, so this obligation "
            "is left unsettled rather than reported as broken",
            "completed",
        )

    def _validated(self, obligation, claim, refuted):
        """The witness this obligation's own replay confirms, the evidence
        it established and this tool will not write, or `None`.

        Every way of confirming a candidate ends in writing the evidence
        back as the characters a reader sees, and the reference semantics
        can compute a number longer than this tool writes. That is read
        here, in the one place every confirmation passes through, because
        letting it out would end the operation and lose the inventory the
        reader asked for -- and because an obligation whose evidence
        cannot be shown is unsettled, not broken.
        """
        try:
            return self._confirmed(obligation, claim, refuted)
        except TooLargeToWrite as too_large:
            return witnesses.EvidenceTooLargeToWrite(
                "the evidence that breaks this obligation",
                WRITTEN_DIGITS.name,
                too_large.reached,
                too_large.limit,
            )

    def _confirmed(self, obligation, claim, refuted):
        function = self._program.functions[obligation.function]
        supplied = self._arguments(obligation, claim, refuted, function)
        if supplied is None:
            return TheRunCouldNotFinish(
                "could not be written back as values of the program to run it "
                "over"
            )
        texts, args = supplied
        if obligation.confirmed_by == obligations.BY_THE_INVARIANT_AFTER_THE_STEP:
            return obligation.confirmed_by_replaying(
                self._program, claim, texts, args
            )
        try:
            for argument, parameter in zip(args, function.signature.params):
                evaluator.check_value_type(
                    argument, parameter.type_name, self._program, "argument"
                )
            answered = evaluator.call_function(function, args, self._program)
        except evaluator.PreconditionViolation as refusal:
            return self._if_confirmed(
                obligation, obligations.BY_A_PRECONDITION, texts, refusal
            )
        except evaluator.PostconditionViolation as refusal:
            return self._if_confirmed(
                obligation, obligations.BY_A_POSTCONDITION, texts, refusal
            )
        except (
            evaluator.EvaluationTooDeep,
            evaluator.MalformedValue,
            evaluator.IllTypedValue,
        ) as stopped:
            return TheRunCouldNotFinish(f"could not be carried to the end: {stopped}")
        return self._if_answered_another_value(obligation, texts, answered)

    def _if_confirmed(
        self, obligation, refusal_kind: str, texts: tuple, refusal
    ) -> ValidatedWitness | None:
        """The refusal as a witness, where it is the refusal this
        obligation denies.

        A declared example is confirmed by any refusal at all: it states
        that running the function over its own arguments answers a
        value, so a run refused anywhere inside is already not that.
        Every other kind denies one function's refusal -- the callee of
        the call, the function whose promise is in question -- and a
        refusal made by anything else means the run never reached what
        this obligation is about. Reading it as a confirmation would
        report a counterexample that does not get there.
        """
        if obligation.confirmed_by == obligations.BY_THE_EXAMPLE_ITSELF:
            return ValidatedWitness(obligation.function, texts, str(refusal))
        if obligation.confirmed_by != refusal_kind:
            return None
        if refusal.function_name != obligation.whose_refusal_confirms_it:
            return None
        return ValidatedWitness(obligation.function, texts, str(refusal))

    def _if_answered_another_value(
        self, obligation, texts: tuple, answered: object
    ) -> ValidatedWitness | None:
        if obligation.confirmed_by != obligations.BY_THE_EXAMPLE_ITSELF:
            return None
        if evaluator.values_equal(answered, obligation.example.expected):
            return None
        return ValidatedWitness(
            obligation.function,
            texts,
            f"the function answers {render(answered)} and the example states "
            f"{render(obligation.example.expected)}",
        )

    def _arguments(self, obligation, claim, refuted, function):
        """The input to replay, as the texts a reader sees and as the
        values the evaluator takes.

        A claim about no variable at all -- a declared example -- is
        replayed over the example's own arguments; every other claim is
        replayed over the solution the solver found.

        A function that takes nothing is replayed over the empty tuple,
        which is the whole of its input: a solution naming no variable
        is the solution for it, and reading "no names" as "nothing to
        run" would throw away the one witness such a function can have.
        A claim whose variables are not the parameters of the function
        is not one this replay can run at all.
        """
        if obligation.confirmed_by == obligations.BY_THE_EXAMPLE_ITSELF:
            values = tuple(obligation.example.args)
            return tuple(render(value) for value in values), values
        names = tuple(name for name, _ in claim.variables)
        if len(names) != len(function.signature.params):
            return None
        texts = refuted.arguments(names)
        try:
            return texts, tuple(self._value_of(text) for text in texts)
        except (ReaderError, syntax.SyntaxError_):
            return None

    def _value_of(self, text: str) -> object:
        forms = read_program(text)
        if len(forms) != 1:
            raise ReaderError(f"expected one value, got {len(forms)}", 1, 1)
        return syntax.parse_value(forms[0])

    def _what_it_stands_on(self):
        if not self._asked_a_solver:
            return provenance.SolverStanding.asked_none(
                "this answer put no obligation to a solver: every one of them "
                "was settled by a rule of core-0, or was outside what this "
                "tool translates"
            )
        version = self._solver.version()
        if isinstance(version, solving.SolverUnavailable):
            return provenance.SolverStanding.asked_none(
                "this answer needed a solver and could not load one, so every "
                "obligation that needed it is unsettled with that reason"
            )
        return provenance.SolverStanding.asked(self._solver.name(), version)
