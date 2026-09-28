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

import re

from _reservation_fixtures import reservation_source, reserve_bug_source, run_check

FRESH_RESERVE_INPUT = 1

# Matches `(example (step (Reservation N) (Reserve)) ...)` in the real
# SPEC.md source text, capturing N -- the `current.reserved` value each
# declared Reserve example is actually called with.
DECLARED_RESERVE_EXAMPLE = re.compile(
    r"\(example \(step \(Reservation (-?\d+)\) \(Reserve\)\)"
)


def test_b2_declared_examples_never_reach_the_injected_site():
    """The injected defect only fires when `current.reserved` = 1. This
    reads the protected source's own declared examples for `step` (Reserve)
    calls and confirms none of them passes 1 -- if SPEC.md's examples ever
    changed to include 1, this would fail, since the defect would then be
    reachable by a declared example rather than only by a fresh input."""
    declared_reserve_inputs = [
        int(value) for value in DECLARED_RESERVE_EXAMPLE.findall(reservation_source())
    ]
    assert declared_reserve_inputs, "found no declared Reserve examples for step"
    assert FRESH_RESERVE_INPUT not in declared_reserve_inputs, (
        f"declared Reserve examples {declared_reserve_inputs} already reach "
        f"current.reserved={FRESH_RESERVE_INPUT}, so the injected defect is not hidden"
    )


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
