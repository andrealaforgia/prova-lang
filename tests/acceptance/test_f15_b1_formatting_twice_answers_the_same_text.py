"""F15.B1 -- an accepted program is answered with canonical text, and
formatting that text again answers exactly the same bytes.

The Owner's outcome is that one program has one spelling: whichever way
a reader wrote it, asking for the canonical text twice gives the same
characters, so two agents never disagree about how a program is written.

still passes if: the tool answered the submitted text unchanged. The
second assertion below therefore also states that a text written on one
line comes back written on several, so an answer that simply echoes the
request fails.
"""

from __future__ import annotations

from _f15_format_fixtures import ask_to_format, canonical_text

# One accepted program, written on a single line with runs of spaces:
# a spelling no reader would choose and the tool must still accept.
WRITTEN_ON_ONE_LINE = (
    "(defn add-one   (sig ((n Int)) -> Int ! pure)   "
    "(ensures (= result (+ n 1)))   "
    "(examples (example (add-one 41) => 42))   (+ n 1))"
)


def test_the_canonical_text_is_what_formatting_it_again_answers():
    answered = ask_to_format(WRITTEN_ON_ONE_LINE)

    assert answered["status"] == "completed", (
        f"formatting an accepted program answered {answered['status']!r} and "
        f"not 'completed': {answered}. A program the tool accepts has a "
        "canonical spelling; answer it, or say which rule of core-0 the "
        "program breaks"
    )
    once = canonical_text(answered)
    assert isinstance(once, str) and once, (
        f"the answer carried no canonical text: {answered}. The Owner asked "
        "for the text, so a completed answer must carry it under 'result'"
    )

    twice = canonical_text(ask_to_format(once))
    assert twice == once, (
        "formatting the canonical text answered different characters:\n"
        f"first:\n{once!r}\nsecond:\n{twice!r}\nThe canonical text of a "
        "program is one text, so formatting it again must change nothing; "
        "make the layout a function of the tree alone"
    )


def test_a_program_written_on_one_line_comes_back_written_on_several():
    once = canonical_text(ask_to_format(WRITTEN_ON_ONE_LINE))

    assert once != WRITTEN_ON_ONE_LINE, (
        "the answer repeated the submitted text character for character, so "
        "nothing says a layout was applied at all; write the program the one "
        "canonical way instead of echoing what was sent"
    )
    assert len(once.splitlines()) >= 5, (
        f"the canonical text of a function with a signature, a postcondition, "
        f"an examples clause and a body is {len(once.splitlines())} line(s):\n"
        f"{once}\nA reader must be able to open the line a part of the "
        "program stands on; write each clause of a function on its own line"
    )
    assert once.endswith("\n") and not once.endswith("\n\n"), (
        f"the canonical text ends {once[-3:]!r}: a text with no final line "
        "terminator, or with more than one, is a second spelling of the same "
        "program; end it with exactly one line terminator"
    )
