"""The four budgets every operation of this tool runs under: how large a
source it reads, how long one run may take, how much memory one run may
take, and how large an answer may be.

SPEC.md lines 503-508 ask for declared input, time, memory and output
budgets with controlled failure on exhaustion, observable and part of
the evidence, and forbid a limit quietly becoming a rule about what a
program may mean. The numbers are the Owner's (docs/ROADMAP.md section
5, D5, approved in section 8): 1 MiB of source, 10 s, 512 MiB of memory
and 1 MiB of answer.

This module owns the four numbers and nothing else: it knows no
operation name, reads no request and writes no answer. It says which
budget was passed, what it allowed and what was reached; the dispatcher
turns that into the answer a caller reads. The two limits this tool had
before -- how deeply a text nests, how far a run stands inside itself --
stay with the reader and the evaluator that count them.
"""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from typing import ClassVar

try:  # every platform this tool is run on has it; Windows does not.
    import resource as _rusage
except ImportError:  # pragma: no cover - not reached on macOS or Linux
    _rusage = None

# The category of the refusal each budget answers with. One per budget,
# because a caller handling a source that was too large does something
# different from a caller whose run ran out of time, and neither should
# have to read the sentence to tell them apart.
INPUT_BUDGET_EXCEEDED = "input_budget_exceeded"
TIME_BUDGET_EXCEEDED = "time_budget_exceeded"
MEMORY_BUDGET_EXCEEDED = "memory_budget_exceeded"
OUTPUT_BUDGET_EXCEEDED = "output_budget_exceeded"

BUDGET_CATEGORIES = (
    INPUT_BUDGET_EXCEEDED,
    TIME_BUDGET_EXCEEDED,
    MEMORY_BUDGET_EXCEEDED,
    OUTPUT_BUDGET_EXCEEDED,
)

# What a caller writes in its environment to lower one budget for one
# run. The manifest states this spelling beside every budget, so a
# caller never has to guess it.
LOWERED_WITH = "PROVA_BUDGET_"

# Why every number here is a number someone chose rather than one this
# tool measured. Read by a caller deciding how much to trust it.
DECLARED = "declared"


@dataclass(frozen=True)
class PeakMemory:
    """The greatest memory this process has taken, in bytes.

    A run is measured against the memory budget by asking the operating
    system what this process has already taken, which costs one call and
    nothing else. Where the platform cannot say, it says so rather than
    guessing: a budget nobody can measure is never reported as kept.
    """

    bytes_taken: int

    # The same number is reported in bytes on macOS and in kibibytes on
    # Linux. One conversion, in the one place that reads it.
    _TO_BYTES: ClassVar[int] = 1 if sys.platform == "darwin" else 1024

    @classmethod
    def readable(cls) -> bool:
        """Whether this platform reports the memory a process has taken."""
        return _rusage is not None

    @classmethod
    def taken_so_far(cls) -> "PeakMemory | None":
        if _rusage is None:  # pragma: no cover - not reached on macOS or Linux
            return None
        return cls(_rusage.getrusage(_rusage.RUSAGE_SELF).ru_maxrss * cls._TO_BYTES)


@dataclass(frozen=True)
class Exhaustion:
    """Which budget a run passed, what that budget allowed, how much was
    reached, and the sentence that says so.

    It holds nothing else. There is no field for a claim, a result or
    the revision of a source, so an answer about a run this tool stopped
    cannot appear to report on the program it was given.
    """

    budget: str
    maximum: int
    reached: int
    category: str
    message: str


class BudgetExhausted(Exception):
    """Raised where a run meets a budget, caught once where the answer
    is built.

    Carried as an exception for the same reason a text that nests too
    deep is: the stages of an operation are written to answer about a
    program, and threading a second kind of answer back through every
    one of them would put the budget in the way of every line of work
    this tool does.
    """

    def __init__(self, exhaustion: Exhaustion):
        super().__init__(exhaustion.message)
        self.exhaustion = exhaustion


