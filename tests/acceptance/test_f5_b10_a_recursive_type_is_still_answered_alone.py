"""Acceptance test for the order of the rules: a program whose declared
types lead back to themselves is still answered with that refusal alone,
even when one of its functions also hides a binding.

The recursive-data refusal already says that the functions of such a
program were not checked, because every check that follows the fields of
a type is defined only on acyclic types. The binding rule is one of
those checks for a reader: it reports the functions. Adding it must not
make the tool answer two unrelated refusals, one of which it cannot
stand behind.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool reported recursive data for everything. The
control below is the same hiding function without the recursive type and
requires the hidden-binding refusal.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    A_RECURSIVE_TYPE_BESIDE_A_HIDING_LET,
    LET_HIDING_A_PARAMETER,
    SHADOWED_BINDING_CATEGORY,
    assert_refused,
    categories,
    check,
)

RECURSIVE_TYPE_CATEGORY = "recursive_type"


def test_a_recursive_type_beside_a_hiding_let_answers_recursive_data_alone():
    """Given the record `Node` whose field leads back to `Node`, beside
    a function whose `let` hides its parameter, when the program is
    checked, then the 1 refusal is the recursive-data one."""
    response = check(A_RECURSIVE_TYPE_BESIDE_A_HIDING_LET).response()

    assert response.get("status") == "invalid_program", response
    assert categories(response) == [RECURSIVE_TYPE_CATEGORY], (
        f"a program with recursive data was answered with {categories(response)}: "
        f"{response}. The recursive-data refusal says the functions were not "
        "checked, so no refusal about them may be reported beside it."
    )


def test_the_same_hiding_function_without_the_recursive_type_is_refused_for_hiding():
    """Control: the same function alone, with no recursive type in the
    program, is refused for the hidden binding, so the test above shows
    an order and not a rule that never fires."""
    assert_refused(check(LET_HIDING_A_PARAMETER), SHADOWED_BINDING_CATEGORY, ["cents"])
