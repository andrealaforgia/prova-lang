"""Whole-program static checking: declarations, scope, nominal typing and
the acyclic dependency rule.

Reports every referenced type, constructor and name as it resolves them,
and infers the nominal type of every expression (including both branches
of an `if` and every `match` clause, reached or not) to catch a type
error anywhere in the program, not only ones a call happens to exercise.

It also refuses a program whose functions depend on themselves. SPEC.md
requires the combined dependency graph of function bodies and contracts
to be acyclic, and excludes the calls an example makes to its own
function from that graph.

It refuses a function whose declared example is about another
function: SPEC.md requires every function to have an example directly
calling that same function, with one closed value for each parameter it
takes, so an example that calls another name demonstrates that other
name and leaves its own function with none.

It refuses recursive data for the same reason: SPEC.md requires the
type-dependency graph to be acyclic too, so a record field or a union
payload that leads back to its own type belongs to a later profile. A
program whose types lead back to themselves is answered with that
refusal alone, because every check that follows the fields of a type
ends only on acyclic types.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from typing import ClassVar

from prova import syntax
from prova.values import ConstructorValue

BUILTIN_TYPES = {"Unit", "Bool", "Int"}

NUMERIC = "numeric"
COMPARISON = "comparison"
EQUALITY = "equality"
BOOLEAN = "boolean"


@dataclass(frozen=True)
class BuiltinOperator:
    """One builtin operator as SPEC.md lines 178-189 give it: how many
    arguments it takes, and which group of operands and answers it
    belongs to.

    Operators have no variable arity, so `arity` is the only number of
    arguments its operator accepts, and a call written with any other
    number is refused rather than read as a shorter or longer operator.
    """

    arity: int
    family: str


# The eleven operators of core-0, and nothing else. This is the one
# place the checker learns which operators exist, how many arguments
# each takes and how each reads its operands: the groups below and the
# answer to `arity_of` are all read from here, so an operator added to
# the language is added once.
BUILTIN_OPERATORS = {
    "+": BuiltinOperator(2, NUMERIC),
    "-": BuiltinOperator(2, NUMERIC),
    "*": BuiltinOperator(2, NUMERIC),
    "<": BuiltinOperator(2, COMPARISON),
    "<=": BuiltinOperator(2, COMPARISON),
    ">": BuiltinOperator(2, COMPARISON),
    ">=": BuiltinOperator(2, COMPARISON),
    "=": BuiltinOperator(2, EQUALITY),
    "and": BuiltinOperator(2, BOOLEAN),
    "or": BuiltinOperator(2, BOOLEAN),
    "not": BuiltinOperator(1, BOOLEAN),
}


def _operators_of(family: str) -> frozenset[str]:
    return frozenset(
        operator
        for operator, builtin in BUILTIN_OPERATORS.items()
        if builtin.family == family
    )


NUMERIC_OPERATORS = _operators_of(NUMERIC)
COMPARISON_OPERATORS = _operators_of(COMPARISON)
EQUALITY_OPERATORS = _operators_of(EQUALITY)
BOOLEAN_OPERATORS = _operators_of(BOOLEAN)

CYCLIC_DEPENDENCY = "cyclic_dependency"
DUPLICATE_DECLARATION = "duplicate_declaration"
RECURSIVE_TYPE = "recursive_type"
SHADOWED_BINDING = "shadowed_binding"
RESERVED_NAME = "reserved_name"
UNRELATED_EXAMPLE = "unrelated_example"

# The one name core-0 reserves: a postcondition reads it as the
# function's return value, so no binder may take it.
RESERVED_FOR_POSTCONDITIONS = "result"


@dataclass(frozen=True)
class Diagnostic:
    category: str
    reason: str
    location: tuple[int, int] | None = None
    cycle: "DeclarationCycle | None" = None


def listed(parts: tuple[str, ...]) -> str:
    """`parts` as a reader reads them: `a`, `a and b`, `a, b and c`."""
    if len(parts) == 1:
        return parts[0]
    return f"{', '.join(parts[:-1])} and {parts[-1]}"


@dataclass(frozen=True)
class DeclarationCycle:
    """The declarations of one cycle in a dependency graph of a program,
    in the order the program declares them.

    A cycle that names nothing cannot be built: the refusal it carries
    would not tell the reader which declaration to repair. Each kind of
    cycle says what it is a cycle of and which refusal it carries.
    """

    members: tuple[str, ...]

    KIND: ClassVar[str] = "declaration"

    def __post_init__(self) -> None:
        if not self.members:
            raise ValueError(
                f"a cycle must name at least one {self.KIND}: this one was built "
                "with no member, so the refusal it carries would not say which "
                f"{self.KIND} to repair; build it from the {self.KIND}s the "
                "dependency search found depending on each other"
            )

    def names(self) -> tuple[str, ...]:
        return self.members

    def described(self) -> str:
        return listed(self.members)


@dataclass(frozen=True)
class Cycle(DeclarationCycle):
    """The functions of one cycle in the dependency graph of function
    bodies and contracts."""

    KIND: ClassVar[str] = "function"

    def diagnostic(self) -> Diagnostic:
        return Diagnostic(
            CYCLIC_DEPENDENCY,
            f"the program depends on itself through {self.described()}: core-0 "
            "requires the combined dependency graph of function bodies and "
            "contracts to be acyclic, so the tool cannot promise that such a "
            "call ends; remove one of the calls that closes the cycle (a call "
            "an example makes to its own function is not part of the graph)",
            cycle=self,
        )


@dataclass(frozen=True)
class TypeCycle(DeclarationCycle):
    """The declared types of one cycle in the type-dependency graph: the
    types whose record fields and union payloads lead back to each
    other."""

    KIND: ClassVar[str] = "type"

    def described(self) -> str:
        return listed(tuple(repr(member) for member in self.members))

    def _leads_back_to(self) -> str:
        return "itself" if len(self.members) == 1 else "each other"

    def diagnostic(self) -> Diagnostic:
        return Diagnostic(
            RECURSIVE_TYPE,
            f"the declared field types of {self.described()} lead back to "
            f"{self._leads_back_to()}: core-0 requires the type-dependency graph "
            "to be acyclic, so this is recursive data, which belongs to a later "
            "profile and is not a fault of the program; keep the type for a "
            "profile that declares recursive data, or give the field that closes "
            "the cycle a type that does not lead back. The functions of this "
            "program were not checked, because every check that follows the "
            "fields of a type is defined only on acyclic types",
            cycle=self,
        )


def _repeated_name_diagnostic(group: tuple[syntax.DeclaredName, ...]) -> Diagnostic:
    """The refusal a name declared more than once carries: what was
    declared twice, at which places, which rule it breaks and what to do
    about it."""
    first = group[0]
    places = listed(tuple(member.place() for member in group))
    return Diagnostic(
        DUPLICATE_DECLARATION,
        f"the {first.described()} is declared {len(group)} times, at {places}: "
        f"core-0 requires that {first.uniqueness_rule()}, so the tool cannot tell "
        f"which declaration a use of {first.name!r} means; remove or rename all "
        "but one of them",
        (group[-1].line, group[-1].column),
    )


def _redeclared_builtin_diagnostic(declared: syntax.DeclaredName) -> Diagnostic:
    builtins = listed(tuple(sorted(BUILTIN_TYPES)))
    return Diagnostic(
        DUPLICATE_DECLARATION,
        f"the type {declared.name!r} is declared at {declared.place()}, but "
        f"{declared.name!r} is one of the builtin types ({builtins}): core-0 does "
        "not allow a builtin type to be redeclared, so the name would stand for "
        f"two different types; give the declared type a name of its own",
        (declared.line, declared.column),
    )


@dataclass(frozen=True)
class BinderKind:
    """One kind of binder, with the two sentences it owns: the construct
    whose place the tool can report, and how an earlier binder of this
    kind is named when a later one hides it.

    The program carries no position for a binder itself, only for the
    construct that introduces it, so a refusal says which construct it
    is reporting instead of pretending to point at the name.
    """

    named: str
    introduced_by: str
    visible_as: str

    def describes(self, name: str) -> str:
        return f"the {self.named} {name!r}"

    def already_bound(self, name: str) -> str:
        return f"{self.describes(name)} {self.visible_as}"


PARAMETER = BinderKind(
    "parameter", "of the function declared at", "of the same function"
)
LET_BINDING = BinderKind(
    "let binding", "introduced by the 'let' at", "that encloses it"
)
PATTERN_VARIABLE = BinderKind(
    "pattern variable", "of the 'match' at", "of the same pattern"
)


@dataclass(frozen=True)
class Binder:
    """One name a program introduces where a value is bound: a
    parameter, a sequential `let` binding or a pattern variable, with
    the place of the construct that introduces it."""

    name: str
    kind: BinderKind
    line: int
    column: int

    def described(self) -> str:
        return self.kind.describes(self.name)

    def located(self) -> str:
        return (
            f"{self.described()} {self.kind.introduced_by} "
            f"line {self.line} column {self.column}"
        )

    def already_bound(self) -> str:
        return self.kind.already_bound(self.name)


@dataclass(frozen=True)
class HiddenBinding:
    """One binder that took a name already visible where it stands, and
    what that name already means."""

    binder: Binder
    hidden: str

    def diagnostic(self) -> Diagnostic:
        return Diagnostic(
            SHADOWED_BINDING,
            f"{self.binder.located()} hides "
            f"{self.hidden}: core-0 requires that a binding does not shadow a "
            "visible value binding, function or builtin, so a reader cannot tell "
            f"which {self.binder.name!r} a use means; rename "
            f"{self.binder.described()} to a name that is not already visible there",
            (self.binder.line, self.binder.column),
        )


@dataclass(frozen=True)
class ReservedBinder:
    """One binder that took `result`, the name only a postcondition may
    read."""

    binder: Binder

    def diagnostic(self) -> Diagnostic:
        return Diagnostic(
            RESERVED_NAME,
            f"{self.binder.located()} uses "
            f"{RESERVED_FOR_POSTCONDITIONS!r}, which core-0 reserves: only a "
            f"postcondition may read {RESERVED_FOR_POSTCONDITIONS!r}, where it "
            "names the value the function returns, so no binder may use it; rename "
            f"{self.binder.described()} and read "
            f"{RESERVED_FOR_POSTCONDITIONS!r} in a postcondition only",
            (self.binder.line, self.binder.column),
        )


@dataclass(frozen=True)
class ReservedRead:
    """One read of `result` where nothing binds it: in a body or in a
    precondition, where core-0 does not make it readable at all."""

    line: int
    column: int

    def diagnostic(self) -> Diagnostic:
        return Diagnostic(
            RESERVED_NAME,
            f"{RESERVED_FOR_POSTCONDITIONS!r} is read at line {self.line} column "
            f"{self.column}, where nothing binds it: core-0 reserves "
            f"{RESERVED_FOR_POSTCONDITIONS!r} for a postcondition, where it names "
            "the value the function returns, and a body and a precondition run "
            "before there is one; read it in a postcondition only, or read a name "
            "the function binds",
            (self.line, self.column),
        )


@dataclass(frozen=True)
class VisibleNames:
    """The names in scope where a binding is introduced, each with what
    introduced it, in the order the program introduces them.

    A scope is never changed: introducing a binder answers with the
    scope that follows it, so a clause or a `let` body can be read in
    its own scope without the bindings of a sibling reaching it.
    """

    introduced: tuple[tuple[str, str], ...] = ()

    def hidden_by(self, binder: Binder) -> HiddenBinding | None:
        for name, described in self.introduced:
            if name == binder.name:
                return HiddenBinding(binder, described)
        return None

    def holds(self, name: str) -> bool:
        return any(bound == name for bound, _ in self.introduced)

    def also(self, binder: Binder) -> "VisibleNames":
        return VisibleNames(self.introduced + ((binder.name, binder.already_bound()),))

    def with_the_returned_value(self) -> "VisibleNames":
        """The same scope, plus the one name a postcondition may read."""
        return VisibleNames(
            self.introduced
            + (
                (
                    RESERVED_FOR_POSTCONDITIONS,
                    "the value the function returns",
                ),
            )
        )


def _introduce(
    binder: Binder, visible: VisibleNames
) -> tuple[list[Diagnostic], VisibleNames]:
    """The refusals `binder` carries where `visible` is in scope, and
    the scope that follows it.

    A binder that took the reserved word carries that refusal alone: the
    reader has one binder to rename, and naming a hidden binding as well
    would offer a second repair for one defect.
    """
    if binder.name == RESERVED_FOR_POSTCONDITIONS:
        return [ReservedBinder(binder).diagnostic()], visible.also(binder)
    hidden = visible.hidden_by(binder)
    refusals = [] if hidden is None else [hidden.diagnostic()]
    return refusals, visible.also(binder)


def _pattern_binders(pattern: object, line: int, column: int) -> list[Binder]:
    """Every name `pattern` binds, in the order it writes them, so a
    spelling written twice is seen twice.

    Read apart from `_pattern_bindings`, which answers a different
    question: the type of each name a clause binds, where a repeated
    spelling is one entry.
    """
    if isinstance(pattern, syntax.PatVar):
        return [Binder(pattern.name, PATTERN_VARIABLE, line, column)]
    if isinstance(pattern, syntax.PatConstructor):
        return [
            binder
            for subpattern in pattern.subpatterns
            for binder in _pattern_binders(subpattern, line, column)
        ]
    return []


def _binder_refusals_in(expression: object, visible: VisibleNames) -> list[Diagnostic]:
    """Every refusal the binders written inside `expression` carry, read
    in the scope each of them stands in.

    A `let` initializer is read in the scope before its own binding, as
    core-0 requires; each clause of a `match` is read in the scope of the
    whole expression, so a sibling clause's variables are not visible to
    it. Any other node is descended by its own fields, so a node kind
    added to the grammar later cannot escape the rule.
    """
    if isinstance(expression, syntax.Let):
        found: list[Diagnostic] = []
        scope = visible
        for name, bound_expression in expression.bindings:
            found += _binder_refusals_in(bound_expression, scope)
            binder = Binder(name, LET_BINDING, expression.line, expression.column)
            refusals, scope = _introduce(binder, scope)
            found += refusals
        return found + _binder_refusals_in(expression.body, scope)

    if isinstance(expression, syntax.Match):
        found = _binder_refusals_in(expression.scrutinee, visible)
        for clause in expression.clauses:
            scope = visible
            for binder in _pattern_binders(
                clause.pattern, expression.line, expression.column
            ):
                refusals, scope = _introduce(binder, scope)
                found += refusals
            found += _binder_refusals_in(clause.body, scope)
        return found

    if isinstance(expression, syntax.NameRef):
        if expression.name == RESERVED_FOR_POSTCONDITIONS and not visible.holds(
            expression.name
        ):
            return [ReservedRead(expression.line, expression.column).diagnostic()]
        return []

    if is_dataclass(expression):
        return [
            diagnostic
            for field in fields(expression)
            for diagnostic in _binder_refusals_in(
                getattr(expression, field.name), visible
            )
        ]
    if isinstance(expression, (tuple, list)):
        return [
            diagnostic
            for item in expression
            for diagnostic in _binder_refusals_in(item, visible)
        ]
    return []


def _program_scope(program: syntax.Program) -> VisibleNames:
    """The names every binding of `program` must leave alone: its
    declared functions and the builtin operators.

    The builtin types are not among them: they live in the namespace of
    types, where a value binding cannot hide them.
    """
    functions = tuple(
        (name, f"the declared function {name!r}") for name in program.functions
    )
    operators = tuple(
        (operator, f"the builtin operator {operator!r}")
        for operator in sorted(syntax.OPERATORS)
    )
    return VisibleNames(functions + operators)


def _declared_places(program: syntax.Program) -> dict[str, tuple[int, int]]:
    return {
        declared.name: (declared.line, declared.column)
        for declared in program.declarations.of_kind("function")
    }


def _binding_diagnostics(program: syntax.Program) -> list[Diagnostic]:
    """Every refusal the bindings of `program` carry: a binder that
    hides a name already visible, and a binder that takes the word
    core-0 reserves.

    A parameter is a binding too, so it is read in the scope of the
    declarations before the body is read in the scope of the parameters.
    """
    diagnostics: list[Diagnostic] = []
    declarations = _program_scope(program)
    places = _declared_places(program)
    for function in program.functions.values():
        line, column = places[function.name]
        scope = declarations
        for parameter_name, _ in function.signature.params:
            refusals, scope = _introduce(
                Binder(parameter_name, PARAMETER, line, column), scope
            )
            diagnostics += refusals
        for expression in (*function.requires, function.body):
            diagnostics += _binder_refusals_in(expression, scope)
        postcondition_scope = scope.with_the_returned_value()
        for expression in function.ensures:
            diagnostics += _binder_refusals_in(expression, postcondition_scope)
    return diagnostics


def _declaration_diagnostics(program: syntax.Program) -> list[Diagnostic]:
    """Every refusal the declarations of `program` carry on their own:
    one name declared twice, and a builtin type redeclared.

    Read from the declarations in source order, not from the lookup
    tables of the program, where a later declaration of one name has
    already replaced the earlier one.
    """
    diagnostics = [
        _repeated_name_diagnostic(group)
        for group in program.declarations.repeated()
    ]
    diagnostics += [
        _redeclared_builtin_diagnostic(declared)
        for declared in program.declarations.of_kind("type")
        if declared.name in BUILTIN_TYPES
    ]
    return diagnostics


@dataclass(frozen=True)
class DeclaredExample:
    """One example a function declares, read as what it demonstrates:
    which function declares it, where it stands among that function's
    examples, which function the example calls and with how many
    arguments.

    SPEC.md lines 228-234 require an example to call directly the
    function that declares it, and its arguments to be closed values of
    the declared types, one for each parameter. An example that calls
    another name demonstrates that other name, whether the program
    declares that name as a function or not at all -- a constructor and
    a builtin operator are not functions either -- and leaves its own
    function with no example;
    an example that calls its own function with another number of
    arguments cannot be run against it at all.

    The two refusals are built here, beside the question they answer, so
    a reader of the rule reads what a reader of the program is told.
    """

    owner: str
    ordinal: int
    called: str
    arguments: int
    parameters: int
    calls_a_declared_function: bool

    @classmethod
    def of(
        cls,
        function: syntax.Function,
        example: syntax.Example,
        ordinal: int,
        program: syntax.Program,
    ) -> "DeclaredExample":
        return cls(
            function.name,
            ordinal,
            example.function,
            len(example.args),
            len(function.signature.params),
            example.function in program.functions,
        )

    def is_about_its_own_function(self) -> bool:
        return self.called == self.owner

    def diagnostics(self) -> list[Diagnostic]:
        """What the tool says about this example: nothing when it calls
        its own function with the number of arguments that function
        takes, and otherwise the one refusal its defect carries.

        A wrong name is answered alone: an example about another
        function is not also an example of this one with the wrong
        number of arguments, and a reader has one repair to make.
        """
        if not self.is_about_its_own_function():
            return [self._about_another_function()]
        if self.arguments != self.parameters:
            return [self._with_the_wrong_number_of_arguments()]
        return []

    def _described(self) -> str:
        return f"example {self.ordinal} of function {self.owner!r}"

    def _about_another_function(self) -> Diagnostic:
        undeclared = (
            ""
            if self.calls_a_declared_function
            else ", which is not a function this program declares"
        )
        demonstrates = (
            f"this example demonstrates {self.called!r}"
            if self.calls_a_declared_function
            else "this example demonstrates nothing"
        )
        repair = (
            f"; write the example as a call to {self.owner!r}, or declare it among "
            f"the examples of {self.called!r}"
            if self.calls_a_declared_function
            else f"; write the example as a call to {self.owner!r}"
        )
        return Diagnostic(
            UNRELATED_EXAMPLE,
            f"{self._described()} calls {self.called!r}{undeclared}: core-0 requires "
            "every function to have an example directly calling that same function, "
            f"so {demonstrates} and leaves {self.owner!r} with no example of its "
            f"own{repair}",
        )

    def _with_the_wrong_number_of_arguments(self) -> Diagnostic:
        return Diagnostic(
            "arity_mismatch",
            f"{self._described()} passes {self.arguments} argument(s), expected "
            f"{self.parameters}: an example supplies one closed value for each "
            f"parameter the function declares, so this example cannot be run "
            f"against {self.owner!r}; write exactly {self.parameters} argument(s) "
            "in the example",
        )


def check_program(program: syntax.Program) -> list[Diagnostic]:
    diagnostics: list[Diagnostic] = _declaration_diagnostics(program)
    known_types = BUILTIN_TYPES | set(program.types)

    def check_type_name(type_name: str, where: str) -> None:
        if type_name not in known_types:
            diagnostics.append(
                Diagnostic("unbound_type", f"unknown type {type_name!r} in {where}")
            )

    for type_decl in program.types.values():
        if isinstance(type_decl, syntax.RecordType):
            for field_name, field_type in type_decl.fields:
                check_type_name(field_type, f"record {type_decl.name!r} field {field_name!r}")
        elif isinstance(type_decl, syntax.UnionType):
            for variant in type_decl.variants:
                for field_name, field_type in variant.fields:
                    check_type_name(
                        field_type,
                        f"union {type_decl.name!r} variant {variant.name!r} field {field_name!r}",
                    )

    recursive = [cycle.diagnostic() for cycle in _type_cycles_in(program)]
    if recursive:
        # Every check below follows the fields of a type -- whether a
        # match covers its scrutinee, whether a value has the shape its
        # type declares -- and those walks only end on acyclic types.
        return diagnostics + recursive

    diagnostics += _binding_diagnostics(program)

    for function in program.functions.values():
        for param_name, param_type in function.signature.params:
            check_type_name(param_type, f"function {function.name!r} parameter {param_name!r}")
        check_type_name(function.signature.return_type, f"function {function.name!r} return type")

        params_env = {name: type_ for name, type_ in function.signature.params}
        for clause_expr in function.requires:
            _check_contract_clause_is_bool(clause_expr, params_env, program, diagnostics)

        return_type = function.signature.return_type
        body_type = _infer(function.body, params_env, program, diagnostics)
        if body_type is not None and body_type != return_type:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"function {function.name!r} body has type {body_type}, "
                    f"declared return type {return_type}",
                    (function.body.line, function.body.column),
                )
            )

        result_env = dict(params_env)
        result_env["result"] = return_type
        for clause_expr in function.ensures:
            _check_contract_clause_is_bool(clause_expr, result_env, program, diagnostics)

        for ordinal, example in enumerate(function.examples):
            where = f"function {function.name!r} example {ordinal}"
            diagnostics += DeclaredExample.of(
                function, example, ordinal, program
            ).diagnostics()
            for arg in example.args:
                _check_value(arg, program, where, diagnostics)
            _check_value(example.expected, program, where, diagnostics)

    diagnostics.extend(cycle.diagnostic() for cycle in _cycles_in(program))

    return diagnostics


def _calls_in(expression: object) -> list[syntax.Call]:
    """Every call written anywhere inside `expression`.

    The walk follows the structure of the parsed nodes instead of a list
    of node kinds, so a kind added to the grammar later cannot escape the
    dependency rule by being forgotten here. Its depth is the depth of
    the expression, as `_infer`'s already is.
    """
    found: list[syntax.Call] = []
    if isinstance(expression, syntax.Call):
        found.append(expression)
    if is_dataclass(expression) and not isinstance(expression, type):
        for field in fields(expression):
            found.extend(_calls_in(getattr(expression, field.name)))
    elif isinstance(expression, (tuple, list)):
        for item in expression:
            found.extend(_calls_in(item))
    return found


def _callees_of(function: syntax.Function, program: syntax.Program) -> list[str]:
    """The declared functions `function` depends on: the ones it calls in
    its body and in its contract clauses.

    Its declared examples are never read. An example names its own
    function -- `DeclaredExample` refuses a program where it does not --
    and SPEC.md excludes those calls from the graph. A call to a function the program does not declare is not an
    edge either; `_infer` already reports it as an unbound name.
    """
    expressions = [function.body, *function.requires, *function.ensures]
    called = [
        call.name for expression in expressions for call in _calls_in(expression)
    ]
    return [name for name in dict.fromkeys(called) if name in program.functions]


def _cycles_in(program: syntax.Program) -> list[Cycle]:
    """Every set of functions that depend on each other, one `Cycle` per
    set, ordered by where the program declares them."""
    declared = list(program.functions)
    edges = {
        name: _callees_of(program.functions[name], program) for name in declared
    }
    return [Cycle(members) for members in _cycles_among(declared, edges)]


def _type_cycles_in(program: syntax.Program) -> list[TypeCycle]:
    """Every set of declared types whose fields lead back to each other,
    one `TypeCycle` per set, ordered by where the program declares them.

    A field whose declared type the program never declares is no edge:
    `check_program` already reports it as an unknown type.
    """
    declared = list(program.types)
    edges = {
        name: [
            held
            for held in dict.fromkeys(
                field_type for _, field_type in _declared_fields(program.types[name])
            )
            if held in program.types
        ]
        for name in declared
    }
    return [TypeCycle(members) for members in _cycles_among(declared, edges)]


def _cycles_among(
    declared: list[str], edges: dict[str, list[str]]
) -> list[tuple[str, ...]]:
    """Every set of declarations that depend on each other, one tuple per
    set: its members in the order `declared` gives them, the sets ordered
    by their first member.

    The search is iterative on purpose. A recursive one would end the
    process with a `RecursionError` on a program with more declarations
    than Python allows nested calls, which is the very failure the rules
    that use it exist to remove.
    """
    rank_of = {name: rank for rank, name in enumerate(declared)}

    index: dict[str, int] = {}
    low: dict[str, int] = {}
    on_stack: set[str] = set()
    pending: list[str] = []
    components: list[list[str]] = []
    counter = 0

    def enter(name: str) -> None:
        nonlocal counter
        index[name] = low[name] = counter
        counter += 1
        pending.append(name)
        on_stack.add(name)

    for root in declared:
        if root in index:
            continue
        enter(root)
        work = [(root, iter(edges[root]))]
        while work:
            node, remaining = work[-1]
            descended = False
            for callee in remaining:
                if callee not in index:
                    enter(callee)
                    work.append((callee, iter(edges[callee])))
                    descended = True
                    break
                if callee in on_stack:
                    low[node] = min(low[node], index[callee])
            if descended:
                continue
            work.pop()
            if work:
                low[work[-1][0]] = min(low[work[-1][0]], low[node])
            if low[node] == index[node]:
                components.append(_component_from(pending, on_stack, node))

    return sorted(
        (
            tuple(sorted(component, key=lambda name: rank_of[name]))
            for component in components
            if _is_a_cycle(component, edges)
        ),
        key=lambda members: rank_of[members[0]],
    )


def _component_from(pending: list[str], on_stack: set[str], root: str) -> list[str]:
    component: list[str] = []
    while True:
        member = pending.pop()
        on_stack.discard(member)
        component.append(member)
        if member == root:
            return component


def _is_a_cycle(component: list[str], edges: dict[str, list[str]]) -> bool:
    """A set of functions that depend on each other: either more than one
    function, or a single function that calls itself."""
    if len(component) > 1:
        return True
    only = component[0]
    return only in edges[only]


def _check_contract_clause_is_bool(
    expr: object, env: dict[str, str], program: syntax.Program, diagnostics: list[Diagnostic]
) -> None:
    clause_type = _infer(expr, env, program, diagnostics)
    if clause_type is not None and clause_type != "Bool":
        diagnostics.append(
            Diagnostic(
                "type_mismatch",
                f"contract clause expects Bool, got {clause_type}",
                (expr.line, expr.column),
            )
        )


def _check_value(value: object, program: syntax.Program, where: str, diagnostics: list[Diagnostic]) -> None:
    if not isinstance(value, ConstructorValue):
        return
    if syntax.resolve_constructor_fields(value.constructor, program) is None:
        diagnostics.append(
            Diagnostic("unbound_constructor", f"unknown constructor {value.constructor!r} in {where}")
        )
        return
    for field_value in value.fields:
        _check_value(field_value, program, where, diagnostics)


def _declared_fields(type_decl: object) -> tuple[tuple[str, str], ...]:
    """The fields a declared type holds, each as its name and its
    declared type: a record's own fields, or the fields of every variant
    of a union. Empty for anything that is not a declared type."""
    if isinstance(type_decl, syntax.RecordType):
        return type_decl.fields
    if isinstance(type_decl, syntax.UnionType):
        return tuple(f for variant in type_decl.variants for f in variant.fields)
    return ()


def _field_type(type_name: str, field_name: str, program: syntax.Program) -> str | None:
    for name, field_type in _declared_fields(program.types.get(type_name)):
        if name == field_name:
            return field_type
    return None


_LITERAL_PATTERN_TYPES = {
    syntax.PatInt: "Int",
    syntax.PatBool: "Bool",
    syntax.PatUnit: "Unit",
}


def _constructor_signature(type_name: str, program: syntax.Program) -> dict[str, list[str]] | None:
    """Constructor key -> field types for a finitely-inhabited-by-constructors
    type; `None` for `Int` and for types with no known constructors."""
    if type_name == "Bool":
        return {"true": [], "false": []}
    if type_name == "Unit":
        return {"()": []}
    type_decl = program.types.get(type_name)
    if isinstance(type_decl, syntax.RecordType):
        return {type_decl.name: [t for _, t in type_decl.fields]}
    if isinstance(type_decl, syntax.UnionType):
        return {v.name: [t for _, t in v.fields] for v in type_decl.variants}
    return None


def _pattern_key(pattern: object) -> str | None:
    if isinstance(pattern, syntax.PatBool):
        return "true" if pattern.value else "false"
    if isinstance(pattern, syntax.PatUnit):
        return "()"
    if isinstance(pattern, syntax.PatConstructor):
        return pattern.name
    return None


def _is_wild(pattern: object) -> bool:
    return isinstance(pattern, (syntax.PatWildcard, syntax.PatVar))


def _covers(rows: list[tuple], types: list[str], program: syntax.Program) -> bool:
    """True when the pattern rows match every value of the column types."""
    if not types:
        return bool(rows)
    head_type, rest_types = types[0], types[1:]
    signature = _constructor_signature(head_type, program)
    if signature is None:
        return _covers([row[1:] for row in rows if _is_wild(row[0])], rest_types, program)
    for key, field_types in signature.items():
        specialised = []
        for row in rows:
            head = row[0]
            if _is_wild(head):
                specialised.append((syntax.PatWildcard(),) * len(field_types) + row[1:])
            elif _pattern_key(head) == key:
                sub = head.subpatterns if isinstance(head, syntax.PatConstructor) else ()
                specialised.append(tuple(sub) + row[1:])
        if not _covers(specialised, field_types + rest_types, program):
            return False
    return True


def _pattern_bindings(
    pattern: object,
    scrutinee_type: str | None,
    program: syntax.Program,
    diagnostics: list[Diagnostic],
    location: tuple[int, int],
) -> dict[str, str]:
    if isinstance(pattern, syntax.PatVar):
        return {pattern.name: scrutinee_type} if scrutinee_type is not None else {}
    literal_type = _LITERAL_PATTERN_TYPES.get(type(pattern))
    if literal_type is not None:
        if scrutinee_type is not None and scrutinee_type != literal_type:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"{literal_type} literal pattern against scrutinee of type {scrutinee_type}",
                    location,
                )
            )
        return {}
    if isinstance(pattern, syntax.PatConstructor):
        resolved = syntax.resolve_constructor(pattern.name, program)
        if resolved is None:
            diagnostics.append(
                Diagnostic(
                    "unbound_constructor",
                    f"unknown constructor {pattern.name!r} in match pattern",
                    location,
                )
            )
            for subpattern in pattern.subpatterns:
                _pattern_bindings(subpattern, None, program, diagnostics, location)
            return {}
        owning_type, fields = resolved
        if scrutinee_type is not None and owning_type != scrutinee_type:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"match pattern {pattern.name!r} has type {owning_type}, "
                    f"scrutinee has type {scrutinee_type}",
                    location,
                )
            )
        if len(fields) != len(pattern.subpatterns):
            diagnostics.append(
                Diagnostic(
                    "arity_mismatch",
                    f"match pattern {pattern.name!r} takes {len(fields)} field(s), "
                    f"got {len(pattern.subpatterns)}",
                    location,
                )
            )
        bindings: dict[str, str] = {}
        for (field_name, field_type), subpattern in zip(fields, pattern.subpatterns):
            bindings.update(_pattern_bindings(subpattern, field_type, program, diagnostics, location))
        return bindings
    return {}


def _infer(
    expr: object, env: dict[str, str], program: syntax.Program, diagnostics: list[Diagnostic]
) -> str | None:
    if isinstance(expr, syntax.IntLit):
        return "Int"
    if isinstance(expr, syntax.BoolLit):
        return "Bool"
    if isinstance(expr, syntax.UnitLit):
        return "Unit"

    if isinstance(expr, syntax.NameRef):
        if expr.name in env:
            return env[expr.name]
        if expr.name != RESERVED_FOR_POSTCONDITIONS:
            # A read of the reserved word carries its own refusal, which
            # says why the name is unreadable here; reporting it as an
            # unbound name as well would offer a second repair.
            diagnostics.append(
                Diagnostic(
                    "unbound_name",
                    f"unbound name {expr.name!r}",
                    (expr.line, expr.column),
                )
            )
        return None

    if isinstance(expr, syntax.Let):
        local_env = dict(env)
        for name, bound_expr in expr.bindings:
            local_env[name] = _infer(bound_expr, local_env, program, diagnostics)
        return _infer(expr.body, local_env, program, diagnostics)

    if isinstance(expr, syntax.If):
        condition_type = _infer(expr.condition, env, program, diagnostics)
        if condition_type is not None and condition_type != "Bool":
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"'if' condition expects Bool, got {condition_type}",
                    (expr.line, expr.column),
                )
            )
        then_type = _infer(expr.then_branch, env, program, diagnostics)
        else_type = _infer(expr.else_branch, env, program, diagnostics)
        if then_type is not None and else_type is not None and then_type != else_type:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"'if' branches disagree: {then_type} vs {else_type}",
                    (expr.line, expr.column),
                )
            )
            return None
        return then_type if then_type is not None else else_type

    if isinstance(expr, syntax.Match):
        scrutinee_type = _infer(expr.scrutinee, env, program, diagnostics)
        result_type: str | None = None
        disagreement = False
        diagnostics_before_patterns = len(diagnostics)
        for clause in expr.clauses:
            clause_env = dict(env)
            clause_env.update(
                _pattern_bindings(
                    clause.pattern, scrutinee_type, program, diagnostics, (expr.line, expr.column)
                )
            )
            clause_type = _infer(clause.body, clause_env, program, diagnostics)
            if clause_type is None:
                continue
            if result_type is None:
                result_type = clause_type
            elif result_type != clause_type:
                disagreement = True
        patterns_well_formed = len(diagnostics) == diagnostics_before_patterns
        if (
            scrutinee_type is not None
            and patterns_well_formed
            and not _covers([(c.pattern,) for c in expr.clauses], [scrutinee_type], program)
        ):
            diagnostics.append(
                Diagnostic(
                    "non_exhaustive_match",
                    f"'match' does not cover every value of type {scrutinee_type}",
                    (expr.line, expr.column),
                )
            )
        if disagreement:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    "'match' clauses disagree on result type",
                    (expr.line, expr.column),
                )
            )
            return None
        return result_type

    if isinstance(expr, syntax.FieldAccess):
        target_type = _infer(expr.target, env, program, diagnostics)
        if target_type is None:
            return None
        field_type = _field_type(target_type, expr.field_name, program)
        if field_type is None:
            diagnostics.append(
                Diagnostic(
                    "unbound_field",
                    f"type {target_type!r} has no field {expr.field_name!r}",
                    (expr.line, expr.column),
                )
            )
        return field_type

    if isinstance(expr, syntax.OperatorCall):
        arg_types = [_infer(arg, env, program, diagnostics) for arg in expr.args]
        return _check_operator(expr, arg_types, diagnostics)

    if isinstance(expr, syntax.ConstructorCall):
        fields = syntax.resolve_constructor_fields(expr.name, program)
        if fields is None:
            diagnostics.append(
                Diagnostic(
                    "unbound_constructor",
                    f"unknown constructor {expr.name!r}",
                    (expr.line, expr.column),
                )
            )
            for arg in expr.args:
                _infer(arg, env, program, diagnostics)
            return None
        if len(fields) != len(expr.args):
            diagnostics.append(
                Diagnostic(
                    "arity_mismatch",
                    f"constructor {expr.name!r} takes {len(fields)} field(s), got {len(expr.args)}",
                    (expr.line, expr.column),
                )
            )
        for (field_name, field_type), arg in zip(fields, expr.args):
            arg_type = _infer(arg, env, program, diagnostics)
            if arg_type is not None and arg_type != field_type:
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"constructor {expr.name!r} field {field_name!r} expects "
                        f"{field_type}, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        for arg in expr.args[len(fields):]:
            _infer(arg, env, program, diagnostics)
        return syntax.resolve_constructor(expr.name, program)[0]

    if isinstance(expr, syntax.Call):
        callee = program.functions.get(expr.name)
        if callee is None:
            diagnostics.append(
                Diagnostic(
                    "unbound_name",
                    f"call to undeclared function {expr.name!r}",
                    (expr.line, expr.column),
                )
            )
            for arg in expr.args:
                _infer(arg, env, program, diagnostics)
            return None
        params = callee.signature.params
        if len(expr.args) != len(params):
            diagnostics.append(
                Diagnostic(
                    "arity_mismatch",
                    f"call to {expr.name!r} passes {len(expr.args)} argument(s), "
                    f"expected {len(params)}",
                    (expr.line, expr.column),
                )
            )
        for (param_name, param_type), arg in zip(params, expr.args):
            arg_type = _infer(arg, env, program, diagnostics)
            if arg_type is not None and arg_type != param_type:
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"call to {expr.name!r} argument {param_name!r} expects "
                        f"{param_type}, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        for arg in expr.args[len(params):]:
            _infer(arg, env, program, diagnostics)
        return callee.signature.return_type

    raise TypeError(f"unrecognised expression node: {expr!r}")


def arity_of(operator: str) -> int:
    """How many arguments SPEC.md gives `operator`.

    The one place that answers that question: the operand checks below,
    and the refusal a wrongly written call draws, read the same number.
    """
    try:
        return BUILTIN_OPERATORS[operator].arity
    except KeyError:
        raise ValueError(f"unknown operator {operator!r}") from None


def _check_operator(
    expr: syntax.OperatorCall, arg_types: list[str | None], diagnostics: list[Diagnostic]
) -> str:
    op = expr.operator
    takes = arity_of(op)
    if len(expr.args) != takes:
        diagnostics.append(
            Diagnostic(
                "arity_mismatch",
                f"operator {op!r} takes exactly {takes} argument(s), "
                f"got {len(expr.args)}; operators have no variable arity, so write "
                f"the call with exactly {takes}",
                (expr.line, expr.column),
            )
        )
    if op in NUMERIC_OPERATORS:
        for arg_type in arg_types:
            if arg_type is not None and arg_type != "Int":
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"operator {op!r} expects Int operands, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        return "Int"
    if op in COMPARISON_OPERATORS:
        for arg_type in arg_types:
            if arg_type is not None and arg_type != "Int":
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"operator {op!r} expects Int operands, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        return "Bool"
    if op in EQUALITY_OPERATORS:
        known = [t for t in arg_types if t is not None]
        if len(set(known)) > 1:
            diagnostics.append(
                Diagnostic(
                    "type_mismatch",
                    f"'=' operands have different types: {known}",
                    (expr.line, expr.column),
                )
            )
        return "Bool"
    if op in BOOLEAN_OPERATORS:
        for arg_type in arg_types:
            if arg_type is not None and arg_type != "Bool":
                diagnostics.append(
                    Diagnostic(
                        "type_mismatch",
                        f"operator {op!r} expects Bool operands, got {arg_type}",
                        (expr.line, expr.column),
                    )
                )
        return "Bool"
    raise ValueError(f"unknown operator {op!r}")
