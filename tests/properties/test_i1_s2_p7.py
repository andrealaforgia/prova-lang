"""I1.S2.P7: `examples` reports exactly one result per declared example,
for any number of functions and any number of examples per function.

The fixed seven-example reservation spec (P1-P6) proves the count and
attribution rules hold for one particular shape (2, 1, 4 examples across
three functions). It cannot distinguish that from an implementation that
happens to work for exactly seven examples spread that way -- one that
silently drops or double-counts examples when the number of functions or
the number of examples per function differs would still pass every one of
those tests.

Given a synthetic `core-0` program built from N identity functions (each
`(sig ((x Int)) -> Int ! pure)` with body `x`), the i-th function declaring
M_i examples `(example (f_i k) => k)` for k in 0..M_i-1, when the real
`examples` operation runs against it, then the response reports exactly
sum(M_i) results, one per (function, ordinal) pair with no gaps,
duplicates or merges, and every one passes (the body always returns its own
argument).

N and M_i are drawn by Hypothesis rather than fixed, so the count/shape
invariant is checked across shapes the fixed spec never varies.
Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which shapes Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from _prova_client import parse_value
from _i1_s2_fixtures import extract_results, index_by_identity, run_examples

_shapes = st.lists(st.integers(min_value=1, max_value=5), min_size=1, max_size=5)


def _function_name(i: int) -> str:
    return f"synthetic-identity-{i}"


def _build_source(example_counts: list[int]) -> str:
    declarations = []
    for i, count in enumerate(example_counts):
        name = _function_name(i)
        examples = " ".join(f"(example ({name} {k}) => {k})" for k in range(count))
        declarations.append(
            f"(defn {name} (sig ((x Int)) -> Int ! pure) (examples {examples}) x)"
        )
    return " ".join(declarations)


@settings(derandomize=True, max_examples=25, deadline=None)
@given(example_counts=_shapes)
def test_p7_result_count_and_attribution_track_arbitrary_shape(example_counts):
    source = _build_source(example_counts)
    returncode, response, stdout, stderr = run_examples(source)
    assert returncode == 0, f"tool failure running examples: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"

    results = extract_results(response)
    total = sum(example_counts)
    assert len(results) == total, (
        f"shape {example_counts}: expected {total} example results "
        f"(sum of per-function example counts), got {len(results)}: {results}"
    )

    indexed = index_by_identity(results)  # raises on a duplicate identity
    expected_identities = {
        (_function_name(i), k)
        for i, count in enumerate(example_counts)
        for k in range(count)
    }
    assert set(indexed) == expected_identities, (
        f"shape {example_counts}: attributed identities did not match the "
        f"declared examples: {sorted(indexed)} vs {sorted(expected_identities)}"
    )

    for (function, ordinal), entry in indexed.items():
        assert entry["passed"] is True, (
            f"shape {example_counts}: {(function, ordinal)} unexpectedly failed: {entry}"
        )
        assert parse_value(entry["actual"]) == ordinal, (
            f"shape {example_counts}: {(function, ordinal)} actual={entry['actual']!r} "
            f"did not reproduce the identity function's own argument"
        )
