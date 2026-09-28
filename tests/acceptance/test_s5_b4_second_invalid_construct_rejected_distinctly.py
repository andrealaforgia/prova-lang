"""Acceptance tests for I1.S5.B4: a second hand-built variant with a
different invalid construct elsewhere in the source -- an unbound name in
`initial`'s body -- is also rejected, with its own category and location,
confirming rejection is not limited to one error shape. The reserve
variant (Bool arithmetic in `step`) is the contrasting error shape.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

from _reservation_fixtures import (
    INIT_BUG_SITE,
    RESERVE_BUG_SITE,
    line_column_of,
    reserve_bug_source,
    run_check,
    unbound_name_source,
)

EXPECTED_UNBOUND_CATEGORY = "unbound_name"
EXPECTED_RESERVE_CATEGORY = "type_mismatch"


def _assert_rejected_once_with_category_at(source, category, site):
    response = run_check(source)
    assert response.get("status") == "invalid_program", (
        f"expected the variant to be rejected, got: {response}"
    )
    expected_line, expected_column = line_column_of(source, site)
    matching = [
        d
        for d in (response.get("diagnostics") or [])
        if d.get("category") == category
    ]
    assert matching, f"no {category!r} diagnostic in: {response}"
    locations = [
        ((d.get("location") or {}).get("line"), (d.get("location") or {}).get("column"))
        for d in matching
    ]
    assert (expected_line, expected_column) in locations, (
        f"no {category!r} diagnostic points at the injected defect {site!r} "
        f"(line {expected_line} column {expected_column}); got {locations}: {response}"
    )
    return response


def test_b4_unbound_name_variant_is_rejected_as_unbound_name_at_its_defect():
    """Given a variant with an unbound name in `initial`'s body, when the
    Owner runs the check operation, then it is rejected as invalid_program
    with an unbound_name diagnostic located at the unbound name."""
    _assert_rejected_once_with_category_at(
        unbound_name_source(), EXPECTED_UNBOUND_CATEGORY, INIT_BUG_SITE
    )


def test_b4_reserve_variant_is_rejected_as_type_mismatch_at_its_defect():
    """Given a variant with Bool arithmetic in `step`'s reserve branch,
    when the Owner runs the check operation, then it is rejected as
    invalid_program with a type_mismatch diagnostic located at the
    offending expression."""
    _assert_rejected_once_with_category_at(
        reserve_bug_source(), EXPECTED_RESERVE_CATEGORY, RESERVE_BUG_SITE
    )
