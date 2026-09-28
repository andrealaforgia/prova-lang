"""Acceptance test for I1.S6.B2: given the same add-one program, when the
Owner supplies as runtime input a fresh negative integer below -2^63, then
the reported result is exactly that input plus one.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova; the expected result is computed
independently with Python's own arbitrary-precision `int` arithmetic, not
read from the implementation.
"""

from __future__ import annotations

from _i1_s6_fixtures import evaluate_add_one

N = -9223372036854775810  # below -2**63
EXPECTED = -9223372036854775809


def test_add_one_of_a_fresh_integer_below_negative_2_63_is_exact():
    """Given the same program, when the Owner supplies as runtime input a
    fresh negative integer below -2^63 (-9223372036854775810), then the
    reported result is exactly that input plus one (-9223372036854775809)."""
    response = evaluate_add_one(N)

    assert response.get("status") == "completed", f"expected a successful evaluation: {response}"
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text is not None, f"no successful result value: {response}"
    assert value_text != str(N), f"result echoes the input back instead of adding one: {response}"
    assert value_text == str(EXPECTED), f"expected {EXPECTED}, got {value_text!r}: {response}"
