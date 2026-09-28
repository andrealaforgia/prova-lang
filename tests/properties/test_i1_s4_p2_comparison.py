"""I1.S4.P2 (comparison cases): the missing-guard copy fails at runtime only
at (Reservation 2, Reserve), with the failure attributable to that supplied
call; the other five valid inputs succeed with the table outcome (so the
failure is not blanket rejection), and the unmodified source on (2, Reserve)
succeeds with Outcome(Reservation 2, false).
"""

from __future__ import annotations

from _i1_s4_v4 import (
    ALL_SIX, PINNED_TABLE, assert_runtime_postcondition_violation, assert_success_with_outcome, select,
)


def test_p2_guard_specific_domain_is_the_single_pair_and_it_fails_at_runtime():
    (c,) = [x for x in select(source_id="missing-guard") if (x.count, x.event) == (2, "Reserve")]
    assert c.request["arguments"] == ["(Reservation 2)", "(Reserve)"]
    assert_runtime_postcondition_violation(c)


def test_p2_paired_control_on_the_same_input_returns_the_table_outcome():
    (c,) = [x for x in select("control-before") if (x.count, x.event) == (2, "Reserve")]
    assert_success_with_outcome(c, (2, False))
    assert c.response["result"]["value"] == "(Outcome (Reservation 2) false)"


def test_p2_the_other_five_valid_inputs_succeed_on_the_mutant():
    others = [x for x in select(source_id="missing-guard") if (x.count, x.event) != (2, "Reserve")]
    assert sorted((x.count, x.event) for x in others) == sorted(k for k in ALL_SIX if k != (2, "Reserve"))
    for x in others:
        assert_success_with_outcome(x, PINNED_TABLE[(x.count, x.event)])
