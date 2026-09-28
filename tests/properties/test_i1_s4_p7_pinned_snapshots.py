"""I1.S4.P7 (pinned snapshots): the protected reservation example at the
candidate revision equals the reference at ee5e155 (token-aware, every
declaration, example and table cell), the source used by the runtime controls
is that candidate source, and the protected source and expected outcomes are
byte-identical before mutation construction, after construction and after
execution.
"""

from __future__ import annotations

import subprocess

from _i1_s4_v4 import PINNED_TABLE, campaign, read_forms, run_campaign, sha256, sources
from _i1_s4_fixtures import MUTANTS, mutated_source
from _prova_client import REPO_ROOT, SPEC_ORACLE_SHA, _extract_reservation_source, protected_region

START = "## Core conformance example"


def _reference_spec() -> str:
    return subprocess.run(["git", "show", f"{SPEC_ORACLE_SHA}:SPEC.md"], cwd=REPO_ROOT, capture_output=True,
                          text=True, check=True).stdout


def _candidate_spec() -> str:
    return (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")


def _tokens(text: str) -> list[str]:
    import re
    return re.findall(r"\(|\)|\||[^\s()|]+", text)


def _table_rows(region: str) -> list[tuple[int, str, int, bool]]:
    rows = []
    for line in region.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and cells[0].isdigit():
            rows.append((int(cells[0]), cells[1], int(cells[2]), cells[3] == "true"))
    return rows


def test_p7_protected_section_is_token_identical_to_the_pinned_reference():
    assert _tokens(protected_region(_candidate_spec())) == _tokens(protected_region(_reference_spec()))


def test_p7_source_trees_examples_and_table_cells_match_the_reference():
    ref, cand = protected_region(_reference_spec()), protected_region(_candidate_spec())
    ref_forms, cand_forms = read_forms(_extract_reservation_source(_reference_spec())), read_forms(
        _extract_reservation_source(_candidate_spec()))
    assert ref_forms == cand_forms
    assert [f[1] for f in cand_forms if f[0] == "deftype"] == ["Reservation", "Event", "Outcome"]
    assert [f[1] for f in cand_forms if f[0] == "defn"] == ["valid-state", "initial", "step"]
    examples = [c for f in cand_forms if f[0] == "defn" for c in f if isinstance(c, list) and c[:1] == ["examples"]]
    assert sum(len(e) - 1 for e in examples) == 7
    assert _table_rows(cand) == _table_rows(ref)
    assert {(b, e): (a, acc) for b, e, a, acc in _table_rows(cand)} == PINNED_TABLE


def test_p7_runtime_controls_use_the_candidate_protected_source():
    candidate_source = _extract_reservation_source(_candidate_spec())
    assert sources()["protected"] == candidate_source
    protected_digest = sha256(candidate_source)
    controls = [c for c in campaign() if c.label.startswith("control")]
    assert len(controls) == 12
    assert {c.source_digest for c in controls} == {protected_digest}
    assert {c.response["source_digest"] for c in controls} == {protected_digest}


def _working_tree_digest() -> str:
    """Digest of every file execution could touch: SPEC.md, the conformance
    tree and the evidence fixtures, read from the working tree."""
    import hashlib
    h = hashlib.sha256()
    paths = [REPO_ROOT / "SPEC.md"]
    for d in ("conformance", "evidence"):
        root = REPO_ROOT / d
        if root.is_dir():
            paths += sorted(p for p in root.rglob("*") if p.is_file())
    for path in paths:
        h.update(str(path.relative_to(REPO_ROOT)).encode() + b"\0" + path.read_bytes() + b"\0")
    return h.hexdigest()


def test_p7_protected_snapshots_agree_before_after_construction_and_after_execution():
    """Runs a fresh, uncached campaign (control, three mutants, control) between
    the snapshots, so the bracket surrounds real executions."""
    snapshot = lambda: (_working_tree_digest(), sha256(_extract_reservation_source(_candidate_spec())),
                        tuple(sorted(PINNED_TABLE.items())))
    before = snapshot()
    built = {m.id: mutated_source(m) for m in MUTANTS}
    after_construction = snapshot()
    calls = run_campaign()
    after_execution = snapshot()
    assert len(calls) == 30 and all(c.response is not None for c in calls)
    assert before == after_construction == after_execution
    assert all(sha256(s) != sha256(_extract_reservation_source(_candidate_spec())) for s in built.values())
