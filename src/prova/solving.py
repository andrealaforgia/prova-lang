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
        try:
            import z3
        except Exception as missing:  # noqa: BLE001 - any import failure
            return SolverUnavailable(self._unavailable(missing))
        return z3.get_version_string()

    def asked(self, claim: encoding.Claim, milliseconds_left: int):
        """Whether the denial of `claim` has a solution, within the time
        the run has left."""
        if milliseconds_left < THE_LEAST_WORTH_ASKING:
            return Undecided(
                "the run had no time left to ask the solver: this obligation "
                "was not put to it at all, and nothing about it was decided",
                "timed_out",
            )
        try:
            import z3
        except Exception as missing:  # noqa: BLE001 - any import failure
            return SolverUnavailable(self._unavailable(missing))
        return _Question(z3, claim).answered(milliseconds_left)

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

    def answered(self, milliseconds_left: int):
        z3 = self._z3
        solver = z3.Solver()
        solver.set("timeout", int(milliseconds_left))
        for assumption in self._claim.assumptions:
            solver.add(self._built(assumption))
        solver.add(z3.Not(self._built(self._claim.conclusion)))
        outcome = solver.check()
        if outcome == z3.unsat:
            return Unrefutable()
        if outcome == z3.sat:
            return Refuted(self._read(solver.model()))
        return self._could_not_tell(solver.reason_unknown())

    def _could_not_tell(self, said: str) -> Undecided:
        out_of_time = "timeout" in said or "canceled" in said
        return Undecided(
            f"the solver could not settle this obligation: {said}. "
            + (
                "The run's time budget bounds every question put to it, so a "
                "question that runs out is left unsettled rather than "
                "answered from half a search."
                if out_of_time
                else "It is left unsettled rather than answered either way."
            ),
            "timed_out" if out_of_time else "completed",
        )

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
        z3 = self._z3
        parts = tuple(self._built(part) for part in term.parts)
        primitive = term.primitive
        if primitive is encoding.INTEGER:
            return z3.IntVal(term.carried)
        if primitive is encoding.VARIABLE:
            return self._constants[term.carried[0]]
        if primitive is encoding.TRUTH:
            return z3.BoolVal(True)
        if primitive is encoding.FALSITY:
            return z3.BoolVal(False)
        if primitive is encoding.UNIT:
            return self._sorts.the_unit_value()
        if primitive is encoding.SHAPE:
            return self._sorts.constructor(term.carried)(*parts)
        if primitive is encoding.FIELD:
            constructor, field_name = term.carried
            return self._sorts.accessor(constructor, field_name)(parts[0])
        if primitive is encoding.IS_SHAPE:
            return self._sorts.recognizer(term.carried)(parts[0])
        return _OF_TWO_OR_MORE[primitive.name](z3, parts)


_OF_TWO_OR_MORE = {
    encoding.SUM.name: lambda z3, p: p[0] + p[1],
    encoding.DIFFERENCE.name: lambda z3, p: p[0] - p[1],
    encoding.PRODUCT.name: lambda z3, p: p[0] * p[1],
    encoding.LESS.name: lambda z3, p: p[0] < p[1],
    encoding.AT_MOST.name: lambda z3, p: p[0] <= p[1],
    encoding.GREATER.name: lambda z3, p: p[0] > p[1],
    encoding.AT_LEAST.name: lambda z3, p: p[0] >= p[1],
    encoding.EQUALS.name: lambda z3, p: p[0] == p[1],
    encoding.CONJUNCTION.name: lambda z3, p: z3.And(*p),
    encoding.DISJUNCTION.name: lambda z3, p: z3.Or(*p),
    encoding.NEGATION.name: lambda z3, p: z3.Not(p[0]),
    encoding.CONDITIONAL.name: lambda z3, p: z3.If(p[0], p[1], p[2]),
}


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


def _written(z3, value) -> str:
    """One value of a solution, written the way a program writes it, so
    the Owner can hand it straight to a run."""
    if isinstance(value, z3.IntNumRef):
        return str(value.as_long())
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
