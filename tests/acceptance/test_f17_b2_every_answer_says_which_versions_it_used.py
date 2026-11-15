"""F17.B2 -- every completed answer names the compiler, the encoding, the
solver and the runtime it used, or says which of them do not apply and
why.

A reader comparing two answers can then see whether the same tool and the
same runtime stand behind them, and a reader of this tool's answer learns
that no solver and no encoding were in it at all.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool answered "not applicable" for all 4. The second
test requires the 2 it really used to name a version with a digit, and
the third requires a reason of its own for each of the 2 that do not.
"""

from __future__ import annotations

from _f17_provenance_fixtures import (
    DOES_NOT_APPLY,
    THE_OPERATIONS_THAT_READ_A_PROGRAM,
    THE_VERSIONS_AN_ANSWER_NAMES,
    answer_about,
    the_manifest,
    versions_of,
)

THE_ONES_THIS_TOOL_USED = ("compiler", "runtime")
THE_ONES_THIS_TOOL_HAS_NONE_OF = ("encoding", "solver")


def _every_completed_answer() -> dict:
    answers = {
        operation: answer_about(operation)
        for operation in THE_OPERATIONS_THAT_READ_A_PROGRAM
    }
    answers["discover"] = the_manifest()
    return answers


def test_every_completed_answer_names_all_four_versions():
    """Given the 2-function program and the manifest, when each of the 6
    completed answers is read, then it names exactly the 4 versions, each
    as a text with something in it."""
    for operation, answer in _every_completed_answer().items():
        named = versions_of(answer, f"of {operation!r}")

        assert sorted(named) == sorted(THE_VERSIONS_AN_ANSWER_NAMES), (
            f"WHAT: the {operation!r} answer names {sorted(named)} and the 4 "
            f"asked for are {sorted(THE_VERSIONS_AN_ANSWER_NAMES)}. WHY: a "
            "reader comparing two answers has to find every one of them in "
            "both. HOW: name all 4, saying of each either the version used or "
            "that it does not apply."
        )
        for version in THE_VERSIONS_AN_ANSWER_NAMES:
            said = named[version]
            assert isinstance(said, str) and said.strip(), (
                f"WHAT: the {operation!r} answer says {said!r} about "
                f"{version!r}. WHY: a name with nothing beside it tells a "
                "reader neither a version nor that there is none. "
                "HOW: write the version, or a sentence saying it does not "
                "apply and why."
            )


def test_the_two_this_tool_really_used_name_a_version():
    """Given the same 6 answers, then the compiler and the runtime each
    name the thing used and a version with at least 1 digit, and neither
    says it does not apply."""
    for operation, answer in _every_completed_answer().items():
        named = versions_of(answer, f"of {operation!r}")
        for version in THE_ONES_THIS_TOOL_USED:
            said = named[version]
            assert not said.startswith(DOES_NOT_APPLY), (
                f"WHAT: the {operation!r} answer says {version!r} does not "
                f"apply: {said!r}. WHY: this answer was produced by that "
                f"{version}, so a reader told it does not apply cannot "
                "reproduce the answer. HOW: name it with its version."
            )
            assert any(character.isdigit() for character in said), (
                f"WHAT: the {operation!r} answer says {said!r} about "
                f"{version!r} and no digit stands in it. WHY: two answers "
                "from two versions would read the same. HOW: name the version."
            )

        assert "prova" in named["compiler"].lower(), (
            f"WHAT: the {operation!r} answer says {named['compiler']!r} about "
            "the compiler and does not name it. WHY: a reader has to know "
            "which compiler the version belongs to. HOW: name the tool beside "
            "its version."
        )


def test_the_two_this_tool_has_none_of_say_so_with_a_reason():
    """Given the same 6 answers, then the encoding and the solver each
    say they do not apply, and each says why in at least 20 characters of
    its own."""
    for operation, answer in _every_completed_answer().items():
        named = versions_of(answer, f"of {operation!r}")
        for version in THE_ONES_THIS_TOOL_HAS_NONE_OF:
            said = named[version]
            assert said.startswith(DOES_NOT_APPLY), (
                f"WHAT: the {operation!r} answer says {said!r} about "
                f"{version!r}. WHY: this tool has none, and a version written "
                "there would say work was done that nobody did. "
                f"HOW: write {DOES_NOT_APPLY!r} and the reason."
            )
            reason = said[len(DOES_NOT_APPLY):].strip()
            assert len(reason) >= 20, (
                f"WHAT: the {operation!r} answer gives {reason!r} as the "
                f"reason {version!r} does not apply. WHY: a reader has to "
                "learn why there is none, not only that there is none. "
                "HOW: say what this tool does instead."
            )

        assert (
            named["encoding"] != named["solver"]
        ), (
            f"WHAT: the {operation!r} answer gives one sentence for the "
            "encoding and the solver. WHY: they are 2 different absences and "
            "a reader told one sentence learns about one of them. "
            "HOW: give each its own reason."
        )
