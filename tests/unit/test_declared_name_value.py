"""A declared name with no spelling cannot be built.

Every refusal this feature reports names the symbol that was declared
twice. A nameless declaration would produce a refusal that tells the
reader nothing to repair, so the value refuses to exist, at its
constructor, rather than being checked again at each place that reads
it.
"""

from __future__ import annotations

import pytest

from prova.syntax import DeclaredName


def test_a_declared_name_without_a_spelling_cannot_be_built():
    with pytest.raises(ValueError) as refusal:
        DeclaredName("function", "", 1, 1)

    assert "which name to repair" in str(refusal.value), (
        f"the refusal does not say why a nameless declaration is useless: "
        f"{refusal.value}. Say what is missing and what a reader would lose."
    )


def test_a_declared_name_with_a_spelling_describes_itself_and_its_place():
    declared = DeclaredName("field", "amount", 4, 25, within="record 'Money'")

    assert declared.described() == "field 'amount' in record 'Money'"
    assert declared.place() == "line 4 column 25"
