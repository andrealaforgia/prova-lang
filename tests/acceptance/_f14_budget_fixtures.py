"""Shared fixtures for F14: the budgets every operation runs under, the
runs that pass one of them, and the answers a caller must get instead.

Not a test module (no `test_` prefix); pytest will not collect it. Every
helper drives the real `prova` command over its own stdin/stdout surface
and reads its exit code, because a command that ends in a traceback, or
never comes back at all, is exactly what these tests exist to see. A
budget a test lowers is lowered the way the manifest says a caller
lowers it, so the tests use the published surface and nothing else. No
imports from src/prova.
"""

from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass

from _r1_robustness_fixtures import (  # the programs this repository ships
    hour_clock_source,
    shipped_programs,
)

# The status every answer carries when a budget this tool declares was
# passed. The same status R1 already answers a passed limit with.
RESOURCE_EXHAUSTED = "resource_exhausted"
INVALID_INPUT = "invalid_input"

# The name the manifest gives each budget, and the name the refusal
# carries, so a caller meeting a refusal can look the number up.
INPUT_SIZE = "input_size"
OPERATION_TIME = "operation_time"
PEAK_MEMORY = "peak_memory"
ANSWER_SIZE = "answer_size"
BUDGET_NAMES = (INPUT_SIZE, OPERATION_TIME, PEAK_MEMORY, ANSWER_SIZE)

# The category of the refusal each budget answers with.
CATEGORY_OF = {
    INPUT_SIZE: "input_budget_exceeded",
    OPERATION_TIME: "time_budget_exceeded",
    PEAK_MEMORY: "memory_budget_exceeded",
    ANSWER_SIZE: "output_budget_exceeded",
}

# The numbers the Owner decided (docs/ROADMAP.md section 5, D5, approved
# in section 8): 1 MiB of source, 10 s, 512 MiB of memory, 1 MiB of
# answer, written in the unit each budget is published in.
DECLARED = {
    INPUT_SIZE: 1024 * 1024,
    OPERATION_TIME: 10_000,
    PEAK_MEMORY: 512 * 1024 * 1024,
    ANSWER_SIZE: 1024 * 1024,
}

# The fields a refusal carries beside its category and its sentence.
SYMBOL = "symbol"
EXPECTED = "expected"
ACTUAL = "actual"

# Words a budget refusal may never use: four that would turn a budget of
# this tool into a statement about what a program means, and three that
# would claim work this tool did not do (SPEC.md lines 280-284, 503-508).
FORBIDDEN_WORDS = (
    "bound",
    "bounded",
    "domain",
    "verified",
    "proved",
    "proof",
    "total",
)

# The keys an answer carries only when the tool really read a program.
SEMANTIC_KEYS = ("claim", "result", "source_digest", "contract_report")


def variable_for(budget: str) -> str:
    """The environment variable a caller sets to lower one budget for one
    run, spelled the way the manifest publishes it."""
    return f"PROVA_BUDGET_{budget.upper()}"


@dataclass(frozen=True)
class ToolRun:
    exit_code: int
    stdout: str
    stderr: str

    def response(self) -> dict:
        try:
            return json.loads(self.stdout)
        except (json.JSONDecodeError, ValueError):
            raise AssertionError(
                "the tool's answer is not JSON a caller can read, so there is "
                f"no outcome in it: it exited {self.exit_code} and printed "
                f"{self.stdout[:400]!r} on standard output and "
                f"{self.stderr[-800:]!r} on standard error. Every request gets "
                "one complete JSON answer; a traceback, a half-written answer "
                "or nothing at all is not one. Answer the request with a "
                "refusal in a published category instead."
            ) from None

    def assert_answered(self, why: str) -> dict:
        assert self.exit_code == 0, (
            f"the tool exited {self.exit_code} for {why}, not 0: a caller "
            "reading the exit code learns the tool broke rather than that it "
            f"stopped inside a budget. Standard error held "
            f"{self.stderr[-800:]!r}. Answer with a refusal in a published "
            "category and exit 0."
        )
        assert self.stderr.strip() == "", (
            f"the tool wrote {self.stderr[-800:]!r} on standard error for "
            f"{why}: a caller reading only standard output would miss it, and "
            "a traceback there means a budget decided control flow by "
            "escaping. Answer the request instead."
        )
        return self.response()


