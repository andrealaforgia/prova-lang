"""Acceptance test for F5 criterion 4: `result` read in a body or in a
precondition is refused as the reserved name it is, while a
postcondition may read it.

SPEC.md line 149: no binder may use `result`; only a postcondition may
read it. A body and a precondition run before there is a returned value,
so the name is not readable there at all.

The stimulus is a genuine read: nothing in these programs binds
`result`, so what is observed is the read itself and not a binder (a
binder named `result` is the subject of its own test beside this one).

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program that mentions `result`,
including the postcondition that may read it. The control below reads
`result` in a postcondition and requires acceptance.
"""

from __future__ import annotations

import pytest

from _f5_binding_fixtures import (
    RESERVED_NAME_CATEGORY,
    RESULT_READ_IN_A_PRECONDITION,
    RESULT_READ_IN_A_POSTCONDITION_ONLY,
    RESULT_READ_WHERE_NOTHING_BINDS_IT,
    UNBOUND_NAME_CATEGORY,
    assert_accepted,
    assert_refused,
    categories,
    check,
)

READS_OUTSIDE_A_POSTCONDITION = [
    pytest.param(RESULT_READ_WHERE_NOTHING_BINDS_IT, (4, 6), id="in-the-body"),
    pytest.param(RESULT_READ_IN_A_PRECONDITION, (3, 16), id="in-a-precondition"),
]


@pytest.mark.parametrize("source,place", READS_OUTSIDE_A_POSTCONDITION)
def test_reading_result_outside_a_postcondition_is_refused_as_reserved(
    source: str, place: tuple[int, int]
):
    """Given a function that reads `result` in its body, or in its 1
    precondition clause, while nothing binds that name, when the program
    is checked, then it is invalid, the refusal names `result` and it
    points at the read."""
    run = check(source)

    assert_refused(run, RESERVED_NAME_CATEGORY, ["result"], at=place)


@pytest.mark.parametrize("source,place", READS_OUTSIDE_A_POSTCONDITION)
def test_such_a_read_is_not_answered_as_an_unbound_name(
    source: str, place: tuple[int, int]
):
    """The same 2 programs carry no unbound-name refusal: `result` is a
    name the language reserves, and a reader told only that it is
    unbound would look for the missing declaration instead of reading
    the rule."""
    response = check(source).response()

    assert UNBOUND_NAME_CATEGORY not in categories(response), (
        f"reading `result` was answered with {categories(response)}: {response}. One "
        "defect has one repair; the reserved-word refusal already says why the name "
        "cannot be read here."
    )


def test_the_same_function_reading_result_in_its_postcondition_is_accepted():
    """Control: a function with 1 postcondition clause that reads
    `result`, and a parameter named `n`, is accepted, so the refusals
    above are about reading `result` outside a postcondition."""
    assert_accepted(
        check(RESULT_READ_IN_A_POSTCONDITION_ONLY),
        "a postcondition that reads result",
    )
