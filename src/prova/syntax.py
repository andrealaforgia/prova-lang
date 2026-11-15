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
        "ensures", "examples", "example", "true", "false",
        # 'result' is not here: SPEC.md reserves it for the value a
        # postcondition speaks about, which is a rule about what a name
        # binds, not about how a name is spelled. The checker owns it and
        # publishes it as its own refusal, so the spelling rule lets it
        # through and leaves that answer to the one owner of the rule.
    }
) | frozenset(SPECIAL_FORMS)
RESERVED_WORDS = CORE_KEYWORDS | frozenset(OPERATORS)

# The builtin type names core-0 reserves. checker.BUILTIN_TYPES holds the
# same three names for its own rule about a redeclared type; the two are
# not yet one set, because the delivery running beside this one owns that
# file. Reconciling them is one line once that file is free.
BUILTIN_TYPE_NAMES = frozenset({"Unit", "Bool", "Int"})


class SyntaxError_(Exception):
    def __init__(self, message: str, line: int = 0, column: int = 0):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column


class UnsupportedConstruct(Exception):
    """A construct core-0 does not have, met in the source.

    A different answer from `SyntaxError_`: that one says the tool cannot
    read the source as a core-0 program, and a reader repairs it by
    writing the form the way core-0 writes it. This one says core-0 has
    no such construct at all, so no spelling repairs it and the reader
    must stop writing it (SPEC.md lines 51-54, 96-99).

    It carries the `OutOfProfileConstruct` that met the source, not a
    name copied out of it, so what the refusal says is outside the
    profile is what the profile itself declares and can be nothing else.
    """

    def __init__(
        self,
        message: str,
        construct: OutOfProfileConstruct,
        line: int,
        column: int,
    ):
        super().__init__(message)
        self.message = message
        self.construct = construct
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
    refused_words: frozenset = frozenset()

    SHAPE: ClassVar[re.Pattern] = re.compile(r"[A-Z][A-Za-z0-9]*$")

    def __post_init__(self) -> None:
        if self.text in self.refused_words:
            raise SyntaxError_(
                f"the {self.role} {self.text!r} is one of the builtin type names "
                f"core-0 reserves ({', '.join(sorted(self.refused_words))}): a "
                "reserved type name already means a builtin type wherever it "
                "appears, so a declaration cannot introduce it again; give the "
                "constructor a name of its own, such as 'Whole'",
                self.line,
                self.column,
            )
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

    @classmethod
    def read_constructor(cls, node: object) -> "TypeName":
        """A declared constructor name, which may not be one of the
        builtin type names core-0 reserves (SPEC.md line 74)."""
        role = "constructor name"
        return cls(
            role,
            _symbol_text(role, node),
            *_position(node),
            refused_words=BUILTIN_TYPE_NAMES,
        )


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
MATCH_CLAUSES = AtLeastOne(
    "clause",
    "write it as (match expr (pattern expr) ...)",
)


# --- what core-0 does not have ------------------------------------------

@dataclass(frozen=True)
class OutOfProfileConstruct:
    """One construct core-0 does not have: the name a caller sorts it
    by, what is absent that makes it meaningless here, and how to write
    the same intent with what core-0 does have.

    `name` is the stable word the response carries beside the sentence,
    so a caller tells the kinds apart without reading prose.

    Mirrors `MarkerToken`, which owns one token core-0 fixes at a single
    grammar position. This owns a construct core-0 fixes nowhere at all,
    and builds its own refusal, so no caller composes that sentence.
    """

    name: str
    absence: str
    repair: str

    def refuse(self, named: str, line: int, column: int) -> UnsupportedConstruct:
        return UnsupportedConstruct(
            f"{named} is unsupported in the core-0 profile: {self.absence}; "
            f"{self.repair}",
            self,
            line,
            column,
        )


