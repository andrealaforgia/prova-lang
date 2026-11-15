"""Shared fixtures for feature F6's acceptance tests: programs that spell a
name or a marker the way the language does not define it, the almost
identical programs that spell it the way the language does define it, and
the helpers that read a refusal back.

Every refused program here has an accepted twin that differs only in the
one spelling under observation, so a test that observes a refusal is
always paired with a control that observes acceptance of nearly the same
program.

Not itself a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
from dataclasses import dataclass

# The category a program carries when it cannot be read as a program of
# the language. Part of the tool's published response vocabulary (the
# manifest lists it), not an internal symbol.
SPELLING_CATEGORY = "syntax"

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# --- the well spelled program every refused program below is a copy of

WELL_SPELLED = """\
(defn add-one
  (sig ((n Int)) -> Int ! pure)
  (examples (example (add-one 41) => 42))
  (+ n 1))
"""


def _function_named(name: str) -> str:
    """The well spelled program with its function named `name` instead of
    `add-one`, example call included."""
    return WELL_SPELLED.replace("add-one", name)


# --- 1. a reserved word used as a function name

# The words whose spelling the language refuses as a declared name: the
# core keywords and the builtin operator names, as SPEC.md lists them.
#
# `result` is not among them. SPEC.md reserves it for the value a
# postcondition speaks about, which is a rule about what a name binds
# rather than how a name is spelled, and the tool answers it with its own
# refusal from the whole-program check. Sweeping it here would ask the
# spelling rule for an answer another rule owns.
RESERVED_WORDS = (
    "deftype", "record", "union", "defn", "sig", "pure", "requires",
    "ensures", "examples", "example", "let", "if", "match", "true",
    "false",
    "+", "-", "*", "<", "<=", ">", ">=", "=", "and", "or", "not",
)


def program_with_function_named(name: str) -> str:
    return _function_named(name)


# A name the language allows and reserves nowhere: the control for the
# reserved-word refusals.
UNRESERVED_FUNCTION_NAME = "step-one"


# --- 2. names that start with the wrong case

FUNCTION_NAME_STARTING_WITH_A_CAPITAL = _function_named("Add-one")

PARAMETER_NAME_STARTING_WITH_A_CAPITAL = """\
(defn add-one
  (sig ((N Int)) -> Int ! pure)
  (examples (example (add-one 41) => 42))
  (+ N 1))
"""

TYPE_NAME_STARTING_LOWER_CASE = """\
(deftype point (record (x Int)))

(defn add-one
  (sig ((n Int)) -> Int ! pure)
  (examples (example (add-one 41) => 42))
  (+ n 1))
"""

TYPE_NAME_STARTING_UPPER_CASE = TYPE_NAME_STARTING_LOWER_CASE.replace(
    "point", "Point"
)

CONSTRUCTOR_NAME_STARTING_LOWER_CASE = """\
(deftype Colour (union (red) (Blue)))

(defn add-one
  (sig ((n Int)) -> Int ! pure)
  (examples (example (add-one 41) => 42))
  (+ n 1))
"""

CONSTRUCTOR_NAME_STARTING_UPPER_CASE = CONSTRUCTOR_NAME_STARTING_LOWER_CASE.replace(
    "(red)", "(Red)"
)

# --- a constructor spelled as a builtin type, and the same union whose
# --- constructors are named for themselves

CONSTRUCTOR_NAMED_AS_A_BUILTIN_TYPE = """\
(deftype Measure (union (Int) (Bool)))

(defn add-one
  (sig ((n Int)) -> Int ! pure)
  (examples (example (add-one 41) => 42))
  (+ n 1))
"""

CONSTRUCTOR_NAMED_FOR_ITSELF = CONSTRUCTOR_NAMED_AS_A_BUILTIN_TYPE.replace(
    "(union (Int) (Bool))", "(union (Whole) (Flag))"
)


# --- 3. signature markers

SIGNATURE_WITHOUT_AN_ARROW = """\
(defn add-one
  (sig ((n Int)) Int)
  (examples (example (add-one 41) => 42))
  (+ n 1))
"""

SIGNATURE_WITH_THE_EXAMPLE_ARROW = """\
(defn add-one
  (sig ((n Int)) => Int ! pure)
  (examples (example (add-one 41) => 42))
  (+ n 1))
