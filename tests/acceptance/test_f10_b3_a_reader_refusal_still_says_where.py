"""F10.B3 -- a refusal that comes from the reader still says where.

The reader refuses a source and it refuses a value a request supplies as
an argument. Both refusals know the place they stand at; only the first
used to report it.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool stamped line 1 column 1 on every reader
refusal. The second case supplies two values on one line and requires
the place of the second one, column 3, so a constant place is seen. The
last case evaluates a well-formed argument and requires an answer, so a
tool that refuses every argument is seen.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    INVALID_INPUT,
    LOCATION,
    WELL_FORMED,
    check,
    evaluate,
    revision_of,
    the_one_refusal,
)

UNCLOSED_SOURCE = "(defn fare\n"

# Each argument text the reader cannot read as one value, and the place
# in that text the reader stands at when it refuses.
MALFORMED_ARGUMENTS = {
    "an argument that opens a list and never closes it": ("(", {"line": 1, "column": 1}),
    "an argument that is empty": ("", {"line": 1, "column": 1}),
    "an argument holding two values": ("1 2", {"line": 1, "column": 3}),
    "an argument that closes a list it never opened": (")", {"line": 1, "column": 1}),
}


def test_a_refused_argument_says_where_in_the_argument_it_stands():
    """Given the 4 argument texts the reader cannot read as one value,
    when `fare` is evaluated with each, then the refusal carries the
    place in that text where the reader stopped."""
    for why, (argument, place) in MALFORMED_ARGUMENTS.items():
        response = evaluate(WELL_FORMED, "fare", [argument])
        assert response.get("status") == INVALID_INPUT, (why, response)
        entry = the_one_refusal(response, why)
        assert entry.get(LOCATION) == place, (
            f"the refusal for {why} is placed at {entry.get(LOCATION)} but the "
            f"reader stopped at {place}: {entry}. A refusal from the reader "
            "says where it stopped, so a client can point at the text."
        )

    answered = evaluate(WELL_FORMED, "fare", ["7"])
    assert answered.get("status") == "completed", (
        f"a well-formed argument was refused: {answered}. The refusals above "
        "are about the argument text, not about every argument."
    )


def test_a_refused_source_still_says_where_it_stands():
    """Control plus guard: given a source that opens a form and never
    closes it, when it is checked, then the refusal still carries the
    place the form opens at, line 1 column 1."""
    response = check(UNCLOSED_SOURCE)
    entry = the_one_refusal(response, "a source with an unclosed form")

    assert entry.get("category") == "syntax", entry
    assert entry.get(LOCATION) == {"line": 1, "column": 1}, (
        f"a source the reader cannot read came back without the place it "
        f"stopped at: {entry}."
    )
    assert entry.get("source_revision") == revision_of(UNCLOSED_SOURCE), (
        f"the refusal does not say which text it is about: {entry}. A reader "
        "refusal is about a source too."
    )
