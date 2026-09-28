"""I1.S1.P6 (and I1.S1.B4): a refused build preserves every pre-existing
output, and creates nothing, even temporarily.

Given an output directory generated to hold 1-8 pre-existing regular files
(nesting depth 0-3, byte lengths 0-4096, names that include spaces and
non-ASCII characters, an empty file, a file holding every byte value, an
existing executable and files sitting at conventional executable target
names), when a build against the protected reservation source is refused,
then

* the response is the structured `unavailable` refusal,
* every pre-existing file still has its bytes, permission bits, size, device
  and inode (identity) and modification time, and the set of paths (files
  and directories) is exactly the original set, and
* the execution trace of the whole request records no filesystem-mutating
  event at all under the output directory: no create, truncate, write,
  rename, delete, chmod or write-then-restore, however brief.

The trace is an audit-event trace of the candidate's own process, so a file
created and deleted within microseconds is still recorded; a final snapshot
or polling could not promise that. The detection is validated by control
scripts that do exactly those things (transient create-delete, write-then-
restore of identical bytes, truncation, replacement by rename, deletion and
recreation) against a real directory, plus a read-only control that must not
be flagged.

The interface declares no output target name (the discover manifest lists
none), so conventional names are covered as explicit boundary examples
rather than assumed. Evidence limit: native code that changes files without
an audit event is not observed.

Derandomized with a fixed seed and a bounded example count.
"""

from __future__ import annotations

import os
import pathlib
import tempfile
import textwrap
import unicodedata

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from _prova_client import load_reservation_source
from _trace_client import mutations_under, run_traced

TARGET_NAMES = ["program", "a.out", "reservation", "reservation.out", "out"]

_ALPHABET = list("abcXYZ019_-") + [" ", "é", "ß", "ü", "日", "本", "ж"]
_name = st.text(alphabet=_ALPHABET, min_size=1, max_size=8).filter(
    lambda text: text == text.strip() and not text.startswith(".")
)

_file_fixture = st.tuples(
    st.lists(_name, min_size=0, max_size=3),  # nested directories
    _name,  # filename
    st.binary(min_size=0, max_size=4096),
    st.booleans(),  # mark executable
)


def _key(fixture) -> tuple[str, ...]:
    # Case- and normalisation-insensitive, so names that would collide on a
    # case-insensitive or normalising filesystem are treated as one.
    directories, filename, _, _ = fixture
    return tuple(unicodedata.normalize("NFC", part).casefold() for part in (*directories, filename))


def _no_path_collides_with_another(files) -> bool:
    paths = [_key(f) for f in files]
    return not any(
        i != j and q[: len(p)] == p
        for i, p in enumerate(paths)
        for j, q in enumerate(paths)
    )


_files = st.lists(_file_fixture, min_size=1, max_size=8, unique_by=_key).filter(
    _no_path_collides_with_another
)


def _write_fixture(root: pathlib.Path, files) -> None:
    for directories, filename, content, executable in files:
        directory = root.joinpath(*directories)
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / filename
        path.write_bytes(content)
        if executable:
            path.chmod(path.stat().st_mode | 0o111)


def _identity_snapshot(root: pathlib.Path) -> dict[str, tuple]:
    """Every path (files and directories) with type, bytes, mode, size,
    device, inode and mtime."""
    snapshot: dict[str, tuple] = {}
    for path in sorted(root.rglob("*")):
        info = path.lstat()
        content = path.read_bytes() if path.is_file() else None
        snapshot[str(path.relative_to(root))] = (
            path.is_dir(), content, info.st_mode, info.st_size, info.st_dev, info.st_ino, info.st_mtime_ns,
        )
    return snapshot


def _refused_build(root: pathlib.Path):
    return run_traced(
        {
            "prova": "i1",
            "operation": "build",
            "source": load_reservation_source(),
            "output_directory": str(root),
        }
    )


