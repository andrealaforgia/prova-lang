"""Acceptance test for F2 criterion 6: the hour clock and the reservation
example still pass when they are checked.

Both call other functions from their bodies and from their contracts, so
they are the programs a cycle rule is most likely to refuse by mistake.
Each test also checks one copy of the same program with a cycle injected
into it, so "still accepted" is distinguishable from "accepted whatever
the program does". The copies live in memory only; SPEC.md and
examples/hour-clock.prova are read, never written.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

from _f2_cycle_fixtures import (
    HOUR_CLOCK_GUARD,
    RESERVATION_GUARD,
    accepted,
    check,
    hour_clock_source,
    reported_cycles,
    reservation_source,
    with_a_self_calling_guard,
)


def test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself():
    """Given the shipped hour clock, when it is checked, then it is
    accepted; a copy whose `valid-state` guard is replaced by a call to
    `valid-state` is refused."""
    shipped = hour_clock_source()
    cyclic_copy = with_a_self_calling_guard(shipped, HOUR_CLOCK_GUARD)

    assert accepted(check(shipped)), (
        f"the shipped hour clock was refused: {check(shipped).response()}. Its "
        "calls are acyclic -- `step` and `initial` call `valid-state`, which calls "
        "nothing -- so it must stay accepted."
    )
    refused = check(cyclic_copy).response()
    assert refused.get("status") == "invalid_program", (
        f"an hour clock whose `valid-state` calls itself was accepted: {refused}. "
        "The check must actually run on this program, not skip it."
    )
    assert reported_cycles(refused) == [frozenset({"valid-state"})], (
        f"the refusal does not name `valid-state` as the cycle: {refused}."
    )


def test_the_reservation_example_still_passes_unlike_a_copy_whose_guard_calls_itself():
    """Given the reservation example SPEC.md publishes, when it is
    checked, then it is accepted; a copy whose `valid-state` guard is
    replaced by a call to `valid-state` is refused."""
    shipped = reservation_source()
    cyclic_copy = with_a_self_calling_guard(shipped, RESERVATION_GUARD)

    assert accepted(check(shipped)), (
        f"the reservation example was refused: {check(shipped).response()}. Its "
        "calls are acyclic -- `step`'s contract calls `valid-state`, which calls "
        "nothing -- so it must stay accepted."
    )
    refused = check(cyclic_copy).response()
    assert refused.get("status") == "invalid_program", (
        f"a reservation example whose `valid-state` calls itself was accepted: "
        f"{refused}. The check must actually run on this program, not skip it."
    )
    assert reported_cycles(refused) == [frozenset({"valid-state"})], (
        f"the refusal does not name `valid-state` as the cycle: {refused}."
    )
