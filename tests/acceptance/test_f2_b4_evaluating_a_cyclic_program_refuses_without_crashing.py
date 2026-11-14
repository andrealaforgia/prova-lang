"""Acceptance test for F2 criterion 4: asking a cyclic program for an
answer gives a structured refusal in valid JSON and the process exits
normally -- the tool never dies with a Python traceback.

`docs/spec-trace.md` defect 1 records what happened instead: a recursive
program passed `check`, then `evaluate` raised an uncaught
`RecursionError`.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered every request with the same refusal.
The last test asks the same question of an acyclic program and requires a
value back, so a tool that always refuses fails here.
"""

from __future__ import annotations

from _f2_cycle_fixtures import (
    CYCLE_CATEGORY,
    ONE_STEP_COUNTDOWN,
    SELF_CALLING_COUNTDOWN,
    declared_examples,
    evaluate,
    reported_cycles,
)


def test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json():
    """Given the program whose `countdown` calls itself, when `countdown`
    is evaluated with the argument 3, then the answer is a structured
    refusal in valid JSON and the process exits normally."""
    run = evaluate(SELF_CALLING_COUNTDOWN, "countdown", ["3"])

    assert run.exit_code == 0, (
        f"the command exited with {run.exit_code} instead of 0, so a caller sees a "
        f"failed process rather than an answer; its standard error ended with "
        f"{run.stderr[-400:]!r}. Refuse the cyclic program and exit normally."
    )
    assert not run.shows_a_crash(), (
        f"the command printed a Python traceback: {run.stderr[-400:]!r}. A refused "
        "program must be reported as a diagnostic, never as an uncaught exception."
    )
    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"evaluating a cyclic program did not answer with a refusal: {response}. "
        "The program is invalid; say so instead of attempting the evaluation."
    )
    assert reported_cycles(response) == [frozenset({"countdown"})], (
        f"the refusal does not name the cycle that makes the program invalid: "
        f"{response}. Report the same cycle `evaluate` refuses on as `check` does."
    )


def test_running_the_declared_examples_of_a_cyclic_program_is_refused_in_json():
    """Given the same program, when its declared examples are run, then
    the answer is a structured refusal in valid JSON and the process exits
    normally."""
    run = declared_examples(SELF_CALLING_COUNTDOWN)

    assert run.exit_code == 0, (
        f"the command exited with {run.exit_code} instead of 0 while running the "
        f"declared examples of a cyclic program; its standard error ended with "
        f"{run.stderr[-400:]!r}. Refuse the program and exit normally."
    )
    assert not run.shows_a_crash(), (
        f"the command printed a Python traceback: {run.stderr[-400:]!r}. Refuse the "
        "cyclic program before running any example from it."
    )
    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"running the examples of a cyclic program did not answer with a refusal: "
        f"{response}. Check the program first and refuse it."
    )
    assert reported_cycles(response) == [frozenset({"countdown"})], (
        f"the refusal does not name the cycle that makes the program invalid: "
        f"{response}. Report the same cycle every operation refuses on."
    )


def test_evaluating_the_acyclic_function_still_answers_with_its_value():
    """Control: the same `countdown` without the self-call still answers
    the question -- 3 counted down one step is 2 -- so the refusals above
    come from the cycle, not from refusing every request."""
    run = evaluate(ONE_STEP_COUNTDOWN, "countdown", ["3"])

    response = run.response()
    assert run.exit_code == 0, f"the command exited with {run.exit_code}: {run.stderr[-400:]!r}"
    assert response.get("status") == "completed", (
        f"an acyclic program was not evaluated: {response}. Only a program whose "
        "calls form a cycle may be refused for that reason."
    )
    assert (response.get("result") or {}).get("value") == "2", (
        f"counting 3 down one step did not answer 2: {response}. The cycle check "
        "must not change what an acyclic program computes."
    )
