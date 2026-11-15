"""R2.B1 -- a request carrying a character that cannot be written as
UTF-8 is refused by name and by position, not left to end in a
traceback.

A client that built its request from text it had already decoded badly
sends a lone surrogate: half of a character, which no UTF-8 writer can
write. The tool used to take the revision of such a source by hashing
its bytes, find there are none, and exit 1 with a traceback and nothing
on standard output. It now refuses the field by name, says which
character position cannot be written, and exits 0.

still passes if: the tool refused every request, or always said the
defect stands at position 0, or named the field 'request' whatever was
wrong. The control below sends the same request without the surrogate
and requires it to be answered as before; one case puts the surrogate
five characters in and requires the position to say so; the arguments
case requires the name of the element, not of the request.
"""

from __future__ import annotations

from _r1_robustness_fixtures import (
    INVALID_INPUT,
    MALFORMED_REQUEST,
    RESOURCE_EXHAUSTED,
    SYMBOL,
    answered,
    assert_accepted,
    hour_clock_source,
    the_refusal,
)

# Half of a character: the low half of a surrogate pair, standing alone.
# A JSON text can write it, and no UTF-8 writer can write it out again.
LONE_SURROGATE = "\udccc"

# The operations that read a program from the source field. Every one of
# them is answered about the bytes of that field, so every one of them
# must refuse a field that has none.
SOURCE_READING_OPERATIONS = ("check", "examples", "verify", "parse", "evaluate")


def _refused_source(request: object, why: str, at_position: int) -> dict:
    response = answered(request, why)

    assert response["status"] == INVALID_INPUT, (
        f"the answer for {why} says {response['status']!r}: {response}. A "
        "field this tool cannot read is a request the client built wrongly, "
        "answered as invalid input."
    )
    refusal = the_refusal(response, MALFORMED_REQUEST, why)
    assert refusal.get(SYMBOL) == "source", (
        f"the refusal for {why} names {refusal.get(SYMBOL)!r}: {refusal}. A "
        "client repairs the field the refusal names; a refusal that names "
        "another field, or none, sends it to the wrong place."
    )
    assert f"position {at_position}" in refusal.get("reason", ""), (
        f"the refusal for {why} does not say that the character at position "
        f"{at_position} is the one that cannot be written: "
        f"{refusal.get('reason')!r}. A client that sent a long source cannot "
        "find half a character by reading it; the refusal says where it is."
    )
    return refusal


def test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it():
    """Given a request whose source holds a lone surrogate, when each
    operation that reads source is asked, then each answers invalid_input
    with one malformed_request naming the source field and the character
    position, and the tool exits 0 with nothing on standard error.
    """
    for operation in SOURCE_READING_OPERATIONS:
        _refused_source(
            {
                "prova": "i1",
                "operation": operation,
                "source": LONE_SURROGATE,
                "function": "step",
                "arguments": [],
            },
            f"{operation} over a source that is one lone surrogate",
            at_position=0,
        )


def test_the_refusal_says_where_the_character_that_cannot_be_written_stands():
    """Given a source whose sixth character is a lone surrogate, when it
    is checked, then the refusal says position 5, not position 0.
    """
    refusal = _refused_source(
        {"prova": "i1", "operation": "check", "source": "(defn" + LONE_SURROGATE},
        "a source whose sixth character cannot be written",
        at_position=5,
    )
    assert "UTF-8" in refusal["reason"], (
        f"the refusal does not say what the character cannot be written as: "
        f"{refusal['reason']!r}. A client that reads only that its text is "
        "wrong has nothing to repair."
    )


def test_an_argument_that_cannot_be_written_as_utf8_names_that_argument():
    """Given an evaluate request whose second argument holds a lone
    surrogate, when it is sent, then the answer names arguments[1] and
    the character position inside it, not the source.
    """
    response = answered(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": hour_clock_source(),
            "function": "step",
            "arguments": ["(Clock 1)", LONE_SURROGATE],
        },
        "an argument that cannot be written as UTF-8",
    )

    assert response["status"] == INVALID_INPUT, response
    refusal = the_refusal(
        response, MALFORMED_REQUEST, "an argument that cannot be written as UTF-8"
    )
    assert refusal.get(SYMBOL) == "arguments[1]", (
        f"the refusal names {refusal.get(SYMBOL)!r}: {refusal}. The client "
        "sent two arguments and must learn which of them to repair."
    )
    assert "position 0" in refusal.get("reason", ""), refusal


def test_a_request_whose_function_cannot_be_written_as_utf8_names_the_function():
    """Given an evaluate request whose function name holds a lone
    surrogate, when it is sent, then the answer names the function field.
    """
    response = answered(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": hour_clock_source(),
            "function": LONE_SURROGATE,
            "arguments": [],
        },
        "a function name that cannot be written as UTF-8",
    )

    assert response["status"] == INVALID_INPUT, response
    refusal = the_refusal(
        response, MALFORMED_REQUEST, "a function name that cannot be written"
    )
    assert refusal.get(SYMBOL) == "function", refusal


def test_a_source_large_enough_to_be_sized_still_answers_when_it_holds_one():
    """Given a source long enough that the tool measures its size in
    bytes before reading it, and holding a lone surrogate, when it is
    checked, then the tool still answers with one JSON response rather
    than failing inside the measurement.
    """
    long_source = "x" * 100_000 + LONE_SURROGATE
    response = answered(
        {"prova": "i1", "operation": "check", "source": long_source},
        "a source of 100001 characters holding a lone surrogate",
    )

    assert response["status"] in (INVALID_INPUT, RESOURCE_EXHAUSTED), (
        f"a long source holding a lone surrogate was answered "
        f"{response['status']!r}: {response}. It is either refused as a field "
        "this tool cannot read or refused against a budget; it is never read "
        "as a program."
    )


def test_the_same_requests_without_the_surrogate_are_answered_as_before():
    """Given the shipped hour clock and a well formed evaluate request,
    when each is sent, then each is still answered completed: the refusal
    above is about the half character and about nothing else.
    """
    assert_accepted(
        answered(
            {"prova": "i1", "operation": "check", "source": hour_clock_source()},
            "the hour clock, untouched",
        ),
        "the hour clock, untouched",
    )
    assert_accepted(
        answered(
            {
                "prova": "i1",
                "operation": "evaluate",
                "source": hour_clock_source(),
                "function": "step",
                "arguments": ["(Clock 1)", "(Tick)"],
            },
            "an evaluate request whose fields are all writable text",
        ),
        "an evaluate request whose fields are all writable text",
    )
