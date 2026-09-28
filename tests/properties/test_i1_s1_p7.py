"""I1.S1.P7 / I1.S1.CHAR1: the protected reservation example is unchanged.

Given SPEC.md's Core conformance example read from the immutable baseline
commit `ee5e155...` (SPEC.md blob `7ea9095...`, itself asserted here) and
from the candidate's SPEC.md, when the two regions are compared token by
token, then Reservation/Event/Outcome, valid-state/initial/step with their
contracts, all seven declared examples, the six-row transition table and the
normative prose are identical. Only meaning-preserving formatting differences
(whitespace, line wrapping, indentation, line endings, spacing around
parentheses and table pipes) are tolerated; anything else fails.

The guard is shown to be sensitive by isolated mutations of the baseline
region (capacity, the input precondition, an acceptance guarantee, a declared
example, and each of the 24 table cells), each of which must be reported as a
difference, and to be tolerant by formatting-only positive controls, each of
which must be reported as equivalent. Neither side of any comparison is
derived from the candidate.
"""

from __future__ import annotations

import re
import subprocess

import pytest

from _prova_client import REPO_ROOT, SPEC_ORACLE_SHA, protected_region

BASELINE_BLOB = "7ea909543707fb2abadac95c6b3fba94a32cfaa3"


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True, check=True
    ).stdout


def normalise(region: str) -> list[str]:
    """Token stream that ignores only formatting: parentheses and table pipes
    are separate tokens; all whitespace (including CRLF) separates tokens."""
    spaced = re.sub(r"([()|])", r" \1 ", region)
    return spaced.split()


def equivalent(baseline: str, candidate: str) -> bool:
    return normalise(baseline) == normalise(candidate)


BASELINE_TEXT = _git("show", f"{SPEC_ORACLE_SHA}:SPEC.md")
BASELINE_REGION = protected_region(BASELINE_TEXT)


def test_p7_baseline_is_the_fixed_oracle():
    assert _git("rev-parse", f"{SPEC_ORACLE_SHA}:SPEC.md").strip() == BASELINE_BLOB
    assert BASELINE_REGION.count("(example ") == 7, "seven declared examples expected in the oracle region"
    assert BASELINE_REGION.count("| 0 | Reserve | 1 | true |") == 1


def test_p7_protected_reservation_region_matches_baseline():
    candidate_region = protected_region((REPO_ROOT / "SPEC.md").read_text(encoding="utf-8"))
    if not equivalent(BASELINE_REGION, candidate_region):
        pytest.fail(
            "SPEC.md's protected reservation example changed beyond formatting "
            f"since baseline {SPEC_ORACLE_SHA}:\n"
            f"--- baseline ---\n{BASELINE_REGION}\n--- candidate ---\n{candidate_region}"
        )


def _replace_once(old: str, new: str) -> str:
    assert BASELINE_REGION.count(old) == 1, f"mutation anchor not unique in the oracle: {old!r}"
    return BASELINE_REGION.replace(old, new, 1)


NAMED_MUTATIONS = {
    "capacity in valid-state": _replace_once("(<= (.reserved current) 2)", "(<= (.reserved current) 3)"),
    "capacity in step guarantee": _replace_once("((Reserve) (< (.reserved current) 2))", "((Reserve) (< (.reserved current) 3))"),
    "capacity in step body": _replace_once("(if (< (.reserved current) 2)\n", "(if (< (.reserved current) 3)\n"),
    "input precondition": _replace_once("(requires (valid-state current))", "(requires true)"),
    "acceptance guarantee": _replace_once(
        "((Release) (> (.reserved current) 0))))", "((Release) (>= (.reserved current) 0))))"
    ),
    "delta guarantee": _replace_once("(match event ((Reserve) 1) ((Release) -1))", "(match event ((Reserve) 1) ((Release) -2))"),
    "declared example outcome": _replace_once(
        "=> (Outcome (Reservation 2) false)", "=> (Outcome (Reservation 2) true)"
    ),
    "declared example removed": _replace_once(
        "\n    (example (step (Reservation 0) (Release)) => (Outcome (Reservation 0) false)))", ")"
    ),
    "type field": _replace_once("(record (reserved Int))", "(record (reserved Nat))"),
    "initial value": _replace_once("(= result (Reservation 0))", "(= result (Reservation 1))"),
}


def _table_mutations() -> dict[str, str]:
    mutations = {}
    lines = BASELINE_REGION.splitlines()
    columns = ("before", "event", "after", "accepted")
    for index, line in enumerate(lines):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 4 or not (cells[0].isdigit() and cells[1] in ("Reserve", "Release")):
            continue
        for column, name in enumerate(columns):
            changed = list(cells)
            value = cells[column]
            changed[column] = {
                "Reserve": "Release", "Release": "Reserve", "true": "false", "false": "true",
            }.get(value, str((int(value) + 1) % 3) if value.isdigit() else value)
            mutated_lines = list(lines)
            mutated_lines[index] = "| " + " | ".join(changed) + " |"
            mutations[f"table row {cells[0]}/{cells[1]} cell {name}"] = "\n".join(mutated_lines) + "\n"
    return mutations


TABLE_MUTATIONS = _table_mutations()


def test_p7_table_mutations_cover_every_cell():
    assert len(TABLE_MUTATIONS) == 24


@pytest.mark.parametrize("name", sorted({**NAMED_MUTATIONS, **TABLE_MUTATIONS}))
def test_p7_guard_detects_isolated_mutation(name):
    mutated = {**NAMED_MUTATIONS, **TABLE_MUTATIONS}[name]
    assert mutated != BASELINE_REGION, f"mutation {name!r} did not change the region"
    assert not equivalent(BASELINE_REGION, mutated), f"the guard missed mutation {name!r}"


FORMATTING_ONLY = {
    "crlf line endings": lambda t: t.replace("\n", "\r\n"),
    "trailing whitespace": lambda t: t.replace("\n", "   \n"),
    "re-indented": lambda t: re.sub(r"(?m)^ +", "        ", t),
    "unwrapped code lines": lambda t: t.replace("\n    (example", " (example").replace("\n  (", " ("),
    "extra blank lines": lambda t: t.replace("\n", "\n\n"),
    "spaces inside parentheses": lambda t: t.replace("(Outcome", "( Outcome").replace("true)", "true )"),
    "table pipe spacing": lambda t: re.sub(r"(?m)^\| (\d) \| (\w+) \| (\d) \| (\w+) \|$", r"|\1|\2|\3|\4|", t),
    "tabs for spaces": lambda t: t.replace("  ", "\t"),
}


@pytest.mark.parametrize("name", sorted(FORMATTING_ONLY))
def test_p7_guard_tolerates_formatting_only_change(name):
    changed = FORMATTING_ONLY[name](BASELINE_REGION)
    assert changed != BASELINE_REGION, f"formatting control {name!r} did not change the region"
    assert equivalent(BASELINE_REGION, changed), f"the guard rejected formatting-only change {name!r}"
