"""F14.B3 -- when a run passes the time budget, the caller gets a budget
answer: not half an answer, and not a command that never comes back.

The tool stops where it stands and says which budget stopped it. What it
had done so far is not reported, because a half-run operation has
nothing a caller may rely on.

still passes if: the tool refused every run. The second test sends the
same request with nothing lowered and requires the four declared
examples of the hour clock to be run and answered.
"""

from __future__ import annotations

from _f14_budget_fixtures import (
    CATEGORY_OF,
    OPERATION_TIME,
    RESOURCE_EXHAUSTED,
    answered,
    assert_claims_nothing,
    assert_names_the_budget,
    the_refusal,
    within_every_budget,
)


def _examples_request() -> dict:
    return {
        "prova": "i1",
        "operation": "examples",
        "source": within_every_budget(),
    }


def test_a_run_with_no_time_left_is_answered_with_the_time_budget():
    """Given a caller that lowered its time budget to 0 milliseconds,
    when it asks the tool to run the hour clock's examples, then the
    answer is the time budget, named, with no list of examples in it and
    no wait for one.
    """
    response = answered(
        _examples_request(), "a run with no time left", {OPERATION_TIME: 0}
    )

    why = "a run under a time budget of 0 milliseconds"
    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: {response}. "
        "A run that ran out of the time this tool gives it stops inside a "
        "budget; any other status tells a caller something about the program "
        "that was never checked."
    )
    refusal = the_refusal(response, CATEGORY_OF[OPERATION_TIME], why)
    assert_names_the_budget(refusal, OPERATION_TIME, 0, None, why)
    assert_claims_nothing(response, why)


def test_the_same_run_with_the_time_it_needs_answers_every_example():
    """Given the same request with nothing lowered, when the tool runs
    it, then the hour clock's 8 declared examples are all run and
    answered, so the budget refuses only a run that has no time left.
    """
    response = answered(_examples_request(), "the same run with its full budget")

    assert response["status"] == "completed", (
        f"the hour clock's examples were answered {response.get('status')!r} "
        f"with nothing lowered: {response}. Every shipped program runs far "
        "inside the declared time budget; a tool that refuses one has made "
        "its budget a rule about what may be run."
    )
    ran = response["result"]["examples"]
    assert len(ran) == 8 and all(entry["passed"] for entry in ran), (
        f"{sum(1 for e in ran if e.get('passed'))} of {len(ran)} declared "
        f"examples of the hour clock passed: {ran}. All 8 pass today, and the "
        "budget work must leave that answer exactly as it was."
    )
