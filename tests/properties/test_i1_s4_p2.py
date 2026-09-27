"""I1.S4.P2 / I1.S4.B1: a missing upper guard is caught at runtime.

Given the missing-guard mutation source, evaluated directly at the one valid
state/event pair the entry precondition admits but the removed guard would
have rejected -- (Reservation 2), (Reserve) -- when the tool runs `step`
directly, then it reports a runtime postcondition violation for that
supplied call, not a successful result. The unmodified protected source is
evaluated on the same input as a paired control and must succeed.
"""

from __future__ import annotations

from _i1_s4_fixtures import (
    MUTANTS,
    assert_postcondition_violation,
    assert_success,
    evaluate_step,
    protected_source,
)

MISSING_GUARD = next(m for m in MUTANTS if m.id == "missing-guard")


def test_p2_missing_guard_boundary_call_is_rejected_at_runtime():
    from _i1_s4_fixtures import mutated_source

    source = mutated_source(MISSING_GUARD)
    returncode, response, stdout, stderr = evaluate_step(source, count=2, event="Reserve")
    assert_postcondition_violation(returncode, response, stdout, stderr)


def test_p2_paired_control_succeeds_on_the_same_boundary_call():
    returncode, response, stdout, stderr = evaluate_step(protected_source(), count=2, event="Reserve")
    assert_success(returncode, response, stdout, stderr, expected_count=2, expected_accepted=False)
