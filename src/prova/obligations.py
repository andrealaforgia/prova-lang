"""The obligations a `core-0` program owes, and the condition that reaches
each one.

SPEC.md, "Verification obligations and the initial fragment": every
potentially evaluated call emits a precondition obligation under its path
condition; each function emits obligations connecting its body to its
postcondition; example validity, contract definedness and structural
termination have separate records; an unreachable path can make an
obligation vacuous but does not remove it.

Nothing here attempts an obligation. This module has no solver, reads no
file, spawns nothing and keeps no state: it turns a typed program into the
list of what would have to be shown about it. Every obligation carries two
words that are constants of the type and not something a caller can set:
`not_attempted`, its standing as a statement, and `unsupported`, what
happened when something tried to settle it.

The inventory is built only for a program the checker accepted, so every
call it meets is resolved; a call that is not resolved is a programming
error here and refuses loudly.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import syntax

# What an obligation stands as, and what happened to the attempt to
# settle it: SPEC.md lines 270-284 keep the two apart and give each its
# own words, which share none. This tool has no solver, so nothing here
# supported an attempt and every entry carries both constants.
NOT_ATTEMPTED = "not_attempted"
UNSUPPORTED = "unsupported"

NOTHING_WAS_ATTEMPTED = (
    "This tool has no solver and ran none of these obligations: every entry is "
    "still owed and its result is not_attempted. The list says what work remains "
    "and nothing else."
)


# --- where an obligation arises, and what reaches it -----------------------

@dataclass(frozen=True)
class Site:
    """Where in a declaration an obligation arises, as a structural path
    (`contract`, `body`, `ensures[1]/arg[0]`, `body/then`): never a line
    number, so reformatting a program leaves every identity unchanged."""

    segments: tuple[str, ...]

    def inside(self, segment: str) -> "Site":
        return Site(self.segments + (segment,))

    def text(self) -> str:
        return "/".join(self.segments)


@dataclass(frozen=True)
class Holds:
    """A condition reached because an expression of the program is true
    there: the test of an `if` on the way into its branch, or a clause of
    the function's own precondition."""

    expression: object

    def text(self) -> str:
        return text_of(self.expression)


@dataclass(frozen=True)
class Fails:
    """A condition reached because an expression of the program is false
    there: the test of an `if` on the way into its other branch."""

    expression: object

    def text(self) -> str:
        return f"(not {text_of(self.expression)})"


@dataclass(frozen=True)
class Matches:
    """A condition reached because the scrutinee of a `match` has the
    shape one of its patterns writes."""

    scrutinee: object
    pattern: object

    def text(self) -> str:
        return f"(matches {text_of(self.scrutinee)} {pattern_text(self.pattern)})"


@dataclass(frozen=True)
class DoesNotMatch:
    """A condition reached because an earlier clause of a `match` did not
    take the value: clauses are tried in source order, so a later one is
    reached only where every earlier pattern failed."""

    scrutinee: object
    pattern: object

    def text(self) -> str:
        return (
            f"(not (matches {text_of(self.scrutinee)} "
            f"{pattern_text(self.pattern)}))"
        )


@dataclass(frozen=True)
class PathCondition:
    """What must hold for a site to be reached: the function's own
    precondition where the site is answered under it, then the branch and
    match conditions on the way down. It reads `true` only when there is
    none.

    Each clause is the condition it is -- an expression holding or
    failing, a pattern matching or not -- and not the text of one. A
    reader is shown the text; anything that has to decide what reaches a
    site, rather than print it, is given the program's own expressions.
    """

    clauses: tuple[object, ...] = ()

    def extended_with(self, clauses: tuple[object, ...]) -> "PathCondition":
        return PathCondition(self.clauses + clauses)

    def text(self) -> str:
        if not self.clauses:
            return "true"
        written = [clause.text() for clause in self.clauses]
        if len(written) == 1:
            return written[0]
        return "(and " + " ".join(written) + ")"


# --- what must be shown ----------------------------------------------------

