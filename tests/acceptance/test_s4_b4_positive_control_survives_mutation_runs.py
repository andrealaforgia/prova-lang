"""Acceptance test for I1.S4.B4: the unmodified reservation source is the
positive control around the mutation campaign in I1.S4.B1-B3. Run against
it, every result is reported as satisfying its postcondition for the
supplied inputs, no report describes these runtime checks as universal
proof, and the protected source and its expected outcomes are unchanged by
the mutation runs.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SPEC_ORACLE_SHA = "ee5e1556b3a5e06945a02a61ef3a4cad51744b12"

STEP_BODY_OLD = (
    "  (match event\n"
    "    ((Reserve)\n"
    "      (if (< (.reserved current) 2)\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) true)\n"
    "          (Outcome current false)))\n"
    "    ((Release)\n"
    "      (if (> (.reserved current) 0)\n"
    "          (Outcome (Reservation (- (.reserved current) 1)) true)\n"
    "          (Outcome current false)))))\n"
)

ALWAYS_REJECT_BODY_NEW = "  (Outcome current false))\n"

# (count, event) -> (expected_result_count, expected_accepted), read off the
# six-row transition table in SPEC.md's Core conformance example.
EXPECTED = {
    (0, "Reserve"): (1, True),
    (1, "Reserve"): (2, True),
    (2, "Reserve"): (2, False),
    (0, "Release"): (0, False),
    (1, "Release"): (0, True),
    (2, "Release"): (1, True),
}

FORBIDDEN_UNIVERSAL_WORDS = ("verified", "proved", "proven", "universal", " holds ", "guarantee")


def _spec_text_at(sha: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{sha}:SPEC.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _reservation_source_at(sha: str) -> str:
    text = _spec_text_at(sha)
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _evaluate_step(source: str, current_text: str, event: str) -> dict:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": "step",
        "arguments": [current_text, f"({event})"],
    }
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure evaluating step: stderr={proc.stderr!r}"
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response evaluating step: {proc.stdout!r}")


def test_b4_unmodified_source_satisfies_every_postcondition_and_stays_unchanged():
    """Given the unmodified reservation source as the positive control,
    when the Owner runs the same operation against it, then every result
    is reported as satisfying its postcondition for the supplied inputs;
    no report describes these runtime checks as universal proof, and the
    protected source and its expected outcomes are unchanged by the
    mutation runs."""
    source = _reservation_source_at(SPEC_ORACLE_SHA)
    on_disk_before = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")

    responses = []
    for (count, event), (expected_count, expected_accepted) in EXPECTED.items():
        response = _evaluate_step(source, f"(Reservation {count})", event)
        responses.append(response)
        assert response.get("status") == "completed", (
            f"unmodified step((Reservation {count}), {event}) must satisfy its "
            f"postcondition: {response}"
        )
        result = response.get("result") or {}
        assert result.get("value") == f"(Outcome (Reservation {expected_count}) {'true' if expected_accepted else 'false'})", (
            f"unexpected result for step((Reservation {count}), {event}): {response}"
        )

    # Run the three mutation sources too (the campaign this control brackets),
    # each in its own fresh process, then re-check the control is undisturbed.
    occurrences = source.count(STEP_BODY_OLD)
    assert occurrences == 1
    mutant_bodies = [
        "  (match event\n"
        "    ((Reserve)\n"
        "      (if true\n"
        "          (Outcome (Reservation (+ (.reserved current) 1)) true)\n"
        "          (Outcome current false)))\n"
        "    ((Release)\n"
        "      (if (> (.reserved current) 0)\n"
        "          (Outcome (Reservation (- (.reserved current) 1)) true)\n"
        "          (Outcome current false)))))\n",
        "  (match event\n"
        "    ((Reserve)\n"
        "      (if (< (.reserved current) 2)\n"
        "          (Outcome (Reservation (+ (.reserved current) 1)) false)\n"
        "          (Outcome current true)))\n"
        "    ((Release)\n"
        "      (if (> (.reserved current) 0)\n"
        "          (Outcome (Reservation (- (.reserved current) 1)) false)\n"
        "          (Outcome current true)))))\n",
        ALWAYS_REJECT_BODY_NEW,
    ]
    for new_body in mutant_bodies:
        mutated = source.replace(STEP_BODY_OLD, new_body, 1)
        _evaluate_step(mutated, "(Reservation 0)", "Reserve")

    for response in responses:
        text = json.dumps(response).lower()
        for word in FORBIDDEN_UNIVERSAL_WORDS:
            assert word not in text, f"response claims more than a runtime check ({word!r}): {response}"

    assert source == _reservation_source_at(SPEC_ORACLE_SHA), (
        "the protected source text changed after the mutation runs"
    )
    on_disk_after = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    assert on_disk_after == on_disk_before, "SPEC.md on disk changed during the mutation campaign"
