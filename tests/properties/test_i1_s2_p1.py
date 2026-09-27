"""I1.S2.P1: `examples` reports a pass for every declared example.

Given the protected reservation source's seven declared examples (two for
`valid-state`, one for `initial`, four for `step`), when the real `examples`
operation evaluates them at the candidate revision, then every one is
reported as passed, matched one-to-one against an inventory transcribed by
hand from SPEC.md at the pinned oracle commit -- not a summary count.
"""

from __future__ import annotations

from _prova_client import parse_value
from _i1_s2_fixtures import INVENTORY, extract_results, index_by_identity, protected_source, run_examples


def test_p1_all_seven_declared_examples_pass():
    returncode, response, stdout, stderr = run_examples(protected_source())
    assert returncode == 0, f"tool failure running examples: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"

    results = extract_results(response)
    assert len(results) == 7, f"expected seven example results, got {len(results)}: {results}"

    indexed = index_by_identity(results)
    assert set(indexed) == {(e["function"], e["ordinal"]) for e in INVENTORY}, (
        f"example identities did not match the seven-example inventory: {sorted(indexed)}"
    )

    for expected in INVENTORY:
        identity = (expected["function"], expected["ordinal"])
        entry = indexed[identity]
        assert entry["passed"] is True, (
            f"expected {identity} to pass, got entry={entry}"
        )
        assert parse_value(entry["expected"]) == parse_value(expected["expected"]), (
            f"{identity}: response's own expected value {entry['expected']!r} does not "
            f"match the independent inventory's {expected['expected']!r}"
        )
        assert parse_value(entry["actual"]) == parse_value(expected["expected"]), (
            f"{identity}: actual result {entry['actual']!r} does not match the "
            f"independently transcribed expected value {expected['expected']!r}"
        )
