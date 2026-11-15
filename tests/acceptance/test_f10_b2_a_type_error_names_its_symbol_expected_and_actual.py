"""F10.B2 -- a type error names the symbol it is about and gives the
expected and the actual type as separate fields.

A client repairs `flagged.flag` from `Bool` to `Int` without parsing the
sentence that says the same thing.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool named the same symbol for every type error.
The three cases below name three different symbols -- a function, an
operator and a parameter of a called function -- and each pins its own
expected and actual type, so one answer for all three is seen. Each case
is paired with the twin the tool accepts, so a tool that refuses
everything is seen too.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    ACTUAL,
    EXPECTED,
    INVALID_PROGRAM,
    SYMBOL,
    TYPE_ERRORS,
    assert_accepted,
    assert_field,
    check,
    the_one_refusal,
)


def test_a_type_error_names_the_symbol_and_both_types():
    """Given the 3 programs whose types disagree, when each is checked,
    then the refusal names the symbol ('fare', '+', 'flagged.flag') and
    carries the expected and the actual type as 2 separate fields."""
    for why, case in TYPE_ERRORS.items():
        response = check(case.source)
        assert response.get("status") == INVALID_PROGRAM, (why, response)
        entry = the_one_refusal(response, why)

        assert_field(entry, "category", "type_mismatch", why=why)
        assert_field(entry, SYMBOL, case.symbol, why=why)
        assert_field(entry, EXPECTED, case.expected, why=why)
        assert_field(entry, ACTUAL, case.actual, why=why)

        assert_accepted(check(case.twin), why)


def test_the_two_types_are_separate_fields_not_one_sentence():
    """Given a body whose type is not the declared return type, when it
    is checked, then `expected` is exactly 'Bool' and `actual` is exactly
    'Int': 2 fields a client compares, not 1 sentence it parses."""
    why = "a body that does not have the declared return type"
    entry = the_one_refusal(check(TYPE_ERRORS[why].source), why)

    assert entry.get(EXPECTED) == "Bool" and entry.get(ACTUAL) == "Int", entry
    assert entry.get(EXPECTED) != entry.get(ACTUAL), (
        f"the expected and the actual type are the same value: {entry}. A type "
        "error reports a disagreement, so the two sides differ."
    )
