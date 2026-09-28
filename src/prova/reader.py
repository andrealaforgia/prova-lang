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
class _Token:
    kind: str  # "(" | ")" | "atom"
    text: str
    line: int
    column: int


def _tokenize(text: str) -> list[_Token]:
    tokens: list[_Token] = []
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
            while i < n and text[i] != "\n":
                i += 1
                column += 1
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
    return tokens


def read_program(text: str) -> list[object]:
    """Read every top-level form in `text` into a list of Atom/SList nodes."""
    tokens = _tokenize(text)
    forms: list[object] = []
    pos = 0
    while pos < len(tokens):
        node, pos = _read_form(tokens, pos)
        forms.append(node)
    return forms


def _read_form(tokens: list[_Token], pos: int) -> tuple[object, int]:
    if pos >= len(tokens):
        raise ReaderError("unexpected end of input", 0, 0)
    token = tokens[pos]
    if token.kind == ")":
        raise ReaderError("unexpected ')'", token.line, token.column)
    if token.kind == "atom":
        return Atom(token.text, token.line, token.column), pos + 1
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
        node, pos = _read_form(tokens, pos)
        items.append(node)
    return SList(tuple(items), open_token.line, open_token.column), pos
