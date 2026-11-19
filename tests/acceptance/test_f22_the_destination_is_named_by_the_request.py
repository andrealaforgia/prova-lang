"""Where a build writes, and when it refuses to write there.

This slice writes only to the file the request names, only if that
file's directory is there and the file is not. F24 widens those rules;
what never widens is that a refusal writes nothing.

Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

from _f22_fixtures import artefact_of, ask, build, files_under, hour_clock


def test_a_second_build_over_a_file_that_is_there_is_refused():
    """Given one artefact already written at a path, when the Owner asks
    for a build to the same path, then the answer refuses, names the
    file, and the artefact that was there is left byte for byte as it
    was.

    still passes if: the tool had refused the first build too -- the
    first build is required to publish an artefact.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        target = destination / "clock.py"
        artefact_of(build(hour_clock(), "step", target), "the first build")
        first = target.read_bytes()

        again = build(hour_clock(), "valid-state", target)
        after = files_under(destination)

    assert again.get("status") == "invalid_input", (
        f"WHAT: a build over a file that is already there was answered "
        f"{again.get('status')!r}. "
        "WHY: this slice writes only where nothing is; overwriting what the "
        "Owner has without being asked is the one thing a build must never "
        "do by accident. "
        f"HOW: inspect the answer: {again}"
    )
    assert not again.get("result"), f"the refusal carried a result: {again}"
    assert "clock.py" in " ".join(
        d.get("reason", "") for d in again.get("diagnostics") or []
    ), (
        f"WHAT: the refusal does not name the file that is in the way: "
        f"{again}. "
        "WHY: the Owner must know which file to move or which path to choose. "
        "HOW: name the path the request carried."
    )
    assert after == {"clock.py": first}, (
        f"WHAT: the destination holds {sorted(after)} and the artefact of the "
        "first build was changed. "
        "WHY: a refused build changes nothing, least of all the artefact the "
        "Owner already has. "
        "HOW: decide the refusal before anything is written."
    )


def test_a_request_without_a_destination_or_an_entry_is_refused_by_name():
    """Given a build request whose `output_file` is a number, and one
    with no `entry` at all, when each is sent, then each is refused
    naming the field to repair, and nothing is written anywhere.

    still passes if: the tool had refused every build request whatever
    its fields -- the tests above build the same program with both
    fields written properly.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        not_a_path = ask(
            {
                "operation": "build",
                "source": hour_clock(),
                "entry": "step",
                "output_file": 7,
            }
        )
        no_entry = ask(
            {
                "operation": "build",
                "source": hour_clock(),
                "output_file": str(destination / "clock.py"),
            }
        )
        written = files_under(destination)

    assert written == {}, f"a refused build wrote {sorted(written)}"
    for about, answer, field in (
        ("an output_file that is a number", not_a_path, "output_file"),
        ("a request with no entry", no_entry, "entry"),
    ):
        assert answer.get("status") == "invalid_input", (
            f"WHAT: {about} was answered {answer.get('status')!r}. "
            "WHY: a field of the request this tool cannot read is refused by "
            "name before any work starts. "
            f"HOW: inspect the answer: {answer}"
        )
        named = [d.get("symbol") for d in answer.get("diagnostics") or []]
        assert field in named, (
            f"WHAT: the refusal of {about} names {named} and not {field!r}. "
            "WHY: the Owner repairs the field the answer sends them to. "
            f"HOW: read the field through the request reader: {answer}"
        )
