"""Acceptance test for F5 criterion 5: a pattern that binds the same
name twice is refused.

SPEC.md lines 156-161: a pattern variable binds once per pattern, so two
fields of one pattern cannot carry the same spelling.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every 2-field pattern. The control
below runs the same pattern with two different names and requires it to
be accepted.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    PATTERN_BINDING_ONE_NAME_TWICE,
    PATTERN_BINDING_TWO_NAMES,
    SHADOWED_BINDING_CATEGORY,
    assert_accepted,
    assert_refused,
    check,
)


def test_a_pattern_that_binds_one_name_to_both_fields_is_refused():
    """Given the record `Pair` of 2 Int fields and a pattern that binds
    `n` to both of them, when the program is checked, then it is invalid
    and the refusal names `n`."""
    run = check(PATTERN_BINDING_ONE_NAME_TWICE)

    assert_refused(run, SHADOWED_BINDING_CATEGORY, ["n", "pattern"])


def test_the_same_pattern_with_two_names_is_accepted():
    """Control: the same 2-field pattern binding `n` and `m` is
    accepted, so the refusal above is about the repeated spelling and
    not about the pattern."""
    assert_accepted(check(PATTERN_BINDING_TWO_NAMES), "a pattern of two names")
