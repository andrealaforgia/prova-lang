"""Acceptance test for I1.S1.B4: a refused build leaves an output location
that already held files from before byte-for-byte untouched, and creates
no executable.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

BUILD_TARGET_NAME = "program"


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def test_b4_refused_build_leaves_pre_existing_outputs_byte_for_byte_untouched(tmp_path):
    """Given an output location that already holds files from before, when
    the Owner requests the build operation against the reservation source
    and it is refused, then no executable is created and every
    pre-existing output is left byte-for-byte untouched."""
    pre_existing = {
        "notes.txt": b"kept from an earlier session\n",
        "artifacts/old-binary": b"\x7fELF\x00fake-previous-executable",
    }
    for relpath, content in pre_existing.items():
        path = tmp_path / relpath
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    baseline = {relpath: (tmp_path / relpath).stat().st_mode for relpath in pre_existing}

    source = _reservation_source()
    request = {
        "prova": "i1",
        "operation": "build",
        "source": source,
        "output_directory": str(tmp_path),
    }
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure requesting build: stderr={proc.stderr!r}"
    try:
        response = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response requesting build: {proc.stdout!r}")

    assert response.get("operation") == "build", response
    assert response.get("status") == "unavailable", f"build was not refused: {response}"

    for relpath, content in pre_existing.items():
        path = tmp_path / relpath
        assert path.exists(), f"pre-existing file {relpath!r} was removed by a refused build"
        assert path.read_bytes() == content, f"pre-existing file {relpath!r} bytes changed"
        assert path.stat().st_mode == baseline[relpath], f"pre-existing file {relpath!r} permission bits changed"

    target = tmp_path / BUILD_TARGET_NAME
    assert not target.exists(), "a refused build created an executable at the intended output path"
