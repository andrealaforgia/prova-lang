"""Acceptance tests for I1.S2.B1-B3: run every function's declared examples
through the `examples` operation and see them pass, attributed one per
function/example, with a wrong-expected-value copy failing in isolation.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

DECLARED_IDENTITIES = {
    ("valid-state", 0), ("valid-state", 1),
    ("initial", 0),
    ("step", 0), ("step", 1), ("step", 2), ("step", 3),
}


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _run_examples(source: str) -> dict:
    request = {"prova": "i1", "operation": "examples", "source": source}
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure running examples: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response: {proc.stdout!r}")


def _results(response: dict) -> list[dict]:
    assert response.get("operation") == "examples", response
    assert response.get("status") == "completed", response
    results = ((response.get("result") or {}).get("examples")) or []
    assert results, f"examples response carried no per-example results: {response}"
    return results


def test_b1_all_seven_declared_examples_pass():
    """Given the reservation source's declared examples (two for
    valid-state, one for initial, four for step), when the Owner runs the
    direct evaluation operation over them, then all seven are reported as
    passed."""
    results = _results(_run_examples(_reservation_source()))

    assert len(results) == 7, f"expected seven example results, got {len(results)}: {results}"
    assert all(entry.get("passed") is True for entry in results), (
        f"not every declared example was reported as passed: {results}"
    )


def test_b2_each_result_attributed_to_its_own_function_and_example():
    """Given the reported outcome, when the Owner reads it, then each
    example's pass is attributed to the specific function and example it
    belongs to, not folded into a single total."""
    results = _results(_run_examples(_reservation_source()))

    identities = set()
    for entry in results:
        assert "function" in entry and "ordinal" in entry, (
            f"result entry carries no per-example identity: {entry}"
        )
        identity = (entry["function"], entry["ordinal"])
        assert identity not in identities, f"duplicate example identity {identity}: {results}"
        identities.add(identity)

    assert identities == DECLARED_IDENTITIES, (
        f"attributed identities did not match the seven declared examples: {sorted(identities)}"
    )


def test_b3_one_wrong_expected_value_fails_while_protected_source_still_passes():
    """Given a separate copy of the reservation source with one declared
    example's expected value deliberately changed to an incorrect one, when
    the Owner runs the same direct evaluation operation against that copy,
    then that one example is reported as failed while the protected
    source's own examples continue to pass unchanged."""
    protected = _reservation_source()
    target = "(valid-state (Reservation 0)) => true"
    replacement = "(valid-state (Reservation 0)) => false"
    assert protected.count(target) == 1, "expected exactly one occurrence to mutate"
    mutated = protected.replace(target, replacement, 1)
    assert mutated != protected

    mutated_by_identity = {
        (e["function"], e["ordinal"]): e["passed"] for e in _results(_run_examples(mutated))
    }
    assert mutated_by_identity.get(("valid-state", 0)) is False, (
        f"mutated example was not reported as failed: {mutated_by_identity}"
    )
    for identity, passed in mutated_by_identity.items():
        if identity != ("valid-state", 0):
            assert passed is True, (
                f"unrelated example {identity} was affected by the mutation: {mutated_by_identity}"
            )

    protected_by_identity = {
        (e["function"], e["ordinal"]): e["passed"] for e in _results(_run_examples(protected))
    }
    assert all(passed is True for passed in protected_by_identity.values()), (
        f"protected source's own examples changed after running the mutated copy: {protected_by_identity}"
    )
