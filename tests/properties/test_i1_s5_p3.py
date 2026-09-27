"""I1.S5.P3 / I1.S5.B2 / I1.S5.B3: the diagnostic for each hidden-type-error
variant locates the offending expression, and tracks it under layout
changes.

Given each of the two invalid fixtures from I1.S5.P2, rendered with 0, 1 or
3 leading blank lines crossed with 0 or 2 additional leading spaces on
every nonblank line (six renderings per fixture, twelve cases total), when
`check` runs against each rendering, then every rejection reports the same
diagnostic category, and the reported line/column moves by exactly the
blank-line and indent-space deltas applied to that rendering relative to
the unrendered fixture -- not a location copied verbatim from the
unrendered fixture, and not a generic file-level report.
"""

from __future__ import annotations

import pytest

from _i1_s5_fixtures import (
    assert_rejected_as_invalid_program,
    location_of,
    release_bug_source,
    render,
    reserve_bug_source,
    run_check,
)

RENDERINGS = [
    (blank_lines, indent_spaces)
    for blank_lines in (0, 1, 3)
    for indent_spaces in (0, 2)
]

assert len(RENDERINGS) == 6

FIXTURES = [
    pytest.param(reserve_bug_source, id="reserve"),
    pytest.param(release_bug_source, id="release"),
]


@pytest.mark.parametrize("fixture_source", FIXTURES)
def test_p3_layout_renderings_are_all_rejected_with_a_consistent_category(fixture_source):
    base = fixture_source()
    categories = set()
    for blank_lines, indent_spaces in RENDERINGS:
        rendered = render(base, blank_lines, indent_spaces)
        returncode, response, stdout, stderr = run_check(rendered)
        found = assert_rejected_as_invalid_program(returncode, response, stdout, stderr)
        categories.add(frozenset(found))
    assert len(categories) == 1, (
        f"the reported category set changed across layout renderings: {categories}"
    )


@pytest.mark.parametrize("fixture_source", FIXTURES)
def test_p3_location_tracks_the_layout_changes(fixture_source):
    base = fixture_source()

    baseline_rendered = render(base, 0, 0)
    assert baseline_rendered == base
    returncode, response, stdout, stderr = run_check(baseline_rendered)
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)
    base_line, base_column = location_of(response)

    seen_lines_and_columns = {(0, 0): (base_line, base_column)}

    for blank_lines, indent_spaces in RENDERINGS:
        if (blank_lines, indent_spaces) == (0, 0):
            continue
        rendered = render(base, blank_lines, indent_spaces)
        returncode, response, stdout, stderr = run_check(rendered)
        assert_rejected_as_invalid_program(returncode, response, stdout, stderr)
        line, column = location_of(response)
        seen_lines_and_columns[(blank_lines, indent_spaces)] = (line, column)

        assert line == base_line + blank_lines, (
            f"blank_lines={blank_lines}, indent_spaces={indent_spaces}: "
            f"expected line {base_line + blank_lines}, got {line}"
        )
        assert column == base_column + indent_spaces, (
            f"blank_lines={blank_lines}, indent_spaces={indent_spaces}: "
            f"expected column {base_column + indent_spaces}, got {column}"
        )

    # A location copied verbatim from the unrendered fixture would report
    # the same (line, column) for every rendering; the six renderings per
    # fixture must actually differ from one another.
    assert len(set(seen_lines_and_columns.values())) == len(RENDERINGS), (
        f"location did not vary across distinct layouts: {seen_lines_and_columns}"
    )
