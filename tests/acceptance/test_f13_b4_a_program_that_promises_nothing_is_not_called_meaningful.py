"""F13.B4 -- when every contract of a program is omitted or trivial,
nothing in the answer describes that program as meaningfully correct.

A clean answer about a program that promises nothing says only that the
rules of the profile were kept over its text.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the scan could never fire. The last test runs the same
scan over a sentence that does describe a program that way and asserts it
fires there.
"""

from __future__ import annotations

from _f13_contract_fixtures import (
    NO_FUNCTION_AT_ALL,
    PROMISES_NOTHING,
    REAL_CONTRACT,
    check,
    claim_words_in,
    entries_by_function,
    report_of,
)


def test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct():
    """Given two functions whose 4 blocks are omitted or literally `true`,
    when the program is checked, then the report says the program states
    no contract, and no word of the whole answer describes it as
    meaningfully correct."""
    answer = check(PROMISES_NOTHING)
    report = report_of(answer)
    entries = entries_by_function(report)

    assert set(entries) == {"twice", "thrice"}, (
        f"the report names {sorted(entries)}, and the program declares "
        "'twice' and 'thrice'."
    )
    for name, entry in entries.items():
        for block in ("precondition", "postcondition"):
            assert entry.get(block) in ("omitted", "trivial"), (
                f"the report records the {block} of {name!r} as "
                f"{entry.get(block)!r}: every block in this program is "
                "absent or written as the literal true."
            )
    assert report.get("states_a_contract") is False, (
        f"the report says states_a_contract="
        f"{report.get('states_a_contract')!r} for a program whose every "
        "block is omitted or trivial. The Owner reads that one field to see "
        "that a clean answer about this program is not a meaningful one."
    )

    found = claim_words_in(answer)
    assert found == [], (
        f"the answer uses {sorted(set(found))} about a program whose every "
        "contract is omitted or trivial. Accepting a trivial claim must not "
        "be described as meaningful domain correctness (SPEC.md lines "
        "204-206); word the answer so it reports only that the rules of "
        "core-0 were kept over this text."
    )


def test_a_program_that_states_a_contract_is_told_apart_from_one_that_does_not():
    """Given a function with a real contract and a program with no
    function at all, when each is checked, then only the first is recorded
    as stating a contract."""
    stating = report_of(check(REAL_CONTRACT))
    empty = report_of(check(NO_FUNCTION_AT_ALL))

    assert stating.get("states_a_contract") is True, (
        "a function writing '(requires (> n 0))' and "
        "'(ensures (= result (* n 2)))' is reported as stating no contract, "
        "so the field reads the same for every program and tells the Owner "
        "nothing."
    )
    assert empty.get("states_a_contract") is False, (
        "a program declaring one type and no function is reported as "
        "stating a contract. A program with nothing to promise promises "
        "nothing."
    )
    assert entries_by_function(empty) == {}, (
        f"the report lists {entries_by_function(empty)} for a program that "
        "declares no function at all."
    )


def test_the_scan_fires_on_a_sentence_that_does_describe_a_program_that_way():
    """Given a hand-written answer that calls a program meaningfully
    correct, when the same scan reads it, then it reports that word."""
    pretend_answer = {
        "operation": "check",
        "status": "completed",
        "note": "this program is meaningfully correct and its contracts hold",
    }

    found = claim_words_in(pretend_answer)

    assert sorted(set(found)) == ["correct", "meaningfully"], (
        f"the scan read {found} from a sentence that plainly describes a "
        "program as meaningfully correct. A scan that cannot fire proves "
        "nothing about the answers it passes."
    )
