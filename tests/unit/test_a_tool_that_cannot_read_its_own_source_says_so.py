"""A tool that cannot read one of its own modules says so where its
identity is published, instead of publishing a digest that identifies
nothing.

The digest an answer stands on covers the source of every module of the
package. Where one of them cannot be read -- an installation whose
files a caller may not open -- there is no identity to take, and a
digest taken over what could be read would name a tool nobody has. The
branch says what happened and names the module, so a client comparing a
kept answer reads that the comparison is not available rather than a
digest that silently means something else.

No request reaches this: it is decided when the tool starts, out of the
files it was installed from, so the case below installs a copy of the
package with one module unreadable and asks that copy in a subprocess
of its own.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
THE_PACKAGE = REPO_ROOT / "src" / "prova"

THE_QUESTION = (
    "import sys;"
    "sys.path.insert(0, sys.argv[1]);"
    "from prova import provenance;"
    "print(provenance.THIS_IMPLEMENTATION)"
)

THE_UNREADABLE_MODULE = "reader.py"


def _answered_by(tree: pathlib.Path) -> str:
    ran = subprocess.run(
        [sys.executable, "-c", THE_QUESTION, str(tree)],
        capture_output=True,
        text=True,
        timeout=120.0,
    )
    assert ran.returncode == 0, (ran.returncode, ran.stderr[-500:])
    return ran.stdout.strip()


@pytest.fixture
def a_copy(tmp_path) -> pathlib.Path:
    tree = tmp_path / "tree"
    tree.mkdir()
    shutil.copytree(THE_PACKAGE, tree / "prova")
    return tree


def test_the_identity_says_the_source_could_not_be_read(a_copy):
    if os.geteuid() == 0:
        pytest.skip("a superuser reads a file whatever its mode says")
    unreadable = a_copy / "prova" / THE_UNREADABLE_MODULE
    os.chmod(unreadable, 0)
    try:
        said = _answered_by(a_copy)
    finally:
        os.chmod(unreadable, 0o644)

    assert said.startswith("not readable:"), said
    assert THE_UNREADABLE_MODULE in said, said
    assert len(said) != 64, (
        "the tool published something the length of a digest for a package it "
        "could not read: " + said
    )


def test_the_same_copy_read_whole_publishes_a_digest(a_copy):
    said = _answered_by(a_copy)

    assert len(said) == 64 and all(c in "0123456789abcdef" for c in said), said
