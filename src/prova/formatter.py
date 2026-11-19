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
        return any(part.breaks() for part in parts)

    def opens_with_the_first_part(self) -> bool:
        """Whether the part after the opening word may share the line
        the form opens on, which reads as `(match event` or `(let ((m n))`
        rather than leaving the word standing alone.

        It may only when that part is itself written on one line; a part
        that must be written over several is never squeezed onto one to
        fit here, which would give one expression two layouts depending
        on where it was written.
        """
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
class Word:
    """A part of the canonical text written on one line whatever the
    program holds: a name, a whole number, a marker token, an operator,
    or a whole pattern -- which core-0 builds out of literals, names and
    constructors and never out of a `let`, an `if` or a `match`.

    It is also the only thing a form may open with, beside the NoWord
    below, which is what makes the opening line of a form written over
    several lines buildable at all: neither of the two can ever need a
    second line, so no opening is ever the thing that gets flattened.

    How much that is worth saying plainly. This repository runs no type
    checker, so the annotation on `Form.opening` proves nothing by
    itself. What keeps the rule is that every form is built in this
    module, by the builders below, and that a form handed to another
    form as its opening fails loudly rather than quietly: a Form answers
    no `opens`, so it raises where it is written rather than producing a
    flattened line. Centralised construction and a loud failure, not a
    proof.
    """

    text: str

    def breaks(self) -> bool:
        return False

    def flat(self) -> str:
        return self.text

    def opens(self) -> str:
        return self.text

    def written(self, indent: Indent) -> tuple[str, ...]:
        return (indent.before(self.text),)


class NoWord:
    """What a parenthesised list opens with where core-0 gives it no
    word of its own: the bindings of a `let` and the parameters of a
    signature are a list of forms and nothing else.

    A Null Object rather than an absent word, so a form opens the same
    way whether or not it has one to open with, and no reader of a form
    asks whether there is a word before deciding what to write.
    """

    def opens(self) -> str:
        return ""


NO_WORD = NoWord()


@dataclass(frozen=True)
class Form:
    """One parenthesised form of the canonical text: the word it opens
    with, the parts written inside it in the order a program writes
    them, and how it spreads over lines.

    It answers how it is written and over how many lines, so no caller
    ever composes a line itself and no second place decides whether a
    form fits on one.
    """

    opening: Word | NoWord
    parts: tuple[object, ...] = ()
    layout: WhenItHoldsABrokenPart = WHEN_IT_HOLDS_A_BROKEN_PART

    def breaks(self) -> bool:
        return self.layout.breaks(self.parts)

    def flat(self) -> str:
        """This form and everything inside it, written on one line."""
        return "(" + " ".join(self._words_of(self.opening.opens())) + ")"

    def _words_of(self, opening: str) -> list[str]:
        written = [opening, *(part.flat() for part in self.parts)]
        return [one for one in written if one]

    def written(self, indent: Indent) -> tuple[str, ...]:
        """The lines this form is written over, each already carrying
        the spaces that put it where it stands."""
        if not self.breaks():
            return (indent.before(self.flat()),)
        return self._over_several_lines(indent)

    def _over_several_lines(self, indent: Indent) -> tuple[str, ...]:
        under = self.parts
        shared = ""
        if under and self.layout.opens_with_the_first_part() and not under[0].breaks():
            shared = under[0].flat()
            under = under[1:]
        opening = " ".join(one for one in (self.opening.opens(), shared) if one)
        lines = [indent.before(f"({opening}")]
        for part in under:
            lines.extend(part.written(indent.deeper()))
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


def _declaration(declared: object) -> Form:
    if isinstance(declared, syntax.RecordType):
        return Form(
            Word("deftype"),
            (
                Word(declared.name),
                Form(Word("record"), _fields(declared.fields)),
            ),
        )
    if isinstance(declared, syntax.UnionType):
        return Form(
            Word("deftype"),
            (
                Word(declared.name),
                Form(
                    Word("union"),
                    tuple(_variant(one) for one in declared.variants),
                ),
            ),
        )
    return _function(declared)


def _fields(fields: tuple[tuple[str, str], ...]) -> tuple[Form, ...]:
    return tuple(
        Form(Word(name), (Word(type_name),)) for name, type_name in fields
    )


