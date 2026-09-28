"""Acceptance test for I1.S5.B3: the diagnostic reported for I1.S5.B2's
rejection names both the category of the error and its location within
the source.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
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


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _reserve_bug_source() -> str:
    source = _reservation_source()
    assert source.count(RESERVE_OLD) == 1
    return source.replace(RESERVE_OLD, RESERVE_BUG, 1)


def _run_check(source: str) -> dict:
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


def test_b3_rejection_diagnostic_names_category_and_location():
    """Given that rejection, when the Owner reads the reported diagnostic,
    then it names both the category of the error and its location within
    the source."""
    response = _run_check(_reserve_bug_source())
    assert response.get("status") == "invalid_program", response

    diagnostics = response.get("diagnostics") or []
    assert diagnostics, f"rejection carried no diagnostics: {response}"
    diagnostic = diagnostics[0]

    category = diagnostic.get("category")
    assert category, f"diagnostic did not name a category: {diagnostic}"

    location = diagnostic.get("location") or {}
    line = location.get("line")
    column = location.get("column")
    assert isinstance(line, int) and isinstance(column, int), (
        f"diagnostic did not name a line/column location within the source: {diagnostic}"
    )
