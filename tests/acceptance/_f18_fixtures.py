"""Shared helpers for F18's acceptance tests: how an answer is asked for
over the real `prova` command, and how the parts of a verify answer are
read out of it.

Not a test module (no `test_` prefix); pytest will not collect it.
Drives only the command's real JSON stdin/stdout surface, as the other
acceptance fixtures here do. No imports from src/prova.

Every answer is asked once per process and kept, so a file that reads
several things about one answer pays for one run of the command.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# The four words a logical obligation result may carry and the seven an
# execution status may carry, as SPEC.md lines 270-284 fix them. No word
# belongs to both.
LOGICAL_RESULTS = ("proved", "disproved", "unknown", "not_attempted")
EXECUTION_STATUSES = (
    "completed",
    "unsupported",
    "timed_out",
    "cancelled",
    "resource_exhausted",
    "invalid_input",
    "tool_failure",
)

# How an obligation that was settled says what settled it: a solver that
# was asked, or a rule of core-0 that settles it without one. SPEC.md,
# "Results and evidence scope": the inventory identifies structurally
# discharged checks as well as solver checks.
WAYS_OF_DISCHARGING = ("solver", "structure")

_ANSWERS: dict = {}


def ask(request: dict) -> dict:
    """The one answer the installed command gives to `request`."""
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=60.0,
    )
    assert proc.returncode == 0, (
        f"WHAT: the command exited {proc.returncode} for "
        f"{request.get('operation')!r} instead of answering. "
        "WHY: every request is answered, and a run that stops with nothing "
        "on standard output leaves a caller with no verdict at all. "
        f"HOW: read the failure on its error output: {proc.stderr[-600:]!r}"
    )
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(
            f"WHAT: the answer to {request.get('operation')!r} is not JSON: "
            f"{proc.stdout[:600]!r}. "
            "WHY: a caller reads one JSON object per answer. "
            "HOW: inspect what the command printed."
        )


def verify(source: str) -> dict:
    """What the Owner is told when they ask what a program owes and
    whether it is owed no longer."""
    key = ("verify", source)
    if key not in _ANSWERS:
        _ANSWERS[key] = ask({"operation": "verify", "source": source})
    return _ANSWERS[key]


def evaluate(source: str, function: str, arguments: list) -> dict:
    """What the Owner is told when they run one function of a program
    over values written the way a program writes them."""
    return ask(
        {
            "operation": "evaluate",
            "source": source,
            "function": function,
            "arguments": list(arguments),
        }
    )


def the_manifest() -> dict:
    if "manifest" not in _ANSWERS:
        _ANSWERS["manifest"] = ask({"operation": "discover"})
    return _ANSWERS["manifest"]


def completed(answer: dict, about: str) -> dict:
    assert answer.get("status") == "completed", (
        f"WHAT: the verify answer about {about} has status "
        f"{answer.get('status')!r}, not 'completed'. "
        "WHY: the obligations of a program are read out of a completed "
        "answer; a refusal carries none. "
        f"HOW: inspect the answer: {answer}"
    )
    return answer


def obligations_of(answer: dict, about: str) -> list:
    """Every obligation the answer lists, with the list refusing to be
    empty: a file that reads entries out of an empty list would pass
    while the tool listed nothing at all."""
    entries = (
        ((answer.get("result") or {}).get("inventory") or {}).get("obligations")
    ) or []
    assert entries, (
        f"WHAT: the verify answer about {about} lists no obligation. "
        "WHY: every function of a core-0 program owes a contract, a body "
        "and a termination entry at least, so an empty list is a tool that "
        "listed nothing rather than a program that owes nothing. "
        f"HOW: inspect the answer: {answer}"
    )
    return entries


def totals_of(answer: dict) -> dict:
    return (
        ((answer.get("result") or {}).get("inventory") or {}).get("totals")
    ) or {}


def results_by_identity(answer: dict, about: str) -> dict:
    """What each obligation of the answer stands as, by its identity."""
    return {entry["id"]: entry["result"] for entry in obligations_of(answer, about)}


def entry_named(answer: dict, identity: str, about: str) -> dict:
    for entry in obligations_of(answer, about):
        if entry["id"] == identity:
            return entry
    raise AssertionError(
        f"WHAT: the answer about {about} lists no obligation {identity!r}; it "
        f"lists {[entry['id'] for entry in obligations_of(answer, about)]}. "
        "WHY: this test is about that obligation, and an answer that drops it "
        "has skipped what it was asked about. "
        "HOW: inspect the answer and the program it is about."
    )


def not_proved(answer: dict, about: str) -> list:
    """Every obligation of the answer that did not come back proved, as
    pairs a reader can act on."""
    return [
        (entry["id"], entry["result"])
        for entry in obligations_of(answer, about)
        if entry.get("result") != "proved"
    ]