def _variant(variant: syntax.Variant) -> Form:
    return Form(Word(variant.name), _fields(variant.fields))


def _function(declared: syntax.Function) -> Form:
    return Form(
        Word("defn"),
        (
            Word(declared.name),
            _signature(declared.signature),
            *_conditions("requires", declared.requires),
            *_conditions("ensures", declared.ensures),
            Form(
                Word("examples"),
                tuple(_example(one) for one in declared.examples),
                ONE_PART_PER_LINE,
            ),
            _expression(declared.body),
        ),
        ALWAYS,
    )


def _conditions(word: str, conditions: tuple[object, ...]) -> tuple[Form, ...]:
    """The requires or the ensures clause of a function, or nothing at
    all where it declares none.

    Every condition of a clause stands in that one clause, in the order
    the source writes them, which is the only shape core-0 has for them.

    A clause holding no condition is the empty conjunction, which is
    true, and SPEC.md line 204 says an omitted block means true: the two
    spell one thing. The typed tree cannot tell them apart in any case,
    so the canonical text writes the shorter of the two.
    """
    if not conditions:
        return ()
    return (Form(Word(word), tuple(_expression(one) for one in conditions)),)


def _signature(signature: syntax.Signature) -> Form:
    return Form(
        Word("sig"),
        (
            Form(
                NO_WORD,
                tuple(
                    Form(Word(one.name), (Word(one.type_name),))
                    for one in signature.params
                ),
            ),
            Word("->"),
            Word(signature.return_type),
            Word("!"),
            Word("pure"),
        ),
    )


def _example(example: syntax.Example) -> Form:
    return Form(
        Word("example"),
        (
            Form(
                Word(example.function),
                tuple(Word(render(one)) for one in example.args),
            ),
            Word("=>"),
            Word(render(example.expected)),
        ),
    )


def expression_text(expr: object) -> str:
    """One expression written as core-0 writes it, on one line.

    The one place an expression becomes text, asked by the canonical
    text of a program and by the artefact a build generates, whose
    refusal quotes the contract that did not hold the way the source
    writes it.
    """
    return _expression(expr).flat()


def _expression(expr: object) -> object:
    return _EXPRESSIONS[type(expr)](expr)


def _binding(binding: syntax.Binding) -> Form:
    return Form(Word(binding.name), (_expression(binding.value),))


def _clause(clause: syntax.MatchClause) -> Form:
    return Form(_pattern(clause.pattern), (_expression(clause.body),))


def _pattern(pattern: object) -> Word:
    """One pattern of a match clause, written out.

    A Word, because core-0 builds a pattern out of literals, names and
    constructors and never out of a `let`, an `if` or a `match`: it
    stands on one line whatever it holds, which is what lets a match
    clause open with it.
    """
    return Word(_PATTERNS[type(pattern)](pattern))


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
    syntax.IntLit: lambda e: Word(render(e.value)),
    syntax.BoolLit: lambda e: Word(render(e.value)),
    syntax.UnitLit: lambda e: Word(render(UNIT)),
    syntax.NameRef: lambda e: Word(e.name),
    syntax.Call: lambda e: Form(
        Word(e.name), tuple(_expression(a) for a in e.args)
    ),
    syntax.ConstructorCall: lambda e: Form(
        Word(e.name), tuple(_expression(a) for a in e.args)
    ),
    syntax.OperatorCall: lambda e: Form(
        Word(e.operator), tuple(_expression(a) for a in e.args)
    ),
    syntax.FieldAccess: lambda e: Form(
        Word(f".{e.field_name}"), (_expression(e.target),)
    ),
    syntax.Let: lambda e: Form(
        Word("let"),
        (
            Form(NO_WORD, tuple(_binding(b) for b in e.bindings)),
            _expression(e.body),
        ),
        ALWAYS,
    ),
    syntax.If: lambda e: Form(
        Word("if"),
        (
            _expression(e.condition),
            _expression(e.then_branch),
            _expression(e.else_branch),
        ),
        ALWAYS,
    ),
    syntax.Match: lambda e: Form(
        Word("match"),
        (
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
        Word(p.name), tuple(_pattern(s) for s in p.subpatterns)
    ).flat(),
}
