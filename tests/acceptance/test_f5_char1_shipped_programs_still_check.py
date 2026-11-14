"""Characterization test for F5: the programs this repository ships are
still accepted, and their declared examples still pass, after the rules
about hidden bindings and the reserved word `result` arrive.

These two programs are what a reader of the project meets first. One of
them reads `result` in its postconditions, which stays allowed. If a new
rule refused either of them, the rule would be wrong, not the program.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool accepted everything, or stopped checking
these sources at all. The same test adds one hiding binding to each
shipped program and requires that copy to be refused, so acceptance of
the shipped text means the rule ran on it and found nothing.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from _f5_binding_fixtures import accepted, check, run

REPOSITORY = Path(__file__).resolve().parents[2]
SHIPPED_PROGRAMS = ("examples/hour-clock.prova", "conformance/add-one.prova")


def _source_of(relative_path: str) -> str:
    return (REPOSITORY / relative_path).read_text(encoding="utf-8")


A_FUNCTION_WHOSE_LET_HIDES_ITS_PARAMETER = """

(defn probe
  (sig ((n Int)) -> Int ! pure)
  (examples (example (probe 4) => 4))
  (let ((n n)) n))
"""


@pytest.mark.parametrize("relative_path", SHIPPED_PROGRAMS, ids=lambda p: p)
def test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it(
    relative_path: str,
):
    """Given the program this repository ships at `relative_path`, when
    it is checked, then it is accepted with 0 diagnostics; and when the
    same program is checked with 1 function added whose `let` hides its
    own parameter, then that copy is invalid."""
    outcome = check(_source_of(relative_path))

    assert accepted(outcome), (
        f"the shipped program {relative_path} was refused: {outcome.response()}. A "
        "rule about bindings must not refuse a program the project ships; repair the "
        "rule, not the program."
    )

    with_a_hiding_binding = check(
        _source_of(relative_path) + A_FUNCTION_WHOSE_LET_HIDES_ITS_PARAMETER
    )

    assert with_a_hiding_binding.response().get("status") == "invalid_program", (
        f"{relative_path} with one hiding binding added was not refused: "
        f"{with_a_hiding_binding.response()}. Acceptance of the shipped text must "
        "mean the rule ran on it and found nothing, not that it was never applied."
    )


@pytest.mark.parametrize("relative_path", SHIPPED_PROGRAMS, ids=lambda p: p)
def test_the_declared_examples_of_a_shipped_program_still_pass(relative_path: str):
    """Given the same shipped program, when its declared examples run,
    then every one of them passes."""
    response = run(
        {
            "prova": "i1",
            "operation": "examples",
            "source": _source_of(relative_path),
        }
    ).response()

    results = response.get("result", {}).get("examples", [])
    failed = [entry for entry in results if not entry.get("passed")]
    assert results and not failed, (
        f"{len(failed)} of {len(results)} declared examples of {relative_path} did "
        f"not pass: {response}. The shipped programs must keep working."
    )
