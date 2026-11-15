"""Shared helpers for F12's acceptance tests: the published fixtures, the
two requests the tests send, and the walk over a published tree.

Not itself a test module; imported by the F12 acceptance tests.
"""

from __future__ import annotations

import json
import pathlib

from prova import service

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
PUBLISHED_FIXTURES = REPO_ROOT / "conformance" / "parse"


def fixture_source(name: str) -> str:
    return (PUBLISHED_FIXTURES / f"{name}.prova").read_text(encoding="utf-8")


def fixture_tree(name: str) -> dict:
    return json.loads((PUBLISHED_FIXTURES / f"{name}.tree.json").read_text(encoding="utf-8"))


def published_pairs() -> list[str]:
    """The name of every source published beside the tree it must answer."""
    return sorted(path.stem for path in PUBLISHED_FIXTURES.glob("*.prova"))


def ask_for_the_tree(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "parse", "source": source})


def ask_for_the_check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def ask_for_the_manifest() -> dict:
    return service.handle({"prova": "i1", "operation": "discover"})


def nodes_of(tree: object) -> list[dict]:
    """Every node of a published tree, outermost first.

    A node is anything the answer gives a kind to, wherever it stands:
    under a named part, inside a list of parts, or among the comments a
    node carries.
    """
    found: list[dict] = []
    if isinstance(tree, dict):
        if "kind" in tree:
            found.append(tree)
        for value in tree.values():
            found.extend(nodes_of(value))
    elif isinstance(tree, list):
        for item in tree:
            found.extend(nodes_of(item))
    return found


def place_of(node: dict) -> tuple[int, int]:
    return node["position"]["line"], node["position"]["column"]


def text_at(source: str, place: tuple[int, int]) -> str:
    """What the source holds from `place` to the end of that line."""
    line, column = place
    lines = source.split("\n")
    assert 1 <= line <= len(lines), f"line {line} is outside a source of {len(lines)} line(s)"
    return lines[line - 1][column - 1 :]


def categories_of(response: dict) -> list[str]:
    return sorted(diagnostic["category"] for diagnostic in response["diagnostics"])
