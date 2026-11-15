"""Programs of core-0 as a reader might write them, generated.

Every program this module writes is a program the tool accepts, built
from a closed set of declaration shapes rather than from characters: the
laws of F15 are about what writing an accepted program out does, so a
generator that mostly produced refused text would prove nothing.

What varies is everything a reader chooses and the language does not:
which declarations stand in the program, the whole numbers in them, how
each number is spelled, whether a declaration is written on one line or
spread over several, and where the comments stand.

Not itself a test module; imported by the F15 property tests.
"""

from __future__ import annotations

from dataclasses import dataclass

from hypothesis import strategies as st

from prova import service

# How a reader may spell a whole number core-0 accepts (SPEC.md lines
# 76-78): the number itself, with a leading plus, with leading zeros, or
# with both.
SPELLINGS = ("plain", "plus", "padded", "plus-padded")

# How a reader may lay a declaration out: all on one line, or with each
# of its clauses on a line of its own under an indent of its choosing.
LAYOUTS = ("on-one-line", "spread")

# The declaration shapes the generator writes. Each is one shape of
# core-0 body: an operator call, a conditional, a binding, a match over
# whole numbers, a field selection and a match over a union.
KINDS = ("plus", "branch", "bound", "chosen", "held", "flagged")

# The two type declarations the shapes above need, written once when a
# shape that uses one is drawn.
BOX = "(deftype Box (record (held Int)))"
FLAG = "(deftype Flag (union (On) (Off)))"


def spelled(value: int, spelling: str) -> str:
    """One whole number, written the way a reader chose to write it."""
    sign = "-" if value < 0 else ""
    digits = str(abs(value))
    if spelling == "plain":
        return str(value)
    if spelling == "plus":
        return f"+{digits}" if value >= 0 else f"-{digits}"
    if spelling == "padded":
        return f"{sign}00{digits}"
    return f"+00{digits}" if value >= 0 else f"-00{digits}"


@dataclass(frozen=True)
class WrittenProgram:
    """One program as a reader wrote it: the characters, and the comments
    standing in them in the order they were written."""

    text: str
    comments: tuple[str, ...]


def _laid_out(name: str, clauses: list[str], layout: str, indent: int) -> str:
    """One `defn` form, written on one line or with a clause per line."""
    if layout == "on-one-line":
        return f"(defn {name} " + " ".join(clauses) + ")"
    pad = "\n" + " " * indent
    return f"(defn {name}" + pad + pad.join(clauses) + ")"


def _declaration(
    name: str, kind: str, first: int, second: int, spelling: str
) -> tuple[list[str], str, str]:
    """The clauses of one function of the drawn shape, the type
    declaration it needs (empty when it needs none), and the body."""
    k = spelled(second, spelling)
    a = spelled(first, spelling)
    if kind == "plus":
        answered = first + second
        return (
            [
                "(sig ((n Int)) -> Int ! pure)",
                f"(ensures (= result (+ n {k})))",
                f"(examples (example ({name} {a}) => {answered}))",
                f"(+ n {k})",
            ],
            "",
            "",
        )
    if kind == "branch":
        answered = second if first < second else first
        return (
            [
                "(sig ((n Int)) -> Int ! pure)",
                f"(examples (example ({name} {a}) => {answered}))",
                f"(if (< n {k}) {k} n)",
            ],
            "",
            "",
        )
    if kind == "bound":
        answered = first * second + second
        return (
            [
                "(sig ((n Int)) -> Int ! pure)",
                f"(examples (example ({name} {a}) => {answered}))",
                f"(let ((v (* n {k}))) (+ v {k}))",
            ],
            "",
            "",
        )
    if kind == "chosen":
        answered = 1 if first == second else 0
        return (
            [
                "(sig ((n Int)) -> Int ! pure)",
                f"(examples (example ({name} {a}) => {answered}))",
                f"(match n ({k} 1) (_ 0))",
            ],
            "",
            "",
        )
    if kind == "held":
        return (
            [
                "(sig ((b Box)) -> Int ! pure)",
                f"(examples (example ({name} (Box {a})) => {first}))",
                "(.held b)",
            ],
            BOX,
            "",
        )
    return (
        [
            "(sig ((f Flag)) -> Int ! pure)",
            f"(examples (example ({name} (On)) => {second}))",
            f"(match f ((On) {k}) ((Off) 0))",
        ],
        FLAG,
        "",
    )


