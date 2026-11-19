"""What an authorised replacement does, and what a build that fails
after it was authorised leaves behind.

The Owner authorises a replacement explicitly. When the build then goes
through, the answer says that it replaced and records the digest of what
it replaced. When it fails anywhere after that -- because the program
was not shown whole, because the answer could not be given, or because
the directory could not be written -- the artefact that was there is
byte for byte what it was, and no working file is left behind.

Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess

import pytest

from _f22_fixtures import run_artefact
from _f24_fixtures import (
    NOT_WRITABLE,
    REFUSED,
    a_program_whose_example_is_wrong,
    ask,
    build_into,
    categories_of,
    digest_of_bytes,
    entries_under,
    hour_clock,
    reasons_of,
    working_files_under,
)


def _an_artefact_standing_at(tmp_path: pathlib.Path, name: str = "clock.py"):
    """One published artefact under the authorised directory, and the
    bytes it holds."""
    authorised = tmp_path / "authorised"
    authorised.mkdir()
    first = build_into(authorised, name)
    assert first.get("status") == "completed", f"the first build: {first}"
    return authorised, (authorised / name).read_bytes()


def test_an_authorised_replacement_says_what_it_replaced(tmp_path):
    """Given an artefact of the hour clock's 'step' standing under the
    chosen name, when the Owner asks for a build of 'valid-state' there
    and authorises the replacement, then the answer completes, says it
    replaced, records the digest of the 64 characters the old artefact
    hashes to, and the file now answers as the new entry does.

    still passes if: the tool had written the new artefact beside the
    old one under another name -- the test reads the chosen name back
    and runs it.
    """
    authorised, before = _an_artefact_standing_at(tmp_path)
    target = authorised / "clock.py"

    answer = build_into(authorised, "clock.py", entry="valid-state", replace=True)

    assert answer.get("status") == "completed", (
        f"WHAT: an authorised replacement was answered "
        f"{answer.get('status')!r}. "
        "WHY: the Owner said the artefact may be replaced, which is the one "
        "thing that was in the way. "
        f"HOW: inspect the answer: {answer}"
    )
    published = (answer.get("result") or {}).get("artefact") or {}
    assert published.get("replaced") is True, (
        f"WHAT: the answer records 'replaced' as "
        f"{published.get('replaced')!r}. "
        "WHY: the Owner must read from the answer whether an artefact they "
        "held was replaced or whether this build wrote where nothing was. "
        f"HOW: inspect the answer: {answer}"
    )
    assert published.get("replaced_digest") == digest_of_bytes(before), (
        f"WHAT: the answer records the replaced artefact as "
        f"{published.get('replaced_digest')!r}, and the artefact that was "
        f"there hashes to {digest_of_bytes(before)!r}. "
        "WHY: the digest is what the Owner recovers the replaced artefact "
        "by, and a digest of something else names nothing. "
        f"HOW: inspect the answer: {answer}"
    )
    assert target.read_bytes() != before, (
        "WHAT: the file under the chosen name is the artefact that was there "
        "before. "
        "WHY: an authorised replacement replaces it. "
        f"HOW: inspect the answer: {answer}"
    )
    ran = run_artefact(target, ["(Clock 11)"])
    assert ran.returncode == 0 and "Traceback" not in ran.stderr, (
        f"WHAT: the replacing artefact exited {ran.returncode}: "
        f"{ran.stderr[-300:]!r}. "
        "WHY: a replacement is a whole artefact, not a half-written file. "
        "HOW: write the whole text before the name is given to it."
    )
    assert working_files_under(authorised) == [], (
        f"WHAT: the build left {working_files_under(authorised)} behind. "
        "WHY: the working file is removed whatever happens. "
        "HOW: remove it on every path out."
    )


def test_a_first_build_to_a_free_name_says_it_replaced_nothing(tmp_path):
    """Given nothing under the chosen name, when the Owner asks for a
    build and authorises a replacement anyway, then the answer completes
    and records that it replaced nothing.

    still passes if: the answer had left the field out altogether -- the
    assertion reads it as false, not as absent.
    """
    authorised = tmp_path / "authorised"
    authorised.mkdir()

    answer = build_into(authorised, "clock.py", replace=True)

    published = (answer.get("result") or {}).get("artefact") or {}
    assert answer.get("status") == "completed", f"the build: {answer}"
    assert published.get("replaced") is False, (
        f"WHAT: a build where nothing stood records 'replaced' as "
        f"{published.get('replaced')!r}. "
        "WHY: the Owner reads one field to learn whether anything of theirs "
        "was replaced; absent and false are not the same answer. "
        f"HOW: inspect the answer: {answer}"
    )
    assert "replaced_digest" not in published, (
        f"WHAT: the answer records a replaced digest of "
        f"{published.get('replaced_digest')!r} where nothing was replaced. "
        "WHY: a digest of nothing is a digest the Owner cannot look up. "
        f"HOW: inspect the answer: {answer}"
    )


def test_a_program_not_shown_whole_leaves_an_authorised_replacement_alone(tmp_path):
    """Given an artefact standing under the chosen name and a program
    whose one example claims 3 where the program answers 2, when the
    Owner authorises the replacement and asks for a build of it, then
    the answer refuses and the artefact is byte for byte what it was.

    still passes if: the tool had refused every replacement -- the first
    test of this file replaces an artefact and is answered.
    """
    authorised, before = _an_artefact_standing_at(tmp_path)

    answer = build_into(
        authorised,
        "clock.py",
        source=a_program_whose_example_is_wrong(),
        entry="plus-one",
        replace=True,
    )

    assert answer.get("status") == "not_verified", (
        f"WHAT: a build of a program that was not shown whole was answered "
        f"{answer.get('status')!r}. "
        "WHY: an artefact is published only for a program whose whole was "
        "shown, whatever the Owner authorised about the destination. "
        f"HOW: inspect the answer: {answer}"
    )
    assert (authorised / "clock.py").read_bytes() == before, (
        "WHAT: the artefact the Owner held was changed by a build that "
        "failed. "
        "WHY: an authorised replacement is an authority to replace it with a "
        "whole artefact, never an authority to lose it. "
        "HOW: publish only after everything else has gone through."
    )
    assert entries_under(authorised) == ["clock.py"], (
        f"WHAT: the directory holds {entries_under(authorised)}. "
        "WHY: a failed build leaves no working file beside the artefact. "
        "HOW: remove the working file on every path out."
    )


def test_an_answer_that_cannot_be_given_leaves_the_artefact_alone(tmp_path):
    """Given an artefact standing under the chosen name and the answer
    budget lowered to 1 character, when the Owner authorises the
    replacement and asks for a build, then the answer says the budget
    was passed and the artefact is byte for byte what it was.

    still passes if: the tool had refused the build before reading the
    destination at all -- what matters is the artefact, and the test
    reads its bytes back.
    """
    authorised, before = _an_artefact_standing_at(tmp_path)

    answer = build_into(
        authorised,
        "clock.py",
        replace=True,
        lowered={"PROVA_BUDGET_ANSWER_SIZE": "1"},
    )

    assert answer.get("status") == "resource_exhausted", (
        f"WHAT: a build whose answer passed the budget was answered "
        f"{answer.get('status')!r}. "
        "WHY: an answer the tool may not print is a budget of the run. "
        f"HOW: inspect the answer: {answer}"
    )
    assert (authorised / "clock.py").read_bytes() == before, (
        "WHAT: the artefact was replaced by a build whose answer was never "
        "given. "
        "WHY: an artefact nobody was told about is one the Owner never "
        "asked for; the one they had must survive. "
        "HOW: measure the answer before publishing anything."
    )
    assert entries_under(authorised) == ["clock.py"], (
        f"WHAT: the directory holds {entries_under(authorised)}. "
        "WHY: nothing is left behind by a build that gave no answer. "
        "HOW: remove the working file on every path out."
    )


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="a superuser writes into a directory that allows nobody to write",
)
def test_a_directory_that_cannot_be_written_is_refused_not_broken(tmp_path):
    """Given an artefact standing in a directory nobody may write into,
    when the Owner authorises the replacement and asks for a build, then
    the answer refuses naming the field to repair, the artefact is byte
    for byte what it was, and nothing ends in a traceback.

    still passes if: the tool had refused because the artefact was there
    -- the replacement is authorised here, so the only thing in the way
    is the directory itself.
    """
    authorised, before = _an_artefact_standing_at(tmp_path)
    os.chmod(authorised, 0o500)
    try:
        answer = build_into(authorised, "clock.py", entry="valid-state", replace=True)
        after = (authorised / "clock.py").read_bytes()
        left = entries_under(authorised)
    finally:
        os.chmod(authorised, 0o700)

    assert answer.get("status") == REFUSED, (
        f"WHAT: a build into a directory that may not be written was "
        f"answered {answer.get('status')!r}. "
        "WHY: the destination is a field of the request, and a destination "
        "this tool cannot write to is a fact about that field. "
        f"HOW: inspect the answer: {answer}"
    )
    assert NOT_WRITABLE in categories_of(answer), (
        f"WHAT: it was refused as {sorted(categories_of(answer))}. "
        "WHY: a client reads one word for a destination that could not be "
        "written, and this one is not about a file being in the way. "
        f"HOW: inspect the answer: {answer}"
    )
    assert "output_directory" in reasons_of(answer), (
        f"WHAT: the refusal names no field: {reasons_of(answer)!r}. "
        "WHY: the Owner repairs the directory the refusal names. "
        f"HOW: inspect the answer: {answer}"
    )
    assert after == before, (
        "WHAT: the artefact changed although nothing could be written. "
        "WHY: a build that cannot write replaces nothing. "
        "HOW: replace only after the whole text is written."
    )
    assert left == ["clock.py"], (
        f"WHAT: the directory holds {left}. "
        "WHY: a build that failed while writing leaves no working file. "
        "HOW: remove it on every path out."
    )


@pytest.mark.skipif(
    hasattr(os, "geteuid") and os.geteuid() == 0,
    reason="a superuser reads a file that allows nobody to read it",
)
def test_an_artefact_that_cannot_be_read_is_not_replaced(tmp_path):
    """Given a file of 18 bytes standing under the chosen name that
    allows nobody to read it, in a directory that may be written, when
    the Owner authorises the replacement and asks for a build, then the
    answer refuses, says that what stands there could not be read and
    that its digest cannot be recorded, and the file is byte for byte
    what it was.

    still passes if: the tool had refused every replacement -- the
    first test of this file replaces a readable artefact and is
    answered.
    """
    authorised = tmp_path / "authorised"
    authorised.mkdir()
    standing = authorised / "clock.py"
    standing.write_bytes(b"ORIGINAL ARTEFACT\n")
    os.chmod(standing, 0o000)
    try:
        answer = build_into(authorised, "clock.py", replace=True)
        left = entries_under(authorised)
        os.chmod(standing, 0o600)
        after = standing.read_bytes()
    finally:
        os.chmod(standing, 0o600)

    assert answer.get("status") == REFUSED, (
        f"WHAT: a replacement of a file this tool cannot read was answered "
        f"{answer.get('status')!r}. "
        "WHY: the answer of a replacement records the digest of what it "
        "replaced; what cannot be read has no digest to record, so there is "
        "nothing to answer with and the file must survive. "
        f"HOW: inspect the answer: {answer}"
    )
    assert not answer.get("result"), f"the refusal carried a result: {answer}"
    reasons = reasons_of(answer).lower()
    assert "read" in reasons and "digest" in reasons, (
        f"WHAT: the refusal does not say that what stands there could not "
        f"be read and that its digest cannot be recorded: "
        f"{reasons_of(answer)!r}. "
        "WHY: the Owner must know why the replacement they authorised did "
        "not happen. "
        f"HOW: say both in the reason."
    )
    assert after == b"ORIGINAL ARTEFACT\n", (
        f"WHAT: the file that could not be read now reads {after!r}. "
        "WHY: a build that cannot record what it would destroy destroys "
        "nothing. "
        "HOW: refuse before the name is given away."
    )
    assert left == ["clock.py"], (
        f"WHAT: the directory holds {left}. "
        "WHY: a refused build leaves no working file. "
        "HOW: remove it on every path out."
    )


def test_two_builds_asked_at_once_leave_exactly_one_whole_artefact(tmp_path):
    """Given two builds of the same program started at the same time,
    both authorised to replace, into one authorised directory under one
    name, when both have answered, then exactly one file stands under
    that name, it runs and answers '(Clock 0)' for '(Clock 11)', and no
    working file is left behind.

    The premise this proves from outside: both commands were running at
    the same moment, read by asking each of them whether it had ended
    while the other was still going. What it does not prove is that the
    two publishing steps themselves overlapped; that window is not
    observable from outside this tool.

    still passes if: the second build had been refused outright -- the
    test asserts that every answer is an answer and that the file left
    behind runs.
    """
    authorised = tmp_path / "authorised"
    authorised.mkdir()
    request = json.dumps(
        {
            "operation": "build",
            "source": hour_clock(),
            "entry": "step",
            "output_directory": str(authorised),
            "output_name": "clock.py",
            "replace": True,
        }
    )
    asked = tmp_path / "request.json"
    asked.write_text(request, encoding="utf-8")

    overlapped = False
    answers = []
    for _ in range(3):
        for stale in authorised.iterdir():
            stale.unlink()
        with open(asked, "r", encoding="utf-8") as first_input, open(
            asked, "r", encoding="utf-8"
        ) as second_input:
            first = subprocess.Popen(
                ["prova"], stdin=first_input, stdout=subprocess.PIPE, text=True
            )
            second = subprocess.Popen(
                ["prova"], stdin=second_input, stdout=subprocess.PIPE, text=True
            )
            overlapped = first.poll() is None and second.poll() is None
            answers = [first.communicate()[0], second.communicate()[0]]
        if overlapped:
            break

    assert overlapped, (
        "WHAT: the two builds never ran at the same time, so this test "
        "observed no race at all. "
        "WHY: a test that would pass whether or not the two builds "
        "overlapped proves nothing about two builds at once. "
        "HOW: start both before either has answered."
    )
    for printed in answers:
        answer = json.loads(printed)
        assert answer.get("status") in ("completed", REFUSED), (
            f"WHAT: one of two builds at once answered "
            f"{answer.get('status')!r}. "
            "WHY: each build is answered, with an artefact or with a reason. "
            f"HOW: inspect the answer: {answer}"
        )
    assert entries_under(authorised) == ["clock.py"], (
        f"WHAT: after two builds at once the directory holds "
        f"{entries_under(authorised)}. "
        "WHY: two builds under one name leave exactly one file, and no "
        "working file of either of them. "
        "HOW: give the name to a whole file in one step."
    )
    ran = run_artefact(authorised / "clock.py", ["(Clock 11)", "(Tick)"])
    assert ran.returncode == 0 and ran.stdout.strip() == "(Outcome (Clock 12) true)", (
        f"WHAT: the one file left by two builds at once exited "
        f"{ran.returncode} and printed {ran.stdout.strip()!r}. "
        "WHY: the file that survives a race is a whole artefact, never two "
        "halves of two builds. "
        f"HOW: read its error output: {ran.stderr[-300:]!r}"
    )
