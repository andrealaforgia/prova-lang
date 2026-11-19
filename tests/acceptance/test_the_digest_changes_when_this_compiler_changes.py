"""The digest an answer stands on changes when this compiler changes.

A client keeps an answer and compares what it stood on with what the
tool publishes now, and asks again when the two differ. The digest was
taken over the profile, the language and the four version strings this
tool is built of, none of which a change to the code moves: two trees
whose operations differed -- one publishing `build` as unavailable, the
other answering it -- published the same digest, so the comparison the
tool advertises could not see this compiler change at all.

The digest now covers the source of every module of the package, hashed
in a stable order and read once when the tool starts. The cases below
copy the package, change one byte of one module in the copy, and ask
each copy for its digest in a subprocess of its own: a copy that is
byte for byte the same stands on the same digest, and a copy with one
byte changed does not.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys

import pytest

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
THE_PACKAGE = REPO_ROOT / "src" / "prova"

# The one question each subprocess is asked, out of a tree it is given
# rather than out of the one installed: what the tool at that path says
# a completed answer stands on.
THE_QUESTION = (
    "import json, sys;"
    "sys.path.insert(0, sys.argv[1]);"
    "from prova import service;"
    "print(json.dumps("
    "service.handle({'operation': 'discover'})['stands_on']"
    "['dependency_digest']))"
)

# The modules changed by one byte, chosen so that the sample is not one
# file: what a build writes, what the checker refuses, what an answer
# stands on, and the reader behind all of them.
THE_MODULES = ("building.py", "checker.py", "provenance.py", "reader.py")


def _a_copy_at(root: pathlib.Path) -> pathlib.Path:
    """The package copied under `root`, with nothing changed."""
    tree = root / "tree"
    tree.mkdir(parents=True)
    shutil.copytree(THE_PACKAGE, tree / "prova")
    return tree


def _digest_of(tree: pathlib.Path) -> str:
    ran = subprocess.run(
        [sys.executable, "-c", THE_QUESTION, str(tree)],
        capture_output=True,
        text=True,
        timeout=120.0,
    )
    assert ran.returncode == 0, (
        f"the tool at {tree} answered nothing: exit {ran.returncode}, "
        f"{ran.stderr[-600:]!r}"
    )
    return json.loads(ran.stdout)


def _one_byte_changed(tree: pathlib.Path, module: str) -> None:
    """Change one byte of one module of the copy, inside its own
    documentation, so the file still reads as the module it was."""
    path = tree / "prova" / module
    written = path.read_bytes()
    first_full_stop = written.index(b".")
    path.write_bytes(
        written[:first_full_stop] + b"!" + written[first_full_stop + 1 :]
    )
    assert len(path.read_bytes()) == len(written)


def test_a_copy_of_this_package_stands_on_the_same_digest(tmp_path):
    """The positive control: the digest is over what the modules hold,
    not over where they stand, so copying the package moves nothing."""
    unchanged = _a_copy_at(tmp_path)

    assert _digest_of(unchanged) == _digest_of(THE_PACKAGE.parent), (
        "a copy of this package, byte for byte the same, publishes another "
        "digest: a client comparing a kept answer would be told the tool "
        "changed because it was installed somewhere else."
    )


@pytest.mark.parametrize("module", THE_MODULES)
def test_one_byte_of_one_module_moves_the_digest(tmp_path, module):
    unchanged = _a_copy_at(tmp_path / "before")
    changed = _a_copy_at(tmp_path / "after")
    _one_byte_changed(changed, module)

    assert _digest_of(changed) != _digest_of(unchanged), (
        f"a tool whose {module} differs by one byte publishes the digest of "
        "the tool it was: the comparison this tool advertises cannot see a "
        "change to its own compiler."
    )


def test_the_digest_is_the_same_for_one_tree_asked_twice(tmp_path):
    """It is a digest of the tool and not of the moment: two runs of one
    tree answer the same, so a client comparing a kept answer reads a
    change of the tool and never a change of the clock."""
    tree = _a_copy_at(tmp_path)

    assert _digest_of(tree) == _digest_of(tree)
