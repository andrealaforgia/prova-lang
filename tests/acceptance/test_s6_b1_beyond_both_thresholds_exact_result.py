"""Acceptance test for I1.S6.B1: given the separate add-one program, when
the Owner supplies as runtime input a fresh positive integer above both
2^53 and 2^63-1, then the reported result is exactly that input plus one,
not the input echoed back.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova; the expected result is computed
independently with Python's own arbitrary-precision `int` arithmetic, not
read from the implementation.
"""

from __future__ import annotations

from _i1_s6_acceptance_fixtures import evaluate_add_one

N = 9223372036854775808  # 2**63, above both 2**53 and 2**63 - 1
EXPECTED = 9223372036854775809


def test_add_one_of_a_fresh_integer_above_both_2_53_and_2_63_minus_1_is_exact():
    """Given the separate add-one program, when the Owner supplies as
    runtime input a fresh positive integer above both 2^53 and 2^63-1
    (9223372036854775808), then the reported result is exactly that input
    plus one (9223372036854775809), not the input echoed back."""
    response = evaluate_add_one(N)

    assert response.get("status") == "completed", f"expected a successful evaluation: {response}"
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text is not None, f"no successful result value: {response}"
    assert value_text != str(N), f"result echoes the input back instead of adding one: {response}"
    assert value_text == str(EXPECTED), f"expected {EXPECTED}, got {value_text!r}: {response}"
