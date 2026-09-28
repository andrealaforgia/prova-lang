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

from _reservation_fixtures import (
    INIT_BUG_SITE,
    RESERVE_BUG_SITE,
    line_column_of,
    reservation_source,
    reserve_bug_source,
    run_check,
    unbound_name_source,
)

EXPECTED_CATEGORIES = {
    "reserve": "type_mismatch",
    "unbound": "unbound_name",
}


def test_int_check_accepts_the_valid_program_and_rejects_two_differently_shaped_variants():
    """Given the reservation source and two hand-built invalid variants,
    when the Owner runs the check operation against each, one independent
    process per case, then the valid source is accepted with no errors and
    each variant is rejected with its own category and location."""
    accepted = run_check(reservation_source())
    assert accepted.get("status") == "completed", (
        f"the unmodified reservation source must be accepted: {accepted}"
    )
    assert not accepted.get("diagnostics"), (
        f"acceptance carried diagnostics: {accepted}"
    )

    cases = {
        "reserve": (reserve_bug_source(), RESERVE_BUG_SITE),
        "unbound": (unbound_name_source(), INIT_BUG_SITE),
    }

    seen_categories = set()
    for label, (source, bug_site) in cases.items():
        response = run_check(source)
        assert response.get("status") == "invalid_program", (
            f"expected the {label} variant to be rejected as an invalid program, "
            f"got: {response}"
        )
        diagnostics = response.get("diagnostics") or []
        assert diagnostics, f"rejection carried no diagnostics: {response}"
        diagnostic = diagnostics[0]

        category = diagnostic.get("category")
        assert category == EXPECTED_CATEGORIES[label], (
            f"diagnostic category {category!r} does not identify the {label} "
            f"defect as {EXPECTED_CATEGORIES[label]!r}: {diagnostic}"
        )

        expected_line, expected_column = line_column_of(source, bug_site)
        location = diagnostic.get("location") or {}
        assert (location.get("line"), location.get("column")) == (
            expected_line,
            expected_column,
        ), (
            f"diagnostic location {location} does not point at the injected "
            f"{label} defect {bug_site!r}, expected line {expected_line} column "
            f"{expected_column}: {diagnostic}"
        )
        seen_categories.add(category)

    assert len(seen_categories) == 2, (
        f"the two differently shaped variants must be distinguished by category, "
        f"confirming rejection is not limited to one error shape: {seen_categories}"
    )
