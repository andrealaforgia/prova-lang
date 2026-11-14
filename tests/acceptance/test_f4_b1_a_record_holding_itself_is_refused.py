"""Acceptance test for F4 criterion 1: a record with a field of its own
type is refused, and the refusal names the cycle.

SPEC.md lines 135-136: the type-dependency graph must be acyclic in
core-0, so recursive data requires a later profile.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The control below runs
the same program with the self-holding field changed to `Int` and
requires it to be accepted.
"""

from __future__ import annotations

from _f4_recursive_type_fixtures import (
    RECORD_HOLDING_A_NUMBER,
    RECORD_HOLDING_ITSELF,
    assert_accepted,
    assert_refused_naming_the_cycle,
    check,
)


def test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle():
    """Given the record `Node` whose field `next` has type `Node`, when
    the program is checked, then it is invalid and the refusal names
    `Node` as the type that leads back to itself."""
    run = check(RECORD_HOLDING_ITSELF)

    assert_refused_naming_the_cycle(run, ["Node"])


def test_the_same_record_whose_field_is_a_number_is_accepted():
    """Control: the same 2-field record with `next` declared `Int`
    instead of `Node` is accepted, so the refusal above is about the
    cycle and not about the record."""
    assert_accepted(check(RECORD_HOLDING_A_NUMBER), "a record of two Int fields")
