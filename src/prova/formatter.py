"""The one text a core-0 program is written as.

The only place that knows how a program is laid out for a person to
read. `syntax.py` owns the typed tree and learns no layout from here;
`service.py` owns operations and answers and learns none either;
`tree.py` owns the tree an agent walks as JSON, where a part carries its
place as two numbers and never as a column on a page.

The text is built from the typed tree and the comments the reader kept,
and from nothing else: no character of the submitted source reaches it.
That is what makes writing a program out twice answer the same text. Two
spellings of one program are written identically, because the layout is
decided by what the program declares and never by how wide a line has
grown -- so a text this module wrote is written again unchanged, by the
same rules that wrote it the first time.

SPEC.md lines 81-84 ask for a deterministic canonical rendering that is
idempotent and preserves meaning and comments, and for the layout to be
fixed in conformance fixtures before `format` ships. The fixtures are
published under conformance/format: each is a source a reader might
write beside the one text answered for it.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import syntax
from prova.reader import Comment
from prova.tree import AttachedComments, Place
from prova.values import UNIT, render


class WhenItHoldsABrokenPart:
    """How a form of core-0 is laid out, unless one of the two below
    says otherwise: on one line, unless something written inside it must
    stand over several lines of its own.

    Nothing here measures how wide a line has grown. A form is written
    over several lines because of what it holds, which is a fact about
    the program; a form written out twice therefore breaks the same way
    both times.
    """

    def breaks(self, parts: tuple[object, ...]) -> bool:
        return any(_breaks(part) for part in parts)

    def opens_with_the_first_part(self) -> bool:
        """Whether the part after the opening word may share the line
        the form opens on, which reads as `(match event` or `(let ((m n))`
        rather than leaving the word standing alone."""
        return True


class Always(WhenItHoldsABrokenPart):
    """How a `defn`, a `let`, an `if` and a `match` are laid out: over
    several lines whatever they hold.

    These are the forms a reader follows down the page rather than
    across it -- a function and its clauses, a binding and its body, a
    question and its two answers, a value and the clauses it is matched
    against -- so they are never squeezed onto one line.
    """

    def breaks(self, parts: tuple[object, ...]) -> bool:
        return True


class OnePartPerLine(Always):
    """How an examples clause is laid out: the word on its own, and then
    one example per line.

    An example is the one place a reader looks to see what a function
    answers, so each stands where it can be read and changed on its own.
    """

    def opens_with_the_first_part(self) -> bool:
        return False


WHEN_IT_HOLDS_A_BROKEN_PART = WhenItHoldsABrokenPart()
ALWAYS = Always()
ONE_PART_PER_LINE = OnePartPerLine()


@dataclass(frozen=True)
class Indent:
    """How far from the left margin a line of the canonical text stands.

    The one answer to what "further in" means, so every form that writes
    its parts under itself puts them at the same distance.
    """

    columns: int = 0

    def deeper(self) -> "Indent":
        return Indent(self.columns + 2)

    def before(self, written: str) -> str:
        return " " * self.columns + written


@dataclass(frozen=True)
class Form:
    """One parenthesised form of the canonical text: the parts written
    inside it, in the order a program writes them, and how it spreads
    over lines.

    It answers how it is written and over how many lines, so no caller
    ever composes a line itself and no second place decides whether a
    form fits on one.

    The first part is the word the form opens with -- `defn`, `let`, an
    operator, a constructor name, or the pattern of a match clause --
    and never stands over several lines, so the opening line of a form
    written over several can always be built.
    """

    parts: tuple[object, ...]
    layout: WhenItHoldsABrokenPart = WHEN_IT_HOLDS_A_BROKEN_PART

    def breaks(self) -> bool:
        return self.layout.breaks(self.parts)

    def flat(self) -> str:
        """This form and everything inside it, written on one line."""
        return "(" + " ".join(_flat(part) for part in self.parts) + ")"

    def written(self, indent: Indent) -> tuple[str, ...]:
        """The lines this form is written over, each already carrying
        the spaces that put it where it stands."""
        if not self.breaks():
            return (indent.before(self.flat()),)
        return self._over_several_lines(indent)

    def _over_several_lines(self, indent: Indent) -> tuple[str, ...]:
        opening = "(" + _flat(self.parts[0])
        under = self.parts[1:]
        if under and self.layout.opens_with_the_first_part() and not _breaks(under[0]):
            opening = f"{opening} {_flat(under[0])}"
            under = under[1:]
        lines = [indent.before(opening)]
        for part in under:
            lines.extend(_written(part, indent.deeper()))
        lines[-1] += ")"
        return tuple(lines)


@dataclass(frozen=True)
class CanonicalText:
    """The paragraphs one program is written as.

    The comments standing over a declaration and that declaration are
    one paragraph; the comments no declaration follows are the last one.
    This is the one answer to how a document opens and closes: exactly
    one empty line between two paragraphs, and exactly one line
    terminator at the end.
    """

    paragraphs: tuple[tuple[str, ...], ...]

    def rendered(self) -> str:
        return "\n\n".join("\n".join(lines) for lines in self.paragraphs) + "\n"


def canonical_text(program: syntax.Program, comments: tuple[Comment, ...]) -> str:
    """The one text `program` is written as, with `comments` standing
    where they belong.

    Takes what `tree.tree_of` takes, because it answers about the same
    two things: the program a source declares, and the prose written
    between its parts. This one is read by a person and that one by an
    agent.

    A comment stands over the declaration that follows it, and the
    comments no declaration follows stand at the end, which is what
    SPEC.md line 63 asks of a formatter. A comment written inside a
    declaration therefore rises to stand over the next one: the rule
    then finds it in the place it already put it, which is what makes
    writing the text out again change nothing.
    """
    standing = AttachedComments(comments)
    paragraphs = [
        _paragraph(declared, standing) for declared in program.in_source_order()
    ]
    left_over = standing.left_over()
    if left_over:
        paragraphs.append(tuple(written.text for written in left_over))
    return CanonicalText(tuple(paragraphs)).rendered()


def _paragraph(declared: object, standing: AttachedComments) -> tuple[str, ...]:
    """The comments written over one declaration, and the declaration
    itself, which a reader reads as one thing."""
    above = standing.standing_before(Place.of(declared))
    return tuple(written.text for written in above) + _declaration(declared).written(
        Indent()
    )


def _flat(part: object) -> str:
    return part if isinstance(part, str) else part.flat()


def _breaks(part: object) -> bool:
    return isinstance(part, Form) and part.breaks()


def _written(part: object, indent: Indent) -> tuple[str, ...]:
    if isinstance(part, str):
        return (indent.before(part),)
    return part.written(indent)


def _declaration(declared: object) -> Form:
    if isinstance(declared, syntax.RecordType):
        return Form(
            ("deftype", declared.name, Form(("record", *_fields(declared.fields))))
        )
    if isinstance(declared, syntax.UnionType):
        return Form(
            (
                "deftype",
                declared.name,
                Form(("union", *(_variant(one) for one in declared.variants))),
            )
        )
    return _function(declared)


def _fields(fields: tuple[tuple[str, str], ...]) -> tuple[Form, ...]:
    return tuple(Form((name, type_name)) for name, type_name in fields)


def _variant(variant: syntax.Variant) -> Form:
    return Form((variant.name, *_fields(variant.fields)))


def _function(declared: syntax.Function) -> Form:
    return Form(
        (
            "defn",
            declared.name,
            _signature(declared.signature),
            *_conditions("requires", declared.requires),
            *_conditions("ensures", declared.ensures),
            Form(
                ("examples", *(_example(one) for one in declared.examples)),
                ONE_PART_PER_LINE,
            ),
            _expression(declared.body),
        ),
        ALWAYS,
    )


def _conditions(word: str, conditions: tuple[object, ...]) -> tuple[Form, ...]:
    """The requires or the ensures clause of a function, or nothing at
    all where it declares none.

    A clause holding no condition is the empty conjunction, which is
    true, and SPEC.md line 204 says an omitted block means true: the two
    spell one thing. The typed tree cannot tell them apart in any case,
    so the canonical text writes the shorter of the two.
    """
    if not conditions:
        return ()
    return (Form((word, *(_expression(one) for one in conditions))),)


def _signature(signature: syntax.Signature) -> Form:
    return Form(
        (
            "sig",
            Form(tuple(Form((one.name, one.type_name)) for one in signature.params)),
            "->",
            signature.return_type,
            "!",
            "pure",
        )
    )


def _example(example: syntax.Example) -> Form:
    return Form(
        (
            "example",
            Form((example.function, *(render(one) for one in example.args))),
            "=>",
            render(example.expected),
        )
    )


def _expression(expr: object) -> object:
    return _EXPRESSIONS[type(expr)](expr)


def _binding(binding: syntax.Binding) -> Form:
    return Form((binding.name, _expression(binding.value)))


def _clause(clause: syntax.MatchClause) -> Form:
    return Form((_pattern(clause.pattern), _expression(clause.body)))


def _pattern(pattern: object) -> object:
    return _PATTERNS[type(pattern)](pattern)


# How each part of the typed tree is written: a word already written, or
# a form holding the parts inside it in the order a program writes them.
# A `let`, an `if` and a `match` carry the layout that always spreads
# them over lines, which is also what makes every form holding one of
# them spread.
#
# Every whole number, boolean and unit value is written by `values.render`,
# which already owns how a program writes a value: that is what makes
# `+002` come back as `2` without a second rule about spelling.
_EXPRESSIONS = {
    syntax.IntLit: lambda e: render(e.value),
    syntax.BoolLit: lambda e: render(e.value),
    syntax.UnitLit: lambda e: render(UNIT),
    syntax.NameRef: lambda e: e.name,
    syntax.Call: lambda e: Form((e.name, *(_expression(a) for a in e.args))),
    syntax.ConstructorCall: lambda e: Form(
        (e.name, *(_expression(a) for a in e.args))
    ),
    syntax.OperatorCall: lambda e: Form(
        (e.operator, *(_expression(a) for a in e.args))
    ),
    syntax.FieldAccess: lambda e: Form(
        (f".{e.field_name}", _expression(e.target))
    ),
    syntax.Let: lambda e: Form(
        (
            "let",
            Form(tuple(_binding(b) for b in e.bindings)),
            _expression(e.body),
        ),
        ALWAYS,
    ),
    syntax.If: lambda e: Form(
        (
            "if",
            _expression(e.condition),
            _expression(e.then_branch),
            _expression(e.else_branch),
        ),
        ALWAYS,
    ),
    syntax.Match: lambda e: Form(
        (
            "match",
            _expression(e.scrutinee),
            *(_clause(c) for c in e.clauses),
        ),
        ALWAYS,
    ),
}

_PATTERNS = {
    syntax.PatWildcard: lambda p: "_",
    syntax.PatVar: lambda p: p.name,
    syntax.PatInt: lambda p: render(p.value),
    syntax.PatBool: lambda p: render(p.value),
    syntax.PatUnit: lambda p: render(UNIT),
    syntax.PatConstructor: lambda p: Form(
        (p.name, *(_pattern(s) for s in p.subpatterns))
    ),
}
