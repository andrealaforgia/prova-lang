"""Acceptance test for I1.S1.B3: `build` and `verify` are recognized I1
operations that are deliberately refused as unavailable, never attempted --
as distinct from a request naming an operation the tool does not recognize
at all.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

OPERATIONS = ["build", "verify"]

UNRECOGNIZED_OPERATION = "totally_bogus_xyz"


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _request(operation: str, source: str) -> dict:
    request = {"prova": "i1", "operation": operation, "source": source}
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure requesting {operation}: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response requesting {operation}: {proc.stdout!r}")


def test_b3_build_and_verify_are_refused_as_explicit_unavailable_failures():
    """Given the Owner requests the build operation or the verify
    operation against the reservation source, when either request runs,
    then the tool returns an explicit structured failure reporting the
    operation as unavailable rather than attempting it."""
    source = _reservation_source()

    for operation in OPERATIONS:
        response = _request(operation, source)

        assert response.get("operation") == operation, response
        assert response.get("status") == "unavailable", (
            f"{operation} was not refused as unavailable: {response}"
        )
        assert not response.get("result"), f"{operation} refusal carried a result: {response}"

        diagnostics = response.get("diagnostics") or []
        categories = {d.get("category") for d in diagnostics}
        assert categories, f"{operation} refusal carried no diagnostic naming why: {response}"
        assert "tool_failure" not in categories, (
            f"{operation} refusal reported a tool_failure diagnostic, suggesting a "
            f"crashed attempt rather than a clean refusal: {response}"
        )
        assert "unknown_operation" not in categories, (
            f"{operation} was refused with the same category the tool uses for an "
            f"operation it does not recognize at all, so the refusal is not shown "
            f"to be a deliberate, operation-specific decision: {response}"
        )


def test_b3_build_and_verify_refusal_is_distinct_from_an_unrecognized_operation():
    """Given the Owner requests an operation name the tool has never heard
    of, when compared against the build and verify refusals, then the
    unrecognized-operation failure is reported under a different diagnostic
    category -- proving build and verify are known, declared-unavailable
    operations rather than falling through the same generic catch-all that
    handles garbage input."""
    source = _reservation_source()

    bogus_response = _request(UNRECOGNIZED_OPERATION, source)
    assert bogus_response.get("status") == "unavailable", bogus_response
    bogus_categories = {d.get("category") for d in bogus_response.get("diagnostics") or []}
    assert bogus_categories, f"unrecognized operation carried no diagnostic: {bogus_response}"

    for operation in OPERATIONS:
        response = _request(operation, source)
        categories = {d.get("category") for d in response.get("diagnostics") or []}
        assert categories.isdisjoint(bogus_categories), (
            f"{operation} was refused under the same diagnostic category "
            f"({categories & bogus_categories!r}) as a completely unrecognized "
            f"operation name, so nothing in the response distinguishes a "
            f"deliberate refusal of a known operation from a generic fallback: "
            f"{operation}={response!r} bogus={bogus_response!r}"
        )
