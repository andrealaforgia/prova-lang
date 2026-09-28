"""Acceptance test for I1.S5.B4: a second hand-built variant with a
different invalid construct elsewhere in the source -- an unbound name in
`initial`'s body -- is also rejected, with its own category and location,
confirming rejection is not limited to one error shape.

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


def test_b4_unbound_name_variant_differs_from_the_first_variant():
    assert unbound_name_source() != reserve_bug_source()


def test_b4_second_invalid_construct_is_rejected_with_its_own_category_and_location():
    """Given a second hand-built variant with a different invalid
    construct elsewhere in the source, when the Owner runs the check
    operation against it, then it is also rejected with its own category
    and location, confirming rejection is not limited to one error shape."""
    unbound_source = unbound_name_source()
    unbound_response = run_check(unbound_source)
    assert unbound_response.get("status") == "invalid_program", (
        f"expected the unbound-name variant to be rejected, got: {unbound_response}"
    )
    unbound_diagnostics = unbound_response.get("diagnostics") or []
    assert unbound_diagnostics, f"rejection carried no diagnostics: {unbound_response}"
    unbound_diagnostic = unbound_diagnostics[0]

    unbound_category = unbound_diagnostic.get("category")
    assert unbound_category == EXPECTED_UNBOUND_CATEGORY, (
        f"diagnostic category {unbound_category!r} does not identify this defect as "
        f"{EXPECTED_UNBOUND_CATEGORY!r}: {unbound_diagnostic}"
    )

    expected_unbound_line, expected_unbound_column = line_column_of(
        unbound_source, INIT_BUG_SITE
    )
    unbound_location = unbound_diagnostic.get("location") or {}
    assert (unbound_location.get("line"), unbound_location.get("column")) == (
        expected_unbound_line,
        expected_unbound_column,
    ), (
        f"diagnostic location {unbound_location} does not point at the injected "
        f"defect {INIT_BUG_SITE!r}, expected line {expected_unbound_line} column "
        f"{expected_unbound_column}: {unbound_diagnostic}"
    )

    reserve_source = reserve_bug_source()
    reserve_response = run_check(reserve_source)
    reserve_diagnostics = reserve_response.get("diagnostics") or []
    assert reserve_diagnostics, f"rejection carried no diagnostics: {reserve_response}"
    reserve_diagnostic = reserve_diagnostics[0]
    reserve_category = reserve_diagnostic.get("category")
    assert reserve_category == EXPECTED_RESERVE_CATEGORY, (
        f"diagnostic category {reserve_category!r} does not identify this "
        f"Bool-arithmetic defect as {EXPECTED_RESERVE_CATEGORY!r}: {reserve_diagnostic}"
    )

    assert unbound_category != reserve_category, (
        f"the unbound-name defect and the Bool-arithmetic type-error defect "
        f"reported the same category, so rejection does not confirm two "
        f"distinct error shapes: unbound={unbound_category}, reserve={reserve_category}"
    )
