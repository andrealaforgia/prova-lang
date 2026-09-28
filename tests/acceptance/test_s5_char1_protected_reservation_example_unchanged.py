"""I1.S5.CHAR1 characterization: the protected reservation example in
SPEC.md (capacity two, `step`'s contract, its declared examples and the
six-row transition table) is unchanged at the candidate revision;
formatting-only differences are permitted.

This is a characterization guard: it must PASS now, before any
implementation for this story exists, and keep passing through the story.
Pinned to the same baseline commit as I1.S1.CHAR1/I1.S3.CHAR1: this story
does not introduce a second, independent oracle for the same protected
region.
"""

from __future__ import annotations

import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

BASELINE_SHA = "30fcbe9dda345d5b7283790023032c0145765428"


def _protected_region(spec_text: str) -> str:
    start = spec_text.index("## Core conformance example")
    end = spec_text.index("## Empirical evaluation", start)
    return spec_text[start:end]


def _spec_text_at(sha: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{sha}:SPEC.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def test_char1_protected_reservation_example_unchanged_at_candidate_revision():
    baseline = _protected_region(_spec_text_at(BASELINE_SHA)).split()
    candidate = _protected_region((REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")).split()

    assert candidate == baseline, (
        "the protected reservation example (types, capacity, contracts, "
        "declared examples, six-row transition table) changed beyond "
        "formatting since the baseline commit"
    )
