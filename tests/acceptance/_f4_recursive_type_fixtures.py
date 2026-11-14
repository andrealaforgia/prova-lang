"""Shared fixtures for feature F4's acceptance tests: the programs whose
declared types lead back to themselves, the near-identical programs whose
types do not, and the helpers that read a refusal back.

Each refused program has an accepted twin that differs only in the field
type that closes the cycle, so a test that observes a refusal can always
be paired with a control that observes acceptance of almost the same
program.

Not itself a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass

# The category a refused program carries when its data leads back to
# itself. Part of the tool's public response vocabulary, not an internal
# symbol.
RECURSIVE_TYPE_CATEGORY = "recursive_type"

# The category the tool uses when a field names a type the program never
# declares. A recursive type is declared, so this must never be the
# answer to recursive data.
UNKNOWN_TYPE_CATEGORY = "unbound_type"

# --- a record with a field of its own type, and the same record without

RECORD_HOLDING_ITSELF = """\
(deftype Node (record (value Int) (next Node)))
"""

RECORD_HOLDING_A_NUMBER = """\
(deftype Node (record (value Int) (next Int)))
"""

# --- two records that each hold the other, and the same pair where the
# --- second one holds a number instead

TWO_RECORDS_HOLDING_EACH_OTHER = """\
(deftype Invoice (record (payment Payment) (number Int)))

(deftype Payment (record (invoice Invoice) (cents Int)))
"""

ONE_RECORD_HOLDING_THE_OTHER = """\
(deftype Invoice (record (payment Payment) (number Int)))

(deftype Payment (record (invoice Int) (cents Int)))
"""

# --- a union whose variant payload closes a cycle, and the same union
# --- whose payload is a number

UNION_WITH_A_RECURSIVE_VARIANT = """\
(deftype Stack (union (Empty) (Pushed (top Int) (rest Stack))))
"""

UNION_WITHOUT_A_RECURSIVE_VARIANT = """\
(deftype Stack (union (Empty) (Pushed (top Int) (rest Int))))
"""

# --- the same recursive union, read by a function that matches on it:
# --- the shape in which the tool used to end in a crash

UNION_WITH_A_RECURSIVE_VARIANT_READ_BY_A_FUNCTION = """\
(deftype Stack (union (Empty) (Pushed (top Int) (rest Stack))))

(defn top-of
  (sig ((s Stack)) -> Int ! pure)
  (examples (example (top-of (Empty)) => 0))
  (match s ((Empty) 0) ((Pushed t r) t)))
"""

# --- three types in a chain, no cycle: Invoice holds Line holds Money

CHAIN_OF_THREE_TYPES = """\
(deftype Money (record (amount Int)))

(deftype Line (record (price Money) (count Int)))

(deftype Invoice (record (entry Line) (number Int)))
"""


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


# --- reading a refusal back

def categories(response: dict) -> list[str]:
    return [
        diagnostic.get("category", "")
        for diagnostic in response.get("diagnostics") or []
    ]


def recursive_type_diagnostics(response: dict) -> list[dict]:
    """Every diagnostic that refuses data leading back to itself."""
    return [
        diagnostic
        for diagnostic in response.get("diagnostics") or []
        if diagnostic.get("category") == RECURSIVE_TYPE_CATEGORY
    ]


def accepted(run_result: ToolRun) -> bool:
    response = run_result.response()
    return response.get("status") == "completed" and not response.get("diagnostics")


def assert_accepted(run_result: ToolRun, why: str) -> None:
    response = run_result.response()
    assert accepted(run_result), (
        f"{why} was not accepted: {response}. Only a type that can lead back to "
        "itself may be refused for recursion; every other program stays accepted."
    )


def assert_refused_naming_the_cycle(run_result: ToolRun, type_names: list[str]) -> None:
    """The program was refused as invalid with exactly one recursive-data
    refusal, and that refusal names every type on the cycle, both in the
    sentence a reader gets and in the machine-readable member list."""
    response = run_result.response()
    assert response.get("status") == "invalid_program", (
        f"a program whose types {type_names} lead back to themselves was not "
        f"refused: {response}. Data that depends on itself must make the program "
        "invalid; report it as an invalid program."
    )
    refusals = recursive_type_diagnostics(response)
    assert len(refusals) == 1, (
        f"expected exactly 1 recursive-data refusal for {type_names}, got "
        f"{len(refusals)}: {response}. One cycle is one defect with one repair; "
        f"report it once, in the {RECURSIVE_TYPE_CATEGORY!r} category."
    )
    reason = refusals[0].get("reason", "")
    for type_name in type_names:
        assert type_name in reason, (
            f"the refusal does not name the type {type_name!r}, so a reader cannot "
            f"tell which declarations close the cycle: {reason!r}. Name every type "
            "on the cycle."
        )
    assert set(refusals[0].get("cycle") or ()) == set(type_names), (
        f"the refusal reports the cycle members {refusals[0].get('cycle')} but the "
        f"types that lead back to themselves are {sorted(type_names)}: {response}. "
        "Report exactly the types on the cycle, and no type that is not on one."
    )
