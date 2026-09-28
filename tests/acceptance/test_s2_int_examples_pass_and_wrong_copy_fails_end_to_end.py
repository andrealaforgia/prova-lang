"""Acceptance test for I1.S2.INT: the Owner runs the protected reservation
source's declared examples through the public `prova` command, sees every
one pass, then runs a separate on-disk copy with one expected value
deliberately wrong and sees exactly that named example fail, with the
protected reference left byte-for-byte untouched.

Drives only the installed `prova` command over its JSON stdin/stdout
surface (the wrong copy is a real file whose contents are submitted as the
request). No imports from src/prova.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC = REPO_ROOT / "SPEC.md"

DECLARED_IDENTITIES = {
    ("valid-state", 0), ("valid-state", 1),
    ("initial", 0),
    ("step", 0), ("step", 1), ("step", 2), ("step", 3),
}

# (declared example line, the same line with a wrong expected value, identity)
WRONG_VALUE_CASES = [
    (
        "(example (valid-state (Reservation 0)) => true)",
        "(example (valid-state (Reservation 0)) => false)",
        ("valid-state", 0),
    ),
    (
        "(example (step (Reservation 0) (Reserve)) => (Outcome (Reservation 1) true))",
        "(example (step (Reservation 0) (Reserve)) => (Outcome (Reservation 2) true))",
        ("step", 0),
    ),
]

FORBIDDEN_WORDS = ("verified", "proved", "built", "holds")


def _protected_source() -> str:
    text = SPEC.read_text(encoding="utf-8")
    start = text.index("## Core conformance example")
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    return text[fence_start:text.index("```", fence_start)]


def _run_examples(source: str) -> dict:
    request = {"prova": "i1", "operation": "examples", "source": source}
    proc = subprocess.run(
        ["prova"], input=json.dumps(request), capture_output=True, text=True, timeout=10.0
    )
    assert proc.returncode == 0, f"tool failure: stderr={proc.stderr!r}"
    response = json.loads(proc.stdout)
    assert response.get("operation") == "examples", response
    assert response.get("status") == "completed", response
    lowered = proc.stdout.lower()
    for word in FORBIDDEN_WORDS:
        assert word not in lowered, f"response claims {word!r}: {proc.stdout}"
    return response


def _by_identity(response: dict) -> dict:
    entries = (response.get("result") or {}).get("examples") or []
    assert entries, f"no per-example results: {response}"
    return {(e["function"], e["ordinal"]): e for e in entries}


def _digest(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.mark.parametrize("original,wrong,identity", WRONG_VALUE_CASES)
def test_int_unchanged_examples_pass_then_wrong_copy_fails_only_the_named_example(
    tmp_path, original, wrong, identity
):
    """Given the protected reservation source, when its declared examples
    run unchanged, then all seven pass; and given a separate copy on disk
    with one expected value made wrong, when the same operation runs on the
    copy, then only the named example fails (showing the wrong expected and
    the true actual value) while the protected reference is untouched and
    still passes."""
    spec_digest_before = _digest(SPEC)
    protected = _protected_source()

    baseline = _by_identity(_run_examples(protected))
    assert set(baseline) == DECLARED_IDENTITIES, sorted(baseline)
    assert all(e["passed"] is True for e in baseline.values()), baseline

    assert protected.count(original) == 1, "expected exactly one line to mutate"
    copy_path = tmp_path / "reservation-wrong-expected.prova"
    copy_path.write_text(protected.replace(original, wrong, 1), encoding="utf-8")
    assert copy_path.read_text(encoding="utf-8") != protected

    mutated = _by_identity(_run_examples(copy_path.read_text(encoding="utf-8")))
    assert set(mutated) == DECLARED_IDENTITIES, sorted(mutated)
    failed = sorted(i for i, e in mutated.items() if e["passed"] is not True)
    assert failed == [identity], f"expected only {identity} to fail, got {failed}"
    assert mutated[identity]["expected"] != baseline[identity]["expected"]
    assert mutated[identity]["actual"] == baseline[identity]["actual"], (
        "the failing example must report the true actual value"
    )

    assert _digest(SPEC) == spec_digest_before, "protected SPEC.md was modified"
    assert _protected_source() == protected
    rerun = _by_identity(_run_examples(protected))
    assert all(e["passed"] is True for e in rerun.values()), rerun
