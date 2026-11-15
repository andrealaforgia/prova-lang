"""Shared fixtures for feature F7's acceptance tests: programs that apply
a builtin operator to the wrong number of arguments, and the
near-identical programs that apply the same operator correctly.

SPEC.md lines 178-189 fix the number of arguments of every builtin
operator (`not` takes one, every other operator takes two) and state
that operators have no variable arity. Those are the counts written in
`THE_OPERATORS_AND_THEIR_ARITIES` below: the table comes from SPEC.md,
not from the tool under test.

Every refused program has an accepted twin that differs only in the
number of arguments, so a test that observes a refusal is always paired
with a control that observes acceptance of almost the same program.
Without that pairing a tool that refused every program would still pass.

Not itself a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

# The category a refused program carries when something is applied to the
# wrong number of arguments. Already part of the tool's published
# response vocabulary (a call to a declared function and a constructor
# both answer with it); an operator is the same defect, so it is the same
# word. Not an internal symbol: a client reads it from `discover`.
ARITY_MISMATCH_CATEGORY = "arity_mismatch"

# The category the tool uses when an operand has the wrong type. A wrong
# NUMBER of operands must not be answered with this one: the program's
# defect is the count.
TYPE_MISMATCH_CATEGORY = "type_mismatch"

# SPEC.md lines 178-189: the whole operator table, with the number of
# arguments each operator takes.
THE_OPERATORS_AND_THEIR_ARITIES = (
    ("+", 2),
    ("-", 2),
    ("*", 2),
    ("<", 2),
    ("<=", 2),
    (">", 2),
    (">=", 2),
    ("=", 2),
    ("and", 2),
    ("or", 2),
    ("not", 1),
)

# Which operators read true/false operands and which read whole numbers,
# and the answer each one gives back: SPEC.md lines 178-189 again.
BOOLEAN_OPERATORS = ("and", "or", "not")
OPERATORS_ANSWERING_A_NUMBER = ("+", "-", "*")

# What each operator answers when it is applied correctly to the single
# example argument below, worked out from SPEC.md's meanings and not from
# the tool: 2 and 2 for the two-number operators, true for the flag.
THE_ANSWER_WHEN_APPLIED_CORRECTLY = {
    "+": "4",
    "-": "0",
    "*": "4",
    "<": "false",
    "<=": "true",
    ">": "false",
    ">=": "true",
    "=": "true",
    "and": "true",
    "or": "true",
    "not": "false",
}


def _operand_of(operator: str) -> str:
    return "flag" if operator in BOOLEAN_OPERATORS else "cents"


def _answer_type_of(operator: str) -> str:
    return "Int" if operator in OPERATORS_ANSWERING_A_NUMBER else "Bool"


def program_applying(operator: str, argument_count: int, name: str = "probe") -> str:
    """A program whose one function applies `operator` to `argument_count`
    operands of the type that operator reads.

    Everything else about the program is valid: the operands have the
    right type and the function answers the type the operator answers,
    so the only thing a reader can hold against it is the count.

    The operator call always stands at line 4 column 3.
    """
    operand = _operand_of(operator)
    operands = " ".join([operand] * argument_count)
    call = f"({operator} {operands})" if operands else f"({operator})"
    answer = _answer_type_of(operator)
    placeholder = "4" if answer == "Int" else "false"
    return (
        f"(defn {name}\n"
        f"  (sig ((cents Int) (flag Bool)) -> {answer} ! pure)\n"
        f"  (examples (example ({name} 2 true) => {placeholder}))\n"
        f"  {call})\n"
    )


# The place every program `program_applying` writes puts its operator
# call: the fourth line, third column.
THE_OPERATOR_CALL_SITE = (4, 3)


# --- the headline programs, written out so a reader sees them whole

NOT_WITH_TWO_ARGUMENTS = """\
(defn unflagged?
  (sig ((flag Bool)) -> Bool ! pure)
  (examples (example (unflagged? true) => false))
  (not flag flag))
