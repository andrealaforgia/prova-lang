"""Acceptance test for I1.S6.B4: given the same program, when the Owner
supplies 41 as runtime input as the positive control, then the reported
result is exactly 42.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

from _i1_s6_fixtures import evaluate_add_one


def test_add_one_of_41_is_42_as_a_positive_control():
    """Given the same program, when the Owner supplies 41 as runtime
    input as the positive control, then the reported result is exactly
    42."""
    response = evaluate_add_one(41)

    assert response.get("status") == "completed", f"expected a successful evaluation: {response}"
    result = response.get("result") or {}
    assert result.get("value") == "42", f"expected 42, got {response}"
