"""I1.S2.P2: every passing result is attributed to its own function and
example, never folded into a total.

Given the same `examples` run over the protected source, when the Owner
inspects the public response's per-example identities, then all seven are
distinguishable -- across functions and within the same function -- and
form a one-to-one correspondence with the independent inventory (two
`valid-state`, one `initial`, four `step`), with no identity missing,
duplicated or merged.
"""

from __future__ import annotations

from _i1_s2_fixtures import INVENTORY, extract_results, index_by_identity, protected_source, run_examples


def test_p2_every_result_is_individually_attributed():
    returncode, response, stdout, stderr = run_examples(protected_source())
    assert returncode == 0, f"tool failure running examples: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"

    results = extract_results(response)
    # No merged/duplicated entries: exactly seven, all distinct identities.
    assert len(results) == 7, f"expected seven distinct results, got {len(results)}: {results}"
    indexed = index_by_identity(results)  # raises on a duplicate identity

    by_function: dict[str, set[int]] = {}
    for function, ordinal in indexed:
        by_function.setdefault(function, set()).add(ordinal)

    assert by_function == {
        "valid-state": {0, 1},
        "initial": {0},
        "step": {0, 1, 2, 3},
    }, f"per-function example ordinals did not match the inventory partition: {by_function}"

    for expected in INVENTORY:
        identity = (expected["function"], expected["ordinal"])
        entry = indexed[identity]
        assert entry["arguments"] == expected["arguments"] or list(entry["arguments"]) == expected["arguments"], (
            f"{identity}: reported arguments {entry['arguments']!r} do not match the "
            f"declared example's own arguments {expected['arguments']!r}"
        )
        assert entry["passed"] is True, f"{identity}: expected a pass, got {entry}"