def run(request: object, lowered: dict | None = None, timeout: float = 30.0) -> ToolRun:
    """One run of the real command, with each named budget lowered the
    way the manifest says a caller lowers it.

    `timeout` is the test's own patience, not a measurement: a command
    that never comes back raises here instead of hanging the suite.
    """
    environment = dict(os.environ)
    for budget, maximum in (lowered or {}).items():
        environment[variable_for(budget)] = str(maximum)
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=timeout,
        check=False,
        env=environment,
    )
    return ToolRun(proc.returncode, proc.stdout, proc.stderr)


def run_with_environment(request: object, variables: dict) -> ToolRun:
    """One run with exactly the variables given, whatever they spell: the
    way a caller that mistyped a name or a number meets the tool."""
    environment = dict(os.environ)
    environment.update(variables)
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=30.0,
        check=False,
        env=environment,
    )
    return ToolRun(proc.returncode, proc.stdout, proc.stderr)


def answered(request: object, why: str, lowered: dict | None = None) -> dict:
    return run(request, lowered).assert_answered(why)


def check(source: str, why: str, lowered: dict | None = None) -> dict:
    return answered(
        {"prova": "i1", "operation": "check", "source": source}, why, lowered
    )


def discover(lowered: dict | None = None) -> dict:
    return answered({"prova": "i1", "operation": "discover"}, "the manifest", lowered)


def published_budgets(manifest: dict) -> dict:
    """What the manifest says each operation's budgets are.

    Every test reads the numbers from here rather than from the tool's
    source, because the promise is that a caller can read them before it
    meets one.
    """
    limits = manifest.get("result", {}).get("resource_limits", {})
    budgets = limits.get("budgets")
    assert isinstance(budgets, dict) and budgets, (
        f"the manifest states no budgets for any operation: {limits}. A caller "
        "must read the input, time, memory and answer budget it runs under "
        "before it sends work, not learn it by being refused. Publish them "
        "under 'budgets' in the resource limits the 'discover' operation "
        "answers with, one entry per operation."
    )
    return budgets


def budget_entry(manifest: dict, operation: str, budget: str) -> dict:
    budgets = published_budgets(manifest)
    assert operation in budgets, (
        f"the manifest states no budgets for the {operation!r} operation: it "
        f"states them for {sorted(budgets)}. Every operation this tool offers "
        "runs under a budget, so every one of them states it."
    )
    entry = budgets[operation].get(budget)
    assert isinstance(entry, dict), (
        f"the manifest states no {budget!r} budget for {operation!r}: it "
        f"states {sorted(budgets[operation])}. A caller reads the four "
        f"budgets {list(BUDGET_NAMES)} under their published names."
    )
    return entry


def the_refusal(response: dict, category: str, why: str) -> dict:
    """The one refusal of `category` in `response`, or a failure saying
    what came instead."""
    found = [
        entry
        for entry in (response.get("diagnostics") or [])
        if entry.get("category") == category
    ]
    assert len(found) == 1, (
        f"the answer to {why} carries {len(found)} refusals of category "
        f"{category!r}, expected exactly 1: {response}. A caller matches on "
        "one cause; none leaves it with nothing to handle and two leave it "
        "unable to say which budget stopped the run."
    )
    return found[0]


