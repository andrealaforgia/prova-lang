"""F10.B6 -- the refusals that used to say nothing about where now point
at the declaration they are about.

A type no declaration gives, a record that leads back to itself, two
functions that call each other, an example about another function, an
example with the wrong number of arguments and an example value no
constructor builds: six refusals that carried no place at all.

The place is the declared name they are about. The parsed tree keeps no
place for a type written inside a signature, for an example of its own,
or for a value inside an example, so the place is the declaration's, not
the exact word; the manifest says so for each category.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool stamped line 1 column 1 on everything. The six
cases stand at four different places, each pinned, and the last two
stand on line 2, so a constant place is seen. Each case is paired with
the twin the tool accepts.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    DECLARATION_CASES,
    INVALID_PROGRAM,
    LOCATION,
    SYMBOL,
    assert_accepted,
    assert_field,
    check,
    the_one_refusal,
)


def test_each_refusal_about_a_declaration_names_it_and_points_at_it():
    """Given the 6 programs whose refusal carried no place, when each is
    checked, then the refusal names the symbol it is about and carries
    the line and column of the declaration it stands in."""
    for why, case in DECLARATION_CASES.items():
        response = check(case.source)
        assert response.get("status") == INVALID_PROGRAM, (why, response)
        entry = the_one_refusal(response, why)

        assert_field(entry, "category", case.category, why=why)
        assert_field(entry, SYMBOL, case.symbol, why=why)
        assert entry.get(LOCATION) == {"line": case.line, "column": case.column}, (
            f"the refusal for {why} is placed at {entry.get(LOCATION)}, expected "
            f"line {case.line} column {case.column}: {entry}. A client opens the "
            "file at that place to repair it."
        )

        assert_accepted(check(case.twin), why)


def test_an_example_counted_wrong_says_how_many_were_expected_and_found():
    """Given an example passing 2 arguments to a function of 1
    parameter, when it is checked, then `expected` is 1 and `actual` is
    2: the counts as numbers, not as a sentence."""
    why = "an example with one argument too many"
    entry = the_one_refusal(check(DECLARATION_CASES[why].source), why)

    assert entry.get("expected") == 1 and entry.get("actual") == 2, (
        f"the refusal does not carry the two counts: {entry}. A client compares "
        "what the function takes with what the example passes."
    )
