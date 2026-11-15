"""Acceptance test for F8: the sources a rule about whose example it is
must not take over.

A source the reader cannot read at all, and a source that declares
nothing, are refused for reasons of their own. Neither is an example
about another function, so neither may be answered with that word.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool stopped refusing these sources. Each test
requires the refusal that belongs to the source, not merely the absence
of the new one.
"""

from __future__ import annotations

from _f8_example_subject_fixtures import (
    AN_EXAMPLES_CLAUSE_THAT_IS_NEVER_CLOSED,
    A_SOURCE_WITH_NOTHING_IN_IT,
    SYNTAX_CATEGORY,
    UNRELATED_EXAMPLE_CATEGORY,
    assert_answered,
    categories,
    check,
)


def test_a_source_with_nothing_in_it_is_refused_for_its_own_reason():
    """Given a source of 0 characters, when it is checked, then it is
    invalid, and the refusal is not the one about whose example it is:
    a source that declares no function declares no example either."""
    response = assert_answered(check(A_SOURCE_WITH_NOTHING_IN_IT), "an empty source")

    assert response.get("status") == "invalid_program", (
        f"a source with nothing in it was not refused: {response}. Core-0 asks for "
        "at least 1 declaration."
    )
    assert UNRELATED_EXAMPLE_CATEGORY not in categories(response), (
        f"an empty source was answered with {UNRELATED_EXAMPLE_CATEGORY!r}: "
        f"{response}. Keep that word for a function whose example is about another "
        "function."
    )


def test_an_examples_clause_that_is_never_closed_is_still_a_reading_refusal():
    """Given a source whose `(examples ...` is never closed, when it is
    checked, then it is invalid for the reading refusal it already
    carried, and not for whose example it is."""
    response = assert_answered(
        check(AN_EXAMPLES_CLAUSE_THAT_IS_NEVER_CLOSED), "an unclosed examples clause"
    )

    assert categories(response) == [SYNTAX_CATEGORY], (
        f"a source the reader cannot read was answered with {categories(response)}: "
        f"{response}. A source that cannot be read is refused as it was before; "
        "rules about declared examples are reached only after it is read."
    )
