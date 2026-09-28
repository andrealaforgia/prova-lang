"""Acceptance test for I1.S6.B3: given the same program, when the Owner
supplies runtime inputs beyond 2^53 but within 64-bit range, positive and
negative, then the reported results are exact.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova; the expected results are
computed independently with Python's own arbitrary-precision `int`
arithmetic, not read from the implementation.
"""

from __future__ import annotations

from _i1_s6_acceptance_fixtures import evaluate_add_one

CASES = [
    (9007199254740993, 9007199254740994),
    (-9007199254740995, -9007199254740994),
]


def test_add_one_beyond_2_53_but_within_64_bit_range_positive_and_negative():
    """Given the same program, when the Owner supplies runtime inputs
    beyond 2^53 but within 64-bit range, positive and negative
    (9007199254740993 and -9007199254740995), then the reported results
    are exactly 9007199254740994 and -9007199254740994."""
    for n, expected in CASES:
        response = evaluate_add_one(n)

        assert response.get("status") == "completed", f"expected a successful evaluation of add-one({n}): {response}"
        result = response.get("result") or {}
        value_text = result.get("value")
        assert value_text is not None, f"no successful result value for add-one({n}): {response}"
        assert value_text != str(n), f"result echoes input {n} back instead of adding one: {response}"
        assert value_text == str(expected), f"add-one({n}): expected {expected}, got {value_text!r}: {response}"