@settings(derandomize=True, max_examples=25, deadline=None)
@given(files=_files)
@example(files=[([], "empty.txt", b"", False)])
@example(files=[([], "binary.bin", bytes(range(256)), False)])
@example(files=[([], "existing", b"#!/bin/sh\necho hi\n", True)])
@example(files=[([], "with space é日.txt", b"unicode name", False)])
@example(files=[(["nested dir", "ü"], "deep", b"\x00" * 4096, True)])
@example(files=[([], target, b"placeholder", executable) for target, executable in zip(TARGET_NAMES, [True, False, True, False, True])])
def test_p6_refused_build_preserves_pre_existing_outputs(files):
    # A fresh directory per Hypothesis example (the tmp_path fixture is
    # function-scoped and would leak files between examples).
    with tempfile.TemporaryDirectory() as tmp_dir:
        root = pathlib.Path(tmp_dir)
        _write_fixture(root, files)
        before = _identity_snapshot(root)

        run = _refused_build(root)

        assert run.response is not None, f"non-JSON response refusing build: {run.stdout!r}"
        assert run.response.get("operation") == "build", run.response
        assert run.response.get("status") == "unavailable", run.response
        assert ("prova.service", "handle") in run.calls, "the trace did not observe the request being handled"

        mutations = mutations_under(run, root)
        assert not mutations, f"the refused build mutated the output location: {mutations}"

        after = _identity_snapshot(root)
        assert after == before, (
            "the output location differs after a refused build (path set, bytes, "
            f"permission bits, inode or mtime): before={before} after={after}"
        )


CONTROLS = {
    "transient create then delete": """
        import os
        def main():
            with open(os.path.join(ROOT, "program"), "wb") as h:
                h.write(b"x")
            os.remove(os.path.join(ROOT, "program"))
    """,
    "write-then-restore of identical bytes": """
        import os
        def main():
            path = os.path.join(ROOT, "keep.txt")
            data = open(path, "rb").read()
            with open(path, "wb") as h:
                h.write(b"clobbered")
            with open(path, "wb") as h:
                h.write(data)
    """,
    "truncation": """
        import os
        def main():
            os.truncate(os.path.join(ROOT, "keep.txt"), 0)
    """,
    "replacement by rename": """
        import os
        def main():
            os.rename(os.path.join(ROOT, "other.txt"), os.path.join(ROOT, "keep.txt"))
    """,
    "delete then recreate with the same bytes": """
        import os
        def main():
            path = os.path.join(ROOT, "keep.txt")
            data = open(path, "rb").read()
            os.remove(path)
            with open(path, "wb") as h:
                h.write(data)
    """,
    "permission change": """
        import os
        def main():
            os.chmod(os.path.join(ROOT, "keep.txt"), 0o755)
    """,
    "new directory": """
        import os
        def main():
            os.mkdir(os.path.join(ROOT, "made"))
    """,
}


def _run_control(tmp_path: pathlib.Path, body: str):
    root = tmp_path / "out"
    root.mkdir()
    (root / "keep.txt").write_bytes(b"pre-existing")
    (root / "other.txt").write_bytes(b"other")
    script = tmp_path / "control.py"
    script.write_text(f"ROOT = {str(root)!r}\n" + textwrap.dedent(body) + "\nmain()\n", encoding="utf-8")
    return root, run_traced({"operation": "build"}, entry=str(script))


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_p6_controlled_transient_mutation_is_detected(tmp_path, name):
    root, run = _run_control(tmp_path, CONTROLS[name])
    assert mutations_under(run, root), f"the trace missed the {name!r} control: {run.events}"


def test_p6_read_only_control_is_not_flagged(tmp_path):
    root, run = _run_control(
        tmp_path,
        """
        import os
        def main():
            os.listdir(ROOT)
            open(os.path.join(ROOT, "keep.txt"), "rb").read()
        """,
    )
    assert run.returncode == 0
    assert mutations_under(run, root) == []


def test_p6_snapshot_detects_identity_change_with_identical_bytes(tmp_path):
    root = tmp_path / "out"
    root.mkdir()
    path = root / "keep.txt"
    path.write_bytes(b"same")
    before = _identity_snapshot(root)
    replacement = root / "swap"
    replacement.write_bytes(b"same")
    os.replace(replacement, path)
    swapped = {k: v for k, v in _identity_snapshot(root).items() if k == "keep.txt"}
    assert swapped["keep.txt"][1] == before["keep.txt"][1]
    assert swapped["keep.txt"] != before["keep.txt"]
