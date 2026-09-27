"""I1.S6.P1 / I1.S6.B1: the separate add-one program returns exactly n + 1
for fresh positive runtime integers above both 2^53 and 2^63-1, including
9223372036854775808 (2^63) returning 9223372036854775809, without echoing,
rounding, wrapping, clamping or rejecting these valid inputs.

Finite evidence domain: generated n in [2^63, 2^256-1], with mandatory
cases 2^63, 2^63+1, 2^64-1, 2^64, 2^128-1 and 2^256-1. These generation
bounds are evidence limits, not language limits.

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s6_fixtures import assert_add_one_result, evaluate_add_one

LOWER = 2**63
UPPER = 2**256 - 1


@settings(derandomize=True, max_examples=10, deadline=None)
@given(n=st.integers(min_value=LOWER, max_value=UPPER))
@example(n=2**63)
@example(n=2**63 + 1)
@example(n=2**64 - 1)
@example(n=2**64)
@example(n=2**128 - 1)
@example(n=2**256 - 1)
def test_p1_add_one_beyond_2_63_returns_exact_successor(n):
    returncode, response, stdout, stderr = evaluate_add_one(n)
    assert_add_one_result(returncode, response, stdout, stderr, n=n)
