"""I1.S5.P4 / I1.S5.B1 / I1.S5.B4: `check` finds a second, differently
shaped defect -- an unbound name in `initial`'s body -- confirming
rejection is not limited to the Bool-arithmetic shape from I1.S5.P2/P3.

Given a variant where `initial`'s body reads an unbound name instead of
`(Reservation 0)`, when `check` runs against it, then it is rejected as an
invalid program with a location that tracks the name's position in the
source (not a fixed, layout-independent report), and after the single
repair (restoring `0`), the source is accepted again.

B4 also requires this rejection to carry "its own category", confirming
rejection is not limited to one error shape. A checker reporting one fixed
generic category for every static defect would satisfy every other
assertion in this module while never actually identifying what went
wrong, so this file also checks that the unbound-name category differs
from the Bool-arithmetic type-error category from I1.S5.P2/P3.
"""

from __future__ import annotations

from _i1_s5_fixtures import (
    UNBOUND_NAME,
    assert_accepted,
    diagnostic_locations,
    line_col,
    assert_rejected_as_invalid_program,
    location_of,
    render,
    reserve_bug_source,
    run_check,
    unbound_bug_source,
    unbound_fix_source,
)


def test_p4_unbound_name_variant_is_rejected_as_invalid_program():
    returncode, response, stdout, stderr = run_check(unbound_bug_source())
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)


def test_p4_unbound_name_is_absent_from_every_binding_site():
    source = unbound_bug_source()
    assert UNBOUND_NAME in source
    # Independent inspection of bindings: every declared top-level name and
    # `initial`'s own (empty) parameter list, transcribed from the source
    # text rather than derived from any diagnostic the tool produces.
    declared_top_level = {
        line.split()[1]
        for line in source.splitlines()
        if line.startswith("(deftype ") or line.startswith("(defn ")
    }
    assert UNBOUND_NAME not in declared_top_level
    initial_signature_line = next(
        line for line in source.splitlines() if line.strip() == "(sig () -> Reservation ! pure)"
    )
    assert UNBOUND_NAME not in initial_signature_line


def test_p4_repaired_source_is_accepted():
    fixed = unbound_fix_source()
    returncode, response, stdout, stderr = run_check(fixed)
    assert_accepted(returncode, response, stdout, stderr)


def test_p4_bug_and_fix_actually_differ():
    assert unbound_bug_source() != unbound_fix_source()


def test_p4_location_tracks_the_unbound_names_position():
    base = unbound_bug_source()
    returncode, response, stdout, stderr = run_check(base)
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)
    base_line, base_column = location_of(response)

    shifted = render(base, blank_lines=2, indent_spaces=3)
    returncode, response, stdout, stderr = run_check(shifted)
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)
    shifted_line, shifted_column = location_of(response)

    assert shifted_line == base_line + 2, (
        f"expected line {base_line + 2}, got {shifted_line}"
    )
    assert shifted_column == base_column + 3, (
        f"expected column {base_column + 3}, got {shifted_column}"
    )


def test_p4_category_differs_from_the_bool_arithmetic_type_error_category():
    returncode, response, stdout, stderr = run_check(unbound_bug_source())
    unbound_categories = assert_rejected_as_invalid_program(returncode, response, stdout, stderr)

    returncode, response, stdout, stderr = run_check(reserve_bug_source())
    type_error_categories = assert_rejected_as_invalid_program(returncode, response, stdout, stderr)

    assert unbound_categories.isdisjoint(type_error_categories), (
        f"the unbound-name rejection and the Bool-arithmetic type-error rejection "
        f"reported overlapping categories, so neither category actually denotes "
        f"its own defect as B3/B4 require: unbound={unbound_categories}, "
        f"type_error={type_error_categories}"
    )


def test_p4_unbound_name_is_reported_as_unbound_name_at_the_name_in_every_layout():
    """Resolved against each submitted text: the diagnostic category is
    exactly `unbound_name` and one of its locations is where `missing-count`
    actually starts in that text (found by counting newlines)."""
    base = unbound_bug_source()
    for blank_lines in (0, 1, 3):
        for indent_spaces in (0, 2):
            rendered = render(base, blank_lines, indent_spaces)
            assert rendered.count(UNBOUND_NAME) == 1
            expected = line_col(rendered, rendered.index(UNBOUND_NAME))
            returncode, response, stdout, stderr = run_check(rendered)
            categories = assert_rejected_as_invalid_program(returncode, response, stdout, stderr)
            assert "unbound_name" in categories, (
                f"blank_lines={blank_lines}, indent_spaces={indent_spaces}: "
                f"category is not unbound_name: {categories}"
            )
            reported = diagnostic_locations(response, "unbound_name")
            assert expected in reported, (
                f"blank_lines={blank_lines}, indent_spaces={indent_spaces}: no "
                f"unbound_name at {expected}; reported {sorted(reported)}: {response}"
            )
