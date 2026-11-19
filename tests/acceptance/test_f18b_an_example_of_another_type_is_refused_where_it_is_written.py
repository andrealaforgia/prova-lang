"""F18b -- an example written with a value of another type is refused
where it stands.

An example is a closed value written in the program beside the types it
must have, so whether it has them is known when the program is read.
Left to a run it is not merely late: the obligations are listed about
it, the example is counted among those that passed, the program is
called `verified`, an artefact of it is published, and the first thing
to notice is that artefact refusing the value at run time. The checker
refuses it instead, so nothing downstream is ever reached.

Four shapes, each a value of the wrong type in a different place: an
argument, the stated result, a field inside a record, and a value of
another declared type altogether.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program. The last test sends a
program whose example types check and requires `check`, `verify` and
`build` all to accept it.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from _f18_fixtures import ask

# The one category the checker already publishes for a value standing
# where a value of another type is declared.
THE_CATEGORY = "type_mismatch"

A_BOOLEAN_WHERE_A_NUMBER_IS_DECLARED = """(defn f
  (sig ((n Int)) -> Int ! pure)
  (examples (example (f true) => 0))
  0)
"""

A_BOOLEAN_STATED_AS_A_NUMBER_RESULT = """(defn f
  (sig ((n Int)) -> Int ! pure)
  (examples (example (f 1) => true))
  0)
"""

A_FIELD_OF_ANOTHER_TYPE_INSIDE_A_RECORD = """(deftype Pair (record (a Int)))

(defn f
  (sig ((p Pair)) -> Int ! pure)
  (examples (example (f (Pair true)) => 0))
  0)
"""

A_VALUE_OF_ANOTHER_DECLARED_TYPE = """(deftype Pair (record (a Int)))
(deftype Sign (union (Plus) (Minus)))

(defn f
  (sig ((p Pair)) -> Int ! pure)
  (examples (example (f (Plus)) => 0))
  0)
"""

AN_EXAMPLE_OF_THE_DECLARED_TYPES = """(defn f
  (sig ((n Int)) -> Int ! pure)
  (ensures (= result 0))
  (examples (example (f 1) => 0))
  0)
