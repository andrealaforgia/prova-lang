"""Running the examples a program declares, and what each one answered.

One place decides whether a declared example passes. Two operations
need that: the one the Owner asks to run the examples, and the one that
says whether a program was shown -- and a fact decided twice is a fact
that can be decided two ways.

Nothing here answers a request or writes a field of one. An example is
run through the reference semantics, exactly as `evaluate` runs a call,
and what came back is recorded. A run that cannot be finished -- because
the program nests deeper than this tool runs, or because a value it
answered has more digits than this tool writes -- stops where it stopped
and says so, carrying what it had already seen. The caller decides what
that is worth to it: the operation that was asked to run the examples
refuses, and the one that was asked about the obligations keeps its
inventory and counts the examples it never saw.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import evaluator, syntax
from prova.values import TooLargeToWrite, render


@dataclass(frozen=True)
class ExampleOutcome:
    """One declared example beside what running it answered.

    `answered` is the value the run came back with, written the way a
    program writes it, or nothing at all where the run was refused; in
    that case `refused_with` says what refused it. The two are never
    both there and never both absent.
    """

    function: str
    ordinal: int
    arguments: tuple[str, ...]
    expected: str
    answered: str | None
    passed: bool
    refused_with: str | None = None

    def published(self) -> dict:
        entry = {
            "function": self.function,
            "ordinal": self.ordinal,
            "arguments": list(self.arguments),
            "expected": self.expected,
            "actual": self.answered,
            "passed": self.passed,
        }
        if self.refused_with is not None:
            entry["reason"] = self.refused_with
        return entry


@dataclass(frozen=True)
class DeclaredExamples:
    """Every example one program declares, beside what running it did.

    Built by the two constructors below and nowhere else: a run either
    saw every declared example or says which refusal stopped it, and a
    caller cannot build a run that quietly saw fewer than it claims.
    """

    outcomes: tuple[ExampleOutcome, ...]
    declared: int
    stopped_by: object | None = None
    stopped_at: str | None = None

    @classmethod
    def finished(
        cls, outcomes: tuple[ExampleOutcome, ...], declared: int
    ) -> "DeclaredExamples":
        return cls(outcomes, declared)

    @classmethod
    def stopped(
        cls,
        outcomes: tuple[ExampleOutcome, ...],
        declared: int,
        refusal: object,
        function: str,
    ) -> "DeclaredExamples":
        return cls(outcomes, declared, stopped_by=refusal, stopped_at=function)

    def published(self) -> list:
        return [outcome.published() for outcome in self.outcomes]


def how_many_are_declared(program: syntax.Program) -> int:
    """How many examples the program declares, counted from the program
    itself rather than from any run of them: a run stopped part way is
    then seen to have left some unseen."""
    return sum(len(function.examples) for function in program.functions.values())


def run_declared(program: syntax.Program, run) -> DeclaredExamples:
    """Every example `program` declares, run in declaration order.

    The order of the work is the order it has always been in: the texts
    a reader will see are written first, then the run's own budget is
    checked, then the example is run. A refusal that is about the
    program -- a precondition or a postcondition the run meets -- is one
    example's outcome; a refusal that is about this tool's limits stops
    the whole run and is handed back to the caller.
    """
    declared = how_many_are_declared(program)
    seen: list[ExampleOutcome] = []
    for function in program.functions.values():
        try:
            for ordinal, example in enumerate(function.examples):
                written = tuple(render(argument) for argument in example.args)
                expected = render(example.expected)
                run.stop_if_exhausted()
                seen.append(
                    _answered(program, function, ordinal, example, written, expected)
                )
        except evaluator.EvaluationTooDeep as too_deep:
            return DeclaredExamples.stopped(
                tuple(seen), declared, too_deep, function.name
            )
        except TooLargeToWrite as too_large:
            return DeclaredExamples.stopped(
                tuple(seen), declared, too_large, function.name
            )
    return DeclaredExamples.finished(tuple(seen), declared)


def _answered(program, function, ordinal, example, written, expected) -> ExampleOutcome:
    try:
        answered = evaluator.call_function(function, example.args, program)
    except (
        evaluator.PreconditionViolation,
        evaluator.PostconditionViolation,
    ) as violation:
        return ExampleOutcome(
            function.name,
            ordinal,
            written,
            expected,
            None,
            False,
            refused_with=str(violation),
        )
    return ExampleOutcome(
        function.name,
        ordinal,
        written,
        expected,
        render(answered),
        evaluator.values_equal(answered, example.expected),
    )
