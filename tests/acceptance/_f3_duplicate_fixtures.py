"""Shared fixtures for feature F3's acceptance tests: the programs that
declare one name twice, the near-identical programs that declare each
name once, and the helpers that read a refusal back.

Where a test needs the places a name was declared, it does not spell
line and column numbers out: it finds them in the fixture's own source
text, so a change to the fixture cannot leave a stale expectation
behind.

Not itself a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass

# The category a refused program carries when it declares one name twice.
# Part of the tool's public response vocabulary, not an internal symbol.
DUPLICATE_CATEGORY = "duplicate_declaration"

# --- two functions with one name, and the same pair with two names

TWO_FUNCTIONS_NAMED_TOTAL = """\
(deftype Money (record (amount Int)))

(defn total
  (sig ((n Int)) -> Int ! pure)
  (examples (example (total 1) => 1))
  n)

(defn total
  (sig ((n Int)) -> Int ! pure)
  (examples (example (total 2) => 4))
  (* n 2))
"""

TWO_FUNCTIONS_WITH_TWO_NAMES = """\
(deftype Money (record (amount Int)))

(defn total
  (sig ((n Int)) -> Int ! pure)
  (examples (example (total 1) => 1))
  n)

(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 2) => 4))
  (* n 2))
"""

# --- two types with one name, and the same pair with two names

TWO_TYPES_NAMED_MONEY = """\
(deftype Money (record (amount Int)))

(deftype Money (record (cents Int)))
"""

TWO_TYPES_WITH_TWO_NAMES = """\
(deftype Money (record (amount Int)))

(deftype Deposit (record (cents Int)))
"""

# --- one constructor name introduced by two different types: the record
# --- `Money` and the `Money` variant of the union `Payment`

ONE_CONSTRUCTOR_FROM_TWO_TYPES = """\
(deftype Money (record (amount Int)))

(deftype Payment (union (Money (cents Int)) (Cheque (number Int))))
"""

TWO_CONSTRUCTORS_FROM_TWO_TYPES = """\
(deftype Money (record (amount Int)))

(deftype Payment (union (Transfer (cents Int)) (Cheque (number Int))))
"""

# --- one field spelling twice inside one record, and inside one variant

RECORD_WITH_THE_FIELD_AMOUNT_TWICE = """\
(deftype Money (record (amount Int) (amount Int)))
"""

VARIANT_WITH_THE_FIELD_AMOUNT_TWICE = """\
(deftype Payment (union (Transfer (amount Int) (amount Int)) (Cheque (number Int))))
"""

# --- two different records that each have a field spelled `amount`

TWO_RECORDS_SHARING_THE_FIELD_AMOUNT = """\
(deftype Money (record (amount Int)))

(deftype Invoice (record (amount Int) (number Int)))
"""

BUILTIN_TYPE_NAMES = ("Int", "Bool", "Unit")


def redeclaring_a_builtin(type_name: str) -> str:
    """A program whose only declaration is a record type named after one
    of the three builtin types."""
    return f"(deftype {type_name} (record (value Int)))\n"


def declaring_an_ordinary_type(type_name: str) -> str:
    """The same program with the builtin name replaced by a name the
    language does not reserve."""
    return f"(deftype {type_name} (record (value Int)))\n"


# --- reading a declaration's place out of the fixture's own source text

def places_where(source: str, pattern: str) -> list[tuple[int, int]]:
    """Every place, as (line, column) counted from 1, at which the group
    `name` of `pattern` matches in `source`. Used to state where a
    fixture declares something without hard-coding a line number."""
    places = []
    for number, text in enumerate(source.splitlines(), start=1):
        for match in re.finditer(pattern, text):
            places.append((number, match.start("name") + 1))
    if not places:
        raise AssertionError(
            f"pattern {pattern!r} matches nothing in the fixture source, so the "
            "test cannot say where the declaration is; the fixture text and the "
            "pattern that locates its declarations disagree -- update the pattern"
        )
    return places


def declaration_places(source: str, keyword: str, name: str) -> list[tuple[int, int]]:
    """Where `source` declares `name` with `keyword` (`defn`, `deftype`)."""
    return places_where(source, rf"\({keyword}\s+(?P<name>{re.escape(name)})(?![\w-])")


def member_places(source: str, name: str) -> list[tuple[int, int]]:
    """Where `source` opens a form with `name`: a union variant, or a
    field declaration, both written as `(name ...)`."""
    return places_where(source, rf"\((?P<name>{re.escape(name)})\s")


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
                f"outcome from it; it printed {self.stdout!r} on standard output and "
                f"{self.stderr[-400:]!r} on standard error. The command must answer "
                "every request with one JSON response."
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


def duplicate_reasons(response: dict) -> list[str]:
    """The reason of every diagnostic that refuses a repeated name."""
    return [
        diagnostic.get("reason", "")
        for diagnostic in response.get("diagnostics", [])
        if diagnostic.get("category") == DUPLICATE_CATEGORY
    ]


def places_named_in(reason: str) -> set[tuple[int, int]]:
    """Every place the reason names, as (line, column) pairs."""
    return {
        (int(line), int(column))
        for line, column in re.findall(r"line (\d+) column (\d+)", reason)
    }


def accepted(run_result: ToolRun) -> bool:
    response = run_result.response()
    return response.get("status") == "completed" and response.get("diagnostics") == []


def assert_refused_naming(run_result: ToolRun, symbol: str, places: list[tuple[int, int]]):
    """The program was refused as invalid, with exactly one repeated-name
    refusal, and that refusal names `symbol` and every place in `places`."""
    response = run_result.response()
    assert response.get("status") == "invalid_program", (
        f"a program that declares {symbol!r} {len(places)} times was not refused: "
        f"{response}. A name declared more than once must make the program "
        "invalid; report it as an invalid program."
    )
    reasons = duplicate_reasons(response)
    assert len(reasons) == 1, (
        f"expected exactly 1 repeated-name refusal for {symbol!r}, got "
        f"{len(reasons)}: {reasons}. One name declared twice is one defect with "
        "one repair; report it once, in the "
        f"{DUPLICATE_CATEGORY!r} category."
    )
    assert symbol in reasons[0], (
        f"the refusal does not name {symbol!r}, so a reader cannot tell which "
        f"name was declared twice: {reasons[0]!r}. Name the repeated symbol in "
        "the reason."
    )
    assert places_named_in(reasons[0]) == set(places), (
        f"the refusal names the places {sorted(places_named_in(reasons[0]))} but "
        f"{symbol!r} is declared at {sorted(places)}: {reasons[0]!r}. Name every "
        "place the symbol was declared, as a line and a column, so the reader can "
        "go to both of them."
    )
