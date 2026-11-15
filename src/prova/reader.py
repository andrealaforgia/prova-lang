"""UTF-8 s-expression reader for core-0 source text.

Produces a generic parenthesised tree (Atom / SList) carrying line/column
spans, with comments and whitespace already stripped. `syntax.py` turns
this generic tree into the typed core-0 program.
"""

from __future__ import annotations

from dataclasses import dataclass
import re

INT_RE = re.compile(r"[+-]?[0-9]+$")


class ReaderError(Exception):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column


class TooDeeplyNested(Exception):
    """A text nests one form inside another more deeply than this tool
    reads.

    Deliberately not a `ReaderError`: a text that nests too deep breaks
    no rule of how core-0 is written, and answering it as a syntax
    refusal would tell a reader to repair a program that may be
    perfectly well formed. It carries the limit, the depth the text
    reached and the place the form that went too deep stands at.
    """

    def __init__(self, message: str, line: int, column: int, limit: int, reached: int):
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.limit = limit
        self.reached = reached


@dataclass(frozen=True)
class NestingLimit:
    """The greatest nesting this tool reads, and the name a caller reads
    that number under.

    One object holds the number. The reader asks it whether a depth has
    passed it, and the manifest publishes the same object's number, so
    what a caller is promised and what the tool does cannot drift apart.
    """

    maximum: int
    name: str = "expression_nesting"

    def passed_by(self, depth: int) -> bool:
        return depth > self.maximum

    def reason(self) -> str:
        """Why the number is the number it is, for a caller that must
        change its generator and is owed the reason."""
        return (
            f"reading one form inside another costs 2 interpreter frames per "
            f"form, so {self.maximum} forms cost about {2 * self.maximum + 13} "
            "of the 1000 frames Python allows by default: the refusal is "
            "therefore reached with room to spare however deep the caller's "
            "own stack already is. It is also far above any program written "
            "to be read, the deepest shipped here standing 10 forms deep."
        )

    def refusal_at(self, depth: int, line: int, column: int) -> TooDeeplyNested:
        return TooDeeplyNested(
            f"the text nests {depth} forms deep and this tool reads "
            f"{self.maximum}: it reads one form inside another by calling "
            "itself once per form, and declares a maximum so that it refuses "
            "here instead of exhausting the interpreter stack and answering "
            "nothing at all; write the inner forms as separate 'let' bindings "
            f"so that no form stands more than {self.maximum} forms inside the "
            f"text, and read {self.maximum} from the {self.name!r} entry of "
            "the resource limits the 'discover' operation publishes",
            line,
            column,
            self.maximum,
            depth,
        )


# How deep a text may nest, for every text this tool reads: the source
# of a program and the value of an argument alike.
READING_LIMIT = NestingLimit(128)


@dataclass(frozen=True)
class Atom:
    text: str
    line: int
    column: int

    @property
    def is_int(self) -> bool:
        return bool(INT_RE.match(self.text))

    @property
    def int_value(self) -> int:
        return int(self.text)


@dataclass(frozen=True)
class SList:
    items: tuple[object, ...]
    line: int
    column: int


@dataclass(frozen=True)
class Comment:
    """One comment as a reader wrote it: the characters from its ';' to
    the end of its line, and the place that ';' stands at.

    Kept rather than dropped, and kept exactly: a tool that writes the
    source back out must write the reader's own words, not a tidied
    version of them, and a client that reads the program's tree is owed
    the prose written about each part of it.
    """

    text: str
    line: int
    column: int


@dataclass(frozen=True)
class SourceText:
    """One text as this reader reads it: the forms it writes, and the
    comments met between them."""

    forms: tuple[object, ...]
    comments: tuple[Comment, ...]


@dataclass(frozen=True)
class _Token:
    kind: str  # "(" | ")" | "atom"
    text: str
    line: int
    column: int


def _tokenize(text: str) -> tuple[list[_Token], list[Comment]]:
    tokens: list[_Token] = []
    comments: list[Comment] = []
    line = 1
    column = 1
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "\n":
            i += 1
            line += 1
            column = 1
            continue
        if ch.isspace():
            i += 1
            column += 1
            continue
        if ch == ";":
            start_line, start_column = line, column
            start = i
            while i < n and text[i] != "\n":
                i += 1
                column += 1
            # A text written on a system that ends its lines with
            # two characters leaves the first of them inside the
            # comment; it ends the line and is not one of the reader's
            # own characters, so it is not kept.
            written = text[start:i]
            if written.endswith("\r"):
                written = written[:-1]
            comments.append(Comment(written, start_line, start_column))
            continue
        if ch in "()":
            tokens.append(_Token(ch, ch, line, column))
            i += 1
            column += 1
            continue
        start_line, start_column = line, column
        j = i
        while j < n and not text[j].isspace() and text[j] not in "();":
            j += 1
            column += 1
        tokens.append(_Token("atom", text[i:j], start_line, start_column))
        i = j
    return tokens, comments


def end_of(text: str) -> tuple[int, int]:
    """The place just past the last character of `text`.

    Where a refusal of the reader stands when the text ran out: the
    reader stopped there and nowhere else, and a refusal that said
    nothing about where would leave a reader of it with no line to open.
    """
    lines = text.split("\n")
    return len(lines), len(lines[-1]) + 1


def read_source(text: str) -> SourceText:
    """Every top-level form `text` writes, and every comment met between
    them.

    The one reader of characters: a caller that wants the forms alone
    asks `read_program` below, and nothing else in this tool reads a
    character of a source.
    """
    tokens, comments = _tokenize(text)
    forms: list[object] = []
    pos = 0
    while pos < len(tokens):
        node, pos = _read_form(tokens, pos, text)
        forms.append(node)
    return SourceText(tuple(forms), tuple(comments))


def read_program(text: str) -> list[object]:
    """Read every top-level form in `text` into a list of Atom/SList nodes."""
    return list(read_source(text).forms)


def _read_form(
    tokens: list[_Token], pos: int, text: str = "", enclosing: int = 0
) -> tuple[object, int]:
    """One form, read at `enclosing` forms already open around it.

    The one place the depth of a text grows, so the one place the limit
    is counted. Every text this tool reads passes through here, which is
    why no later stage has to defend itself against a tree it cannot
    walk.
    """
    if pos >= len(tokens):
        line, column = end_of(text)
        raise ReaderError("unexpected end of input", line, column)
    token = tokens[pos]
    if token.kind == ")":
        raise ReaderError("unexpected ')'", token.line, token.column)
    if token.kind == "atom":
        return Atom(token.text, token.line, token.column), pos + 1
    depth = enclosing + 1
    if READING_LIMIT.passed_by(depth):
        raise READING_LIMIT.refusal_at(depth, token.line, token.column)
    items: list[object] = []
    open_token = token
    pos += 1
    while True:
        if pos >= len(tokens):
            raise ReaderError(
                "unclosed '('", open_token.line, open_token.column
            )
        if tokens[pos].kind == ")":
            pos += 1
            break
        node, pos = _read_form(tokens, pos, text, depth)
        items.append(node)
    return SList(tuple(items), open_token.line, open_token.column), pos