@st.composite
def written_programs(draw) -> WrittenProgram:
    """One accepted program, written as a reader might have written it."""
    kinds = draw(st.lists(st.sampled_from(KINDS), min_size=1, max_size=3))
    numbers = draw(
        st.lists(
            # The second number is written into the body of the
            # function, where it decides what the function answers, so
            # it reaches below zero: a program whose expressions held
            # only numbers above zero could not tell a tool that writes
            # a number's size and drops its sign from one that does not.
            st.tuples(st.integers(-40, 40), st.integers(-9, 9)),
            min_size=len(kinds),
            max_size=len(kinds),
        )
    )
    spellings = draw(
        st.lists(
            st.sampled_from(SPELLINGS), min_size=len(kinds), max_size=len(kinds)
        )
    )
    layouts = draw(
        st.lists(st.sampled_from(LAYOUTS), min_size=len(kinds), max_size=len(kinds))
    )
    indents = draw(
        st.lists(st.integers(1, 4), min_size=len(kinds), max_size=len(kinds))
    )
    # Where the comments stand: above each declaration, inside each
    # declaration that is spread over several lines, and after the last.
    above = draw(
        st.lists(st.booleans(), min_size=len(kinds), max_size=len(kinds))
    )
    inside = draw(
        st.lists(st.booleans(), min_size=len(kinds), max_size=len(kinds))
    )
    at_the_end = draw(st.booleans())

    lines: list[str] = []
    comments: list[str] = []
    types_written: list[str] = []
    bodies: list[tuple[str, list[str], str, int, bool]] = []

    for place, kind in enumerate(kinds):
        name = f"fn{place}"
        first, second = numbers[place]
        clauses, needs, _ = _declaration(name, kind, first, second, spellings[place])
        if needs and needs not in types_written:
            types_written.append(needs)
        bodies.append((name, clauses, layouts[place], indents[place], inside[place]))

    def next_comment() -> str:
        written = f"; note {len(comments)}"
        comments.append(written)
        return written

    lines.extend(types_written)

    for place, (name, clauses, layout, indent, has_inner) in enumerate(bodies):
        if above[place]:
            lines.append(next_comment())
        if layout == "spread" and has_inner:
            # A comment written inside a declaration, which no part of
            # that declaration follows: SPEC.md line 63 hands it to the
            # next node, which is the next declaration or the document end.
            body = clauses[-1]
            clauses = clauses[:-1] + [next_comment() + "\n" + " " * indent + body]
        lines.append(_laid_out(name, clauses, layout, indent))

    if at_the_end:
        lines.append(next_comment())

    return WrittenProgram("\n".join(lines) + "\n", tuple(comments))


def ask(operation: str, source: str) -> dict:
    return service.handle(
        {"prova": "i1", "operation": operation, "source": source}
    )


def canonical_text(answer: dict) -> object:
    return (answer.get("result") or {}).get("text")


def comments_of(tree: object) -> list[str]:
    """Every comment of an answered tree, in the order a reader meets
    them."""
    found: list[str] = []
    _collect(tree, found)
    return found


def _collect(part: object, found: list[str]) -> None:
    if isinstance(part, dict):
        if part.get("kind") == "comment":
            found.append(part["text"])
            return
        for key in ("comments", *[k for k in part if k != "comments"]):
            if key in part:
                _collect(part[key], found)
        return
    if isinstance(part, list):
        for item in part:
            _collect(item, found)


def meaning_of(tree: object) -> object:
    """What an answered tree says about the program, with the two things
    a change of layout may change taken out: where each node stands, and
    which node each comment was handed to."""
    if isinstance(tree, dict):
        return {
            key: meaning_of(value)
            for key, value in tree.items()
            if key not in ("position", "comments", "trailing_comments")
        }
    if isinstance(tree, list):
        return [meaning_of(item) for item in tree]
    return tree
