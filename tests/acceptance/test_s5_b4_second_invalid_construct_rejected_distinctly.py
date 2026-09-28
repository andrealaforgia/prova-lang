"""Acceptance test for I1.S5.B4: a second hand-built variant with a
different invalid construct elsewhere in the source -- an unbound name in
`initial`'s body -- is also rejected, with its own category and location,
confirming rejection is not limited to one error shape.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

INIT_OLD = "  (examples (example (initial) => (Reservation 0)))\n  (Reservation 0))\n"
INIT_BUG = "  (examples (example (initial) => (Reservation 0)))\n  (Reservation missing-count))\n"

RESERVE_OLD = "(Outcome (Reservation (+ (.reserved current) 1)) true)"
RESERVE_BUG = (
    "(Outcome (Reservation (if (= (.reserved current) 1) "
    "(+ true 1) (+ (.reserved current) 1))) true)"
)


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _unbound_name_source() -> str:
    source = _reservation_source()
    assert source.count(INIT_OLD) == 1
    return source.replace(INIT_OLD, INIT_BUG, 1)


def _reserve_bug_source() -> str:
    source = _reservation_source()
    assert source.count(RESERVE_OLD) == 1
    return source.replace(RESERVE_OLD, RESERVE_BUG, 1)


def _run_check(source: str) -> dict:
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


def test_b4_unbound_name_variant_differs_from_the_first_variant():
    assert _unbound_name_source() != _reserve_bug_source()


def test_b4_second_invalid_construct_is_rejected_with_its_own_category_and_location():
    """Given a second hand-built variant with a different invalid
    construct elsewhere in the source, when the Owner runs the check
    operation against it, then it is also rejected with its own category
    and location, confirming rejection is not limited to one error shape."""
    unbound_response = _run_check(_unbound_name_source())
    assert unbound_response.get("status") == "invalid_program", (
        f"expected the unbound-name variant to be rejected, got: {unbound_response}"
    )
    unbound_diagnostics = unbound_response.get("diagnostics") or []
    assert unbound_diagnostics, f"rejection carried no diagnostics: {unbound_response}"
    unbound_diagnostic = unbound_diagnostics[0]
    unbound_category = unbound_diagnostic.get("category")
    assert unbound_category, f"diagnostic did not name a category: {unbound_diagnostic}"
    unbound_location = unbound_diagnostic.get("location") or {}
    assert isinstance(unbound_location.get("line"), int) and isinstance(
        unbound_location.get("column"), int
    ), f"diagnostic did not name a line/column location: {unbound_diagnostic}"

    reserve_response = _run_check(_reserve_bug_source())
    reserve_categories = {
        d.get("category") for d in (reserve_response.get("diagnostics") or [])
    }
    assert unbound_category not in reserve_categories, (
        f"the unbound-name defect and the Bool-arithmetic type-error defect "
        f"reported the same category, so rejection does not confirm two "
        f"distinct error shapes: unbound={unbound_category}, reserve={reserve_categories}"
    )
