"""Typed syntax tree for the core-0 grammar, built from reader output."""

from __future__ import annotations

from dataclasses import dataclass, field

from prova.reader import Atom, SList
from prova.values import UNIT, ConstructorValue

OPERATORS = {"+", "-", "*", "<", "<=", ">", ">=", "=", "and", "or", "not"}
SPECIAL_FORMS = {"let", "if", "match"}


class SyntaxError_(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column


# --- declarations -----------------------------------------------------

@dataclass(frozen=True)
class RecordType:
    name: str
    fields: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class Variant:
    name: str
    fields: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class UnionType:
    name: str
    variants: tuple[Variant, ...]


@dataclass(frozen=True)
class Signature:
    params: tuple[tuple[str, str], ...]
    return_type: str


@dataclass(frozen=True)
class Example:
    function: str
    args: tuple[object, ...]
    expected: object


@dataclass(frozen=True)
class Function:
    name: str
    signature: Signature
    requires: tuple["Expr", ...]
    ensures: tuple["Expr", ...]
    examples: tuple[Example, ...]
    body: "Expr"


@dataclass(frozen=True)
class Program:
    types: dict[str, object] = field(default_factory=dict)
    functions: dict[str, Function] = field(default_factory=dict)


def resolve_constructor_fields(constructor: str, program: Program) -> tuple[tuple[str, str], ...] | None:
    """Field declarations for a constructor's owning type: either a record
    type of the same name, or the variant of that name inside some union
    type (a union variant's constructor name is the variant's own name,
    not the union type's name it is keyed under in `program.types`). `None`
    when no declared type or variant matches."""
    type_decl = program.types.get(constructor)
    if isinstance(type_decl, RecordType):
        return type_decl.fields
    for type_decl in program.types.values():
        if isinstance(type_decl, UnionType):
            for variant in type_decl.variants:
                if variant.name == constructor:
                    return variant.fields
    return None


# --- expressions --------------------------------------------------------

@dataclass(frozen=True)
class IntLit:
    value: int


@dataclass(frozen=True)
class BoolLit:
    value: bool


@dataclass(frozen=True)
class UnitLit:
    pass


@dataclass(frozen=True)
class NameRef:
    name: str


@dataclass(frozen=True)
class Call:
    name: str
    args: tuple["Expr", ...]


@dataclass(frozen=True)
class ConstructorCall:
    name: str
    args: tuple["Expr", ...]


@dataclass(frozen=True)
class OperatorCall:
    operator: str
    args: tuple["Expr", ...]


@dataclass(frozen=True)
class FieldAccess:
    field_name: str
    target: "Expr"


@dataclass(frozen=True)
class Let:
    bindings: tuple[tuple[str, "Expr"], ...]
    body: "Expr"


@dataclass(frozen=True)
class If:
    condition: "Expr"
    then_branch: "Expr"
    else_branch: "Expr"


@dataclass(frozen=True)
class MatchClause:
    pattern: "Pattern"
    body: "Expr"


@dataclass(frozen=True)
class Match:
    scrutinee: "Expr"
    clauses: tuple[MatchClause, ...]


Expr = object  # IntLit | BoolLit | UnitLit | NameRef | Call | ConstructorCall
# | OperatorCall | FieldAccess | Let | If | Match


# --- patterns -------------------------------------------------------------

@dataclass(frozen=True)
class PatWildcard:
    pass


@dataclass(frozen=True)
class PatVar:
    name: str


@dataclass(frozen=True)
class PatInt:
    value: int


@dataclass(frozen=True)
class PatBool:
    value: bool


@dataclass(frozen=True)
class PatUnit:
    pass


@dataclass(frozen=True)
class PatConstructor:
    name: str
    subpatterns: tuple["Pattern", ...]


Pattern = object


# --- parsing: declarations -------------------------------------------------

def parse_program(forms: list[object]) -> Program:
    types: dict[str, object] = {}
    functions: dict[str, Function] = {}
    for form in forms:
        head = _head_symbol(form)
        if head == "deftype":
            type_decl = _parse_type_decl(form)
            types[type_decl.name] = type_decl
        elif head == "defn":
            function = _parse_function_decl(form)
            functions[function.name] = function
        else:
            line, column = _position(form)
            raise SyntaxError_(
                f"expected a top-level 'deftype' or 'defn' form, found {head!r}",
                line,
                column,
            )
    return Program(types=types, functions=functions)


def _position(node: object) -> tuple[int, int]:
    if isinstance(node, (Atom, SList)):
        return node.line, node.column
    return 0, 0


def _head_symbol(node: object) -> str | None:
    if isinstance(node, SList) and node.items and isinstance(node.items[0], Atom):
        return node.items[0].text
    return None


def _parse_type_decl(form: SList) -> RecordType | UnionType:
    name = form.items[1].text
    body = form.items[2]
    kind = body.items[0].text
    if kind == "record":
        fields = tuple(_parse_field(f) for f in body.items[1:])
        return RecordType(name, fields)
    if kind == "union":
        variants = tuple(_parse_variant(v) for v in body.items[1:])
        return UnionType(name, variants)
    raise SyntaxError_(f"expected 'record' or 'union', found {kind!r}", *_position(body))


def _parse_field(node: SList) -> tuple[str, str]:
    return node.items[0].text, node.items[1].text


def _parse_variant(node: SList) -> Variant:
    name = node.items[0].text
    fields = tuple(_parse_field(f) for f in node.items[1:])
    return Variant(name, fields)


def _parse_signature(node: SList) -> Signature:
    params_list = node.items[1]
    params = tuple(_parse_field(p) for p in params_list.items)
    return_type = node.items[3].text
    return Signature(params, return_type)


def _parse_function_decl(form: SList) -> Function:
    name = form.items[1].text
    signature = _parse_signature(form.items[2])
    rest = list(form.items[3:])

    requires: tuple[Expr, ...] = ()
    ensures: tuple[Expr, ...] = ()

    if rest and _head_symbol(rest[0]) == "requires":
        requires = tuple(parse_expr(e) for e in rest[0].items[1:])
        rest = rest[1:]
    if rest and _head_symbol(rest[0]) == "ensures":
        ensures = tuple(parse_expr(e) for e in rest[0].items[1:])
        rest = rest[1:]

    examples = _parse_examples(rest[0])
    body = parse_expr(rest[1])
    return Function(name, signature, requires, ensures, examples, body)


def _parse_examples(node: SList) -> tuple[Example, ...]:
    return tuple(_parse_example(e) for e in node.items[1:])


def _parse_example(node: SList) -> Example:
    call = node.items[1]
    function_name = call.items[0].text
    args = tuple(parse_value(v) for v in call.items[1:])
    expected = parse_value(node.items[3])
    return Example(function_name, args, expected)


# --- parsing: values (used only by declared examples) ----------------------

def parse_value(node: object) -> object:
    if isinstance(node, Atom):
        if node.text == "true":
            return True
        if node.text == "false":
            return False
        if node.is_int:
            return node.int_value
        raise SyntaxError_(f"not a value: {node.text!r}", node.line, node.column)
    assert isinstance(node, SList)
    if not node.items:
        return UNIT
    head = node.items[0]
    constructor_name = head.text
    fields = tuple(parse_value(v) for v in node.items[1:])
    return ConstructorValue(constructor_name, fields)


# --- parsing: expressions ---------------------------------------------------

def parse_expr(node: object) -> Expr:
    if isinstance(node, Atom):
        if node.text == "true":
            return BoolLit(True)
        if node.text == "false":
            return BoolLit(False)
        if node.is_int:
            return IntLit(node.int_value)
        return NameRef(node.text)

    assert isinstance(node, SList)
    if not node.items:
        return UnitLit()

    head = node.items[0]
    if not isinstance(head, Atom):
        raise SyntaxError_("a call's head must be a symbol", *_position(node))
    name = head.text

    if name == "let":
        bindings = tuple(
            (b.items[0].text, parse_expr(b.items[1])) for b in node.items[1].items
        )
        body = parse_expr(node.items[2])
        return Let(bindings, body)

    if name == "if":
        return If(
            parse_expr(node.items[1]),
            parse_expr(node.items[2]),
            parse_expr(node.items[3]),
        )

    if name == "match":
        scrutinee = parse_expr(node.items[1])
        clauses = tuple(_parse_clause(c) for c in node.items[2:])
        return Match(scrutinee, clauses)

    if name.startswith("."):
        target = parse_expr(node.items[1])
        return FieldAccess(name[1:], target)

    args = tuple(parse_expr(a) for a in node.items[1:])
    if name in OPERATORS:
        return OperatorCall(name, args)
    if name[0].isupper():
        return ConstructorCall(name, args)
    return Call(name, args)


def _parse_clause(node: SList) -> MatchClause:
    pattern = _parse_pattern(node.items[0])
    body = parse_expr(node.items[1])
    return MatchClause(pattern, body)


def _parse_pattern(node: object) -> Pattern:
    if isinstance(node, Atom):
        if node.text == "_":
            return PatWildcard()
        if node.text == "true":
            return PatBool(True)
        if node.text == "false":
            return PatBool(False)
        if node.is_int:
            return PatInt(node.int_value)
        return PatVar(node.text)
    assert isinstance(node, SList)
    if not node.items:
        return PatUnit()
    name = node.items[0].text
    subpatterns = tuple(_parse_pattern(p) for p in node.items[1:])
    return PatConstructor(name, subpatterns)
