"""F10.B1 -- every diagnostic says which source the answer is about.

The revision is the SHA-256 of the exact source text the request
carried: a client that keeps two versions of a file tells apart the
answer about one from the answer about the other without trusting the
order of its calls.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova; the revision is computed here the way a client
computes it.

still passes if: the tool stamped one constant on every answer. The
second test submits two sources and requires two different revisions,
and both tests compare against the digest computed here, so a constant
or a digest of something else is seen.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    ALL_CASES,
    INVALID_PROGRAM,
    REVISION,
    WELL_FORMED,
    check,
    diagnostics,
    revision_of,
    with_body,
)


def test_every_refusal_carries_the_revision_of_the_source_it_is_about():
    """Given each of the 9 refused programs, when it is checked, then
    every diagnostic in the answer carries `source_revision` equal to the
    SHA-256 of the submitted text."""
    for why, case in ALL_CASES.items():
        response = check(case.source)
        assert response.get("status") == INVALID_PROGRAM, (why, response)
        found = diagnostics(response)
        assert found, f"{why} came back with no diagnostic: {response}."
        for entry in found:
            assert entry.get(REVISION) == revision_of(case.source), (
                f"the refusal for {why} carries {entry.get(REVISION)!r} as its "
                f"revision, expected {revision_of(case.source)!r}: {entry}. A "
                "client decides which version of its file the answer is about "
                "by this field alone."
            )


def test_two_sources_are_two_revisions_and_one_source_is_one():
    """Given two programs that differ by one character, when both are
    checked, then the 2 refusals carry 2 different revisions, and
    checking the same program twice carries the same revision twice."""
    one = with_body("(+ cents true)")
    other = with_body("(+ cents false)")

    first = diagnostics(check(one))[0]
    second = diagnostics(check(other))[0]
    again = diagnostics(check(one))[0]

    assert first.get(REVISION) != second.get(REVISION), (
        f"two different programs carry the same revision {first.get(REVISION)!r}: "
        f"{first} and {second}. A revision that does not change with the text "
        "cannot tell two versions apart."
    )
    assert first.get(REVISION) == again.get(REVISION) == revision_of(one), (
        f"checking one program twice gave {first.get(REVISION)!r} and "
        f"{again.get(REVISION)!r}: the revision is a function of the text, so "
        "the same text has the same revision every time."
    )
    accepted = check(WELL_FORMED)
    assert accepted.get("status") == "completed", accepted
