"""A part of a read program is built with the place it stands at, or not
at all.

The place is what a reader of a published tree opens to find the part.
A part that could be built without one would be answered standing
nowhere, and the reader would only learn of it when it tried to open
line 0 of a text whose lines start at 1.
"""

from __future__ import annotations

import pytest

from prova import syntax

BUILT_WITHOUT_A_PLACE = {
    "a signature": lambda: syntax.Signature((), "Int"),
    "an example": lambda: syntax.Example("twice", (1,), 2),
    "a function": lambda: syntax.Function("twice", None, (), (), (), None),
    "a parameter": lambda: syntax.Parameter("n", "Int"),
    "a binding": lambda: syntax.Binding("m", None),
    "a declared record": lambda: syntax.RecordType("Counter", ()),
    "a clause of a match": lambda: syntax.MatchClause(None, None),
    "a pattern that binds a name": lambda: syntax.PatVar("m"),
}


@pytest.mark.parametrize("what", sorted(BUILT_WITHOUT_A_PLACE))
def test_a_part_built_without_a_place_is_refused(what):
    with pytest.raises(TypeError) as refused:
        BUILT_WITHOUT_A_PLACE[what]()

    assert "line" in str(refused.value) and "column" in str(refused.value), (
        f"{what} was built without saying where it stands, and the refusal "
        f"says {str(refused.value)!r}: the place is part of what it is, so "
        "the refusal must name the line and the column it was built without"
    )


def test_the_same_parts_are_built_when_the_place_is_given():
    """The positive control: nothing above is refused for another reason."""
    built = (
        syntax.Signature((), "Int", 1, 1),
        syntax.Example("twice", (1,), 2, 1, 1),
        syntax.Parameter("n", "Int", 1, 1),
        syntax.Binding("m", None, 1, 1),
        syntax.RecordType("Counter", (), 1, 1),
        syntax.MatchClause(None, None, 1, 1),
        syntax.PatVar("m", 1, 1),
    )

    assert [(one.line, one.column) for one in built] == [(1, 1)] * 7, (
        f"a part built with line 1 column 1 does not carry it: {built}"
    )
