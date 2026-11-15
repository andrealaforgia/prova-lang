"""F18.1 and F18.2 -- the Owner asks what the hour clock and the
reservation example owe, and is told that every one of those obligations
is owed no longer.

The expected list is written out here by hand, read off the two programs
and the rule SPEC.md states under "Verification obligations and the
initial fragment": every function owes that its contract is defined, that
its body answers its postcondition, and that it ends because the calls it
reaches are acyclic; every declared example owes that it is a valid
example of its own function; every call under the condition that reaches
it owes the precondition of what it calls. Nothing here is taken from
what the tool answers.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered 'proved' for everything whatever the
program says. The last test in this file sends the same clock with the
wrap at 12 taken out of what `step` does -- a program whose promise is
then false at hour 12 -- and requires that one not to come back proved.
"""

from __future__ import annotations

from _f18_fixtures import (
    WAYS_OF_DISCHARGING,
    completed,
    entry_named,
    not_proved,
    obligations_of,
    results_by_identity,
    totals_of,
    verify,
)
from _hour_clock_fixtures import clock_without_the_wrap, shipped_clock_source
from _reservation_fixtures import reservation_source

# The 20 obligations the shipped hour clock owes. `valid-state` promises
# nothing and calls nothing, so it owes its contract, its body, its 4
# declared examples and its ending; `initial` promises that what it
# answers is a valid state, which calls `valid-state` from its
# postcondition; `step` asks for a valid state and promises three things
# about its outcome, calling `valid-state` once in what it asks for and
# once in what it promises.
THE_HOUR_CLOCK_OWES = {
    "contract_definedness:valid-state:contract",
    "body_postcondition:valid-state:body",
    "example_validity:valid-state:example[0]",
    "example_validity:valid-state:example[1]",
    "example_validity:valid-state:example[2]",
    "example_validity:valid-state:example[3]",
    "structural_termination:valid-state:calls",
    "contract_definedness:initial:contract",
    "call_precondition:initial:ensures[0]",
    "body_postcondition:initial:body",
    "example_validity:initial:example[0]",
    "structural_termination:initial:calls",
    "contract_definedness:step:contract",
    "call_precondition:step:requires[0]",
    "call_precondition:step:ensures[0]",
    "body_postcondition:step:body",
    "example_validity:step:example[0]",
    "example_validity:step:example[1]",
    "example_validity:step:example[2]",
    "structural_termination:step:calls",
}

# The 18 the reservation example of SPEC.md owes, read off it the same
# way: `valid-state` with 2 examples, `initial` promising the empty
# reservation with 1, and `step` asking for a valid state, promising
# three things and declaring 4 examples.
THE_RESERVATION_OWES = {
    "contract_definedness:valid-state:contract",
    "body_postcondition:valid-state:body",
    "example_validity:valid-state:example[0]",
    "example_validity:valid-state:example[1]",
    "structural_termination:valid-state:calls",
    "contract_definedness:initial:contract",
    "body_postcondition:initial:body",
    "example_validity:initial:example[0]",
    "structural_termination:initial:calls",
    "contract_definedness:step:contract",
    "call_precondition:step:requires[0]",
    "call_precondition:step:ensures[0]",
    "body_postcondition:step:body",
    "example_validity:step:example[0]",
    "example_validity:step:example[1]",
    "example_validity:step:example[2]",
    "example_validity:step:example[3]",
    "structural_termination:step:calls",
}

# What `step` of the reservation example asks for, and where the answer
# reports it: the entry state must be a valid one, so what `step`
# promises is promised only of such a state and every declared example
# starts from one.
THE_STEP_PRECONDITION = "call_precondition:step:requires[0]"
WHAT_STEP_PROMISES_UNDER_IT = "call_precondition:step:ensures[0]"
THE_STATE_IT_ASKS_FOR = "(valid-state current)"


