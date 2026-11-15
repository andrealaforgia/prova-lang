"""Shared fixtures for feature F8's acceptance tests: programs whose
declared example is about a function other than the one that declares
it, and the near-identical programs whose example is about its own
function.

SPEC.md lines 228-234 state the rule these fixtures read: "Every
function needs an example directly calling that same function",
"Arguments and expected outputs must be closed values of the declared
types" and "An unrelated expression cannot stand in for an example of
the function." The expectations below come from those lines, not from
the tool under test.

Every refused program has an accepted twin that differs only in the call
its example writes, so a test that observes a refusal is always paired
with a control that observes acceptance of almost the same program.
Without that pairing a tool that refused every program would still pass.

Not itself a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova. Each feature's fixtures are self-contained here,
as F2 to F7's are.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

# The word a refused program carries when a function's example is about
# some other function. No published category said this before: the ones
# that exist report a name that does not resolve, a count, a type, a
# repeated declaration, a cycle, a hidden binding or a reserved word,
# and none of them says "this example demonstrates another function".
# Not an internal symbol: a client reads it from `discover`.
UNRELATED_EXAMPLE_CATEGORY = "unrelated_example"

# The category the tool already uses when something is applied to the
# wrong number of arguments (a call in a body, a constructor, a builtin
# operator). An example that names its own function but writes the wrong
# number of arguments is the same defect, so it is the same word.
ARITY_MISMATCH_CATEGORY = "arity_mismatch"

# The category a source the tool cannot read as a core-0 program carries.
SYNTAX_CATEGORY = "syntax"


# --- the headline programs, written out so a reader sees them whole

# `double` declares one example, and that example calls `triple`. Its
# expected value is the one `triple` answers, so a tool that runs the
# example without reading whose example it is reports it as passing.
AN_EXAMPLE_ABOUT_ANOTHER_FUNCTION = """\
(defn double
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (triple 2) => 6))
  (+ cents cents))

(defn triple
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (triple 2) => 6))
  (* cents 3))
"""

# The twin: the same two functions, each with an example of its own.
EVERY_EXAMPLE_ABOUT_ITS_OWN_FUNCTION = """\
(defn double
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (double 2) => 4))
  (+ cents cents))

(defn triple
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (triple 2) => 6))
  (* cents 3))
"""

# The same mistake written twice in one examples clause: two examples,
# both about `triple`, so `double` still has none.
TWO_EXAMPLES_BOTH_ABOUT_ANOTHER_FUNCTION = """\
(defn double
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (triple 2) => 6) (example (triple 3) => 9))
  (+ cents cents))

(defn triple
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (triple 2) => 6))
  (* cents 3))
"""

AN_EXAMPLE_NAMING_A_FUNCTION_THE_PROGRAM_DOES_NOT_DECLARE = """\
(defn double
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (treble 2) => 4))
  (+ cents cents))
"""

A_LONE_FUNCTION_WITH_ITS_OWN_EXAMPLE = """\
(defn double
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (double 2) => 4))
  (+ cents cents))
"""

AN_EXAMPLE_WITH_ONE_ARGUMENT_TOO_MANY = """\
(defn double
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (double 2 3) => 4))
  (+ cents cents))
"""

AN_EXAMPLE_WITH_NO_ARGUMENT_AT_ALL = """\
(defn double
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (double) => 4))
  (+ cents cents))
"""

A_TWO_PARAMETER_FUNCTION_GIVEN_ONE_ARGUMENT = """\
(defn fare
  (sig ((cents Int) (flag Bool)) -> Int ! pure)
  (examples (example (fare 100) => 110))
  (+ cents 10))
"""

A_TWO_PARAMETER_FUNCTION_GIVEN_BOTH_ARGUMENTS = """\
(defn fare
  (sig ((cents Int) (flag Bool)) -> Int ! pure)
  (examples (example (fare 100 true) => 110))
  (+ cents 10))
"""

# A function that takes nothing and whose example writes nothing: the
# count a rule about counts must leave alone.
A_FUNCTION_THAT_TAKES_NO_ARGUMENT = """\
(defn standard-fare
  (sig () -> Int ! pure)
  (examples (example (standard-fare) => 110))
  110)
"""

# An examples clause that is never closed: a source the reader refuses
# before any rule about examples is reached.
AN_EXAMPLES_CLAUSE_THAT_IS_NEVER_CLOSED = """\
(defn double
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (double 2) => 4)
  (+ cents cents))
