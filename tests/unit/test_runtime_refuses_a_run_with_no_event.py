"""Driving a machine through no event at all is a mistake of the caller,
not an answer about a machine.

The request reader refuses an empty `events` field by name, so no
request reaches the runtime with none. That is the reader's rule, in
another module; this one is the runtime's own, so a second caller added
later cannot drive an empty sequence and read the state it was handed
back as a machine that moved.
"""

from __future__ import annotations

import types

import pytest

from prova import runtime


def _a_program_declaring_nothing() -> object:
    """A program whose functions are never reached: the machine below
    refuses to name one first."""
    return types.SimpleNamespace(functions={})


class _NothingIsAsked:
    """A machine nothing is asked of: the refusal must be decided before
    any role is run, so every call here is a defect of the code under
    test and says so."""

    def named_for(self, role):
        raise AssertionError(
            f"WHAT: the role {role!r} was asked for while driving no event. "
            "WHY: a run with no event is refused before any role is read. "
            "HOW: refuse the empty sequence first."
        )

    @property
    def assumptions(self):
        raise AssertionError(
            "WHAT: the assumptions were read while driving no event. "
            "WHY: a run with no event publishes nothing. "
            "HOW: refuse the empty sequence first."
        )


def test_a_run_with_no_event_is_refused_before_any_role_is_read():
    driver = runtime.MachineRuntime.of(_NothingIsAsked(), _a_program_declaring_nothing())

    with pytest.raises(ValueError) as refused:
        driver.driven("any state", ())

    said = str(refused.value)
    for part in ("WHAT:", "WHY:", "HOW:"):
        assert part in said, (
            f"WHAT: the refusal reads {said!r} and does not say {part!r}. "
            "WHY: every refusal of this tool says what failed, why it is a "
            "rule and how to repair it, and this one is read by whoever "
            "added the caller. HOW: write the three parts."
        )
    assert "events" in said, (
        f"WHAT: the refusal reads {said!r} and does not name what was empty. "
        "WHY: the caller must be sent to the sequence it passed. "
        "HOW: name it."
    )


def test_one_event_is_enough_to_be_driven():
    """The refusal is about the empty sequence and nothing else: a
    sequence of one is read past the guard, which is observed here by the
    machine above refusing to answer the first role it is asked for."""
    driver = runtime.MachineRuntime.of(_NothingIsAsked(), _a_program_declaring_nothing())

    with pytest.raises(AssertionError) as asked:
        driver.driven("any state", ("any event",))

    assert "invariant" in str(asked.value), (
        f"WHAT: driving one event asked for {str(asked.value)!r}. "
        "WHY: a sequence of one is driven, and the first thing a run reads "
        "is the invariant role; a ValueError here would mean the guard "
        "refuses more than the empty sequence. HOW: guard the empty "
        "sequence alone."
    )
