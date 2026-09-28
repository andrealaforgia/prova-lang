"""Acceptance test for I1.S6.INT: Story I1.S6 works end to end through the
product's real surface -- preserve exact arbitrarily large integers
through direct evaluation.

Exercises the whole story together, each case its own fresh `prova`
process: beyond both 2^53 and 2^63-1 positive (I1.S6.B1), below -2^63
(I1.S6.B2), beyond 2^53 but within 64-bit range on both signs (I1.S6.B3),
and the small positive control (I1.S6.B4). This is the union of B1-B4's
own values run through the same helper, kept as the story-level check
that runs alongside them rather than in place of them; it does not add
assertion power beyond running B1-B4 together.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova; every expected result is
computed independently with Python's own arbitrary-precision `int`
arithmetic, not read from the implementation.
"""

from __future__ import annotations

from _i1_s6_acceptance_fixtures import evaluate_add_one

CASES = [
    9223372036854775808,  # 2**63: beyond both 2**53 and 2**63 - 1
    -9223372036854775810,  # below -2**63
    9007199254740993,  # beyond 2**53, within 64-bit range
    -9007199254740995,  # beyond 2**53, within 64-bit range, negative
    41,  # positive control
]


def test_int_add_one_is_exact_across_every_declared_magnitude_end_to_end():
    """Given the separate add-one program, when the Owner supplies, across
    fresh runtime inputs and separate tool invocations, integers spanning
    both sides of 2^53 and 2^63-1 plus the 41-to-42 positive control, then
    every reported result is exactly that input plus one, never the input
    echoed back and never a value consistent with binary64 rounding or
    64-bit wraparound."""
    for n in CASES:
        expected = n + 1
        response = evaluate_add_one(n)

        assert response.get("status") == "completed", f"expected a successful evaluation of add-one({n}): {response}"
        result = response.get("result") or {}
        value_text = result.get("value")
        assert value_text is not None, f"no successful result value for add-one({n}): {response}"
        assert value_text != str(n), f"result echoes input {n} back instead of adding one: {response}"
        assert value_text == str(expected), f"add-one({n}): expected {expected}, got {value_text!r}: {response}"
