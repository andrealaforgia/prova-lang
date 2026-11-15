"""F10.B5 -- a repaired program is accepted, and the answer is about the
repaired text.

The client edits, submits again, and reads the revision of what it has
now; the revision of the text it refused is gone from the answer.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool accepted everything after the first call. The
last test checks the broken program again after the repair and requires
the same refusal, so an accepting tool is seen.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    INVALID_PROGRAM,
    REVISION,
    TYPE_ERRORS,
    WELL_FORMED,
    check,
    diagnostics,
    revision_of,
)

WHY = "a body that does not have the declared return type"
BROKEN = TYPE_ERRORS[WHY].source
REPAIRED = WELL_FORMED


def test_the_repaired_program_is_accepted_with_the_revision_of_its_new_text():
    """Given a program refused for a type error, when the declared
    return type is repaired and it is checked again, then the answer is
    `completed` and binds to the SHA-256 of the repaired text, which is
    not the revision the refusal carried."""
    refusal = diagnostics(check(BROKEN))[0]
    assert refusal.get(REVISION) == revision_of(BROKEN), refusal

    accepted = check(REPAIRED)

    assert accepted.get("status") == "completed", (
        f"the repaired program was still refused: {accepted}."
    )
    assert accepted.get("source_digest") == revision_of(REPAIRED), (
        f"the accepted answer binds to {accepted.get('source_digest')!r}, not to "
        f"the repaired text {revision_of(REPAIRED)!r}: {accepted}. Evidence "
        "about an old text cannot certify the new one."
    )
    assert accepted.get("source_digest") != refusal.get(REVISION), (
        f"the answer about the repaired program carries the revision of the "
        f"text that was refused: {accepted}."
    )


def test_the_refused_text_is_still_refused_after_the_repair():
    """Control: given the broken program again after the repaired one
    was accepted, when it is checked, then it is refused once more with
    its own revision."""
    check(REPAIRED)
    again = check(BROKEN)

    assert again.get("status") == INVALID_PROGRAM, (
        f"the broken program was accepted after the repaired one: {again}."
    )
    assert diagnostics(again)[0].get(REVISION) == revision_of(BROKEN), diagnostics(again)
