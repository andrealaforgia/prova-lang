"""I1.S4.P3 / I1.S4.B2: a flipped acceptance flag is caught at runtime for
every valid input, including cases whose count still satisfies the invariant.

Given the flipped-flag mutation source, evaluated directly on all six valid
(count, event) pairs, when the tool runs `step`, then every call reports a
runtime postcondition violation and none reports a successful result. The
unmodified protected source is evaluated on the same six inputs as a paired
control and must succeed on all of them.
"""

from __future__ import annotations

from _i1_s4_fixtures import (
    COUNTS,
    EVENTS,
    MUTANTS,
    assert_postcondition_violation,
    assert_success,
    evaluate_step,
    independent_expected_outcome,
    mutated_source,
    protected_source,
)

FLIPPED_FLAG = next(m for m in MUTANTS if m.id == "flipped-flag")

ALL_SIX_CASES = [(count, event) for count in COUNTS for event in EVENTS]
assert len(ALL_SIX_CASES) == 6


def test_p3_flipped_flag_rejected_at_runtime_for_all_six_cases():
    source = mutated_source(FLIPPED_FLAG)
    executed = []
    for count, event in ALL_SIX_CASES:
        returncode, response, stdout, stderr = evaluate_step(source, count, event)
        assert_postcondition_violation(returncode, response, stdout, stderr)
        executed.append((count, event))
    assert executed == ALL_SIX_CASES, "not all six cases executed"


def test_p3_paired_control_succeeds_on_all_six_cases():
    source = protected_source()
    executed = []
    for count, event in ALL_SIX_CASES:
        expected_count, expected_accepted = independent_expected_outcome(None, count, event)
        returncode, response, stdout, stderr = evaluate_step(source, count, event)
        assert_success(
            returncode, response, stdout, stderr,
            expected_count=expected_count, expected_accepted=expected_accepted,
        )
        executed.append((count, event))
    assert executed == ALL_SIX_CASES, "not all six control cases executed"
