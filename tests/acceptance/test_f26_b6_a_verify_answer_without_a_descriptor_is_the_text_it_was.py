"""F26, the promise that nothing else moved -- a verify request that
sends no descriptor is answered with the same characters it was answered
with before the obligations of a machine existed.

The law: adding the three obligations of a machine changes nothing about
an answer to a request that names no machine -- not a word of it, not a
count, not an order, not a byte.

The answers pinned beside this test were taken from the tree as it was
before this feature, through that tree's own build of the `prova`
command, and are compared character for character with what the command
answers now. One field is read apart: `stands_on.dependency_digest` is
the digest of the tool itself, which any change to the tool moves by
design, so the test requires it to be present in both answers and
compares every other character exactly. Had the digest been included,
this test could only ever have said that the tool changed, which the
commit already says.

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

# What the digest of the tool stands under in an answer, read apart
# because a change to the tool moves it by design.
THE_DIGEST_OF_THE_TOOL = "dependency_digest"


def _pinned() -> dict:
    assert PINNED.exists(), (
        f"WHAT: {PINNED.name} is not beside this test. "
        "WHY: the answers this tool gave before the obligations of a machine "
        "existed are the only thing the answers it gives now can be compared "
        "with. HOW: ship the pinned answers beside this test."
    )
    return json.loads(PINNED.read_text(encoding="utf-8"))


def _without_the_digest_of_the_tool(answer_text: str) -> str:
    """`answer_text` with the digest of the tool replaced by one word, so
    that every other character is compared."""
    answer = json.loads(answer_text)
    stands_on = answer.get("stands_on")
    if isinstance(stands_on, dict) and THE_DIGEST_OF_THE_TOOL in stands_on:
        stands_on[THE_DIGEST_OF_THE_TOOL] = "the digest of the tool"
    return json.dumps(answer, sort_keys=True)


def test_the_pinned_answers_are_the_six_taken_before_the_feature():
    """Given the answers pinned beside this test, then there are 6 of
    them, each with the program it is about and the characters the tool
    answered, and each says it is a verify answer."""
    pinned = _pinned()

    assert len(pinned) == 6, (
        f"WHAT: {len(pinned)} answers are pinned, not 6: {sorted(pinned)}. "
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
        assert THE_DIGEST_OF_THE_TOOL in str(kept["answer_text"]) or answered.get(
            "status"
        ) != "completed", (
            f"WHAT: the completed answer pinned for {named!r} names no "
            f"{THE_DIGEST_OF_THE_TOOL}. "
            "WHY: the one field read apart must be there to be read apart; "
            "without it the comparison below would silently compare nothing. "
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

    now = _without_the_digest_of_the_tool(json.dumps(answered, sort_keys=True))
    before = _without_the_digest_of_the_tool(kept["answer_text"])
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

    assert _without_the_digest_of_the_tool(
        json.dumps(without, sort_keys=True)
    ) == _without_the_digest_of_the_tool(pinned["answer_text"]), (
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
