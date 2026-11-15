"""The tree a client is answered with, and the schema that names its kinds.

The one place that knows how the typed tree of `syntax.py` is written for
a reader outside this tool. `syntax.py` owns the tree the checker walks
and learns no wire format from here; `service.py` owns operations and
answers and learns no shape of a tree.

Every node carries the kind it is and the place it stands at, so an agent
that reads the tree can open the exact line any part of it was written
on. The kinds the manifest publishes and the kinds this module answers
are one table, so a kind can never be answered without being published.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from prova import syntax
from prova.reader import Comment
from prova.values import render


@dataclass(frozen=True, order=True)
class Place:
    """The line and the column a node stands at, counted as the reader
    counts them: line 1 column 1 at the first character of a source.

    A place that stands before line 1 column 1 is no place in any text,
    so it cannot be built: a node that carried one would send a reader
    of the tree to a line that does not exist.
    """

    line: int
    column: int

    def __post_init__(self) -> None:
        if self.line < 1 or self.column < 1:
            raise ValueError(
                f"line {self.line} column {self.column} is no place in a "
                "source: places are counted from line 1 column 1, and a node "
                "carrying one outside that would send a reader of the tree to "
                "a line no source has; build the place from the form the node "
                "was read from"
            )

    @classmethod
    def of(cls, node: object) -> "Place":
        """Where `node` stands, read from the form the reader placed."""
        return cls(node.line, node.column)

    def published(self) -> dict:
        return {"line": self.line, "column": self.column}


class AttachedComments:
    """Every comment of one source, handed out to the nodes that follow
    them.

    A comment belongs to the first node standing after it, so the walk
    that publishes the tree asks here as it reaches each node, in the
    order it reaches them -- outermost first, and in source order within
    each node. What is left when the walk ends is what no node follows,
    and belongs to the end of the document.
    """

    def __init__(self, comments: tuple[Comment, ...]) -> None:
        self._pending = list(comments)

    def standing_before(self, place: Place) -> tuple[Comment, ...]:
        taken: list[Comment] = []
        while self._pending and Place.of(self._pending[0]) < place:
            taken.append(self._pending.pop(0))
        return tuple(taken)

    def left_over(self) -> tuple[Comment, ...]:
        return tuple(self._pending)


@dataclass(frozen=True)
class PublishedNode:
    """One node of the published tree: the kind it is, the place it
    stands at, and the parts it carries, in the order the source writes
    them.

    It is built with a place or not at all, which is what makes the
    promise that every node of an answered tree says where it stands
    true by construction rather than by remembering.
    """

    kind: str
    place: Place
    parts: tuple[tuple[str, object], ...] = ()

    def published(self, comments: AttachedComments) -> dict:
        """This node and everything under it, with the comments that
        stand before each of them attached.

        The comments of this node are taken before its parts are
        published, so the first node after a comment is the one that
        gets it.
        """
        standing = comments.standing_before(self.place)
        entry: dict = {"kind": self.kind, "position": self.place.published()}
        if standing:
            entry["comments"] = [_comment(written).published(comments) for written in standing]
        for name, part in self.parts:
            entry[name] = _published_part(part, comments)
        return entry


def _published_part(part: object, comments: AttachedComments) -> object:
    if isinstance(part, PublishedNode):
        return part.published(comments)
    if isinstance(part, tuple) and all(isinstance(one, PublishedNode) for one in part):
        return [one.published(comments) for one in part]
    return part


@dataclass(frozen=True)
class NodeKind:
    """One kind of node this tool answers: its name, and what a node of
    that kind carries beside its kind and its place."""

    name: str
    carries: dict[str, str] = field(default_factory=dict)

    def published(self) -> dict:
        return {"carries": dict(self.carries)}


@dataclass(frozen=True)
class TreeSchema:
    """The kinds of node a published tree holds, and what each one
    carries.

    The manifest publishes this table and the builder below answers from
    it, so a kind an agent meets is always a kind it can look up.
    """

    kinds: tuple[NodeKind, ...]

    def names(self) -> tuple[str, ...]:
        return tuple(kind.name for kind in self.kinds)

    def published(self) -> dict:
        return {
            "node": (
                "Every node carries 'kind', which says what it is, and "
                "'position', which says where it stands. A node carries the "
                "parts its kind declares below, in the order the source "
                "writes them."
            ),
            "position": (
                "The line and the column the form the node was read from "
                "starts at, counted from line 1 column 1, with the column "
                "counted again from 1 after each line break."
            ),
            "comments": (
                "The comments written before a node stand on it, under "
                "'comments', each one a node of kind 'comment' carrying the "
                "characters from its ';' to the end of its line. The key is "
                "absent when a node carries none. A comment that no node "
                "follows stands on the program, under 'trailing_comments'."
            ),
            "kinds": {kind.name: kind.published() for kind in self.kinds},
        }


SCHEMA = TreeSchema(
    (
        NodeKind(
            "program",
            {
                "declarations": "every declaration of the source, in source order",
                "trailing_comments": "the comments no node follows, absent when there are none",
            },
        ),
        NodeKind("comment", {"text": "the characters written, from the ';' to the end of the line"}),
        NodeKind("record_type", {"name": "the declared type name", "fields": "the fields it declares"}),
        NodeKind("union_type", {"name": "the declared type name", "variants": "the variants it declares"}),
        NodeKind("variant", {"name": "the constructor it declares", "fields": "the fields it carries"}),
        NodeKind("field", {"name": "the field name", "type": "the type name declared for it"}),
        NodeKind(
            "function",
            {
                "name": "the declared function name",
                "signature": "its signature",
                "requires": "the conditions of its precondition, empty when it declares none",
                "ensures": "the conditions of its postcondition, empty when it declares none",
                "examples": "the examples it declares",
                "body": "the expression it answers with",
            },
        ),
        NodeKind(
            "signature",
            {
                "parameters": "the parameters it declares, in order",
                "return_type": "the type name it answers with",
                "effect": "the effect it declares, which core-0 writes as 'pure'",
            },
        ),
        NodeKind("parameter", {"name": "the parameter name", "type": "the type name declared for it"}),
        NodeKind(
            "example",
            {
                "function": "the function the example calls",
                "arguments": "the value of each argument, written as a program writes it",
                "expected": "the value it expects, written as a program writes it",
            },
        ),
        NodeKind("integer", {"value": "the whole number written"}),
        NodeKind("boolean", {"value": "true or false"}),
        NodeKind("unit", {}),
        NodeKind("name", {"name": "the name read"}),
        NodeKind("call", {"name": "the function called", "arguments": "the expressions passed to it"}),
        NodeKind("constructor", {"name": "the constructor written", "arguments": "the expressions it is written with"}),
        NodeKind("operator", {"operator": "the operator of core-0 written", "operands": "the expressions it reads"}),
        NodeKind("field_access", {"field": "the field read", "target": "the expression read from"}),
        NodeKind("let", {"bindings": "the names it binds, in order", "body": "the expression they are bound in"}),
        NodeKind("binding", {"name": "the name bound", "value": "the expression bound to it"}),
        NodeKind(
            "conditional",
            {
                "condition": "the expression decided on",
                "then_branch": "the expression answered when the condition is true",
                "else_branch": "the expression answered when it does not",
            },
        ),
        NodeKind("match", {"scrutinee": "the expression examined", "clauses": "the clauses, in source order"}),
        NodeKind("match_clause", {"pattern": "the pattern it answers for", "body": "the expression it answers with"}),
        NodeKind("pattern_wildcard", {}),
        NodeKind("pattern_name", {"name": "the name the pattern binds"}),
        NodeKind("pattern_integer", {"value": "the whole number matched"}),
        NodeKind("pattern_boolean", {"value": "true or false"}),
        NodeKind("pattern_unit", {}),
        NodeKind(
            "pattern_constructor",
            {"name": "the constructor matched", "subpatterns": "the patterns of its fields"},
        ),
    )
)


def tree_of(program: syntax.Program, comments: tuple[Comment, ...]) -> dict:
    """The published tree of `program`, with `comments` attached.

    The program stands at the start of the document, so a comment
    written above everything belongs to the first declaration and not to
    the program itself.
    """
    declarations = tuple(_declaration(declared, program) for declared in _in_source_order(program))
    standing = AttachedComments(comments)
    root = PublishedNode("program", Place(1, 1), (("declarations", declarations),))
    published = root.published(standing)
    left_over = standing.left_over()
    if left_over:
        published["trailing_comments"] = [
            _comment(written).published(standing) for written in left_over
        ]
    return published


def _in_source_order(program: syntax.Program) -> tuple[object, ...]:
    """Every declaration of `program`, in the order the source writes
    them: the lookup tables keep types and functions apart, and a source
    may write them interleaved."""
    declared = (*program.types.values(), *program.functions.values())
    return tuple(sorted(declared, key=lambda one: (one.line, one.column)))


def _comment(written: Comment) -> PublishedNode:
    return PublishedNode("comment", Place.of(written), (("text", written.text),))


def _declaration(declared: object, program: syntax.Program) -> PublishedNode:
    if isinstance(declared, syntax.RecordType):
        return PublishedNode(
            "record_type",
            Place.of(declared),
            (
                ("name", declared.name),
                ("fields", _fields(declared.fields, syntax.within_record(declared.name), program)),
            ),
        )
    if isinstance(declared, syntax.UnionType):
        return PublishedNode(
            "union_type",
            Place.of(declared),
            (
                ("name", declared.name),
                (
                    "variants",
                    tuple(_variant(variant, declared, program) for variant in declared.variants),
                ),
            ),
        )
    return _function(declared)


def _variant(
    variant: syntax.Variant, union: syntax.UnionType, program: syntax.Program
) -> PublishedNode:
    return PublishedNode(
        "variant",
        Place.of(variant),
        (
            ("name", variant.name),
            (
                "fields",
                _fields(
                    variant.fields,
                    syntax.within_variant(variant.name, union.name),
                    program,
                ),
            ),
        ),
    )


def _fields(
    fields: tuple[tuple[str, str], ...], within: str, program: syntax.Program
) -> tuple[PublishedNode, ...]:
    """The fields of one record or variant, each standing where the
    source writes its name.

    The place comes from the table of declared names the program already
    owns, which is the one answer to where a declared name stands.
    """
    return tuple(
        PublishedNode(
            "field",
            Place(*program.declarations.place_of("field", name, within)),
            (("name", name), ("type", type_name)),
        )
        for name, type_name in fields
    )


def _function(declared: syntax.Function) -> PublishedNode:
    return PublishedNode(
        "function",
        Place.of(declared),
        (
            ("name", declared.name),
            ("signature", _signature(declared.signature)),
            ("requires", tuple(_expression(one) for one in declared.requires)),
            ("ensures", tuple(_expression(one) for one in declared.ensures)),
            ("examples", tuple(_example(one) for one in declared.examples)),
            ("body", _expression(declared.body)),
        ),
    )


def _signature(signature: syntax.Signature) -> PublishedNode:
    return PublishedNode(
        "signature",
        Place.of(signature),
        (
            ("parameters", tuple(_parameter(one) for one in signature.params)),
            ("return_type", signature.return_type),
            ("effect", "pure"),
        ),
    )


def _parameter(parameter: syntax.Parameter) -> PublishedNode:
    return PublishedNode(
        "parameter",
        Place.of(parameter),
        (("name", parameter.name), ("type", parameter.type_name)),
    )


def _example(example: syntax.Example) -> PublishedNode:
    return PublishedNode(
        "example",
        Place.of(example),
        (
            ("function", example.function),
            ("arguments", [render(one) for one in example.args]),
            ("expected", render(example.expected)),
        ),
    )


def _expression(expr: object) -> PublishedNode:
    kind, parts = _EXPRESSIONS[type(expr)](expr)
    return PublishedNode(kind, Place.of(expr), parts)


def _binding(binding: syntax.Binding) -> PublishedNode:
    return PublishedNode(
        "binding",
        Place.of(binding),
        (("name", binding.name), ("value", _expression(binding.value))),
    )


def _clause(clause: syntax.MatchClause) -> PublishedNode:
    return PublishedNode(
        "match_clause",
        Place.of(clause),
        (("pattern", _pattern(clause.pattern)), ("body", _expression(clause.body))),
    )


def _pattern(pattern: object) -> PublishedNode:
    kind, parts = _PATTERNS[type(pattern)](pattern)
    return PublishedNode(kind, Place.of(pattern), parts)


# What each node of the typed tree is published as: its kind, and the
# parts it carries in the order the source writes them. One table, so a
# node kind is added to the tree and to the schema in one place.
_EXPRESSIONS = {
    syntax.IntLit: lambda e: ("integer", (("value", e.value),)),
    syntax.BoolLit: lambda e: ("boolean", (("value", e.value),)),
    syntax.UnitLit: lambda e: ("unit", ()),
    syntax.NameRef: lambda e: ("name", (("name", e.name),)),
    syntax.Call: lambda e: (
        "call",
        (("name", e.name), ("arguments", tuple(_expression(a) for a in e.args))),
    ),
    syntax.ConstructorCall: lambda e: (
        "constructor",
        (("name", e.name), ("arguments", tuple(_expression(a) for a in e.args))),
    ),
    syntax.OperatorCall: lambda e: (
        "operator",
        (("operator", e.operator), ("operands", tuple(_expression(a) for a in e.args))),
    ),
    syntax.FieldAccess: lambda e: (
        "field_access",
        (("field", e.field_name), ("target", _expression(e.target))),
    ),
    syntax.Let: lambda e: (
        "let",
        (
            ("bindings", tuple(_binding(b) for b in e.bindings)),
            ("body", _expression(e.body)),
        ),
    ),
    syntax.If: lambda e: (
        "conditional",
        (
            ("condition", _expression(e.condition)),
            ("then_branch", _expression(e.then_branch)),
            ("else_branch", _expression(e.else_branch)),
        ),
    ),
    syntax.Match: lambda e: (
        "match",
        (
            ("scrutinee", _expression(e.scrutinee)),
            ("clauses", tuple(_clause(c) for c in e.clauses)),
        ),
    ),
}

_PATTERNS = {
    syntax.PatWildcard: lambda p: ("pattern_wildcard", ()),
    syntax.PatVar: lambda p: ("pattern_name", (("name", p.name),)),
    syntax.PatInt: lambda p: ("pattern_integer", (("value", p.value),)),
    syntax.PatBool: lambda p: ("pattern_boolean", (("value", p.value),)),
    syntax.PatUnit: lambda p: ("pattern_unit", ()),
    syntax.PatConstructor: lambda p: (
        "pattern_constructor",
        (("name", p.name), ("subpatterns", tuple(_pattern(s) for s in p.subpatterns))),
    ),
}
