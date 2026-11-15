"""F14.B7 -- a program well inside every budget is answered exactly as
it was before this tool declared any of them.

A budget that changed an answer would be a rule about programs. These
cases pin the answers a caller already gets, beside a twin run of the
same request with every budget lowered, so a tool that refused
everything would not pass either.

still passes if: the tool stopped enforcing the budgets altogether. The
twin at the end requires the lowered run to be refused.
"""

from __future__ import annotations

import json

from _f14_budget_fixtures import (
    ANSWER_SIZE,
    INPUT_SIZE,
    OPERATION_TIME,
    PEAK_MEMORY,
    RESOURCE_EXHAUSTED,
    answered,
    check,
    discover,
    published_budgets,
    shipped_programs,
    within_every_budget,
)

EVALUATE_THE_CLOCK = {
    "prova": "i1",
    "operation": "evaluate",
    "source": within_every_budget(),
    "function": "step",
    "arguments": ["(Clock 11)", "(Tick)"],
}


def test_a_program_inside_every_budget_is_evaluated_and_answered():
    """Given the hour clock, 1474 bytes against a stated input budget of
    1 MiB, when a caller steps it from 11 o'clock, then it completes
    with the clock at 12 and no refusal, as it did before any budget was
    declared.
    """
    budgets = published_budgets(discover())["evaluate"]
    size = len(within_every_budget().encode("utf-8"))
    assert size < budgets[INPUT_SIZE]["maximum"], (
        f"the hour clock is {size} bytes against a stated input budget of "
        f"{budgets[INPUT_SIZE]['maximum']}: this case is meant to run a "
        "program well inside every budget, and it no longer is."
    )

    response = answered(EVALUATE_THE_CLOCK, "a step of the hour clock")

    assert response["status"] == "completed", (
        f"stepping the hour clock from 11 was answered "
        f"{response.get('status')!r}: {response}. The program is far inside "
        "every declared budget, so an answer other than the one it gave "
        "before means a budget became a rule about what may be run."
    )
    assert response["result"]["value"] == "(Outcome (Clock 12) true)", (
        f"stepping the hour clock from 11 gave "
        f"{response['result'].get('value')!r}: {response}. The clock ticks to "
        "12 and the step is accepted; the budget work changes no answer."
    )
    assert response["diagnostics"] == [], (
        f"a run inside every budget carries {response['diagnostics']}: a "
        "caller reads a refusal where there is nothing to refuse."
    )
    answer_size = len(json.dumps(response).encode("utf-8"))
    assert answer_size < budgets[ANSWER_SIZE]["maximum"], (
        f"the answer is {answer_size} bytes against a stated answer budget of "
        f"{budgets[ANSWER_SIZE]['maximum']}: a program inside every budget is "
        "answered inside every budget too."
    )


def test_every_program_this_repository_ships_still_checks():
    """Given the 3 programs this repository ships, when a caller checks
    each of them with nothing lowered, then each is accepted: the
    declared budgets leave room for every program shipped here.
    """
    for name, source in shipped_programs().items():
        response = check(source, name)
        assert response["status"] == "completed", (
            f"{name} was answered {response.get('status')!r} under the "
            f"declared budgets: {str(response)[:400]}. A budget that refuses a "
            "program this repository ships is no longer a budget against a "
            "runaway caller; it is a rule about how people may write."
        )


def test_the_same_step_with_every_budget_lowered_is_refused():
    """Given the same step of the hour clock with all 4 budgets lowered
    to 0 or 1, when the caller runs it, then it is refused inside a
    budget: the run that completes above does so because it fits, not
    because nothing is enforced.
    """
    response = answered(
        EVALUATE_THE_CLOCK,
        "a step of the hour clock with every budget lowered",
        {INPUT_SIZE: 1, OPERATION_TIME: 0, PEAK_MEMORY: 1, ANSWER_SIZE: 1},
    )

    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"a run with every budget lowered to 0 or 1 was answered "
        f"{response.get('status')!r}: {response}. Nothing fits in those "
        "numbers, so a run that completes anyway shows the budgets are "
        "stated and not enforced."
    )
