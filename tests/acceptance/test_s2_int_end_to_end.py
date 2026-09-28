"""I1.S2.INT integration: story I1.S2 works end to end through the
product's real surface -- run every function's declared examples and see
them pass.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _run_examples() -> dict:
    request = {"prova": "i1", "operation": "examples", "source": _reservation_source()}
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


def test_int_running_every_declared_example_shows_all_seven_pass():
    response = _run_examples()

    assert response.get("operation") == "examples", response
    assert response.get("status") == "completed", response
    results = (response.get("result") or {}).get("examples") or []
    assert len(results) == 7, f"expected seven declared examples, got {len(results)}: {results}"
    assert all(entry.get("passed") is True for entry in results), (
        f"the Owner did not see every declared example pass end to end: {results}"
    )
