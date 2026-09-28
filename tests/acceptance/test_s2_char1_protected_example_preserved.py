"""I1.S2.CHAR1 characterization: the protected reservation example in
SPEC.md (capacity two, `step`'s contract, its declared examples and the
six-row transition table) is unchanged from the pinned oracle commit;
formatting-only differences are permitted.

This is a characterization guard: it must PASS now, before any
implementation exists, and keep passing through the story.
"""

from __future__ import annotations

import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# The SPEC.md commit that first published the reservation example, used as
# the independent oracle for this guard.
ORACLE_SHA = "ee5e1556b3a5e06945a02a61ef3a4cad51744b12"


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


def test_char1_protected_reservation_example_unchanged_since_oracle():
    baseline = _protected_region(_spec_text_at(ORACLE_SHA)).split()
    candidate = _protected_region((REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")).split()

    assert candidate == baseline, (
        "the protected reservation example (types, capacity, contracts, "
        "declared examples, six-row transition table) changed beyond "
        "formatting since the oracle commit"
    )
