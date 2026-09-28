"""Acceptance test for I1.S5.B1: the unmodified reservation source is
accepted by whole-program static checking, with no errors.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


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


def test_b1_unmodified_reservation_source_is_accepted_with_no_errors():
    """Given the unmodified reservation source, when the Owner runs the
    check operation against it, then the tool reports the whole program as
    accepted with no errors."""
    response = _run_check(_reservation_source())

    assert response.get("operation") == "check", response
    assert response.get("status") == "completed", (
        f"expected the whole program to be accepted, got: {response}"
    )
    assert not response.get("diagnostics"), (
        f"acceptance carried diagnostics: {response}"
    )
