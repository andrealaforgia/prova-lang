"""Acceptance test for I1.S5.B2: a hand-built variant with a type error
placed inside one of `step`'s two branches, in a spot none of the four
declared examples reaches, is rejected by the check operation.

The variant replaces the Reserve accepted arm's integer expression with a
nested `if` whose `true` branch does `(+ true 1)` -- a Bool operand of a
numeric operator. It only fires when `(.reserved current) = 1`; step's four
declared examples call it with 0 and 2, never 1, so no declared example
reaches the defect. A fresh input within the contract domain (1) does.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

from _reservation_fixtures import reserve_bug_source, run_check

# step's four declared examples call Reserve only with 0 and 2 -- neither
# equals 1, so neither reaches the injected branch's true arm.
DECLARED_RESERVE_INPUTS = [0, 2]
FRESH_RESERVE_INPUT = 1


def test_b2_declared_examples_never_reach_the_injected_site():
    assert FRESH_RESERVE_INPUT not in DECLARED_RESERVE_INPUTS


def test_b2_hidden_type_error_in_steps_branch_is_rejected():
    """Given a hand-built variant with a type error placed inside one of
    step's two branches, in a spot none of the four declared examples
    reaches, when the Owner runs the check operation against it, then the
    tool rejects the program."""
    response = run_check(reserve_bug_source())

    assert response.get("operation") == "check", response
    assert response.get("status") == "invalid_program", (
        f"expected the variant to be rejected as an invalid program, got: {response}"
    )
    assert response.get("diagnostics"), (
        f"rejection carried no diagnostics: {response}"
    )
