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
        if not (written.isascii() and written.isdecimal()):
            return UnreadableBudget(
                self.lowered_with(),
                f"the budget written in {self.lowered_with()} is "
                f"{written!r}, which is not a whole number of "
                f"{self.unit} written in the digits 0 to 9: this tool reads "
                "one such number from that variable and nothing else -- a "
                "digit of another alphabet, a digit written above the line, a "
                "sign, a space around the number or nothing at all would "
                "otherwise leave the run under a budget the caller did not "
                f"choose; write it as a whole number no larger than "
                f"{self.maximum}, as {max(1, self.maximum // 2)}, or leave "
                "the variable unset to run under the number this tool "
                "declares",
            )
        significant = written.lstrip("0")
        readable = sys.get_int_max_str_digits()
        if len(significant) > readable:
            # Only a run of digits the interpreter will not turn into a
            # number at all is refused by its length; every text that
            # can be read as a number is read, and answered against the
            # number this tool declares exactly as it was before.
            return UnreadableBudget(
                self.lowered_with(),
                f"the budget written in {self.lowered_with()} is "
                f"{len(written)} characters long, writing a number of "
                f"{len(significant)} digits, and the interpreter this tool "
                f"runs on turns at most {readable} digits into one number: a "
                "run of digits longer than that is not read as a number at "
                "all, so it is refused here by its length, before anything "
                f"reads it; write a whole number no larger than {self.maximum}, "
                f"as {max(1, self.maximum // 2)}, or leave the variable unset",
            )
        asked = int(significant or "0")
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
            **self.also_published(),
        }

    def also_published(self) -> dict:
        """What this budget states beside what every budget states."""
        return {}

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
        "twice: this tool reads at most this budget plus 'request_allowance' "
        "bytes from its input at all, and answers a longer request against "
        "this budget without reading it; the source a shorter request carries "
        "is then sized against this budget before any rule of the language is "
        "read over it"
    )

    # What this tool reads of a request around the source itself: the
    # operation, the function and arguments of an evaluate request, the
    # JSON that holds them, and whatever a client adds. 64 KiB is far
    # above every request this tool is sent -- the largest it answers
    # today is an evaluate request of a few hundred bytes around its
    # source -- and small enough that a request this tool cannot use is
    # refused after reading a page or two rather than after copying all
    # of it into memory.
    REQUEST_ALLOWANCE: ClassVar[int] = 64 * 1024

    def also_published(self) -> dict:
        return {
            "request_allowance": self.REQUEST_ALLOWANCE,
            "request_allowance_reason": (
                f"this tool reads at most {self.maximum} + "
                f"{self.REQUEST_ALLOWANCE} bytes of a request before it "
                "answers: the first number is the source it would read, the "
                "second is everything a request carries around that source. "
                "A longer request is answered against this budget without "
                "being read, so a caller that sends one is told which budget "
                "stopped it and not which operation it asked for, because "
                "that was never read. The second number was chosen, not "
                "measured on a run of this tool."
            ),
        }

    def request_ceiling(self) -> int:
        """How many bytes of a request this tool reads at all."""
        return self.maximum + self.REQUEST_ALLOWANCE

    def request_too_large(self, at_least: int) -> "Exhaustion":
        return Exhaustion(
            self.name,
            self.maximum,
            at_least,
            self.category,
            f"the request sent to this tool is at least {at_least} bytes, "
            f"more than the {self.maximum} bytes of source this tool reads "
            f"and the {self.REQUEST_ALLOWANCE} bytes it allows a request to "
            "carry around one: it stopped reading there, so it never read "
            "which operation was asked for and says nothing about any "
            "program; send a shorter request, and read the two numbers from "
            f"the {self.name!r} budget the 'discover' operation states",
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
        "declared example is run, by asking the operating system for the "
        "greatest memory this process has taken. That figure is a high-water "
        "mark: it never falls, so once a run has passed this budget every "
        "later measurement in the same process is past it too. The command "
        "answers one request per process, so a run of it is measured against "
        "its own work alone"
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
            f"this process has taken {amount} of the {self.maximum} bytes "
            "of memory this operation is given: the tool stops first rather "
            "than being stopped by the machine with nothing to say. The "
            "figure is the greatest this process has taken and never falls, "
            "so this run cannot come back under the budget: start the work "
            "again in a new process, with a smaller program, or with the "
            f"memory this run may take raised up to {self.maximum} by "
            f"leaving {self.lowered_with()} unset"
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
        """Whether `source` is larger than the input budget of this run.

        Sized without a second copy of the text: a character is one to
        four bytes, so a text of more characters than the budget allows
        is already past it and a text of a quarter as many characters
        cannot be. Only a text between the two is measured, and then a
        page at a time.
        """
        budget = self._of(InputBudget)
        if len(source) * 4 <= budget.maximum:
            return None
        return budget.exhausted_by(_size_of(source))

    def request_ceiling(self) -> int:
        """How many bytes of a request this tool reads at all."""
        return self._of(InputBudget).request_ceiling()

    def request_exhausted_by(self, sent: str) -> "Exhaustion | None":
        """Whether what was read of a request is already longer than
        this tool reads.

        Read and sized the way a source is: a request of more characters
        than the ceiling allows is past it whatever its characters are,
        and one of a quarter as many cannot be, so only a request between
        the two is measured.
        """
        budget = self._of(InputBudget)
        ceiling = budget.request_ceiling()
        if len(sent) > ceiling:
            return budget.request_too_large(len(sent))
        if len(sent) * 4 <= ceiling:
            return None
        size = _size_of(sent)
        if size > ceiling:
            return budget.request_too_large(size)
        return None

    def time_exhausted_by(self, elapsed: int) -> "Exhaustion | None":
        return self._of(TimeBudget).exhausted_by(elapsed)

    def memory_exhausted_by(self, taken: int) -> "Exhaustion | None":
        return self._of(MemoryBudget).exhausted_by(taken)

    def answer_exhausted_by(self, answer: str) -> "Exhaustion | None":
        """Whether the text of `answer` is larger than the answer budget
        of this run. Sized the way a source is, and for the same reason."""
        budget = self._of(AnswerBudget)
        if len(answer) * 4 <= budget.maximum:
            return None
        return budget.exhausted_by(_size_of(answer))

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


# How much of a text is turned into bytes at once while it is sized.
# One page at a time rather than all of it, so that measuring a text
# this tool is about to refuse costs a page of memory and not a second
# copy of the text itself.
_A_PAGE = 64 * 1024


def _size_of(text: str) -> int:
    """How many bytes `text` is, measured a page at a time.

    Written with the surrogate escapes passed through, so that a source
    carrying one is sized here exactly as it is sized everywhere else in
    this tool and this budget introduces no new refusal of its own.
    """
    if len(text) <= _A_PAGE:
        return len(text.encode("utf-8", "surrogatepass"))
    size = 0
    for start in range(0, len(text), _A_PAGE):
        size += len(text[start : start + _A_PAGE].encode("utf-8", "surrogatepass"))
    return size
