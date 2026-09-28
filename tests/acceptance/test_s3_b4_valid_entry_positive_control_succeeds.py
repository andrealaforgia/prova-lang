"""Acceptance test for I1.S3.B4: (Reservation 0), a valid entry state, with
a valid event succeeds -- the positive control confirming that the
rejections in I1.S3.B1-B3 are specific to their invalid inputs, not a
blanket refusal of `step`.

The same run also re-checks (Reservation 3) -- the entry state I1.S3.B1
rejects -- against the identical source and event in the same test, so the
contrast between "this one succeeds" and "that one is rejected" is drawn
within a single acceptance run rather than left to be inferred from
separate files.

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


def test_b4_valid_entry_succeeds_while_matching_invalid_entry_still_rejects():
    """Given a valid entry state such as (Reservation 0) as the positive
    control, when the Owner runs the same operation with a valid event,
    then the tool returns a successful result, confirming the rejections
    above are specific to the invalid inputs."""
    valid_response = _evaluate_step("(Reservation 0)", "Reserve")
    assert valid_response.get("status") == "completed", (
        f"expected the positive control to succeed: {valid_response}"
    )
    result = valid_response.get("result") or {}
    assert result.get("value") == "(Outcome (Reservation 1) true)", (
        f"unexpected successful result for the positive control: {valid_response}"
    )

    invalid_response = _evaluate_step("(Reservation 3)", "Reserve")
    invalid_result = invalid_response.get("result") or {}
    assert not invalid_result.get("value"), (
        f"the over-capacity entry state must still be rejected, not succeed like "
        f"the positive control: {invalid_response}"
    )
