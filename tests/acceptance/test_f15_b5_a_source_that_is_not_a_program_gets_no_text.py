"""F15.B5 -- a source the tool does not accept is refused, and the
refusal carries no text at all.

Text beside a refusal would read as a program the tool understood and
tidied, and an agent would write that text to a file. So the refusal
carries the reason and nothing else -- exactly as the operations that
already read a source refuse.

still passes if: the tool had refused every source, accepted or not.
F15.B1 and F15.B4 state that accepted programs are answered with their
text, so a tool that refuses everything fails there.
"""

from __future__ import annotations

import pytest

from _f15_format_fixtures import ask_to_check, ask_to_format

# Four sources the tool does not accept, one per reason it can give: a
# text that stops partway, a text with no declaration in it, a program
# that breaks a rule of core-0, and a program using a construct core-0
# does not have.
REFUSED_SOURCES = {
    "a text that stops after 1 unclosed parenthesis": "(defn add-one",
    "a text holding no declaration at all": "",
    "a program adding a number to true": (
        "(defn add-one\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (add-one 1) => 2))\n"
        "  (+ n true))\n"
    ),
    "a program dividing, which core-0 has no operator for": (
        "(defn halve\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (halve 4) => 2))\n"
        "  (/ n 2))\n"
    ),
}


@pytest.mark.parametrize("described", sorted(REFUSED_SOURCES))
def test_a_source_the_tool_refuses_is_answered_without_any_text(described):
    source = REFUSED_SOURCES[described]

    answered = ask_to_format(source)

    assert answered["operation"] == "format", answered
    assert answered["status"] != "completed", (
        f"{described} was answered 'completed': {answered}. A text the tool "
        "cannot read as a core-0 program has no canonical spelling; refuse "
        "it and say which rule it breaks"
    )
    assert "result" not in answered, (
        f"{described} was refused and the refusal still carried "
        f"{answered.get('result')!r}: an agent reading it would write that "
        "text to a file as though the program had been understood; carry the "
        "reason and nothing else"
    )
    assert answered.get("diagnostics"), (
        f"{described} was refused with no diagnostic saying why: {answered}. "
        "A reader is owed the rule that was broken and the place it stands at"
    )


@pytest.mark.parametrize("described", sorted(REFUSED_SOURCES))
def test_a_refusal_says_what_a_check_of_the_same_source_says(described):
    source = REFUSED_SOURCES[described]

    refused = ask_to_format(source)
    checked = ask_to_check(source)

    assert refused["status"] == checked["status"], (
        f"{described} was refused {refused['status']!r} by formatting and "
        f"{checked['status']!r} by checking. One source gets one answer "
        "about why it is not a program; a reader moving between operations "
        "must not meet two"
    )
    assert refused["diagnostics"] == checked["diagnostics"], (
        f"{described} was refused with\n{refused['diagnostics']}\nby "
        f"formatting and\n{checked['diagnostics']}\nby checking. The reason a "
        "source is not a program does not depend on what was asked about it"
    )
