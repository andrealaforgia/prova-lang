"""I1.S3.P7 / I1.S3.CHAR1: the protected reservation example is unchanged,
and its declared examples, table and invalid-entry behaviour still execute
as recorded.

Given SPEC.md's Core conformance example at the fixed baseline commit
30fcbe9dda345d5b7283790023032c0145765428, when compared against the same
region at the candidate revision, then the source text is unchanged up to
insignificant whitespace (the source-comparison half of this check, shared
with I1.S1.P7). Supplementing that comparison -- not replacing it -- this
module also executes the source's seven declared examples, the six-row
table and the four invalid-state/event cases from P1/P2 against the
candidate `prova` binary, so a source-level match is corroborated by
matching behaviour. Never refresh the baseline from the candidate.
"""

from __future__ import annotations

import subprocess

import pytest

from _i1_s2_fixtures import INVENTORY
from _i1_s3_fixtures import (
    PRECONDITION_CATEGORY,
    TABLE,
    assert_rejected,
    assert_success_outcome,
    evaluate_step,
)
from _prova_client import (
    BASELINE_SHA,
    REPO_ROOT,
    load_reservation_source,
    parse_value,
    run_prova,
)

START_HEADING = "## Core conformance example"
END_HEADING = "## Empirical evaluation"


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


def test_p7_protected_reservation_region_matches_baseline():
    baseline_region = _protected_region(_baseline_spec_text())
    candidate_text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    candidate_region = _protected_region(candidate_text)

    baseline_tokens = baseline_region.split()
    candidate_tokens = candidate_region.split()

    if candidate_tokens != baseline_tokens:
        pytest.fail(
            "SPEC.md's protected reservation example changed beyond formatting "
            f"since baseline {BASELINE_SHA}:\n"
            f"--- baseline ---\n{baseline_region}\n--- candidate ---\n{candidate_region}"
        )


@pytest.mark.parametrize(
    "entry",
    INVENTORY,
    ids=[f"{e['function']}-{e['ordinal']}" for e in INVENTORY],
)
def test_p7_every_declared_example_still_evaluates_as_recorded(entry):
    source = load_reservation_source()
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": entry["function"],
        "arguments": entry["arguments"],
    }
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0, f"tool failure evaluating {entry}: stderr={stderr!r}"
    assert response is not None, f"non-JSON response for {entry}: {stdout!r}"
    assert response.get("status") == "completed", f"declared example {entry} did not succeed: {response}"
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text, f"declared example {entry} carried no result value: {response}"
    assert parse_value(value_text) == parse_value(entry["expected"]), (
        f"declared example {entry} returned {value_text!r}, expected {entry['expected']!r}"
    )


@pytest.mark.parametrize("before,event,after,accepted", TABLE, ids=[f"{b}-{e}" for b, e, _, _ in TABLE])
def test_p7_table_row_still_holds(before, event, after, accepted):
    returncode, response, stdout, stderr = evaluate_step(f"(Reservation {before})", event)
    assert_success_outcome(
        returncode, response, stdout, stderr,
        expected_state=after, expected_accepted=accepted,
    )


@pytest.mark.parametrize(
    "before,event",
    [(3, "Reserve"), (3, "Release"), (-1, "Reserve"), (-1, "Release")],
)
def test_p7_invalid_entry_states_still_reject(before, event):
    returncode, response, stdout, stderr = evaluate_step(f"(Reservation {before})", event)
    assert_rejected(returncode, response, stdout, stderr, category=PRECONDITION_CATEGORY)
