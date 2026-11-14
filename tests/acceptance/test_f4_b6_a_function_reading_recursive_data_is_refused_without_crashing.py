"""Acceptance test for F4: a program whose function reads a recursive
union is refused with the recursive-data answer, and the command stays a
well-behaved JSON tool while doing it.

This is the shape the rule exists for. The checks that follow the fields
of a type -- here, whether a `match` covers every value of its scrutinee
-- are defined only on acyclic types, so on this program the tool used to
walk the type forever instead of answering.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the command answered this one program and crashed on
the plain recursive union. test_f4_b3 checks that program through the
same command.
"""

from __future__ import annotations

from _f4_recursive_type_fixtures import (
    UNION_WITH_A_RECURSIVE_VARIANT_READ_BY_A_FUNCTION,
    assert_refused_naming_the_cycle,
    check,
)


def test_a_function_that_matches_on_recursive_data_is_refused_not_crashed():
    """Given the recursive union `Stack` and a function whose body
    matches on it, when the program is checked, then the command exits 0
    with 1 JSON response that refuses the program and names `Stack`."""
    run = check(UNION_WITH_A_RECURSIVE_VARIANT_READ_BY_A_FUNCTION)

    assert run.exit_code == 0, (
        f"the command exited {run.exit_code} instead of 0 on a program with "
        f"recursive data; it printed {run.stderr[-400:]!r} on standard error. "
        "Answer every request with one JSON response, including this one."
    )
    assert "Traceback" not in run.stderr, (
        f"the command printed a traceback: {run.stderr[-400:]!r}. A program the "
        "profile does not support is refused, not crashed on."
    )

    assert_refused_naming_the_cycle(run, ["Stack"])
