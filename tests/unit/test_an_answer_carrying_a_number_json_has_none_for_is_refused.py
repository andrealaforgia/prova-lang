"""The last place an answer becomes the characters a caller reads
refuses to print a number JSON has no number for.

Every number a request carries is already refused by the rule that
reads the request, so this stands behind it: if infinity, or a number
that is no number, ever reached an answer -- computed inside this tool
rather than sent to it -- a client reading the answer with any reader
holding to JSON would get no outcome at all, because `Infinity` and
`NaN` are not JSON. No request the command accepts reaches it, so the
answers below are built by hand.
"""

from __future__ import annotations

import json

import pytest

from prova import service

NOT_A_JSON_NUMBER = (float("inf"), float("-inf"), float("nan"))


def _strictly(printed: str) -> dict:
    def refuse(constant: str) -> object:
        raise AssertionError(
            f"the tool printed {constant} inside {printed[:200]!r}: a reader "
            "holding to JSON reads no outcome from that text at all."
        )

    return json.loads(printed, parse_constant=refuse)


@pytest.mark.parametrize("number", NOT_A_JSON_NUMBER)
def test_an_answer_holding_such_a_number_is_refused_before_it_is_printed(number):
    printed = service.printable_answer(
        {
            "operation": "check",
            "status": "completed",
            "diagnostics": [],
            "result": {"value": number},
        }
    )

    answer = _strictly(printed)
    assert answer["status"] == "invalid_input", printed
    assert answer["diagnostics"][0]["category"] == "malformed_request", answer
    assert "result" not in answer, answer


def test_the_refusal_does_not_repeat_the_number_it_refused():
    printed = service.printable_answer(
        {"operation": "check", "status": "completed", "result": float("nan")}
    )

    for token in ("NaN", "Infinity", "nan", "1e999"):
        assert token not in printed, (token, printed)
    _strictly(printed)


def test_an_answer_whose_numbers_are_finite_is_written_exactly_as_json():
    answer = {
        "operation": "evaluate",
        "status": "completed",
        "diagnostics": [],
        "result": {"value": "7", "measured": 0.5, "counted": 10**30},
    }

    assert json.loads(service.printable_answer(answer)) == answer, answer
