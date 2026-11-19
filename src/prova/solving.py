"""The one place a solver is asked anything.

A claim is valid exactly when its negation has no solution, so that is
the one question asked here: the assumptions together with the denial of
the conclusion. Three answers come back -- no solution, a solution, or
the solver could not tell -- and nothing here decides what any of them
means for an obligation.

SPEC.md lines 302-305: the initial implementation may trust a selected
solver's validity result, disclosing that trust. Nothing in this module
checks the solver's word. The answer the caller builds says so.

The solver package is imported inside the calls that need it and never
at module level. Three things rest on that: no other operation of this
tool pays for loading it, a request this tool refuses enters no solver
work at all, and a machine without the package still answers -- with
every obligation that needed it unsettled and the reason named, rather
than with a failure of the tool.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import encoding
from prova.values import WRITTEN_DIGITS

# What the solver is called and the package it is pinned as. One place,
# read by the answer and by what the answer stands on.
SOLVER = "z3"
PACKAGE = "z3-solver"

# How little of the time budget is too little to ask anything. A query
# given no time cannot answer, so it is not asked: the obligation is
# unsettled with a timed-out status instead, which is the truth about it.
THE_LEAST_WORTH_ASKING = 1


@dataclass(frozen=True)
class Unrefutable:
    """The denial of the claim has no solution: the claim is valid, on
    the solver's word, which this tool does not check."""


@dataclass(frozen=True)
class Refuted:
    """The denial of the claim has a solution: a candidate the caller
    must still replay against the reference semantics before calling
    anything disproved.

    It carries one text per variable of the claim, written the way a
    program writes a value, so the caller can hand them straight to a
    run.
    """

    assignment: tuple[tuple[str, str], ...]

    def arguments(self, names: tuple[str, ...]) -> tuple[str, ...]:
        written = dict(self.assignment)
        return tuple(written[name] for name in names)


@dataclass(frozen=True)
class Undecided:
    """The solver could not tell, or was never asked: the reason, and
    what happened to the attempt."""

    reason: str
    execution_status: str


@dataclass(frozen=True)
class SolverUnavailable:
    """The solver package could not be loaded, with what Python said.

    Kept apart from `Undecided`: an obligation nothing could ask about is
    a failure of this tool's installation, not a question the solver
    found hard.
    """

    reason: str


class PinnedZ3:
    """The pinned solver, asked one question at a time, inside the time
    the run has left.

    Holds nothing between questions: each one builds its own solver, so
    no claim is answered from what another claim left behind.
    """

    def name(self) -> str:
        return SOLVER

    def version(self) -> "str | SolverUnavailable":
        """The version of the library that would answer, read from the
        library itself rather than from the pin, so an answer names what
        really ran."""
        loaded = self._loaded()
        if isinstance(loaded, SolverUnavailable):
            return loaded
        return loaded.get_version_string()

    def asked(self, claim: encoding.Claim, milliseconds_left: int):
        """Whether the denial of `claim` has a solution, within the time
        the run has left."""
        if milliseconds_left < THE_LEAST_WORTH_ASKING:
            return Undecided(
                "the run had no time left to ask the solver: this obligation "
                "was not put to it at all, and nothing about it was decided",
                "timed_out",
            )
        loaded = self._loaded()
        if isinstance(loaded, SolverUnavailable):
            return loaded
        return _Question(loaded, claim).answered(milliseconds_left)

    def _loaded(self):
        """The solver library, or the reason it could not be loaded.

        The one place this tool loads it: inside the call that needs it,
        never at module level, so no other operation pays for it and a
        machine without it still answers.
        """
        try:
            import z3
        except Exception as missing:  # noqa: BLE001 - any import failure
            return SolverUnavailable(self._unavailable(missing))
        return z3

    def _unavailable(self, failure: Exception) -> str:
        return (
            f"the solver could not be loaded, so this obligation was not put "
            f"to it: {type(failure).__name__}: {failure}. This tool stands on "
            f"the {PACKAGE!r} package; install the dependencies of this tool "
            "(uv sync) and ask again. Nothing about this obligation was "
            "decided"
        )


