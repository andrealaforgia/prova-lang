"""The programs F13 reads a contract report about, and the one way these
tests talk to the tool.

Not a test module (no `test_` prefix); pytest will not collect it.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova: every expected strength below is read by hand
from the source text written here, never from the answer under
observation.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# Words that would describe the program as meaningfully correct. Read by
# hand from the request's own sentence ("nothing in the answer describes
# the program as meaningfully correct") and from the words a reader of a
# checker would take for a statement about the program itself. Scanned
# over the whole answer, keys and values alike. `check` is the
# operation's public name and says nothing about an outcome, so it is
# not listed.
CLAIM_WORD = re.compile(
    r"\b(correct|correctness|meaningful|meaningfully|verified|verifies|"
    r"verification|proved|proven|proves|proof|guaranteed|sound|holds|"
    r"satisfied|discharged)\b",
    re.IGNORECASE,
)

# A function with no `requires` block at all: its precondition is
# omitted, and its postcondition states a real relation between the
# argument and the result.
NO_PRECONDITION = """
(defn twice
  (sig ((n Int)) -> Int ! pure)
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""

# A function whose `ensures` block is literally `true`: it promises
# nothing, while its `requires` narrows the input to positive numbers.
TRIVIAL_POSTCONDITION = """
(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures true)
  (examples (example (twice 2) => 4))
  (* n 2))
"""

# A function whose two blocks each say something: neither is omitted and
# neither is written as the literal `true`.
REAL_CONTRACT = """
(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""

# Two functions and four blocks, every one of them omitted or literally
# `true`: nothing in this program promises anything.
PROMISES_NOTHING = """
(defn twice
  (sig ((n Int)) -> Int ! pure)
  (examples (example (twice 2) => 4))
  (* n 2))

(defn thrice
  (sig ((n Int)) -> Int ! pure)
  (requires true)
  (ensures true)
  (examples (example (thrice 2) => 6))
  (* n 3))
"""

# A program that declares a type and no function at all.
NO_FUNCTION_AT_ALL = "(deftype Clock (record (hr Int)))"

# The hour clock this repository ships, read by hand from
# examples/hour-clock.prova: its three functions in the order it declares
# them, and what each of its two contract blocks says there.
#   valid-state declares neither block.
#   initial declares (ensures (valid-state result)) and no requires.
#   step declares (requires (valid-state current)) and three ensures
#   clauses, none of them the literal true.
CLOCK_CONTRACTS = {
    "valid-state": ("omitted", "omitted"),
    "initial": ("omitted", "stated"),
    "step": ("stated", "stated"),
}


def hour_clock_source() -> str:
    return (REPO_ROOT / "examples" / "hour-clock.prova").read_text(encoding="utf-8")


def _ask(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=20.0,
    )
    assert proc.returncode == 0, (
        f"the tool exited {proc.returncode} instead of 0 for request "
        f"{request.get('operation')!r}. An answered request exits 0; a "
        f"non-zero exit means the request was not read at all. stderr: "
        f"{proc.stderr!r}"
    )
    return json.loads(proc.stdout)


def ask(operation: str, source: str) -> dict:
    """The answer of any operation that reads a program, so a test can ask
    every one of them the same question."""
    return _ask({"operation": operation, "source": source})


def check(source: str) -> dict:
    return _ask({"operation": "check", "source": source})


def verify(source: str) -> dict:
    return _ask({"operation": "verify", "source": source})


def discover() -> dict:
    return _ask({"operation": "discover"})


def report_of(answer: dict) -> dict:
    """The contract report the answer carries, or a failure that says what
    is missing."""
    assert answer.get("status") == "completed", (
        f"the program was not accepted: {answer.get('status')!r} with "
        f"{answer.get('diagnostics')}. These programs keep every rule of "
        "core-0; repair the source in the fixtures before reading a report."
    )
    report = answer.get("contract_report")
    assert isinstance(report, dict), (
        f"the answer carries no contract report: keys {sorted(answer)}. The "
        "Owner reads which functions promise nothing from that report; add "
        "the report to the answer of the operation that carries it."
    )
    return report


def entries_by_function(report: dict) -> dict:
    entries = report.get("functions")
    assert isinstance(entries, list), (
        f"the report lists no functions: {report}. Every declared function "
        "is recorded once, so a reader can see each one at a glance."
    )
    by_name = {}
    for entry in entries:
        name = entry.get("function")
        assert name not in by_name, (
            f"the function {name!r} is recorded twice in one report: "
            f"{entries}. One entry names one function, so a reader counts "
            "each function once."
        )
        by_name[name] = entry
    return by_name


def claim_words_in(answer: dict) -> list:
    """Every word in the answer, keys and values alike, that would
    describe the program as meaningfully correct."""
    found = []

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                found.extend(CLAIM_WORD.findall(str(key)))
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)
        else:
            found.extend(CLAIM_WORD.findall(str(node)))

    walk(answer)
    return found
