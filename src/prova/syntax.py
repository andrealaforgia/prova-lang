"""Typed syntax tree for the core-0 grammar, built from reader output."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import ClassVar

from prova.reader import Atom, SList
from prova.values import UNIT, ConstructorValue

OPERATORS = {"+", "-", "*", "<", "<=", ">", ">=", "=", "and", "or", "not"}
SPECIAL_FORMS = {"let", "if", "match"}

# The words core-0 reserves, as SPEC.md lists them: its core keywords,
# the special forms and the builtin operator names. Composed from the
# sets above so the words live in one place only.
CORE_KEYWORDS = frozenset(
    {
        "deftype", "record", "union", "defn", "sig", "pure", "requires",
        "ensures", "examples", "example", "true", "false", "result",
    }
) | frozenset(SPECIAL_FORMS)
RESERVED_WORDS = CORE_KEYWORDS | frozenset(OPERATORS)


class SyntaxError_(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column


# --- how core-0 spells a name, and the tokens it fixes ------------------

@dataclass(frozen=True)
class ValueName:
    """The spelling of one value or function name as the source writes
    it: the name position it stands at, its spelling and its place.

    A spelling core-0 does not give a value name cannot be built, so no
    misspelled function or parameter name reaches the typed tree.
    """

    role: str
    text: str
    line: int = 0
    column: int = 0

    SHAPE: ClassVar[re.Pattern] = re.compile(r"[a-z][a-z0-9-]*[?!]?$")

    def __post_init__(self) -> None:
        if self.text in RESERVED_WORDS:
            raise SyntaxError_(
                f"the {self.role} {self.text!r} is a reserved word of core-0: a "
                "reserved word already means something else wherever it appears, "
                "so no declaration can take it as its name; rename it to a word "
                "core-0 does not reserve, such as 'step-one'",
                self.line,
                self.column,
            )
        if not self.SHAPE.match(self.text):
            raise SyntaxError_(
                f"the {self.role} {self.text!r} is not spelled as core-0 spells a "
                "value name, which is a lower-case letter followed by letters, "
                "digits and hyphens and an optional '?' or '!': the first letter "
                "of a name says whether it means a value or a type; spell it with "
                "a lower-case first letter, as 'add-one'",
                self.line,
                self.column,
            )

    @classmethod
    def read(cls, role: str, node: object) -> "ValueName":
        return cls(role, _symbol_text(role, node), *_position(node))


@dataclass(frozen=True)
class TypeName:
    """The spelling of one declared type or constructor name, refused
    unless core-0 spells a type name that way."""

    role: str
    text: str
    line: int = 0
    column: int = 0

    SHAPE: ClassVar[re.Pattern] = re.compile(r"[A-Z][A-Za-z0-9]*$")

    def __post_init__(self) -> None:
        if not self.SHAPE.match(self.text):
            raise SyntaxError_(
                f"the {self.role} {self.text!r} is not spelled as core-0 spells a "
                "type name, which is a capital letter followed by letters and "
                "digits: the first letter of a name says whether it means a value "
                "or a type; spell it with a capital first letter, as 'Point'",
                self.line,
                self.column,
            )

    @classmethod
    def read(cls, role: str, node: object) -> "TypeName":
        return cls(role, _symbol_text(role, node), *_position(node))


@dataclass(frozen=True)
class MarkerToken:
    """One token core-0 fixes at a single grammar position -- a reserved
    marker token, or the one effect core-0 declares -- together with the
    position it stands at and the repair a reader needs."""

    token: str
    position: str
    repair: str

    def demand(self, node: object, within: str, line: int, column: int) -> None:
        found = node.text if isinstance(node, Atom) else None
        if found == self.token:
            return
        raise SyntaxError_(
            f"{within} must carry {self.token!r} as {self.position}, but "
            f"{self._stands(node, found)}: a marker token stands at one grammar "
            "position only, so without it the tool cannot tell which word means "
            f"what; {self.repair}",
            line,
            column,
        )

    def _stands(self, node: object, found: str | None) -> str:
        if found is not None:
            return f"{found!r} stands there"
        return "nothing stands there" if node is None else "a form stands there"


RETURN_ARROW = MarkerToken(
    "->",
    "the arrow before its return type",
    "write the signature as (sig (parameters) -> Type ! pure)",
)
EFFECT_MARKER = MarkerToken(
    "!",
    "the effect marker after its return type",
    "write the signature as (sig (parameters) -> Type ! pure)",
)
PURE_EFFECT = MarkerToken(
    "pure",
    "the effect after its effect marker",
    "core-0 declares only the pure effect: write '! pure'",
)
EXAMPLE_ARROW = MarkerToken(
    "=>",
    "the arrow between its call and its expected value",
    "write the example as (example (f arguments) => value)",
)


@dataclass(frozen=True)
class AtLeastOne:
    """A grammar repetition core-0 writes with a plus: what it repeats,
    and how to repair a source that writes none of it."""

    repeated: str
    repair: str

    def demand(self, members: tuple, within: str, line: int, column: int) -> tuple:
        if members:
            return tuple(members)
        raise SyntaxError_(
            f"{within} holds no {self.repeated}: core-0 writes it with a plus, so "
            f"it must have at least one {self.repeated}; {self.repair}",
            line,
            column,
        )


PROGRAM_DECLARATIONS = AtLeastOne(
    "declaration",
    "add at least one (deftype ...) or (defn ...) form to the source",
)
FUNCTION_EXAMPLES = AtLeastOne(
    "example",
    "add at least one example to the clause, or remove the function",
)


def _symbol_text(role: str, node: object) -> str:
    if isinstance(node, Atom):
        return node.text
    raise SyntaxError_(
        f"the {role} must be one symbol, but a form stands there: a core-0 name is "
        "a single symbol; write one name in that position",
        *_position(node),
    )


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
class DeclaredName:
    """One name as the source declares it: what kind of thing it names,
    where the uniqueness rule applies to it, and the place it stands.

    A name with no spelling cannot be built: a refusal carrying it would
    not tell the reader which name to repair.
    """

    kind: str
    name: str
    line: int
    column: int
    within: str = ""

    _RULES = {
        "function": "top-level function names must be unique within their namespace",
        "type": "top-level type names must be unique within their namespace",
        "constructor": "constructor names must be unique across the program",
        "field": "fields are unique within each record or variant",
    }

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError(
                "a declared name must have a spelling: this one was built with "
                "none, so a refusal carrying it would not say which name to "
                f"repair; build it from the {self.kind or 'declaration'} the "
                "source declares"
            )

    def scope(self) -> tuple[str, str, str]:
        """What makes two declarations a repeat of one another: the same
        spelling, of the same kind, in the same place of the program."""
        return (self.kind, self.within, self.name)

    def place(self) -> str:
        return f"line {self.line} column {self.column}"

    def described(self) -> str:
        described = f"{self.kind} {self.name!r}"
        return f"{described} in {self.within}" if self.within else described

    def uniqueness_rule(self) -> str:
        return self._RULES[self.kind]


@dataclass(frozen=True)
class Declarations:
    """Every name a program declares, in source order -- including the
    repeats that the lookup tables of a `Program` cannot hold, because a
    later declaration overwrites an earlier one there."""

    entries: tuple[DeclaredName, ...] = ()

    def of_kind(self, kind: str) -> tuple[DeclaredName, ...]:
        return tuple(entry for entry in self.entries if entry.kind == kind)

    def repeated(self) -> tuple[tuple[DeclaredName, ...], ...]:
        """Each group of two or more declarations of one name in one
        scope, in source order.

        A record declares a type and a constructor of that same name at
        one place, so declaring it twice repeats a name in two scopes at
        the identical two places. That is one defect with one repair:
        the group is reported once.
        """
        groups: dict[tuple[str, str, str], list[DeclaredName]] = {}
        for entry in self.entries:
            groups.setdefault(entry.scope(), []).append(entry)
        reported: list[tuple[DeclaredName, ...]] = []
        places_reported: set[frozenset[tuple[int, int]]] = set()
        for members in groups.values():
            if len(members) < 2:
                continue
            places = frozenset((member.line, member.column) for member in members)
            if places in places_reported:
                continue
            places_reported.add(places)
            reported.append(tuple(members))
        return tuple(reported)


@dataclass(frozen=True)
class Program:
    types: dict[str, object] = field(default_factory=dict)
    functions: dict[str, Function] = field(default_factory=dict)
    declarations: Declarations = Declarations()


def resolve_constructor(constructor: str, program: Program) -> tuple[str, tuple[tuple[str, str], ...]] | None:
    """The declared type name owning `constructor` and its field
    declarations: either a record type of the same name, or the union type
    containing a variant of that name (a union variant's constructor name
    is the variant's own name, not the union type's name it is keyed under
    in `program.types`). `None` when no declared type or variant matches."""
    type_decl = program.types.get(constructor)
    if isinstance(type_decl, RecordType):
        return type_decl.name, type_decl.fields
    for type_decl in program.types.values():
        if isinstance(type_decl, UnionType):
            for variant in type_decl.variants:
                if variant.name == constructor:
                    return type_decl.name, variant.fields
    return None


def resolve_constructor_fields(constructor: str, program: Program) -> tuple[tuple[str, str], ...] | None:
    """Field declarations for a constructor's owning type. `None` when no
    declared type or variant matches. See `resolve_constructor`."""
    resolved = resolve_constructor(constructor, program)
    return None if resolved is None else resolved[1]


# --- expressions --------------------------------------------------------

@dataclass(frozen=True)
class IntLit:
    value: int
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class BoolLit:
    value: bool
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class UnitLit:
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class NameRef:
    name: str
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class Call:
    name: str
    args: tuple["Expr", ...]
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class ConstructorCall:
    name: str
    args: tuple["Expr", ...]
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class OperatorCall:
    operator: str
    args: tuple["Expr", ...]
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class FieldAccess:
    field_name: str
    target: "Expr"
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class Let:
    bindings: tuple[tuple[str, "Expr"], ...]
    body: "Expr"
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class If:
    condition: "Expr"
    then_branch: "Expr"
    else_branch: "Expr"
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class MatchClause:
    pattern: "Pattern"
    body: "Expr"


@dataclass(frozen=True)
class Match:
    scrutinee: "Expr"
    clauses: tuple[MatchClause, ...]
    line: int = 0
    column: int = 0


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
    PROGRAM_DECLARATIONS.demand(tuple(forms), "the source", 1, 1)
    types: dict[str, object] = {}
    functions: dict[str, Function] = {}
    declared: list[DeclaredName] = []
    for form in forms:
        head = _head_symbol(form)
        if head == "deftype":
            type_decl = _parse_type_decl(form)
            types[type_decl.name] = type_decl
            declared.extend(_declared_names_of_type(form, type_decl))
        elif head == "defn":
            function = _parse_function_decl(form)
            functions[function.name] = function
            declared.append(
                DeclaredName("function", function.name, *_position(form.items[1]))
            )
        else:
            line, column = _position(form)
            raise SyntaxError_(
                f"expected a top-level 'deftype' or 'defn' form, found {head!r}",
                line,
                column,
            )
    return Program(
        types=types,
        functions=functions,
        declarations=Declarations(tuple(declared)),
    )


def _declared_names_of_type(form: SList, type_decl: RecordType | UnionType) -> list[DeclaredName]:
    """Every name one `deftype` form declares: the type, the
    constructors it introduces -- a record introduces one of its own
    name, a union one per variant -- and the fields of each of them."""
    line, column = _position(form.items[1])
    names = [DeclaredName("type", type_decl.name, line, column)]
    body = form.items[2]
    if isinstance(type_decl, RecordType):
        names.append(DeclaredName("constructor", type_decl.name, line, column))
        names += _declared_field_names(body.items[1:], f"record {type_decl.name!r}")
        return names
    for variant_node in body.items[1:]:
        variant_name = variant_node.items[0].text
        names.append(
            DeclaredName("constructor", variant_name, *_position(variant_node.items[0]))
        )
        names += _declared_field_names(
            variant_node.items[1:],
            f"variant {variant_name!r} of union {type_decl.name!r}",
        )
    return names


def _declared_field_names(nodes: list[SList], within: str) -> list[DeclaredName]:
    return [
        DeclaredName("field", node.items[0].text, *_position(node.items[0]), within=within)
        for node in nodes
    ]


def _position(node: object) -> tuple[int, int]:
    if isinstance(node, (Atom, SList)):
        return node.line, node.column
    return 0, 0


def _head_symbol(node: object) -> str | None:
    if isinstance(node, SList) and node.items and isinstance(node.items[0], Atom):
        return node.items[0].text
    return None


def _parse_type_decl(form: SList) -> RecordType | UnionType:
    name = TypeName.read("type name", form.items[1]).text
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
    name = TypeName.read("constructor name", node.items[0]).text
    fields = tuple(_parse_field(f) for f in node.items[1:])
    return Variant(name, fields)


def _parse_signature(node: SList) -> Signature:
    """The declared parameters and return type of one signature, read
    through the marker tokens core-0 fixes, never by position alone: a
    signature that carries another token, or none, is refused where it
    stands instead of being read as if the tokens were there."""
    line, column = _position(node)
    within = "a signature"
    params_list = _item_at(node, 1)
    if not isinstance(params_list, SList):
        raise SyntaxError_(
            f"{within} must carry a parameter list after 'sig': without it the "
            "tool cannot tell a parameter from a return type; write the signature "
            "as (sig (parameters) -> Type ! pure)",
            line,
            column,
        )
    params = tuple(_parse_parameter(p) for p in params_list.items)
    RETURN_ARROW.demand(_item_at(node, 2), within, line, column)
    # A use of a type name, not a declaration of one: whether the type
    # exists stays the checker's answer, as it is for a parameter type.
    return_type = _symbol_text("return type", _item_at(node, 3))
    EFFECT_MARKER.demand(_item_at(node, 4), within, line, column)
    PURE_EFFECT.demand(_item_at(node, 5), within, line, column)
    if len(node.items) > 6:
        raise SyntaxError_(
            f"{within} carries {len(node.items) - 6} form(s) after its effect: a "
            "signature ends with its effect, so the tool cannot tell what they "
            "would mean; remove them from the signature",
            line,
            column,
        )
    return Signature(params, return_type)


def _item_at(node: SList, index: int) -> object | None:
    return node.items[index] if index < len(node.items) else None


def _parse_parameter(node: SList) -> tuple[str, str]:
    """One declared parameter: its name, spelled as core-0 spells a
    value name, and its declared type."""
    return ValueName.read("parameter name", node.items[0]).text, node.items[1].text


def _parse_function_decl(form: SList) -> Function:
    name = ValueName.read("function name", form.items[1]).text
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

    if not rest or _head_symbol(rest[0]) != "examples":
        raise SyntaxError_(
            f"function {name!r} must declare an examples clause "
            "(examples ...) before its body",
            *_position(form),
        )
    if len(rest) != 2:
        raise SyntaxError_(
            f"function {name!r} must have exactly one body expression after its examples clause",
            *_position(form),
        )
    examples = _parse_examples(rest[0], name)
    body = parse_expr(rest[1])
    return Function(name, signature, requires, ensures, examples, body)


def _parse_examples(node: SList, function_name: str) -> tuple[Example, ...]:
    declared = FUNCTION_EXAMPLES.demand(
        tuple(node.items[1:]),
        f"the examples clause of function {function_name!r}",
        *_position(node),
    )
    return tuple(_parse_example(e) for e in declared)


def _parse_example(node: object) -> Example:
    if not (
        isinstance(node, SList)
        and len(node.items) == 4
        and isinstance(node.items[1], SList)
        and node.items[1].items
        and isinstance(node.items[1].items[0], Atom)
    ):
        raise SyntaxError_(
            "a declared example must have the shape (example (f args...) -> expected)",
            *_position(node),
        )
    EXAMPLE_ARROW.demand(node.items[2], "a declared example", *_position(node))
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
    if not isinstance(head, Atom):
        raise SyntaxError_("a value's constructor name must be a symbol", *_position(node))
    constructor_name = head.text
    fields = tuple(parse_value(v) for v in node.items[1:])
    return ConstructorValue(constructor_name, fields)


# --- parsing: expressions ---------------------------------------------------

def parse_expr(node: object) -> Expr:
    if isinstance(node, Atom):
        if node.text == "true":
            return BoolLit(True, node.line, node.column)
        if node.text == "false":
            return BoolLit(False, node.line, node.column)
        if node.is_int:
            return IntLit(node.int_value, node.line, node.column)
        return NameRef(node.text, node.line, node.column)

    assert isinstance(node, SList)
    line, column = node.line, node.column
    if not node.items:
        return UnitLit(line, column)

    head = node.items[0]
    if not isinstance(head, Atom):
        raise SyntaxError_("a call's head must be a symbol", *_position(node))
    name = head.text

    if name == "let":
        bindings = tuple(
            (b.items[0].text, parse_expr(b.items[1])) for b in node.items[1].items
        )
        body = parse_expr(node.items[2])
        return Let(bindings, body, line, column)

    if name == "if":
        return If(
            parse_expr(node.items[1]),
            parse_expr(node.items[2]),
            parse_expr(node.items[3]),
            line,
            column,
        )

    if name == "match":
        scrutinee = parse_expr(node.items[1])
        clauses = tuple(_parse_clause(c) for c in node.items[2:])
        return Match(scrutinee, clauses, line, column)

    if name.startswith("."):
        target = parse_expr(node.items[1])
        return FieldAccess(name[1:], target, line, column)

    args = tuple(parse_expr(a) for a in node.items[1:])
    if name in OPERATORS:
        return OperatorCall(name, args, line, column)
    if name[0].isupper():
        return ConstructorCall(name, args, line, column)
    return Call(name, args, line, column)


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
