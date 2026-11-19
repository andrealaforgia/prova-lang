"""Where a build is allowed to write, and what it says when it is asked
to write somewhere else.

The Owner authorises one directory and chooses one plain name inside it.
A name that climbs out of that directory, and a name that is a link
pointing anywhere at all, are refused before anything is written, and
each refusal names the rule it stands on rather than saying that
something went wrong.

Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import os
import pathlib

from _f24_fixtures import (
    FILE_EXISTS,
    NAME_IS_A_LINK,
    OUTSIDE_AUTHORITY,
    REFUSED,
    build_into,
    categories_of,
    entries_under,
    hour_clock,
    ask,
    reasons_of,
    says_the_authority_rule,
    working_files_under,
)


def _authorised_and_outside(tmp_path: pathlib.Path):
    """A directory the Owner authorises, and a directory outside it
    holding one file of 8 characters the build must not touch."""
    authorised = tmp_path / "authorised"
    outside = tmp_path / "outside"
    authorised.mkdir()
    outside.mkdir()
    (outside / "target.py").write_text("ORIGINAL\n", encoding="utf-8")
    return authorised, outside


def test_a_name_that_climbs_out_of_the_authorised_directory_is_refused(tmp_path):
    """Given the Owner authorises one directory, when they ask for an
    artefact under the name '../escape.py', then the answer refuses
    naming the authority rule and no file appears anywhere.

    still passes if: the tool had refused every build whatever its name
    -- the last assertion below builds the same program under a plain
    name in the same directory and reads the artefact it published.
    """
    authorised, outside = _authorised_and_outside(tmp_path)
    authority = os.path.realpath(authorised)

    climbed = build_into(authorised, "../escape.py")

    assert climbed.get("status") == REFUSED, (
        f"WHAT: a build under the name '../escape.py' was answered "
        f"{climbed.get('status')!r} instead of being refused. "
        "WHY: a name carrying '..' leaves the directory the Owner authorised, "
        "and a build writes only inside it. "
        f"HOW: inspect the answer: {climbed}"
    )
    assert OUTSIDE_AUTHORITY in categories_of(climbed), (
        f"WHAT: the refusal is categorised {sorted(categories_of(climbed))} "
        f"and not {OUTSIDE_AUTHORITY!r}. "
        "WHY: a client sorts refusals by their category word before it reads "
        "any prose, and this one is about the destination rule. "
        f"HOW: inspect the answer: {climbed}"
    )
    missing = says_the_authority_rule(climbed, authority)
    assert missing is None, (
        f"WHAT: the refusal does not name the authority rule: {missing}. "
        "WHY: a refusal that says only 'error' leaves the Owner guessing "
        "which rule they broke and what to send instead. "
        f"HOW: read the reasons it gave: {reasons_of(climbed)!r}"
    )
    assert not climbed.get("result"), f"the refusal carried a result: {climbed}"
    assert entries_under(authorised) == [], (
        f"WHAT: the authorised directory holds {entries_under(authorised)} "
        "after a refused build. "
        "WHY: a refusal writes nothing at all, working file included. "
        "HOW: decide the destination before anything is opened for writing."
    )
    assert entries_under(outside) == ["target.py"], (
        f"WHAT: the directory outside holds {entries_under(outside)}: the "
        "build wrote where it was not allowed. "
        "WHY: an artefact outside the authorised directory is a file the "
        "Owner never authorised. "
        "HOW: refuse a name that climbs out, before writing."
    )

    allowed = build_into(authorised, "clock.py")
    assert allowed.get("status") == "completed", (
        f"WHAT: a plain name inside the authorised directory was answered "
        f"{allowed.get('status')!r}. "
        "WHY: the rule refuses names that leave the directory, not every "
        "name. "
        f"HOW: inspect the answer: {allowed}"
    )
    assert entries_under(authorised) == ["clock.py"], (
        f"WHAT: the authorised directory holds {entries_under(authorised)} "
        "after a completed build. "
        "WHY: a build publishes exactly the one artefact it was asked for. "
        f"HOW: inspect the answer: {allowed}"
    )


def test_a_name_that_carries_a_directory_of_its_own_is_refused(tmp_path):
    """Given the Owner authorises one directory, when they ask for the
    names 'sub/clock.py', '/etc/clock.py' and '.', then each is refused
    naming the authority rule, and nothing is written.

    still passes if: the tool had refused every name -- the test above
    builds an artefact under a plain name in the same directory.
    """
    authorised, _ = _authorised_and_outside(tmp_path)
    authority = os.path.realpath(authorised)
    (authorised / "sub").mkdir()

    for name in ("sub/clock.py", "/etc/clock.py", ".", "..", ""):
        answer = build_into(authorised, name)
        assert answer.get("status") == REFUSED, (
            f"WHAT: the name {name!r} was answered "
            f"{answer.get('status')!r} instead of being refused. "
            "WHY: the Owner chooses one plain file name inside the directory "
            "they authorised; anything else names a place the authority does "
            "not cover. "
            f"HOW: inspect the answer: {answer}"
        )
        assert OUTSIDE_AUTHORITY in categories_of(answer), (
            f"WHAT: the name {name!r} was refused as "
            f"{sorted(categories_of(answer))}. "
            f"WHY: this is the one category that says a destination stands "
            "outside the authorised directory. "
            f"HOW: inspect the answer: {answer}"
        )
        missing = says_the_authority_rule(answer, authority)
        assert missing is None, (
            f"WHAT: the refusal of {name!r} does not name the authority "
            f"rule: {missing}. "
            "WHY: the Owner must read which rule refused their name. "
            f"HOW: read the reasons it gave: {reasons_of(answer)!r}"
        )
        assert entries_under(authorised) == ["sub"], (
            f"WHAT: after refusing {name!r} the authorised directory holds "
            f"{entries_under(authorised)}. "
            "WHY: a refusal writes nothing at all. "
            "HOW: decide the destination before opening anything."
        )


def test_a_link_at_the_chosen_name_is_refused_and_never_followed(tmp_path):
    """Given a link inside the authorised directory pointing at a file
    of 8 characters outside it, when the Owner asks for an artefact
    under the link's name, then the answer refuses naming the authority
    rule, the file outside is byte for byte as it was, and the link is
    still a link.

    still passes if: the tool had refused every name in that directory
    -- the first test builds an artefact under a plain name there.
    """
    authorised, outside = _authorised_and_outside(tmp_path)
    authority = os.path.realpath(authorised)
    target = outside / "target.py"
    before = target.read_bytes()
    os.symlink(str(target), str(authorised / "clock.py"))

    answer = build_into(authorised, "clock.py")

    assert answer.get("status") == REFUSED, (
        f"WHAT: a build under a name that is a link was answered "
        f"{answer.get('status')!r}. "
        "WHY: writing through a link writes wherever the link points, which "
        "is not what the authority covers. "
        f"HOW: inspect the answer: {answer}"
    )
    assert NAME_IS_A_LINK in categories_of(answer), (
        f"WHAT: the refusal is categorised {sorted(categories_of(answer))} "
        f"and not {NAME_IS_A_LINK!r}. "
        "WHY: a link at the destination is its own rule: it is refused "
        "whatever it points at, which is not the same as a file being in the "
        "way. "
        f"HOW: inspect the answer: {answer}"
    )
    missing = says_the_authority_rule(answer, authority)
    assert missing is None, (
        f"WHAT: the refusal does not name the authority rule: {missing}. "
        f"HOW: read the reasons it gave: {reasons_of(answer)!r}"
    )
    assert target.read_bytes() == before, (
        "WHAT: the file the link pointed at was changed by a refused build. "
        "WHY: a build never follows a link at its destination, so a file "
        "outside the authorised directory can never be touched. "
        "HOW: look at the name itself, without following it."
    )
    assert (authorised / "clock.py").is_symlink(), (
        "WHAT: the link itself was replaced. "
        "WHY: a refusal changes nothing, the link included. "
        "HOW: refuse before anything is written."
    )
    assert working_files_under(authorised) == [], (
        f"WHAT: the build left {working_files_under(authorised)} behind. "
        "WHY: a refused build leaves no working file. "
        "HOW: refuse before the working file is created."
    )


def test_a_link_pointing_inside_the_directory_is_refused_too(tmp_path):
    """Given a link inside the authorised directory pointing at another
    name inside the same directory, and a link pointing at nothing at
    all, when the Owner asks for an artefact under each name, then each
    is refused as a link.

    still passes if: the tool had refused the first link only because
    its target was outside -- this link points inside, where a plain
    file would be allowed.
    """
    authorised, _ = _authorised_and_outside(tmp_path)
    (authorised / "real.py").write_text("ORIGINAL\n", encoding="utf-8")
    os.symlink(str(authorised / "real.py"), str(authorised / "inside.py"))
    os.symlink(str(authorised / "nothing-here.py"), str(authorised / "broken.py"))

    for name in ("inside.py", "broken.py"):
        answer = build_into(authorised, name, replace=True)
        assert answer.get("status") == REFUSED, (
            f"WHAT: a build under the link {name!r} was answered "
            f"{answer.get('status')!r}. "
            "WHY: a link at the destination is refused whatever it points "
            "at, even when the Owner authorised a replacement. "
            f"HOW: inspect the answer: {answer}"
        )
        assert NAME_IS_A_LINK in categories_of(answer), (
            f"WHAT: the link {name!r} was refused as "
            f"{sorted(categories_of(answer))}. "
            "WHY: a client reads one word for a link at the destination. "
            f"HOW: inspect the answer: {answer}"
        )
    assert (authorised / "real.py").read_bytes() == b"ORIGINAL\n", (
        "WHAT: the file the link inside pointed at was changed. "
        "WHY: a refused build changes nothing. "
        "HOW: refuse the link without following it."
    )
    assert not (authorised / "nothing-here.py").exists(), (
        "WHAT: the build created the file the broken link pointed at. "
        "WHY: a link is never followed, so nothing is created through one. "
        "HOW: look at the name itself."
    )


def test_a_file_that_is_there_is_refused_unless_a_replacement_is_authorised(tmp_path):
    """Given an artefact already standing under the chosen name, when
    the Owner asks for a build without authorising a replacement, then
    it is refused and the artefact is byte for byte as it was.

    still passes if: the tool had refused the request for some other
    reason -- the answer's category says which rule refused it, and the
    test that follows authorises the replacement and is answered.
    """
    authorised, _ = _authorised_and_outside(tmp_path)
    first = build_into(authorised, "clock.py")
    assert first.get("status") == "completed", f"the first build: {first}"
    before = (authorised / "clock.py").read_bytes()

    again = build_into(authorised, "clock.py", entry="valid-state")

    assert again.get("status") == REFUSED, (
        f"WHAT: a build over an artefact that is already there was answered "
        f"{again.get('status')!r}. "
        "WHY: an artefact the Owner holds is replaced only when they say so. "
        f"HOW: inspect the answer: {again}"
    )
    assert FILE_EXISTS in categories_of(again), (
        f"WHAT: it was refused as {sorted(categories_of(again))}. "
        "WHY: a file in the way is its own rule, and the Owner repairs it by "
        "authorising a replacement. "
        f"HOW: inspect the answer: {again}"
    )
    assert "replace" in reasons_of(again), (
        f"WHAT: the refusal does not tell the Owner how to ask for the "
        f"replacement: {reasons_of(again)!r}. "
        "WHY: a refusal names the field that would make the request work. "
        "HOW: name the 'replace' field in the reason."
    )
    assert (authorised / "clock.py").read_bytes() == before, (
        "WHAT: the artefact that was there was changed by a refused build. "
        "WHY: a refused build changes nothing. "
        "HOW: decide the refusal before writing."
    )


def test_a_destination_written_as_one_path_is_answered_as_before(tmp_path):
    """Given a request naming the file to write as one path, as every
    build before this one did, when the Owner asks for a build to a free
    path and then to the same path again, then the first publishes an
    artefact and the second is refused with a file in the way.

    still passes if: the tool had stopped reading that field and refused
    both -- the first build is required to publish.
    """
    authorised, _ = _authorised_and_outside(tmp_path)
    target = authorised / "clock.py"

    first = ask(
        {
            "operation": "build",
            "source": hour_clock(),
            "entry": "step",
            "output_file": str(target),
        }
    )
    assert first.get("status") == "completed", (
        f"WHAT: a build naming its file as one path was answered "
        f"{first.get('status')!r}. "
        "WHY: every build asked for before this change named its file that "
        "way, and they are answered exactly as before. "
        f"HOW: inspect the answer: {first}"
    )
    published = (first.get("result") or {}).get("artefact") or {}
    assert published.get("path") == str(target), (
        f"WHAT: the answer records the path {published.get('path')!r}. "
        "WHY: the artefact record names the file the Owner now holds. "
        f"HOW: inspect the answer: {first}"
    )

    again = ask(
        {
            "operation": "build",
            "source": hour_clock(),
            "entry": "step",
            "output_file": str(target),
        }
    )
    assert again.get("status") == REFUSED and FILE_EXISTS in categories_of(again), (
        f"WHAT: the second build to the same path was answered "
        f"{again.get('status')!r} with {sorted(categories_of(again))}. "
        "WHY: this is what it answered before this change, and nothing asked "
        "for that to change. "
        f"HOW: inspect the answer: {again}"
    )

    authorised_replacement = ask(
        {
            "operation": "build",
            "source": hour_clock(),
            "entry": "valid-state",
            "output_file": str(target),
            "replace": True,
        }
    )
    assert authorised_replacement.get("status") == "completed", (
        f"WHAT: a replacement the Owner authorised, with the destination "
        f"written as one path, was answered "
        f"{authorised_replacement.get('status')!r}. "
        "WHY: the Owner authorises a replacement the same way whichever way "
        "they name the destination. "
        f"HOW: inspect the answer: {authorised_replacement}"
    )
    replacing = (authorised_replacement.get("result") or {}).get("artefact") or {}
    assert replacing.get("replaced") is True, (
        f"WHAT: the answer records 'replaced' as {replacing.get('replaced')!r}. "
        "WHY: the Owner reads from the answer whether something of theirs was "
        "replaced. "
        f"HOW: inspect the answer: {authorised_replacement}"
    )


def test_a_request_that_names_the_destination_twice_or_by_half_is_refused(tmp_path):
    """Given requests that name the destination in both ways at once,
    that send only half of the two-field way, and that send none of the
    three fields, when each is sent, then each is refused naming the
    fields to repair, and nothing is written.

    still passes if: the tool had refused every build request -- the
    tests above send each of the two ways on its own and are answered.
    """
    authorised, _ = _authorised_and_outside(tmp_path)
    source = hour_clock()
    both = ask(
        {
            "operation": "build",
            "source": source,
            "entry": "step",
            "output_file": str(authorised / "clock.py"),
            "output_directory": str(authorised),
            "output_name": "clock.py",
        }
    )
    half = ask(
        {
            "operation": "build",
            "source": source,
            "entry": "step",
            "output_directory": str(authorised),
        }
    )
    other_half = ask(
        {
            "operation": "build",
            "source": source,
            "entry": "step",
            "output_name": "clock.py",
        }
    )
    none = ask({"operation": "build", "source": source, "entry": "step"})

    for about, answer in (
        ("both ways at once", both),
        ("a directory with no name", half),
        ("a name with no directory", other_half),
        ("neither way", none),
    ):
        assert answer.get("status") == REFUSED, (
            f"WHAT: the request naming {about} was answered "
            f"{answer.get('status')!r}. "
            "WHY: a build must know exactly one destination; a request that "
            "names two or half of one names none. "
            f"HOW: inspect the answer: {answer}"
        )
        named = reasons_of(answer)
        assert "output_directory" in named or "output_name" in named or (
            "output_file" in named
        ), (
            f"WHAT: the refusal of {about} names no field to repair: "
            f"{named!r}. "
            "WHY: a client repairs the field the refusal names. "
            f"HOW: inspect the answer: {answer}"
        )
    assert entries_under(authorised) == [], (
        f"WHAT: the authorised directory holds {entries_under(authorised)} "
        "after four refused requests. "
        "WHY: a refused request writes nothing. "
        "HOW: read the request before writing."
    )


def test_a_hostile_field_is_refused_by_name_without_a_traceback(tmp_path):
    """Given build requests whose destination fields hold a number, a
    zero byte, 5000 characters, a lone surrogate, a relative directory
    and a 'replace' that is the text 'yes', when each is sent, then each
    is refused as an invalid input naming its field, and nothing is
    written.

    still passes if: the tool had refused every build -- the tests above
    send well written fields of both kinds and are answered.
    """
    authorised, _ = _authorised_and_outside(tmp_path)
    hostile = {
        "a directory that is a number": build_into(7, "clock.py"),
        "a name that is a number": build_into(authorised, 7),
        "a name carrying a zero byte": build_into(authorised, "clo\x00ck.py"),
        "a name of 5000 characters": build_into(authorised, "c" * 5000),
        "a name carrying a lone surrogate": build_into(authorised, "cl\ud800ck.py"),
        "a relative directory": build_into("authorised", "clock.py"),
        "a replacement authorised with the text yes": build_into(
            authorised, "clock.py", replace="yes"
        ),
        "a replacement authorised with a list": build_into(
            authorised, "clock.py", replace=[1]
        ),
    }
    for about, answer in hostile.items():
        assert answer.get("status") == REFUSED, (
            f"WHAT: a request carrying {about} was answered "
            f"{answer.get('status')!r}. "
            "WHY: a field this tool cannot use is a fact about the request, "
            "answered as an invalid input and never as a fact about a "
            "program. "
            f"HOW: inspect the answer: {answer}"
        )
        named = reasons_of(answer)
        assert (
            "output_directory" in named
            or "output_name" in named
            or "replace" in named
        ), (
            f"WHAT: the refusal of {about} names no field: {named!r}. "
            "WHY: the Owner repairs the field the refusal names. "
            f"HOW: inspect the answer: {answer}"
        )
        assert not answer.get("result"), f"a refusal carried a result: {answer}"
    assert entries_under(authorised) == [], (
        f"WHAT: the authorised directory holds {entries_under(authorised)} "
        "after eight refused requests. "
        "WHY: a refused request writes nothing. "
        "HOW: read the fields before writing."
    )


def test_the_tool_publishes_the_three_fields_of_an_authorised_destination():
    """Given the manifest every client reads before it asks, when it is
    asked for, then the build operation publishes 'output_directory',
    'output_name' and 'replace' beside 'output_file', each saying when
    it must be sent.

    still passes if: the manifest had published fields that do not work
    -- the tests above send each of them to the real command.
    """
    manifest = ask({"operation": "discover"})
    schemas = manifest.get("result", {}).get("operation_schemas", {})
    build = schemas.get("build") or {}
    request_fields = (build.get("request") or {}).get("fields") or {}

    for field in ("output_directory", "output_name", "replace", "output_file"):
        assert field in request_fields, (
            f"WHAT: the build operation publishes "
            f"{sorted(request_fields)} and not {field!r}. "
            "WHY: a client writes the fields the manifest publishes, and a "
            "field that works but is published nowhere cannot be found. "
            f"HOW: inspect what build publishes: {build}"
        )
        published = request_fields[field]
        assert published.get("presence") and published.get("what"), (
            f"WHAT: the field {field!r} is published as {published}. "
            "WHY: a client reads when a field must be sent and what it is "
            "for. "
            "HOW: publish both."
        )
    assert "replace" in str(request_fields.get("replace")), (
        "WHAT: the 'replace' field says nothing about itself. "
        "WHY: the Owner learns from the manifest how to authorise a "
        "replacement. "
        f"HOW: inspect: {request_fields.get('replace')}"
    )
