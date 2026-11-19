"""Closed core-0 values: Unit, Bool, Int and named constructors."""

from __future__ import annotations

from dataclasses import dataclass
import math
import sys

# What one decimal digit is worth in bits, and one bit in decimal digits.
# Both are asked about the size of a number before its exact size is
# counted, and both are written here once so the two never disagree.
BITS_PER_DIGIT = math.log2(10)
DIGITS_PER_BIT = math.log10(2)


class TooLargeToWrite(Exception):
    """An integer this tool computed and will not write into an answer.

    Carried as an exception for the same reason a text that nests too
    deep is: every stage of an operation is written to answer about a
    program, and threading a second kind of answer back through each of
    them would put this limit in the way of every line of work the tool
    does. It carries the limit, the digits the value reached and the
    sentence that says so; it never carries the value itself, which is
    the one thing that cannot be written.
    """

    def __init__(self, message: str, limit: int, reached: int):
        super().__init__(message)
        self.message = message
        self.limit = limit
        self.reached = reached


@dataclass(frozen=True)
class DigitsWritten:
    """How many digits this tool writes as one integer in an answer, and
    the name a caller reads that number under.

    One object holds the number, as the nesting limit and the digit
    limit of the reader do: the renderer asks it whether a value has
    passed it, the refusal quotes it, and the manifest documents the
    same object's number, so what a caller is promised and what the
    tool does cannot drift apart.

    It bounds the characters an answer writes and nothing else: an
    integer under it is kept and written exactly however far past 64
    bits it stands, and no rule of core-0 is read over a program refused
    here.
    """

    declared: int
    name: str = "written_integer_digits"

    @property
    def maximum(self) -> int:
        """The limit in force: the one number enforced, refused with and
        published. It is the declared number unless the interpreter this
        tool runs on writes fewer digits than that, because its caller
        lowered PYTHONINTMAXSTRDIGITS; a limit of 0 there means the
        interpreter has none, and the declared number stands.
        """
        interpreter = sys.get_int_max_str_digits()
        if interpreter == 0 or interpreter >= self.declared:
            return self.declared
        return interpreter

    def produced_by(self) -> str:
        """Which setting produced the number in force."""
        interpreter = sys.get_int_max_str_digits()
        if self.maximum == self.declared:
            if interpreter == 0:
                return (
                    f"the number this tool declares, {self.declared}, "
                    "because the interpreter's own limit (PYTHONINTMAXSTRDIGITS) "
                    "is 0, which disables it"
                )
            return (
                f"the number this tool declares, {self.declared}, which the "
                f"interpreter's own limit of {interpreter} digits "
                "(PYTHONINTMAXSTRDIGITS) does not go below"
            )
        return (
            f"the interpreter's own limit of {interpreter} digits "
            f"(PYTHONINTMAXSTRDIGITS), which the caller of this process "
            f"set below the {self.declared} this tool declares"
        )

    def passed_by(self, value: int) -> bool:
        """Whether `value` writes more digits than this tool writes.

        Asked of every integer an answer carries, so the cheap question
        is asked first: a value of few enough bits cannot reach the
        limit whatever its digits are, and only a value past that is
        compared with the first number the limit excludes.
        """
        if value.bit_length() <= int(self.maximum * BITS_PER_DIGIT):
            return False
        return abs(value) >= 10**self.maximum

    def digits_of(self, value: int) -> int:
        """How many digits `value` writes, counted without writing it.

        A value past the limit is exactly the value this interpreter
        refuses to turn into characters, so the count a refusal carries
        is reached from the bits of the number instead.
        """
        size = abs(value)
        counted = max(1, int(size.bit_length() * DIGITS_PER_BIT))
        while 10**counted <= size:
            counted += 1
        while counted > 1 and 10 ** (counted - 1) > size:
            counted -= 1
        return counted

    def reason(self) -> str:
        """Why the number is the number it is, for a caller that must
        make its program compute a smaller result."""
        return (
            f"the limit in force is {self.maximum} digits, being "
            f"{self.produced_by()}; turning a number into characters costs "
            "time that grows with the square of its length, and the "
            "interpreter this tool runs on refuses a number past its own "
            "limit with an error of its own, so a caller meets this tool's "
            "refusal, naming the place and the limit, rather than the "
            "interpreter's. The limit stands far above "
            "the numbers programs are written to compute: a value that fills "
            f"64 bits is 20 digits long, and this tool reads an integer "
            f"literal of up to 1000 digits."
        )

    def refusal_for(self, value: int) -> TooLargeToWrite:
        reached = self.digits_of(value)
        return TooLargeToWrite(
            f"this operation computed an integer of {reached} digits and this "
            f"tool writes an integer of at most {self.maximum} digits into an "
            f"answer: {self.reason()}; the number itself is not in this answer, "
            "because writing it is the one thing that could not be done. Have "
            f"the program compute a result of at most {self.maximum} digits, "
            f"and read that length from what the 'discover' operation "
            "documents about computed integers",
            self.maximum,
            reached,
        )


# How many digits this tool writes as one integer in an answer, for
# every answer it gives.
WRITTEN_DIGITS = DigitsWritten(4000)


class Unit:
    """The sole value of type Unit, rendered `()`."""

    _instance: "Unit | None" = None

    def __new__(cls) -> "Unit":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Unit)

    def __hash__(self) -> int:
        return hash(Unit)

    def __repr__(self) -> str:
        return "()"


UNIT = Unit()


@dataclass(frozen=True)
class ConstructorValue:
    """A record or union-variant value: a constructor name plus its
    ordered field values."""

    constructor: str
    fields: tuple[object, ...]

    def field(self, index: int) -> object:
        return self.fields[index]


def render(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        if WRITTEN_DIGITS.passed_by(value):
            raise WRITTEN_DIGITS.refusal_for(value)
        try:
            return str(value)
        except ValueError:
            # Unreachable while the limit in force is not above the
            # interpreter's own; kept so a value is still refused by name.
            raise WRITTEN_DIGITS.refusal_for(value) from None
    if isinstance(value, Unit):
        return "()"
    if isinstance(value, ConstructorValue):
        if not value.fields:
            return f"({value.constructor})"
        rendered_fields = " ".join(render(f) for f in value.fields)
        return f"({value.constructor} {rendered_fields})"
    raise TypeError(f"not a core-0 value: {value!r}")