@dataclass(frozen=True)
class Budget:
    """One number this tool declares, under the name a caller reads it
    by.

    The one object the manifest states and the run is measured against,
    so what a caller is promised and what the tool enforces cannot drift
    apart. A budget is passed when the amount taken is past the maximum;
    reaching the maximum exactly is inside it.
    """

    maximum: int

    name: ClassVar[str]
    unit: ClassVar[str]
    category: ClassVar[str]
    observed: ClassVar[str]

    def passed_by(self, amount: int) -> bool:
        return amount > self.maximum

    def exhausted_by(self, amount: int) -> "Exhaustion | None":
        if not self.passed_by(amount):
            return None
        return Exhaustion(
            self.name, self.maximum, amount, self.category, self.refusal(amount)
        )

    def enforced(self) -> bool:
        return True

    def lowered_with(self) -> str:
        return LOWERED_WITH + self.name.upper()

    def lowered_to(self, written: str) -> "Budget | UnreadableBudget":
        """This budget written down to `written`, or the reason that
        text cannot be read as a budget.

        Only downwards: the number this tool declares is the most it
        answers for, and a caller that could raise it would be given a
        promise the tool never made.
        """
        if not written.strip().isdigit():
            return UnreadableBudget(
                self.lowered_with(),
                f"the budget written in {self.lowered_with()} is "
                f"{written!r}, which is not a whole number of "
                f"{self.unit}: this tool reads one whole number from that "
                "variable and would otherwise run under a budget the caller "
                f"did not choose; write it as a whole number no larger than "
                f"{self.maximum}, as {max(1, self.maximum // 2)}, or leave "
                "the variable unset to run under the number this tool "
                "declares",
            )
        asked = int(written.strip())
        if asked > self.maximum:
            return UnreadableBudget(
                self.lowered_with(),
                f"the budget written in {self.lowered_with()} is {asked}, "
                f"above the {self.maximum} {self.unit} this tool declares "
                f"for {self.name!r}: a caller may lower a budget for its own "
                "run and may not raise the one this tool answers for; write "
                f"a number no larger than {self.maximum}, or leave the "
                "variable unset",
            )
        return type(self)(asked)

    def published(self, status: str) -> dict:
        """What a caller reads about this budget before it sends work."""
        return {
            "maximum": self.maximum,
            "unit": self.unit,
            "status": status,
            "category": self.category,
            "enforced": self.enforced(),
            "basis": DECLARED,
            "observed": self.observed,
            "lower_with": self.lowered_with(),
            "reason": self.reason(),
        }

    def reason(self) -> str:  # pragma: no cover - every budget writes its own
        raise NotImplementedError

    def refusal(self, amount: int) -> str:  # pragma: no cover - likewise
        raise NotImplementedError


@dataclass(frozen=True)
class InputBudget(Budget):
    """How large a source this tool reads, counted in bytes of the text
    a request carries."""

    name: ClassVar[str] = "input_size"
    unit: ClassVar[str] = "bytes of the source a request carries"
    category: ClassVar[str] = INPUT_BUDGET_EXCEEDED
    observed: ClassVar[str] = (
        "the size of the source a request carries, before any rule of the "
        "language is read over it"
    )

    def reason(self) -> str:
        return (
            f"{self.maximum} bytes is far above every program written to be "
            "read -- the largest one this repository ships is under 4000 "
            "bytes -- and small enough that a text this tool cannot do "
            "anything useful with is refused before it is read rather than "
            "after. The number was chosen, not measured on a run of this "
            "tool."
        )

    def refusal(self, amount: int) -> str:
        return (
            f"the source this request carries is {amount} bytes and this "
            f"operation reads {self.maximum}: the tool stopped before reading "
            "it, so it read no rule of the language over the text and says "
            "nothing about it; send a smaller source, or lower nothing and "
            f"read {self.maximum} from the {self.name!r} budget the "
            "'discover' operation states for this operation"
        )


