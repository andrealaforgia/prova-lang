"""Oracle-side helpers for F14's property tests: one run of the real
`prova` command, with the budgets a caller lowered.

Not a test module (no `test_` prefix); pytest will not collect it. It
talks to the command over its stdin/stdout surface only, and imports
nothing from src/prova: the laws below are about what a caller reads,
not about how the tool is written.
"""

from __future__ import annotations

import json
import os
import subprocess

INPUT_SIZE = "input_size"
OPERATION_TIME = "operation_time"
PEAK_MEMORY = "peak_memory"
ANSWER_SIZE = "answer_size"
BUDGET_NAMES = (INPUT_SIZE, OPERATION_TIME, PEAK_MEMORY, ANSWER_SIZE)

CATEGORY_OF = {
    INPUT_SIZE: "input_budget_exceeded",
    OPERATION_TIME: "time_budget_exceeded",
    PEAK_MEMORY: "memory_budget_exceeded",
    ANSWER_SIZE: "output_budget_exceeded",
}
DECLARED = {
    INPUT_SIZE: 1024 * 1024,
    OPERATION_TIME: 10_000,
    PEAK_MEMORY: 512 * 1024 * 1024,
    ANSWER_SIZE: 1024 * 1024,
}
# The smallest value of each budget that no run of this tool can fit in,
# so a case that lowers one is really a run past it.
NOTHING_FITS_IN = {
    INPUT_SIZE: 1,
    OPERATION_TIME: 0,
    PEAK_MEMORY: 1,
    ANSWER_SIZE: 1,
}

RESOURCE_EXHAUSTED = "resource_exhausted"
SEMANTIC_KEYS = ("claim", "result", "source_digest", "contract_report")
FORBIDDEN_WORDS = ("bound", "bounded", "domain", "verified", "proved", "proof", "total")

# The operations that read the program a request carries, and the ones
# this tool offers in all.
READS_A_SOURCE = ("check", "examples", "evaluate", "verify", "parse")
OFFERED = ("check", "examples", "evaluate", "verify", "parse", "discover")


def variable_for(budget: str) -> str:
    return f"PROVA_BUDGET_{budget.upper()}"


def printed_answer(request: dict, lowered: dict | None = None) -> str:
    environment = dict(os.environ)
    for budget, maximum in (lowered or {}).items():
        environment[variable_for(budget)] = str(maximum)
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=30.0,
        check=False,
        env=environment,
    )
    assert proc.returncode == 0 and proc.stderr.strip() == "", (
        f"the tool exited {proc.returncode} for {request.get('operation')!r} "
        f"with {lowered} lowered and wrote {proc.stderr[-400:]!r} on standard "
        "error: every request gets one JSON answer and exit 0, whichever "
        "budget stopped it."
    )
    return proc.stdout


def answer(request: dict, lowered: dict | None = None) -> dict:
    text = printed_answer(request, lowered)
    try:
        return json.loads(text)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(
            f"the answer to {request.get('operation')!r} with {lowered} "
            f"lowered is not JSON: {text[:400]!r}. A caller reads one complete "
            "answer per request; a cut-short answer is not one."
        ) from None


def refusals(response: dict, category: str) -> list:
    return [
        entry
        for entry in (response.get("diagnostics") or [])
        if entry.get("category") == category
    ]


def program_of(functions: int) -> str:
    """A legal program of `functions` functions, each answering 1.

    Nothing in it is deep, long-running or recursive: only its size
    changes with the number asked for, which is what the laws about the
    input budget need.
    """
    written = []
    for place in range(functions):
        written.append(
            f"(defn f{place}\n"
            "  (sig () -> Int ! pure)\n"
            f"  (examples (example (f{place}) => 1))\n"
            "  1)"
        )
    return "\n".join(written) + "\n"


def comment_of_exactly(size: int) -> str:
    """A source of exactly `size` bytes holding one comment: the
    cheapest text of a known size there is."""
    text = ";" + "x" * (size - 1)
    assert len(text.encode("utf-8")) == size
    return text
