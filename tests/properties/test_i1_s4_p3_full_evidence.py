"""I1.S4.P3 (six-case evidence): every valid input to the flipped-flag copy
yields exactly one runtime postcondition violation and no result, including
(2,Reserve) and (0,Release) where the flag goes false->true, with a separate
recorded response per input and paired protected controls.
"""

from __future__ import annotations

from _i1_s4_v4 import (
    ALL_SIX, PINNED_TABLE, assert_runtime_postcondition_violation, assert_success_with_outcome, derive_all,
    select, sources,
)


def test_p3_six_distinct_calls_each_report_a_runtime_violation():
    calls = select(source_id="flipped-flag")
    assert [(c.count, c.event) for c in calls] == ALL_SIX
    assert len({(c.count, c.event) for c in calls}) == 6
    for c in calls:
        assert_runtime_postcondition_violation(c)


def test_p3_the_false_to_true_boundary_rows_are_included():
    d = derive_all(sources()["flipped-flag"])
    for key in [(2, "Reserve"), (0, "Release")]:
        assert PINNED_TABLE[key][1] is False and d[key].accepted is True
        assert d[key].invariant_holds
    # remaining four rows go true -> false
    for key in [k for k in ALL_SIX if k not in [(2, "Reserve"), (0, "Release")]]:
        assert PINNED_TABLE[key][1] is True and d[key].accepted is False


def test_p3_paired_controls_succeed_on_all_six():
    for c in select("control-before"):
        assert_success_with_outcome(c, PINNED_TABLE[(c.count, c.event)])
