"""Acceptance test for I1.S1.B3: `build` and `verify` are refused with an
explicit structured `unavailable` failure, never attempted.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

OPERATIONS = ["build", "verify"]


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def test_b3_build_and_verify_are_refused_as_explicit_unavailable_failures():
    """Given the Owner requests the build operation or the verify
    operation against the reservation source, when either request runs,
    then the tool returns an explicit structured failure reporting the
    operation as unavailable rather than attempting it."""
    source = _reservation_source()

    for operation in OPERATIONS:
        request = {"prova": "i1", "operation": operation, "source": source}
        proc = subprocess.run(
            ["prova"],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=10.0,
        )
        assert proc.returncode == 0, f"tool failure requesting {operation}: stderr={proc.stderr!r}"
        try:
            response = json.loads(proc.stdout)
        except (json.JSONDecodeError, ValueError):
            raise AssertionError(f"non-JSON response requesting {operation}: {proc.stdout!r}")

        assert response.get("operation") == operation, response
        assert response.get("status") == "unavailable", (
            f"{operation} was not refused as unavailable: {response}"
        )
        assert not response.get("result"), f"{operation} refusal carried a result: {response}"

        diagnostics = response.get("diagnostics") or []
        categories = {d.get("category") for d in diagnostics}
        assert categories, f"{operation} refusal carried no diagnostic naming why: {response}"
        assert "tool_failure" not in categories, (
            f"{operation} refusal reported a tool_failure diagnostic, suggesting a "
            f"crashed attempt rather than a clean refusal: {response}"
        )
