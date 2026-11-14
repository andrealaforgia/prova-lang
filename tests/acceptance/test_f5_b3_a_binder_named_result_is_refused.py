"""Acceptance test for F5 criterion 3: every kind of binder named
`result` is refused -- a parameter, a `let` binding and a pattern
variable alike.

SPEC.md line 149: no binder may use `result`; only a postcondition may
read it.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused the three programs for some other
reason, or refused every program. Each refusal is required to be the
reserved-word refusal and to name `result`, and each program has a twin
that differs only in that binder's name and is required to be accepted.
"""

from __future__ import annotations

import pytest

from _f5_binding_fixtures import (
    A_PARAMETER_AND_A_LET_BOTH_NAMED_RESULT,
    LET_NAMED_RESULT,
    LET_NAMED_TOTAL,
    PARAMETER_NAMED_N,
    PARAMETER_NAMED_RESULT,
    PATTERN_VARIABLE_NAMED_HELD,
    PATTERN_VARIABLE_NAMED_RESULT,
    RESERVED_NAME_CATEGORY,
    assert_accepted,
    assert_refused,
    categories,
    check,
)

BINDERS_NAMED_RESULT = [
    pytest.param(PARAMETER_NAMED_RESULT, "parameter", id="parameter"),
    pytest.param(LET_NAMED_RESULT, "let", id="let-binding"),
    pytest.param(PATTERN_VARIABLE_NAMED_RESULT, "pattern", id="pattern-variable"),
]

THE_SAME_BINDERS_WITH_ANOTHER_NAME = [
    pytest.param(PARAMETER_NAMED_N, "a parameter named n", id="parameter"),
    pytest.param(LET_NAMED_TOTAL, "a let binding named total", id="let-binding"),
    pytest.param(
        PATTERN_VARIABLE_NAMED_HELD,
        "a pattern variable named amount",
        id="pattern-variable",
    ),
]


@pytest.mark.parametrize("source,kind_of_binder", BINDERS_NAMED_RESULT)
def test_a_binder_named_result_is_refused(source: str, kind_of_binder: str):
    """Given a program whose binder is named `result`, when the program
    is checked, then it is invalid, the refusal names `result` and says
    which kind of binder used it."""
    run = check(source)

    assert_refused(run, RESERVED_NAME_CATEGORY, ["result", kind_of_binder])


@pytest.mark.parametrize("source,why", THE_SAME_BINDERS_WITH_ANOTHER_NAME)
def test_the_same_binder_under_another_name_is_accepted(source: str, why: str):
    """Control: each of the three programs, with its binder renamed and
    nothing else changed, is accepted, so the refusals above are about
    the word `result` and not about the binder."""
    assert_accepted(check(source), why)


def test_each_binder_named_result_is_refused_on_its_own():
    """Given a function whose parameter is `result` and whose body also
    binds `result` in a `let`, when the program is checked, then it is
    invalid with 2 reserved-word refusals, 1 per binder: each is a
    binder the reader must rename."""
    response = check(A_PARAMETER_AND_A_LET_BOTH_NAMED_RESULT).response()

    assert response.get("status") == "invalid_program", response
    reserved = [
        diagnostic
        for diagnostic in response.get("diagnostics") or []
        if diagnostic.get("category") == RESERVED_NAME_CATEGORY
    ]
    assert len(reserved) == 2, (
        f"2 binders named `result` were answered with {categories(response)}: "
        f"{response}. Each binder is one defect with one repair; report every one of "
        "them, so the reader does not rename one and meet the next."
    )
    assert {
        (diagnostic["location"]["line"], diagnostic["location"]["column"])
        for diagnostic in reserved
    } == {(1, 7), (4, 3)}, (
        f"the 2 refusals do not point at the 2 binders: {reserved}. One is the "
        "parameter of the function declared on line 2, the other the `let` on line 4."
    )
