"""I1.S6.P2 / I1.S6.B2: the same add-one program returns exactly n + 1 for
fresh negative runtime integers below -2^63, including -9223372036854775810
returning -9223372036854775809, without losing the sign, rounding, wrapping
or rejecting these valid inputs.

Finite evidence domain: generated n in [-2^256, -2^63-1], with mandatory
cases -2^63-1, -2^63-2, -2^64, -2^64-1, -2^128 and -2^256.

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s6_fixtures import assert_add_one_result, evaluate_add_one

LOWER = -(2**256)
UPPER = -(2**63) - 1


@settings(derandomize=True, max_examples=10, deadline=None)
@given(n=st.integers(min_value=LOWER, max_value=UPPER))
@example(n=-(2**63) - 1)
@example(n=-(2**63) - 2)
@example(n=-(2**64))
@example(n=-(2**64) - 1)
@example(n=-(2**128))
@example(n=-(2**256))
def test_p2_add_one_below_negative_2_63_returns_exact_successor(n):
    returncode, response, stdout, stderr = evaluate_add_one(n)
    assert_add_one_result(returncode, response, stdout, stderr, n=n)
