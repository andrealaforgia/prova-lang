"""Acceptance test for F2fix criterion 1: the refusal of a program whose
calls form a cycle names the whole cycle, and writes the names in the
order the program declares them.

SPEC.md lines 163-165 require the dependency graph to be acyclic. The
refusal points at one declaration of the cycle, so the list of names, and
the order a reader meets them in, is what tells the reader which other
functions to read and in which order to walk the source.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

from _f2_cycle_fixtures import (
    LEDGER_CYCLE_DECLARED_AGAINST_CALL_ORDER,
    LEDGER_CYCLE_IN_DECLARATION_ORDER,
    REPORT_CYCLE_DECLARED_IN_CALL_ORDER,
    REPORT_CYCLE_IN_DECLARATION_ORDER,
    check,
    cycle_members,
)


def test_a_cycle_of_three_functions_is_named_in_full_and_in_declaration_order():
    """Given `gather` calling `summarise`, `summarise` calling `publish`
    and `publish` calling `gather`, declared in that order, when the
    program is checked, then it is refused and the one reported cycle
    reads `gather`, `summarise`, `publish`.

    still passes if: the tool wrote the three names in the order its own
    search reached them, because here that order and the declaration order
    cannot be told apart. The second test below separates them.
    """
    run = check(REPORT_CYCLE_DECLARED_IN_CALL_ORDER)

    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"three functions that call each other round were not refused: {response}. "
        "A program whose calls lead back to where they started has a cycle; refuse "
        "it when it is checked."
    )
    assert cycle_members(response) == [REPORT_CYCLE_IN_DECLARATION_ORDER], (
        f"the refusal reports {cycle_members(response)} instead of one cycle "
        f"reading {list(REPORT_CYCLE_IN_DECLARATION_ORDER)}: {response}. Report the "
        "three functions as a single cycle, leave none of them out, and write them "
        "in the order the program declares them."
    )


def test_a_cycle_is_named_in_declaration_order_when_the_calls_run_in_another_order():
    """Given `audit` calling `refund`, `refund` calling `settle` and
    `settle` calling `audit`, but declared audit, settle, refund, when the
    program is checked, then the one reported cycle reads `audit`,
    `settle`, `refund` -- the order of the declarations, not of the calls.

    still passes if: the tool wrote the names in the order it happened to
    collect them and that order was the declaration order by luck. No
    rotation of this call chain gives the declaration order, so an order
    taken from the calls, or from the order the functions were collected
    in, reads differently and fails the assertion.
    """
    run = check(LEDGER_CYCLE_DECLARED_AGAINST_CALL_ORDER)

    response = run.response()
    assert response.get("status") == "invalid_program", (
        f"three functions that call each other round were not refused: {response}. "
        "The order of the declarations does not change the fault; refuse the "
        "program when it is checked."
    )
    assert cycle_members(response) == [LEDGER_CYCLE_IN_DECLARATION_ORDER], (
        f"the refusal reports {cycle_members(response)} instead of one cycle "
        f"reading {list(LEDGER_CYCLE_IN_DECLARATION_ORDER)}: {response}. Write the "
        "members of a cycle in the order the program declares them, so a reader "
        "walks the source from the first of them downwards."
    )
