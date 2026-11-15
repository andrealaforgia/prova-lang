"""F14.B6 -- whichever budget stopped a run, the answer reports the
budget and nothing about the program.

A budget says how much work this tool does. It never says what a program
means, what it may compute, or that anything about it was checked. An
answer that carried a claim, a result or a digest of the source beside a
budget refusal would say the tool had read the program through.

still passes if: the tool answered an empty refusal with no category at
all. Each case below first requires the refusal that names its own
budget, and only then requires the answer to carry nothing else.
"""

from __future__ import annotations

import pytest

from _f14_budget_fixtures import (
    ANSWER_SIZE,
    BUDGET_NAMES,
    CATEGORY_OF,
    INPUT_SIZE,
    OPERATION_TIME,
    PEAK_MEMORY,
    RESOURCE_EXHAUSTED,
    assert_claims_nothing,
    run,
    source_of_exactly,
    the_refusal,
    within_every_budget,
)

# One run per budget, each one chosen so that exactly that budget is the
# one it passes: a request, and the budget the caller lowered.
RUNS_PAST_ONE_BUDGET = {
    INPUT_SIZE: (
        {"prova": "i1", "operation": "check", "source": source_of_exactly(300)},
        {INPUT_SIZE: 50},
    ),
    OPERATION_TIME: (
        {"prova": "i1", "operation": "evaluate", "source": within_every_budget(),
         "function": "initial", "arguments": []},
        {OPERATION_TIME: 0},
    ),
    PEAK_MEMORY: (
        {"prova": "i1", "operation": "verify", "source": within_every_budget()},
        {PEAK_MEMORY: 1},
    ),
    ANSWER_SIZE: (
        {"prova": "i1", "operation": "discover"},
        {ANSWER_SIZE: 30},
    ),
}


@pytest.mark.parametrize("budget", BUDGET_NAMES)
def test_a_run_stopped_by_a_budget_reports_only_that_budget(budget):
    """Given a run stopped by one of the four budgets, when the caller
    reads the answer, then it holds the status, one refusal naming that
    budget and nothing else: no claim, no result, no digest of the
    source, and no word about what the program may mean.
    """
    request, lowered = RUNS_PAST_ONE_BUDGET[budget]

    response = run(request, lowered).assert_answered(f"a run past the {budget} budget")

    why = f"a run past the {budget} budget"
    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: "
        f"{str(response)[:400]}. Every budget this tool declares is answered "
        "with one status, so a caller handles them in one place."
    )
    the_refusal(response, CATEGORY_OF[budget], why)
    assert len(response.get("diagnostics") or []) == 1, (
        f"the answer to {why} carries "
        f"{len(response.get('diagnostics') or [])} refusals: {response}. The "
        "run stopped at the first budget it passed, so there is one cause to "
        "report."
    )
    assert_claims_nothing(response, why)
