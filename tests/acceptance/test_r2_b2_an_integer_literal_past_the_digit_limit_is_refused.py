"""R2.B2 -- an integer literal written with more digits than this tool
reads is refused where it stands, naming the limit, instead of ending in
an error of the interpreter.

A generator that wrote a number as a long run of digits used to drive
the tool into the interpreter's own refusal to turn such a run into a
number: the tool exited 1 with `ValueError: Exceeds the limit (4300
digits)` and nothing on standard output. The tool now declares a limit
of its own, far below that one, refuses the literal at the line and
column it stands at, and says how long the literal is and how long a
literal it reads.

still passes if: the tool refused every program, or refused every
number, or echoed the whole run of digits back into its answer. The
tests below send a literal of exactly the limit and require it to be
answered and kept exact, and require the refusal to carry the two
lengths without the digits themselves.
"""

from __future__ import annotations

import json

from _r1_robustness_fixtures import (
    INVALID_INPUT,
    INVALID_PROGRAM,
    answered,
    assert_accepted,
    assert_located,
    discover,
    hour_clock_source,
    the_refusal,
)

# The longest run of digits this tool reads as one integer literal. The
# promise is this number: a literal of exactly this length is answered,
# and a longer one is refused.
DIGIT_LIMIT = 1000

# A length past both this tool's limit and the interpreter's own 4300.
PAST_EVERY_LIMIT = 4301

SYNTAX = "syntax"
MALFORMED_VALUE = "malformed_value"

SOURCE_READING_OPERATIONS = ("check", "examples", "verify", "parse", "evaluate")


def _digits(length: int) -> str:
    """A run of `length` digits, every one of them significant."""
    return "9" * length


def _program_returning(literal: str, expecting: str = "1") -> str:
    """A program whose body writes `literal` on its fourth line.

    The example on the third line expects something else by default, so
    that the only long run of digits in the text is the one on line 4
    and a refusal that names another line names the wrong one.
    """
    return (
        "(defn big\n"
        "  (sig () -> Int ! pure)\n"
        f"  (examples (example (big) => {expecting}))\n"
        f"  {literal})\n"
    )


def test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact():
    """Given a program whose body writes a 4301-digit integer literal,
    when it is checked, then the answer refuses it as invalid_program
    with one syntax refusal, carrying the line and column the literal
    stands at and naming the 1000 digits this tool reads -- and the same
    program written with exactly 1000 digits is still answered, its
    example still passes and the value it answers is the same 1000
    digits, so the refusal is about the length and about nothing else.
    """
    literal = _digits(PAST_EVERY_LIMIT)
    why = "a program writing a 4301-digit literal"

    response = answered(
        {"prova": "i1", "operation": "check", "source": _program_returning(literal)},
        why,
    )

    assert response["status"] == INVALID_PROGRAM, (
        f"a 4301-digit literal was answered {response['status']!r}: "
        f"{str(response)[:400]}. The tool reads shorter literals, so this one "
        "is refused about the text that was sent."
    )
    refusal = the_refusal(response, SYNTAX, why)
    line, column = assert_located(refusal, why)
    assert line == 4, (
        f"the refusal stands at line {line}, and the literal that is too long "
        f"stands on line 4 of the program: {refusal}. A reader of the refusal "
        "opens the line it names."
    )
    reason = refusal["reason"]
    assert str(DIGIT_LIMIT) in reason and str(PAST_EVERY_LIMIT) in reason, (
        f"the refusal says neither how long the literal is nor how long a "
        f"literal this tool reads: {reason!r}. A caller that must shorten its "
        "number needs both numbers."
    )
    assert literal not in json.dumps(response), (
        "the answer carries the whole run of 4301 digits back to the caller: "
        "a refusal about a text too long to read is not a place to repeat it."
    )

    _assert_the_longest_literal_is_still_answered_exactly()


def test_every_operation_that_reads_source_refuses_the_same_literal():
    """Given the same 4301-digit literal, when each operation that reads
    source is asked, then each refuses it rather than ending in a
    traceback, and none of them answers completed.
    """
    source = _program_returning(_digits(PAST_EVERY_LIMIT))
    for operation in SOURCE_READING_OPERATIONS:
        why = f"{operation} over a program writing a 4301-digit literal"
        response = answered(
            {
                "prova": "i1",
                "operation": operation,
                "source": source,
                "function": "big",
                "arguments": [],
            },
            why,
        )
        assert response["status"] != "completed", (
            f"{why} was answered completed: {str(response)[:300]}. The tool "
            "never read the literal, so it has nothing to report about the "
            "program."
        )
        assert_located(the_refusal(response, SYNTAX, why), why)


def test_a_literal_too_long_in_an_argument_is_refused_where_it_stands():
    """Given an evaluate request whose argument is a 4301-digit run of
    digits, when it is sent, then the answer refuses that argument as
    invalid input, says where in the argument the refusal stands and
    names the limit.
    """
    why = "an argument written as 4301 digits"
    response = answered(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": hour_clock_source(),
            "function": "valid-state",
            "arguments": [_digits(PAST_EVERY_LIMIT)],
        },
        why,
    )

    assert response["status"] == INVALID_INPUT, (
        f"{why} was answered {response['status']!r}: {str(response)[:300]}."
    )
    refusal = the_refusal(response, MALFORMED_VALUE, why)
    assert_located(refusal, why)
    assert str(DIGIT_LIMIT) in refusal["reason"], refusal


def _assert_the_longest_literal_is_still_answered_exactly() -> None:
    """A program whose body writes an integer of exactly 1000 digits is
    answered completed by check, its example passes when the examples
    are run, and evaluating it answers the same 1000 digits: a number
    far past 64 bits is kept exactly.
    """
    literal = _digits(DIGIT_LIMIT)
    source = _program_returning(literal, expecting=literal)

    assert_accepted(
        answered({"prova": "i1", "operation": "check", "source": source}, "a literal of exactly 1000 digits"),
        "a literal of exactly 1000 digits",
    )

    ran = assert_accepted(
        answered({"prova": "i1", "operation": "examples", "source": source}, "the examples of that program"),
        "the examples of that program",
    )
    examples = ran["result"]["examples"]
    assert len(examples) == 1 and examples[0]["passed"] is True, examples
    assert examples[0]["actual"] == literal, (
        f"the example answered {str(examples[0]['actual'])[:60]}...: a literal "
        "inside the limit is kept exactly, digit for digit."
    )

    evaluated = assert_accepted(
        answered(
            {
                "prova": "i1",
                "operation": "evaluate",
                "source": source,
                "function": "big",
                "arguments": [],
            },
            "evaluating that program",
        ),
        "evaluating that program",
    )
    assert evaluated["result"]["value"] == literal, (
        f"evaluating answered {str(evaluated['result']['value'])[:60]}...: an "
        "integer below the limit is answered exactly however large it is."
    )


def test_the_manifest_says_how_long_a_literal_this_tool_reads():
    """Given a caller reading the manifest before it writes a program,
    when it looks for what the tool says about integer literals, then it
    finds the number of digits the tool reads, so the limit is learned
    without meeting it.
    """
    said = discover()["result"]["documentation"]

    assert "integer_literals" in said, (
        f"the manifest says nothing about integer literals: {sorted(said)}. A "
        "generator that writes numbers has no length to stay under, so it "
        "learns the limit by being refused."
    )
    assert str(DIGIT_LIMIT) in said["integer_literals"], said["integer_literals"]
