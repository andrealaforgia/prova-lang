"""F27 criteria 2 and 3 -- an event the machine does not admit is
answered as a boundary rejection with the state unchanged, and the Owner
reads it as something different from an event the machine admits whose
business result is a rejection.

The law: a boundary rejection runs no transition and changes no state,
and it is published under a different word from the admitted event whose
outcome says the business rejected it.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the two rejections were published under the same word
and told apart only by the presence of the outcome -- both the word and
the outcome are asserted, and the two answers are compared against each
other in the last test here.
"""

from __future__ import annotations

import _f27_runtime_fixtures as machines

# The same component at the same state, sent the same event, under the
# two admissibility predicates: the shipped one admits every typed event,
# and the narrower one admits what the component's own guards accept.
THE_STATE_AT_CAPACITY = "(Reservation 2)"
ONE_MORE_RESERVE = ["(Reserve)"]


def _outside_the_domain() -> dict:
    source, descriptor = machines.reservation_that_admits_less()
    return machines.drive(source, descriptor, THE_STATE_AT_CAPACITY, ONE_MORE_RESERVE)


def _rejected_by_the_business() -> dict:
    source, descriptor = machines.shipped_machine("reservation")
    return machines.drive(source, descriptor, THE_STATE_AT_CAPACITY, ONE_MORE_RESERVE)


def test_an_inadmissible_reserve_is_a_boundary_rejection_and_runs_nothing():
    """Given a reservation component full at 2 units whose admissibility
    predicate refuses a reserve there, when the Owner sends one reserve,
    then the answer is a boundary rejection naming position 1, and no
    outcome was published."""
    answer = _outside_the_domain()

    assert answer.get("status") == "completed", (
        f"WHAT: an event outside the admissible domain was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: the runtime did its work: it read the admissibility "
        "predicate and refused the event at the boundary, which is an "
        "answer about the machine and not a request the tool could not "
        "read. HOW: answer the boundary rejection as the result it is."
    )
    ran = machines.transitions_of(answer)
    assert len(ran) == 1, (
        f"WHAT: the answer reports {len(ran)} entries for the 1 event "
        f"sent: {ran}. "
        "WHY: the Owner reads which event was refused. "
        "HOW: report the event that met the boundary."
    )
    assert ran[0].get("result") == machines.A_BOUNDARY_REJECTION, (
        f"WHAT: the inadmissible reserve was published as "
        f"{ran[0].get('result')!r}, not "
        f"{machines.A_BOUNDARY_REJECTION!r}: {ran[0]}. "
        "WHY: criterion 2 promises an explicit boundary rejection for an "
        "event outside the admissible domain. "
        "HOW: publish it under that word."
    )
    assert "outcome" not in ran[0], (
        f"WHAT: the boundary rejection carries an outcome: {ran[0]}. "
        "WHY: the step was never run, so there is no outcome to publish; "
        "one there would read as a result the machine answered. "
        "HOW: publish no outcome for an event the machine does not admit."
    )
    stopped = machines.stopped_at_of(answer) or {}
    assert stopped.get("position") == 1, (
        f"WHAT: the answer says the run stopped at {stopped!r}, and the "
        "event refused was the first one sent. "
        "WHY: the Owner is promised the position of the event that stopped "
        "the run. HOW: name the position of the refused event."
    )
    assert stopped.get("reason") == machines.A_BOUNDARY_REJECTION, (
        f"WHAT: the stop says its reason is {stopped.get('reason')!r}: "
        f"{stopped}. "
        "WHY: a run stops for one of the reasons the manifest publishes, "
        "and the Owner reads which. HOW: name the reason."
    )


def test_an_inadmissible_reserve_leaves_the_state_exactly_as_it_was():
    """Given the same component full at 2 units, when the reserve outside
    the admissible domain is refused, then the state published is
    '(Reservation 2)', the state it was sent."""
    answer = _outside_the_domain()

    ran = machines.transitions_of(answer)
    assert ran[0].get("state_before") == THE_STATE_AT_CAPACITY, (
        f"WHAT: the entry says the state before the refused event was "
        f"{ran[0].get('state_before')!r}, and the Owner sent "
        f"{THE_STATE_AT_CAPACITY!r}. "
        "WHY: the Owner reads the refusal against the state they sent. "
        "HOW: carry that state."
    )
    assert ran[0].get("state_after") == THE_STATE_AT_CAPACITY, (
        f"WHAT: the state after the refused event is "
        f"{ran[0].get('state_after')!r}, and the state before it was "
        f"{THE_STATE_AT_CAPACITY!r}. "
        "WHY: criterion 2 promises the state is unchanged by an event "
        "outside the admissible domain. "
        "HOW: publish the state the run came in with."
    )
    assert machines.state_now_of(answer) == THE_STATE_AT_CAPACITY, (
        f"WHAT: after the refusal the answer says the component holds "
        f"{machines.state_now_of(answer)!r}, and nothing ran. "
        "WHY: the Owner drives the next event from the state this answer "
        "published, and a changed state there would move a machine no "
        "transition moved. HOW: publish the unchanged state."
    )


def test_the_business_rejection_and_the_boundary_rejection_read_differently():
    """Given the same component full at 2 units sent the same reserve,
    when its admissibility predicate admits the event and the business
    rejects it, then the answer is a transition carrying the outcome
    '(Outcome (Reservation 2) false)' -- and the two answers differ in
    the word they publish and in the outcome they carry."""
    at_the_boundary = _outside_the_domain()
    by_the_business = _rejected_by_the_business()

    admitted = machines.transitions_of(by_the_business)[0]
    refused = machines.transitions_of(at_the_boundary)[0]
    assert admitted.get("result") == machines.A_TRANSITION, (
        f"WHAT: the admitted reserve the business rejected was published "
        f"as {admitted.get('result')!r}: {admitted}. "
        "WHY: criterion 3 promises it is a normal answer. "
        "HOW: publish it as a transition."
    )
    assert admitted.get("outcome") == "(Outcome (Reservation 2) false)", (
        f"WHAT: the admitted reserve published the outcome "
        f"{admitted.get('outcome')!r}, and the component's step answers "
        f"'(Outcome (Reservation 2) false)' when it is full: {admitted}. "
        "WHY: the business rejection is in the outcome the machine "
        "answered, which is the thing the Owner reads it from. "
        "HOW: publish the outcome whole."
    )
    assert admitted.get("result") != refused.get("result"), (
        f"WHAT: the business rejection and the boundary rejection are both "
        f"published as {admitted.get('result')!r}. "
        "WHY: criterion 3 promises the two are distinguishable: one is the "
        "machine's own result at an event it admits, the other is the "
        "runtime refusing to run the step at all. "
        "HOW: publish the two under different words."
    )
    assert ("outcome" in admitted) and ("outcome" not in refused), (
        f"WHAT: the business rejection carries "
        f"{admitted.get('outcome')!r} and the boundary rejection carries "
        f"{refused.get('outcome')!r}. "
        "WHY: an answer where both carry an outcome, or neither does, "
        "leaves the Owner unable to tell a result of the machine from the "
        "runtime refusing to ask it. "
        "HOW: carry an outcome for an admitted event alone."
    )
    assert machines.state_now_of(by_the_business) == machines.state_now_of(
        at_the_boundary
    ), (
        f"WHAT: the two answers published the states "
        f"{machines.state_now_of(by_the_business)!r} and "
        f"{machines.state_now_of(at_the_boundary)!r}. "
        "WHY: this component rejects without changing state, so both leave "
        "it at 2 units: the difference between the two answers is what was "
        "run, not where the component stands. "
        "HOW: publish the state each run reached."
    )
