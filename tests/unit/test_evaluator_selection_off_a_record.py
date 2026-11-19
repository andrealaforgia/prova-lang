"""A selector the checker would refuse says what went wrong, rather
than failing on a list lookup.

No program `check` accepts reaches these trees: field selection is
defined only for records (SPEC.md line 142) and a selector naming a
field the operand's type does not declare is refused before anything
runs. The trees below are built by hand, bypassing the checker, so that
the one line the evaluator cannot otherwise be asked about is still
observed: it must name the selector, the value it stood on and the rule
that keeps such a tree out, not raise `ValueError: 'x' is not in list`.
"""

from __future__ import annotations

import pytest

from prova import evaluator, syntax
from prova.reader import read_program
from prova.values import UNIT, ConstructorValue

UNION_PROGRAM = """
(deftype E (union (A (x Int)) (B)))
(defn f (sig ((e E)) -> Int ! pure)
  (examples (example (f (B)) => 0))
  0)
"""


def _program() -> syntax.Program:
    return syntax.parse_program(read_program(UNION_PROGRAM))


def _select(field: str, value: object) -> object:
    program = _program()
    return evaluator.eval_expr(
        syntax.FieldAccess(field, syntax.NameRef("e", 1, 1), 1, 1),
        {"e": value},
        program,
    )


def test_a_selector_on_a_variant_without_that_field_names_the_selector_and_the_value():
    with pytest.raises(evaluator.SelectionOffARecord) as refused:
        _select("x", ConstructorValue("B", ()))

    reason = refused.value.reason
    assert "'x'" in reason, reason
    assert "'B'" in reason, reason
    assert "no field" in reason, reason


def test_a_selector_on_a_variant_that_declares_other_fields_names_them():
    with pytest.raises(evaluator.SelectionOffARecord) as refused:
        _select("y", ConstructorValue("A", (0,)))

    reason = refused.value.reason
    assert "'y'" in reason, reason
    assert "'x'" in reason, reason


def test_a_selector_on_a_value_that_is_not_a_constructed_one_is_named_too():
    with pytest.raises(evaluator.SelectionOffARecord) as refused:
        _select("x", UNIT)

    assert "carries no fields" in refused.value.reason, refused.value.reason


def test_the_selector_the_checker_does_accept_still_reads_its_field():
    assert _select("x", ConstructorValue("A", (7,))) == 7
