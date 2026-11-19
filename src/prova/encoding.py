"""What a `core-0` construct means as a logical term, and where the
fragment this tool translates ends.

SPEC.md, "Verification obligations and the initial fragment": the
initial automated fragment is quantifier-free Boolean reasoning, linear
integer arithmetic and the non-recursive algebraic data of `core-0`,
after semantics-preserving expansion of acyclic calls; conditionals and
matches retain their path conditions; an obligation remaining outside
the fragment returns unknown with that reason and must not be translated
unsoundly.

Nothing here asks a solver, reads a file or keeps state. It turns one
obligation into a claim written in the small closed language below, or
declines it by name. There is no third way out, so a construct this
translation does not cover cannot be dropped quietly.

The meaning of every primitive the translation can emit is declared once,
beside the primitive itself: the manifest publishes it and the shipped
document explains it, both read from `published_primitives` and never
written out a second time.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import syntax, values

# The version of this translation. A client comparing two answers reads
# it beside the solver's own version: the same solver with a different
# translation is a different thing to have trusted.
VERSION = "1"

# How far a call may be expanded before the translation gives up.
# SPEC.md: inlining is a valid initial strategy, not a mandate to expand
# without resource bounds. The number is chosen, not measured: it is far
# above what either shipped example needs (3 expansions at most) and far
# below what would make one query slow.
EXPANSION_LIMIT = 64

# How deeply one expression may stand inside another before the
# translation gives up. The expansion count above bounds how many calls
# are inlined and says nothing about how far the result nests: twenty
# calls each written inside twenty additions expand to four hundred
# expressions standing on one another, which is twenty expansions and a
# stack this tool will not walk. Both are resource bounds SPEC.md asks
# for, and neither covers the other.
#
# One level costs about three interpreter frames here and two where the
# term is then built for the solver, and the two walks are made one
# after the other rather than inside one another. So 200 levels cost
# about 620 of the 1000 frames Python allows by default, measured
# against a tool that runs out at about 320 levels, and the refusal is
# reached with room to spare however deep the caller's own stack
# already stands.
#
# It stands above the 160 evaluation steps the evaluator runs rather
# than beside it. An expression a little deeper than the evaluator runs
# is still translated and still put to the solver: a solution it finds
# is then replayed, the replay runs out of depth, and the obligation is
# left unsettled for that reason. Were the two numbers equal, nothing
# would ever reach that gate and this tool would have an answer no
# program could produce.
TRANSLATION_DEPTH_LIMIT = 200

# Where the translation is written out for a reader: what every primitive
# above means, and why settling an obligation settles the claim the
# source makes. The manifest publishes this path, so a reader follows the
# answer to the document rather than having to know where it lives.
DOCUMENTED_IN = "docs/translation-to-the-solver.md"


@dataclass(frozen=True)
class Primitive:
    """One logical primitive this translation can emit, and what it
    means. Built once, here, so the published list and the documented
    list are the same list."""

    name: str
    means: str


def _declare(name: str, means: str) -> Primitive:
    primitive = Primitive(name, means)
    _PRIMITIVES.append(primitive)
    return primitive


_PRIMITIVES: list[Primitive] = []

INTEGER = _declare(
    "integer",
    "a whole number exactly as the program writes it, in the mathematical "
    "integers: no width, no wrapping and no largest value",
)
VARIABLE = _declare(
    "variable",
    "one value of a declared type, standing for every value that type has; "
    "the parameters of the function the obligation is about",
)
TRUTH = _declare("truth", "the boolean the program writes as true")
FALSITY = _declare("falsity", "the boolean the program writes as false")
UNIT = _declare("unit", "the single value of the type Unit, written ()")
SUM = _declare("sum", "the mathematical sum of two whole numbers")
DIFFERENCE = _declare(
    "difference", "the mathematical difference of two whole numbers"
)
PRODUCT = _declare(
    "product",
    "the mathematical product of two whole numbers, emitted only where one "
    "of them is written as a literal, which keeps the arithmetic linear",
)
LESS = _declare("less", "whether the first whole number is below the second")
AT_MOST = _declare(
    "at_most", "whether the first whole number is below the second or equal to it"
)
GREATER = _declare("greater", "whether the first whole number is above the second")
AT_LEAST = _declare(
    "at_least", "whether the first whole number is above the second or equal to it"
)
EQUALS = _declare(
    "equals",
    "whether two values of one type are the same value, which for the shapes "
    "below means the same constructor with the same field values throughout",
)
CONJUNCTION = _declare("conjunction", "all of the given conditions are true at once")
DISJUNCTION = _declare("disjunction", "at least one of the two conditions is true")
NEGATION = _declare("negation", "the condition is not true")
CONDITIONAL = _declare(
    "conditional",
    "the value of the second term where the first condition is true and of "
    "the third where it is not, which is what an if and a match both become",
)
SHAPE = _declare(
    "shape",
    "one value made by a declared constructor from its field values: a "
    "record or one variant of a union, never a recursive one",
)
FIELD = _declare(
    "field",
    "the value of one declared field of a value made by a constructor",
)
IS_SHAPE = _declare(
    "is_shape", "whether a value was made by the constructor this term names"
)


def published_primitives() -> dict:
    """Every primitive this translation can emit, with its meaning.

    The one declaration the manifest publishes and the shipped document
    explains, so a primitive added later cannot reach an answer with
    nothing said about what it means.
    """
    return {primitive.name: primitive.means for primitive in _PRIMITIVES}


@dataclass(frozen=True)
class Term:
    """One term of the closed language above: which primitive it is, the
    terms it is built from, and what it carries of its own (a number, a
    name, a constructor).

    Built only through the constructors below, so a term naming a
    primitive this translation never declared cannot be made.
    """

    primitive: Primitive
    parts: tuple["Term", ...] = ()
    carried: object = None

    @classmethod
    def integer(cls, value: int) -> "Term":
        return cls(INTEGER, (), value)

    @classmethod
    def variable(cls, name: str, type_name: str) -> "Term":
        return cls(VARIABLE, (), (name, type_name))

    @classmethod
    def truth(cls) -> "Term":
        return cls(TRUTH)

    @classmethod
    def falsity(cls) -> "Term":
        return cls(FALSITY)

    @classmethod
    def unit(cls) -> "Term":
        return cls(UNIT)

    @classmethod
    def built(cls, primitive: Primitive, parts: tuple["Term", ...]) -> "Term":
        return cls(primitive, parts)

    @classmethod
    def shape(cls, constructor: str, parts: tuple["Term", ...]) -> "Term":
        return cls(SHAPE, parts, constructor)

    @classmethod
    def field(cls, constructor: str, field_name: str, of: "Term") -> "Term":
        return cls(FIELD, (of,), (constructor, field_name))

    @classmethod
    def is_shape(cls, constructor: str, of: "Term") -> "Term":
        return cls(IS_SHAPE, (of,), constructor)

    @classmethod
    def all_of(cls, parts: tuple["Term", ...]) -> "Term":
        if not parts:
            return cls.truth()
        if len(parts) == 1:
            return parts[0]
        return cls(CONJUNCTION, parts)


@dataclass(frozen=True)
class Shapes:
    """Every type the claim's values can have, written so that nothing
    reading this has to know the syntax of `core-0`: each declared type
    with its constructors, and each constructor with its fields and the
    type of each.

    A record declares one constructor named for the type; a union
    declares one per variant. The type graph of `core-0` is acyclic, so
    none of these is recursive.
    """

    declared: tuple[tuple[str, tuple[tuple[str, tuple[tuple[str, str], ...]], ...]], ...]

    @classmethod
    def of(cls, program: syntax.Program) -> "Shapes":
        declared = []
        for name, kind in program.types.items():
            if isinstance(kind, syntax.RecordType):
                declared.append((name, ((name, tuple(kind.fields)),)))
            else:
                declared.append(
                    (
                        name,
                        tuple(
                            (variant.name, tuple(variant.fields))
                            for variant in kind.variants
                        ),
                    )
                )
        return cls(tuple(declared))


@dataclass(frozen=True)
class Claim:
    """One obligation as a question a solver can be asked: the shapes its
    values have, the variables it is about, what may be assumed and the
    one thing to be shown.

    It is valid exactly when `assumptions and not conclusion` has no
    solution, which is the one question the solver port is asked.
    """

    shapes: Shapes
    variables: tuple[tuple[str, str], ...]
    assumptions: tuple[Term, ...]
    conclusion: Term


@dataclass(frozen=True)
class OutsideTheFragment:
    """A construct this translation does not cover, named with the
    reason. The only way the translation can decline."""

    reason: str


@dataclass(frozen=True)
class ByRuleOfTheProfile:
    """An obligation no solver is asked about, because a rule of `core-0`
    settles it.

    It carries the name of the rule and not its sentence: an answer about
    a program of many functions would otherwise repeat the same paragraph
    once per entry, and a reader comparing two entries could not tell at
    a glance that they rest on the same rule. The sentences are published
    once beside the inventory.
    """

    rule: str


class _Outside(Exception):
    """Raised inside the walk below and turned into `OutsideTheFragment`
    at the one place the walk is entered. Never leaves this module."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


