"""F14.B8 -- a caller lowers a budget for one run the way the manifest
says, and anything else it writes is refused by name.

A caller that believes it lowered a budget and did not would read a run
that completed as proof that the work fits. So a name this tool does not
publish, a value that is not a whole number, and a value above the
number the tool declares are each refused by name rather than ignored.

still passes if: the tool refused every run with any of these variables
set. The first test lowers a budget the published way and requires the
run to be answered by that budget, not by a complaint about the
variable.
"""

from __future__ import annotations

import pytest

from _f14_budget_fixtures import (
    CATEGORY_OF,
    DECLARED,
    INPUT_SIZE,
    INVALID_INPUT,
    OPERATION_TIME,
    RESOURCE_EXHAUSTED,
    discover,
    run,
    run_with_environment,
    source_of_exactly,
    the_refusal,
    variable_for,
    within_every_budget,
)

CHECK_THE_CLOCK = {
    "prova": "i1",
    "operation": "check",
    "source": within_every_budget(),
}

# What a caller writes by mistake: the variable it wrote it in, the text
# it wrote, and what the refusal must quote back -- the value when the
# value is at fault, the name when the name is.
MISTAKES = {
    "a value that is not a whole number": (
        variable_for(OPERATION_TIME), "ten", "'ten'",
    ),
    "a value with nothing in it": (variable_for(OPERATION_TIME), "", "''"),
    "a negative value": (variable_for(OPERATION_TIME), "-1", "'-1'"),
    "a value above the number this tool declares": (
        variable_for(OPERATION_TIME),
        str(DECLARED[OPERATION_TIME] + 1),
        str(DECLARED[OPERATION_TIME] + 1),
    ),
    "a budget name this tool does not publish": (
        "PROVA_BUDGET_DISK_SIZE", "5", "PROVA_BUDGET_DISK_SIZE",
    ),
}


def test_the_published_way_to_lower_a_budget_is_the_way_that_works():
    """Given the name the manifest publishes for lowering the input
    budget, when a caller sets it to 50 and sends a source of 300 bytes,
    then the run is refused for the input budget with 50 allowed: the
    published name is the one the tool reads.
    """
    manifest = discover()
    entry = manifest["result"]["resource_limits"]["budgets"]["check"][INPUT_SIZE]
    published_name = entry["lower_with"]

    answer = run_with_environment(
        {"prova": "i1", "operation": "check", "source": source_of_exactly(300)},
        {published_name: "50"},
    )
    response = answer.assert_answered("a budget lowered by its published name")

    why = f"an input budget lowered to 50 with {published_name}"
    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: {response}. "
        "The name the manifest publishes is the name the tool reads; a caller "
        "that followed the manifest and changed nothing has been misled."
    )
    refusal = the_refusal(response, CATEGORY_OF[INPUT_SIZE], why)
    assert refusal.get("expected") == 50, (
        f"the refusal reports {refusal.get('expected')!r} allowed against the "
        f"50 the caller set with {published_name}: {refusal}."
    )


@pytest.mark.parametrize("mistake", sorted(MISTAKES))
def test_a_budget_a_caller_cannot_set_is_refused_by_name(mistake):
    """Given a caller that wrote a budget this tool cannot read -- a
    name it does not publish, a value that is not a whole number, a
    negative value, or a value above the number it declares -- when it
    sends a request, then the tool refuses by naming the variable
    instead of running as if nothing had been asked.
    """
    variable, written, quoted_back = MISTAKES[mistake]

    answer = run_with_environment(CHECK_THE_CLOCK, {variable: written})
    response = answer.assert_answered(mistake)

    assert response["status"] == INVALID_INPUT, (
        f"the tool answered {response.get('status')!r} for {mistake} "
        f"({variable}={written!r}): {response}. A caller that believes it "
        "lowered a budget and did not reads the run that follows as proof "
        "that its work fits."
    )
    refusal = the_refusal(response, "malformed_request", mistake)
    assert refusal.get("symbol") == variable, (
        f"the refusal for {mistake} names {refusal.get('symbol')!r}, not "
        f"{variable!r}: {refusal}. A caller is sent to the one variable it "
        "must repair."
    )
    assert quoted_back in refusal.get("reason", ""), (
        f"the refusal for {mistake} does not quote back {quoted_back!r}: "
        f"{refusal.get('reason')!r}. A caller reads what the tool saw at "
        "fault -- the value it wrote, or the name it wrote it under -- so it "
        "can tell a typing mistake from a disagreement about the number."
    )
    assert "result" not in response, (
        f"the answer to {mistake} carries a result: {response}. The tool "
        "never ran the request, so it has nothing to report about it."
    )