"""

NOT_WITH_ONE_ARGUMENT = """\
(defn unflagged?
  (sig ((flag Bool)) -> Bool ! pure)
  (examples (example (unflagged? true) => false))
  (not flag))
"""

NOT_WITH_NO_ARGUMENTS = """\
(defn unflagged?
  (sig ((flag Bool)) -> Bool ! pure)
  (examples (example (unflagged? true) => false))
  (not))
"""

SUM_WITH_ONE_ARGUMENT = """\
(defn total
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (total 2) => 4))
  (+ cents))
"""

SUM_WITH_THREE_ARGUMENTS = """\
(defn total
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (total 2) => 4))
  (+ cents cents cents))
"""

SUM_WITH_TWO_ARGUMENTS = """\
(defn total
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (total 2) => 4))
  (+ cents cents))
"""

# An extra argument written deep inside another expression, not as the
# whole body: the count is read wherever the call stands.
NOT_WITH_TWO_ARGUMENTS_INSIDE_AN_ARGUMENT = """\
(defn unflagged?
  (sig ((flag Bool)) -> Bool ! pure)
  (examples (example (unflagged? true) => false))
  (and flag (not flag flag)))
"""

THE_INNER_OPERATOR_CALL_SITE = (4, 13)

NOT_WITH_ONE_ARGUMENT_INSIDE_AN_ARGUMENT = """\
(defn unflagged?
  (sig ((flag Bool)) -> Bool ! pure)
  (examples (example (unflagged? true) => false))
  (and flag (not flag)))
"""

# An operator given both the wrong number of operands and an operand of
# the wrong type: two independent defects in one expression.
SUM_WITH_THREE_ARGUMENTS_ONE_OF_THEM_A_FLAG = """\
(defn total
  (sig ((cents Int) (flag Bool)) -> Int ! pure)
  (examples (example (total 2 true) => 4))
  (+ cents cents flag))
"""

# A name that looks like an operator but is not one of the eleven: the
# tool must still answer about an unknown name, not about a count.
AN_UNKNOWN_OPERATOR_LIKE_NAME = """\
(defn total
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (total 2) => 4))
  (mod cents cents))
"""

# An operator call that is never closed.
AN_UNCLOSED_OPERATOR_CALL = """\
(defn total
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (total 2) => 4))
  (+ cents cents)
"""

EMPTY_SOURCE = ""


@dataclass(frozen=True)
class WrongCall:
    """One operator call a program writes with the wrong number of
    arguments: which operator, how many it takes, how many were written
    and where the call stands."""

    operator: str
    takes: int
    got: int
    at: tuple[int, int]


def every_operator_with_a_wrong_count() -> tuple[str, tuple[WrongCall, ...]]:
    """One program that applies every operator twice: once with one
    argument fewer than SPEC.md gives it and once with one more.

    `not` takes one argument, so its two calls have none and two. Every
    other operator takes two, so its calls have one and three. The
    program is otherwise valid, and the places returned beside it are
    where each call stands, so a reader can be sent to the right line.
    """
    blocks: list[str] = []
    wrong: list[WrongCall] = []
    line = 1
    for ordinal, (operator, arity) in enumerate(THE_OPERATORS_AND_THEIR_ARITIES):
        for half, count in enumerate((arity - 1, arity + 1)):
            name = f"probe-{ordinal}-{half}"
            blocks.append(program_applying(operator, count, name=name))
            wrong.append(
                WrongCall(operator, arity, count, (line + 3, THE_OPERATOR_CALL_SITE[1]))
            )
            line += 5  # four lines of function, then the blank line between
    return "\n".join(blocks), tuple(wrong)


def every_operator_applied_correctly() -> str:
    """One program that applies all eleven operators, each to the number
    of arguments SPEC.md gives it, each in its own function, with the
    answer SPEC.md's meaning gives for the arguments supplied."""
    parts = []
    for ordinal, (operator, arity) in enumerate(THE_OPERATORS_AND_THEIR_ARITIES):
        operand = _operand_of(operator)
        name = f"probe-{ordinal}"
        parts.append(
            f"(defn {name}\n"
            f"  (sig ((cents Int) (flag Bool)) -> {_answer_type_of(operator)} ! pure)\n"
            f"  (examples (example ({name} 2 true) => "
            f"{THE_ANSWER_WHEN_APPLIED_CORRECTLY[operator]}))\n"
            f"  ({operator} {' '.join([operand] * arity)}))\n"
        )
    return "\n".join(parts)


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
        f"{why} was not accepted: {response}. Only an operator applied to a number "
        "of arguments other than the one the language gives it may be refused for "
        "this rule; every other program stays accepted."
    )


