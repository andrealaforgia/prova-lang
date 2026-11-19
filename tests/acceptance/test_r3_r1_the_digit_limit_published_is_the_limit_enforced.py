"""R3 repair -- the interpreter's digit setting changes neither what is
refused wrongly nor what is promised wrongly.

Python reads 0 as "no limit on digits": a caller who sets it disables
the limit, so nothing may be refused for an interpreter limit of 0. A
caller who lowers it below the 4000 digits this tool writes gets the
lowered number as the limit, enforced and published as one number.

still passes if: the discover answer and the refusal carry different
numbers, or a disabled limit refuses a budget.
"""

from __future__ import annotations

import json

from _r3_fixtures import (
    BUDGET_VARIABLE,
    INVALID_INPUT,
    RESOURCE_EXHAUSTED,
    WRITTEN_DIGITS_EXCEEDED,
    answered,
    computing,
    diagnostic_of,
)

LOWERED = "640"


def _product_of_two(digits: int) -> str:
    n = "9" * digits
    return computing(f"(* {n} {n})")


def _evaluate(source: str) -> dict:
    return {"operation": "evaluate", "source": source, "function": "big",
            "arguments": []}


def test_a_disabled_interpreter_limit_does_not_refuse_a_budget_within_the_maximum():
    """Given the interpreter's digit limit disabled with 0, when a caller
    sets the input-size budget to 4096, then the tool answers completed."""
    response = answered(
        {"operation": "discover"}, "discover with the digit limit disabled",
        {"PYTHONINTMAXSTRDIGITS": "0", BUDGET_VARIABLE: "4096"},
    )
    assert response.get("status") == "completed", (
        f"a disabled digit limit with a valid budget was answered "
        f"{str(response)[:300]}: 0 means no limit, so nothing is refused."
    )


def test_a_disabled_limit_refuses_a_budget_past_the_maximum_by_the_ordinary_sentence():
    """Given the digit limit disabled, when the budget is a 5000-digit
    number, then it is refused as above the declared maximum, never as
    too long to be read."""
    response = answered(
        {"operation": "discover"}, "discover, 5000-digit budget, no limit",
        {"PYTHONINTMAXSTRDIGITS": "0", BUDGET_VARIABLE: "9" * 5000},
    )
    assert response.get("status") == INVALID_INPUT, str(response)[:300]
    text = json.dumps(response)
    assert "declares" in text and "characters long" not in text, (
        f"the refusal is {text[:500]}: with no digit limit the number can "
        "be read, so it is refused as above the maximum and not by length."
    )


def test_under_a_lowered_limit_the_published_number_is_the_enforced_one():
    """Given the interpreter limit lowered to 640, when a program computes
    a 700-digit product of two 350-digit literals, then the refusal says
    640, which is the number discover publishes, and the same program
    with a 600-digit result is written exactly."""
    env = {"PYTHONINTMAXSTRDIGITS": LOWERED}
    discovered = answered({"operation": "discover"}, "discover at 640", env)
    text = json.dumps(discovered)
    assert "4000 digits" not in text and "stands below" not in text, (
        "discover still promises 4000 digits while the limit in force is 640."
    )
    assert "PYTHONINTMAXSTRDIGITS" in text and "640" in text, (
        "discover names neither the setting nor the number it produced."
    )

    refused = answered(_evaluate(_product_of_two(350)), "700 digits at 640", env)
    assert refused["status"] == RESOURCE_EXHAUSTED, str(refused)[:300]
    refusal = diagnostic_of(refused, WRITTEN_DIGITS_EXCEEDED, "700 digits")
    assert (refusal.get("expected"), refusal.get("actual")) == (640, 700), refusal

    # 300 digits x 300 digits = 599 or 600 digits: inside 640.
    inside = answered(_evaluate(_product_of_two(300)), "600 digits at 640", env)
    assert inside.get("status") == "completed", str(inside)[:300]
    n = 10**300 - 1
    assert str(n * n) in json.dumps(inside), "the 600-digit result is not exact."
