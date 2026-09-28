"""Shared fixtures for Story I1.S5's acceptance tests: the reservation
source, its hand-built invalid variants, the source-offset-to-line/column
helper used to check reported diagnostic locations for real, and the
`prova` command runner.

Not itself a test module; imported by test_s5_b2/b3/b4/int.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

RESERVE_OLD = "(Outcome (Reservation (+ (.reserved current) 1)) true)"
RESERVE_BUG = (
    "(Outcome (Reservation (if (= (.reserved current) 1) "
    "(+ true 1) (+ (.reserved current) 1))) true)"
)
RESERVE_BUG_SITE = "(+ true 1)"

INIT_OLD = "  (examples (example (initial) => (Reservation 0)))\n  (Reservation 0))\n"
INIT_BUG = "  (examples (example (initial) => (Reservation 0)))\n  (Reservation missing-count))\n"
INIT_BUG_SITE = "missing-count"


def reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def reserve_bug_source() -> str:
    source = reservation_source()
    assert source.count(RESERVE_OLD) == 1
    return source.replace(RESERVE_OLD, RESERVE_BUG, 1)


def unbound_name_source() -> str:
    source = reservation_source()
    assert source.count(INIT_OLD) == 1
    return source.replace(INIT_OLD, INIT_BUG, 1)


def line_column_of(source: str, needle: str) -> tuple[int, int]:
    """The 1-indexed (line, column) of `needle`'s first character in
    `source`, using the same convention as the reader: line 1 column 1 at
    the start, column resets to 1 after each newline."""
    index = source.index(needle)
    last_newline = source.rfind("\n", 0, index)
    line = source.count("\n", 0, index) + 1
    column = index + 1 if last_newline == -1 else index - last_newline
    return line, column


def run_check(source: str) -> dict:
    request = {"prova": "i1", "operation": "check", "source": source}
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response: {proc.stdout!r}")