def assert_refused_for_its_count(
    run_result: ToolRun,
    operator: str,
    takes: int,
    got: int,
    at: tuple[int, int] | None = THE_OPERATOR_CALL_SITE,
    alone: bool = True,
) -> None:
    """The program was refused as invalid with exactly one count refusal,
    that refusal names the operator, the number of arguments the operator
    takes and the number the program gave, and it points at the place of
    the call.

    `takes` and `got` are read as the two separate numbers a reader needs:
    a refusal that states one of them, or that swaps them, fails here.
    When `alone` is set, the count refusal is the only thing the tool says
    about the program.
    """
    response = run_result.response()
    assert run_result.exit_code == 0, (
        f"the command did not answer the program whose {operator!r} has {got} "
        f"argument(s); it exited {run_result.exit_code} saying "
        f"{run_result.stderr[-400:]!r}. A program the tool refuses must come back "
        "as a refusal, never as a crash."
    )
    assert response.get("status") == "invalid_program", (
        f"a program applying {operator!r} to {got} argument(s) was not refused: "
        f"{response}. An operator takes exactly the number of arguments the "
        "language gives it; report a program that breaks that as invalid."
    )
    refusals = of_category(response, ARITY_MISMATCH_CATEGORY)
    assert len(refusals) == 1, (
        f"expected exactly 1 {ARITY_MISMATCH_CATEGORY!r} refusal for {operator!r}, "
        f"got {len(refusals)} in {categories(response)}: {response}. One operator "
        f"applied to the wrong number of arguments is one defect with one repair; "
        f"report it once, in the {ARITY_MISMATCH_CATEGORY!r} category."
    )
    if alone:
        assert categories(response) == [ARITY_MISMATCH_CATEGORY], (
            f"the program whose only defect is the number of arguments of "
            f"{operator!r} was also answered with {categories(response)}: "
            f"{response}. An operand of the right type is not a second defect; say "
            "only what is wrong."
        )
    reason = refusals[0].get("reason", "")
    assert operator in reason, (
        f"the refusal does not name the operator {operator!r}, so a reader cannot "
        f"tell which call to repair: {reason!r}. Name the operator."
    )
    assert f"takes exactly {takes}" in reason, (
        f"the refusal does not say the operator takes exactly {takes} argument(s), "
        f"so a reader does not learn how many to write: {reason!r}. State the number "
        "the operator takes."
    )
    assert f"got {got}" in reason, (
        f"the refusal does not say the program gave {got} argument(s), so a reader "
        f"cannot see what is wrong with the call as written: {reason!r}. State the "
        "number the program gave."
    )
    location = refusals[0].get("location") or {}
    line, column = location.get("line"), location.get("column")
    assert line and column, (
        f"the refusal carries no place ({refusals[0]}), so a reader must search the "
        "file for the call. Report the line and column of the operator call."
    )
    if at is not None:
        assert (line, column) == at, (
            f"the refusal points at line {line} column {column}, but the "
            f"{operator!r} call is at line {at[0]} column {at[1]}: {refusals[0]}. "
            "Report the place of the call that has the wrong number of arguments."
        )
