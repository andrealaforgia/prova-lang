"""Shared fixtures for feature F5's acceptance tests: the programs whose
local bindings hide a name that is already visible, the programs that use
the reserved word `result` outside a postcondition, and the
near-identical programs that do neither.

Every refused program has an accepted twin that differs only in the name
of the binder that breaks the rule, so a test that observes a refusal is
always paired with a control that observes acceptance of almost the same
program. Without that pairing a tool that refused every program would
still pass.

Not itself a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

# The category a refused program carries when a binding hides a name
# that is already visible where the binding is introduced. Part of the
# tool's public response vocabulary, not an internal symbol.
SHADOWED_BINDING_CATEGORY = "shadowed_binding"

# The category a refused program carries when a binder uses `result`,
# the word reserved for reading a function's return value in a
# postcondition.
RESERVED_NAME_CATEGORY = "reserved_name"

# The category the tool uses when a name is read where nothing binds it.
# A name that IS bound, by a binding the tool refuses, must not be
# answered with this one: the program's defect is the binding.
UNBOUND_NAME_CATEGORY = "unbound_name"

# --- a `let` that binds a name already bound as a parameter, and the
# --- same program whose `let` uses a name of its own

LET_HIDING_A_PARAMETER = """\
(defn fare
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (fare 100) => 110))
  (let ((cents (+ cents 10))) cents))
"""

LET_WITH_ITS_OWN_NAME = """\
(defn fare
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (fare 100) => 110))
  (let ((raised (+ cents 10))) raised))
"""

# --- a pattern variable that hides a declared function name, and the
# --- same program whose pattern variable has a name of its own

PATTERN_VARIABLE_HIDING_A_FUNCTION = """\
(deftype Dial (union (Hour (value Int))))

(defn offset
  (sig () -> Int ! pure)
  (examples (example (offset) => 1))
  1)

(defn hour-of
  (sig ((d Dial)) -> Int ! pure)
  (examples (example (hour-of (Hour 7)) => 7))
  (match d ((Hour offset) offset)))
"""

PATTERN_VARIABLE_WITH_ITS_OWN_NAME = """\
(deftype Dial (union (Hour (value Int))))

(defn offset
  (sig () -> Int ! pure)
  (examples (example (offset) => 1))
  1)

(defn hour-of
  (sig ((d Dial)) -> Int ! pure)
  (examples (example (hour-of (Hour 7)) => 7))
  (match d ((Hour hour) hour)))
"""

# --- the three binders named `result`, and their twins

LET_NAMED_RESULT = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 21) => 42))
  (let ((result (* n 2))) result))
"""

PARAMETER_NAMED_RESULT = """\
(defn doubled
  (sig ((result Int)) -> Int ! pure)
  (examples (example (doubled 21) => 42))
  (* result 2))
"""

PATTERN_VARIABLE_NAMED_RESULT = """\
(deftype Box (record (held Int)))

(defn held-of
  (sig ((b Box)) -> Int ! pure)
  (examples (example (held-of (Box 5)) => 5))
  (match b ((Box result) result)))
"""

LET_NAMED_TOTAL = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 21) => 42))
  (let ((total (* n 2))) total))
"""

PARAMETER_NAMED_N = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 21) => 42))
  (* n 2))
"""

PATTERN_VARIABLE_NAMED_HELD = """\
(deftype Box (record (held Int)))

(defn held-of
  (sig ((b Box)) -> Int ! pure)
  (examples (example (held-of (Box 5)) => 5))
  (match b ((Box amount) amount)))
"""

# --- `result` read where only a postcondition may read it, and the same
# --- program that reads it in its postcondition only

RESULT_READ_IN_A_BODY_AND_A_PRECONDITION = """\
(defn doubled
  (sig ((result Int)) -> Int ! pure)
  (requires (> result 0))
  (examples (example (doubled 21) => 42))
  (* result 2))
"""

RESULT_READ_IN_A_POSTCONDITION_ONLY = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (= result (* n 2)))
  (examples (example (doubled 21) => 42))
  (* n 2))
"""

RESULT_READ_WHERE_NOTHING_BINDS_IT = """\
(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 21) => 42))
  (* result 2))
"""

# --- one pattern that binds the same name twice, and the same pattern
# --- with two names

PATTERN_BINDING_ONE_NAME_TWICE = """\
(deftype Pair (record (left Int) (right Int)))

(defn left-of
  (sig ((p Pair)) -> Int ! pure)
  (examples (example (left-of (Pair 3 4)) => 3))
  (match p ((Pair n n) n)))
"""

PATTERN_BINDING_TWO_NAMES = """\
(deftype Pair (record (left Int) (right Int)))

(defn left-of
  (sig ((p Pair)) -> Int ! pure)
  (examples (example (left-of (Pair 3 4)) => 3))
  (match p ((Pair n m) n)))
"""

# --- one spelling in two disjoint clauses, and the same program whose
# --- first clause binds the parameter's name instead

ONE_SPELLING_IN_TWO_CLAUSES = """\
(deftype Colour (union (Red (shade Int)) (Blue (shade Int))))

