"""I1.S1.P4 (paired with P6) and I1.S1.B4: a refused build preserves every
pre-existing output byte for byte, even temporarily.

Given an output location generated to already hold 1-8 pre-existing regular
files (nesting depth 0-3, byte lengths 0-4096, including an empty file, a
binary file, an existing executable and a file occupying the build's
intended target path), when a build against the protected reservation
source is refused, then no executable is created and every pre-existing
file's bytes and permission bits are unchanged afterwards.

The "even temporarily" clause needs more than a before/after snapshot: an
implementation that writes the executable and deletes it before returning
would pass a final-only diff while still having created it. This test
launches the candidate as a subprocess and polls the output directory in a
tight loop (no sleep between iterations) for as long as the subprocess runs,
comparing every poll against the pre-existing baseline, so a transient file
that exists for at least one poll iteration is caught. This is still a
black-box proxy, not in-process instrumentation of a build dispatch path (none
exists yet): a create-delete cycle faster than a single poll iteration could
still be missed. It is strictly stronger than comparing only the state before
and after the subprocess exits.

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import time

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _prova_client import load_reservation_source, snapshot_tree

# The build target this fixture treats as "the intended target path": the
# executable name a successful build would conventionally write.
BUILD_TARGET_NAME = "program"

_path_component = st.from_regex(r"[a-zA-Z0-9_]{1,8}", fullmatch=True)

_file_fixture = st.tuples(
    st.lists(_path_component, min_size=0, max_size=3),  # nested directories
    _path_component,  # filename
    st.binary(min_size=0, max_size=4096),
    st.booleans(),  # mark executable
)

def _full_path(fixture) -> tuple[str, ...]:
    directories, filename, _, _ = fixture
    return tuple(directories) + (filename,)


def _no_path_collides_with_another(files) -> bool:
    # Reject fixtures where one entry's full path is a directory-chain
    # prefix of another's (e.g. a top-level file "p" and another entry
    # nested under directory "p"); such a set can't be written to disk.
    paths = [_full_path(f) for f in files]
    return not any(
        i != j and q[: len(p)] == p
        for i, p in enumerate(paths)
        for j, q in enumerate(paths)
    )


_files = st.lists(
    _file_fixture,
    min_size=1,
    max_size=8,
    unique_by=lambda f: (tuple(f[0]), f[1]),
).filter(_no_path_collides_with_another)


def _poll_snapshot(root: pathlib.Path):
    try:
        return snapshot_tree(root)
    except FileNotFoundError:
        # A path was listed by rglob but vanished before we could read it:
        # itself proof that something was written and removed within this
        # poll interval. Return a value that can never equal a real
        # snapshot, so the caller registers it as a deviation.
        return "<transient file observed mid-poll>"


def _run_build_polling_for_deviations(source: str, output_directory: pathlib.Path, poll_budget: float = 10.0):
    """Launch `prova build` and poll `output_directory` continuously while it
    runs, so a file created and removed before the process exits is still
    observed. Returns (returncode, response, stdout, stderr, baseline,
    first_deviation), where first_deviation is the first polled snapshot that
    differed from the pre-execution baseline, or None if none did.
    """
    request = {
        "prova": "i1",
        "operation": "build",
        "source": source,
        "output_directory": str(output_directory),
    }
    baseline = snapshot_tree(output_directory)

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
        if time.monotonic() - started > poll_budget:
            proc.kill()
            proc.wait()
            raise TimeoutError(f"prova build did not exit within {poll_budget}s")
        current = _poll_snapshot(output_directory)
        if current != baseline and first_deviation is None:
            first_deviation = current

    # stdin was already closed above; proc.communicate() would try to close
    # it again and raise, so read the pipes directly instead.
    stdout = proc.stdout.read()
    stderr = proc.stderr.read()
    proc.wait()

    final = _poll_snapshot(output_directory)
    if final != baseline and first_deviation is None:
        first_deviation = final

    try:
        response = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        response = None
    return proc.returncode, response, stdout, stderr, baseline, first_deviation


@settings(derandomize=True, max_examples=15, deadline=None)
@given(files=_files)
@example(files=[([], "empty.txt", b"", False)])
@example(files=[([], "binary.bin", bytes(range(256)), False)])
@example(files=[([], "existing", b"#!/bin/sh\necho hi\n", True)])
@example(files=[([], BUILD_TARGET_NAME, b"placeholder", False)])
def test_p6_refused_build_preserves_pre_existing_outputs(files):
    # A fresh directory per Hypothesis example, not the tmp_path fixture: that
    # fixture is function-scoped and would leak files between examples.
    source = load_reservation_source()

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = pathlib.Path(tmp_dir)
        written: dict[str, tuple[bytes, int]] = {}

        for directories, filename, content, executable in files:
            directory = tmp_path
            for part in directories:
                directory = directory / part
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / filename
            path.write_bytes(content)
            if executable:
                path.chmod(path.stat().st_mode | 0o111)
            written[str(path.relative_to(tmp_path))] = (content, path.stat().st_mode)

        (
            returncode,
            response,
            stdout,
            stderr,
            baseline,
            deviation,
        ) = _run_build_polling_for_deviations(source, tmp_path)

        assert response is not None, f"non-JSON response refusing build: {stdout!r}"
        assert response.get("operation") == "build", response
        assert response.get("status") == "unavailable", response

        assert deviation is None, (
            "the output directory's contents changed at some point while the "
            "build was running, even though a snapshot taken only at the end "
            f"would have matched the pre-existing baseline: baseline={baseline} "
            f"first observed deviation={deviation}"
        )

        for relpath, (content, mode) in written.items():
            path = tmp_path / relpath
            assert path.exists(), f"pre-existing file {relpath!r} was removed by a refused build"
            assert path.read_bytes() == content, f"pre-existing file {relpath!r} bytes changed"
            assert path.stat().st_mode == mode, f"pre-existing file {relpath!r} permission bits changed"

        target = tmp_path / BUILD_TARGET_NAME
        if BUILD_TARGET_NAME not in written:
            assert not target.exists(), "a refused build created an executable at the intended output path"
