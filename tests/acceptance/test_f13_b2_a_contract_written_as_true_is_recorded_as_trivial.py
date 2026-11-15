"""F13.B2 -- a block written as the literal `true` is recorded as
trivial.

A contract that is present but says `true` promises exactly as much as no
contract at all, and the Owner sees that without opening the source.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the report called a written block trivial whatever it
said. The second test reads the same field for a block that states a real
relation and asserts it differs; a third asserts trivial and omitted are
told apart.
"""

from __future__ import annotations

from _f13_contract_fixtures import (
    NO_PRECONDITION,
    REAL_CONTRACT,
    TRIVIAL_POSTCONDITION,
    check,
    entries_by_function,
    report_of,
)


def test_a_postcondition_written_as_true_is_recorded_as_trivial():
    """Given a function `twice` whose `ensures` is literally `true`, when
    the program is checked, then the report records its postcondition as
    `trivial`."""
    answer = check(TRIVIAL_POSTCONDITION)

    entry = entries_by_function(report_of(answer))["twice"]

    assert entry.get("postcondition") == "trivial", (
        f"the report records the postcondition of 'twice' as "
        f"{entry.get('postcondition')!r}, expected 'trivial': that function "
        "writes (ensures true), which promises nothing about its result. A "
        "block whose every clause is the literal true is recorded as "
        "trivial."
    )


def test_a_postcondition_that_states_a_relation_is_not_recorded_as_trivial():
    """Given a function `twice` whose `ensures` relates `result` to `n`,
    when the program is checked, then its postcondition is not recorded as
    `trivial`."""
    answer = check(REAL_CONTRACT)

    entry = entries_by_function(report_of(answer))["twice"]

    assert entry.get("postcondition") != "trivial", (
        "the report records '(ensures (= result (* n 2)))' as 'trivial', so "
        "a real promise reads like one that says nothing. Record a block "
        "with a clause that is not the literal true as stated."
    )


def test_a_block_written_as_true_reads_differently_from_a_block_never_written():
    """Given one function writing `(ensures true)` and one writing no
    `requires` at all, when both are checked, then the report tells the two
    apart."""
    written = entries_by_function(report_of(check(TRIVIAL_POSTCONDITION)))["twice"]
    absent = entries_by_function(report_of(check(NO_PRECONDITION)))["twice"]

    assert written.get("postcondition") != absent.get("precondition"), (
        "a block written as the literal true and a block the program never "
        "writes are recorded with the same word "
        f"{written.get('postcondition')!r}, so the Owner cannot tell a "
        "contract somebody wrote and emptied from one nobody wrote. SPEC.md "
        "asks the report to identify omitted and explicitly trivial "
        "contracts as two things."
    )
