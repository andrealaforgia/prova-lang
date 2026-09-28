"""Shared request/response plumbing for I1.S6's add-one acceptance tests
(B1-B4, INT). Each test still drives its own fresh `prova` subprocess and
computes its own expected value independently; only the request shape and
JSON handling are shared, the same way tests/properties/_i1_s3_fixtures.py
shares plumbing for that story's property tests.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ADD_ONE_PATH = REPO_ROOT / "conformance" / "add-one.prova"


def evaluate_add_one(n: int) -> dict:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": ADD_ONE_PATH.read_text(encoding="utf-8"),
        "function": "add-one",
        "arguments": [str(n)],
    }
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure evaluating add-one({n}): stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response evaluating add-one({n}): {proc.stdout!r}")
