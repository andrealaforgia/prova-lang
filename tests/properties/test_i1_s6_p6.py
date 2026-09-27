"""I1.S6.P6 / I1.S6.CHAR1: at the candidate revision, the protected
reservation source, capacity two, step's signature and contract, its seven
declared examples and the six-row transition table are semantically
identical to the pinned pre-implementation baseline (SPEC.md at
30fcbe9dda345d5b7283790023032c0145765428), allowing only formatting-only
differences.

Compares the whole "Core conformance example" section (code block, prose
and table) between the baseline and the working tree, collapsing all
whitespace runs to a single space so only formatting differs -- token
content, order and every literal must match exactly.
"""

from __future__ import annotations

from _i1_s6_fixtures import (
    SPEC_ORACLE_SHA,
    normalize_formatting,
    protected_region,
    spec_text_at,
    working_tree_spec_text,
)


def test_p6_protected_region_unchanged_ignoring_formatting():
    baseline = normalize_formatting(protected_region(spec_text_at(SPEC_ORACLE_SHA)))
    candidate = normalize_formatting(protected_region(working_tree_spec_text()))
    assert candidate == baseline, (
        "the protected reservation region (source, contract, examples and "
        "transition table) changed beyond formatting"
    )
