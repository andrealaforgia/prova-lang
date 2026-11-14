"""Acceptance test for F2 criterion 1: a function whose body calls itself
is refused when the program is checked, and the refusal names it.

SPEC.md lines 163-165: the combined dependency graph of function bodies
and contracts must be acyclic.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program, naming every function.
The control below removes exactly one call from the same program and
requires that program to be accepted, so a tool that refuses everything
fails here.
"""

from __future__ import annotations

from _f2_cycle_fixtures import (
    CYCLE_CATEGORY,
    ONE_STEP_COUNTDOWN,
    SELF_CALLING_COUNTDOWN,
    accepted,
    check,
    cycle_reasons,
    reported_cycles,
)


def test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it():
    """Given a function `countdown` whose body calls `countdown`, when the
    program is checked, then the program is invalid and the refusal names
    `countdown` as the function in the cycle."""
    run = check(SELF_CALLING_COUNTDOWN)

    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"a program whose only function calls itself was not refused: {response}. "
        "A cyclic program must be refused when it is checked; report it as an "
        "invalid program."
    )
    assert reported_cycles(response) == [frozenset({"countdown"})], (
        f"the refusal does not report exactly the one cycle this program has "
        f"({{countdown}}): {response}. Every set of functions that depend on each "
        "other, and no other function, must be reported as a cycle."
    )
    assert all("countdown" in reason for reason in cycle_reasons(response)), (
        f"the reported reason does not name `countdown`, so a reader cannot tell "
        f"which function the cycle runs through: {cycle_reasons(response)}. Name "
        "every function of the cycle in the reason."
    )


def test_the_same_function_without_the_self_call_is_accepted():
    """Control: the same `countdown`, with its one self-call replaced by
    ordinary arithmetic, is accepted with no diagnostics -- so the refusal
    above is caused by the call, not by the shape of the program."""
    run = check(ONE_STEP_COUNTDOWN)

    assert accepted(run), (
        f"a function with no call at all was refused: {run.response()}. Only a "
        "program whose calls form a cycle may be refused for that reason; leave "
        "every acyclic program accepted."
    )
