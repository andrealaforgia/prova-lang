"""F26, the promise that nothing else moved -- a verify request that
sends no descriptor is answered with the same characters it was answered
with before the obligations of a machine existed.

The law: adding the three obligations of a machine changes nothing about
an answer to a request that names no machine -- not a word of it, not a
count, not an order, not a byte.

The answers pinned beside this test were taken from the tree as it was
before this feature, through that tree's own build of the `prova`
command, and are compared character for character with what the command
answers now. Two parts of `stands_on` are read apart, because neither is
a statement about the answer: `dependency_digest`, the digest of the tool
itself, which any change to the tool moves by design, and `versions`,
which names the Python and the solver this run used and moves when either
is upgraded. The test requires both to be present in the answer and
compares every other character exactly. Had they been included, this
test could only ever have said that the tool or its interpreter changed,
which the commit and the environment already say.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the pinned file were empty or its answers were taken
from the tool as it is now. The first test below requires all 6 pinned
programs to be there and their answers to say what they said, and the
file is read from the pre-feature tree in the delivery workspace, never
written by the tool under test.
"""

from __future__ import annotations

import json
import pathlib

import pytest

import _f26_induction_fixtures as induction

PINNED = pathlib.Path(__file__).with_name("_f26_pinned_verify_answers.json")

# What an answer says about the tool that produced it rather than about
# the program it is about: the digest of the tool, which any change to
# the tool moves, and the versions behind this run, which an upgrade of
# Python or of the solver moves. Both are read apart from the comparison.
THE_DIGEST_OF_THE_TOOL = "dependency_digest"
WHAT_THIS_RUN_USED = "versions"
ABOUT_THE_TOOL = (THE_DIGEST_OF_THE_TOOL, WHAT_THIS_RUN_USED)

# How many answers are pinned: every shape a verify answer has, so that
# nothing can move in any of them unnoticed.
THE_PINNED_PROGRAMS = 12


def _pinned() -> dict:
    assert PINNED.exists(), (
        f"WHAT: {PINNED.name} is not beside this test. "
        "WHY: the answers this tool gave before the obligations of a machine "
        "existed are the only thing the answers it gives now can be compared "
        "with. HOW: ship the pinned answers beside this test."
    )
    return json.loads(PINNED.read_text(encoding="utf-8"))


def _without_what_is_about_the_tool(answer_text: str) -> str:
    """`answer_text` with what it says about the tool itself replaced by
    one word each, so that every other character is compared."""
    answer = json.loads(answer_text)
    stands_on = answer.get("stands_on")
    if isinstance(stands_on, dict):
        for part in ABOUT_THE_TOOL:
            if part in stands_on:
                stands_on[part] = f"what this answer says about the tool: {part}"
    return json.dumps(answer, sort_keys=True)


def test_the_pinned_answers_are_the_twelve_taken_before_the_feature():
    """Given the answers pinned beside this test, then there are 12 of
    them, each with the program it is about and the characters the tool
    answered, and each says it is a verify answer."""
    pinned = _pinned()

    assert len(pinned) == THE_PINNED_PROGRAMS, (
        f"WHAT: {len(pinned)} answers are pinned, not {THE_PINNED_PROGRAMS}: "
        f"{sorted(pinned)}. "
        "WHY: the promise is about every shape a verify answer has -- a "
        "program verified, a program not verified, a source refused, a "
        "source with nothing in it -- and a pin of fewer programs covers "
        "fewer shapes. HOW: pin the six answers again from the pre-feature "
        "tree."
    )
    for named, kept in pinned.items():
        answered = json.loads(kept["answer_text"])
        assert answered.get("operation") == "verify", (
            f"WHAT: the answer pinned for {named!r} is about "
            f"{answered.get('operation')!r}. "
            "WHY: this test is about verify answers alone. "
            "HOW: pin a verify answer."
        )
        stands_on = answered.get("stands_on") or {}
        assert answered.get("status") != "completed" or all(
            part in stands_on for part in ABOUT_THE_TOOL
        ), (
            f"WHAT: the completed answer pinned for {named!r} says "
            f"{sorted(stands_on)} about what it stands on, and the parts read "
            f"apart are {list(ABOUT_THE_TOOL)}. "
            "WHY: a part read apart must be there to be read apart; without "
            "it the comparison below would silently compare nothing. "
            "HOW: pin an answer that says what it stands on."
        )


@pytest.mark.parametrize("named", sorted(_pinned()))
def test_a_verify_request_with_no_descriptor_answers_the_characters_it_did(named):
    """Given a program this tool answered before the obligations of a
    machine existed, when the Owner asks to verify it and sends no
    descriptor, then the answer is character for character the one it
    was, apart from the digest of the tool itself."""
    kept = _pinned()[named]

    answered = induction.ask_to_verify(kept["source"])

    now = _without_what_is_about_the_tool(json.dumps(answered, sort_keys=True))
    before = _without_what_is_about_the_tool(kept["answer_text"])
    assert now == before, (
        f"WHAT: the answer for {named} is no longer the text it was. Before: "
        f"{before[:400]}... Now: {now[:400]}... "
        "WHY: a request that names no machine asks nothing about one, so "
        "nothing about its answer may move -- an Owner comparing an answer "
        "kept from before with one taken now must see no difference, and a "
        "caller that parses the answer must not have to be changed. "
        "HOW: read a descriptor only where the request sent one, and add "
        "nothing to the answer when it did not."
    )


def test_the_same_program_answers_more_only_when_a_descriptor_is_sent():
    """Given the hour clock's machine program, when it is verified with
    no descriptor and then with the one this repository ships for it,
    then the first answer is the text it always was and the second
    carries the three obligations the first does not."""
    pinned = _pinned()["the hour clock's machine program"]
    source, descriptor = induction.shipped_machine("hour-clock")

    without = induction.ask_to_verify(source)
    with_descriptor = induction.ask_to_verify(source, descriptor)

    assert _without_what_is_about_the_tool(
        json.dumps(without, sort_keys=True)
    ) == _without_what_is_about_the_tool(pinned["answer_text"]), (
        "WHAT: the machine program's answer without a descriptor is not the "
        "text it was before this feature. "
        "WHY: the same program must answer the same thing until a machine is "
        "named. HOW: read the descriptor field only when it is sent."
    )
    assert sorted(induction.the_three_obligations(with_descriptor)) == sorted(
        induction.THE_THREE
    ), (
        f"WHAT: sending the descriptor for the same program listed "
        f"{sorted(induction.the_three_obligations(with_descriptor))}. "
        "WHY: the pin must not be kept by answering nothing new; the three "
        "obligations are what the descriptor adds. HOW: list the three."
    )
