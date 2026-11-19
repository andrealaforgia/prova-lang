"""F28 repair -- a machine whose evidence is longer than this tool writes.
The reference semantics can compute a number of thousands of digits, and
this tool writes an integer of at most the length it publishes. The
answer still carries the inventory and the word over the whole: the
obligation whose evidence cannot be shown is unsettled, naming the limit,
and the trace that could not be written is disclosed as that.

The law: a limit this tool declares never turns an answer about a program
into a failure of the tool. The inventory a reader asked for stands, no
obligation is reported broken on evidence nobody can read, and nothing is
silently dropped.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool answered 'unknown' for every obligation of
every machine. test_f28_b1 requires preservation disproved for the
missing guard and test_f28_b6 requires all three proved for both shipped
machines.
"""

from __future__ import annotations

import _f28_repair_fixtures as repair


def test_an_oversized_witness_leaves_the_inventory_and_the_word_standing():
    """Given a counter whose step multiplies the count by a thousand
    nines five times over, so that the state one step from its initial
    state is about five thousand digits long, when the Owner asks the
    tool to verify it with its descriptor, then the answer is a completed
    answer about the program, carries the word over the whole, and leaves
    preservation unsettled rather than disproved."""
    source, descriptor = repair.a_machine_whose_evidence_is_too_large_to_write()

    answered = repair.ask_to_verify(source, descriptor)

    assert answered.get("status") == "completed", (
        f"WHAT: the answer about a machine whose evidence is too long to "
        f"write has status {answered.get('status')!r}: "
        f"{repair.as_text(answered)[:400]}. "
        "WHY: a limit this tool declares is part of answering about a "
        "program, not a failure of the tool; a reader who asked what the "
        "program owes is left with nothing. HOW: read the limit where the "
        "evidence is written and leave that one obligation unsettled."
    )
    assert repair.aggregate_of(answered).get("result") == repair.NOT_VERIFIED, (
        f"WHAT: the word over the whole is "
        f"{repair.aggregate_of(answered).get('result')!r}: "
        f"{repair.aggregate_of(answered)}. "
        "WHY: an obligation left unsettled is not an obligation proved, and "
        "the Owner must not be told a machine was shown whole when one of "
        "its obligations could not be settled. HOW: compute the word over "
        "every obligation as it stands."
    )
    entry = repair.the_three_obligations(answered).get(repair.PRESERVATION) or {}
    assert entry.get("result") == repair.UNKNOWN, (
        f"WHAT: preservation stands as {entry.get('result')!r}: {entry}. "
        "WHY: the solver found a solution and the replay established "
        "something, but the evidence cannot be shown to the reader; "
        "evidence nobody can read is no counterexample, and 'proved' would "
        "certify an invariant that is not inductive. "
        "HOW: leave it unsettled with the limit in its reason."
    )
    assert entry.get("counterexample") is None, (
        f"WHAT: the unsettled obligation carries a counterexample: {entry}. "
        "WHY: the one thing that could not be done is writing it. "
        "HOW: carry none."
    )
    reason = entry.get("reason") or ""
    assert "digits" in reason and "4000" in reason, (
        f"WHAT: the reason does not name the limit that withheld the word: "
        f"{reason!r}. "
        "WHY: the Owner must be able to tell this from an invariant that "
        "held and from a solver that could not tell, and to act on it by "
        "having the program compute a shorter result. "
        "HOW: name the limit and the digits the value reached."
    )


def test_a_trace_too_long_to_write_is_disclosed_and_not_dropped():
    """Given that same machine, whose first declared transition from its
    initial state answers a number too long to write, when the Owner
    reads the machine block, then it says a run established something
    this tool will not write, naming the limit, and carries no reachable
    counterexample."""
    source, descriptor = repair.a_machine_whose_evidence_is_too_large_to_write()

    answered = repair.ask_to_verify(source, descriptor)

    said = repair.machine_block_of(answered)
    unwritten = said.get(repair.THE_UNWRITTEN_FIELD) or {}
    assert unwritten, (
        f"WHAT: the machine block says nothing about evidence that could "
        f"not be written: {sorted(said)}. "
        "WHY: the absence of a trace reads as every declared transition "
        "replaying, which is not what happened here; silence would tell the "
        "Owner the opposite of the truth. HOW: disclose it under "
        f"{repair.THE_UNWRITTEN_FIELD!r}."
    )
    assert unwritten.get("maximum") and unwritten.get("digits_reached"), (
        f"WHAT: the disclosure names neither the limit nor the length "
        f"reached: {unwritten}. "
        "WHY: a reader who cannot see the number must at least be told how "
        "long it was and what the limit is. HOW: carry both."
    )
    assert repair.reachable_counterexample_of(answered) is None, (
        f"WHAT: the answer carries a reachable counterexample whose "
        f"evidence could not be written: "
        f"{repair.reachable_counterexample_of(answered)}. "
        "WHY: the name is for a trace a reader can see and replay. "
        "HOW: disclose the limit instead."
    )