DIVISION = OutOfProfileConstruct(
    "division",
    "core-0 declares no division operator, so the tool can give it no meaning "
    "here",
    "write the calculation with an operator core-0 has, '+', '-' or '*'; exact "
    "division arrives with a later numeric profile",
)
DECIMAL_LITERAL = OutOfProfileConstruct(
    "decimal_literal",
    "the core-0 literals are 'true', 'false', the unit value '()' and whole "
    "numbers",
    "write a whole number, such as 1; decimal arithmetic arrives with a later "
    "numeric profile",
)
TEXT_LITERAL = OutOfProfileConstruct(
    "text_literal",
    "core-0 has no text values and no operator that reads one",
    "remove it, or say what it stands for with a type core-0 declares; text "
    "arrives with a later profile",
)
TOP_LEVEL_EXPRESSION = OutOfProfileConstruct(
    "top_level_expression",
    "core-0 writes only 'deftype' and 'defn' forms at the top level, so a call "
    "written beside them has no place to run",
    "move the call into a function body, or ask for it with the 'evaluate' "
    "operation",
)
DECLARATION_FORM = OutOfProfileConstruct(
    "declaration_form",
    "core-0 declares only 'deftype' and 'defn'",
    "write the declaration as (defn name (sig (parameters) -> Type ! pure) "
    "(examples (example (name arguments) => value)) body)",
)

# The declaration words of the historical language that core-0 leaves out
# (SPEC.md lines 96-99). Each one is a word a reader may well have meant,
# so each is answered by name.
OUT_OF_PROFILE_DECLARATION_WORDS = frozenset({"defspec", "fn", "trust", "module"})

DIVISION_SIGN = "/"
TEXT_OPENING = '"'
DECIMAL_SHAPE = re.compile(r"[+-]?(?:[0-9]+\.[0-9]*|\.[0-9]+)$")

DECLARATION_WORDS = ("deftype", "defn")


@dataclass(frozen=True)
class ProfileBoundary:
    """What core-0 does not have, read over one source before its typed
    tree is built.

    It holds the function names that source declares, and that is what
    lets it tell a call written after the declarations -- the trailing
    top-level expression core-0 does not have -- from a declaration word
    the reader simply cannot place, which is a misspelling that its own
    refusal already answers.
    """

    declared_functions: frozenset

    @classmethod
    def of(cls, forms: tuple) -> ProfileBoundary:
        return cls(frozenset(_declared_function_names(forms)))

    def refuse_what_core_0_does_not_have(self, forms: tuple) -> None:
        """Refuse the first construct core-0 does not have, in source
        order; return when the source uses only what core-0 has.

        Read before the typed tree is built, so an out-of-profile source
        never reaches the spelling rules or the checker and cannot be
        answered as a misspelling or a type error.
        """
        for form in forms:
            self._read_top_level(form)
            self._read_every_token(form)

    def _read_top_level(self, form: object) -> None:
        head = _head_symbol(form)
        if head in DECLARATION_WORDS:
            return
        line, column = _position(form)
        if head in OUT_OF_PROFILE_DECLARATION_WORDS:
            raise DECLARATION_FORM.refuse(
                f"the declaration form {head!r}", line, column
            )
        if self._is_an_expression(form, head):
            raise TOP_LEVEL_EXPRESSION.refuse(
                self._named_expression(form, head), line, column
            )

    def _is_an_expression(self, form: object, head: object) -> bool:
        """Whether a top-level form that declares nothing is recognisably
        an expression a reader meant to write.

        A form whose head is not a symbol -- a parenthesised group, or a
        form wrapped in one pair of parentheses too many -- is not one:
        it is a misplaced parenthesis, which the reader repairs by moving
        it, so it keeps the refusal that already owns it. The same holds
        for a word the reader cannot place at all.
        """
        if head is None:
            return isinstance(form, Atom)
        if head in OPERATORS or head in SPECIAL_FORMS:
            return True
        if head.startswith(".") or head[:1].isupper():
            return True
        return head in self.declared_functions

    @staticmethod
    def _named_expression(form: object, head: object) -> str:
        if head is None:
            return f"the top-level expression {form.text!r}"
        return f"the top-level expression calling {head!r}"

    def _read_every_token(self, node: object) -> None:
        if isinstance(node, Atom):
            self._read_token(node)
            return
        for item in node.items:
            self._read_every_token(item)

    @staticmethod
    def _read_token(atom: Atom) -> None:
        if atom.text == DIVISION_SIGN:
            raise DIVISION.refuse(f"the operator {atom.text!r}", atom.line, atom.column)
        if DECIMAL_SHAPE.match(atom.text):
            raise DECIMAL_LITERAL.refuse(
                f"the decimal literal {atom.text!r}", atom.line, atom.column
            )
        if atom.text.startswith(TEXT_OPENING):
            raise TEXT_LITERAL.refuse(
                f"the text literal {atom.text!r}", atom.line, atom.column
            )


def _declared_function_names(forms: tuple) -> list:
    """The name of every function the source declares, read before
    anything else, because core-0 allows forward references."""
    return [
        form.items[1].text
        for form in forms
        if _head_symbol(form) == "defn"
        and len(form.items) > 1
        and isinstance(form.items[1], Atom)
    ]


