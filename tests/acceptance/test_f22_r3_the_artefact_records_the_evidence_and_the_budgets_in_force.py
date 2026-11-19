"""What an artefact records about the evidence behind it, and under
which budgets that evidence was reached.

Two things an independent review found. The evidence digest was in the
header and in the answer and was compared with nothing: a digest the
Owner cannot recompute says only that two fields of one answer agree.
And the recorded budgets were the numbers this tool declares rather than
the numbers the run stood inside, so an artefact built under a budget
the caller lowered recorded a configuration the program was never
verified under.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import tempfile

from _f22_fixtures import artefact_of, ask, build, header_of, hour_clock

A = "=>"

ANOTHER_PROGRAM = f"""(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (requires (>= n 0))
  (ensures (>= result 0))
  (examples (example (doubled 3) {A} 6))
  (* 2 n))
"""


def _the_digest_of_the_evidence(source: str) -> str:
    """The digest of what certified `source`, recomputed the way the
    manifest says it is taken: over the canonical JSON text of the
    aggregate and the inventory the `verify` answer for the same source
    carries, with the keys sorted and nothing between them.
    """
    verified = ask({"operation": "verify", "source": source})
    assert verified.get("status") == "completed", verified
    canonical = json.dumps(
        {"aggregate": verified["aggregate"], "inventory": verified["result"]},
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def test_the_recorded_evidence_digest_is_the_digest_of_the_verification():
    """Given a build of the shipped hour clock, when the Owner recomputes
    the digest of the evidence from the `verify` answer for the same
    source, then it is the digest the artefact records -- and the digest
    of another program's evidence is not.

    still passes if: the digest had been taken over something stable but
    unrelated -- it is computed here from the answer the Owner can ask
    for themselves, and the negative control requires a different
    program to have a different one.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        recorded = header_of(
            _built(hour_clock(), "step", destination / "clock.py")
        )
        other = header_of(
            _built(ANOTHER_PROGRAM, "doubled", destination / "doubled.py")
        )

    expected = _the_digest_of_the_evidence(hour_clock())
    assert recorded["evidence_digest"] == expected, (
        f"WHAT: the artefact records the evidence digest "
        f"{recorded['evidence_digest']!r} and the digest of the verification "
        f"of the same source is {expected!r}. "
        "WHY: the digest ties the artefact to evidence the Owner can ask for "
        "again; one they cannot recompute ties it to nothing. "
        "HOW: take it over the canonical text the manifest describes."
    )
    assert other["evidence_digest"] == _the_digest_of_the_evidence(
        ANOTHER_PROGRAM
    ), other
    assert other["evidence_digest"] != recorded["evidence_digest"], (
        "WHAT: two programs with different obligations and different "
        "examples have the same evidence digest. "
        "WHY: the digest would then say nothing about which evidence it is. "
        f"HOW: inspect the two: {recorded} {other}"
    )


def _built(source: str, entry: str, target: pathlib.Path) -> pathlib.Path:
    artefact_of(build(source, entry, target), f"the program built for {entry}")
    return target


def test_the_recorded_budgets_are_the_ones_the_run_stood_inside():
    """Given a build under the budgets this tool declares and a build of
    the same program with the input budget lowered to 2000 bytes, when
    the Owner reads the two artefacts, then the first records 1048576
    bytes as declared and the second records 2000 as lowered.

    still passes if: the artefact had recorded the lowered number for
    both -- the first build is required to record the declared one.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        under_the_declared = _built(
            hour_clock(), "step", destination / "declared.py"
        )
        lowered_target = destination / "lowered.py"
        artefact_of(
            build(
                hour_clock(),
                "step",
                lowered_target,
                lowered={"PROVA_BUDGET_INPUT_SIZE": "2000"},
            ),
            "the hour clock under a lowered input budget",
        )
        declared = header_of(under_the_declared)["configuration"]["budgets"]
        lowered = header_of(lowered_target)["configuration"]["budgets"]

    assert declared["input_size"]["maximum"] == 1024 * 1024, (
        f"WHAT: a build under no lowered budget recorded "
        f"{declared['input_size']} for the source it reads. "
        "WHY: that run stood inside the number this tool declares. "
        f"HOW: inspect the artefact: {declared}"
    )
    assert declared["input_size"]["basis"] == "declared", declared["input_size"]
    assert lowered["input_size"]["maximum"] == 2000, (
        f"WHAT: a build under PROVA_BUDGET_INPUT_SIZE=2000 recorded "
        f"{lowered['input_size']} for the source it reads. "
        "WHY: the program was verified inside the number the caller chose, "
        "and the configuration an artefact records is the one it was "
        "verified under -- not the one this tool would have used. "
        f"HOW: record the budgets of the run: {lowered}"
    )
    assert lowered["input_size"]["basis"] == "lowered", (
        f"WHAT: the lowered budget says it rests on "
        f"{lowered['input_size'].get('basis')!r}. "
        "WHY: a reader must be able to tell a number this tool declares from "
        "one a caller set. "
        f"HOW: say which of the two it is: {lowered['input_size']}"
    )
    for name in ("operation_time", "peak_memory", "answer_size"):
        assert declared[name] == lowered[name], (
            f"WHAT: the {name} budget differs between the two builds: "
            f"{declared[name]} against {lowered[name]}. "
            "WHY: only the input budget was lowered. "
            "HOW: record each budget as it stood."
        )
