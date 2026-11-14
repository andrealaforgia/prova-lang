"""Acceptance test for F4 criterion 2: two records that each hold the
other are refused, and the refusal names both of them.

SPEC.md lines 135-136: the type-dependency graph must be acyclic in
core-0, so recursive data requires a later profile.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program that declares two types.
The control below keeps both declarations and only breaks the return
edge, and requires that program to be accepted.
"""

from __future__ import annotations

from _f4_recursive_type_fixtures import (
    ONE_RECORD_HOLDING_THE_OTHER,
    TWO_RECORDS_HOLDING_EACH_OTHER,
    assert_accepted,
    assert_refused_naming_the_cycle,
    check,
)


def test_two_records_that_each_hold_the_other_are_refused_naming_both():
    """Given the records `Invoice` and `Payment`, each with a field of
    the other's type, when the program is checked, then it is invalid and
    the refusal names both `Invoice` and `Payment`."""
    run = check(TWO_RECORDS_HOLDING_EACH_OTHER)

    assert_refused_naming_the_cycle(run, ["Invoice", "Payment"])


def test_the_same_pair_with_only_one_direction_is_accepted():
    """Control: `Invoice` still holds a `Payment`, but `Payment` holds an
    `Int`, so nothing leads back; the 2 declarations are accepted."""
    assert_accepted(
        check(ONE_RECORD_HOLDING_THE_OTHER), "a record that holds another record"
    )
