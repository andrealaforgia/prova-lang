"""Acceptance test for I1.S1.B2: the reported output of a direct
evaluation run describes itself only as evaluation output, never as
verified, proved or built.

Covers the six happy-path table-row runs from I1.S1.B1, plus the two
runtime outcomes that produce free-form diagnostic text rather than a
rendered value -- an entry precondition violation and a postcondition
violation -- since that free text is the most likely place a stray
"holds"/"proves"/"verified" could leak in. Each of the eight cases is its
own parametrized test, so a failure on one case cannot hide whether the
others would also fail.

The universal claim this behaviour makes -- no run of `evaluate`, over any
function, argument shape or error path, ever emits a verified/proved/built
claim -- is not fully covered by these eight hand-picked examples; see the
accompanying property test in `tests/properties/` for that.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

SIX_PAIRS = [
    (0, "Reserve"), (1, "Reserve"), (2, "Reserve"),
    (0, "Release"), (1, "Release"), (2, "Release"),
]

FORBIDDEN_CLAIM = re.compile(
    r"\b(verifie[sd]|verify|verification|prove[nd]?|proves|built|build|holds)\b",
    re.IGNORECASE,
)

# Field names that would carry an epistemic claim (certainty, proof, a
# guarantee) even if phrased without any FORBIDDEN_CLAIM word -- e.g. a
# hypothetical `{"confidence": "certain"}` or `{"guarantee": "total"}`.
# Checked independently of both the response's declared `claim.kind` and the
# free-text word scan, so a mutation that only one of those two would catch
# does not silently pass for lack of a third, unrelated check.
FORBIDDEN_CLAIM_KEYS = {"confidence", "guarantee", "certainty", "proof", "verification", "verified"}

# Unique in the reservation source: the `step` body's accepted-Reserve
# branch. Bumping the increment from 1 to 2 breaks the postcondition
# `(= (.reserved (.state result)) (+ (.reserved current) 1))` for an
# accepted Reserve, without touching requires/ensures/examples.
POSTCONDITION_MUTATION_TARGET = "(Outcome (Reservation (+ (.reserved current) 1)) true)"
POSTCONDITION_MUTATION_REPLACEMENT = "(Outcome (Reservation (+ (.reserved current) 2)) true)"


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _postcondition_violating_source() -> str:
    protected = _reservation_source()
    assert protected.count(POSTCONDITION_MUTATION_TARGET) == 1, "expected exactly one occurrence to mutate"
    mutated = protected.replace(POSTCONDITION_MUTATION_TARGET, POSTCONDITION_MUTATION_REPLACEMENT, 1)
    assert mutated != protected
    return mutated


def _find_forbidden(value) -> list[str]:
    hits: list[str] = []

    def walk(node):
        if isinstance(node, str):
            hits.extend(m.group(0) for m in FORBIDDEN_CLAIM.finditer(node))
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(value)
    return hits


def _run_evaluate(source: str, function: str, arguments: list[str]) -> tuple[dict, str]:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": function,
        "arguments": arguments,
    }
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure evaluating {function}({arguments}): stderr={proc.stderr!r}"
    try:
        response = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response evaluating {function}({arguments}): {proc.stdout!r}")
    return response, proc.stderr


def _find_forbidden_keys(value) -> set[str]:
    hits: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for key, child in node.items():
                if key.lower() in FORBIDDEN_CLAIM_KEYS:
                    hits.add(key)
                walk(child)
        elif isinstance(node, list):
            for child in node:
                walk(child)

    walk(value)
    return hits


def _assert_claim_kind_is_evaluation(response: dict, label: str) -> None:
    assert response.get("claim", {}).get("kind") == "evaluation", (
        f"response does not describe itself as evaluation output for {label}: {response}"
    )


def _assert_no_forbidden_wording(response: dict, stderr: str, label: str) -> None:
    body_hits = _find_forbidden(response)
    stderr_hits = FORBIDDEN_CLAIM.findall(stderr)
    assert not body_hits, f"forbidden claim wording in response body for {label}: {body_hits}; response={response}"
    assert not stderr_hits, f"forbidden claim wording on stderr for {label}: {stderr_hits}"


def _assert_no_forbidden_claim_keys(response: dict, label: str) -> None:
    key_hits = _find_forbidden_keys(response)
    assert not key_hits, f"unexpected epistemic-claim field(s) {key_hits} for {label}: {response}"


def _assert_no_forbidden_claim(response: dict, stderr: str, label: str) -> None:
    # Three independent checks: the declared claim kind, the free-text word
    # scan, and the response's field names. Each targets a different way a
    # forbidden claim could leak, so no single mutation is caught by more
    # than one of them.
    _assert_claim_kind_is_evaluation(response, label)
    _assert_no_forbidden_wording(response, stderr, label)
    _assert_no_forbidden_claim_keys(response, label)


@pytest.mark.parametrize("before,event", SIX_PAIRS, ids=[f"{b}-{e}" for b, e in SIX_PAIRS])
def test_b2_happy_path_run_describes_itself_only_as_evaluation_output(before, event):
    """Given the reported output of a happy-path step run, when the Owner
    reads it, then it describes itself only as evaluation output and
    contains no claim of verified, proved or built."""
    source = _reservation_source()
    response, stderr = _run_evaluate(source, "step", [f"(Reservation {before})", f"({event})"])
    label = f"step({before}, {event})"
    assert response.get("status") == "completed", f"{label} was not evaluated: {response}"
    _assert_no_forbidden_claim(response, stderr, label)


def test_b2_precondition_violation_describes_itself_only_as_evaluation_output():
    """Given the reported output of a run whose entry precondition is
    violated, when the Owner reads it, then it describes itself only as
    evaluation output and contains no claim of verified, proved or built."""
    # (Reservation 5) fails `valid-state` (0 <= reserved <= 2), so `step`'s
    # own `requires` rejects it before the body runs. The violation's
    # free-form reason text is exactly the kind of prose the happy-path
    # cases above cannot exercise.
    source = _reservation_source()
    response, stderr = _run_evaluate(source, "step", ["(Reservation 5)", "(Reserve)"])
    assert response.get("status") == "completed", response
    categories = {d.get("category") for d in (response.get("diagnostics") or [])}
    assert "precondition_violation" in categories, (
        f"expected a precondition_violation diagnostic for step((Reservation 5), (Reserve)): {response}"
    )
    _assert_no_forbidden_claim(response, stderr, "step((Reservation 5), (Reserve)) [precondition]")


def test_b2_postcondition_violation_describes_itself_only_as_evaluation_output():
    """Given the reported output of a run whose postcondition is violated,
    when the Owner reads it, then it describes itself only as evaluation
    output and contains no claim of verified, proved or built."""
    # A deliberately mutated copy of `step` whose body no longer satisfies
    # its own `ensures`. Only the free-form diagnostic reason differs from
    # the protected source's happy path.
    mutated_source = _postcondition_violating_source()
    response, stderr = _run_evaluate(mutated_source, "step", ["(Reservation 0)", "(Reserve)"])
    assert response.get("status") == "completed", response
    categories = {d.get("category") for d in (response.get("diagnostics") or [])}
    assert "postcondition_violation" in categories, (
        f"expected a postcondition_violation diagnostic for the mutated step((Reservation 0), (Reserve)): {response}"
    )
    _assert_no_forbidden_claim(response, stderr, "mutated step((Reservation 0), (Reserve)) [postcondition]")
