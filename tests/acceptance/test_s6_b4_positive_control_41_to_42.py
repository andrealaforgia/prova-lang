"""Acceptance test for I1.S6.B4: given the same program, when the Owner
supplies 41 as runtime input as the positive control, then the reported
result is exactly 42.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ADD_ONE_PATH = REPO_ROOT / "conformance" / "add-one.prova"


def _evaluate_add_one(n: int) -> dict:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": ADD_ONE_PATH.read_text(encoding="utf-8"),
        "function": "add-one",
        "arguments": [str(n)],
    }
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure evaluating add-one({n}): stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response evaluating add-one({n}): {proc.stdout!r}")


def test_add_one_of_41_is_42_as_a_positive_control():
    """Given the same program, when the Owner supplies 41 as runtime
    input as the positive control, then the reported result is exactly
    42."""
    response = _evaluate_add_one(41)

    assert response.get("status") == "completed", f"expected a successful evaluation: {response}"
    result = response.get("result") or {}
    assert result.get("value") == "42", f"expected 42, got {response}"
