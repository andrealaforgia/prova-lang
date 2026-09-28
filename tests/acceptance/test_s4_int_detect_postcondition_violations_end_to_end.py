"""Acceptance test for I1.S4.INT: Story I1.S4 works end to end through the
product's real surface -- detect postcondition violations in deliberately
wrong step bodies.

Exercises the whole story together, each case its own fresh `prova`
process: the missing-guard boundary call (I1.S4.B1), all six flipped-flag
calls (I1.S4.B2), the four always-reject accepted-input calls (I1.S4.B3),
and the unmodified source as a positive control evaluated on the same six
inputs (I1.S4.B4). This is the story-level check that these behaviours
compose correctly on the real surface, not a restatement of any single
behaviour's own acceptance test.

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

MISSING_GUARD_BODY_NEW = (
    "  (match event\n"
    "    ((Reserve)\n"
    "      (if true\n"
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

ALWAYS_REJECT_BODY_NEW = "  (Outcome current false))\n"

COUNTS = [0, 1, 2]
EVENTS = ["Reserve", "Release"]
ALL_SIX_CASES = [(count, event) for count in COUNTS for event in EVENTS]
ACCEPTED_CASES = [(0, "Reserve"), (1, "Reserve"), (1, "Release"), (2, "Release")]

EXPECTED = {
    (0, "Reserve"): (1, True),
    (1, "Reserve"): (2, True),
    (2, "Reserve"): (2, False),
    (0, "Release"): (0, False),
    (1, "Release"): (0, True),
    (2, "Release"): (1, True),
}


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


def _mutated_source(new_body: str) -> str:
    source = _reservation_source_at(SPEC_ORACLE_SHA)
    occurrences = source.count(STEP_BODY_OLD)
    assert occurrences == 1, f"expected exactly one occurrence of step's body, found {occurrences}"
    return source.replace(STEP_BODY_OLD, new_body, 1)


def _evaluate_step_fresh_process(source: str, current_text: str, event: str) -> dict:
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


def _assert_postcondition_violation(response: dict, description: str) -> None:
    result = response.get("result") or {}
    assert not result.get("value"), f"{description} returned a successful result: {response}"
    categories = {d.get("category") for d in (response.get("diagnostics") or [])}
    assert "postcondition_violation" in categories, (
        f"expected a postcondition_violation diagnostic for {description}: {response}"
    )


def test_int_deliberately_wrong_step_bodies_are_caught_and_the_unmodified_source_stays_clean():
    """Given the reservation source and three deliberately wrong copies of
    `step`'s body -- missing guard, flipped flag, always-reject -- when
    the Owner directly evaluates `step` against each mutated copy on the
    inputs that expose its specific defect, and against the unmodified
    source on all six valid inputs, then every mutated call reports a
    runtime postcondition violation and every unmodified call succeeds
    with the table's expected result."""
    missing_guard_source = _mutated_source(MISSING_GUARD_BODY_NEW)
    response = _evaluate_step_fresh_process(missing_guard_source, "(Reservation 2)", "Reserve")
    _assert_postcondition_violation(response, "missing-guard step((Reservation 2), Reserve)")

    flipped_flag_source = _mutated_source(FLIPPED_FLAG_BODY_NEW)
    for count, event in ALL_SIX_CASES:
        response = _evaluate_step_fresh_process(flipped_flag_source, f"(Reservation {count})", event)
        _assert_postcondition_violation(response, f"flipped-flag step((Reservation {count}), {event})")

    always_reject_source = _mutated_source(ALWAYS_REJECT_BODY_NEW)
    for count, event in ACCEPTED_CASES:
        response = _evaluate_step_fresh_process(always_reject_source, f"(Reservation {count})", event)
        _assert_postcondition_violation(response, f"always-reject step((Reservation {count}), {event})")

    unmodified_source = _reservation_source_at(SPEC_ORACLE_SHA)
    for count, event in ALL_SIX_CASES:
        expected_count, expected_accepted = EXPECTED[(count, event)]
        response = _evaluate_step_fresh_process(unmodified_source, f"(Reservation {count})", event)
        assert response.get("status") == "completed", (
            f"unmodified step((Reservation {count}), {event}) must succeed: {response}"
        )
        result = response.get("result") or {}
        expected_text = f"(Outcome (Reservation {expected_count}) {'true' if expected_accepted else 'false'})"
        assert result.get("value") == expected_text, (
            f"unexpected result for unmodified step((Reservation {count}), {event}): {response}"
        )
