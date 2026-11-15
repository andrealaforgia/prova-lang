"""Shared fixtures for feature F2's acceptance tests: the programs whose
calls form a cycle, the acyclic controls that differ from them by one
call, the two shipped programs with a cycle injected into a copy, and a
runner that keeps the command's exit code and standard error so a crash
stays visible instead of being hidden behind an assertion.

Not itself a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
from dataclasses import dataclass

from _reservation_fixtures import reservation_source

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
HOUR_CLOCK_PATH = REPO_ROOT / "examples" / "hour-clock.prova"

# The category a refused program carries when its calls form a cycle. Part
# of the tool's public response vocabulary, not an internal symbol.
CYCLE_CATEGORY = "cyclic_dependency"

# --- a function that calls itself, and the same function without the call

SELF_CALLING_COUNTDOWN = """\
(defn countdown
  (sig ((n Int)) -> Int ! pure)
  (examples (example (countdown 1) => 0))
  (countdown (- n 1)))
"""

ONE_STEP_COUNTDOWN = """\
(defn countdown
  (sig ((n Int)) -> Int ! pure)
  (examples (example (countdown 1) => 0))
  (- n 1))
"""

# --- two functions that call each other, and the same pair with one call
# --- replaced so that only one of them calls the other

MUTUALLY_CALLING_STEPS = """\
(defn even-steps
  (sig ((n Int)) -> Int ! pure)
  (examples (example (even-steps 2) => 0))
  (odd-steps (- n 1)))

(defn odd-steps
  (sig ((n Int)) -> Int ! pure)
  (examples (example (odd-steps 1) => 0))
  (even-steps (- n 1)))
"""

ONE_WAY_STEPS = """\
(defn even-steps
  (sig ((n Int)) -> Int ! pure)
  (examples (example (even-steps 2) => 0))
  (odd-steps (- n 1)))

(defn odd-steps
  (sig ((n Int)) -> Int ! pure)
  (examples (example (odd-steps 1) => 0))
  (- n 1))
"""

# --- a cycle that exists only because a contract clause makes it: the
# --- body of `balance` calls nothing at all

CONTRACT_ONLY_CYCLE = """\
(defn balance
  (sig ((n Int)) -> Int ! pure)
  (ensures (= (balance result) result))
  (examples (example (balance 1) => 1))
  n)
"""

CONTRACT_CALLS_ANOTHER_FUNCTION = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 3) => 6))
  (+ n n))

(defn balance
  (sig ((n Int)) -> Int ! pure)
  (ensures (= (doubled result) (doubled n)))
  (examples (example (balance 1) => 1))
  n)
"""

# --- a function whose two declared examples both name that same function

EXAMPLES_NAME_THEIR_OWN_FUNCTION = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples
    (example (doubled 3) => 6)
    (example (doubled 0) => 0))
  (+ n n))
"""

EXAMPLES_PLUS_A_SELF_CALLING_BODY = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples
    (example (doubled 3) => 6)
    (example (doubled 0) => 0))
  (+ n (doubled n)))
"""

# --- three functions that call each other round, declared in the order in
# --- which they call: `gather` calls `summarise`, `summarise` calls
# --- `publish`, `publish` calls `gather` again

REPORT_CYCLE_DECLARED_IN_CALL_ORDER = """\
(defn gather
  (sig ((n Int)) -> Int ! pure)
  (examples (example (gather 1) => 1))
  (+ (summarise n) n))

(defn summarise
  (sig ((n Int)) -> Int ! pure)
  (examples (example (summarise 1) => 1))
  (+ (publish n) n))

(defn publish
  (sig ((n Int)) -> Int ! pure)
  (examples (example (publish 1) => 1))
  (+ (gather n) n))
"""

REPORT_CYCLE_IN_DECLARATION_ORDER = ("gather", "summarise", "publish")

# --- three functions that call each other round, declared against the
# --- order in which they call: `audit` calls `refund`, `refund` calls
# --- `settle`, `settle` calls `audit` again, but the program declares
# --- them audit, settle, refund. No rotation of the call chain gives that
# --- order, so a report written from the order the calls run in differs
# --- from a report written from the order the program declares.

LEDGER_CYCLE_DECLARED_AGAINST_CALL_ORDER = """\
(defn audit
  (sig ((n Int)) -> Int ! pure)
  (examples (example (audit 1) => 1))
  (+ (refund n) n))

(defn settle
  (sig ((n Int)) -> Int ! pure)
  (examples (example (settle 1) => 1))
  (+ (audit n) n))

(defn refund
  (sig ((n Int)) -> Int ! pure)
  (examples (example (refund 1) => 1))
  (+ (settle n) n))
"""

LEDGER_CYCLE_IN_DECLARATION_ORDER = ("audit", "settle", "refund")

# --- the shipped programs, and the one-call edit that makes each cyclic

