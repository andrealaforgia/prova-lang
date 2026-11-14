"""Acceptance test for F5 criterion 6: a pattern variable is scoped to
its own clause, so the same spelling in two disjoint clauses is
accepted; the same spelling that hides the parameter is not.

SPEC.md lines 147-148: pattern variables are scoped to their clause and
the same spelling in disjoint clauses is allowed, while a binding must
not shadow a visible value binding.

Both observations live in one test because either alone proves little: a
tool that accepted everything would pass the first, and a tool that
refused every repeated spelling would pass the second.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    ONE_CLAUSE_BINDING_THE_PARAMETER_NAME,
    ONE_SPELLING_IN_TWO_CLAUSES,
    SHADOWED_BINDING_CATEGORY,
    assert_accepted,
    assert_refused,
    check,
)


def test_a_clause_variable_is_visible_only_inside_its_own_clause():
    """Given the union `Colour` with 2 variants and a `match` whose two
    clauses both bind `tone`, when the program is checked, then it is
    accepted; and when the first clause binds the parameter's name `c`
    instead, then that program is invalid and the refusal names `c`."""
    assert_accepted(
        check(ONE_SPELLING_IN_TWO_CLAUSES),
        "two disjoint clauses that bind the same spelling",
    )

    assert_refused(
        check(ONE_CLAUSE_BINDING_THE_PARAMETER_NAME),
        SHADOWED_BINDING_CATEGORY,
        ["c", "parameter"],
    )
