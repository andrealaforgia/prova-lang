"""Acceptance test for I1.S1.INT: Story I1.S1 works end to end through the
product's real surface -- directly evaluate the reservation `step`
function on fresh inputs and see all six table rows reproduced.

Unlike I1.S1.B1 (which pins per-row correctness), this test exercises the
"fresh inputs" clause itself: each of the six rows is submitted to a brand
new `prova` process, in an order that does not match the table's own row
order, and the six independent processes must still reproduce the table
without depending on one another or on argument order -- i.e. this is
genuinely a batch of one-shot evaluations, not a stateful session replaying
declared examples.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

TABLE = [
    (0, "Reserve", 1, True),
    (1, "Reserve", 2, True),
    (2, "Reserve", 2, False),
    (0, "Release", 0, False),
    (1, "Release", 0, True),
    (2, "Release", 1, True),
]

# Deliberately not the table's own order, and not sorted: proves the six
# results don't depend on being run in the order SPEC.md lists them.
SHUFFLED_ORDER = [3, 0, 5, 1, 4, 2]


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _evaluate_step_fresh_process(source: str, before: int, event: str) -> dict:
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
    assert response.get("status") == "completed", f"step({before}, {event}) was not evaluated: {response}"
    value_text = ((response.get("result") or {}).get("value")) or ""
    assert value_text.startswith("(Outcome "), f"unexpected result shape for step({before}, {event}): {value_text!r}"
    inner = value_text[len("(Outcome "):-1]
    state_part, accepted_part = inner.rsplit(" ", 1)
    after = int(state_part[len("(Reservation "):-1])
    accepted = {"true": True, "false": False}[accepted_part]
    return after, accepted


def test_int_all_six_table_rows_reproduced_by_independent_fresh_evaluations():
    """Given the reservation source, when the Owner directly evaluates the
    `step` function on fresh inputs, one independent process per row, in an
    order unrelated to the table, then all six table rows are reproduced."""
    source = _reservation_source()
    reproduced: dict[tuple[int, str], tuple[int, bool]] = {}

    for index in SHUFFLED_ORDER:
        before, event, expected_after, expected_accepted = TABLE[index]
        response = _evaluate_step_fresh_process(source, before, event)
        after, accepted = _after_and_accepted(response, before, event)
        reproduced[(before, event)] = (after, accepted)
        assert (after, accepted) == (expected_after, expected_accepted), (
            f"fresh evaluation of step({before}, {event}) expected "
            f"(after={expected_after}, accepted={expected_accepted}), got "
            f"(after={after}, accepted={accepted})"
        )

    assert set(reproduced) == {(before, event) for before, event, _, _ in TABLE}, (
        f"not all six table rows were reproduced: {sorted(reproduced)}"
    )
