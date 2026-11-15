"""R1.B1 -- a program whose example writes a record without all its
fields is refused where it stands, instead of being accepted and then
breaking the tool that runs it.

The hour clock declares `Clock` with one field. Delete the single
character that holds the number inside `(Clock 1)` and the example reads
`(Clock)`: a record with no field at all. The tool used to accept that
program and then end in a traceback while running the example, so a
caller got no answer, no place to repair and an exit code that said the
tool had broken rather than its input.

still passes if: the tool refused every program. The last two tests send
the untouched programs and require the same answers they give today.
"""

from __future__ import annotations

import pytest

from _r1_robustness_fixtures import (
    ACTUAL,
    ARITY_MISMATCH,
    EXPECTED,
    INVALID_PROGRAM,
    SYMBOL,
    answered,
    assert_accepted,
    assert_located,
    hour_clock_source,
    shipped_programs,
    the_refusal,
    without_character,
)

# The two characters whose removal left a record empty. Both hold the
# `1` inside a `(Clock 1)` written in an example.
EMPTIED_A_CLOCK = (550, 1191)

# A record with one field, and an example that writes it with none and
# with two: the same defect as the hour clock's, in a program small
# enough to read.
ONE_FIELD_RECORD = """\
(deftype Box (record (size Int)))

(defn box-size
  (sig ((b Box)) -> Int ! pure)
  (examples (example (box-size {written}) => 3))
  (.size b))
"""

WRITTEN_WRONG = {
    "no field where one is declared": ("(Box)", 1, 0),
    "two fields where one is declared": ("(Box 3 4)", 1, 2),
}


def _examples(source: str) -> dict:
    return answered(
        {"prova": "i1", "operation": "examples", "source": source},
        "a program whose example writes a record with the wrong fields",
    )


@pytest.mark.parametrize("index", EMPTIED_A_CLOCK)
def test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands(index):
    """Given the hour clock with the character at a named position
    deleted, so one example writes `(Clock)` instead of `(Clock 1)`, when
    a caller asks for the examples, then the answer says the program is
    invalid, names `Clock`, says it takes 1 field and got 0, and says
    where to go.
    """
    source = without_character(hour_clock_source(), index)

    response = _examples(source)

    why = f"the hour clock with character {index} deleted"
    assert response.get("status") == INVALID_PROGRAM, (
        f"the tool answered {response.get('status')!r} for {why}: {response}. A "
        "record written without the field it declares is a program the rules of "
        "core-0 refuse, so the answer says the program is invalid; running it "
        "instead leaves the tool reading a field that is not there."
    )
    assert "result" not in response, (
        f"the answer for {why} carries a result beside its refusal: {response}. "
        "A program that was never run has no examples to report."
    )
    refusal = the_refusal(response, ARITY_MISMATCH, why)
    assert refusal.get(SYMBOL) == "Clock", (
        f"the refusal for {why} names {refusal.get(SYMBOL)!r}, not 'Clock': "
        f"{refusal}. A caller repairs the record the refusal names."
    )
    assert (refusal.get(EXPECTED), refusal.get(ACTUAL)) == (1, 0), (
        f"the refusal for {why} says {refusal.get(EXPECTED)!r} fields were "
        f"expected and {refusal.get(ACTUAL)!r} given: {refusal}. `Clock` "
        "declares one field and the example writes none, so a caller reads 1 "
        "and 0 and knows what to add."
    )
    assert_located(refusal, why)


@pytest.mark.parametrize("why", sorted(WRITTEN_WRONG))
def test_a_record_written_with_the_wrong_number_of_fields_is_refused(why):
    """Given a program whose example writes `Box` with no field or with
    two where one is declared, when a caller asks for the examples, then
    the answer says the program is invalid and reports the field count
    declared beside the one written.
    """
    written, declared, given = WRITTEN_WRONG[why]

    response = _examples(ONE_FIELD_RECORD.format(written=written))

    assert response.get("status") == INVALID_PROGRAM, (
        f"the tool answered {response.get('status')!r} for {why}: {response}. "
        "An example supplies one value per declared field; a value with another "
        "number of them is a program core-0 refuses."
    )
    refusal = the_refusal(response, ARITY_MISMATCH, why)
    assert (refusal.get(SYMBOL), refusal.get(EXPECTED), refusal.get(ACTUAL)) == (
        "Box",
        declared,
        given,
    ), (
        f"the refusal for {why} reports {refusal.get(SYMBOL)!r} with "
        f"{refusal.get(EXPECTED)!r} expected and {refusal.get(ACTUAL)!r} given: "
        f"{refusal}. A caller counts the fields it must add or remove from "
        "these two numbers."
    )
    assert_located(refusal, why)


def test_a_record_written_with_every_field_is_still_run():
    """Given the same program with `Box` written with the one field it
    declares, when a caller asks for the examples, then the example runs
    and reports 3.
    """
    response = _examples(ONE_FIELD_RECORD.format(written="(Box 3)"))

    assert_accepted(response, "a record written with the field it declares")
    reported = [entry.get("actual") for entry in response["result"]["examples"]]
    assert reported == ["3"], (
        f"the example reported {reported}, expected ['3']: {response}. The "
        "program reads the size out of the box it was given, so a tool that "
        "refuses the empty box must still run the full one."
    )


@pytest.mark.parametrize("name", sorted(shipped_programs()))
def test_every_shipped_program_is_still_answered(name):
    """Given each program this repository ships, when a caller asks for
    its examples, then every declared example is run and passes, exactly
    as before.
    """
    response = _examples(shipped_programs()[name])

    assert_accepted(response, f"{name}, which this repository ships")
    entries = response["result"]["examples"]
    failed = [entry for entry in entries if not entry.get("passed")]
    assert entries and not failed, (
        f"{len(failed)} of the {len(entries)} examples of {name} did not pass: "
        f"{failed}. A new rule that refuses a program this repository ships, or "
        "changes what one of its examples reports, has become a rule about "
        "correct programs."
    )