HOUR_CLOCK_GUARD = "(>= (.hr current) 1)"
RESERVATION_GUARD = "(>= (.reserved current) 0)"
GUARD_THAT_CALLS_ITS_OWN_FUNCTION = "(valid-state current)"


def hour_clock_source() -> str:
    return HOUR_CLOCK_PATH.read_text(encoding="utf-8")


def with_a_self_calling_guard(source: str, guard: str) -> str:
    """`source` with its one `valid-state` range guard replaced by a call
    to `valid-state` itself, so the program's calls form a cycle and
    nothing else about it changes."""
    occurrences = source.count(guard)
    if occurrences != 1:
        raise AssertionError(
            f"expected exactly 1 occurrence of {guard!r} to replace, found {occurrences}: "
            "the shipped source changed shape, so this fixture no longer injects "
            "the cycle it names; update the guard text it looks for"
        )
    return source.replace(guard, GUARD_THAT_CALLS_ITS_OWN_FUNCTION, 1)


@dataclass(frozen=True)
class ToolRun:
    """One run of the `prova` command: everything the operating system and
    the command reported, kept so a test can observe a crash."""

    exit_code: int
    stdout: str
    stderr: str

    def response(self) -> dict:
        try:
            return json.loads(self.stdout)
        except (json.JSONDecodeError, ValueError):
            raise AssertionError(
                "the command's answer is not valid JSON, so a caller cannot read an "
                f"outcome from it; it printed {self.stdout!r} on standard output and "
                f"{self.stderr[-400:]!r} on standard error. The command must answer "
                "every request with one JSON response."
            ) from None

    def shows_a_crash(self) -> bool:
        return "Traceback (most recent call last)" in self.stderr


def run(request: dict) -> ToolRun:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=30.0,
    )
    return ToolRun(proc.returncode, proc.stdout, proc.stderr)


def check(source: str) -> ToolRun:
    return run({"prova": "i1", "operation": "check", "source": source})


def evaluate(source: str, function: str, arguments: list[str]) -> ToolRun:
    return run(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": source,
            "function": function,
            "arguments": arguments,
        }
    )


def declared_examples(source: str) -> ToolRun:
    return run({"prova": "i1", "operation": "examples", "source": source})


def reported_cycles(response: dict) -> list[frozenset[str]]:
    """The set of function names each reported cycle diagnostic names, one
    entry per such diagnostic. A set: which member a cycle is written from
    first is a presentation choice the criteria do not fix."""
    return [
        frozenset(diagnostic.get("cycle") or ())
        for diagnostic in response.get("diagnostics") or []
        if diagnostic.get("category") == CYCLE_CATEGORY
    ]


def cycle_members(response: dict) -> list[tuple[str, ...]]:
    """The function names each reported cycle diagnostic names, in the
    order that diagnostic writes them, one entry per such diagnostic.

    `reported_cycles` reads the same field as a set, for the tests whose
    promise is membership alone; this reader keeps the order, for the
    tests whose promise is that a reader meets the names in the order the
    program declares them.
    """
    return [
        tuple(diagnostic.get("cycle") or ())
        for diagnostic in response.get("diagnostics") or []
        if diagnostic.get("category") == CYCLE_CATEGORY
    ]


def cycle_reasons(response: dict) -> list[str]:
    return [
        diagnostic.get("reason") or ""
        for diagnostic in response.get("diagnostics") or []
        if diagnostic.get("category") == CYCLE_CATEGORY
    ]


def accepted(run_result: ToolRun) -> bool:
    response = run_result.response()
    return response.get("status") == "completed" and not response.get("diagnostics")


__all__ = [
    "CONTRACT_CALLS_ANOTHER_FUNCTION",
    "CONTRACT_ONLY_CYCLE",
    "CYCLE_CATEGORY",
    "EXAMPLES_NAME_THEIR_OWN_FUNCTION",
    "EXAMPLES_PLUS_A_SELF_CALLING_BODY",
    "HOUR_CLOCK_GUARD",
    "LEDGER_CYCLE_DECLARED_AGAINST_CALL_ORDER",
    "LEDGER_CYCLE_IN_DECLARATION_ORDER",
    "MUTUALLY_CALLING_STEPS",
    "ONE_STEP_COUNTDOWN",
    "ONE_WAY_STEPS",
    "REPORT_CYCLE_DECLARED_IN_CALL_ORDER",
    "REPORT_CYCLE_IN_DECLARATION_ORDER",
    "RESERVATION_GUARD",
    "SELF_CALLING_COUNTDOWN",
    "ToolRun",
    "accepted",
    "check",
    "cycle_members",
    "cycle_reasons",
    "declared_examples",
    "evaluate",
    "hour_clock_source",
    "reported_cycles",
    "reservation_source",
    "run",
    "with_a_self_calling_guard",
]
