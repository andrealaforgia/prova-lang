"""Shared fixtures for feature F10: the programs whose refusal a client
must be able to act on without reading the prose, and the accepted twins
that differ only in the one defect under observation.

Every refused program here has a twin that the tool accepts, so a test
that observes a refusal is always paired with a control that observes
acceptance of almost the same program. Without the twins a tool that
refused every program would still pass.

What a refusal says in prose belongs to the rule that owns it and is
never pinned here. F10 observes only the structured fields beside the
prose: the revision of the source the answer is about, the symbol the
refusal names, what was expected there, what was found, and where it
stands.

Not itself a test module (no `test_` prefix); pytest will not collect
it. The helpers drive only the `prova` command's real JSON stdin/stdout
surface. No imports from src/prova: the revision below is computed from
the submitted text the way a client computes it.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from dataclasses import dataclass

# The field names a client reads instead of the prose. Part of the
# tool's published answer vocabulary -- the manifest describes them per
# category -- not internal symbols.
REVISION = "source_revision"
SYMBOL = "symbol"
EXPECTED = "expected"
ACTUAL = "actual"
LOCATION = "location"

INVALID_PROGRAM = "invalid_program"
INVALID_INPUT = "invalid_input"


def revision_of(source: str) -> str:
    """The revision of a source text as a client computes it: the SHA-256
    of the exact bytes it submitted."""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


# --- the program every case below is a copy of ----------------------------

# Line 1 column 7 is where the declared name `fare` stands; line 4
# column 3 is where the body stands.
WELL_FORMED = """\
(defn fare
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (fare 100) => 110))
  (+ cents 10))
"""

DECLARATION_LINE = 1
DECLARATION_COLUMN = 7
BODY_LINE = 4
BODY_COLUMN = 3


def with_body(expression: str) -> str:
    return WELL_FORMED.replace("  (+ cents 10))\n", f"  {expression})\n")


def with_signature(signature: str) -> str:
    return WELL_FORMED.replace(
        "  (sig ((cents Int)) -> Int ! pure)\n", f"  {signature}\n", 1
    )


def with_example(example: str) -> str:
    return WELL_FORMED.replace(
        "  (examples (example (fare 100) => 110))\n",
        f"  (examples {example})\n",
        1,
    )


def with_signature_and_example(signature: str, example: str) -> str:
    """The program with both its signature and its example replaced.

    A case that changes the declared types alone leaves the example
    stating a value of the types that were there before, which is a
    second defect of its own and not the one the case is about. The
    fixtures here hold one defect per program, so a case changing the
    signature says what the example states under it.
    """
    return with_signature(signature).replace(
        "  (examples (example (fare 100) => 110))\n",
        f"  (examples {example})\n",
        1,
    )


@dataclass(frozen=True)
class Case:
    """One refused program and the structured answer a client acts on:
    the category, the symbol the refusal is about, what was expected
    there and what was found, and the place it stands at.

    `twin` is the same program with the one defect repaired.
    """

    source: str
    category: str
    symbol: str
    line: int
    column: int
    twin: str = WELL_FORMED
    expected: object = None
    actual: object = None
    granularity: str = "expression"

    def has_expectation(self) -> bool:
        return self.expected is not None


# --- a wrong type, said as a symbol, an expectation and what was found ----

TWO_FUNCTIONS = """\
(defn flagged
  (sig ((flag Bool)) -> Int ! pure)
  (examples (example (flagged true) => 1))
  1)
(defn fare
  (sig ((cents Int)) -> Int ! pure)
  (examples (example (fare 100) => 110))
  {body})
