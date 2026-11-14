"""A reported cycle of types always names at least one type.

The refusal a type cycle carries tells the reader which declarations
lead back to each other, so one built with no member would carry a
refusal that says nothing. The rule lives in the constructor rather than
at each place that builds one, and these two tests are its refused and
accepted demonstration.

The public JSON surface cannot observe this: no program produces an
empty cycle, which is the point. The checker's own contract is the
narrowest surface that carries the rule, and this repository already
tests it directly (see the other tests/unit/test_checker_*.py files).
"""

from __future__ import annotations

import pytest

from prova.checker import TypeCycle


def test_a_type_cycle_that_names_no_type_is_refused_with_a_reason():
    """Building a type cycle with no member is refused, and the refusal
    says what was wrong and what to build it from."""
    with pytest.raises(ValueError) as refusal:
        TypeCycle(())

    message = str(refusal.value)
    assert "at least one type" in message, (
        f"the refusal does not say what was wrong with the cycle: {message!r}. "
        "State that a cycle must name at least one type."
    )
    assert "depending on each other" in message, (
        f"the refusal does not say what to build a cycle from: {message!r}. "
        "Name the dependency search whose result is a valid member list."
    )


def test_a_cycle_of_two_types_names_both_in_the_order_they_are_declared():
    """A cycle built from the types the search found keeps their order
    and names both of them in the sentence it carries."""
    cycle = TypeCycle(("Invoice", "Payment"))

    assert cycle.names() == ("Invoice", "Payment")
    assert cycle.described() == "'Invoice' and 'Payment'"
    assert cycle.diagnostic().cycle is cycle, (
        "the diagnostic a type cycle builds does not carry that cycle, so a "
        "caller cannot read its members from the answer"
    )
