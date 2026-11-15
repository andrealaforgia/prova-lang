"""F14 laws -- the four budgets, stated over every input a caller may
send rather than over the handful of examples the acceptance tests pin.

Each property names the design law it protects. Derandomized with a
fixed seed and a small example count: every case starts the real command
as a child process, so the number of cases is the test's cost.
"""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings, strategies as st

from _f14_budget_client import (
    ANSWER_SIZE,
    CATEGORY_OF,
    DECLARED,
    FORBIDDEN_WORDS,
    INPUT_SIZE,
    NOTHING_FITS_IN,
    OFFERED,
    READS_A_SOURCE,
    RESOURCE_EXHAUSTED,
    SEMANTIC_KEYS,
    answer,
    comment_of_exactly,
    printed_answer,
    program_of,
    refusals,
)

CASES = settings(
    derandomize=True,
    max_examples=10,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

MANIFEST = {"prova": "i1", "operation": "discover"}


def _check(source: str, lowered: dict | None = None) -> dict:
    return answer(
        {"prova": "i1", "operation": "check", "source": source}, lowered
    )


@CASES
@given(allowed=st.integers(min_value=16, max_value=2048), over=st.integers(min_value=1, max_value=256))
def test_the_input_budget_a_caller_sets_is_the_size_that_refuses(allowed, over):
    """LAW1: for every input budget a caller sets, a source of that size
    is read and a source past it is refused, with the budget and the
    size sent reported back.
    """
    fits = _check(comment_of_exactly(allowed), {INPUT_SIZE: allowed})
    too_large = _check(comment_of_exactly(allowed + over), {INPUT_SIZE: allowed})

    assert not refusals(fits, CATEGORY_OF[INPUT_SIZE]), (
        f"a source of exactly {allowed} bytes was refused for the input "
        f"budget of {allowed}: {fits}. The size a caller was allowed is "
        "allowed; a tool that refuses it publishes a number no caller can use."
    )
    refusal = refusals(too_large, CATEGORY_OF[INPUT_SIZE])
    assert len(refusal) == 1 and too_large["status"] == RESOURCE_EXHAUSTED, (
        f"a source of {allowed + over} bytes against a budget of {allowed} was "
        f"answered {too_large.get('status')!r} with {len(refusal)} input "
        f"budget refusals: {str(too_large)[:400]}. Past the number the caller "
        "set, the tool stops and says so."
    )
    assert refusal[0].get("expected") == allowed, (
        f"the refusal reports {refusal[0].get('expected')!r} allowed against "
        f"the {allowed} the caller set: {refusal[0]}. The number enforced is "
        "the number read back."
    )
    assert refusal[0].get("actual") == allowed + over, (
        f"the refusal reports {refusal[0].get('actual')!r} sent, expected "
        f"{allowed + over}: {refusal[0]}. A caller reads how far past the "
        "budget it went from this number."
    )


@CASES
@given(
    operation=st.sampled_from(OFFERED),
    budget=st.sampled_from(tuple(NOTHING_FITS_IN)),
    functions=st.integers(min_value=1, max_value=4),
)
def test_a_run_stopped_by_any_budget_reports_no_result(operation, budget, functions):
    """LAW2: whichever budget stops whichever operation, the answer
    carries the budget and nothing about the program: no claim, no
    result, no digest, and no word about what a program may mean.
    """
    request = {"prova": "i1", "operation": operation, "source": program_of(functions)}
    if operation == "evaluate":
        request.update({"function": "f0", "arguments": []})

    response = answer(request, {budget: NOTHING_FITS_IN[budget]})

    stops_this_run = budget != INPUT_SIZE or operation in READS_A_SOURCE
    if not stops_this_run:
        assert response["status"] == "completed", (
            f"{operation!r} was answered {response.get('status')!r} with the "
            f"input budget at 1: {str(response)[:300]}. The input budget sizes "
            "the program a request carries, and this operation reads none."
        )
        return

    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"{operation!r} under {budget}={NOTHING_FITS_IN[budget]} was answered "
        f"{response.get('status')!r}: {str(response)[:300]}. Nothing fits in "
        "that budget, so the run stops inside it."
    )
    assert len(refusals(response, CATEGORY_OF[budget])) == 1, (
        f"{operation!r} stopped by the {budget!r} budget carries "
        f"{response.get('diagnostics')}: a caller reads one cause, named for "
        "the budget that stopped it."
    )
    for key in SEMANTIC_KEYS:
        assert key not in response, (
            f"the answer to {operation!r} stopped by {budget!r} carries "
            f"{key!r}: {str(response)[:300]}. The tool stopped inside its own "
            "budget, so it has nothing to report about the program."
        )
    prose = " ".join(
        str(entry.get("reason", "")) for entry in response["diagnostics"]
    ).lower()
    used = [word for word in FORBIDDEN_WORDS if word in prose]
    assert not used, (
        f"the refusal for {operation!r} stopped by {budget!r} uses {used}: "
        f"{prose!r}. A budget says how much work this tool does, never what a "
        "program may mean (SPEC.md lines 503-508 and 280-284)."
    )


@CASES
@given(functions=st.integers(min_value=1, max_value=5))
def test_a_run_inside_the_declared_budgets_answers_as_if_none_were_set(functions):
    """LAW3: a program inside every declared budget gets the same answer
    whether or not the caller states the budgets, so stating them
    changes no answer.
    """
    request = {"prova": "i1", "operation": "examples", "source": program_of(functions)}

    untouched = answer(request)
    stated = answer(request, dict(DECLARED))

    assert stated == untouched, (
        f"a program of {functions} function(s) was answered differently when "
        f"the declared budgets were stated: {str(stated)[:300]} against "
        f"{str(untouched)[:300]}. A budget bounds how much work the tool does "
        "and nothing else, so an answer inside it is the answer it always was."
    )
    assert untouched["status"] == "completed", (
        f"a program of {functions} function(s) was answered "
        f"{untouched.get('status')!r}: {str(untouched)[:300]}. It is far "
        "inside every declared budget."
    )


@CASES
@given(allowed=st.integers(min_value=1, max_value=2000))
def test_an_answer_past_the_output_budget_is_replaced_whole(allowed):
    """LAW4: an answer larger than the budget a caller set is replaced
    by one complete refusal naming that budget; no caller ever reads the
    first part of an answer the tool could not give.
    """
    printed = printed_answer(MANIFEST, {ANSWER_SIZE: allowed})
    response = answer(MANIFEST, {ANSWER_SIZE: allowed})

    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the manifest under an answer budget of {allowed} bytes was answered "
        f"{response.get('status')!r}: {str(response)[:300]}. The manifest is "
        "thousands of bytes, so no answer budget this small can hold it."
    )
    assert len(refusals(response, CATEGORY_OF[ANSWER_SIZE])) == 1, (
        f"the answer under a budget of {allowed} carries "
        f"{response.get('diagnostics')}: one refusal, naming the answer "
        "budget, is what a caller reads."
    )
    assert refusals(response, CATEGORY_OF[ANSWER_SIZE])[0].get("expected") == allowed, (
        f"the refusal reports "
        f"{refusals(response, CATEGORY_OF[ANSWER_SIZE])[0].get('expected')!r} "
        f"allowed against the {allowed} the caller set."
    )
    assert "profile" not in printed and "diagnostic_schemas" not in printed, (
        f"the answer under a budget of {allowed} still carries part of the "
        f"manifest: {printed[:300]!r}. An answer that did not fit is withheld "
        "whole."
    )
