"""F22 criteria 3 and 4: the artefact's recorded source revision equals
the verified one, and when the source changes, the artefact's evidence
does not certify the new source.

SPEC.md line 487: verification binds to the typed program and backend
configuration used for output. An artefact with no recorded revision, or
one that could be taken to stand for a source other than the verified
one, is the worst thing a build can leave behind: the Owner would read a
word about a program they no longer have.

Drives only the `prova` command's real JSON stdin/stdout surface, the
file it writes, and that file's own answer about itself. No imports from
src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile

from _f22_fixtures import (
    answered,
    artefact_of,
    ask,
    build,
    digest_of,
    header_of,
    hour_clock,
    run_artefact,
)


def _asked_whether_it_certifies(path: pathlib.Path, source: str) -> bool:
    """What the artefact itself answers about a source text: whether the
    evidence it carries is about that text."""
    ran = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            "import json,runpy,sys;"
            "m=runpy.run_path(sys.argv[1]);"
            "print(json.dumps(m['certifies'](sys.stdin.read())))",
            str(path),
        ],
        input=source,
        capture_output=True,
        text=True,
        timeout=30.0,
    )
    assert ran.returncode == 0, (
        f"WHAT: the artefact could not be asked whether it certifies a "
        f"source: exit {ran.returncode}. "
        "WHY: an artefact must answer which source its evidence is about; a "
        "reader holding two versions of a file has nothing else to go on. "
        f"HOW: read the failure: {ran.stderr[-600:]!r}"
    )
    return json.loads(ran.stdout)


def test_c3_the_recorded_revision_is_the_revision_that_was_verified():
    """Given a build of the shipped hour clock, when the Owner compares
    the revision the artefact records with the revision the `verify`
    answer carries for the same characters, then the two are the same
    digest, and it is the SHA-256 of the source as the request sent it.

    still passes if: the artefact had recorded a digest of something else
    entirely that happened to be stable -- it is compared with the digest
    the Owner computes themselves and with the one `verify` reports.
    """
    source = hour_clock()
    verified = ask({"operation": "verify", "source": source})
    assert verified["aggregate"]["result"] == "verified", (
        "WHAT: the shipped hour clock does not come back verified: "
        f"{verified.get('aggregate')}. "
        "WHY: this test is about an artefact of a verified program; without "
        "one there is nothing to build. "
        f"HOW: inspect the verify answer: {verified}"
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        target = pathlib.Path(tmp_dir) / "clock.py"
        answer = build(source, "step", target)
        published = artefact_of(answer, "the shipped hour clock")
        recorded = header_of(target)

    assert recorded["source_revision"] == verified["source_digest"], (
        f"WHAT: the artefact records the revision "
        f"{recorded.get('source_revision')!r} and the verify answer for the "
        f"same characters carries {verified['source_digest']!r}. "
        "WHY: the artefact stands on that verification and on no other; two "
        "digests mean the Owner cannot tie the two together. "
        f"HOW: record the revision of the source that was verified."
    )
    assert recorded["source_revision"] == digest_of(source) == (
        published["source_revision"]
    ), (
        f"WHAT: the artefact records {recorded.get('source_revision')!r}, the "
        f"answer records {published.get('source_revision')!r} and the SHA-256 "
        f"of the source is {digest_of(source)!r}. "
        "WHY: the Owner recomputes the revision from the file they hold; a "
        "digest taken another way cannot be checked. "
        "HOW: take the SHA-256 of the exact characters the request carried."
    )


def test_c4_an_artefact_does_not_certify_a_changed_source():
    """Given an artefact built from the shipped hour clock, and a changed
    source in which the clock turns back at 11 instead of 12, when the
    old artefact is asked about the new source, then it answers that its
    evidence is not about it, while it still answers that it is about the
    source it was built from.

    still passes if: the artefact had said no to every source -- it is
    required to say yes to the one it was built from.
    """
    source = hour_clock()
    changed = source.replace("(= (.hr current) 12) 1", "(= (.hr current) 11) 1")
    assert changed != source, (
        "WHAT: the text this test changes is not in the shipped clock. "
        "WHY: a test that changed nothing would compare a source with "
        "itself and pass over an artefact that certifies anything. "
        "HOW: read examples/hour-clock.prova and fix the text above."
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        target = pathlib.Path(tmp_dir) / "clock.py"
        build(source, "step", target)
        recorded = header_of(target)

        assert recorded["source_revision"] != digest_of(changed), (
            f"WHAT: the artefact's recorded revision "
            f"{recorded['source_revision']!r} is the revision of the changed "
            "source. "
            "WHY: the two sources are different texts, so one revision "
            "cannot stand for both. "
            "HOW: take the revision over the characters that were verified."
        )
        assert _asked_whether_it_certifies(target, changed) is False, (
            "WHAT: the artefact says its evidence certifies the changed "
            "source. "
            "WHY: nothing was shown about that text; an artefact that "
            "answers yes here would let the Owner run a program its "
            "evidence is not about. "
            f"HOW: compare the revision it records with the digest of the "
            f"text it is asked about: {recorded}"
        )
        assert _asked_whether_it_certifies(target, source) is True, (
            "WHAT: the artefact says its evidence does not certify the "
            "source it was built from. "
            "WHY: without this the test above would pass over an artefact "
            "that certifies nothing at all. "
            f"HOW: inspect what it records: {recorded}"
        )

        at_the_turn = run_artefact(target, ["(Clock 11)", "(Tick)"])
        assert answered(at_the_turn, "(Clock 11) and (Tick)") == (
            "(Outcome (Clock 12) true)"
        ), (
            f"WHAT: the artefact answered {at_the_turn.stdout.strip()!r} at "
            "the hour 11, and the program it was built from makes that 12. "
            "WHY: the artefact is the program that was verified; it must not "
            "have been built from the changed source. "
            f"HOW: read the artefact at {target}"
        )
