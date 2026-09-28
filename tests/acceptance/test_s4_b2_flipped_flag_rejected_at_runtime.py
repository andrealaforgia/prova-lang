"""Acceptance test for I1.S4.B2: a copy of the reservation source whose
`step` body has its accepted flag flipped in both branches is evaluated
directly on a valid input, and the tool reports a runtime postcondition
violation for that call, not a successful result.

Only `step`'s body is changed from the protected source at SPEC_ORACLE_SHA;
every returned `accepted` literal is negated in both branches, while the
state calculation (which branch computes which count) is untouched -- so
the counts still satisfy the state invariant and only the `ensures` clause
tying `accepted` to the event/count relation is violated.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC_ORACLE_SHA = "ee5e1556b3a5e06945a02a61ef3a4cad51744b12"

STEP_BODY_OLD = (
    "  (match event\n"
    "    ((Reserve)\n"
    "      (if (< (.reserved current) 2)\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) true)\n"
    "          (Outcome current false)))\n"
    "    ((Release)\n"
    "      (if (> (.reserved current) 0)\n"
    "          (Outcome (Reservation (- (.reserved current) 1)) true)\n"
    "          (Outcome current false)))))\n"
)

FLIPPED_FLAG_BODY_NEW = (
    "  (match event\n"
    "    ((Reserve)\n"
    "      (if (< (.reserved current) 2)\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) false)\n"
    "          (Outcome current true)))\n"
    "    ((Release)\n"
    "      (if (> (.reserved current) 0)\n"
    "          (Outcome (Reservation (- (.reserved current) 1)) false)\n"
    "          (Outcome current true)))))\n"
)


def _spec_text_at(sha: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{sha}:SPEC.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _reservation_source_at(sha: str) -> str:
    text = _spec_text_at(sha)
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _flipped_flag_source() -> str:
    source = _reservation_source_at(SPEC_ORACLE_SHA)
    occurrences = source.count(STEP_BODY_OLD)
    assert occurrences == 1, f"expected exactly one occurrence of step's body, found {occurrences}"
    return source.replace(STEP_BODY_OLD, FLIPPED_FLAG_BODY_NEW, 1)


def _evaluate_step(source: str, current_text: str, event: str) -> dict:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
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
    assert proc.returncode == 0, f"tool failure evaluating step: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response evaluating step: {proc.stdout!r}")


def test_b2_flipped_flag_rejected_on_a_valid_input():
    """Given a separate copy of the reservation source in which only
    step's body is changed to flip the accepted flag, when the Owner runs
    the direct evaluation operation on that copy with any valid input,
    then the tool reports a runtime postcondition violation for that
    supplied input, not a successful result."""
    source = _flipped_flag_source()
    assert source != _reservation_source_at(SPEC_ORACLE_SHA), "the mutation did not change the source"

    response = _evaluate_step(source, "(Reservation 0)", "Reserve")

    result = response.get("result") or {}
    assert not result.get("value"), (
        f"flipped-flag step((Reservation 0), Reserve) returned a successful "
        f"result despite negating the accepted flag: {response}"
    )
    categories = {d.get("category") for d in (response.get("diagnostics") or [])}
    assert "postcondition_violation" in categories, (
        f"expected a postcondition_violation diagnostic for the flipped-flag call: {response}"
    )
