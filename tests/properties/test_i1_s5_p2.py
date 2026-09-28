"""I1.S5.P2 / I1.S5.B1 / I1.S5.B2: `check` finds a hidden type error inside
`step` that none of its four declared examples reaches.

Given two hand-built variants -- a Bool operand of `+` in the Reserve
accepted arm, and a Bool operand of `-` in the Release accepted arm --
each unreachable by step's four declared examples but reachable by a fresh
valid input within the contract domain, when `check` runs against each,
then both are rejected as an invalid program, and their minimally corrected
counterparts (replacing the Bool literal with the original integer
expression) are accepted, alongside the unmodified positive control.
"""

from __future__ import annotations

import re

import pytest

from _prova_client import parse_value, run_prova

from _i1_s5_fixtures import (
    assert_accepted,
    assert_rejected_as_invalid_program,
    protected_source,
    release_bug_source,
    release_fix_source,
    reserve_bug_source,
    reserve_fix_source,
    run_check,
)


def test_p2_unmodified_source_is_the_positive_control():
    returncode, response, stdout, stderr = run_check(protected_source())
    assert_accepted(returncode, response, stdout, stderr)


DECLARED_STEP_EXAMPLES = re.compile(r"\(example \(step \(Reservation (\d)\) \((Reserve|Release)\)\)")


def _declared_step_inputs(source: str) -> set[tuple[int, str]]:
    return {(int(n), event) for n, event in DECLARED_STEP_EXAMPLES.findall(source)}


def _run(operation, source, **extra):
    request = {"prova": "i1", "operation": operation, "source": source, **extra}
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0 and response is not None, f"{operation}: stdout={stdout!r} stderr={stderr!r}"
    assert response.get("status") == "completed", f"{operation}: {response}"
    return response


@pytest.mark.parametrize(
    "fix_source,injected_input,fresh_input,expected_value",
    [
        pytest.param(reserve_fix_source, (1, "Reserve"), (1, "Reserve"), "(Outcome (Reservation 2) true)", id="reserve"),
        pytest.param(release_fix_source, (2, "Release"), (2, "Release"), "(Outcome (Reservation 1) true)", id="release"),
    ],
)
def test_p2_declared_examples_never_reach_the_injected_site_but_a_fresh_input_does(
    fix_source, injected_input, fresh_input, expected_value
):
    """Reachability through the public surface. The four declared step inputs
    are read from the submitted text; `examples` runs all of them on the
    repaired source and passes (so the declared inputs exercise the program),
    none is the input that selects the injected arm, and `evaluate` on the
    repaired source at the fresh witness returns the SPEC transition-table
    result (so the injected arm is reachable within step's contract)."""
    source = fix_source()
    declared = _declared_step_inputs(source)
    assert declared == {(0, "Reserve"), (2, "Reserve"), (1, "Release"), (0, "Release")}
    assert injected_input not in declared

    examples = _run("examples", source)["result"]["examples"]
    step_results = [e for e in examples if e.get("function") == "step"]
    assert len(step_results) == 4 and all(e.get("passed") is True for e in step_results), step_results

    n, event = fresh_input
    evaluated = _run(
        "evaluate", source, function="step", arguments=[f"(Reservation {n})", f"({event})"]
    )
    assert parse_value(evaluated["result"]["value"]) == parse_value(expected_value), evaluated


def test_p2_reserve_bug_is_rejected_as_invalid_program():
    returncode, response, stdout, stderr = run_check(reserve_bug_source())
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)


def test_p2_release_bug_is_rejected_as_invalid_program():
    returncode, response, stdout, stderr = run_check(release_bug_source())
    assert_rejected_as_invalid_program(returncode, response, stdout, stderr)


def test_p2_reserve_fix_is_accepted():
    returncode, response, stdout, stderr = run_check(reserve_fix_source())
    assert_accepted(returncode, response, stdout, stderr)


def test_p2_release_fix_is_accepted():
    returncode, response, stdout, stderr = run_check(release_fix_source())
    assert_accepted(returncode, response, stdout, stderr)


def test_p2_bug_and_fix_sources_actually_differ_from_the_control():
    control = protected_source()
    assert reserve_bug_source() != control
    assert reserve_fix_source() != control
    assert release_bug_source() != control
    assert release_fix_source() != control
    assert reserve_bug_source() != reserve_fix_source()
    assert release_bug_source() != release_fix_source()
