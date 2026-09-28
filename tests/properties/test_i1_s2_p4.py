"""I1.S2.P4: mutated copies never contaminate the protected source.

Given one protected-source run followed by each of the eleven mutated
copies from I1.S2.P3, with another protected-source run immediately after
every copy, when this whole sequence executes through the same public
`examples` operation, then all twelve protected-source runs report the same
seven passing example identities and expected outcomes, and the protected
source's own byte content is unchanged before and after the sequence.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

from _i1_s2_fixtures import (
    MUTATIONS,
    digest,
    expected_outcome_for,
    extract_results,
    index_by_identity,
    mutated_source,
    protected_source,
    run_examples,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def _working_tree_digests() -> dict[str, str]:
    paths = [REPO_ROOT / "SPEC.md", *sorted((REPO_ROOT / "conformance").rglob("reservation*.prova"))]
    return {str(p.relative_to(REPO_ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def _assert_protected_run_is_clean(label: str):
    source = protected_source()
    returncode, response, stdout, stderr = run_examples(source)
    assert returncode == 0, f"{label}: tool failure running examples: stderr={stderr!r}"
    assert response is not None, f"{label}: non-JSON response: {stdout!r}"

    results = extract_results(response)
    assert len(results) == 7, f"{label}: expected seven results, got {len(results)}: {results}"
    indexed = index_by_identity(results)

    expected_outcome = expected_outcome_for(None)
    assert set(indexed) == set(expected_outcome), (
        f"{label}: protected-source identities changed shape: {sorted(indexed)}"
    )
    for identity in expected_outcome:
        assert indexed[identity]["passed"] is True, (
            f"{label}: protected-source example {identity} did not pass: {indexed[identity]}"
        )
    return digest(source)


def test_p4_protected_source_stays_isolated_across_mutated_runs():
    files_before = _working_tree_digests()
    before_digest = _assert_protected_run_is_clean("initial protected run")

    for mutation in MUTATIONS:
        mutated = mutated_source(mutation)
        returncode, response, stdout, stderr = run_examples(mutated)
        assert returncode == 0, f"{mutation.id}: tool failure: stderr={stderr!r}"
        assert response is not None, f"{mutation.id}: non-JSON response: {stdout!r}"

        results = extract_results(response)
        indexed = index_by_identity(results)
        targeted_identity = (mutation.function, mutation.ordinal)
        assert indexed[targeted_identity]["passed"] is False, (
            f"{mutation.id}: targeted example did not fail in its own run: "
            f"{indexed[targeted_identity]}"
        )

        _assert_protected_run_is_clean(f"protected run after {mutation.id}")

    assert _working_tree_digests() == files_before, (
        "protected working-tree artefacts changed over the course of the sequence"
    )
    assert digest(protected_source()) == before_digest
