"""Acceptance test for I1.S3.INT: Story I1.S3 works end to end through the
product's real surface -- reject invalid entry states and malformed inputs
before evaluation proceeds.

Exercises the whole story together, each case its own fresh `prova`
process: two invalid entry states (I1.S3.B1, I1.S3.B2), a malformed and an
ill-typed value offered where an entry state is expected (I1.S3.B3), and a
valid positive control (I1.S3.B4). This is the story-level check that these
behaviours compose correctly on the real surface, not a restatement of any
single behaviour's own acceptance test.

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


def _evaluate_step_fresh_process(current_text: str, event: str) -> dict:
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


def test_int_invalid_entries_and_malformed_inputs_rejected_before_evaluation_proceeds():
    """Given the reservation source, when the Owner directly evaluates
    `step` across invalid entry states, malformed/ill-typed values and a
    valid entry state, one independent process per case, then every
    invalid or malformed case is rejected with no successful result and a
    diagnostic naming what was wrong, while the valid case succeeds."""
    rejected_cases = [
        ("(Reservation 3)", "Reserve", "precondition_violation"),
        ("(Reservation -1)", "Release", "precondition_violation"),
        ("(NoSuchReservation 1)", "Reserve", "malformed_value"),
        ("(Outcome (Reservation 0) true)", "Release", "ill_typed_value"),
    ]

    for current_text, event, expected_category in rejected_cases:
        response = _evaluate_step_fresh_process(current_text, event)
        result = response.get("result") or {}
        assert not result.get("value"), (
            f"step({current_text}, {event}) must not evaluate to a successful "
            f"result: {response}"
        )
        categories = {d.get("category") for d in (response.get("diagnostics") or [])}
        assert expected_category in categories, (
            f"expected a {expected_category} diagnostic for step({current_text}, {event}): {response}"
        )

    valid_response = _evaluate_step_fresh_process("(Reservation 0)", "Reserve")
    assert valid_response.get("status") == "completed", (
        f"the valid entry state must still evaluate successfully: {valid_response}"
    )
    valid_result = valid_response.get("result") or {}
    assert valid_result.get("value") == "(Outcome (Reservation 1) true)", (
        f"unexpected successful result for the valid entry state: {valid_response}"
    )