(defn shade-of
  (sig ((c Colour)) -> Int ! pure)
  (examples
    (example (shade-of (Red 2)) => 2)
    (example (shade-of (Blue 9)) => 9))
  (match c ((Red tone) tone) ((Blue tone) tone)))
"""

ONE_CLAUSE_BINDING_THE_PARAMETER_NAME = """\
(deftype Colour (union (Red (shade Int)) (Blue (shade Int))))

(defn shade-of
  (sig ((c Colour)) -> Int ! pure)
  (examples
    (example (shade-of (Red 2)) => 2)
    (example (shade-of (Blue 9)) => 9))
  (match c ((Red c) c) ((Blue tone) tone)))
"""

# --- a `let` that hides a builtin operator name, and its twin

LET_HIDING_A_BUILTIN_OPERATOR = """\
(defn tally
  (sig ((n Int)) -> Int ! pure)
  (examples (example (tally 4) => 9))
  (let ((not (+ n 5))) not))
"""

LET_NOT_HIDING_A_BUILTIN_OPERATOR = """\
(defn tally
  (sig ((n Int)) -> Int ! pure)
  (examples (example (tally 4) => 9))
  (let ((bumped (+ n 5))) bumped))
"""

# --- a program with nothing in it at all

EMPTY_SOURCE = ""


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
                "the command's answer is not valid JSON, so a caller cannot read an "
                f"outcome from it; it exited {self.exit_code} and printed "
                f"{self.stdout!r} on standard output and {self.stderr[-400:]!r} on "
                "standard error. The command must answer every request with one "
                "JSON response."
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


def discover() -> ToolRun:
    return run({"prova": "i1", "operation": "discover"})


# --- reading an answer back

def diagnostics(response: dict) -> list[dict]:
    return list(response.get("diagnostics") or [])


def categories(response: dict) -> list[str]:
    return [diagnostic.get("category", "") for diagnostic in diagnostics(response)]


def of_category(response: dict, category: str) -> list[dict]:
    return [d for d in diagnostics(response) if d.get("category") == category]


def accepted(run_result: ToolRun) -> bool:
    response = run_result.response()
    return response.get("status") == "completed" and not response.get("diagnostics")


def assert_accepted(run_result: ToolRun, why: str) -> None:
    response = run_result.response()
    assert accepted(run_result), (
        f"{why} was not accepted: {response}. Only a binding that hides a visible "
        "name, or a binder that uses the reserved word, may be refused for this "
        "rule; every other program stays accepted."
    )


def assert_refused(run_result: ToolRun, category: str, naming: list[str]) -> None:
    """The program was refused as invalid with exactly one refusal of
    `category`, that refusal names every word in `naming`, and it says
    where the offending binder is."""
    response = run_result.response()
    assert response.get("status") == "invalid_program", (
        f"a program whose binding breaks the {category!r} rule was not refused: "
        f"{response}. A binding that may not be introduced must make the program "
        "invalid; report it as an invalid program."
    )
    refusals = of_category(response, category)
    assert len(refusals) == 1, (
        f"expected exactly 1 {category!r} refusal, got {len(refusals)} in "
        f"{categories(response)}: {response}. One offending binder is one defect "
        f"with one repair; report it once, in the {category!r} category."
    )
    reason = refusals[0].get("reason", "")
    for word in naming:
        assert word in reason, (
            f"the refusal does not name {word!r}, so a reader cannot tell which "
            f"binding to repair or what it hides: {reason!r}. Name the binder and "
            "the binding it hides."
        )
    location = refusals[0].get("location") or {}
    assert location.get("line") and location.get("column"), (
        f"the refusal carries no place ({refusals[0]}), so a reader must search the "
        "file for the binder. Report the line and column of the offending binder."
    )

# --- a parameter that hides a declared function, a signature whose
# --- second parameter repeats the first, and the twin of each

PARAMETER_HIDING_A_FUNCTION = """\
(defn offset
  (sig () -> Int ! pure)
  (examples (example (offset) => 1))
  1)

(defn raise-by
  (sig ((offset Int)) -> Int ! pure)
  (examples (example (raise-by 3) => 13))
  (+ offset 10))
"""

PARAMETER_WITH_ITS_OWN_NAME = """\
(defn offset
  (sig () -> Int ! pure)
  (examples (example (offset) => 1))
  1)

(defn raise-by
  (sig ((amount Int)) -> Int ! pure)
  (examples (example (raise-by 3) => 13))
  (+ amount 10))
"""

TWO_PARAMETERS_WITH_ONE_NAME = """\
(defn gap
  (sig ((edge Int) (edge Int)) -> Int ! pure)
  (examples (example (gap 9 4) => 0))
  (- edge edge))
"""

TWO_PARAMETERS_WITH_TWO_NAMES = """\
(defn gap
  (sig ((edge Int) (other Int)) -> Int ! pure)
  (examples (example (gap 9 4) => 5))
  (- edge other))
"""
