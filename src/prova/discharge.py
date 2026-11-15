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

from prova import encoding, evaluator, obligations, provenance, solving, syntax
from prova.reader import ReaderError, read_program
from prova.values import render

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
class ValidatedWitness:
    """An input the reference semantics really refuses.

    The only thing a disproof may carry. Built by `validated` below and
    nowhere else, so a candidate the solver found but the evaluator
    accepted can never be reported as a counterexample.
    """

    function: str
    arguments: tuple[str, ...]
    refused_with: str

    def published(self) -> dict:
        return {
            "function": self.function,
            "arguments": list(self.arguments),
            "refused_when_run": self.refused_with,
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
    witness: ValidatedWitness | None = None

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
    def disproved_with(cls, witness: ValidatedWitness) -> "Finding":
        return cls(
            DISPROVED,
            "completed",
            reason=(
                "the solver found an input of the declared types that breaks "
                "this obligation, and running the program over that input "
                "refuses it for the same reason"
            ),
            witness=witness,
        )

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
        findings = {}
        for obligation in inventory.obligations:
            self._run.stop_if_exhausted()
            findings[obligation.identity] = self._finding_for(obligation)
        return Settlement(findings, self._what_it_stands_on())

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
            return Finding.proved_by_the_solver()
        if isinstance(verdict, solving.SolverUnavailable):
            return Finding.unknown_because(verdict.reason, "tool_failure")
        if isinstance(verdict, solving.Undecided):
            return Finding.unknown_because(
                verdict.reason, verdict.execution_status
            )
        return self._candidate(obligation, claim, verdict)

    def _candidate(self, obligation, claim, refuted: solving.Refuted) -> Finding:
        """A solution the solver found, which is a counterexample only if
        the reference semantics refuses it."""
        confirmed = self._validated(obligation, claim, refuted)
        if confirmed is not None:
            return Finding.disproved_with(confirmed)
        return Finding.unknown_because(
            "the solver found an input where the denial of this obligation "
            "has a solution, and running the program over that input is not "
            "refused for it. A witness that does not replay against the "
            "reference semantics is not a counterexample, so this obligation "
            "is left unsettled rather than reported as broken",
            "completed",
        )

    def _validated(self, obligation, claim, refuted) -> ValidatedWitness | None:
        function = self._program.functions[obligation.function]
        supplied = self._arguments(obligation, claim, refuted, function)
        if supplied is None:
            return None
        texts, args = supplied
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
        ):
            return None
        return self._if_answered_another_value(obligation, texts, answered)

    def _if_confirmed(
        self, obligation, refusal_kind: str, texts: tuple, refusal
    ) -> ValidatedWitness | None:
        if obligation.confirmed_by in (
            refusal_kind,
            obligations.BY_THE_EXAMPLE_ITSELF,
        ):
            return ValidatedWitness(obligation.function, texts, str(refusal))
        return None

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
        """
        if obligation.confirmed_by == obligations.BY_THE_EXAMPLE_ITSELF:
            values = tuple(obligation.example.args)
            return tuple(render(value) for value in values), values
        names = tuple(name for name, _ in claim.variables)
        if not names:
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
