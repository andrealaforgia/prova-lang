"""F13.B3 -- a function with a real contract is recorded as neither
omitted nor trivial, and the shipped hour clock reads the way a human
reads it.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the report recorded a word nobody can count. The last
test asserts the totals count every block of every declared function and
sum back to that population.
"""

from __future__ import annotations

from _f13_contract_fixtures import (
    CLOCK_CONTRACTS,
    REAL_CONTRACT,
    check,
    entries_by_function,
    hour_clock_source,
    report_of,
)

PROMISES_NOTHING_WORDS = ("omitted", "trivial")


def test_a_function_with_a_real_contract_is_recorded_as_neither():
    """Given a function `twice` with `(requires (> n 0))` and
    `(ensures (= result (* n 2)))`, when the program is checked, then
    neither block is recorded as omitted or trivial."""
    entry = entries_by_function(report_of(check(REAL_CONTRACT)))["twice"]

    for block in ("precondition", "postcondition"):
        assert entry.get(block) not in PROMISES_NOTHING_WORDS, (
            f"the report records the {block} of 'twice' as "
            f"{entry.get(block)!r}, although that function states a real "
            "clause there. A block that promises something must read as "
            "neither omitted nor trivial, or a meaningful contract is "
            "reported as an empty one."
        )


def test_the_shipped_hour_clock_reads_the_way_a_human_reads_it():
    """Given the hour clock this repository ships, when it is checked,
    then each of its 3 functions is recorded with the two strengths a
    reader of the source writes down by hand."""
    report = report_of(check(hour_clock_source()))
    entries = entries_by_function(report)

    assert set(entries) == set(CLOCK_CONTRACTS), (
        f"the report names {sorted(entries)}, and the shipped hour clock "
        f"declares {sorted(CLOCK_CONTRACTS)}. Every declared function is "
        "recorded exactly once."
    )
    for name, (precondition, postcondition) in CLOCK_CONTRACTS.items():
        assert (
            entries[name].get("precondition"),
            entries[name].get("postcondition"),
        ) == (precondition, postcondition), (
            f"the report records {name!r} as "
            f"{entries[name].get('precondition')!r}/"
            f"{entries[name].get('postcondition')!r}, and its source writes "
            f"{precondition}/{postcondition}. The report is read instead of "
            "the source, so the two must agree."
        )


def test_the_totals_count_every_block_of_every_declared_function():
    """Given the hour clock's 3 functions, when it is checked, then the
    totals count 6 contract blocks and the three strengths sum back to
    that 6."""
    report = report_of(check(hour_clock_source()))
    totals = report.get("totals") or {}
    entries = entries_by_function(report)

    expected_functions = len(CLOCK_CONTRACTS)
    expected_blocks = 2 * expected_functions
    assert totals.get("functions") == expected_functions == len(entries), (
        f"the totals count {totals.get('functions')!r} functions, the report "
        f"lists {len(entries)} and the shipped clock declares "
        f"{expected_functions}. A count that does not name its population "
        "cannot be read."
    )
    assert totals.get("contracts") == expected_blocks, (
        f"the totals count {totals.get('contracts')!r} contract blocks; each "
        f"of the {expected_functions} functions has a precondition and a "
        f"postcondition, so there are {expected_blocks}."
    )
    parts = {word: totals.get(word) for word in ("omitted", "trivial", "stated")}
    assert sum(value or 0 for value in parts.values()) == expected_blocks, (
        f"the strengths {parts} do not sum to the {expected_blocks} blocks "
        "the program has: a block is omitted, trivial or stated and nothing "
        "else, so the parts must sum back to the whole."
    )
    counted = {word: 0 for word in parts}
    for entry in entries.values():
        for block in ("precondition", "postcondition"):
            counted[entry.get(block)] = counted.get(entry.get(block), 0) + 1
    assert parts == counted, (
        f"the totals say {parts} and the listed entries say {counted}: the "
        "summary and the list are two readings of one program and must "
        "agree."
    )