def _symbol_text(role: str, node: object) -> str:
    if isinstance(node, Atom):
        return node.text
    raise SyntaxError_(
        f"the {role} must be one symbol, but a form stands there: a core-0 name is "
        "a single symbol; write one name in that position",
        *_position(node),
    )


# --- declarations -----------------------------------------------------

# Every declaration below carries the place of the form it was read
# from, as the expressions further down already do: a reader of a
# declaration is owed the line to open, and a part of the tree that
# cannot say where it stands cannot be published either.

@dataclass(frozen=True)
class RecordType:
    name: str
    fields: tuple[tuple[str, str], ...]
    line: int
    column: int


@dataclass(frozen=True)
class Variant:
    name: str
    fields: tuple[tuple[str, str], ...]
    line: int
    column: int


@dataclass(frozen=True)
class UnionType:
    name: str
    variants: tuple[Variant, ...]
    line: int
    column: int


@dataclass(frozen=True)
class Parameter:
    """One parameter as a function declares it: the name it binds, the
    type it declares for it, and the place that name stands at.

    A pair of strings said neither which of the two was the name nor
    where either stood; a caller that needs the place had to go back to
    the source for it.
    """

    name: str
    type_name: str
    line: int
    column: int


@dataclass(frozen=True)
class Signature:
    params: tuple[Parameter, ...]
    return_type: str
    # A signature, an example and a function below keep a place of their
    # own only when they were read from a source: a caller that builds a
    # program in memory, as the obligation inventory's own tests do, has
    # no text to point into. Every part that is published carries a place
    # it cannot be built without.
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class Example:
    function: str
    args: tuple[object, ...]
    expected: object
    line: int = 0
    column: int = 0


@dataclass(frozen=True)
class Function:
    name: str
    signature: Signature
    requires: tuple["Expr", ...]
    ensures: tuple["Expr", ...]
    examples: tuple[Example, ...]
    body: "Expr"
    line: int = 0
    column: int = 0


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


@dataclass(frozen=True)
class DeclaredConstructor:
    """One constructor as a program declares it: the type that owns it
    and the fields it carries.

    The one answer to how many values a constructor takes. Every rule
    that compares that number with the number a program writes asks here
    instead of counting the fields itself, so a rule about a constructor
    written in an expression and a rule about one written as a value can
    never disagree about the same declaration.

    It holds the three parts of one declaration rather than two, which
    keeps the name beside what the name resolves to: a reader of a
    refusal is shown the constructor it wrote and the type that owns it
    in the same breath, and splitting them would add a collaborator no
    rule asks for.
    """

    name: str
    owner: str
    fields: tuple[tuple[str, str], ...]

    @classmethod
    def of(cls, constructor: str, program: Program) -> "DeclaredConstructor | None":
        """What `program` declares `constructor` to be, or `None` when it
        declares no record type and no union variant of that name."""
        resolved = resolve_constructor(constructor, program)
        if resolved is None:
            return None
        owner, fields = resolved
        return cls(constructor, owner, fields)

    def takes(self) -> int:
        """How many values this constructor is written with."""
        return len(self.fields)

    def disagrees_with(self, written: int) -> bool:
        """Whether a program writing this constructor with `written`
        values wrote the wrong number of them."""
        return self.takes() != written


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
class Binding:
    """One binding of a 'let': the name it binds, the expression bound to
    it, and the place the binding stands at."""

    name: str
    value: "Expr"
    line: int
    column: int


@dataclass(frozen=True)
class Let:
    bindings: tuple[Binding, ...]
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
    line: int
    column: int


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
    line: int
    column: int


@dataclass(frozen=True)
class PatVar:
    name: str
    line: int
    column: int


@dataclass(frozen=True)
class PatInt:
    value: int
    line: int
    column: int


@dataclass(frozen=True)
class PatBool:
    value: bool
    line: int
    column: int


@dataclass(frozen=True)
class PatUnit:
    line: int
    column: int


@dataclass(frozen=True)
class PatConstructor:
    name: str
    subpatterns: tuple["Pattern", ...]
    line: int
    column: int


Pattern = object


# --- parsing: declarations -------------------------------------------------