"""

SIGNATURE_WITH_A_MANGLED_EFFECT_MARKER = """\
(defn add-one
  (sig ((n Int)) -> Int ? pure)
  (examples (example (add-one 41) => 42))
  (+ n 1))
"""

SIGNATURE_WITH_AN_UNDECLARED_EFFECT = """\
(defn add-one
  (sig ((n Int)) -> Int ! impure)
  (examples (example (add-one 41) => 42))
  (+ n 1))
"""


# --- 4. the example arrow

EXAMPLE_WITH_THE_SIGNATURE_ARROW = """\
(defn add-one
  (sig ((n Int)) -> Int ! pure)
  (examples (example (add-one 41) -> 42))
  (+ n 1))
"""


# --- 5. a source that declares nothing

NOTHING_AT_ALL = ""

ONLY_SPACE_AND_A_COMMENT = "\n   ; a program I have not written yet\n\n"


# --- 6. an examples block with no example in it

EMPTY_EXAMPLES_BLOCK = """\
(defn add-one
  (sig ((n Int)) -> Int ! pure)
  (examples)
  (+ n 1))
"""


# --- 7. the shipped programs

def shipped_source(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


# --- running the command

@dataclass(frozen=True)
class ToolRun:
    """One run of the `prova` command: everything the operating system and
    the command reported, kept so a crash stays visible."""

    exit_code: int
    stdout: str
    stderr: str

    def response(self) -> dict:
        try:
            return json.loads(self.stdout)
        except (json.JSONDecodeError, ValueError):
            raise AssertionError(
                "the command's answer is not valid JSON, so a caller cannot read "
                f"an outcome from it; it exited {self.exit_code} and printed "
                f"{self.stdout!r} on standard output and {self.stderr[-600:]!r} on "
                "standard error. A program the tool cannot read must come back as "
                f"one JSON response in the {SPELLING_CATEGORY!r} category, never as "
                "a crash."
            ) from None


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


# --- reading a refusal back

def spelling_refusals(response: dict) -> list[dict]:
    return [
        diagnostic
        for diagnostic in response.get("diagnostics") or []
        if diagnostic.get("category") == SPELLING_CATEGORY
    ]


def assert_accepted(run_result: ToolRun, why: str) -> None:
    response = run_result.response()
    assert response.get("status") == "completed" and not response.get("diagnostics"), (
        f"{why} was not accepted: {response}. Only a name or marker spelled other "
        "than the language defines it may be refused for its spelling; every other "
        "program stays accepted."
    )


def assert_refused_naming(run_result: ToolRun, *, naming: list[str], why: str) -> str:
    """The program was refused as invalid with exactly one spelling
    refusal, and that refusal's sentence names every word a reader needs
    to find and repair the spelling. Returns the sentence."""
    response = run_result.response()
    assert response.get("status") == "invalid_program", (
        f"{why} was not refused: {response}. A program the language does not "
        "define must be invalid; report it as an invalid program."
    )
    refusals = spelling_refusals(response)
    assert len(refusals) == 1, (
        f"expected exactly 1 {SPELLING_CATEGORY!r} refusal for {why}, got "
        f"{len(refusals)}: {response}. One misspelling is one defect with one "
        f"repair; report it once, in the {SPELLING_CATEGORY!r} category."
    )
    reason = refusals[0].get("reason", "")
    for word in naming:
        assert word in reason, (
            f"the refusal for {why} does not name {word!r}, so a reader cannot tell "
            f"what to repair: {reason!r}. Name the word that is spelled wrong and "
            "the spelling the language defines."
        )
    return reason


def assert_refused_at(run_result: ToolRun, *, line: int, why: str) -> None:
    """The refusal points at the line the misspelling stands on."""
    response = run_result.response()
    refusals = spelling_refusals(response)
    assert refusals, (
        f"{why} carries no {SPELLING_CATEGORY!r} refusal to place: {response}."
    )
    location = refusals[0].get("location") or {}
    assert location.get("line") == line, (
        f"the refusal for {why} is placed at {location or 'nowhere'} but the "
        f"misspelling stands on line {line}: {response}. A refusal must say where "
        "it happened, so a reader can go to that line."
    )
