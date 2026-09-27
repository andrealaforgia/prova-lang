"""I1.S5.P6 / I1.S5.CHAR1 / I1.S5.B1: the protected reservation example's
semantics, contracts and expected outcomes are unchanged at the candidate
revision.

Given SPEC.md's Core conformance example at the preparation baseline
compared against the candidate revision, when the two are diffed ignoring
only formatting, then they match word-for-word. Given the same protected
source, when `check` accepts it, `examples` runs all seven declared
examples and `evaluate` runs all six transition-table inputs, then every
declared example passes, every transition matches the independently
recorded table, results stay within the valid state range, and a rejected
event leaves the state unchanged -- at the same candidate revision, so a
concurrent edit to SPEC.md cannot validate itself against a stale fixture.
"""

from __future__ import annotations

import subprocess

import pytest

from _i1_s5_fixtures import assert_accepted, protected_source, run_check
from _prova_client import BASELINE_SHA, REPO_ROOT, parse_value, run_prova

START_HEADING = "## Core conformance example"
END_HEADING = "## Empirical evaluation"

# Independent inventory of the seven declared examples, transcribed by hand
# from SPEC.md -- not imported from any other story's fixture module, so a
# shared bug in one inventory cannot hide behind agreement with another.
INVENTORY = [
    ("valid-state", 0, ["(Reservation 0)"], "true"),
    ("valid-state", 1, ["(Reservation 3)"], "false"),
    ("initial", 0, [], "(Reservation 0)"),
    ("step", 0, ["(Reservation 0)", "(Reserve)"], "(Outcome (Reservation 1) true)"),
    ("step", 1, ["(Reservation 2)", "(Reserve)"], "(Outcome (Reservation 2) false)"),
    ("step", 2, ["(Reservation 1)", "(Release)"], "(Outcome (Reservation 0) true)"),
    ("step", 3, ["(Reservation 0)", "(Release)"], "(Outcome (Reservation 0) false)"),
]

assert len(INVENTORY) == 7

# Independent oracle: SPEC.md's six-row transition table, copied by hand.
TABLE = [
    (0, "Reserve", 1, True),
    (1, "Reserve", 2, True),
    (2, "Reserve", 2, False),
    (0, "Release", 0, False),
    (1, "Release", 0, True),
    (2, "Release", 1, True),
]

assert {(before, event) for before, event, _, _ in TABLE} == {
    (0, "Reserve"), (1, "Reserve"), (2, "Reserve"),
    (0, "Release"), (1, "Release"), (2, "Release"),
}


def _protected_region(spec_text: str) -> str:
    start = spec_text.index(START_HEADING)
    end = spec_text.index(END_HEADING, start)
    return spec_text[start:end]


def _baseline_spec_text() -> str:
    result = subprocess.run(
        ["git", "show", f"{BASELINE_SHA}:SPEC.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def test_p6_protected_reservation_region_matches_baseline():
    baseline_region = _protected_region(_baseline_spec_text())
    candidate_text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    candidate_region = _protected_region(candidate_text)
    assert candidate_region.split() == baseline_region.split(), (
        f"SPEC.md's protected reservation example changed beyond formatting since baseline {BASELINE_SHA}"
    )


def test_p6_check_accepts_the_protected_source_with_no_errors():
    source = protected_source()
    returncode, response, stdout, stderr = run_check(source)
    assert_accepted(returncode, response, stdout, stderr)


def test_p6_all_seven_declared_examples_still_pass():
    source = protected_source()
    request = {"prova": "i1", "operation": "examples", "source": source}
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") == "completed", response
    results = ((response.get("result") or {}).get("examples")) or []
    assert len(results) == 7, f"expected seven example results, got {len(results)}: {results}"
    indexed = {(e.get("function"), e.get("ordinal")): e for e in results}
    for function, ordinal, arguments, expected in INVENTORY:
        entry = indexed.get((function, ordinal))
        assert entry is not None, f"missing example result for {(function, ordinal)}: {results}"
        assert entry.get("passed") is True, f"{(function, ordinal)} did not pass: {entry}"
        assert parse_value(entry.get("expected")) == parse_value(expected), (
            f"{(function, ordinal)}: response expected {entry.get('expected')!r} "
            f"does not match the independent inventory {expected!r}"
        )
        assert parse_value(entry.get("actual")) == parse_value(expected), (
            f"{(function, ordinal)}: actual {entry.get('actual')!r} does not match {expected!r}"
        )


def _evaluate_step(before: int, event: str):
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": protected_source(),
        "function": "step",
        "arguments": [f"(Reservation {before})", f"({event})"],
    }
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0, f"tool failure evaluating step({before}, {event}): stderr={stderr!r}"
    assert response is not None, f"non-JSON response evaluating step({before}, {event}): {stdout!r}"
    assert response.get("status") == "completed", response
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text, f"no result value for step({before}, {event}): {response}"
    ctor, args = parse_value(value_text)
    assert ctor == "Outcome" and len(args) == 2, f"unexpected result shape: {value_text!r}"
    state_value, accepted_value = args
    state_ctor, state_args = state_value
    assert state_ctor == "Reservation" and len(state_args) == 1
    return state_args[0], accepted_value


@pytest.mark.parametrize("before,event,expected_after,expected_accepted", TABLE)
def test_p6_all_six_transitions_still_match_the_table(before, event, expected_after, expected_accepted):
    after, accepted = _evaluate_step(before, event)
    assert 0 <= after <= 2, f"step({before}, {event}) left the valid range: after={after}"
    assert (after, accepted) == (expected_after, expected_accepted), (
        f"step({before}, {event}) expected (after={expected_after}, accepted={expected_accepted}), "
        f"got (after={after}, accepted={accepted})"
    )
    if not expected_accepted:
        assert after == before, f"rejected step({before}, {event}) changed state to {after}"
