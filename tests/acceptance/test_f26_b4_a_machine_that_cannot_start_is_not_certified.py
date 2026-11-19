"""F26 criterion 6 -- the Owner's machine cannot start: its initialiser
answers a state the invariant does not admit, or its invariant is a
condition no state satisfies at all. Neither machine is certified.

The law: a machine is certified only with an initial state its invariant
admits; an inconsistent initial condition never silently certifies a
useful machine (SPEC.md lines 406-407), not even when every other
obligation of it is proved.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool certified nothing at all. test_f26_b1 requires
both shipped machines verified, so a tool that withholds the word
everywhere fails there.
"""

from __future__ import annotations

import _f26_induction_fixtures as induction


def test_an_initialiser_that_starts_outside_the_invariant_is_not_certified():
    """Given an hour clock whose initialiser answers the state 0 while
    its invariant admits 1 to 12, and whose every function keeps its own
    contract, when the Owner asks the tool to verify it with its
    descriptor, then initialisation is not proved and the whole is not
    verified."""
    source, descriptor = induction.THE_MACHINE_THAT_CANNOT_START

    answered = induction.ask_to_verify(source, descriptor)

    entry = induction.the_three_obligations(answered).get(induction.INITIALISATION)
    assert entry is not None, (
        f"WHAT: the answer lists no initialisation obligation: "
        f"{sorted(induction.the_three_obligations(answered))}. "
        "WHY: nothing else in this answer is about the state the machine "
        "starts in: every function of this program keeps its own contract. "
        "HOW: list the initialisation obligation."
    )
    assert entry.get("result") != induction.PROVED, (
        f"WHAT: a clock that starts at 0 under an invariant admitting 1 to "
        f"12 has initialisation {entry.get('result')!r}: {entry}. "
        "WHY: criterion 6 promises that a machine whose initial condition "
        "cannot hold is not certified; the state the initialiser answers is "
        "not one the invariant admits. HOW: withhold the word and say why."
    )
    aggregate = induction.aggregate_of(answered)
    assert aggregate.get("result") == induction.NOT_VERIFIED, (
        f"WHAT: the machine stands as {aggregate.get('result')!r}: "
        f"{aggregate}. "
        "WHY: a machine with no initial state to reason from is not one the "
        "Owner may act on. HOW: account for initialisation in that word."
    )


def test_an_invariant_no_state_satisfies_is_not_certified_either():
    """Given a clock whose invariant asks the dial to be at least 1 and
    at most 0, so that no state satisfies it and preservation holds for
    want of any state to step from, when the Owner asks the tool to
    verify it with its descriptor, then initialisation is not proved and
    the whole is not verified."""
    source, descriptor = induction.THE_MACHINE_NO_STATE_SATISFIES

    answered = induction.ask_to_verify(source, descriptor)

    standing = induction.how_the_three_stand(answered)
    assert standing.get(induction.INITIALISATION) != induction.PROVED, (
        f"WHAT: the three obligations of a machine whose invariant no state "
        f"satisfies stand as {standing}. "
        "WHY: SPEC.md lines 406-407 say an inconsistent initial condition "
        "must not silently certify a useful machine; preservation of a "
        "condition nothing satisfies is true for an empty reason, and "
        "initialisation is the obligation that catches it. "
        "HOW: withhold initialisation and say why."
    )
    aggregate = induction.aggregate_of(answered)
    assert aggregate.get("result") == induction.NOT_VERIFIED, (
        f"WHAT: a machine whose invariant no state satisfies stands as "
        f"{aggregate.get('result')!r}: {aggregate}. "
        "WHY: a certified machine is one the Owner may act on, and this one "
        "has no state at all. HOW: withhold the word over the whole."
    )
