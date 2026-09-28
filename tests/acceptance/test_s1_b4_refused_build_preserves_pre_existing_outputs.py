"""Acceptance test for I1.S1.B4: a refused build leaves an output location
that already held files from before byte-for-byte untouched, and creates
no executable -- even temporarily, for the lifetime of the request.

A before/after snapshot alone cannot tell a build that never touches the
filesystem apart from one that writes an output and deletes it again
before returning. This test launches `prova` as a subprocess and polls the
output directory continuously while it runs, so a transient write would be
caught even though none exists in this behaviour's code today; this is the
guard that must start failing the moment any future build implementation
writes before checking refusal.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import time

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

BUILD_TARGET_NAME = "program"
POLL_BUDGET_SECONDS = 10.0


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _snapshot(root: pathlib.Path) -> dict[str, tuple[bytes, int]]:
    try:
        return {
            str(path.relative_to(root)): (path.read_bytes(), path.stat().st_mode)
            for path in sorted(root.rglob("*"))
            if path.is_file()
        }
    except FileNotFoundError:
        # A path listed by rglob vanished before it could be read: itself
        # proof that something was written and removed mid-poll.
        return {"<transient state observed mid-poll>": (b"", 0)}


def test_b4_refused_build_leaves_pre_existing_outputs_byte_for_byte_untouched():
    """Given an output location that already holds files from before, when
    the Owner requests the build operation against the reservation source
    and it is refused, then no executable is created and every
    pre-existing output is left byte-for-byte untouched."""
    source = _reservation_source()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)
        pre_existing = {
            "notes.txt": b"kept from an earlier session\n",
            "artifacts/old-binary": b"\x7fELF\x00fake-previous-executable",
            # Occupies the exact path a successful build would write to.
            BUILD_TARGET_NAME: b"placeholder from a previous build",
        }
        for relpath, content in pre_existing.items():
            path = tmp_path / relpath
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(content)

        baseline = _snapshot(tmp_path)

        request = {
            "prova": "i1",
            "operation": "build",
            "source": source,
            "output_directory": str(tmp_path),
        }
        proc = subprocess.Popen(
            ["prova"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        proc.stdin.write(json.dumps(request))
        proc.stdin.close()

        first_deviation = None
        started = time.monotonic()
        while proc.poll() is None:
            if time.monotonic() - started > POLL_BUDGET_SECONDS:
                proc.kill()
                proc.wait()
                raise TimeoutError(f"prova build did not exit within {POLL_BUDGET_SECONDS}s")
            current = _snapshot(tmp_path)
            if current != baseline and first_deviation is None:
                first_deviation = current

        stdout = proc.stdout.read()
        stderr = proc.stderr.read()
        proc.wait()

        final = _snapshot(tmp_path)
        if final != baseline and first_deviation is None:
            first_deviation = final

        assert proc.returncode == 0, f"tool failure requesting build: stderr={stderr!r}"
        try:
            response = json.loads(stdout)
        except (json.JSONDecodeError, ValueError):
            raise AssertionError(f"non-JSON response requesting build: {stdout!r}")

        assert response.get("operation") == "build", response
        assert response.get("status") == "unavailable", f"build was not refused: {response}"

        build_categories = {d.get("category") for d in response.get("diagnostics") or []}
        bogus_request = {
            "prova": "i1",
            "operation": "totally_bogus_xyz",
            "source": source,
        }
        bogus_proc = subprocess.run(
            ["prova"],
            input=json.dumps(bogus_request),
            capture_output=True,
            text=True,
            timeout=10.0,
        )
        assert bogus_proc.returncode == 0, f"tool failure requesting bogus operation: stderr={bogus_proc.stderr!r}"
        bogus_response = json.loads(bogus_proc.stdout)
        bogus_categories = {d.get("category") for d in bogus_response.get("diagnostics") or []}
        assert build_categories.isdisjoint(bogus_categories), (
            f"build was refused under the same diagnostic category "
            f"({build_categories & bogus_categories!r}) as a completely "
            f"unrecognized operation name, so this is not shown to be a "
            f"deliberate refusal of a known build operation: "
            f"build={response!r} bogus={bogus_response!r}"
        )

        assert first_deviation is None, (
            "the output directory's contents changed at some point while the "
            "build was running, even though a snapshot taken only at the end "
            f"would have matched the pre-existing baseline: baseline={baseline} "
            f"first observed deviation={first_deviation}"
        )
