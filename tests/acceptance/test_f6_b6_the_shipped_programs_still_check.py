"""Acceptance test for F6 criterion 7: the programs this repository ships
-- the hour clock, the reservation example and the conformance program --
still check after the spelling rules arrive.

Every name and marker in them is spelled the way the language defines it,
so a rule that refused any of them would be refusing a valid program.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool accepted every program. The refusals in
test_f6_b1..b5 observe that the same operation refuses misspelled
programs, so a tool that accepts everything fails there.
"""

from __future__ import annotations

from _f6_spelling_fixtures import assert_accepted, check, shipped_source
from _reservation_fixtures import reservation_source


def test_the_shipped_hour_clock_still_checks():
    """Given the hour clock this repository ships, when it is checked,
    then it is valid and carries no diagnostic."""
    assert_accepted(
        check(shipped_source("examples/hour-clock.prova")),
        "the shipped hour clock at examples/hour-clock.prova",
    )


def test_the_reservation_example_still_checks():
    """Given the reservation example, when it is checked, then it is
    valid and carries no diagnostic."""
    assert_accepted(check(reservation_source()), "the reservation example")


def test_the_shipped_conformance_program_still_checks():
    """Given the conformance program `add-one`, when it is checked, then
    it is valid and carries no diagnostic."""
    assert_accepted(
        check(shipped_source("conformance/add-one.prova")),
        "the shipped conformance program at conformance/add-one.prova",
    )