"""

TYPE_ERRORS: dict[str, Case] = {
    "a body that does not have the declared return type": Case(
        source=with_signature_and_example(
            "  (sig ((cents Int)) -> Bool ! pure)",
            "(example (fare 100) => true)",
        ),
        category="type_mismatch",
        symbol="fare",
        expected="Bool",
        actual="Int",
        line=BODY_LINE,
        column=BODY_COLUMN,
    ),
    "an operand of the wrong type": Case(
        source=with_body("(+ cents true)"),
        category="type_mismatch",
        symbol="+",
        expected="Int",
        actual="Bool",
        line=BODY_LINE,
        column=BODY_COLUMN,
    ),
    "an argument of the wrong type": Case(
        source=TWO_FUNCTIONS.format(body="(flagged cents)"),
        category="type_mismatch",
        symbol="flagged.flag",
        expected="Bool",
        actual="Int",
        line=8,
        column=3,
        twin=TWO_FUNCTIONS.format(body="(flagged true)"),
    ),
}


# --- refusals about a declaration, which carried no place before ---------

UNKNOWN_TYPE_SOURCE = with_body("10").replace(
    "  (sig ((cents Int)) -> Int ! pure)\n",
    "  (sig ((cents Cents)) -> Int ! pure)\n",
    1,
)

RECURSIVE_TYPE_SOURCE = "(deftype Loop (record (next Loop)))\n" + WELL_FORMED
ACYCLIC_TYPE_SOURCE = "(deftype Loop (record (next Int)))\n" + WELL_FORMED

MUTUAL_CALLS = """\
(defn even-steps
  (sig ((n Int)) -> Int ! pure)
  (examples (example (even-steps 1) => 1))
  {first})
(defn odd-steps
  (sig ((n Int)) -> Int ! pure)
  (examples (example (odd-steps 1) => 1))
  (even-steps n))
"""

EXAMPLE_VALUE = """\
(deftype Money (record (cents Int)))
(defn fare
  (sig ((m Money)) -> Int ! pure)
  (examples (example (fare ({constructor} 100)) => 100))
  (.cents m))
"""

DECLARATION_CASES: dict[str, Case] = {
    "a type no declaration gives": Case(
        source=UNKNOWN_TYPE_SOURCE,
        category="unbound_type",
        symbol="Cents",
        line=DECLARATION_LINE,
        column=DECLARATION_COLUMN,
        granularity="declaration",
        twin=with_body("10"),
    ),
    "a record whose field leads back to it": Case(
        source=RECURSIVE_TYPE_SOURCE,
        category="recursive_type",
        symbol="Loop",
        line=1,
        column=10,
        twin=ACYCLIC_TYPE_SOURCE,
        granularity="declaration",
    ),
    "two functions that call each other": Case(
        source=MUTUAL_CALLS.format(first="(odd-steps n)"),
        category="cyclic_dependency",
        symbol="even-steps",
        line=1,
        column=7,
        twin=MUTUAL_CALLS.format(first="n"),
        granularity="declaration",
    ),
    "an example about another function": Case(
        source=with_example("(example (other 100) => 110)"),
        category="unrelated_example",
        symbol="fare",
        line=DECLARATION_LINE,
        column=DECLARATION_COLUMN,
        granularity="declaration",
    ),
    "an example with one argument too many": Case(
        source=with_example("(example (fare 100 7) => 110)"),
        category="arity_mismatch",
        symbol="fare",
        expected=1,
        actual=2,
        line=DECLARATION_LINE,
        column=DECLARATION_COLUMN,
        granularity="declaration",
    ),
    "an example value no constructor builds": Case(
        source=EXAMPLE_VALUE.format(constructor="Cash"),
        category="unbound_constructor",
        symbol="Cash",
        line=2,
        column=7,
        twin=EXAMPLE_VALUE.format(constructor="Money"),
        granularity="declaration",
    ),
}

# --- refusals that stand at the expression they are about ----------------

MONEY = """\
(deftype Money (record (cents Int)))
(defn fare
  (sig ((m Money)) -> Int ! pure)
  (examples (example (fare (Money 100)) => 100))
  {body})
"""

LIGHT = """\
(deftype Light (union (Red) (Green)))
(defn go
  (sig ((l Light)) -> Int ! pure)
  (examples (example (go (Red)) => 1))
  {body})
