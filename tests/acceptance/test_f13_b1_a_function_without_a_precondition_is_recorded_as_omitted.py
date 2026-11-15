"""F13.B1 -- a function that demands nothing of its caller is recorded as
having an omitted precondition.

The Owner sees at a glance that `twice` places no demand on its input,
instead of reading the source to find a block that is not there.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the report called every precondition omitted. The second
test reads the same field for a function that does demand something, and
asserts the two differ.
"""

from __future__ import annotations

from _f13_contract_fixtures import (
    NO_PRECONDITION,
    REAL_CONTRACT,
    check,
    entries_by_function,
    report_of,
)


def test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted():
    """Given a function `twice` declaring no `requires`, when the program
    is checked, then the report records its precondition as `omitted`."""
    answer = check(NO_PRECONDITION)

    entry = entries_by_function(report_of(answer))["twice"]

    assert entry.get("precondition") == "omitted", (
        f"the report records the precondition of 'twice' as "
        f"{entry.get('precondition')!r}, expected 'omitted': that function "
        "declares no requires block, and a reader who cannot tell an "
        "absent demand from a stated one can mistake a clean answer for a "
        "meaningful one. Record a block the program does not declare as "
        "omitted."
    )


def test_a_demand_the_function_states_is_not_recorded_as_omitted():
    """Given a function `twice` declaring `(requires (> n 0))`, when the
    program is checked, then its precondition is not recorded as
    `omitted`."""
    answer = check(REAL_CONTRACT)

    entry = entries_by_function(report_of(answer))["twice"]

    assert entry.get("precondition") != "omitted", (
        "the report records a stated precondition '(> n 0)' as 'omitted', "
        "so every function reads the same whether or not it demands "
        "anything. Record a block the program declares with a clause that "
        "is not the literal true as stated."
    )
