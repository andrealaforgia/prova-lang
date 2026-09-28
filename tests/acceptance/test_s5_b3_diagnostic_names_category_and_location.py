"""Acceptance test for I1.S5.B3: the diagnostic reported for I1.S5.B2's
rejection names both the category of the error and its location within
the source.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

from _reservation_fixtures import (
    RESERVE_BUG_SITE,
    line_column_of,
    reserve_bug_source,
    run_check,
)

EXPECTED_CATEGORY = "type_mismatch"


def test_b3_rejection_diagnostic_names_category_and_location():
    """Given that rejection, when the Owner reads the reported diagnostic,
    then it names both the category of the error and its location within
    the source."""
    source = reserve_bug_source()
    response = run_check(source)
    assert response.get("status") == "invalid_program", response

    diagnostics = response.get("diagnostics") or []
    assert diagnostics, f"rejection carried no diagnostics: {response}"
    diagnostic = diagnostics[0]

    category = diagnostic.get("category")
    assert category == EXPECTED_CATEGORY, (
        f"diagnostic category {category!r} does not identify this Bool-arithmetic "
        f"defect as {EXPECTED_CATEGORY!r}: {diagnostic}"
    )

    expected_line, expected_column = line_column_of(source, RESERVE_BUG_SITE)
    location = diagnostic.get("location") or {}
    assert (location.get("line"), location.get("column")) == (
        expected_line,
        expected_column,
    ), (
        f"diagnostic location {location} does not point at the injected defect "
        f"{RESERVE_BUG_SITE!r}, expected line {expected_line} column {expected_column}: "
        f"{diagnostic}"
    )
