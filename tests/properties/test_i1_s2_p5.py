"""I1.S2.P5 / I1.S2.CHAR1: the protected reservation example is unchanged
from the pinned SPEC.md oracle.

Given the complete Core conformance example (types, capacity, `valid-state`
/ `initial` / `step`, their contracts, all seven declared examples and the
six-row transition table) at the pinned oracle commit, when compared
against the exact same region in the candidate revision's SPEC.md, then the
two are identical up to insignificant whitespace, with any other difference
-- a changed capacity, a strengthened precondition, a weakened or removed
postcondition, a deleted example, an altered expected value, a rewritten
table row -- failing this check.

This is a characterization guard: it is expected to pass now, before any
implementation exists, and must keep passing through the story.
"""

from __future__ import annotations

import pytest

from _prova_client import SPEC_ORACLE_SHA, _spec_text_at, _working_tree_spec_text, protected_region


def test_p5_protected_reservation_example_matches_pinned_oracle():
    baseline_region = protected_region(_spec_text_at(SPEC_ORACLE_SHA))
    candidate_region = protected_region(_working_tree_spec_text())

    baseline_tokens = baseline_region.split()
    candidate_tokens = candidate_region.split()

    if candidate_tokens != baseline_tokens:
        pytest.fail(
            "SPEC.md's protected reservation example changed beyond formatting "
            f"since oracle commit {SPEC_ORACLE_SHA}:\n"
            f"--- oracle ---\n{baseline_region}\n--- candidate ---\n{candidate_region}"
        )
