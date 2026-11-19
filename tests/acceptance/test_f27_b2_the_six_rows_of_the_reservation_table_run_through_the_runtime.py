"""F27 criterion 1 against the table SPEC.md defines -- every row of the
reservation component's transition table, driven through the runtime,
answers the state and the acceptance result the document writes.

The law: for every row of that table, driving the shipped reservation
machine from the row's state with the row's event publishes the row's
state after it and the row's acceptance result, and nothing else.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the runtime published a correct state and an outcome
that disagreed with it -- the outcome is asserted whole, including the
acceptance flag the document writes; or the table shrank to a row that
happens to pass, which the count against the document's own rows
catches.
"""

from __future__ import annotations

import pytest

import _f27_runtime_fixtures as machines

THE_ROWS = machines.the_spec_table()


def test_the_document_defines_six_rows():
    """Given SPEC.md's reservation example, when its transition table is
    read, then it defines the 6 rows this test drives."""
    assert len(THE_ROWS) == 6, (
        f"WHAT: the transition table read from SPEC.md has {len(THE_ROWS)} "
        f"rows: {THE_ROWS}. "
        "WHY: the Owner is promised that the six rows of that table run "
        "through the runtime and match it exactly; a table read short would "
        "leave rows nothing was driven for. "
        "HOW: read the table in SPEC.md's core conformance example."
    )


@pytest.mark.parametrize("row", THE_ROWS, ids=lambda row: f"{row[0]}-{row[1]}")
def test_a_row_of_the_table_is_what_the_runtime_answers(row):
    """Given the shipped reservation machine at the state a row of
    SPEC.md's table writes, when the Owner sends that row's event, then
    the state after it and the acceptance result are the row's own."""
    before, event, after, accepted = row
    source, descriptor = machines.shipped_machine("reservation")

    answer = machines.drive(
        source, descriptor, f"(Reservation {before})", [f"({event})"]
    )

    assert answer.get("status") == "completed", (
        f"WHAT: the row {row} was answered {answer.get('status')!r}: "
        f"{answer}. "
        "WHY: every row of the table is a transition of the machine the "
        "document defines, so each of them is answered. "
        "HOW: read the refusals above."
    )
    ran = machines.transitions_of(answer)
    assert len(ran) == 1 and ran[0].get("result") == machines.A_TRANSITION, (
        f"WHAT: the row {row} ran {ran}. "
        "WHY: the table defines all transitions of this model, so every row "
        "is an event the machine admits and runs. "
        "HOW: publish one transition per row."
    )
    assert ran[0].get("state_after") == f"(Reservation {after})", (
        f"WHAT: the row {row} reached the state "
        f"{ran[0].get('state_after')!r}, and the document writes "
        f"'(Reservation {after})'. "
        "WHY: the runtime must answer the transitions the document defines; "
        "a state of its own would be a different machine. "
        "HOW: read SPEC.md's table against the answer above."
    )
    assert ran[0].get("outcome") == f"(Outcome (Reservation {after}) {accepted})", (
        f"WHAT: the row {row} published the outcome "
        f"{ran[0].get('outcome')!r}, and the document writes the state "
        f"{after} accepted {accepted}. "
        "WHY: the acceptance result is the component's observable answer: "
        "the document says 'reject everything' is incorrect even when safe, "
        "so the flag is read and not only the state. "
        "HOW: read SPEC.md's table against the answer above."
    )
    assert machines.state_now_of(answer) == f"(Reservation {after})", (
        f"WHAT: after the row {row} the answer says the component holds "
        f"{machines.state_now_of(answer)!r}, and the row writes "
        f"'(Reservation {after})'. "
        "WHY: the Owner drives the next event from that state. "
        "HOW: publish the state the transition published."
    )


def test_a_rejected_row_keeps_the_state_the_document_writes():
    """Given the two rows of the table whose acceptance result is false,
    when each is driven, then the state after it is the state before it,
    as the document writes, and the answer is a transition and not a
    refusal."""
    rejected = [row for row in THE_ROWS if row[3] == "false"]
    assert len(rejected) == 2, (
        f"WHAT: the table writes {len(rejected)} rejected rows of the "
        f"{len(THE_ROWS)} it defines: {rejected}. "
        "WHY: a business rejection is one of the two rejections the Owner "
        "must tell apart, so the rows that carry one are counted against "
        "the table. HOW: read SPEC.md's table."
    )
    source, descriptor = machines.shipped_machine("reservation")

    for before, event, after, _ in rejected:
        answer = machines.drive(
            source, descriptor, f"(Reservation {before})", [f"({event})"]
        )

        ran = machines.transitions_of(answer)
        assert before == after, (
            f"WHAT: the document's rejected row ({before}, {event}) writes "
            f"the state {after} after it. "
            "WHY: this test is about the rows that change nothing. "
            "HOW: read SPEC.md's table."
        )
        assert ran[0].get("state_before") == ran[0].get("state_after"), (
            f"WHAT: the rejected row ({before}, {event}) moved the state "
            f"from {ran[0].get('state_before')!r} to "
            f"{ran[0].get('state_after')!r}. "
            "WHY: the document's table writes the same state before and "
            "after a rejected event: the component rejects without changing "
            "state. HOW: publish the state the projection read off the "
            "outcome the step answered."
        )
        assert ran[0].get("result") == machines.A_TRANSITION, (
            f"WHAT: the rejected row ({before}, {event}) was published as "
            f"{ran[0].get('result')!r}. "
            "WHY: criterion 3 promises that an admissible event whose "
            "business result is a rejection is a normal answer, "
            "distinguishable from an event outside the admissible domain. "
            "HOW: publish it as a transition carrying its outcome."
        )
