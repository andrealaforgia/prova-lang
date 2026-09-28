"""I1.S2.P4: failures stay confined to the submitted copy, in both run orders.

For each of the seven example positions: protected, mutated copy, protected;
and mutated copy, protected. The protected runs must report seven passes
with no failure carried over, and the protected artefacts (SPEC.md and any
reservation source file in the repository) must be byte-identical before
and after. Each copy is also compared against the source to prove exactly
one expected-value edit, so an accidental fixture edit cannot pass as the
negative control.
"""

from __future__ import annotations

import hashlib
import pathlib

import pytest

from _prova_client import REPO_ROOT
from _i1_s2_fixtures import INVENTORY, extract_results, index_by_identity, protected_source, run_examples

SOURCE = protected_source()
ENTRIES = list(INVENTORY)


def _artefact_digests() -> dict[str, str]:
    paths = [REPO_ROOT / "SPEC.md", *sorted((REPO_ROOT / "conformance").rglob("reservation*.prova"))]
    return {str(p.relative_to(REPO_ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def _flipped_copy(entry: dict) -> str:
    call = " ".join([entry["function"], *entry["arguments"]])
    old = f"({call}) => {entry['expected']}"
    if entry["expected"] in ("true", "false"):
        replacement = "false" if entry["expected"] == "true" else "true"
    elif entry["function"] == "initial":
        replacement = "(Reservation 4)"
    else:
        replacement = "(Outcome (Reservation 3) true)"
    assert SOURCE.count(old) == 1
    copy = SOURCE.replace(old, f"({call}) => {replacement}", 1)
    assert copy != SOURCE and copy.replace(f"({call}) => {replacement}", old, 1) == SOURCE
    return copy


def _run(source: str, label: str) -> dict:
    returncode, response, stdout, stderr = run_examples(source)
    assert returncode == 0, f"{label}: tool failure: {stderr!r}"
    assert response is not None, f"{label}: non-JSON: {stdout!r}"
    return index_by_identity(extract_results(response))


def _assert_protected_all_pass(label: str) -> None:
    indexed = _run(SOURCE, label)
    assert len(indexed) == 7, f"{label}: {sorted(indexed)}"
    bad = sorted(i for i, r in indexed.items() if r["passed"] is not True)
    assert not bad, f"{label}: protected examples failed (carried over?): {bad}"


@pytest.mark.parametrize("entry", ENTRIES, ids=lambda e: f"{e['function']}-{e['ordinal']}")
@pytest.mark.parametrize("order", ["protected-copy-protected", "copy-protected"])
def test_p4_failures_stay_with_the_copy(entry, order):
    before = _artefact_digests()
    assert "SPEC.md" in before
    if order == "protected-copy-protected":
        _assert_protected_all_pass("first protected run")
    indexed = _run(_flipped_copy(entry), "mutated copy")
    failed = sorted(i for i, r in indexed.items() if r["passed"] is not True)
    assert failed == [(entry["function"], entry["ordinal"])], f"copy run failures: {failed}"
    _assert_protected_all_pass("protected run after the copy")
    assert _artefact_digests() == before, "creating or evaluating a copy modified a protected artefact"
