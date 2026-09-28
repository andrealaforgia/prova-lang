"""I1.S4.P5 (twelve controls): the six-input control battery runs before and
after all three mutation batteries; all twelve responses are clean successes
whose outcome matches the pinned table and whose source digest is the
protected source's, never a mutant's. Includes (1,Reserve) and (2,Release),
which are not among step's four declared examples.
"""

from __future__ import annotations

from _i1_s4_v4 import (
    ALL_SIX, PINNED_TABLE, assert_success_with_outcome, campaign, derive_all, select, sha256, sources,
)

DECLARED = [(0, "Reserve"), (2, "Reserve"), (1, "Release"), (0, "Release")]


def test_p5_twelve_control_calls_executed_in_order_around_the_mutation_runs():
    labels = [c.label if c.label != "mutant" else "mutant:" + c.source_id for c in campaign()]
    assert labels == (["control-before"] * 6 + ["mutant:missing-guard"] * 6 + ["mutant:flipped-flag"] * 6
                      + ["mutant:always-reject"] * 6 + ["control-after"] * 6)
    before, after = select("control-before"), select("control-after")
    assert [(c.count, c.event) for c in before] == ALL_SIX == [(c.count, c.event) for c in after]


def test_p5_every_control_matches_the_table_and_all_postcondition_clauses():
    derived = derive_all(sources()["protected"])
    for c in select("control-before") + select("control-after"):
        key = (c.count, c.event)
        assert_success_with_outcome(c, PINNED_TABLE[key])
        assert derived[key].postcondition_holds and derived[key].outcome == PINNED_TABLE[key]


def test_p5_controls_never_reuse_mutant_source():
    protected = sha256(sources()["protected"])
    mutants = {sha256(sources()[m]) for m in ("missing-guard", "flipped-flag", "always-reject")}
    assert protected not in mutants
    for c in select("control-before") + select("control-after"):
        assert c.source_digest == protected == c.response["source_digest"]


def test_p5_before_and_after_are_identical_and_cover_the_undeclared_inputs():
    before = [(c.count, c.event, c.response["result"]) for c in select("control-before")]
    after = [(c.count, c.event, c.response["result"]) for c in select("control-after")]
    assert before == after
    assert {(1, "Reserve"), (2, "Release")}.isdisjoint(DECLARED)
    assert {(1, "Reserve"), (2, "Release")} <= {(c.count, c.event) for c in select("control-after")}


def test_p5_success_is_postcondition_checked_not_merely_correct():
    # Differential evidence: the same request shape on a body that violates a
    # postcondition is refused, so a clean success carries a passed check.
    (bad,) = [c for c in select(source_id="always-reject") if (c.count, c.event) == (0, "Reserve")]
    (good,) = [c for c in select("control-before") if (c.count, c.event) == (0, "Reserve")]
    assert bad.response["diagnostics"] and not good.response["diagnostics"]
    assert bad.response["claim"] == good.response["claim"]
