"""Acceptance test for F4 criterion 3: a union whose variant payload
closes a cycle is refused, and the refusal names the union.

SPEC.md lines 135-136: record fields and union payloads have declared
types, and the type-dependency graph must be acyclic in core-0.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every union. The control below runs the
same union with the recursive payload declared `Int` and requires it to
be accepted.
"""

from __future__ import annotations

from _f4_recursive_type_fixtures import (
    UNION_WITH_A_RECURSIVE_VARIANT,
    UNION_WITHOUT_A_RECURSIVE_VARIANT,
    assert_accepted,
    assert_refused_naming_the_cycle,
    check,
)


def test_a_union_whose_variant_payload_closes_a_cycle_is_refused():
    """Given the union `Stack` whose variant `Pushed` carries a field of
    type `Stack`, when the program is checked, then it is invalid and the
    refusal names `Stack`."""
    run = check(UNION_WITH_A_RECURSIVE_VARIANT)

    assert_refused_naming_the_cycle(run, ["Stack"])


def test_the_same_union_whose_payload_is_a_number_is_accepted():
    """Control: the same 2-variant union with `rest` declared `Int` is
    accepted, so the refusal above is about the cycle, not the union."""
    assert_accepted(
        check(UNION_WITHOUT_A_RECURSIVE_VARIANT), "a union of 2 non-recursive variants"
    )
