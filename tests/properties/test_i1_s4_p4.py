"""I1.S4.P4 / I1.S4.B3: an always-reject body is caught at runtime on every
input the table marks accepted, even though its returned count still
satisfies the invariant.

Given the always-reject mutation source, evaluated directly on the four
accepted-input cases from the protected table -- (0,Reserve), (1,Reserve),
(1,Release), (2,Release) -- when the tool runs `step`, then every call
reports a runtime postcondition violation and none reports a successful
result. The two rejected-input rows, (2,Reserve) and (0,Release), are
excluded: always rejecting agrees with their required behaviour, so they are
not part of this violation claim. The unmodified protected source is
evaluated on the same four accepted inputs as a paired control and must
succeed on all of them.
"""

from __future__ import annotations

from _i1_s4_fixtures import (
    MUTANTS,
    assert_postcondition_violation,
    assert_success,
    evaluate_step,
    independent_expected_outcome,
    mutated_source,
    protected_source,
)

ALWAYS_REJECT = next(m for m in MUTANTS if m.id == "always-reject")

ACCEPTED_CASES = [(0, "Reserve"), (1, "Reserve"), (1, "Release"), (2, "Release")]


def test_p4_always_reject_rejected_at_runtime_for_all_accepted_cases():
    source = mutated_source(ALWAYS_REJECT)
    executed = []
    for count, event in ACCEPTED_CASES:
        returncode, response, stdout, stderr = evaluate_step(source, count, event)
        assert_postcondition_violation(returncode, response, stdout, stderr)
        executed.append((count, event))
    assert executed == ACCEPTED_CASES, "not all four accepted-input cases executed"


def test_p4_paired_control_succeeds_on_all_accepted_cases():
    source = protected_source()
    executed = []
    for count, event in ACCEPTED_CASES:
        expected_count, expected_accepted = independent_expected_outcome(None, count, event)
        assert expected_accepted is True, "ACCEPTED_CASES must only contain table-accepted rows"
        returncode, response, stdout, stderr = evaluate_step(source, count, event)
        assert_success(
            returncode, response, stdout, stderr,
            expected_count=expected_count, expected_accepted=True,
        )
        executed.append((count, event))
    assert executed == ACCEPTED_CASES
