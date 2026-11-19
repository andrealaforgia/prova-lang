"""The two laws of F24, each over a family of names rather than one.

LAW1: whatever name a request chooses, a build either publishes exactly
one file directly inside the directory the Owner authorised, under that
very name, or it refuses: nothing is ever created outside that
directory.
LAW2: whatever a build refuses for, an artefact already standing under
the chosen name is byte for byte what it was, and no working file is
left behind.

Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import os
import pathlib
import sys

from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "acceptance"))

from _f24_fixtures import (  # noqa: E402
    REFUSED,
    build_into,
    entries_under,
    hour_clock,
    working_files_under,
)

# Names a client might send: plain ones, ones carrying a separator or a
# climb, and ones carrying characters no file name can carry.
NAMES = st.one_of(
    st.sampled_from(
        [
            "clock.py",
            "a",
            "../escape.py",
            "../../escape.py",
            "sub/clock.py",
            "/etc/clock.py",
            ".",
            "..",
            "",
            "./clock.py",
            "clock.py/",
            "clo\x00ck.py",
            "x" * 300,
        ]
    ),
    st.text(
        alphabet=st.characters(
            whitelist_categories=("Ll", "Lu", "Nd", "Po", "Pd"),
        ),
        max_size=12,
    ),
)


def _a_fresh_directory(root: pathlib.Path, counter: list) -> pathlib.Path:
    counter.append(1)
    made = root / f"authorised-{len(counter)}"
    made.mkdir()
    return made


@settings(
    max_examples=12,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(name=NAMES)
def test_a_build_writes_inside_the_authorised_directory_or_not_at_all(
    tmp_path, name
):
    """LAW1 -- generator for every name a client can send.

    observation: after the answer, every file that exists stands
    directly inside the authorised directory under the exact name the
    request sent, and the directory beside it is untouched.
    mutant: a build that resolves the name against the directory and
    follows a climb out of it publishes into the directory beside it and
    is caught here.
    """
    outside = tmp_path / "outside"
    outside.mkdir(exist_ok=True)
    (outside / "target.py").write_text("ORIGINAL\n", encoding="utf-8")
    authorised = tmp_path / "authorised"
    authorised.mkdir(exist_ok=True)
    for stale in authorised.iterdir():
        stale.unlink()

    answer = build_into(authorised, name, replace=True)

    standing = entries_under(authorised)
    plain = (
        name
        and "/" not in name
        and "\x00" not in name
        and name not in (".", "..")
        and len(name.encode("utf-8")) < 200
    )
    if plain:
        assert answer.get("status") == "completed", (
            f"WHAT: the plain name {name!r} inside the authorised directory "
            f"was answered {answer.get('status')!r}. "
            "WHY: a plain name inside the directory the Owner authorised is "
            "exactly what the authority allows; refusing it would leave no "
            "name to build under. "
            f"HOW: inspect the answer: {answer}"
        )
    if answer.get("status") == "completed":
        assert standing == [name], (
            f"WHAT: a completed build under the name {name!r} left "
            f"{standing} inside the authorised directory. "
            "WHY: a build publishes exactly the one name it was asked for, "
            "directly inside the directory the Owner authorised. "
            f"HOW: inspect the answer: {answer}"
        )
        published = (answer.get("result") or {}).get("artefact") or {}
        assert os.path.realpath(published.get("path", "")) == os.path.realpath(
            authorised / name
        ), (
            f"WHAT: the answer records the path {published.get('path')!r} for "
            f"the name {name!r}. "
            "WHY: the Owner goes to the path the answer records to find what "
            "they now hold. "
            f"HOW: inspect the answer: {answer}"
        )
    else:
        assert standing == [], (
            f"WHAT: a refused build under the name {name!r} left {standing} "
            "behind. "
            "WHY: a refusal writes nothing at all. "
            f"HOW: inspect the answer: {answer}"
        )
    assert entries_under(outside) == ["target.py"], (
        f"WHAT: the name {name!r} reached the directory beside the "
        f"authorised one: it holds {entries_under(outside)}. "
        "WHY: a build writes only inside the directory the Owner authorised. "
        f"HOW: inspect the answer: {answer}"
    )
    assert (outside / "target.py").read_bytes() == b"ORIGINAL\n", (
        f"WHAT: the name {name!r} changed a file outside the authorised "
        "directory. "
        "WHY: nothing outside the authority is ever written. "
        f"HOW: inspect the answer: {answer}"
    )


@settings(
    max_examples=8,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
@given(
    name=st.sampled_from(["../escape.py", "sub/clock.py", "", ".", "clo\x00ck.py"]),
    authorised_to_replace=st.booleans(),
)
def test_a_refused_build_leaves_the_artefact_and_no_working_file(
    tmp_path, name, authorised_to_replace
):
    """LAW2 -- generator for every name a refusal can be about.

    observation: the artefact that stood under the chosen name before
    the refused build hashes to the same bytes afterwards, and the
    authorised directory holds nothing else.
    mutant: a build that creates its working file or truncates the
    destination before it has decided the destination is allowed is
    caught here.
    """
    authorised = tmp_path / "authorised"
    authorised.mkdir(exist_ok=True)
    for stale in authorised.iterdir():
        stale.unlink()
    standing = authorised / "clock.py"
    standing.write_bytes(b"ORIGINAL ARTEFACT\n")

    answer = build_into(
        authorised, name, replace=True if authorised_to_replace else None
    )

    assert answer.get("status") == REFUSED, (
        f"WHAT: the name {name!r} was answered {answer.get('status')!r}. "
        "WHY: none of these names is a plain name inside the authorised "
        "directory. "
        f"HOW: inspect the answer: {answer}"
    )
    assert "output_name" in " ".join(
        d.get("reason", "") for d in answer.get("diagnostics") or []
    ), (
        f"WHAT: the refusal of the name {name!r} names no field the Owner "
        f"can repair: {answer.get('diagnostics')}. "
        "WHY: the name is a field of the request, and a refusal about it "
        "names that field. "
        f"HOW: inspect the answer: {answer}"
    )
    assert standing.read_bytes() == b"ORIGINAL ARTEFACT\n", (
        f"WHAT: the file the Owner held changed when the name {name!r} was "
        "refused. "
        "WHY: a refused build changes nothing of what the Owner has. "
        f"HOW: inspect the answer: {answer}"
    )
    assert working_files_under(authorised) == [], (
        f"WHAT: refusing {name!r} left "
        f"{working_files_under(authorised)} behind. "
        "WHY: a refusal creates no working file. "
        f"HOW: inspect the answer: {answer}"
    )
    assert hour_clock(), "the program under test is read from the repository"
