"""The checker's table of builtin operators agrees with the language.

The table says how many arguments each builtin operator takes and how
its operands are read. Both the refusal of a wrongly counted call and
the operand checks read it. An operator the language has but the table
does not would stop the checker with a fault of its own instead of
answering about the program, so the two must name exactly the same
operators.

Reads the published contract of the checker and the syntax module.
"""

from __future__ import annotations

import pytest

from prova import checker, syntax


def test_the_checker_knows_exactly_the_operators_the_language_has():
    """Every operator the language parses has an entry in the table,
    and the table invents none the language does not have."""
    known = set(checker.BUILTIN_OPERATORS)
    in_the_language = set(syntax.OPERATORS)

    assert known == in_the_language, (
        f"the checker's operator table and the language disagree: "
        f"{sorted(in_the_language - known)} are operators the table does not "
        f"describe, and {sorted(known - in_the_language)} are entries the "
        "language does not have. A program using an operator the table is "
        "missing stops the checker instead of being answered. Add the operator "
        "to the table beside the others, with the number of arguments SPEC.md "
        "gives it and the group whose operands it reads."
    )


def test_every_operator_belongs_to_one_group_of_operands():
    """Each entry falls in exactly one of the four groups the operand
    checks ask about, so none is left without its operand rule."""
    groups = {
        "numeric": checker.NUMERIC_OPERATORS,
        "comparison": checker.COMPARISON_OPERATORS,
        "equality": checker.EQUALITY_OPERATORS,
        "boolean": checker.BOOLEAN_OPERATORS,
    }

    for operator in checker.BUILTIN_OPERATORS:
        holding = [name for name, members in groups.items() if operator in members]
        assert len(holding) == 1, (
            f"the operator {operator!r} belongs to {holding or 'no group'} instead "
            "of exactly one. An operator in no group reaches the end of the "
            "operand checks and stops the checker; an operator in two is read by "
            "two different operand rules. Give its table entry one of the groups "
            f"{sorted(groups)}."
        )


def test_the_number_of_arguments_comes_from_that_table():
    """`arity_of` answers from the table for every operator, and says
    so plainly for a name that is not an operator at all."""
    for operator, builtin in checker.BUILTIN_OPERATORS.items():
        assert checker.arity_of(operator) == builtin.arity, (
            f"the number of arguments answered for {operator!r} is not the one "
            "its table entry gives. One table is the only place that number is "
            "written; read it from there."
        )

    with pytest.raises(ValueError, match="unknown operator"):
        checker.arity_of("mod")