class Translation:
    """The walk from the expressions of one program to the terms above.

    Holds the program it reads and how many expansions it has spent, and
    nothing else: a fresh one is made for each claim, so no claim is
    shortened by what another one used.
    """

    def __init__(self, program: syntax.Program):
        self._program = program
        self._expansions = 0
        self._standing = 0

    def term_of(self, expression: object, bound: dict) -> Term:
        """`expression` as a term, with `bound` giving a term for each
        name in scope.

        The one place this walk stands inside itself, so the one place
        its depth is counted. Counting it here rather than at a call
        alone covers an expression written inside an expression, a chain
        of calls and any mixture of them, because all three stand on the
        same interpreter stack.
        """
        self._standing += 1
        try:
            if self._standing > TRANSLATION_DEPTH_LIMIT:
                raise _Outside(
                    f"translating this obligation reached {self._standing} "
                    "expressions standing inside one another and this "
                    f"translation walks {TRANSLATION_DEPTH_LIMIT}, which is "
                    "the bound it keeps rather than walking until the "
                    "interpreter stack runs out and nothing at all is "
                    "answered; the obligation is left unsettled instead, "
                    "and the rest of the inventory stands. The bound is on "
                    "how deep the expanded expression nests and not on how "
                    "many calls were expanded, which is counted on its own"
                )
            for shape, translate in (
                (syntax.IntLit, self._integer),
                (syntax.BoolLit, self._boolean),
                (syntax.UnitLit, self._unit),
                (syntax.NameRef, self._name),
                (syntax.OperatorCall, self._operator),
                (syntax.ConstructorCall, self._construction),
                (syntax.FieldAccess, self._selection),
                (syntax.If, self._choice),
                (syntax.Match, self._match),
                (syntax.Call, self._expanded_call),
            ):
                if isinstance(expression, shape):
                    return translate(expression, bound)
            raise _Outside(
                f"the translation covers no "
                f"{type(expression).__name__.lower()} expression yet: it "
                "covers whole numbers, booleans, the unit value, names, the "
                "operators of core-0, constructors, field selection, if, "
                "match and calls to declared functions"
            )
        finally:
            self._standing -= 1

    def term_of_value(self, value: object) -> Term:
        """One closed value -- what a declared example is written from --
        as a term. A value carries no name, so it needs nothing bound."""
        if isinstance(value, bool):
            return Term.truth() if value else Term.falsity()
        if isinstance(value, int):
            return Term.integer(value)
        if isinstance(value, values.Unit):
            return Term.unit()
        if isinstance(value, values.ConstructorValue):
            return Term.shape(
                value.constructor,
                tuple(self.term_of_value(field) for field in value.fields),
            )
        raise _Outside(
            f"the translation covers no value of the kind {value!r} is: it "
            "covers whole numbers, booleans, the unit value and values built "
            "by a declared constructor"
        )

    def condition_of(self, condition: object, bound: dict) -> Term:
        """One clause of the condition that reaches a site, as a term."""
        from prova import obligations

        if isinstance(condition, obligations.Holds):
            return self.term_of(condition.expression, bound)
        if isinstance(condition, obligations.Fails):
            return Term.built(
                NEGATION, (self.term_of(condition.expression, bound),)
            )
        if isinstance(condition, obligations.Matches):
            return self._matched(condition.scrutinee, condition.pattern, bound)
        if isinstance(condition, obligations.DoesNotMatch):
            return Term.built(
                NEGATION,
                (self._matched(condition.scrutinee, condition.pattern, bound),),
            )
        raise _Outside(
            "the translation does not cover the condition that reaches this "
            f"site: {condition!r}"
        )

    # --- one translation per kind of expression ----------------------------

    def _integer(self, expression: syntax.IntLit, bound: dict) -> Term:
        return Term.integer(expression.value)

    def _boolean(self, expression: syntax.BoolLit, bound: dict) -> Term:
        return Term.truth() if expression.value else Term.falsity()

    def _unit(self, expression: syntax.UnitLit, bound: dict) -> Term:
        return Term.unit()

    def _name(self, expression: syntax.NameRef, bound: dict) -> Term:
        known = bound.get(expression.name)
        if known is None:
            raise _Outside(
                f"the name {expression.name!r} stands for a value this "
                "translation does not have a term for: it covers the "
                "parameters of the function and the word result, and no "
                "binding introduced inside an expression"
            )
        return known

    def _operator(self, expression: syntax.OperatorCall, bound: dict) -> Term:
        parts = tuple(self.term_of(arg, bound) for arg in expression.args)
        if expression.operator == "*":
            return self._product(parts)
        primitive = _OPERATORS.get(expression.operator)
        if primitive is None:
            raise _Outside(
                f"the translation covers no operator {expression.operator!r}: "
                f"it covers {', '.join(sorted(_OPERATORS) + ['*'])}"
            )
        return Term.built(primitive, parts)

    def _product(self, parts: tuple[Term, ...]) -> Term:
        if any(part.primitive is INTEGER for part in parts):
            return Term.built(PRODUCT, parts)
        raise _Outside(
            "this multiplies two numbers neither of which is written as a "
            "literal. SPEC.md keeps multiplication linear -- one operand a "
            "known integer constant -- and puts the general product outside "
            "the automation required here, so it is not translated at all; "
            "write one operand as a literal, or read the fragment in the "
            "document this tool names"
        )

    def _construction(self, expression: syntax.ConstructorCall, bound: dict) -> Term:
        return Term.shape(
            expression.name,
            tuple(self.term_of(arg, bound) for arg in expression.args),
        )

    def _selection(self, expression: syntax.FieldAccess, bound: dict) -> Term:
        target = self.term_of(expression.target, bound)
        owner = self._constructor_owning(expression.field_name, expression.target)
        return Term.field(owner, expression.field_name, target)

    def _constructor_owning(self, field_name: str, target: object) -> str:
        """Which constructor declares `field_name`. The checker has
        already resolved the selection from the operand's nominal type,
        so exactly one record declares it here."""
        owning = [
            name
            for name, kind in self._program.types.items()
            if isinstance(kind, syntax.RecordType)
            and any(field == field_name for field, _ in kind.fields)
        ]
        if len(owning) == 1:
            return owning[0]
        raise _Outside(
            f"the field {field_name!r} is declared by {len(owning)} record "
            "types in this program, and this translation reads a selection "
            "from the one record that declares it; equal field spellings in "
            "different records are core-0 and are not covered yet"
        )

    def _choice(self, expression: syntax.If, bound: dict) -> Term:
        return Term.built(
            CONDITIONAL,
            (
                self.term_of(expression.condition, bound),
                self.term_of(expression.then_branch, bound),
                self.term_of(expression.else_branch, bound),
            ),
        )

    def _match(self, expression: syntax.Match, bound: dict) -> Term:
        """A match as a chain of conditionals in source order.

        The last clause is the final alternative, with no test of its
        own: the checker has already shown the match exhaustive over the
        scrutinee's type, so nothing but a value that clause matches can
        reach it. Clauses are tried in source order, which the chain
        keeps.
        """
        clauses = expression.clauses
        answer = self.term_of(clauses[-1].body, bound)
        for clause in reversed(clauses[:-1]):
            answer = Term.built(
                CONDITIONAL,
                (
                    self._matched(expression.scrutinee, clause.pattern, bound),
                    self.term_of(clause.body, bound),
                    answer,
                ),
            )
        return answer

    def _matched(self, scrutinee: object, pattern: object, bound: dict) -> Term:
        """Whether `scrutinee` has the shape `pattern` writes."""
        value = self.term_of(scrutinee, bound)
        if isinstance(pattern, (syntax.PatWildcard, syntax.PatVar)):
            return Term.truth()
        if isinstance(pattern, syntax.PatInt):
            return Term.built(EQUALS, (value, Term.integer(pattern.value)))
        if isinstance(pattern, syntax.PatBool):
            matched = Term.truth() if pattern.value else Term.falsity()
            return Term.built(EQUALS, (value, matched))
        if isinstance(pattern, syntax.PatUnit):
            return Term.truth()
        if isinstance(pattern, syntax.PatConstructor) and not pattern.subpatterns:
            return Term.is_shape(pattern.name, value)
        raise _Outside(
            "the translation covers no constructor pattern carrying patterns "
            "of its own yet: it covers a wildcard, a name, a whole number, a "
            "boolean, the unit value and a constructor with no fields"
        )

    def _expanded_call(self, expression: syntax.Call, bound: dict) -> Term:
        """A call to a declared function, as the callee's body with its
        parameters standing for the arguments.

        SPEC.md names inlining a valid initial strategy. The calls a
        `core-0` program can reach are acyclic, so the expansion ends;
        the count below is the resource bound SPEC.md asks for.
        """
        self._expansions += 1
        if self._expansions > EXPANSION_LIMIT:
            raise _Outside(
                f"expanding the calls of this obligation passed "
                f"{EXPANSION_LIMIT} expansions, which is the bound this "
                "translation keeps rather than expanding without one; the "
                "obligation is left unsettled instead of answered from half "
                "a translation"
            )
        callee = self._program.functions.get(expression.name)
        if callee is None:
            raise _Outside(
                f"the program declares no function {expression.name!r} to "
                "expand, so the call could not be translated"
            )
        return self.term_of(callee.body, self._arguments_of(callee, expression, bound))

    def _arguments_of(
        self, callee: syntax.Function, call: syntax.Call, bound: dict
    ) -> dict:
        return {
            parameter.name: self.term_of(argument, bound)
            for parameter, argument in zip(callee.signature.params, call.args)
        }

    # --- what a function's own parts become --------------------------------

    def parameters_of(self, function: syntax.Function) -> dict:
        return {
            parameter.name: Term.variable(parameter.name, parameter.type_name)
            for parameter in function.signature.params
        }

    def conjunction_of(self, clauses: tuple, bound: dict) -> Term:
        return Term.all_of(tuple(self.term_of(clause, bound) for clause in clauses))


_OPERATORS = {
    "+": SUM,
    "-": DIFFERENCE,
    "<": LESS,
    "<=": AT_MOST,
    ">": GREATER,
    ">=": AT_LEAST,
    "=": EQUALS,
    "and": CONJUNCTION,
    "or": DISJUNCTION,
    "not": NEGATION,
}


def variables_of(function: syntax.Function) -> tuple[tuple[str, str], ...]:
    return tuple(
        (parameter.name, parameter.type_name)
        for parameter in function.signature.params
    )


def attempted(build) -> "Claim | OutsideTheFragment":
    """The one place a translation is entered, and the one place a
    construct outside the fragment becomes the answer rather than a
    failure of the tool."""
    try:
        return build()
    except _Outside as outside:
        return OutsideTheFragment(outside.reason)
