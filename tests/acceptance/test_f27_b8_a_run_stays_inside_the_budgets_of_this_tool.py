"""F27 against the budgets this tool declares -- driving many events is
work, and the run is measured against the time budget while it drives
them, not only before it starts.

The law: a run that passes the time this operation is given stops where
it stands and says so; it never answers a completed run of work the tool
was no longer allowed to do.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused the request for some other reason --
the same request with nothing lowered is driven first and must answer
the whole sequence, so the refusal below is the budget and not the
request.
"""

from __future__ import annotations

import _f27_runtime_fixtures as machines

# Enough ticks that driving them costs far more than the time the run is
# given below, and few enough that the run with nothing lowered stays
# well inside the ten seconds this tool declares.
MANY_TICKS = ["(Tick)"] * 4000

# Twenty-five milliseconds of work. Measured against this tool on this
# machine: reading the request, checking the program and resolving the
# eight roles cost a few milliseconds, and driving 4000 ticks costs about
# 110, so the time runs out inside the sequence and nowhere else. The
# test below shows both ends of that: one tick inside the same 25
# milliseconds is driven whole.
TWENTY_FIVE_MILLISECONDS = {"PROVA_BUDGET_OPERATION_TIME": "25"}


def test_four_thousand_ticks_are_driven_when_nothing_is_lowered():
    """Given the shipped hour clock at 11 o'clock, when the Owner sends
    4000 ticks under the budgets this tool declares, then all 4000 are
    driven and the answer is completed."""
    source, descriptor = machines.shipped_machine("hour-clock")

    answer = machines.drive(source, descriptor, "(Clock 11)", MANY_TICKS)

    assert answer.get("status") == "completed", (
        f"WHAT: 4000 ticks under the declared budgets were answered "
        f"{answer.get('status')!r}: {str(answer)[:400]}. "
        "WHY: this is the control for the budget case below: the work fits "
        "inside the ten seconds this tool declares, so a refusal here would "
        "mean the refusal below says nothing about the budget. "
        "HOW: read the refusal above."
    )
    assert len(machines.transitions_of(answer)) == len(MANY_TICKS), (
        f"WHAT: {len(machines.transitions_of(answer))} of the "
        f"{len(MANY_TICKS)} ticks sent were published. "
        "WHY: every event sent is driven or refused, and the Owner reads one "
        "entry per event. HOW: publish them all."
    )


def test_a_run_past_the_time_it_is_given_is_refused_and_claims_nothing():
    """Given the same 4000 ticks, when the Owner lowers the time this
    operation may take to 25 milliseconds, then the answer is
    'resource_exhausted', carries no result at all and names the budget
    it passed."""
    source, descriptor = machines.shipped_machine("hour-clock")

    one_tick = machines.drive(
        source, descriptor, "(Clock 11)", ["(Tick)"], TWENTY_FIVE_MILLISECONDS
    )
    assert one_tick.get("status") == "completed", (
        f"WHAT: one tick inside 25 milliseconds was answered "
        f"{one_tick.get('status')!r}: {str(one_tick)[:400]}. "
        "WHY: this is the other end of the control: reading the request, "
        "checking the program and resolving the roles fit inside the 25 "
        "milliseconds, so what runs out below is the sequence. "
        "HOW: read the refusal above."
    )

    answer = machines.drive(
        source, descriptor, "(Clock 11)", MANY_TICKS, TWENTY_FIVE_MILLISECONDS
    )

    assert answer.get("status") == "resource_exhausted", (
        f"WHAT: 4000 ticks inside 25 milliseconds were answered "
        f"{answer.get('status')!r}: {str(answer)[:400]}. "
        "WHY: the run is measured against the time this operation is given "
        "while it drives the events; a run that answers a completed sequence "
        "it was no longer allowed to drive tells the Owner the work fit when "
        "it did not. HOW: ask the budget between the events."
    )
    assert answer.get("result") is None, (
        f"WHAT: the refused run still carries a result: "
        f"{str(machines.result_of(answer))[:300]}. "
        "WHY: the run stopped inside a budget of this tool, and a published "
        "state beside that refusal would read as a sequence this tool stands "
        "behind. HOW: answer the budget refusal alone."
    )
    refusal = (machines.diagnostics_of(answer) or [{}])[0]
    assert "operation_time" in str(refusal), (
        f"WHAT: the refusal does not name the budget that was passed: "
        f"{refusal}. "
        "WHY: the Owner reads which of the four budgets to raise, and the "
        "name is the one the manifest publishes for it. "
        "HOW: name the budget, what it allows and what was reached."
    )