class _Question:
    """One claim, built in the solver's own terms and asked once."""

    def __init__(self, z3, claim: encoding.Claim):
        self._z3 = z3
        self._claim = claim
        self._sorts = _Sorts(z3, claim.shapes)
        self._constants = {
            name: z3.Const(name, self._sorts.named(type_name))
            for name, type_name in claim.variables
        }

    @property
    def z3(self):
        return self._z3

    @property
    def sorts(self) -> "_Sorts":
        return self._sorts

    def constant_named(self, name: str):
        return self._constants[name]

    def answered(self, milliseconds_left: int):
        z3 = self._z3
        solver = z3.Solver()
        solver.set("timeout", int(milliseconds_left))
        for assumption in self._claim.assumptions:
            solver.add(self._built(assumption))
        solver.add(z3.Not(self._built(self._claim.conclusion)))
        try:
            return verdict_for(z3, solver.check(), solver, self._read)
        except _TooLargeToWrite as too_large:
            return Undecided(too_large.reason, "completed")

    def _read(self, model) -> tuple[tuple[str, str], ...]:
        """The solution, as one text per variable written the way a
        program writes a value.

        Every variable is read with the model completed, so a variable
        the solution left free is still given a value a reader can run.
        """
        return tuple(
            (name, _written(self._z3, model.eval(constant, model_completion=True)))
            for name, constant in self._constants.items()
        )

    def _built(self, term: encoding.Term):
        """`term` in the solver's own terms.

        One table below says how each primitive of the translation is
        built, so a primitive the translation declares and this adapter
        does not build is a missing row in one table rather than a case
        missing from a chain of tests. Each row is handed the question
        itself, the terms the primitive is built from and whatever it
        carries of its own.
        """
        built = _HOW_EACH_PRIMITIVE_IS_BUILT.get(term.primitive.name)
        if built is None:
            raise KeyError(
                f"WHAT: the translation emitted the primitive "
                f"{term.primitive.name!r} and this adapter has no row for "
                "it, so the claim could not be put to the solver. "
                "WHY: every primitive the translation declares must be "
                "built here; one missing would silently leave a claim "
                "unasked. "
                "HOW: add the row to _HOW_EACH_PRIMITIVE_IS_BUILT in "
                "prova/solving.py, beside the others."
            )
        return built(
            self, tuple(self._built(part) for part in term.parts), term.carried
        )


# How each primitive of the translation is built in the solver's own
# terms: one row per primitive `prova.encoding` declares, each taking the
# question, the terms the primitive is built from and what it carries.
_HOW_EACH_PRIMITIVE_IS_BUILT = {
    encoding.INTEGER.name: lambda q, p, c: q.z3.IntVal(c),
    encoding.VARIABLE.name: lambda q, p, c: q.constant_named(c[0]),
    encoding.TRUTH.name: lambda q, p, c: q.z3.BoolVal(True),
    encoding.FALSITY.name: lambda q, p, c: q.z3.BoolVal(False),
    encoding.UNIT.name: lambda q, p, c: q.sorts.the_unit_value(),
    encoding.SHAPE.name: lambda q, p, c: q.sorts.constructor(c)(*p),
    encoding.FIELD.name: lambda q, p, c: q.sorts.accessor(c[0], c[1])(p[0]),
    encoding.IS_SHAPE.name: lambda q, p, c: q.sorts.recognizer(c)(p[0]),
    encoding.SUM.name: lambda q, p, c: p[0] + p[1],
    encoding.DIFFERENCE.name: lambda q, p, c: p[0] - p[1],
    encoding.PRODUCT.name: lambda q, p, c: p[0] * p[1],
    encoding.LESS.name: lambda q, p, c: p[0] < p[1],
    encoding.AT_MOST.name: lambda q, p, c: p[0] <= p[1],
    encoding.GREATER.name: lambda q, p, c: p[0] > p[1],
    encoding.AT_LEAST.name: lambda q, p, c: p[0] >= p[1],
    encoding.EQUALS.name: lambda q, p, c: p[0] == p[1],
    encoding.CONJUNCTION.name: lambda q, p, c: q.z3.And(*p),
    encoding.DISJUNCTION.name: lambda q, p, c: q.z3.Or(*p),
    encoding.NEGATION.name: lambda q, p, c: q.z3.Not(p[0]),
    encoding.CONDITIONAL.name: lambda q, p, c: q.z3.If(p[0], p[1], p[2]),
}


def verdict_for(z3, outcome, solver, assignment):
    """Which verdict the solver's answer to one question is.

    The three answers a solver can give are read here, in one place, and
    each is named: no solution, a solution, or it could not tell. The
    last is read as its own verdict and never as the first -- "nothing
    refutes it" and "I cannot tell" are different answers, and reading
    the second as the first would report a claim proved that no search
    settled.

    Separate from the question that asked it so that each of the three
    can be read on its own: no program of this fragment makes a solver
    say it cannot tell, so the only way to see what this tool does with
    that answer is to hand it the answer.
    """
    if outcome == z3.unsat:
        return Unrefutable()
    if outcome == z3.sat:
        return Refuted(assignment(solver.model()))
    return could_not_tell(solver.reason_unknown())


