"""R1.B2 -- a request whose fields hold the wrong kind of JSON value is
refused by the name of the field, not crashed.

A client that builds a request from its own data puts a list where a
name belongs, a number where a list belongs, or sends no object at all.
Every one of those used to end in a traceback with nothing on standard
output, so the client could not tell a broken tool from a broken
request. Each one now comes back naming the field to repair.

still passes if: the tool refused every request. The last test sends the
same requests with every field of the right kind and requires them to be
answered as they are today.
"""

from __future__ import annotations

import pytest

from _r1_robustness_fixtures import (
    INVALID_INPUT,
    MALFORMED_REQUEST,
    SYMBOL,
    UNAVAILABLE,
    UNKNOWN_OPERATION,
    answered,
    assert_accepted,
    categories,
    hour_clock_source,
    the_refusal,
)

# The JSON values a client can put in a field that holds neither a name
# nor a list of them.
NOT_A_NAME = {
    "a list holding the name": ["valid-state"],
    "an object holding the name": {"name": "valid-state"},
    "a whole number": 7,
    "a true/false value": True,
    "nothing at all": None,
}

NOT_A_LIST_OF_TEXTS = {
    "a whole number": 7,
    "one text, not wrapped in a list": "(Clock 1)",
    "an object": {"0": "(Clock 1)"},
    "nothing at all": None,
}

NOT_A_TEXT = {
    "a whole number": 7,
    "a list": ["(Clock 1)"],
    "an object": {"hr": 1},
    "nothing at all": None,
}

NOT_AN_OBJECT = {
    "a list of requests": [{"operation": "discover"}],
    "a bare number": 5,
    "a bare text": "discover",
    "nothing at all": None,
    "a true/false value": False,
}


def _evaluate(**fields) -> dict:
    request = {"prova": "i1", "operation": "evaluate", "source": hour_clock_source()}
    request.update(fields)
    return answered(request, f"an evaluate request carrying {sorted(fields)}")


def _assert_names_the_field(response: dict, field: str, why: str) -> None:
    assert response.get("status") == INVALID_INPUT, (
        f"the tool answered {response.get('status')!r} for {why}: {response}. "
        "The request itself cannot be read, so the answer says the input was "
        "invalid rather than reporting on a program."
    )
    refusal = the_refusal(response, MALFORMED_REQUEST, why)
    assert refusal.get(SYMBOL) == field, (
        f"the refusal for {why} names {refusal.get(SYMBOL)!r}, not {field!r}: "
        f"{refusal}. A client repairs the one field the refusal names; without "
        "the name it has to guess which of its fields the tool could not read."
    )
    assert "result" not in response, (
        f"the answer for {why} carries a result beside its refusal: {response}."
    )


@pytest.mark.parametrize("why", sorted(NOT_A_NAME))
def test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field(why):
    """Given an evaluate request whose `function` holds a list, an
    object, a number, true/false or nothing, when the tool answers it,
    then the answer is invalid input naming `function`.
    """
    response = _evaluate(function=NOT_A_NAME[why], arguments=["(Clock 1)"])

    _assert_names_the_field(response, "function", f"a function field holding {why}")


@pytest.mark.parametrize("why", sorted(NOT_A_LIST_OF_TEXTS))
def test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field(why):
    """Given an evaluate request whose `arguments` is not a list of
    texts, when the tool answers it, then the answer is invalid input
    naming `arguments`.
    """
    response = _evaluate(function="valid-state", arguments=NOT_A_LIST_OF_TEXTS[why])

    _assert_names_the_field(response, "arguments", f"arguments holding {why}")


@pytest.mark.parametrize("why", sorted(NOT_A_TEXT))
def test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list(why):
    """Given an evaluate request whose second argument is not the text
    of a value, when the tool answers it, then the answer is invalid
    input naming that place in the list.
    """
    response = _evaluate(
        function="step", arguments=["(Clock 1)", NOT_A_TEXT[why]]
    )

    _assert_names_the_field(
        response, "arguments[1]", f"a second argument holding {why}"
    )


@pytest.mark.parametrize("why", sorted(NOT_A_NAME))
def test_an_operation_that_is_not_a_name_is_answered_as_one_the_tool_does_not_have(why):
    """Given a request whose `operation` holds a list, an object, a
    number, true/false or nothing, when the tool answers it, then the
    answer says the operation is not one this tool has, the same answer
    a misspelled name gets.
    """
    response = answered(
        {"prova": "i1", "operation": NOT_A_NAME[why], "source": hour_clock_source()},
        f"an operation field holding {why}",
    )

    assert response.get("status") == UNAVAILABLE, (
        f"the tool answered {response.get('status')!r} for an operation holding "
        f"{why}: {response}. Nothing the tool does is named by that value, which "
        "is what a caller asking for an operation the tool does not have is told."
    )
    assert categories(response) == [UNKNOWN_OPERATION], (
        f"the answer for an operation holding {why} carries "
        f"{categories(response)}: {response}. A caller reads one cause, and it "
        "is the same cause a misspelled operation name gets."
    )


@pytest.mark.parametrize("why", sorted(NOT_AN_OBJECT))
def test_a_request_that_is_not_an_object_is_refused_as_the_request(why):
    """Given something that is valid JSON but not an object with fields
    -- a list, a number, a text, true/false or nothing -- when the tool
    answers it, then the answer is invalid input naming the request
    itself.
    """
    response = answered(NOT_AN_OBJECT[why], f"a request that is {why}")

    _assert_names_the_field(response, "request", f"a request that is {why}")


def test_a_request_with_every_field_of_the_right_kind_is_still_answered():
    """Given an evaluate request whose function is a name and whose
    arguments are the texts of values, when the tool answers it, then it
    runs the function and reports its value.
    """
    response = _evaluate(function="step", arguments=["(Clock 11)", "(Tick)"])

    assert_accepted(response, "an evaluate request with every field of the right kind")
    assert response["result"]["value"] == "(Outcome (Clock 12) true)", (
        f"the tool reported {response['result']['value']!r} for the hour clock "
        "stepped from 11, expected '(Outcome (Clock 12) true)': "
        f"{response}. A tool that refuses every request would pass the refusals "
        "above; this is what it must still answer."
    )
