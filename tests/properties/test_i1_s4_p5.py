"""I1.S4.P5 / I1.S4.B4: the unmodified source is a stable positive control
around the mutation runs.

Given the unmodified reservation source, when it is evaluated on all six
valid (count, event) pairs -- including (1,Reserve) and (2,Release), which
are not among `step`'s four declared examples -- both before and after the
three mutation sources are exercised, then every call succeeds both times
with a result matching the independently derived table, and the two runs
report identical results.
"""

from __future__ import annotations

from _i1_s4_fixtures import (
    COUNTS,
    EVENTS,
    MUTANTS,
    assert_success,
    evaluate_step,
    independent_expected_outcome,
    mutated_source,
    protected_source,
)

ALL_SIX_CASES = [(count, event) for count in COUNTS for event in EVENTS]
assert (1, "Reserve") in ALL_SIX_CASES and (2, "Release") in ALL_SIX_CASES


def _run_control_battery(source: str) -> dict[tuple[int, str], tuple[int, bool]]:
    results = {}
    for count, event in ALL_SIX_CASES:
        expected_count, expected_accepted = independent_expected_outcome(None, count, event)
        returncode, response, stdout, stderr = evaluate_step(source, count, event)
        assert_success(
            returncode, response, stdout, stderr,
            expected_count=expected_count, expected_accepted=expected_accepted,
        )
        results[(count, event)] = (expected_count, expected_accepted)
    return results


def test_p5_positive_control_succeeds_before_and_after_mutation_runs():
    source = protected_source()

    before = _run_control_battery(source)

    for mutant in MUTANTS:
        mutant_source = mutated_source(mutant)
        for count, event in ALL_SIX_CASES:
            evaluate_step(mutant_source, count, event)

    after = _run_control_battery(source)

    assert before == after == {
        (count, event): independent_expected_outcome(None, count, event)
        for count, event in ALL_SIX_CASES
    }
