"""Acceptance test for I1.S1.B1: the direct evaluation operation against
`step` reproduces every row of SPEC.md's six-row transition table,
including the two rows no declared example covers ((1, Reserve) and
(2, Release)).

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# The independent oracle: SPEC.md's six-row transition table, copied by
# hand as (before, event, after, accepted).
TABLE = [
    (0, "Reserve", 1, True),
    (1, "Reserve", 2, True),
    (2, "Reserve", 2, False),
    (0, "Release", 0, False),
    (1, "Release", 0, True),
    (2, "Release", 1, True),
]

# The two rows no declared example in SPEC.md's `step` covers.
UNCOVERED_ROWS = {(1, "Reserve"), (2, "Release")}
assert UNCOVERED_ROWS <= {(before, event) for before, event, _, _ in TABLE}


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _evaluate_step(source: str, before: int, event: str) -> dict:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": "step",
        "arguments": [f"(Reservation {before})", f"({event})"],
    }
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure evaluating step({before}, {event}): stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response evaluating step({before}, {event}): {proc.stdout!r}")


def _after_and_accepted(response: dict, before: int, event: str) -> tuple[int, bool]:
    assert response.get("operation") == "evaluate", response
    assert response.get("status") == "completed", (
        f"step({before}, {event}) was not evaluated: {response}"
    )
    value_text = ((response.get("result") or {}).get("value")) or ""
    assert value_text.startswith("(Outcome "), f"unexpected result shape for step({before}, {event}): {value_text!r}"
    # "(Outcome (Reservation N) true|false)"
    inner = value_text[len("(Outcome "):-1]
    state_part, accepted_part = inner.rsplit(" ", 1)
    assert state_part.startswith("(Reservation ") and state_part.endswith(")")
    after = int(state_part[len("(Reservation "):-1])
    accepted = {"true": True, "false": False}[accepted_part]
    return after, accepted


def test_b1_every_table_row_is_reproduced_by_direct_evaluation():
    """Given the reservation source, when the Owner runs the direct
    evaluation operation against `step` for each of the six table rows in
    turn, including the two no declared example covers, then the reported
    state and accepted flag match the table exactly for every row."""
    source = _reservation_source()

    for before, event, expected_after, expected_accepted in TABLE:
        response = _evaluate_step(source, before, event)
        after, accepted = _after_and_accepted(response, before, event)
        assert (after, accepted) == (expected_after, expected_accepted), (
            f"step({before}, {event}) expected (after={expected_after}, "
            f"accepted={expected_accepted}), got (after={after}, accepted={accepted}); "
            f"full response={response}"
        )