def parse_program(forms: list[object]) -> Program:
    declarations = PROGRAM_DECLARATIONS.demand(tuple(forms), "the source", 1, 1)
    ProfileBoundary.of(declarations).refuse_what_core_0_does_not_have(declarations)
    types: dict[str, object] = {}
    functions: dict[str, Function] = {}
    declared: list[DeclaredName] = []
    for form in declarations:
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


_DEFTYPE_REPAIR = (
    "write it as (deftype TypeName (record (field Type) ...)) or "
    "(deftype TypeName (union (Constructor (field Type) ...) ...))"
)


def _parse_type_decl(form: SList) -> RecordType | UnionType:
    name = TypeName.read(
        "type name",
        _required_at(form, 1, "the type name of a 'deftype' form", _DEFTYPE_REPAIR),
    ).text
    body = _required_list_at(form, 2, f"the body of type {name!r}", _DEFTYPE_REPAIR)
    kind = _symbol_text(
        f"the kind of type {name!r}",
        _required_at(
            body, 0, f"the kind ('record' or 'union') of type {name!r}", _DEFTYPE_REPAIR
        ),
    )
    if kind == "record":
        fields = tuple(_parse_field(f) for f in body.items[1:])
        return RecordType(name, fields, *_position(form))
    if kind == "union":
        variants = tuple(_parse_variant(v) for v in body.items[1:])
        return UnionType(name, variants, *_position(form))
    raise SyntaxError_(f"expected 'record' or 'union', found {kind!r}", *_position(body))


def _parse_field(node: object) -> tuple[str, str]:
    return _parse_pair(node, "a declared field", None)


def _parse_variant(node: object) -> Variant:
    name = TypeName.read_constructor(
        _required_at(
            node,
            0,
            "the constructor name of a declared variant",
            "write each variant as (Constructor (field Type) ...)",
        )
    ).text
    fields = tuple(_parse_field(f) for f in node.items[1:])
    return Variant(name, fields, *_position(node))


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
    return Signature(params, return_type, line, column)


def _item_at(form: object, index: int) -> object | None:
    """What stands at `index` of `form`, or None when the source wrote
    nothing there -- or wrote no parenthesised form at all."""
    if isinstance(form, SList) and index < len(form.items):
        return form.items[index]
    return None


def _stands_there(node: object) -> str:
    if node is None:
        return "nothing stands there"
    if isinstance(node, Atom):
        return f"the symbol {node.text!r} stands there"
    return "a parenthesised form stands there"


def _member_count(node: object) -> str:
    count = len(node.items) if isinstance(node, SList) else 0
    return f"{count} member(s)"


def _required_at(form: object, index: int, what: str, repair: str) -> object:
    """What core-0 fixes at `index`, or a refusal placed where `form`
    stands when the source wrote nothing there."""
    item = _item_at(form, index)
    if item is None:
        raise SyntaxError_(
            f"{what} is missing: core-0 fixes what stands at that position, so the "
            f"tool cannot read the form without it; {repair}",
            *_position(form),
        )
    return item


def _required_list_at(form: object, index: int, what: str, repair: str) -> SList:
    item = _required_at(form, index, what, repair)
    if isinstance(item, SList):
        return item
    raise SyntaxError_(
        f"{what} must be a parenthesised form, but {_stands_there(item)}: core-0 "
        f"fixes what stands at that position; {repair}",
        *_position(item),
    )


def _parse_pair(node: object, within: str, name_role: str | None) -> tuple[str, str]:
    """One `(name type)` pair, the shape core-0 writes both a declared
    field and a declared parameter with.

    `name_role` names the position when its spelling is a rule of this
    profile, and is None where the spelling of the name is not read here.
    """
    if not isinstance(node, SList) or len(node.items) != 2:
        raise SyntaxError_(
            f"{within} must be written as one name and one type, as (name Type), "
            f"but {_stands_there(node)} with {_member_count(node)}: without both "
            "the tool cannot tell which word is the name and which is the type; "
            "write it as (name Type)",
            *_position(node),
        )
    name_node, type_node = node.items
    name = (
        ValueName.read(name_role, name_node).text
        if name_role is not None
        else _symbol_text("a field name", name_node)
    )
    return name, _symbol_text(f"the type of {name!r}", type_node)


def _parse_parameter(node: object) -> Parameter:
    """One declared parameter: its name, spelled as core-0 spells a
    value name, its declared type, and the place its name stands at."""
    name, type_name = _parse_pair(node, "a declared parameter", "parameter name")
    return Parameter(name, type_name, *_position(node.items[0]))


