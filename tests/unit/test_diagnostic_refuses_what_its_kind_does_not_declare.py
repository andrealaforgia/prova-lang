"""A refusal cannot be built in a shape its category does not publish.

The manifest tells a client what a refusal of each category carries:
which fields, whether it is placed, which text that place stands in.
That promise is kept where a refusal is built, not at each of the forty
places that build one, so a rule added later cannot quietly answer with
a shape no client was told about.

The public JSON surface cannot observe these refusals: no program draws
one, which is the point. The checker's own contract is the narrowest
surface that carries the rule, as it already is for an empty cycle (see
tests/unit/test_checker_cycle_value.py).
"""

from __future__ import annotations

import pytest

from prova.checker import (
    AboutASymbol,
    AboutNothingNamed,
    AboutTwoTypes,
    Cycle,
    Diagnostic,
)


def _refused(**parts) -> str:
    with pytest.raises(ValueError) as refusal:
        Diagnostic(**parts)
    return str(refusal.value)


def test_a_category_no_kind_declares_is_refused():
    """A refusal of a category the manifest does not publish cannot be
    built, and the refusal says what to do about it."""
    message = _refused(category="no_such_category", reason="something happened")

    assert "no_such_category" in message, message
    assert "DIAGNOSTIC_KINDS" in message, (
        f"the refusal does not say where a category is declared: {message!r}"
    )


def test_a_subject_the_category_does_not_declare_is_refused():
    """A type disagreement carries a symbol with both types; one built
    with a bare symbol is refused."""
    message = _refused(
        category="type_mismatch",
        reason="function 'f' body has type Int, declared return type Bool",
        location=(1, 1),
        about=AboutASymbol("f"),
    )

    assert "AboutTwoTypes" in message and "AboutASymbol" in message, message


def test_a_refusal_of_a_placed_category_without_a_place_is_refused():
    """Every unbound name is published as placed, so one built with no
    place is refused."""
    message = _refused(
        category="unbound_name",
        reason="unbound name 'nope'",
        about=AboutASymbol("nope"),
    )

    assert "no place" in message and "unbound_name" in message, message


def test_a_place_counted_from_zero_is_refused():
    """Lines and columns are counted from 1, so a place at line 0 is no
    place in any text and is refused."""
    for place in ((0, 1), (1, 0)):
        message = _refused(
            category="unbound_name",
            reason="unbound name 'nope'",
            location=place,
            about=AboutASymbol("nope"),
        )
        assert "no place in any text" in message, (place, message)


def test_a_cycle_on_a_category_that_names_none_is_refused():
    """Only the two refusals about a cycle carry one; another category
    carrying one would publish a field no client reads."""
    message = _refused(
        category="unbound_name",
        reason="unbound name 'nope'",
        location=(1, 1),
        about=AboutASymbol("nope"),
        cycle=Cycle(("f", "g")),
    )

    assert "cycle" in message and "unbound_name" in message, message


def test_a_text_the_category_does_not_point_into_is_refused():
    """A category whose place always stands in the source cannot say it
    stands somewhere else, and a category that can stand in two texts
    cannot name a third."""
    single = _refused(
        category="unbound_name",
        reason="unbound name 'nope'",
        location=(1, 1),
        about=AboutASymbol("nope"),
        points_into="argument",
    )
    assert "argument" in single and "manifest does not publish" in single, single

    both = _refused(
        category="malformed_value",
        reason="unclosed '('",
        location=(1, 1),
        about=AboutASymbol("fare"),
        points_into="somewhere-else",
    )
    assert "somewhere-else" in both and "argument" in both, both


def test_a_refusal_built_as_its_category_publishes_it_is_accepted():
    """The accepted demonstration: each shape above, built as the
    manifest publishes it, is a value."""
    placed = Diagnostic(
        "unbound_name", "unbound name 'nope'", (1, 1), about=AboutASymbol("nope")
    )
    assert placed.location == (1, 1)

    typed = Diagnostic(
        "type_mismatch",
        "function 'f' body has type Int, declared return type Bool",
        (4, 3),
        about=AboutTwoTypes("f", "Bool", "Int"),
    )
    assert typed.about.expected == "Bool" and typed.about.actual == "Int"

    unplaced = Diagnostic(
        "operation_unavailable", "operation 'build' is not available in I1"
    )
    assert unplaced.location is None and unplaced.about == AboutNothingNamed()

    in_an_argument = Diagnostic(
        "malformed_value",
        "unclosed '('",
        (1, 1),
        about=AboutASymbol("fare"),
        points_into="argument",
    )
    assert in_an_argument.points_into == "argument"
