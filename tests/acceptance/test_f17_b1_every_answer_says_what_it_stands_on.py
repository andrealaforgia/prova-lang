"""F17.B1 -- every completed answer says what kind of claim it makes, how
far it reaches, which revision of the source it is about and which
dependencies it stands on.

A reader of one answer can then tell it from evidence of another kind and
from evidence about another revision, without asking the tool again.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool stamped one constant digest on every answer.
The first test computes the revision from the text it sent rather than
reading it back from the answer. still passes if: a refusal carried the
block too, which the last test forbids.
"""

from __future__ import annotations

from _f17_provenance_fixtures import (
    A_PROGRAM,
    NOT_A_PROGRAM,
    THE_OPERATIONS_THAT_READ_A_PROGRAM,
    answer_about,
    digest_of,
    what_it_stands_on,
    the_manifest,
)

HEX = set("0123456789abcdef")


def test_every_completed_answer_names_its_claim_its_scope_and_its_revision():
    """Given the 2-function program, when each of the 5 operations that
    read a program answers it, then the answer carries a claim with a
    kind and a scope, and the revision of the exact text that was sent."""
    for operation in THE_OPERATIONS_THAT_READ_A_PROGRAM:
        answer = answer_about(operation)
        claim = answer.get("claim") or {}

        assert claim.get("kind") and claim.get("scope"), (
            f"WHAT: the {operation!r} answer claims {claim}. WHY: an answer "
            "that does not say what kind of statement it makes and how far it "
            "reaches is read as evidence of whatever the reader hoped for. "
            "HOW: carry a claim with a kind and a scope."
        )
        assert answer.get("source_digest") == digest_of(A_PROGRAM), (
            f"WHAT: the {operation!r} answer is about "
            f"{answer.get('source_digest')!r} and the text sent is "
            f"{digest_of(A_PROGRAM)!r}. WHY: an answer that names another "
            "revision certifies a text nobody sent. "
            "HOW: stamp the SHA-256 of the submitted characters."
        )


def test_every_completed_answer_names_the_dependencies_it_stands_on():
    """Given the same program, when each of the 5 operations answers,
    then the answer names the digest of the dependencies behind it, and
    it is the 1 digest the manifest publishes for this tool."""
    published = what_it_stands_on(the_manifest(), "of the manifest").get(
        "dependency_digest"
    )
    assert isinstance(published, str) and len(published) == 64, (
        f"WHAT: the manifest publishes {published!r} as the digest of this "
        "tool's dependencies. WHY: a client that cannot read the current "
        "digest cannot tell a kept answer apart from a current one. "
        "HOW: publish a SHA-256 of the profile, the language and the versions."
    )
    assert set(published) <= HEX, (
        f"WHAT: {published!r} is not written as a SHA-256. WHY: a client "
        "recomputes and compares it. HOW: publish the hexadecimal digest."
    )

    for operation in THE_OPERATIONS_THAT_READ_A_PROGRAM:
        carried = what_it_stands_on(
            answer_about(operation), f"of {operation!r}"
        ).get("dependency_digest")
        assert carried == published, (
            f"WHAT: the {operation!r} answer stands on {carried!r} and the "
            f"manifest publishes {published!r}. WHY: two digests for one tool "
            "leave a client unable to decide whether a kept answer is still "
            "about this tool. HOW: read both from the one place that computes "
            "it."
        )


def test_an_answer_that_read_no_program_stands_on_nothing():
    """Given a source that is not a program, when each of the 5
    operations is asked, then the answer carries no claim, no revision
    and no provenance at all."""
    for operation in THE_OPERATIONS_THAT_READ_A_PROGRAM:
        refusal = answer_about(operation, NOT_A_PROGRAM)

        assert refusal["status"] == "invalid_program", refusal
        for field in ("claim", "source_digest", "stands_on"):
            assert field not in refusal, (
                f"WHAT: the {operation!r} refusal carries {field!r}: {refusal}. "
                "WHY: the tool stopped at the text it could not read, so it "
                "stands on nothing and must not appear to. "
                "HOW: carry the block only with a completed answer."
            )
