"""Acceptance test for I1.S3.B3: a malformed or ill-typed value offered in
place of a valid Reservation is rejected distinctly from an entry
precondition violation.

Two cases, each its own parametrized run so one cannot hide the other:
- malformed: `(NoSuchReservation 1)` names no declared record type or union
  variant at all -- there is no value to check a precondition against.
- ill-typed: `(Outcome (Reservation 0) true)` is a well-formed value of a
  *different* declared type (Outcome, not Reservation) offered where
  Reservation is expected.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

CASES = [
    pytest.param("(NoSuchReservation 1)", "malformed_value", id="malformed-unknown-constructor"),
    pytest.param("(Outcome (Reservation 0) true)", "ill_typed_value", id="ill-typed-wrong-declared-type"),
]


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


@pytest.mark.parametrize("current_text,expected_category", CASES)
def test_b3_malformed_or_ill_typed_value_rejected_distinctly_from_precondition(current_text, expected_category):
    """Given a malformed or ill-typed value offered in place of a valid
    Reservation, when the Owner runs the same operation, then the tool
    rejects the call with no successful result, reported distinctly from a
    precondition rejection."""
    response = _evaluate_step(current_text, "Reserve")

    result = response.get("result") or {}
    assert not result.get("value"), (
        f"step({current_text}, Reserve) returned a successful result despite the "
        f"argument not being a valid Reservation: {response}"
    )
    categories = {d.get("category") for d in (response.get("diagnostics") or [])}
    assert expected_category in categories, (
        f"expected a {expected_category} diagnostic for step({current_text}, Reserve): {response}"
    )
    assert "precondition_violation" not in categories, (
        f"a malformed/ill-typed argument must not be reported as a precondition "
        f"violation for step({current_text}, Reserve): {response}"
    )
