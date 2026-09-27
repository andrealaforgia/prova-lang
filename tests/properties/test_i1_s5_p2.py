"""I1.S5.P2 / I1.S5.B1 / I1.S5.B2: `check` finds a hidden type error inside
`step` that none of its four declared examples reaches.

Given two hand-built variants -- a Bool operand of `+` in the Reserve
accepted arm, and a Bool operand of `-` in the Release accepted arm --
each unreachable by step's four declared examples but reachable by a fresh
valid input within the contract domain, when `check` runs against each,
then both are rejected as an invalid program, and their minimally corrected
counterparts (replacing the Bool literal with the original integer
expression) are accepted, alongside the unmodified positive control.
"""

from __future__ import annotations

import pytest

from _i1_s5_fixtures import (
    RELEASE_DECLARED_INPUTS,
    RELEASE_FRESH_INPUT,
    RESERVE_DECLARED_INPUTS,
    RESERVE_FRESH_INPUT,
    assert_accepted,
    assert_rejected_as_invalid_program,
    protected_source,
    release_bug_hits_branch,
    release_bug_source,
    release_fix_source,
    reserve_bug_hits_branch,
    reserve_bug_source,
    reserve_fix_source,
    run_check,
)


def test_p2_unmodified_source_is_the_positive_control():
    returncode, response, stdout, stderr = run_check(protected_source())
    assert_accepted(returncode, response, stdout, stderr)


@pytest.mark.parametrize(
    "declared_input,fresh_input,hits_branch",
    [
        pytest.param(RESERVE_DECLARED_INPUTS, RESERVE_FRESH_INPUT, reserve_bug_hits_branch, id="reserve"),
        pytest.param(RELEASE_DECLARED_INPUTS, RELEASE_FRESH_INPUT, release_bug_hits_branch, id="release"),
    ],
)
def test_p2_declared_examples_never_reach_the_injected_site(declared_input, fresh_input, hits_branch):
    assert not any(hits_branch(c) for c in declared_input), (
        "a declared example unexpectedly reaches the injected defect"
    )
    assert hits_branch(fresh_input), "the fresh input must reach the injected defect"


def test_p2_reserve_bug_is_rejected_as_invalid_program():
    returncode, response, stdout, stderr = run_check(reserve_bug_source())
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)


def test_p2_release_bug_is_rejected_as_invalid_program():
    returncode, response, stdout, stderr = run_check(release_bug_source())
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)


def test_p2_reserve_fix_is_accepted():
    returncode, response, stdout, stderr = run_check(reserve_fix_source())
    assert_accepted(returncode, response, stdout, stderr)


def test_p2_release_fix_is_accepted():
    returncode, response, stdout, stderr = run_check(release_fix_source())
    assert_accepted(returncode, response, stdout, stderr)


def test_p2_bug_and_fix_sources_actually_differ_from_the_control():
    control = protected_source()
    assert reserve_bug_source() != control
    assert reserve_fix_source() != control
    assert release_bug_source() != control
    assert release_fix_source() != control
    assert reserve_bug_source() != reserve_fix_source()
    assert release_bug_source() != release_fix_source()