def _all_proved(label: str, source: str, owed: set) -> dict:
    answer = completed(verify(source), label)
    entries = obligations_of(answer, label)

    assert {entry["id"] for entry in entries} == owed, (
        f"WHAT: {label} is answered about "
        f"{sorted({entry['id'] for entry in entries})} and owes {sorted(owed)}. "
        "WHY: an obligation that is not listed is one nobody was told about, "
        "and one listed that is not owed is work reported on a program that "
        "does not owe it. "
        f"HOW: compare the answer with the program: {answer}"
    )
    assert not not_proved(answer, label), (
        f"WHAT: {label} has obligations that did not come back proved: "
        f"{not_proved(answer, label)}. "
        "WHY: the Owner runs this to learn that each of them is owed no "
        "longer; one left unsettled is a promise of this program that still "
        "stands unshown. "
        f"HOW: inspect the answer: {answer}"
    )

    unfinished = [
        (entry["id"], entry.get("execution_status"))
        for entry in entries
        if entry.get("execution_status") != "completed"
    ]
    assert not unfinished, (
        f"WHAT: {label} reports {unfinished} beside obligations it calls "
        "proved. "
        "WHY: SPEC.md lines 275-277 allow only a completed justified result "
        "to be proved; an interrupted or unsupported attempt is unknown. "
        f"HOW: inspect the answer: {answer}"
    )

    unsaid = [
        (entry["id"], entry.get("discharged_by"))
        for entry in entries
        if entry.get("discharged_by") not in WAYS_OF_DISCHARGING
    ]
    assert not unsaid, (
        f"WHAT: {label} does not say what settled {unsaid}. "
        "WHY: SPEC.md asks the inventory to identify structurally discharged "
        f"checks as well as solver checks, so each entry says which of "
        f"{list(WAYS_OF_DISCHARGING)} settled it. "
        f"HOW: inspect the answer: {answer}"
    )

    totals = totals_of(answer)
    assert totals.get("obligations") == len(entries), (
        f"WHAT: {label} reports {totals.get('obligations')} obligations while "
        f"listing {len(entries)}. "
        "WHY: a count that does not name the list it counts tells the Owner "
        "nothing about this program. "
        f"HOW: inspect the totals: {totals}"
    )
    assert totals.get("attempted") == len(entries), (
        f"WHAT: {label} lists {len(entries)} obligations and reports "
        f"{totals.get('attempted')} attempted. "
        "WHY: nothing may be silently skipped: every obligation of this "
        "program was tried, so the count of what was tried is the whole list. "
        f"HOW: inspect the totals: {totals}"
    )
    assert totals.get("not_attempted") == 0, (
        f"WHAT: {label} reports {totals.get('not_attempted')} obligations "
        "nothing attempted. "
        "WHY: an obligation nobody tried is one the Owner is still owed, and "
        "this program is answered about all of them. "
        f"HOW: inspect the totals: {totals}"
    )
    assert (totals.get("by_result") or {}).get("proved") == len(entries), (
        f"WHAT: {label} counts {totals.get('by_result')} by result while "
        f"listing {len(entries)} obligations. "
        "WHY: the counts must partition the list, so the Owner reading the "
        "summary alone reads the same verdict as the Owner reading every "
        "entry. "
        f"HOW: inspect the totals: {totals}"
    )
    return answer


def test_every_obligation_of_the_hour_clock_comes_back_proved():
    """Given the hour clock this repository ships, when the Owner asks
    what it owes, then all 20 obligations come back proved, each one
    settled and none of them skipped."""
    _all_proved("the hour clock", shipped_clock_source(), THE_HOUR_CLOCK_OWES)


def test_every_obligation_of_the_reservation_example_comes_back_proved():
    """Given the reservation example of SPEC.md, when the Owner asks what
    it owes, then all 18 obligations come back proved, including the one
    about the state `step` asks for."""
    answer = _all_proved(
        "the reservation example", reservation_source(), THE_RESERVATION_OWES
    )

    asked_for = entry_named(answer, THE_STEP_PRECONDITION, "the reservation example")
    promised = entry_named(
        answer, WHAT_STEP_PROMISES_UNDER_IT, "the reservation example"
    )

    assert asked_for["result"] == "proved", (
        f"WHAT: what `step` asks for is answered {asked_for['result']!r}. "
        "WHY: SPEC.md says of this example that the step precondition still "
        "needs proof; the Owner runs this to see it settled. "
        f"HOW: inspect the entry: {asked_for}"
    )
    assert promised["path_condition"] == THE_STATE_IT_ASKS_FOR, (
        f"WHAT: what `step` promises is answered under "
        f"{promised.get('path_condition')!r} and `step` asks for "
        f"{THE_STATE_IT_ASKS_FOR!r}. "
        "WHY: what a function promises is promised only of the inputs it asks "
        "for; an obligation that forgot the condition reaching it would be "
        "shown about inputs this program never accepts. "
        f"HOW: inspect the entry: {promised}"
    )


def test_the_same_clock_without_its_wrap_at_12_is_not_proved():
    """Given the hour clock with the wrap at 12 taken out of what `step`
    does and its promise left as shipped, when the Owner asks what it
    owes, then what `step` does is not answered proved, while the rest of
    the program still is."""
    label = "the hour clock without its wrap"
    broken = clock_without_the_wrap(shipped_clock_source())
    answer = completed(verify(broken), label)
    stood = results_by_identity(answer, label)

    assert stood.get("body_postcondition:step:body") != "proved", (
        "WHAT: a clock that counts past 12 is answered "
        f"{stood.get('body_postcondition:step:body')!r} about what `step` "
        "does. "
        "WHY: at hour 12 that program answers hour 13, which its own promise "
        "forbids; an answer of proved here would be the worst defect this "
        "tool can have. "
        f"HOW: inspect the answer: {answer}"
    )

    still_proved = [
        identity
        for identity, stands in stood.items()
        if identity != "body_postcondition:step:body" and stands == "proved"
    ]
    assert len(still_proved) >= 15, (
        f"WHAT: only {len(still_proved)} of the other obligations of the "
        "broken clock are still proved. "
        "WHY: one false promise taints one obligation, not the program: a "
        "tool that gave up on all of them would pass the test above while "
        "proving nothing at all. "
        f"HOW: inspect the answer: {answer}"
    )