_DEFN_REPAIR = (
    "write it as (defn name (sig (parameters) -> Type ! pure) (examples "
    "(example (name arguments) => value)) body)"
)


def _parse_function_decl(form: SList) -> Function:
    name = ValueName.read(
        "function name",
        _required_at(form, 1, "the name of a 'defn' form", _DEFN_REPAIR),
    ).text
    signature = _parse_signature(
        _required_list_at(form, 2, f"the signature of function {name!r}", _DEFN_REPAIR)
    )
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
    return Function(
        name, signature, requires, ensures, examples, body, *_position(form)
    )


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
            "a declared example must have the shape "
            "(example (f arguments...) => expected)",
            *_position(node),
        )
    EXAMPLE_ARROW.demand(node.items[2], "a declared example", *_position(node))
    call = node.items[1]
    function_name = call.items[0].text
    args = tuple(parse_value(v) for v in call.items[1:])
    expected = parse_value(node.items[3])
    return Example(function_name, args, expected, *_position(node))


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
        repair = "write it as (let ((name expr) ...) expr)"
        bindings_node = _required_list_at(node, 1, "the bindings of a 'let'", repair)
        bindings = tuple(_parse_binding(b) for b in bindings_node.items)
        body = parse_expr(_required_at(node, 2, "the body of a 'let'", repair))
        return Let(bindings, body, line, column)

    if name == "if":
        repair = "write it as (if condition then-expr else-expr)"
        return If(
            parse_expr(_required_at(node, 1, "the condition of an 'if'", repair)),
            parse_expr(_required_at(node, 2, "the then-branch of an 'if'", repair)),
            parse_expr(_required_at(node, 3, "the else-branch of an 'if'", repair)),
            line,
            column,
        )

    if name == "match":
        repair = "write it as (match expr (pattern expr) ...)"
        scrutinee = parse_expr(
            _required_at(node, 1, "the value a 'match' examines", repair)
        )
        clauses = tuple(
            _parse_clause(c)
            for c in MATCH_CLAUSES.demand(
                tuple(node.items[2:]), "a 'match'", line, column
            )
        )
        return Match(scrutinee, clauses, line, column)

    if name.startswith("."):
        target = parse_expr(
            _required_at(
                node,
                1,
                f"the value the selector {name!r} reads",
                "write it as (.field-name expr)",
            )
        )
        return FieldAccess(name[1:], target, line, column)

    args = tuple(parse_expr(a) for a in node.items[1:])
    if name in OPERATORS:
        return OperatorCall(name, args, line, column)
    if name[0].isupper():
        return ConstructorCall(name, args, line, column)
    return Call(name, args, line, column)


def _parse_binding(node: object) -> Binding:
    """One `let` binding: the name it binds and the expression it binds
    to that name."""
    if not isinstance(node, SList) or len(node.items) != 2:
        raise SyntaxError_(
            "a 'let' binding must be written as one name and one expression, as "
            f"(name expr), but {_stands_there(node)} with {_member_count(node)}: "
            "without both the tool cannot tell what is bound to what; write each "
            "binding as (name expr)",
            *_position(node),
        )
    name_node, value_node = node.items
    return Binding(
        _symbol_text("the name of a 'let' binding", name_node),
        parse_expr(value_node),
        *_position(node),
    )


def _parse_clause(node: object) -> MatchClause:
    if not isinstance(node, SList) or len(node.items) != 2:
        raise SyntaxError_(
            "a 'match' clause must be written as one pattern and one expression, "
            f"as (pattern expr), but {_stands_there(node)} with "
            f"{_member_count(node)}: without both the tool cannot tell which "
            "pattern answers with which expression; write each clause as "
            "(pattern expr)",
            *_position(node),
        )
    pattern = _parse_pattern(node.items[0])
    body = parse_expr(node.items[1])
    return MatchClause(pattern, body, *_position(node))


def _parse_pattern(node: object) -> Pattern:
    place = _position(node)
    if isinstance(node, Atom):
        if node.text == "_":
            return PatWildcard(*place)
        if node.text == "true":
            return PatBool(True, *place)
        if node.text == "false":
            return PatBool(False, *place)
        if node.is_int:
            return PatInt(node.int_value, *place)
        return PatVar(node.text, *place)
    assert isinstance(node, SList)
    if not node.items:
        return PatUnit(*place)
    name = _symbol_text("the constructor of a pattern", node.items[0])
    subpatterns = tuple(_parse_pattern(p) for p in node.items[1:])
    return PatConstructor(name, subpatterns, *place)