def could_not_tell(said: str) -> Undecided:
    """What a solver's own reason for not telling becomes: unsettled,
    with the reason kept, and timed out where that is what happened."""
    out_of_time = "timeout" in said or "canceled" in said
    return Undecided(
        f"the solver could not settle this obligation: {said}. "
        + (
            "The run's time budget bounds every question put to it, so a "
            "question that runs out is left unsettled rather than answered "
            "from half a search."
            if out_of_time
            else "It is left unsettled rather than answered either way."
        ),
        "timed_out" if out_of_time else "completed",
    )


class _Sorts:
    """The types of one claim in the solver's own terms.

    Every declared type becomes one freely generated datatype: distinct
    constructors build distinct values, every value is built by one of
    them, and two values are equal exactly when they are the same
    constructor over equal fields. That is what structural equality and
    an exhaustive match mean in core-0, which is why the translation of
    `=` and of `match` is faithful.
    """

    UNIT_TYPE = "Unit"
    THE_UNIT_VALUE = "unit"

    def __init__(self, z3, shapes: encoding.Shapes):
        self._z3 = z3
        building = {name: z3.Datatype(name) for name, _ in shapes.declared}
        unit = z3.Datatype(self.UNIT_TYPE)
        unit.declare(self.THE_UNIT_VALUE)
        building[self.UNIT_TYPE] = unit
        for name, constructors in shapes.declared:
            for constructor, fields in constructors:
                building[name].declare(
                    constructor,
                    *[
                        (field, self._referenced(field_type, building))
                        for field, field_type in fields
                    ],
                )
        created = z3.CreateDatatypes(*building.values())
        self._sorts = dict(zip(building.keys(), created))
        self._places = {}
        for name, constructors in list(shapes.declared) + [
            (self.UNIT_TYPE, ((self.THE_UNIT_VALUE, ()),))
        ]:
            for place, (constructor, fields) in enumerate(constructors):
                self._places[constructor] = (name, place, tuple(f for f, _ in fields))

    def _referenced(self, type_name: str, building: dict):
        z3 = self._z3
        if type_name == "Int":
            return z3.IntSort()
        if type_name == "Bool":
            return z3.BoolSort()
        return building[type_name]

    def named(self, type_name: str):
        z3 = self._z3
        if type_name == "Int":
            return z3.IntSort()
        if type_name == "Bool":
            return z3.BoolSort()
        return self._sorts[type_name]

    def the_unit_value(self):
        return self.constructor(self.THE_UNIT_VALUE)()

    def constructor(self, constructor: str):
        type_name, place, _ = self._places[constructor]
        return self._sorts[type_name].constructor(place)

    def recognizer(self, constructor: str):
        type_name, place, _ = self._places[constructor]
        return self._sorts[type_name].recognizer(place)

    def accessor(self, constructor: str, field_name: str):
        type_name, place, fields = self._places[constructor]
        return self._sorts[type_name].accessor(place, fields.index(field_name))


class _TooLargeToWrite(Exception):
    """A value of a solution this tool cannot write as characters.

    Raised inside the walk below and turned into `Undecided` at the one
    place the question is asked, so an obligation whose solution cannot
    be written is left unsettled with that reason and the answer keeps
    its inventory. It never leaves this module.
    """

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def _written(z3, value) -> str:
    """One value of a solution, written the way a program writes it, so
    the Owner can hand it straight to a run.

    An integer past the digits this tool writes is not written at all:
    the limit is the one the whole tool writes answers under, asked of
    the unit that owns it, and a solution carrying such a value is
    reported as a question the tool could not settle rather than as a
    witness no reader could run or a failure of the tool.
    """
    if isinstance(value, z3.IntNumRef):
        return _written_integer(value)
    if z3.is_true(value):
        return "true"
    if z3.is_false(value):
        return "false"
    constructor = value.decl().name()
    if constructor == _Sorts.THE_UNIT_VALUE:
        return "()"
    fields = [_written(z3, child) for child in value.children()]
    if not fields:
        return f"({constructor})"
    return "(" + constructor + " " + " ".join(fields) + ")"


def _written_integer(value) -> str:
    """One whole number of a solution, as the characters a program writes
    it with.

    The solver writes the decimal itself and this reads its length: the
    interpreter refuses to turn a number of more digits than its own
    limit into characters at all, so counting the digits of the written
    form is the one way to meet the limit this tool declares without
    reaching that refusal first.
    """
    written = value.as_string()
    digits = len(written.lstrip("-"))
    if digits <= WRITTEN_DIGITS.maximum:
        return written
    raise _TooLargeToWrite(
        f"the solver found a solution carrying a whole number of {digits} "
        f"digits, and this tool writes an integer of at most "
        f"{WRITTEN_DIGITS.maximum} ({WRITTEN_DIGITS.name}); "
        "the solution could not be written as a value a reader can run, so "
        "this obligation is left unsettled rather than answered with a "
        "witness nobody can read. Nothing is claimed about the program "
        "either way: the rest of the inventory stands"
    )
