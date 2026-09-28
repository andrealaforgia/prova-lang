"""I1.S4.P4 (accepted-row evidence, plus comparison rows): the always-reject
copy yields a runtime postcondition violation on each of the four table-
accepted rows although the invariant holds; on the two table-rejected rows
it agrees with the table and succeeds; the unmodified source succeeds on the
four accepted rows with both outcome fields matching the table.
"""

from __future__ import annotations

from _i1_s4_v4 import (
    ACCEPTED_ROWS, PINNED_TABLE, REJECTED_ROWS, assert_runtime_postcondition_violation,
    assert_success_with_outcome, derive_all, select, sources,
)


def _mutant_call(key):
    (c,) = [x for x in select(source_id="always-reject") if (x.count, x.event) == key]
    return c


def test_p4_each_accepted_row_reports_a_runtime_violation():
    assert sorted(ACCEPTED_ROWS) == sorted([(0, "Reserve"), (1, "Reserve"), (1, "Release"), (2, "Release")])
    for key in ACCEPTED_ROWS:
        assert_runtime_postcondition_violation(_mutant_call(key))


def test_p4_invariant_only_checking_would_miss_the_defect():
    d = derive_all(sources()["always-reject"])
    for key in ACCEPTED_ROWS:
        assert d[key].invariant_holds and not d[key].postcondition_holds


def test_p4_rejected_rows_are_comparison_cases_that_succeed():
    for key in REJECTED_ROWS:
        assert_success_with_outcome(_mutant_call(key), PINNED_TABLE[key])


def test_p4_unmodified_source_matches_the_table_on_the_accepted_rows():
    controls = {(c.count, c.event): c for c in select("control-before")}
    for key in ACCEPTED_ROWS:
        assert_success_with_outcome(controls[key], PINNED_TABLE[key])