"""

EXPRESSION_CASES: dict[str, Case] = {
    "a name nothing binds": Case(
        source=with_body("nope"),
        category="unbound_name",
        symbol="nope",
        line=BODY_LINE,
        column=BODY_COLUMN,
    ),
    "a field the type does not declare": Case(
        source=MONEY.format(body="(.pence m)"),
        category="unbound_field",
        symbol="Money.pence",
        line=5,
        column=3,
        twin=MONEY.format(body="(.cents m)"),
    ),
    "a match that leaves a value out": Case(
        source=LIGHT.format(body="(match l ((Red) 1))"),
        category="non_exhaustive_match",
        symbol="Light",
        line=5,
        column=3,
        twin=LIGHT.format(body="(match l ((Red) 1) ((Green) 2))"),
    ),
    "a construct the profile does not have": Case(
        source=with_body("(/ cents 2)"),
        category="unsupported_construct",
        symbol="",
        line=BODY_LINE,
        column=4,
        twin=with_body("(* cents 2)"),
    ),
    "a form the reader never closes": Case(
        source="(defn fare\n",
        category="syntax",
        symbol="",
        line=1,
        column=1,
        granularity="token",
    ),
}

ALL_CASES: dict[str, Case] = {**TYPE_ERRORS, **DECLARATION_CASES}

# Every refused program that carries a place, with the granularity its
# category publishes for it.
PLACED_CASES: dict[str, Case] = {**ALL_CASES, **EXPRESSION_CASES}


def declared_places(source: str) -> set:
    """Every place a declaration of `source` writes its own name.

    Read from the text the test submitted, never from the tool: a
    refusal published as standing at a declaration is checked against
    the places this finds, so a refusal standing anywhere else is seen.
    Each fixture writes at most one declaration per line.
    """
    places = set()
    for number, line in enumerate(source.split("\n"), start=1):
        for word in ("defn", "deftype"):
            marker = f"({word} "
            index = line.find(marker)
            if index >= 0:
                places.add((number, index + len(marker) + 1))
    return places


# --- running the command --------------------------------------------------

@dataclass(frozen=True)
class ToolRun:
    """One run of the `prova` command: everything the operating system
    and the command reported, kept so a crash stays visible."""

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
                "standard error. Every request must come back as one JSON "
                "response, never as a crash."
            ) from None


def run(request: dict) -> ToolRun:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=30.0,
        check=False,
    )
    return ToolRun(proc.returncode, proc.stdout, proc.stderr)


def check(source: str) -> dict:
    return run({"prova": "i1", "operation": "check", "source": source}).response()


def examples(source: str) -> dict:
    return run({"prova": "i1", "operation": "examples", "source": source}).response()


def verify(source: str) -> dict:
    return run({"prova": "i1", "operation": "verify", "source": source}).response()


def evaluate(source: str, function: str, arguments: list) -> dict:
    return run(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": source,
            "function": function,
            "arguments": arguments,
        }
    ).response()


def discover() -> dict:
    return run({"prova": "i1", "operation": "discover"}).response()


# --- reading an answer back -----------------------------------------------

def diagnostics(response: dict) -> list:
    return list(response.get("diagnostics") or [])


def categories(response: dict) -> list:
    return [d.get("category") for d in diagnostics(response)]


def the_one_refusal(response: dict, why: str) -> dict:
    """The single diagnostic the answer carries, so a test reading a
    field reads it from a defect it knows."""
    found = diagnostics(response)
    assert len(found) == 1, (
        f"expected exactly one refusal for {why}, got {len(found)}: {response}. "
        "The fixtures hold one defect per program so that a field read back "
        "belongs to that defect."
    )
    return found[0]


def assert_field(entry: dict, name: str, value, *, why: str) -> None:
    assert entry.get(name) == value, (
        f"the refusal for {why} carries {name}={entry.get(name)!r}, expected "
        f"{value!r}: {entry}. A client acts on this field without reading the "
        "prose, so it must name the thing the refusal is about."
    )


def assert_accepted(response: dict, why: str) -> None:
    assert response.get("status") == "completed", (
        f"the twin for {why} was refused: {response}. The twin differs only in "
        "the repaired defect, so a tool that refuses it refuses everything and "
        "the refusal above says nothing."
    )


def structured(entry: dict) -> dict:
    """Everything in a diagnostic except the prose: what a client acts
    on when it does not read `reason`."""
    return {key: value for key, value in entry.items() if key != "reason"}
