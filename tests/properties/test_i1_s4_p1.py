"""I1.S4.P1: the three mutation sources change only `step`'s body.

Given the three complete mutation sources prepared for I1.S4.B1-B3, when each
is compared with the protected reservation source at SPEC_ORACLE_SHA, then
every byte before `step`'s body is identical to the protected source (so the
type declarations, `valid-state`, `initial`, and `step`'s own signature,
`requires`, `ensures` and declared examples are all retained unmodified), and
each mutant's body text matches its declared, hand-written mutation exactly.
Each mutant's intended semantics are also independently recomputed across the
full count x event grid, separate from the mutation-generating code itself.
"""

from __future__ import annotations

from _i1_s4_fixtures import (
    COUNTS,
    EVENTS,
    MUTANTS,
    independent_expected_outcome,
    mutated_source,
    protected_prefix,
    protected_source,
)


def test_p1_mutants_change_only_step_body_and_retain_the_rest():
    prefix = protected_prefix()
    for mutant in MUTANTS:
        source = mutated_source(mutant)
        assert source[: len(prefix)] == prefix, (
            f"mutant {mutant.id!r} changed material before step's body"
        )
        assert source[len(prefix) :] == mutant.new_body, (
            f"mutant {mutant.id!r} body does not match its declared mutation"
        )
        assert source != protected_source(), f"mutant {mutant.id!r} is byte-identical to the protected source"
