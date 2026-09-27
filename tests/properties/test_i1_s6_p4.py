"""I1.S6.P4 / I1.S6.B4: direct evaluation of the same unchanged add-one
program with runtime input 41 (the positive control) completes successfully
and reports exactly 42.
"""

from __future__ import annotations

from _i1_s6_fixtures import assert_add_one_result, evaluate_add_one


def test_p4_add_one_of_41_returns_42():
    returncode, response, stdout, stderr = evaluate_add_one(41)
    assert_add_one_result(returncode, response, stdout, stderr, n=41)
