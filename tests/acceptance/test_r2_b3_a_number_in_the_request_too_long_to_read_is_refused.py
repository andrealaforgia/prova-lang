"""R2.B3 -- a number written in the request itself, too long for the
reader that reads the request, is answered as a request this tool
cannot read.

The digits of a program's own literals are refused where they stand in
the source. A number written as a JSON number in the request, beside
the source rather than inside it, never reaches that refusal: the
command reads its request with a JSON reader that turns every number in
the text into a number, and that reader stopped the run with a
traceback and nothing on standard output.

still passes if: the command refused every request carrying a number,
or refused for the wrong reason. The control below sends the same
request with a short number and requires the answer to be exactly the
answer the request gets without the number at all.
"""

from __future__ import annotations

import json

from _r1_robustness_fixtures import (
    INVALID_INPUT,
    MALFORMED_REQUEST,
    SYMBOL,
    run_text,
    the_refusal,
)

# Longer than the 4300 digits the interpreter reads as one number.
PAST_EVERY_LIMIT = 4301


def _digits(length: int) -> str:
    return "9" * length


def _request_carrying(number: str, nested: bool = False) -> str:
    """The text of a request whose own JSON carries `number` beside the
    source, as a number and not as text."""
    if nested:
        return '{"operation":"check","source":"x","deep":{"n":' + number + "}}"
    return '{"operation":"check","source":"x","n":' + number + "}"


def _refused(sent: str, why: str) -> dict:
    response = run_text(sent).assert_answered(why)

    assert response["status"] == INVALID_INPUT, (
        f"{why} was answered {response['status']!r}: {str(response)[:300]}. A "
        "request this tool cannot read as a request is answered as invalid "
        "input, by the command that read it."
    )
    refusal = the_refusal(response, MALFORMED_REQUEST, why)
    assert refusal.get(SYMBOL) == "request", (
        f"the refusal for {why} names {refusal.get(SYMBOL)!r}: {refusal}. "
        "Nothing of the request was read, so the refusal is about the request "
        "and not about one of its fields."
    )
    assert "digits" in refusal["reason"], (
        f"the refusal for {why} does not say that a number is too long: "
        f"{refusal['reason']!r}. A client that wrote one long number in a "
        "request of many fields has nothing to repair without it."
    )
    return refusal


def test_a_number_of_4301_digits_beside_the_source_is_answered_not_raised():
    """Given the request text {"operation":"check","source":"x","n":<4301
    digits>}, when it is sent to the prova command, then the command
    answers invalid_input with one malformed_request about the request,
    exits 0 and writes nothing on standard error.
    """
    _refused(
        _request_carrying(_digits(PAST_EVERY_LIMIT)),
        "a request carrying a number of 4301 digits",
    )


def test_the_same_number_nested_deeper_in_the_request_is_answered_too():
    """Given the same number inside an object inside the request, when
    it is sent, then it is answered the same way: the reader reads the
    whole text, so every number in it is one the command must answer
    for.
    """
    _refused(
        _request_carrying(_digits(PAST_EVERY_LIMIT), nested=True),
        "a request carrying a number of 4301 digits one object deep",
    )


def test_a_request_carrying_a_short_number_is_answered_exactly_as_before():
    """Given the same request with a 10-digit number, and the same
    request with no number at all, when both are sent, then both get the
    same answer: the refusal above is about the length of the number and
    about nothing else.
    """
    with_number = run_text(_request_carrying(_digits(10))).assert_answered(
        "a request carrying a number of 10 digits"
    )
    without_number = run_text('{"operation":"check","source":"x"}').assert_answered(
        "the same request with no number in it"
    )

    assert with_number == without_number, (
        "a request carrying a short number was answered "
        f"{json.dumps(with_number)[:200]} and the same request without it "
        f"{json.dumps(without_number)[:200]}. A field this tool does not read "
        "changes no answer."
    )
    assert without_number["status"] != INVALID_INPUT, without_number
