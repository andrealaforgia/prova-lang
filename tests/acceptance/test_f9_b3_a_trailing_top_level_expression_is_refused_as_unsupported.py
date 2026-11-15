"""F9.B3 -- a call written after the declarations is refused as outside
this profile, not with the general refusal the reader gives a word it
cannot place at the top level.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: every top-level form the reader cannot place became an
out-of-profile refusal, which would relabel a misspelled declaration
word as a feature of a later profile. The second test requires the
misspelled word to keep the refusal it has today.
"""

from __future__ import annotations

from _f9_profile_fixtures import (
    INVALID_PROGRAM_STATUS,
    MISSPELLED_DECLARATION_WORD,
    OUT_OF_PROFILE,
    UNSUPPORTED_CATEGORY,
    assert_answered_without_the_unsupported_status,
    assert_refused_at,
    assert_unsupported_naming,
    categories,
    check,
)

TRAILING = OUT_OF_PROFILE["a trailing top-level expression"]


def test_a_call_after_the_declarations_is_refused_as_outside_this_profile():
    """Given a declared function followed by the call `(f 1)` on line 6,
    when the source is checked, then it is refused as unsupported, the
    refusal says it is a top-level expression and names `f` and points
    at line 6, and the same source without that call is accepted."""
    refusal = check(TRAILING.source)

    reason = assert_unsupported_naming(
        refusal, naming=TRAILING.naming, why="a call written after the declarations"
    )
    assert_refused_at(
        refusal, line=TRAILING.line, why="a call written after the declarations"
    )
    assert "expected a top-level" not in reason, (
        f"the refusal is the general one for a form the reader cannot place: "
        f"{reason!r}. A call after the declarations is a trailing top-level "
        "expression, which core-0 does not have; say that instead."
    )

    assert_answered_without_the_unsupported_status(
        check(TRAILING.twin),
        expected_status=TRAILING.twin_status,
        why="the same source without the trailing call",
    )


def test_a_misspelled_declaration_word_keeps_the_refusal_it_has_today():
    """Given `(deftypo T (record (x Int)))`, when it is checked, then it
    is still refused as an invalid program naming `deftypo`, because a
    misspelled declaration word is a spelling mistake and not a use of
    something a later profile would add."""
    response = check(MISSPELLED_DECLARATION_WORD).response()

    assert response.get("status") == INVALID_PROGRAM_STATUS, (
        f"a misspelled declaration word was answered {response.get('status')!r}: "
        f"{response}. The reader cannot place the word, which is the refusal it "
        "already gives; the profile boundary has nothing to say about it."
    )
    assert UNSUPPORTED_CATEGORY not in categories(response), (
        f"a misspelled declaration word was reported as out of profile: "
        f"{response}. Telling a reader to wait for a later profile when the "
        "repair is one letter sends them to the wrong place."
    )
    assert "deftypo" in response["diagnostics"][0].get("reason", ""), (
        f"the refusal does not name the word that cannot be placed: {response}."
    )
