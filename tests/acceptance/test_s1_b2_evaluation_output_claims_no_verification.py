"""Acceptance test for I1.S1.B2: the reported output of a direct
evaluation run describes itself only as evaluation output, never as
verified, proved or built.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

SIX_PAIRS = [
    (0, "Reserve"), (1, "Reserve"), (2, "Reserve"),
    (0, "Release"), (1, "Release"), (2, "Release"),
]

FORBIDDEN_CLAIM = re.compile(
    r"\b(verifie[sd]|verify|verification|prove[nd]?|proves|built|build|holds)\b",
    re.IGNORECASE,
)


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


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


def test_b2_every_evaluation_run_describes_itself_only_as_evaluation_output():
    """Given the reported output of any of these runs, when the Owner reads
    it, then it describes itself only as evaluation output and contains no
    claim of verified, proved or built."""
    source = _reservation_source()

    for before, event in SIX_PAIRS:
        request = {
            "prova": "i1",
            "operation": "evaluate",
            "source": source,
            "function": "step",
            "arguments": [f"(Reservation {before})", f"({event})"],
        }
        proc = subprocess.run(
            ["prova"],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=10.0,
        )
        assert proc.returncode == 0, f"tool failure evaluating step({before}, {event}): stderr={proc.stderr!r}"
        try:
            response = json.loads(proc.stdout)
        except (json.JSONDecodeError, ValueError):
            raise AssertionError(f"non-JSON response evaluating step({before}, {event}): {proc.stdout!r}")

        assert response.get("status") == "completed", (
            f"step({before}, {event}) was not evaluated: {response}"
        )
        assert response.get("claim", {}).get("kind") == "evaluation", (
            f"response does not describe itself as evaluation output for "
            f"step({before}, {event}): {response}"
        )

        body_hits = _find_forbidden(response)
        stderr_hits = FORBIDDEN_CLAIM.findall(proc.stderr)
        assert not body_hits, (
            f"forbidden claim wording in response body for step({before}, {event}): "
            f"{body_hits}; response={response}"
        )
        assert not stderr_hits, (
            f"forbidden claim wording on stderr for step({before}, {event}): {stderr_hits}"
        )
