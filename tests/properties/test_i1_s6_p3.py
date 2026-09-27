"""I1.S6.P3 / I1.S6.B3: for positive and negative runtime integers whose
magnitude exceeds 2^53 and whose inputs remain within signed 64-bit range,
add-one returns exactly n + 1, including both approved examples
(9007199254740993 -> 9007199254740994 and -9007199254740995 ->
-9007199254740994) and the input 9223372036854775807 (2^63-1) whose result
crosses the signed 64-bit upper boundary.

Input domains: [2^53+1, 2^63-1] and [-2^63, -2^53-1].

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s6_fixtures import assert_add_one_result, evaluate_add_one

_positive_domain = st.integers(min_value=2**53 + 1, max_value=2**63 - 1)
_negative_domain = st.integers(min_value=-(2**63), max_value=-(2**53) - 1)
_domain = st.one_of(_positive_domain, _negative_domain)


@settings(derandomize=True, max_examples=14, deadline=None)
@given(n=_domain)
@example(n=9007199254740993)
@example(n=-9007199254740995)
@example(n=2**53 + 2)
@example(n=2**53 + 3)
@example(n=-(2**53) - 1)
@example(n=-(2**53) - 2)
@example(n=2**63 - 2)
@example(n=2**63 - 1)
@example(n=-(2**63))
@example(n=-(2**63) + 1)
def test_p3_add_one_beyond_2_53_within_64_bit_range_returns_exact_successor(n):
    returncode, response, stdout, stderr = evaluate_add_one(n)
    assert_add_one_result(returncode, response, stdout, stderr, n=n)