@dataclass(frozen=True)
class TimeBudget(Budget):
    """How long one run may take, counted in milliseconds of wall clock.

    Written in milliseconds so that every budget this tool states is a
    whole number in a stated unit, the way the two limits it had before
    already are.
    """

    name: ClassVar[str] = "operation_time"
    unit: ClassVar[str] = "milliseconds of wall clock"
    category: ClassVar[str] = TIME_BUDGET_EXCEEDED
    observed: ClassVar[str] = (
        "at each boundary between the stages of an operation and before each "
        "declared example is run; a stage already running is not interrupted "
        "part way, and the input budget is what keeps a stage short"
    )

    def passed_by(self, elapsed: int) -> bool:
        """A run has passed this budget when none of it is left.

        A size that reaches the maximum exactly is inside it, because
        the amount is already taken; time left is the other way round --
        a run with 0 of its milliseconds left cannot take the next step.
        """
        return elapsed >= self.maximum

    def reason(self) -> str:
        return (
            f"{self.maximum} milliseconds is far longer than any answer this "
            "tool gives today -- every one of the programs here is answered "
            "in a few -- and short enough that a caller waiting on it learns "
            "quickly. The number was chosen, not measured on a run of this "
            "tool."
        )

    def refusal(self, amount: int) -> str:
        return (
            f"this run has taken {amount} of the {self.maximum} milliseconds "
            "this operation is given: the tool stops where it stands rather "
            "than leaving a caller waiting, and what it had done so far is "
            "not reported because a run stopped part way answers nothing; "
            f"give the run more time, up to {self.maximum}, by leaving "
            f"{self.lowered_with()} unset, or send less work"
        )


@dataclass(frozen=True)
class MemoryBudget(Budget):
    """How much memory one run may take, counted in bytes of the
    greatest memory this process has taken."""

    name: ClassVar[str] = "peak_memory"
    unit: ClassVar[str] = "bytes of the memory this process has taken"
    category: ClassVar[str] = MEMORY_BUDGET_EXCEEDED
    observed: ClassVar[str] = (
        "at each boundary between the stages of an operation and before each "
        "declared example is run, by asking the operating system what this "
        "process has already taken"
    )

    def enforced(self) -> bool:
        return PeakMemory.readable()

    def reason(self) -> str:
        if not self.enforced():
            return (
                "this platform does not report the memory a process has "
                "taken, so the memory a run takes is not measured here: this "
                "budget is stated and not enforced, and no answer from this "
                "platform says it was kept."
            )
        return (
            f"{self.maximum} bytes is far above what this tool takes to "
            "answer -- a run of it takes a few tens of megabytes -- and far "
            "under the memory of the machines it runs on. The number was "
            "chosen, not measured on a run of this tool."
        )

    def refusal(self, amount: int) -> str:
        return (
            f"this run has taken {amount} of the {self.maximum} bytes of "
            "memory this operation is given: the tool stops first rather "
            "than being stopped by the machine with nothing to say; raise "
            f"the memory this run may take, up to {self.maximum}, by leaving "
            f"{self.lowered_with()} unset, or send a smaller program"
        )


@dataclass(frozen=True)
class AnswerBudget(Budget):
    """How large an answer may be, counted in bytes of the text this
    tool prints."""

    name: ClassVar[str] = "answer_size"
    unit: ClassVar[str] = "bytes of the answer this tool prints"
    category: ClassVar[str] = OUTPUT_BUDGET_EXCEEDED
    observed: ClassVar[str] = (
        "the size of the answer, where it is written; the budget sizes the "
        "answer an operation produced, and the refusal that replaces one too "
        "large is this tool's smallest answer and is always printed"
    )

    def reason(self) -> str:
        return (
            f"{self.maximum} bytes is far above every answer this tool gives "
            "today -- the largest, the manifest itself, is under 100000 -- "
            "and small enough that a caller reading one answer into memory "
            "can size what it reads. The number was chosen, not measured on "
            "a run of this tool."
        )

    def refusal(self, amount: int) -> str:
        return (
            f"the answer this operation produced is {amount} bytes and this "
            f"operation gives {self.maximum}: an answer a caller cannot be "
            "given whole is withheld whole, because the first part of one "
            "carries no outcome to read; ask for less in one request, or "
            f"raise the answer this run may give, up to {self.maximum}, by "
            f"leaving {self.lowered_with()} unset"
        )


@dataclass(frozen=True)
class UnreadableBudget:
    """A budget a caller wrote that this tool cannot read, with the name
    it must repair and why.

    Answered rather than ignored: a caller that believed it had lowered
    a budget and had not would read the run that followed as evidence
    that its work fits.
    """

    variable: str
    reason: str