@dataclass(frozen=True)
class Obligation:
    """One thing that would have to be shown about one function.

    No constructor takes either of its two words: `not_attempted` is the
    only standing an obligation can carry and `unsupported` the only
    thing that can have happened to it here, so an inventory reporting
    attempted work cannot be built at all.
    """

    function: str
    site: Site

    kind = "obligation"

    @property
    def identity(self) -> str:
        return f"{self.kind}:{self.function}:{self.site.text()}"

    def to_show(self) -> str:
        raise NotImplementedError("each kind of obligation says what it owes")

    def detail(self) -> dict:
        return {}

    def as_dict(self) -> dict:
        entry = {
            "id": self.identity,
            "kind": self.kind,
            "function": self.function,
            "site": self.site.text(),
            "to_show": self.to_show(),
            "result": NOT_ATTEMPTED,
            "execution_status": UNSUPPORTED,
        }
        entry.update(self.detail())
        return entry


@dataclass(frozen=True)
class CallPrecondition(Obligation):
    """A call meets the precondition of the function it calls, wherever the
    condition that reaches it holds."""

    callee: str
    precondition_clauses: int
    path_condition: PathCondition

    kind = "call_precondition"

    def to_show(self) -> str:
        return (
            f"the arguments this call passes to '{self.callee}' meet its precondition "
            f"whenever the condition that reaches the call is true"
        )

    def detail(self) -> dict:
        return {
            "callee": self.callee,
            "precondition_clauses": self.precondition_clauses,
            "path_condition": self.path_condition.text(),
        }


@dataclass(frozen=True)
class BodyPostcondition(Obligation):
    """A function's body answers what its postcondition states."""

    postcondition_clauses: int

    kind = "body_postcondition"

    def to_show(self) -> str:
        return (
            f"the body of '{self.function}' answers its postcondition for every input "
            f"that meets its precondition"
        )

    def detail(self) -> dict:
        return {"postcondition_clauses": self.postcondition_clauses}


@dataclass(frozen=True)
class ExampleValidity(Obligation):
    """A declared example is a valid example of its own function."""

    ordinal: int

    kind = "example_validity"

    def to_show(self) -> str:
        return (
            f"declared example {self.ordinal} of '{self.function}' has arguments of the "
            f"declared types that meet its precondition, and the result it states"
        )

    def detail(self) -> dict:
        return {"ordinal": self.ordinal}


@dataclass(frozen=True)
class ContractDefinedness(Obligation):
    """A function's contract is defined for every input of its types."""

    contract_clauses: int

    kind = "contract_definedness"

    def to_show(self) -> str:
        return (
            f"every clause of the contract of '{self.function}' is defined for every "
            f"input of the declared types"
        )

    def detail(self) -> dict:
        return {"contract_clauses": self.contract_clauses}


@dataclass(frozen=True)
class StructuralTermination(Obligation):
    """A function terminates because the calls it can reach are acyclic."""

    direct_calls: int

    kind = "structural_termination"

    def to_show(self) -> str:
        return (
            f"'{self.function}' terminates structurally: the calls it can reach are "
            f"acyclic and each of them terminates"
        )

    def detail(self) -> dict:
        return {"direct_calls": self.direct_calls}


# --- the inventory ---------------------------------------------------------

@dataclass(frozen=True)
class Inventory:
    """The obligations a program owes, in declaration order.

    Two obligations may not share an identity: an identity names one
    obligation, so two answers can be compared entry by entry.
    """

    obligations: tuple[Obligation, ...]

    def __post_init__(self) -> None:
        identities = [obligation.identity for obligation in self.obligations]
        repeated = sorted({name for name in identities if identities.count(name) > 1})
        if repeated:
            raise ValueError(
                f"WHAT: {repeated} each name more than one obligation in the same "
                "inventory. "
                "WHY: an identity names one obligation, so that two answers about the "
                "same program can be compared entry by entry; repeated identities make "
                "that comparison meaningless. "
                "HOW: give each obligation a site that says where in the declaration it "
                "arises, as the walk over requires, ensures and the body does."
            )

    def as_dict(self) -> dict:
        entries = [obligation.as_dict() for obligation in self.obligations]
        return {
            "obligations": entries,
            "totals": {
                "obligations": len(entries),
                "attempted": 0,
                "not_attempted": len(entries),
                "by_kind": self._by_kind(),
            },
            "note": NOTHING_WAS_ATTEMPTED,
        }

    def _by_kind(self) -> dict:
        counted: dict[str, int] = {}
        for obligation in self.obligations:
            counted[obligation.kind] = counted.get(obligation.kind, 0) + 1
        return {kind: counted[kind] for kind in sorted(counted)}


