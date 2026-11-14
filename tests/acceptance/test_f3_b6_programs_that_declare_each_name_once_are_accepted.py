"""Acceptance test for F3 criterion 6, and the control for criteria 1-5:
a program that declares each name once is accepted, and two different
records that each have a field spelled `amount` are accepted.

SPEC.md lines 137-143: equal field spellings in different records are
permitted.

Each program here differs from a refused program of this feature by one
name, so a tool that refuses every program fails here.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool accepted every program. The refusals in
test_f3_b1..b5 require each near-identical program with one name
repeated to be refused.
"""

from __future__ import annotations

from _f3_duplicate_fixtures import (
    RECORD_WITH_THE_FIELD_AMOUNT_TWICE,
    TWO_CONSTRUCTORS_FROM_TWO_TYPES,
    TWO_FUNCTIONS_WITH_TWO_NAMES,
    TWO_RECORDS_SHARING_THE_FIELD_AMOUNT,
    TWO_TYPES_WITH_TWO_NAMES,
    accepted,
    check,
    declaring_an_ordinary_type,
)


def test_two_records_that_each_have_a_field_called_amount_are_accepted():
    """Given a record `Money` with a field `amount` and a record
    `Invoice` that also has a field `amount`, when the program is
    checked, then it is accepted with no diagnostic -- and the tool
    answers a different outcome for the program that spells `amount`
    twice inside one record, so acceptance here is a decision about
    where the field sits, not a tool that accepts everything."""
    shared_between_two_records = check(TWO_RECORDS_SHARING_THE_FIELD_AMOUNT)
    repeated_inside_one_record = check(RECORD_WITH_THE_FIELD_AMOUNT_TWICE)

    assert accepted(shared_between_two_records), (
        f"two different records that each have a field spelled `amount` were "
        f"refused: {shared_between_two_records.response()}. Equal field spellings "
        "in different records are permitted; refuse a repeated field only inside "
        "one record or variant."
    )
    assert not accepted(repeated_inside_one_record), (
        "the program whose one record declares `amount` twice was accepted, like "
        "the program whose two records each declare it once: "
        f"{repeated_inside_one_record.response()}. The two must differ -- a field "
        "repeated inside one record is refused, a spelling shared between two "
        "records is kept."
    )


def test_two_functions_with_two_names_are_accepted():
    """Control for criterion 1: the two-function program with the second
    function renamed `doubled` is accepted."""
    run = check(TWO_FUNCTIONS_WITH_TWO_NAMES)

    assert accepted(run), (
        f"a program whose two functions have different names was refused: "
        f"{run.response()}. Only a repeated name may be refused for that reason."
    )


def test_two_types_with_two_names_are_accepted():
    """Control for criterion 2: the two-type program with the second type
    renamed `Deposit` is accepted."""
    run = check(TWO_TYPES_WITH_TWO_NAMES)

    assert accepted(run), (
        f"a program whose two types have different names was refused: "
        f"{run.response()}. Only a repeated name may be refused for that reason."
    )


def test_two_types_introducing_two_constructor_names_are_accepted():
    """Control for criterion 3: the same record and union, with the
    variant renamed `Transfer`, are accepted."""
    run = check(TWO_CONSTRUCTORS_FROM_TWO_TYPES)

    assert accepted(run), (
        f"a program whose constructors all have different names was refused: "
        f"{run.response()}. Only a repeated constructor name may be refused."
    )


def test_a_record_named_like_no_builtin_type_is_accepted():
    """Control for criterion 5: the same one-record program under the
    name `Amount`, which the language does not reserve, is accepted."""
    run = check(declaring_an_ordinary_type("Amount"))

    assert accepted(run), (
        f"a record type with a name the language does not reserve was refused: "
        f"{run.response()}. Only `Int`, `Bool` and `Unit` may not be redeclared."
    )
