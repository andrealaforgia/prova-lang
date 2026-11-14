"""Acceptance test for F5 criterion 4: `result` read in a body or in a
precondition makes the program invalid, while a postcondition may read
it.

SPEC.md line 149: no binder may use `result`; only a postcondition may
read it.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program that mentions `result`,
including the postcondition that is allowed to read it. The control
below reads `result` in a postcondition and requires acceptance; a
second control shows that reading `result` where nothing binds it
reaches a different, already published refusal.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    RESERVED_NAME_CATEGORY,
    RESULT_READ_IN_A_BODY_AND_A_PRECONDITION,
    RESULT_READ_IN_A_POSTCONDITION_ONLY,
    RESULT_READ_WHERE_NOTHING_BINDS_IT,
    UNBOUND_NAME_CATEGORY,
    assert_accepted,
    assert_refused,
    categories,
    check,
)


def test_a_program_that_reads_result_in_its_body_and_precondition_is_refused():
    """Given the function `doubled` that makes `result` readable in its
    body and in its 1-clause precondition, when the program is checked,
    then it is invalid and the refusal names `result`."""
    run = check(RESULT_READ_IN_A_BODY_AND_A_PRECONDITION)

    assert_refused(run, RESERVED_NAME_CATEGORY, ["result"])


def test_the_same_function_reading_result_in_its_postcondition_is_accepted():
    """Control: the same function with 1 postcondition clause that reads
    `result`, and a parameter named `n`, is accepted, so the refusal
    above is about reading `result` outside a postcondition."""
    assert_accepted(
        check(RESULT_READ_IN_A_POSTCONDITION_ONLY),
        "a postcondition that reads result",
    )


def test_reading_result_where_nothing_binds_it_stays_an_unbound_name():
    """Control: a body that reads `result` while no binder introduces it
    is still refused as an unbound name, the answer the tool already
    gave, and is not reported as a reserved-word defect: there is no
    binder to repair."""
    response = check(RESULT_READ_WHERE_NOTHING_BINDS_IT).response()

    assert response.get("status") == "invalid_program", response
    assert UNBOUND_NAME_CATEGORY in categories(response), (
        "a body reading a name nothing binds was not refused as an unbound name: "
        f"{response}. Reading `result` where no binder introduces it is an unbound "
        "name; keep the answer the tool already gave."
    )
    assert RESERVED_NAME_CATEGORY not in categories(response), (
        "a body reading `result` with no binder was reported as a reserved-word "
        f"defect: {response}. The reserved-word refusal asks the reader to rename a "
        "binder; here there is none, so it would name no repair."
    )
