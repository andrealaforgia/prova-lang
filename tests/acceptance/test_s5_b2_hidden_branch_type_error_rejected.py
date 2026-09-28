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

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

RESERVE_OLD = "(Outcome (Reservation (+ (.reserved current) 1)) true)"
RESERVE_BUG = (
    "(Outcome (Reservation (if (= (.reserved current) 1) "
    "(+ true 1) (+ (.reserved current) 1))) true)"
)

# step's four declared examples call Reserve only with 0 and 2 -- neither
# equals 1, so neither reaches the injected branch's true arm.
DECLARED_RESERVE_INPUTS = [0, 2]
FRESH_RESERVE_INPUT = 1


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _reserve_bug_source() -> str:
    source = _reservation_source()
    assert source.count(RESERVE_OLD) == 1
    return source.replace(RESERVE_OLD, RESERVE_BUG, 1)


def _run_check(source: str) -> dict:
    request = {"prova": "i1", "operation": "check", "source": source}
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response: {proc.stdout!r}")


def test_b2_declared_examples_never_reach_the_injected_site():
    assert FRESH_RESERVE_INPUT not in DECLARED_RESERVE_INPUTS


def test_b2_hidden_type_error_in_steps_branch_is_rejected():
    """Given a hand-built variant with a type error placed inside one of
    step's two branches, in a spot none of the four declared examples
    reaches, when the Owner runs the check operation against it, then the
    tool rejects the program."""
    response = _run_check(_reserve_bug_source())

    assert response.get("operation") == "check", response
    assert response.get("status") == "invalid_program", (
        f"expected the variant to be rejected as an invalid program, got: {response}"
    )
    assert response.get("diagnostics"), (
        f"rejection carried no diagnostics: {response}"
    )
