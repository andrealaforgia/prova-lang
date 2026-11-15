"""F13.B5 -- the tool publishes the shape of the contract report, so a
client reads it from the tool instead of guessing it from one answer.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the manifest published a shape nobody honours. The
second and third tests read five real answers and check every field and
every word in them against the published shape.
"""

from __future__ import annotations

from _f13_contract_fixtures import (
    NO_FUNCTION_AT_ALL,
    NO_PRECONDITION,
    PROMISES_NOTHING,
    REAL_CONTRACT,
    TRIVIAL_POSTCONDITION,
    ask,
    check,
    discover,
    entries_by_function,
    hour_clock_source,
    report_of,
)

EVERY_SOURCE = (
    NO_PRECONDITION,
    TRIVIAL_POSTCONDITION,
    REAL_CONTRACT,
    PROMISES_NOTHING,
    NO_FUNCTION_AT_ALL,
)
SHAPE_KEYS = {
    "carried_by",
    "what",
    "entry_fields",
    "strengths",
    "totals_fields",
    "states_a_contract",
}
SOURCE_READING_OPERATIONS = ("check", "verify", "examples", "evaluate")


def _published_shape() -> dict:
    result = discover().get("result") or {}
    shape = result.get("contract_report")
    assert isinstance(shape, dict), (
        f"the manifest says nothing about the contract report: "
        f"{sorted(result)}. A client reads which answers carry the report "
        "and what it holds from the tool, not from an example."
    )
    return shape


def test_the_manifest_says_what_the_report_holds_and_which_answer_carries_it():
    """Given the manifest, then it names the operations whose answer
    carries the report, the 3 fields of an entry, the strengths and the
    fields of the totals."""
    shape = _published_shape()

    assert set(shape) == SHAPE_KEYS, (
        f"the published shape holds {sorted(shape)}, expected "
        f"{sorted(SHAPE_KEYS)}: a client that cannot read every part of the "
        "report from the manifest has to guess one."
    )
    assert isinstance(shape["carried_by"], list) and shape["carried_by"], (
        f"the manifest names no operation carrying the report: "
        f"{shape['carried_by']!r}."
    )
    assert set(shape["entry_fields"]) == {
        "function",
        "precondition",
        "postcondition",
    }, f"an entry's published fields are {sorted(shape['entry_fields'])}."
    assert set(shape["strengths"]) == {"omitted", "trivial", "stated"}, (
        f"the published strengths are {sorted(shape['strengths'])}: a block "
        "is absent, written as the literal true, or says something, and the "
        "manifest names each of the three."
    )


def test_every_answer_carries_the_report_exactly_where_the_manifest_says():
    """Given the 4 operations that read a program, when each is asked
    about the same function with a real contract, then it carries the
    report if and only if the manifest lists it."""
    carried_by = set(_published_shape()["carried_by"])

    for operation in SOURCE_READING_OPERATIONS:
        answer = ask(operation, REAL_CONTRACT)
        carries = "contract_report" in answer
        assert carries == (operation in carried_by), (
            f"the answer of {operation!r} "
            f"{'carries' if carries else 'carries no'} contract report, and "
            f"the manifest lists {sorted(carried_by)}. The published list "
            "and the answers are two readings of one decision and must "
            "agree."
        )


def test_every_word_and_field_the_report_uses_is_one_the_manifest_publishes():
    """Given 5 programs and the shipped hour clock, when each is checked,
    then every entry field, every totals field and every strength word in
    the answer appears in the published shape."""
    shape = _published_shape()

    for source in EVERY_SOURCE + (hour_clock_source(),):
        report = report_of(check(source))
        assert set(report) == {"functions", "totals", "states_a_contract", "note"}, (
            f"the report holds {sorted(report)} for a program the manifest "
            "describes with its published shape."
        )
        assert set(report["totals"]) == set(shape["totals_fields"]), (
            f"the totals hold {sorted(report['totals'])} and the manifest "
            f"publishes {sorted(shape['totals_fields'])}."
        )
        for name, entry in entries_by_function(report).items():
            assert set(entry) == set(shape["entry_fields"]), (
                f"the entry for {name!r} holds {sorted(entry)} and the "
                f"manifest publishes {sorted(shape['entry_fields'])}."
            )
            for block in ("precondition", "postcondition"):
                assert entry[block] in shape["strengths"], (
                    f"the entry for {name!r} records its {block} as "
                    f"{entry[block]!r}, which the manifest does not publish: "
                    f"{sorted(shape['strengths'])}. A word a client cannot "
                    "look up tells it nothing."
                )
