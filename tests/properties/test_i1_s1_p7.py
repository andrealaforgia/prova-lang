"""I1.S1.P7 / I1.S1.CHAR1: the protected reservation example is unchanged.

Given SPEC.md's Core conformance example at the fixed preparation baseline
commit, when compared against the exact same region at the candidate
revision, then Reservation/Event/Outcome, valid-state/initial/step and their
contracts, all seven declared examples and the six-row transition table are
byte-identical up to insignificant whitespace, with any other difference
failing this check rather than silently becoming a new oracle.

This guard is expected to pass now, before any implementation exists, and
must keep passing through the story; it is not evidence that a criterion
has been newly satisfied.
"""

from __future__ import annotations

import subprocess

import pytest

from _prova_client import BASELINE_SHA, REPO_ROOT

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