"""


@dataclass(frozen=True)
class AWrongExample:
    about: str
    source: str
    expected: str
    actual: str


THE_WRONG_ONES = (
    AWrongExample(
        "a boolean supplied where a number is declared",
        A_BOOLEAN_WHERE_A_NUMBER_IS_DECLARED,
        "Int",
        "Bool",
    ),
    AWrongExample(
        "a boolean stated as the result of a function answering a number",
        A_BOOLEAN_STATED_AS_A_NUMBER_RESULT,
        "Int",
        "Bool",
    ),
    AWrongExample(
        "a field of another type inside a record",
        A_FIELD_OF_ANOTHER_TYPE_INSIDE_A_RECORD,
        "Int",
        "Bool",
    ),
    AWrongExample(
        "a value of another declared type",
        A_VALUE_OF_ANOTHER_DECLARED_TYPE,
        "Pair",
        "Sign",
    ),
)


def _check(source: str) -> dict:
    return ask({"operation": "check", "source": source})


def _verify(source: str) -> dict:
    return ask({"operation": "verify", "source": source})


def _build(source: str, output_file) -> dict:
    return ask(
        {
            "operation": "build",
            "source": source,
            "entry": "f",
            "output_file": str(output_file),
        }
    )


def _the_refusal(answer: dict, about: str) -> dict:
    assert answer.get("status") == "invalid_program", (
        f"WHAT: {about} is answered {answer.get('status')!r}, not "
        "'invalid_program'. "
        "WHY: an example of another type is a fault of the source; a tool "
        "that accepts it goes on to list obligations about it, call the "
        "program verified and publish an artefact that refuses the value at "
        "run time. "
        f"HOW: inspect the answer: {answer}"
    )
    wrong = [
        diagnostic
        for diagnostic in answer.get("diagnostics", [])
        if diagnostic["category"] == THE_CATEGORY
    ]
    assert wrong, (
        f"WHAT: {about} is refused with "
        f"{[d['category'] for d in answer.get('diagnostics', [])]} and none of "
        f"them is {THE_CATEGORY!r}. "
        "WHY: the Owner reads the category to know what to repair; a refusal "
        "under another name sends them to the wrong place. "
        f"HOW: inspect the answer: {answer}"
    )
    return wrong[0]


@pytest.mark.parametrize(
    "case", THE_WRONG_ONES, ids=[case.about for case in THE_WRONG_ONES]
)
def test_the_checker_refuses_it_and_says_which_types_disagree(case: AWrongExample):
    """Given a program whose example writes a value of another type,
    when the Owner checks it, then the program is refused where the
    declaration stands, naming the type declared there and the type
    written."""
    diagnostic = _the_refusal(_check(case.source), case.about)

    assert diagnostic["symbol"] == "f", diagnostic
    assert diagnostic.get("expected") == case.expected, (
        f"WHAT: the refusal about {case.about} says {diagnostic.get('expected')!r} "
        f"is declared and the signature declares {case.expected!r}. "
        "WHY: a refusal that names the wrong type is a refusal the Owner "
        "cannot act on. "
        f"HOW: inspect the diagnostic: {diagnostic}"
    )
    assert diagnostic.get("actual") == case.actual, (
        f"WHAT: the refusal about {case.about} says the value is "
        f"{diagnostic.get('actual')!r} and it is written as {case.actual!r}. "
        "WHY: the Owner repairs the value the refusal names. "
        f"HOW: inspect the diagnostic: {diagnostic}"
    )
    location = diagnostic.get("location") or {}
    assert location.get("line", 0) >= 1 and location.get("column", 0) >= 1, (
        f"WHAT: the refusal about {case.about} stands nowhere: {location}. "
        "WHY: every refusal of this tool says where in the text it is about. "
        f"HOW: inspect the diagnostic: {diagnostic}"
    )


@pytest.mark.parametrize(
    "case", THE_WRONG_ONES, ids=[case.about for case in THE_WRONG_ONES]
)
def test_nothing_downstream_is_reached_for_it(case: AWrongExample, tmp_path):
    """Given the same programs, when the Owner asks what one owes or
    asks for an artefact of it, then neither answers about the program:
    no obligation is listed, no word is said about verification, and no
    file is written."""
    answered = _verify(case.source)
    _the_refusal(answered, case.about)
    assert "result" not in answered, (
        f"WHAT: the refused program {case.about} still carries a result: "
        f"{answered.get('result')}. "
        "WHY: an obligation listed about a program the tool refused reads as "
        "work the Owner owes on a program this tool never accepted. "
        f"HOW: inspect the answer: {answered}"
    )

    written = tmp_path / "artefact.py"
    _the_refusal(_build(case.source, written), case.about)
    assert not written.exists(), (
        f"WHAT: a build of the refused program {case.about} wrote "
        f"{written}. "
        "WHY: the artefact would exit with a failure the first time it is "
        "given the value its own example states. "
        "HOW: inspect the build answer."
    )


def test_an_example_of_the_declared_types_is_still_accepted(tmp_path):
    """Given a program whose example writes values of the declared
    types, when the Owner checks it, asks what it owes and asks for an
    artefact, then all three are answered."""
    written = tmp_path / "artefact.py"
    answers = {
        "check": _check(AN_EXAMPLE_OF_THE_DECLARED_TYPES),
        "verify": _verify(AN_EXAMPLE_OF_THE_DECLARED_TYPES),
        "build": _build(AN_EXAMPLE_OF_THE_DECLARED_TYPES, written),
    }
    refused = {
        operation: answer.get("status")
        for operation, answer in answers.items()
        if answer.get("status") != "completed"
    }
    assert not refused, (
        f"WHAT: {refused} for a program whose example writes an Int where an "
        "Int is declared. "
        "WHY: the tests above would all pass for a tool that refused every "
        "program; this one is what stops them from meaning nothing. "
        f"HOW: inspect the answers: {answers}"
    )
    assert written.exists(), (
        f"WHAT: the build of an accepted program wrote no {written}. "
        "WHY: the build test above reads an absent file as a refusal that "
        "worked; it means nothing unless an accepted program leaves one. "
        f"HOW: inspect the build answer: {answers['build']}"
    )
