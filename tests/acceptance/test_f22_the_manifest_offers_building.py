"""`build` is offered, and what it takes and answers is published before
the Owner sends a request.

SPEC.md lines 465-470 ask the manifest to list the operations and to
advertise an unimplemented one as unavailable; line 475 says an agent
must discover signatures and bindings without guessing an undocumented
API. `build` was advertised unavailable while it was refused. It answers
now, so it publishes the two shapes, and every refusal it can give is a
category the manifest describes.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

from _f22_fixtures import build, files_under, hour_clock, the_manifest


def test_the_manifest_says_build_is_available_and_covers_building():
    """Given a client that has sent no request of its own, when it asks
    what this tool offers, then `build` is advertised available, it is
    the operation covering the building category, and its request and
    answer shapes are published.

    still passes if: the shapes had been published for an operation still
    refused as unavailable -- the availability word is read too, and the
    tool refuses to publish a shape for an operation it does not answer.
    """
    manifest = the_manifest().get("result") or {}

    assert manifest["operations"]["build"] == "available", (
        f"WHAT: the manifest advertises build as "
        f"{manifest['operations'].get('build')!r}. "
        "WHY: an agent that reads 'unavailable' never sends the request, so "
        "an operation that answers must say so. "
        f"HOW: inspect the operations: {manifest['operations']}"
    )
    assert manifest["categories"]["building"] == {
        "operation": "build",
        "availability": "available",
    }, (
        f"WHAT: the building category stands as "
        f"{manifest['categories'].get('building')}. "
        "WHY: one operation per category of the profile, with the word that "
        "says whether an agent may call it. "
        f"HOW: inspect the categories: {manifest['categories']}"
    )

    shapes = manifest["operation_schemas"]["build"]
    sent = shapes["request"]["fields"]
    answered = shapes["response"]["fields"]
    for field in ("source", "entry", "output_file"):
        assert field in sent, (
            f"WHAT: the published request shape of build names "
            f"{sorted(sent)} and not {field!r}. "
            "WHY: every field this tool reads is published, or an agent "
            "guesses an undocumented API. "
            f"HOW: name it in manifest.py: {sent}"
        )
    assert sent["entry"]["presence"] == "required", (
        f"WHAT: the entry field is published as "
        f"{sent['entry'].get('presence')!r}. "
        "WHY: a build invokes a named entry function; there is no default "
        "one to fall back to. "
        f"HOW: publish it as required: {sent['entry']}"
    )
    assert sent["output_file"]["presence"] == "required", (
        f"WHAT: the output_file field is published as "
        f"{sent['output_file'].get('presence')!r}. "
        "WHY: a build writes one artefact and nothing decides where but the "
        "request. "
        f"HOW: publish it as required: {sent['output_file']}"
    )
    assert "result" in answered, (
        f"WHAT: the published answer shape of build names {sorted(answered)}. "
        "WHY: a completed build carries what it wrote, and an answer may "
        "carry no field the manifest does not describe. "
        f"HOW: name it in manifest.py: {answered}"
    )
    described = str(answered["result"]).lower()
    for owed in ("entry", "revision", "configuration", "evidence"):
        assert owed in described, (
            f"WHAT: what the manifest publishes about a build's result does "
            f"not mention {owed!r}: {described}. "
            "WHY: the Owner reads which entry, which revision, which "
            "configuration and which evidence the artefact they hold was "
            "built with, and must be able to look each of them up first. "
            "HOW: say all four in the field's description."
        )


def test_every_status_and_category_a_build_answers_is_published():
    """Given the statuses and refusal categories the manifest publishes,
    when a build is refused for each of the three things that can be
    wrong with a request -- a program that was not shown whole, an entry
    the program does not declare, and a destination directory that is
    not there -- then every status and every category in those answers
    is one the manifest publishes, and each refusal says what, why and
    how.

    still passes if: a refusal had carried a category published for
    something else entirely -- each refusal is also required to name the
    thing that is wrong.
    """
    manifest = the_manifest().get("result") or {}
    statuses = set(manifest["statuses"])
    categories = set(manifest["diagnostic_categories"])

    wrong_example = hour_clock().replace(
        "(example (valid-state (Clock 1)) => true)",
        "(example (valid-state (Clock 1)) => false)",
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        refusals = {
            "a program that was not shown whole": build(
                wrong_example, "step", destination / "clock.py"
            ),
            "an entry the program does not declare": build(
                hour_clock(), "tock", destination / "clock.py"
            ),
            "a destination directory that is not there": build(
                hour_clock(), "step", destination / "nowhere" / "clock.py"
            ),
        }
        left_behind = files_under(destination)

    assert left_behind == {}, (
        f"WHAT: the three refused builds left {sorted(left_behind)}. "
        "WHY: a refused build writes nothing. "
        "HOW: decide every refusal before anything is written."
    )
    for about, answer in refusals.items():
        assert answer.get("status") in statuses, (
            f"WHAT: the refusal of {about} carries the status "
            f"{answer.get('status')!r} and the manifest publishes "
            f"{sorted(statuses)}. "
            "WHY: a caller reads the vocabulary from the tool; a status it "
            "cannot look up is a word with no meaning. "
            f"HOW: publish it in service.py beside the others: {answer}"
        )
        said = answer.get("diagnostics") or []
        assert said, f"the refusal of {about} says nothing: {answer}"
        for diagnostic in said:
            assert diagnostic.get("category") in categories, (
                f"WHAT: the refusal of {about} carries the category "
                f"{diagnostic.get('category')!r}, which the manifest does "
                "not publish. "
                "WHY: a client reads the shape of every refusal from the "
                "manifest, so one of a category nothing declares cannot be "
                "read. "
                f"HOW: declare it in checker.py: {sorted(categories)}"
            )
            reason = diagnostic.get("reason") or ""
            assert len(reason) > 80, (
                f"WHAT: the refusal of {about} says {reason!r}. "
                "WHY: a refusal says what failed, why, and how to repair it, "
                "naming the value and the place. "
                f"HOW: write the three parts: {diagnostic}"
            )

    assert "tock" in " ".join(
        d.get("reason", "")
        for d in refusals["an entry the program does not declare"]["diagnostics"]
    ), (
        "WHAT: the refusal of an entry the program does not declare does not "
        f"name it: {refusals['an entry the program does not declare']}. "
        "WHY: the Owner misspelled a name and must be told which one. "
        "HOW: name the entry that was asked for."
    )
    assert "nowhere" in " ".join(
        d.get("reason", "")
        for d in refusals["a destination directory that is not there"]["diagnostics"]
    ), (
        "WHAT: the refusal of a destination whose directory is not there does "
        "not name the place: "
        f"{refusals['a destination directory that is not there']}. "
        "WHY: the Owner must be told which directory to create. "
        "HOW: name the path that was asked for."
    )
