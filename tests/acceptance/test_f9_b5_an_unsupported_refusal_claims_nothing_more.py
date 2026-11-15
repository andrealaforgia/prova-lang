"""F9.B5 -- when the source is outside the profile the tool stops there
and says so: the answer carries no claim about the program, no result
and no digest of a source it did not check through.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered everything with a bare refusal. The
second test requires the accepted twin to carry the claim and the digest
it carries today, so the absence below is the profile boundary speaking
and not an answer that lost its contents.
"""

from __future__ import annotations

from _f9_profile_fixtures import (
    OUT_OF_PROFILE,
    assert_unsupported_naming,
    check,
)

TRAILING = OUT_OF_PROFILE["a trailing top-level expression"]

# Words that would tell a reader something was established about the
# program. None of them can be true of a source the tool refused at its
# profile boundary.
WORDS_THAT_WOULD_CLAIM_MORE = (
    "verified",
    "verify",
    "proved",
    "proven",
    "proof",
    "holds",
    "guarantee",
    "sound",
    "valid program",
)


def test_an_out_of_profile_answer_claims_nothing_about_the_program():
    """Given a source with a trailing call, when it is checked, then the
    answer is the out-of-profile refusal and it carries no `claim`, no
    `result` and no `source_digest`, and none of the 9 words that would
    say something was established."""
    refusal = check(TRAILING.source)
    assert_unsupported_naming(
        refusal, naming=TRAILING.naming, why="a source with a trailing call"
    )
    response = refusal.response()
    printed = str(response).lower()

    for key in ("claim", "result", "source_digest"):
        assert key not in response, (
            f"the out-of-profile answer carries {key!r}: {response}. The tool "
            "stopped at the construct it cannot read, so it has nothing to "
            "report about the program and must not appear to."
        )
    for word in WORDS_THAT_WOULD_CLAIM_MORE:
        assert word not in printed, (
            f"the out-of-profile answer uses the word {word!r}: {response}. "
            "Nothing about the program was established, so no word in the "
            "answer may suggest that it was."
        )


def test_the_accepted_twin_still_carries_its_claim_and_digest():
    """Control: given the same source without the trailing call, when it
    is checked, then the answer still carries the claim and the
    `source_digest` it carries today, so an answer losing its contents
    would be seen."""
    response = check(TRAILING.twin).response()

    assert response.get("status") == "completed", response
    assert response.get("claim") == {"kind": "static_check", "scope": "this input"}, (
        f"the accepted program lost the claim the tool makes about it: "
        f"{response}."
    )
    assert response.get("source_digest"), (
        f"the accepted program lost the digest that binds the answer to the "
        f"source it read: {response}."
    )