def inventory_for(program: syntax.Program) -> Inventory:
    """Everything `program` owes, function by function in declaration order."""
    owed: list[Obligation] = []
    for function in program.functions.values():
        owed.extend(_owed_by(function, program))
    return Inventory(tuple(owed))


def _owed_by(function: syntax.Function, program: syntax.Program) -> list[Obligation]:
    contract_clauses = len(function.requires) + len(function.ensures)
    calls = _calls_owed_by(function, program)
    owed: list[Obligation] = [
        ContractDefinedness(function.name, Site(("contract",)), contract_clauses)
    ]
    owed.extend(calls)
    owed.append(
        BodyPostcondition(function.name, Site(("body",)), len(function.ensures))
    )
    owed.extend(
        ExampleValidity(function.name, Site((f"example[{ordinal}]",)), ordinal)
        for ordinal in range(len(function.examples))
    )
    owed.append(
        StructuralTermination(function.name, Site(("calls",)), len(calls))
    )
    return owed


def _calls_owed_by(
    function: syntax.Function, program: syntax.Program
) -> list[Obligation]:
    owed: list[Obligation] = []
    for index, clause in enumerate(function.requires):
        owed.extend(_calls_in(clause, Site((f"requires[{index}]",)), function, program))
    under_its_own_precondition = _precondition_of(function)
    for index, clause in enumerate(function.ensures):
        owed.extend(
            _calls_in(
                clause,
                Site((f"ensures[{index}]",)),
                function,
                program,
                under_its_own_precondition,
            )
        )
    owed.extend(
        _calls_in(
            function.body,
            Site(("body",)),
            function,
            program,
            under_its_own_precondition,
        )
    )
    return owed


def _precondition_of(function: syntax.Function) -> PathCondition:
    """What a call in the postcondition or the body of `function` is reached
    under.

    SPEC.md, "Meaning of a claim": the claim is `Pre_f(x) implies ...`, so
    the postcondition is checked under the precondition and the body answers
    it for every input that meets the precondition. A call in the
    precondition itself is reached under nothing: a precondition must be
    well-defined for every typed input and cannot assume itself true to
    justify a partial call.
    """
    return PathCondition(tuple(Holds(clause) for clause in function.requires))


def _calls_in(
    expression: object,
    site: Site,
    function: syntax.Function,
    program: syntax.Program,
    reached_under: PathCondition = PathCondition(),
) -> list[Obligation]:
    owed: list[Obligation] = []
    if isinstance(expression, syntax.Call):
        owed.append(_call_obligation(expression, site, reached_under, function, program))
    for part, segment, added in _parts_of(expression):
        owed.extend(
            _calls_in(
                part,
                site.inside(segment),
                function,
                program,
                reached_under.extended_with(added),
            )
        )
    return owed


def _call_obligation(
    call: syntax.Call,
    site: Site,
    reached_under: PathCondition,
    function: syntax.Function,
    program: syntax.Program,
) -> CallPrecondition:
    callee = program.functions.get(call.name)
    if callee is None:
        raise ValueError(
            f"WHAT: '{function.name}' calls '{call.name}' at {site.text()}, and the "
            "program declares no such function, so nothing was listed. "
            "WHY: the obligations of a program are listed only once every call is "
            "resolved; an obligation about a call to nothing would say nothing. "
            "HOW: run the check operation on this program first: it reports the call "
            "as an unknown_function diagnostic, and verify answers with that same "
            "refusal instead of a list."
        )
    return CallPrecondition(
        function.name, site, call.name, len(callee.requires), reached_under
    )


def _parts_of(expression: object) -> list[tuple[object, str, tuple[object, ...]]]:
    """Each subexpression of `expression` with the path segment that names
    it and the conditions that must hold to reach it."""
    if isinstance(
        expression, (syntax.Call, syntax.ConstructorCall, syntax.OperatorCall)
    ):
        return [(arg, f"arg[{index}]", ()) for index, arg in enumerate(expression.args)]
    if isinstance(expression, syntax.FieldAccess):
        return [(expression.target, "target", ())]
    if isinstance(expression, syntax.Let):
        bound = [
            (binding.value, f"bind[{index}]", ())
            for index, binding in enumerate(expression.bindings)
        ]
        return bound + [(expression.body, "in", ())]
    if isinstance(expression, syntax.If):
        asked = expression.condition
        return [
            (expression.condition, "cond", ()),
            (expression.then_branch, "then", (Holds(asked),)),
            (expression.else_branch, "else", (Fails(asked),)),
        ]
    if isinstance(expression, syntax.Match):
        return _parts_of_match(expression)
    return []


