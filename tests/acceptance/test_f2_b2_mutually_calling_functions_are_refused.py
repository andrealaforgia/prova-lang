"""Acceptance test for F2 criterion 2: two functions that call each other
are refused when the program is checked, and the refusal names both.

SPEC.md lines 163-165: this prohibits mutual recursion as well as direct
recursion.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool reported one cycle per function instead of one
cycle for the pair, since both names would still appear somewhere. The
assertion below compares the reported cycles against the one cycle this
program has, so a per-function report fails it.
"""

from __future__ import annotations

from _f2_cycle_fixtures import (
    MUTUALLY_CALLING_STEPS,
    ONE_WAY_STEPS,
    accepted,
    check,
    cycle_reasons,
    reported_cycles,
)

THE_PAIR = frozenset({"even-steps", "odd-steps"})


def test_two_functions_that_call_each_other_are_refused_and_both_are_named():
    """Given `even-steps` calling `odd-steps` and `odd-steps` calling
    `even-steps`, when the program is checked, then the program is invalid
    and the refusal names both functions."""
    run = check(MUTUALLY_CALLING_STEPS)

    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"two functions that call each other were not refused: {response}. Mutual "
        "recursion is a cycle in the dependency graph; refuse the program when it "
        "is checked."
    )
    assert reported_cycles(response) == [THE_PAIR], (
        f"the refusal does not report the two mutually calling functions as one "
        f"cycle naming both: {response}. Report each set of functions that depend "
        "on each other as a single cycle naming every member."
    )
    assert all(
        "even-steps" in reason and "odd-steps" in reason
        for reason in cycle_reasons(response)
    ), (
        f"the reported reason does not name both functions of the cycle: "
        f"{cycle_reasons(response)}. A reader must be able to see the whole cycle "
        "from the reason alone."
    )


def test_the_same_pair_is_accepted_when_only_one_of_them_calls_the_other():
    """Control: the same two functions, with `odd-steps` no longer calling
    back, are accepted with no diagnostics -- so the refusal above is
    caused by the call back, not by one function calling another."""
    run = check(ONE_WAY_STEPS)

    assert accepted(run), (
        f"a program in which one function calls another, and nothing calls back, "
        f"was refused: {run.response()}. One-way calls are acyclic; leave them "
        "accepted."
    )