"""

# A source with nothing in it. Core-0 asks for at least one declaration,
# so it is refused for a reason of its own and never for this rule.
A_SOURCE_WITH_NOTHING_IN_IT = ""


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


def examples(source: str) -> ToolRun:
    return run({"prova": "i1", "operation": "examples", "source": source})


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


def assert_answered(run_result: ToolRun, what: str) -> dict:
    """The command answered `what` with one JSON response instead of
    ending the process."""
    assert run_result.exit_code == 0, (
        f"the command did not answer {what}; it exited {run_result.exit_code} saying "
        f"{run_result.stderr[-600:]!r}. Every request must come back as one JSON "
        "response, a refusal included, never as a crash."
    )
    return run_result.response()


def assert_accepted(run_result: ToolRun, why: str) -> None:
    response = assert_answered(run_result, why)
    assert accepted(run_result), (
        f"{why} was not accepted: {response}. Only an example that is about a "
        "function other than the one declaring it, or that writes a number of "
        "arguments the function does not take, may be refused for this rule; every "
        "other program stays accepted."
    )


def assert_refused_as_an_example_of_another_function(
    run_result: ToolRun,
    owner: str,
    called: str,
    occurrences: int = 1,
    alone: bool = True,
) -> None:
    """The program was refused as invalid with `occurrences` refusals
    saying an example is about another function, and every one of them
    names the function that declares the example and the function the
    example calls, so a reader learns which two functions the repair
    stands between."""
    response = assert_answered(
        run_result, f"the program whose example of {owner!r} calls {called!r}"
    )
    assert response.get("status") == "invalid_program", (
        f"a program whose example of {owner!r} calls {called!r} was not refused: "
        f"{response}. An example that calls some other function is not an example "
        "of the function that declares it; report that program as invalid."
    )
    refusals = of_category(response, UNRELATED_EXAMPLE_CATEGORY)
    assert len(refusals) == occurrences, (
        f"expected exactly {occurrences} {UNRELATED_EXAMPLE_CATEGORY!r} refusal(s) "
        f"for the example(s) of {owner!r}, got {len(refusals)} in "
        f"{categories(response)}: {response}. One example about another function is "
        f"one defect with one repair; report each one once, in the "
        f"{UNRELATED_EXAMPLE_CATEGORY!r} category."
    )
    if alone:
        assert categories(response) == [UNRELATED_EXAMPLE_CATEGORY] * occurrences, (
            f"the program whose only defect is whose example it is was also answered "
            f"with {categories(response)}: {response}. The arguments and the expected "
            "value are well formed; say only what is wrong."
        )
    for refusal in refusals:
        reason = refusal.get("reason", "")
        assert repr(owner) in reason, (
            f"the refusal does not name {owner!r}, the function left without an "
            f"example of its own, so a reader cannot tell which function to repair: "
            f"{reason!r}. Name the function that declares the example."
        )
        assert repr(called) in reason, (
            f"the refusal does not name {called!r}, the function the example calls, "
            f"so a reader cannot see why the example is not about its own function: "
            f"{reason!r}. Name the function the example calls."
        )


def assert_refused_for_its_argument_count(
    run_result: ToolRun,
    function: str,
    takes: int,
    got: int,
    alone: bool = True,
) -> None:
    """The program was refused as invalid with exactly one count refusal
    that names the function, the number of arguments the function takes
    and the number the example wrote.

    `takes` and `got` are read as the two separate numbers a reader
    needs: a refusal that states one of them, or that swaps them, fails
    here.
    """
    response = assert_answered(
        run_result, f"the program whose example of {function!r} wrote {got} argument(s)"
    )
    assert response.get("status") == "invalid_program", (
        f"a program whose example of {function!r} wrote {got} argument(s) for "
        f"{takes} parameter(s) was not refused: {response}. An example supplies one "
        "closed value for each parameter; report a program that breaks that as "
        "invalid."
    )
    refusals = of_category(response, ARITY_MISMATCH_CATEGORY)
    assert len(refusals) == 1, (
        f"expected exactly 1 {ARITY_MISMATCH_CATEGORY!r} refusal for the example of "
        f"{function!r}, got {len(refusals)} in {categories(response)}: {response}. "
        "One example with the wrong number of arguments is one defect with one "
        f"repair; report it once, in the {ARITY_MISMATCH_CATEGORY!r} category."
    )
    if alone:
        assert categories(response) == [ARITY_MISMATCH_CATEGORY], (
            f"the program whose only defect is the number of arguments its example "
            f"writes was also answered with {categories(response)}: {response}. Say "
            "only what is wrong."
        )
    reason = refusals[0].get("reason", "")
    assert repr(function) in reason, (
        f"the refusal does not name the function {function!r}, so a reader cannot "
        f"tell which example to repair: {reason!r}. Name the function."
    )
    assert f"passes {got} argument(s)" in reason, (
        f"the refusal does not say the example wrote {got} argument(s), so a reader "
        f"cannot see what is wrong with the example as written: {reason!r}. State "
        "the number the example wrote."
    )
    assert f"expected {takes}" in reason, (
        f"the refusal does not say the function takes {takes} argument(s), so a "
        f"reader does not learn how many to write: {reason!r}. State the number the "
        "function takes."
    )
