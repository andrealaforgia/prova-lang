"""Acceptance test for I1.S3.B2: the entry state (Reservation -1) -- one
below the lower valid boundary zero -- is rejected before `step`'s body
runs, for either event.

(Reserve)'s body would move the count from -1 back to 0, inside the valid
range; the precondition must still reject before that body ever runs, so a
would-be in-range result never appears as a successful outcome here.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _evaluate_step(current_text: str, event: str) -> dict:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": _reservation_source(),
        "function": "step",
        "arguments": [current_text, f"({event})"],
    }
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure evaluating step({current_text}, {event}): stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response evaluating step({current_text}, {event}): {proc.stdout!r}")


@pytest.mark.parametrize("event", ["Reserve", "Release"])
def test_b2_reservation_minus_one_rejects_citing_precondition(event):
    """Given the entry state (Reservation -1), when the Owner runs the same
    operation, then the tool rejects the call with no successful result,
    citing the precondition."""
    response = _evaluate_step("(Reservation -1)", event)

    result = response.get("result") or {}
    assert not result.get("value"), (
        f"step((Reservation -1), {event}) returned a successful result despite the "
        f"entry state being below the valid range: {response}"
    )
    categories = {d.get("category") for d in (response.get("diagnostics") or [])}
    assert "precondition_violation" in categories, (
        f"expected a precondition_violation diagnostic for step((Reservation -1), {event}): {response}"
    )
