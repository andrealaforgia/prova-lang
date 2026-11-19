"""F27, the failure point the request does not name -- a role function
whose own contract refuses while the run is asking it.

The law: a run that meets a refused contract publishes no state and no
transition at all, and says which event reached which function and which
of its two contracts the values did not satisfy.

What this does NOT promise: the transitions that ran before the refused
one are not published. The Owner reads the position that stopped the run
and drives the events before it again to see where the machine stood;
docs/ROADMAP.md carries the follow-up that asks whether a refused
contract should instead stop the sequence and publish the attempts
before it, as a boundary rejection does.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool refused the request outright before driving
anything -- the answer is asserted to be 'completed', the status of a run
that happened, and the refusal is asserted to name the second event and
not the first.
"""

from __future__ import annotations

import _f27_runtime_fixtures as machines


def test_a_role_whose_contract_refuses_stops_the_run_and_says_which_event():
    """Given a clock whose invariant admits 13 o'clock while its step
    requires an hour between 1 and 12, at 12 o'clock, when the Owner
    sends two ticks, then the answer is completed, carries no result at
    all, and its one refusal names the step function and the second
    event."""
    source, descriptor = machines.clock_whose_step_asks_for_more()

    answer = machines.drive(source, descriptor, "(Clock 12)", ["(Tick)", "(Tick)"])

    assert answer.get("status") == "completed", (
        f"WHAT: the run was answered {answer.get('status')!r}: {answer}. "
        "WHY: the request was readable and the machine resolved, so the run "
        "happened: what it met is the program's own contract refusing, which "
        "this tool answers as it answers the same refusal of an evaluation. "
        "HOW: read the refusal above."
    )
    assert machines.categories_of(answer) == ["precondition_violation"], (
        f"WHAT: the run carries {machines.categories_of(answer)}: {answer}. "
        "WHY: the step function of this clock requires an hour between 1 and "
        "12, and the second tick would run it at 13; the Owner reads which "
        "of a function's two contracts refused. "
        "HOW: answer the category the evaluation of the same call answers."
    )
    refusal = machines.diagnostics_of(answer)[0]
    assert refusal.get("symbol") == descriptor["roles"]["step"], (
        f"WHAT: the refusal names {refusal.get('symbol')!r}, and the "
        f"function whose contract refused is "
        f"{descriptor['roles']['step']!r}: {refusal}. "
        "WHY: the Owner is sent to the function to read, not to the role "
        "that named it. HOW: name the function."
    )
    assert "position 2" in refusal.get("reason", ""), (
        f"WHAT: the refusal does not say which event reached it: "
        f"{refusal.get('reason')!r}. "
        "WHY: the first tick ran and the second was the one that reached a "
        "refused contract; an Owner told only the function cannot tell which "
        "of the events sent to look at. HOW: name the position."
    )
    assert refusal.get("location", {}).get("line"), (
        f"WHAT: the refusal says nowhere to open: {refusal}. "
        "WHY: it is about a function the submitted program declares, so it "
        "stands at that declaration. HOW: carry the line and the column."
    )
    assert answer.get("result") is None, (
        f"WHAT: the run carries a result beside the refusal: "
        f"{machines.result_of(answer)}. "
        "WHY: the run did not finish, and a state published beside a refused "
        "contract would read as a state the program stands behind. "
        "HOW: answer the refusal alone, as this tool answers the same "
        "refusal of an evaluation."
    )
