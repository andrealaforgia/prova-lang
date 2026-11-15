"""F15.B3 -- a whole number written `+002` comes back written `2`, and
the program goes on meaning what it meant.

SPEC.md lines 76-78 say `+002`, `2` and `0002` denote the same integer
and that a canonical integer carries no leading plus and no redundant
zero. A reader who writes one of the other spellings is accepted, and is
answered the one spelling the tool writes.

still passes if: the tool had replaced every number with 0. The second
test runs the program's own examples over the canonical text and over
the source and compares what each answered, so a changed number fails.
"""

from __future__ import annotations

from _f15_format_fixtures import (
    ask_for_the_examples,
    ask_to_format,
    canonical_text,
    example_results,
)

# Every non-canonical spelling of a whole number core-0 accepts: a
# leading plus, leading zeros, both at once, the negative zero SPEC.md
# line 78 says denotes zero, and a negative number written with both.
# The negative one is in the body, where it decides what the function
# answers: a tool that wrote a number's size and dropped its sign would
# be caught by the second test below and by nothing else.
SPELLED_UNCANONICALLY = """(defn shift
  (sig ((n Int)) -> Int ! pure)
  (ensures (>= result -0))
  (examples (example (shift +0007) => 0009))
  (+ n (+ +005 -0003)))
"""


def test_a_leading_plus_and_a_leading_zero_are_written_away():
    canonical = canonical_text(ask_to_format(SPELLED_UNCANONICALLY))

    assert isinstance(canonical, str), (
        f"a program spelling its numbers '+0007' and '-0003' was not answered "
        f"with text: {ask_to_format(SPELLED_UNCANONICALLY)}. SPEC.md line 82 "
        "says non-canonical spelling is accepted"
    )
    for written in ("+0007", "0009", "+005", "-0003", "-0", "+0", "007"):
        assert written not in canonical, (
            f"the canonical text still writes {written!r}:\n{canonical}\n"
            "SPEC.md line 78 says a canonical integer carries no leading plus "
            "and no redundant zero, so two readers would still write one "
            "number two ways; write the number itself"
        )
    for expected in ("7", "9", "5", "-3", "0"):
        assert expected in canonical, (
            f"the canonical text writes no {expected!r}:\n{canonical}\nThe "
            "number the reader meant must still be there; write the "
            "canonical spelling of the same integer, never a different one"
        )


def test_the_program_answers_what_it_answered_before():
    canonical = canonical_text(ask_to_format(SPELLED_UNCANONICALLY))

    before = ask_for_the_examples(SPELLED_UNCANONICALLY)
    after = ask_for_the_examples(canonical)

    assert after["status"] == before["status"] == "completed", (
        f"running the examples answered {before['status']!r} for the source "
        f"and {after['status']!r} for its canonical text. Writing a number "
        "the canonical way changes no meaning, so both must be answered"
    )
    assert example_results(after) == example_results(before), (
        f"the examples answered\n{example_results(before)}\nfor the source "
        f"and\n{example_results(after)}\nfor its canonical text:\n{canonical}\n"
        "SPEC.md line 82 says formatting preserves meaning; a changed "
        "answer means a changed program"
    )
