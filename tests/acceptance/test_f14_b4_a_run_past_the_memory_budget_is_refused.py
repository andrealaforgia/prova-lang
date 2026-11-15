"""F14.B4 -- a run that has taken more memory than its budget allows is
refused for that budget, by name.

A tool that keeps going until the machine refuses it answers nothing at
all, and the caller is left with a killed process and no diagnosis. The
tool watches its own peak and stops first.

still passes if: the tool refused every run. The second test runs the
same request with nothing lowered and requires the normal answer.
"""

from __future__ import annotations

from _f14_budget_fixtures import (
    CATEGORY_OF,
    PEAK_MEMORY,
    RESOURCE_EXHAUSTED,
    assert_claims_nothing,
    assert_names_the_budget,
    check,
    within_every_budget,
)
from _f14_budget_fixtures import the_refusal


def test_a_run_whose_memory_is_already_past_the_budget_is_refused():
    """Given a caller that lowered its memory budget to 1 byte, when it
    checks the hour clock, then the tool stops inside the memory budget,
    names it, and reports 1 byte allowed beside the memory it had
    already taken.
    """
    response = check(
        within_every_budget(), "a run under a 1 byte memory budget", {PEAK_MEMORY: 1}
    )

    why = "a run under a memory budget of 1 byte"
    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: {response}. "
        "A run that has taken more memory than it was given stops inside a "
        "budget of this tool, which says nothing about the program it was "
        "given."
    )
    refusal = the_refusal(response, CATEGORY_OF[PEAK_MEMORY], why)
    assert_names_the_budget(refusal, PEAK_MEMORY, 1, None, why)
    assert_claims_nothing(response, why)


def test_the_same_program_under_the_declared_memory_budget_is_checked():
    """Given the same program with nothing lowered, when a caller checks
    it, then it is accepted, so the memory budget refuses only a run
    that has really taken more than it was given.
    """
    response = check(within_every_budget(), "the hour clock with nothing lowered")

    assert response["status"] == "completed", (
        f"the hour clock was answered {response.get('status')!r} under the "
        f"declared memory budget: {response}. This tool takes a few tens of "
        "megabytes to answer and declares 512 MiB, so a refusal here means "
        "the budget is read from the wrong number or counted in the wrong "
        "unit."
    )