def _parts_of_match(
    expression: syntax.Match,
) -> list[tuple[object, str, tuple[object, ...]]]:
    scrutinee = expression.scrutinee
    parts: list[tuple[object, str, tuple[object, ...]]] = [
        (expression.scrutinee, "scrutinee", ())
    ]
    earlier: tuple[object, ...] = ()
    for index, clause in enumerate(expression.clauses):
        taken = _can_fail(clause.pattern)
        reached = earlier + ((Matches(scrutinee, clause.pattern),) if taken else ())
        parts.append((clause.body, f"case[{index}]", reached))
        earlier = earlier + (
            (DoesNotMatch(scrutinee, clause.pattern),) if taken else ()
        )
    return parts


def _can_fail(pattern: object) -> bool:
    """Whether a value can fail to match the pattern. A wildcard or a plain
    name always matches, so it adds no condition."""
    return not isinstance(pattern, (syntax.PatWildcard, syntax.PatVar))


# --- reading an expression back as text ------------------------------------

def text_of(expression: object) -> str:
    """`expression` written back in the source's own syntax, so a reported
    condition reads the way the program does."""
    if isinstance(expression, syntax.IntLit):
        return str(expression.value)
    if isinstance(expression, syntax.BoolLit):
        return "true" if expression.value else "false"
    if isinstance(expression, syntax.UnitLit):
        return "()"
    if isinstance(expression, syntax.NameRef):
        return expression.name
    if isinstance(expression, (syntax.Call, syntax.ConstructorCall)):
        return _applied(expression.name, expression.args)
    if isinstance(expression, syntax.OperatorCall):
        return _applied(expression.operator, expression.args)
    if isinstance(expression, syntax.FieldAccess):
        return f"(.{expression.field_name} {text_of(expression.target)})"
    if isinstance(expression, syntax.Let):
        return _let_text(expression)
    if isinstance(expression, syntax.If):
        return (
            f"(if {text_of(expression.condition)} {text_of(expression.then_branch)} "
            f"{text_of(expression.else_branch)})"
        )
    if isinstance(expression, syntax.Match):
        return _match_text(expression)
    raise ValueError(
        f"WHAT: {expression!r} is not an expression of the core-0 syntax tree, so the "
        "condition that reaches a call could not be written out. "
        "WHY: every condition reported beside an obligation is the program's own text; "
        "an unknown node would be reported as a condition nobody can read. "
        "HOW: add the node to prova.obligations.text_of, beside the syntax type it "
        "belongs to."
    )


def _applied(head: str, args: tuple) -> str:
    if not args:
        return f"({head})"
    return "(" + head + " " + " ".join(text_of(arg) for arg in args) + ")"


def _let_text(expression: syntax.Let) -> str:
    bindings = " ".join(
        f"({binding.name} {text_of(binding.value)})"
        for binding in expression.bindings
    )
    return f"(let ({bindings}) {text_of(expression.body)})"


def _match_text(expression: syntax.Match) -> str:
    clauses = " ".join(
        f"({pattern_text(clause.pattern)} {text_of(clause.body)})"
        for clause in expression.clauses
    )
    return f"(match {text_of(expression.scrutinee)} {clauses})"


def pattern_text(pattern: object) -> str:
    """`pattern` written back in the source's own syntax."""
    if isinstance(pattern, syntax.PatWildcard):
        return "_"
    if isinstance(pattern, syntax.PatVar):
        return pattern.name
    if isinstance(pattern, syntax.PatInt):
        return str(pattern.value)
    if isinstance(pattern, syntax.PatBool):
        return "true" if pattern.value else "false"
    if isinstance(pattern, syntax.PatUnit):
        return "()"
    if isinstance(pattern, syntax.PatConstructor):
        if not pattern.subpatterns:
            return f"({pattern.name})"
        inner = " ".join(pattern_text(sub) for sub in pattern.subpatterns)
        return f"({pattern.name} {inner})"
    raise ValueError(
        f"WHAT: {pattern!r} is not a pattern of the core-0 syntax tree, so the "
        "condition reaching a match clause could not be written out. "
        "WHY: every condition reported beside an obligation is the program's own text. "
        "HOW: add the pattern to prova.obligations.pattern_text, beside the syntax type "
        "it belongs to."
    )