@dataclass(frozen=True)
class Budgets:
    """The four budgets of one run, held together.

    Built from the numbers this tool declares, and lowered only from the
    environment a caller sets. Nothing else reads them: the dispatcher
    is handed this object, and the manifest states the same four.
    """

    budgets: tuple[Budget, ...]

    @classmethod
    def declared(cls) -> "Budgets":
        """The Owner's numbers: 1 MiB of source, 10 s, 512 MiB of
        memory, 1 MiB of answer."""
        return cls(
            (
                InputBudget(1024 * 1024),
                TimeBudget(10_000),
                MemoryBudget(512 * 1024 * 1024),
                AnswerBudget(1024 * 1024),
            )
        )

    @classmethod
    def from_environment(cls, environment) -> "Budgets | UnreadableBudget":
        """The budgets of one run, with every budget the environment
        lowers written down, or the one variable that cannot be read.

        A name beginning the way a budget does and spelling none of the
        four is refused too: a caller that mistyped one would otherwise
        run under a budget it did not choose.
        """
        declared = cls.declared()
        known = {budget.lowered_with(): budget for budget in declared.budgets}
        for written in sorted(environment):
            if written.startswith(LOWERED_WITH) and written not in known:
                return UnreadableBudget(
                    written,
                    f"this tool states no budget lowered with {written}: it "
                    f"states {', '.join(sorted(known))}, one per budget, and "
                    "reads no other; a name it does not read would leave a "
                    "caller believing it had lowered a budget it had not. "
                    "Set one of those four names, read from the 'lower_with' "
                    "entry of each budget the 'discover' operation states, "
                    "or unset this one",
                )
        lowered = []
        for budget in declared.budgets:
            written = environment.get(budget.lowered_with())
            if written is None:
                lowered.append(budget)
                continue
            asked = budget.lowered_to(written)
            if isinstance(asked, UnreadableBudget):
                return asked
            lowered.append(asked)
        return cls(tuple(lowered))

    def start(self) -> "Run":
        return Run(self, time.monotonic_ns())

    def published_for(self, operations: tuple, status: str) -> dict:
        """What the manifest states about every operation's budgets.

        One entry per operation, each written from the same four
        objects the run is measured against. The numbers are the ones
        this tool declares: a caller that lowered one for its own run
        already knows what it asked for.
        """
        declared = Budgets.declared()
        return {
            operation: {
                budget.name: budget.published(status) for budget in declared.budgets
            }
            for operation in operations
        }

    def source_exhausted_by(self, source: str) -> "Exhaustion | None":
        return self._of(InputBudget).exhausted_by(_size_of(source))

    def time_exhausted_by(self, elapsed: int) -> "Exhaustion | None":
        return self._of(TimeBudget).exhausted_by(elapsed)

    def memory_exhausted_by(self, taken: int) -> "Exhaustion | None":
        return self._of(MemoryBudget).exhausted_by(taken)

    def answer_exhausted_by(self, size: int) -> "Exhaustion | None":
        return self._of(AnswerBudget).exhausted_by(size)

    def _of(self, kind: type) -> Budget:
        for budget in self.budgets:
            if isinstance(budget, kind):
                return budget
        raise KeyError(kind.__name__)


@dataclass(frozen=True)
class Run:
    """One run under its budgets: which budgets, and when it began.

    Asked at each boundary between the stages of an operation whether
    the run may go on. It keeps nothing of what it measured: every
    answer is read afresh from the clock and from the operating system.
    """

    budgets: Budgets
    began_at: int

    def stop_if_exhausted(self) -> None:
        """Stop this run where it stands if its time or its memory has
        run out."""
        exhausted = self.budgets.time_exhausted_by(self._elapsed_milliseconds())
        if exhausted is None:
            taken = PeakMemory.taken_so_far()
            if taken is not None:
                exhausted = self.budgets.memory_exhausted_by(taken.bytes_taken)
        if exhausted is not None:
            raise BudgetExhausted(exhausted)

    def stop_if_source_too_large(self, source: str) -> None:
        """Stop this run before any rule of the language is read over a
        source larger than this operation reads."""
        exhausted = self.budgets.source_exhausted_by(source)
        if exhausted is not None:
            raise BudgetExhausted(exhausted)

    def _elapsed_milliseconds(self) -> int:
        return (time.monotonic_ns() - self.began_at) // 1_000_000


def _size_of(text: str) -> int:
    """How many bytes `text` is.

    Written with the surrogate escapes passed through, so that a source
    carrying one is sized here exactly as it is sized everywhere else in
    this tool and this budget introduces no new refusal of its own.
    """
    return len(text.encode("utf-8", "surrogatepass"))
