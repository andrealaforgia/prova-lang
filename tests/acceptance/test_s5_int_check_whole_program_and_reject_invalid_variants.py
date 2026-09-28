"""Acceptance test for I1.S5.INT: Story I1.S5 works end to end through the
product's real surface -- check the whole reservation program and reject
invalid variants with a structured diagnostic.

Exercises the whole story together, each case its own fresh `prova`
process: the unmodified source is accepted with no errors (I1.S5.B1), and
two differently shaped hand-built variants are each rejected with a
diagnostic naming its own category and location (I1.S5.B2/B3/B4). This is
the story-level check that these behaviours compose correctly on the real
surface, not a restatement of any single behaviour's own acceptance test.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

RESERVE_OLD = "(Outcome (Reservation (+ (.reserved current) 1)) true)"
RESERVE_BUG = (
    "(Outcome (Reservation (if (= (.reserved current) 1) "
    "(+ true 1) (+ (.reserved current) 1))) true)"
)

INIT_OLD = "  (examples (example (initial) => (Reservation 0)))\n  (Reservation 0))\n"
INIT_BUG = "  (examples (example (initial) => (Reservation 0)))\n  (Reservation missing-count))\n"


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _reserve_bug_source() -> str:
    source = _reservation_source()
    assert source.count(RESERVE_OLD) == 1
    return source.replace(RESERVE_OLD, RESERVE_BUG, 1)


def _unbound_name_source() -> str:
    source = _reservation_source()
    assert source.count(INIT_OLD) == 1
    return source.replace(INIT_OLD, INIT_BUG, 1)


def _run_check_fresh_process(source: str) -> dict:
    request = {"prova": "i1", "operation": "check", "source": source}
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response: {proc.stdout!r}")


def test_int_check_accepts_the_valid_program_and_rejects_two_differently_shaped_variants():
    """Given the reservation source and two hand-built invalid variants,
    when the Owner runs the check operation against each, one independent
    process per case, then the valid source is accepted with no errors and
    each variant is rejected with its own category and location."""
    accepted = _run_check_fresh_process(_reservation_source())
    assert accepted.get("status") == "completed", (
        f"the unmodified reservation source must be accepted: {accepted}"
    )
    assert not accepted.get("diagnostics"), (
        f"acceptance carried diagnostics: {accepted}"
    )

    seen_categories = set()
    for source in (_reserve_bug_source(), _unbound_name_source()):
        response = _run_check_fresh_process(source)
        assert response.get("status") == "invalid_program", (
            f"expected the variant to be rejected as an invalid program, got: {response}"
        )
        diagnostics = response.get("diagnostics") or []
        assert diagnostics, f"rejection carried no diagnostics: {response}"
        diagnostic = diagnostics[0]
        category = diagnostic.get("category")
        assert category, f"diagnostic did not name a category: {diagnostic}"
        location = diagnostic.get("location") or {}
        assert isinstance(location.get("line"), int) and isinstance(
            location.get("column"), int
        ), f"diagnostic did not name a line/column location: {diagnostic}"
        seen_categories.add(category)

    assert len(seen_categories) == 2, (
        f"the two differently shaped variants must be distinguished by category, "
        f"confirming rejection is not limited to one error shape: {seen_categories}"
    )