def assert_claims_nothing(response: dict, why: str) -> None:
    """The answer to a passed budget claims no result about the program
    and says nothing about what a program may mean."""
    for key in SEMANTIC_KEYS:
        assert key not in response, (
            f"the answer to {why} carries {key!r}: {response}. The tool "
            "stopped inside a budget it declares, so it read no rule of the "
            "language over the text and has nothing to report about it. Carry "
            "the status and the refusal and nothing else."
        )
    prose = " ".join(
        str(entry.get("reason", "")) for entry in (response.get("diagnostics") or [])
    ).lower()
    used = [word for word in FORBIDDEN_WORDS if word in prose]
    assert not used, (
        f"the refusal for {why} uses {used}: {prose!r}. A budget of this tool "
        "says how much work it does, never what a program may mean or what "
        "was checked; wording like that turns a budget of the runner into a "
        "rule about the mathematics of the program (SPEC.md lines 503-508 and "
        "280-284). Say which budget stopped the run, the number and how to "
        "stay under it."
    )


def assert_names_the_budget(
    refusal: dict, budget: str, maximum: int, reached: int | None, why: str
) -> None:
    assert refusal.get(SYMBOL) == budget, (
        f"the refusal for {why} names {refusal.get(SYMBOL)!r}: {refusal}. It "
        f"names {budget!r}, the name the manifest publishes the number under, "
        "so a caller meeting the refusal can look that budget up and change "
        "what it sends."
    )
    assert refusal.get(EXPECTED) == maximum, (
        f"the refusal for {why} says {refusal.get(EXPECTED)!r} was allowed "
        f"while the run's budget was {maximum}: {refusal}. One number, in one "
        "place: two disagreeing numbers leave a caller unable to pick a size."
    )
    if reached is not None:
        assert refusal.get(ACTUAL) == reached, (
            f"the refusal for {why} says the run reached "
            f"{refusal.get(ACTUAL)!r}, expected {reached}: {refusal}. A caller "
            "reads how far past the budget it went from this number."
        )
    else:
        assert isinstance(refusal.get(ACTUAL), int) and refusal[ACTUAL] >= maximum, (
            f"the refusal for {why} reports {refusal.get(ACTUAL)!r} reached "
            f"against a budget of {maximum}: {refusal}. The amount reached is "
            "a whole number and is at least the budget, or the refusal "
            "contradicts itself."
        )
    assert str(maximum) in str(refusal.get("reason", "")), (
        f"the refusal for {why} does not say {maximum} in its sentence: "
        f"{refusal.get('reason')!r}. A person reading the message is told the "
        "number to stay under without opening the manifest."
    )
    assert str(refusal.get(ACTUAL)) in str(refusal.get("reason", "")), (
        f"the refusal for {why} reports {refusal.get(ACTUAL)!r} reached and "
        f"does not say it in its sentence: {refusal.get('reason')!r}. The "
        "sentence a person reads and the number a program reads are the same "
        "number; two that disagree leave a reader unable to say how far past "
        "the budget the run went."
    )


def source_of_exactly(size: int) -> str:
    """A source of exactly `size` bytes that costs nothing to read: one
    comment line, which carries no declaration at all.

    A text with nothing but a comment declares nothing, so the tool would
    refuse it for that if it ever read it. It never does: a source past
    the input budget is refused before any rule of the language is read
    over it, which is the point of sending this one.
    """
    assert size >= 1, "a source of fewer than 1 byte cannot be written"
    text = ";" + "x" * (size - 1)
    assert len(text.encode("utf-8")) == size
    return text


def within_every_budget() -> str:
    """The smallest shipped program, far inside every declared budget."""
    return hour_clock_source()


__all__ = [
    "ACTUAL",
    "ANSWER_SIZE",
    "BUDGET_NAMES",
    "CATEGORY_OF",
    "DECLARED",
    "EXPECTED",
    "FORBIDDEN_WORDS",
    "INPUT_SIZE",
    "INVALID_INPUT",
    "OPERATION_TIME",
    "PEAK_MEMORY",
    "RESOURCE_EXHAUSTED",
    "SYMBOL",
    "ToolRun",
    "answered",
    "assert_claims_nothing",
    "assert_names_the_budget",
    "budget_entry",
    "check",
    "discover",
    "hour_clock_source",
    "published_budgets",
    "run",
    "run_with_environment",
    "shipped_programs",
    "source_of_exactly",
    "the_refusal",
    "variable_for",
    "within_every_budget",
]
