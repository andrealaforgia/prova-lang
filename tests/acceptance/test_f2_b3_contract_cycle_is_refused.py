"""Acceptance test for F2 criterion 3: a cycle that runs only through a
contract clause is refused when the program is checked.

SPEC.md lines 163-165: the graph covers function bodies *and* contracts,
so recursion through a contract is prohibited even when no body recurses.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program whose contract contains a
call. The control below keeps a contract call but sends it to another
function, and requires that program to be accepted.
"""

from __future__ import annotations

from _f2_cycle_fixtures import (
    CONTRACT_CALLS_ANOTHER_FUNCTION,
    CONTRACT_ONLY_CYCLE,
    accepted,
    check,
    cycle_reasons,
    reported_cycles,
)


def test_a_cycle_that_runs_only_through_a_contract_clause_is_refused():
    """Given `balance`, whose body is just its parameter but whose
    `ensures` clause calls `balance`, when the program is checked, then
    the program is invalid and the refusal names `balance`."""
    run = check(CONTRACT_ONLY_CYCLE)

    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"a function whose contract calls itself was not refused: {response}. A "
        "contract clause is part of the dependency graph; a cycle through it must "
        "be refused exactly as a cycle through a body is."
    )
    assert reported_cycles(response) == [frozenset({"balance"})], (
        f"the refusal does not report the contract cycle as a cycle through "
        f"`balance`: {response}. Report the functions the cycle runs through, "
        "whether the call sits in a body or in a contract clause."
    )
    assert all("balance" in reason for reason in cycle_reasons(response)), (
        f"the reported reason does not name `balance`: {cycle_reasons(response)}. "
        "Name every function of the cycle in the reason."
    )


def test_a_contract_that_calls_another_function_is_accepted():
    """Control: `balance`, whose `ensures` clause calls a different
    function `doubled`, is accepted with no diagnostics -- so the refusal
    above is caused by the cycle, not by calling from a contract."""
    run = check(CONTRACT_CALLS_ANOTHER_FUNCTION)

    assert accepted(run), (
        f"a contract clause calling another function was refused: "
        f"{run.response()}. Contracts may call other functions; only a cycle is "
        "refused."
    )
