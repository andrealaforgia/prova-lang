"""F17.B4 -- in a verify answer, what an obligation would have to show
and what happened when something tried to show it are two separate
fields.

A reader then cannot take "nothing ran" for "nothing is owed", nor a
logical outcome for a run that reached one.

SPEC.md lines 270-284 fix the two vocabularies: a logical obligation
result is proved, disproved, unknown or not_attempted; an execution
status is completed, unsupported, timed out, cancelled, resource
exhausted, invalid input or tool failure. They are read here as the
machine contract they are, and no word belongs to both.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool wrote one value into both fields. The second
test requires each field's value to come from its own vocabulary, and
the two vocabularies share no word.
"""

from __future__ import annotations

from _f17_provenance_fixtures import A_PROGRAM, answer_about

LOGICAL_RESULTS = {"proved", "disproved", "unknown", "not_attempted"}
EXECUTION_STATUSES = {
    "completed",
    "unsupported",
    "timed_out",
    "cancelled",
    "resource_exhausted",
    "invalid_input",
    "tool_failure",
}


def _entries() -> list:
    inventory = (answer_about("verify", A_PROGRAM).get("result") or {}).get(
        "inventory"
    ) or {}
    entries = inventory.get("obligations") or []
    assert entries, (
        f"WHAT: the verify answer lists no obligation for a program whose 2 "
        f"functions own a contract, a body and an example: {inventory}. "
        "WHY: the rest of this file reads those entries. "
        "HOW: list what the program owes."
    )
    return entries


def test_each_obligation_carries_both_a_logical_result_and_an_execution_status():
    """Given the 2-function program, when it is sent to verify, then
    every entry of the inventory carries 2 fields: what it would have to
    show, and what happened when something tried."""
    missing = [
        entry["id"]
        for entry in _entries()
        if "result" not in entry or "execution_status" not in entry
    ]

    assert not missing, (
        f"WHAT: {len(missing)} of {len(_entries())} entries carry only one of "
        f"the two fields: {missing[:3]}. WHY: with one field a reader cannot "
        "tell an obligation nothing attempted from one a run reached and "
        "could not settle. HOW: carry the logical result and the execution "
        "status as 2 fields of every entry."
    )


def test_the_logical_result_and_the_execution_status_speak_their_own_words():
    """Given the same answer, then each entry's logical result is one of
    the 4 logical words, its execution status is one of the 7 execution
    words, and the 2 fields never hold the same word."""
    assert not (LOGICAL_RESULTS & EXECUTION_STATUSES), (
        "WHAT: the 2 vocabularies read from SPEC.md share a word. WHY: this "
        "test tells the fields apart by them. HOW: fix the vocabularies here."
    )

    for entry in _entries():
        assert entry["result"] in LOGICAL_RESULTS, (
            f"WHAT: {entry['id']!r} answers {entry['result']!r} as its "
            f"logical result, which is not 1 of {sorted(LOGICAL_RESULTS)}. "
            "WHY: a reader reads the logical standing of the obligation "
            "there. HOW: answer with one of those 4 words."
        )
        assert entry["execution_status"] in EXECUTION_STATUSES, (
            f"WHAT: {entry['id']!r} answers {entry['execution_status']!r} as "
            f"its execution status, which is not 1 of "
            f"{sorted(EXECUTION_STATUSES)}. WHY: a reader reads what happened "
            "to the attempt there. HOW: answer with one of those 7 words."
        )


def test_this_tool_owes_every_obligation_and_ran_none_of_them():
    """Given the same answer, then every entry is still owed and says
    that nothing supported running it, and the totals count 0 attempted
    against the whole list."""
    entries = _entries()
    owed = [entry for entry in entries if entry["result"] == "not_attempted"]
    unrun = [entry for entry in entries if entry["execution_status"] == "unsupported"]

    assert len(owed) == len(entries) and len(unrun) == len(entries), (
        f"WHAT: of {len(entries)} entries, {len(owed)} are still owed and "
        f"{len(unrun)} say nothing supported running them. WHY: this tool has "
        "no solver, so an entry saying otherwise reports work nobody did. "
        "HOW: answer not_attempted beside unsupported for every entry."
    )

    totals = (
        (answer_about("verify", A_PROGRAM).get("result") or {}).get("inventory") or {}
    ).get("totals") or {}
    assert totals.get("attempted") == 0 and totals.get("obligations") == len(entries), (
        f"WHAT: the totals say {totals} for a list of {len(entries)} entries. "
        "WHY: a count that does not add up to its own list cannot be read. "
        "HOW: count the entries."
    )
