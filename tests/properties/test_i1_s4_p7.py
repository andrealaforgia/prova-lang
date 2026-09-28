"""I1.S4.P7 / I1.S4.B4 / I1.S4.CHAR1: the protected reservation example and
its runtime oracle survive the mutation campaign unchanged.

Given SPEC.md's Core conformance example at the pinned preparation baseline,
when compared against the same region at the candidate revision, then it is
unchanged beyond formatting. The before/after-execution bracket runs a fresh
campaign and lives in test_i1_s4_p7_pinned_snapshots.py.
"""

from __future__ import annotations

import subprocess

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

    assert candidate_region.split() == baseline_region.split(), (
        "SPEC.md's protected reservation example changed beyond formatting "
        f"since baseline {BASELINE_SHA}"
    )
