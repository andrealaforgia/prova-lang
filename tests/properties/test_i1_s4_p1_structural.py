"""I1.S4.P1 (structural): each mutation source differs from the protected
source only inside step's body, and that body implements exactly its stated
mutation.

The syntax trees are compared node by node with an independent reader; the
body is located structurally (the last element of the `defn step` form), not
by the replacement boundaries of the mutation helper. Each submitted body is
then evaluated over all six valid inputs and step's three unchanged `ensures`
clauses are evaluated on the results, from the submitted text itself.
"""

from __future__ import annotations

import pytest

from _i1_s4_v4 import (
    ALL_SIX, PINNED_TABLE, changed_nodes, derive_all, non_body_nodes, read_forms, sha256, sources, step_body,
)

SRC = sources()
REFERENCE = read_forms(SRC["protected"])
MUTANT_IDS = ["missing-guard", "flipped-flag", "always-reject"]


def test_p1_reference_is_the_pinned_protected_source_and_evaluates_to_the_table():
    derived = derive_all(SRC["protected"])
    assert {k: v.outcome for k, v in derived.items()} == PINNED_TABLE
    assert all(v.postcondition_holds for v in derived.values())


@pytest.mark.parametrize("mutant_id", MUTANT_IDS)
def test_p1_only_steps_body_changes(mutant_id):
    candidate = read_forms(SRC[mutant_id])
    assert changed_nodes(REFERENCE, candidate) == ["step-body"]
    # every node outside step's body, including step's signature, requires,
    # ensures and examples, is identical
    assert non_body_nodes(candidate) == non_body_nodes(REFERENCE)
    assert step_body(candidate) != step_body(REFERENCE)
    assert sha256(SRC[mutant_id]) != sha256(SRC["protected"])


def test_p1_three_mutants_are_pairwise_distinct():
    bodies = [repr(step_body(read_forms(SRC[m]))) for m in MUTANT_IDS]
    assert len(set(bodies)) == 3


def test_p1_missing_guard_body_derivation():
    d = derive_all(SRC["missing-guard"])
    # unconditional Reserve increment, Release unchanged
    for (count, event), row in d.items():
        expected = PINNED_TABLE[(count, event)]
        if event == "Reserve":
            assert row.outcome == (count + 1, True)
        else:
            assert row.outcome == expected
    violating = [k for k, v in d.items() if not v.postcondition_holds]
    assert violating == [(2, "Reserve")]
    # the only failing rows break the count invariant (result count 3)
    assert d[(2, "Reserve")].result_count == 3 and not d[(2, "Reserve")].invariant_holds
    assert [k for k in ALL_SIX if k != (2, "Reserve")] and all(
        d[k].outcome == PINNED_TABLE[k] for k in ALL_SIX if k != (2, "Reserve")
    )


def test_p1_flipped_flag_body_derivation():
    d = derive_all(SRC["flipped-flag"])
    for key, row in d.items():
        after, accepted = PINNED_TABLE[key]
        assert row.outcome == (after, not accepted), key   # state preserved, flag negated
        assert row.invariant_holds, f"{key}: the count invariant must still hold"
        assert not row.postcondition_holds, key
    assert len(d) == 6


def test_p1_always_reject_body_derivation():
    d = derive_all(SRC["always-reject"])
    for (count, event), row in d.items():
        assert row.outcome == (count, False)
        assert row.invariant_holds, "invariant-only checking would accept this body"
        accepted_by_table = PINNED_TABLE[(count, event)][1]
        assert row.postcondition_holds == (not accepted_by_table), (count, event)
    assert sorted(k for k, v in d.items() if not v.postcondition_holds) == sorted(
        [(0, "Reserve"), (1, "Reserve"), (1, "Release"), (2, "Release")]
    )


def test_p1_comparison_is_capable_of_flagging_changes_outside_step_body():
    # positive controls: a weakened ensures clause, and a changed example, are not "body only"
    src = SRC["protected"]
    weakened = src.replace("(valid-state (.state result))\n    (= (.accepted result)", "(= (.accepted result)", 1)
    assert weakened != src and changed_nodes(REFERENCE, read_forms(weakened)) != ["step-body"]
    edited_example = src.replace("(Outcome (Reservation 2) false))\n    (example (step (Reservation 1) (Release))",
                                 "(Outcome (Reservation 2) true))\n    (example (step (Reservation 1) (Release))", 1)
    assert edited_example != src and changed_nodes(REFERENCE, read_forms(edited_example)) == ["other:step"]
