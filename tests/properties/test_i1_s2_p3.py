"""I1.S2.P3: exactly the mutated example fails, attributed correctly.

Given each of the eleven separate copies of the reservation source with one
declared example's expected value deliberately changed (flip-only and
state-only variants across `valid-state`, `initial` and `step`), when the
same `examples` operation runs against that copy, then only the targeted
example is reported as failed -- attributed to its own function and
ordinal -- while the other six pass unchanged.
"""

from __future__ import annotations

import pytest

from _i1_s2_fixtures import (
    MUTATIONS,
    expected_outcome_for,
    extract_results,
    index_by_identity,
    mutated_source,
    run_examples,
)


@pytest.mark.parametrize("mutation", MUTATIONS, ids=[m.id for m in MUTATIONS])
def test_p3_only_the_targeted_example_fails(mutation):
    source = mutated_source(mutation)
    returncode, response, stdout, stderr = run_examples(source)
    assert returncode == 0, f"tool failure running examples for {mutation.id}: stderr={stderr!r}"
    assert response is not None, f"non-JSON response for {mutation.id}: {stdout!r}"

    results = extract_results(response)
    assert len(results) == 7, f"{mutation.id}: expected seven results, got {len(results)}: {results}"
    indexed = index_by_identity(results)

    expected_outcome = expected_outcome_for(mutation.id)
    assert set(indexed) == set(expected_outcome), (
        f"{mutation.id}: example identities changed shape under mutation: {sorted(indexed)}"
    )

    for identity, should_pass in expected_outcome.items():
        entry = indexed[identity]
        assert entry["passed"] is should_pass, (
            f"{mutation.id}: identity {identity} expected passed={should_pass}, "
            f"got entry={entry}"
        )

    targeted_identity = (mutation.function, mutation.ordinal)
    assert indexed[targeted_identity]["passed"] is False, (
        f"{mutation.id}: the mutated example {targeted_identity} was not reported as failed: "
        f"{indexed[targeted_identity]}"
    )
