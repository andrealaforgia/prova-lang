"""I1.S5.P5 / I1.S5.B1-B4: repairing one of two independent defects does not
conceal the other.

Given the four sources formed by independently including or repairing the
Reserve hidden type error (I1.S5.P2) and the unbound name in `initial`
(I1.S5.P4), when `check` runs against each, then only the fully repaired
source is accepted, the other three are rejected, and each rejection's
diagnostics are attributable to the defect(s) still present in that source
(one defect's repair still exposes the other).
"""

from __future__ import annotations

import pytest

from _i1_s5_fixtures import (
    RESERVE_BUG_MARKER,
    UNBOUND_NAME,
    diagnostic_locations,
    line_col,
    assert_accepted,
    assert_rejected_as_invalid_program,
    combined_source,
    protected_source,
    run_check,
)

COMBINATIONS = [
    pytest.param(False, False, id="neither-defect"),
    pytest.param(True, False, id="reserve-only"),
    pytest.param(False, True, id="unbound-only"),
    pytest.param(True, True, id="both-defects"),
]


def test_p5_combination_matrix_covers_all_four_cases():
    sources = {(r, u): combined_source(reserve_defect=r, unbound_defect=u) for r in (False, True) for u in (False, True)}
    assert len(sources) == 4
    assert sources[(False, False)] == protected_source()
    assert len({s for s in sources.values()}) == 4, "the four combinations must be textually distinct"


@pytest.mark.parametrize("reserve_defect,unbound_defect", COMBINATIONS)
def test_p5_only_the_fully_repaired_source_is_accepted(reserve_defect, unbound_defect):
    source = combined_source(reserve_defect=reserve_defect, unbound_defect=unbound_defect)
    returncode, response, stdout, stderr = run_check(source)

    if not reserve_defect and not unbound_defect:
        assert_accepted(returncode, response, stdout, stderr)
        return

    categories = assert_rejected_as_invalid_program(returncode, response, stdout, stderr)
    assert categories, f"expected at least one diagnostic for a defective source: {response}"


def test_p5_repairing_the_reserve_defect_alone_still_exposes_the_unbound_name():
    # reserve repaired (False), unbound present (True): must still reject.
    source = combined_source(reserve_defect=False, unbound_defect=True)
    assert UNBOUND_NAME in source
    returncode, response, stdout, stderr = run_check(source)
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)


def test_p5_repairing_the_unbound_name_alone_still_exposes_the_reserve_defect():
    # reserve present (True), unbound repaired (False): must still reject.
    source = combined_source(reserve_defect=True, unbound_defect=False)
    assert UNBOUND_NAME not in source
    returncode, response, stdout, stderr = run_check(source)
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)


def test_p5_unmodified_source_remains_an_additional_positive_control():
    returncode, response, stdout, stderr = run_check(protected_source())
    assert_accepted(returncode, response, stdout, stderr)


def test_p5_both_defects_source_reports_each_defect_at_its_own_site():
    """Each diagnostic is resolved against the submitted text: the type_mismatch
    must sit at the start of `(+ true 1)` and the unbound_name at the start of
    `missing-count`, so neither defect is reported only by proxy."""
    source = combined_source(reserve_defect=True, unbound_defect=True)
    assert source.count(RESERVE_BUG_MARKER) == 1
    assert source.count(UNBOUND_NAME) == 1
    returncode, response, stdout, stderr = run_check(source)
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)

    type_site = line_col(source, source.index(RESERVE_BUG_MARKER))
    name_site = line_col(source, source.index(UNBOUND_NAME))
    type_reported = diagnostic_locations(response, "type_mismatch")
    name_reported = diagnostic_locations(response, "unbound_name")
    assert type_site in type_reported, (
        f"no type_mismatch at {type_site}; reported {sorted(type_reported)}: {response}"
    )
    assert name_site in name_reported, (
        f"no unbound_name at {name_site}; reported {sorted(name_reported)}: {response}"
    )
