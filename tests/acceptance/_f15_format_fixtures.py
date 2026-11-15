"""Shared helpers for F15's acceptance tests: the requests the tests send,
the pairs published under conformance/format, and the two readings of an
answered tree the tests compare.

Not itself a test module; imported by the F15 acceptance tests.
"""

from __future__ import annotations

import pathlib

from _reservation_fixtures import reservation_source
from prova import service

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PUBLISHED_PAIRS = REPO_ROOT / "conformance" / "format"

# The suffix the canonical half of a published pair is written under. A
# pair is two files: the source a reader may write, and the one text the
# tool answers for it.
CANONICAL_SUFFIX = ".canonical.prova"


def ask_to_format(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "format", "source": source})


def ask_to_check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def ask_for_the_examples(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "examples", "source": source})


def ask_for_the_tree(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "parse", "source": source})


def ask_for_the_manifest() -> dict:
    return service.handle({"prova": "i1", "operation": "discover"})


def canonical_text(answer: dict) -> object:
    """The text an answer carries, or None when it carries none.

    Read through `.get` on purpose: a refusal must carry no text at all,
    and a test that reached for it directly would fail by breaking rather
    than by saying what was wrong.
    """
    return (answer.get("result") or {}).get("text")


def published_names() -> list[str]:
    """The name of every pair published under conformance/format."""
    return sorted(
        path.name[: -len(".prova")]
        for path in PUBLISHED_PAIRS.glob("*.prova")
        if not path.name.endswith(CANONICAL_SUFFIX)
    )


def pair_source(name: str) -> str:
    return (PUBLISHED_PAIRS / f"{name}.prova").read_text(encoding="utf-8")


def pair_canonical(name: str) -> str:
    return (PUBLISHED_PAIRS / f"{name}{CANONICAL_SUFFIX}").read_text(encoding="utf-8")


def comments_of(tree: object) -> list[str]:
    """Every comment of an answered tree, in the order a reader meets
    them: the ones standing on a node, outermost first, and then the ones
    no node follows.
    """
    found: list[str] = []
    _collect_comments(tree, found)
    return found


def _collect_comments(part: object, found: list[str]) -> None:
    if isinstance(part, dict):
        if part.get("kind") == "comment":
            found.append(part["text"])
            return
        for key in ("comments", *[k for k in part if k != "comments"]):
            if key in part:
                _collect_comments(part[key], found)
        return
    if isinstance(part, list):
        for item in part:
            _collect_comments(item, found)


def meaning_of(tree: object) -> object:
    """What an answered tree says about the program, with the two things
    a change of layout is allowed to change taken out: where each node
    stands, and which node each comment was handed to.

    Two trees that read alike here are two spellings of one program.
    """
    if isinstance(tree, dict):
        return {
            key: meaning_of(value)
            for key, value in tree.items()
            if key not in ("position", "comments", "trailing_comments")
        }
    if isinstance(tree, list):
        return [meaning_of(item) for item in tree]
    return tree


def example_results(answer: dict) -> list[dict]:
    """One entry per declared example, with the revision of the text
    taken out: the entry says which function was called, with what, what
    it answered and whether that agrees with the expectation."""
    return list((answer.get("result") or {}).get("examples") or [])


def the_reservation_program() -> str:
    """The reservation program SPEC.md publishes, written as SPEC.md
    writes it."""
    return reservation_source()
