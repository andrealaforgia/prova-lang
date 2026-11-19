"""F26 criterion 5 -- the Owner names an invariant the step can leave: a
counter whose ceiling nothing enforces. Preservation is not proved, and
no weaker condition is put in its place.

The law: the preservation obligation is about the invariant the
descriptor names and about no other predicate; when it is not inductive
on its own, the answer withholds 'proved' and says so (SPEC.md lines
403-406).

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool never proves preservation for anything.
test_f26_b1 and test_f26_b2 require it proved for three machines whose
invariants are inductive, so a tool that withholds it everywhere fails
there.
"""

from __future__ import annotations

import _f26_induction_fixtures as induction


def test_an_invariant_the_step_can_leave_is_not_proved_preserved():
    """Given a counter whose invariant is that it stays at or below 10
    and whose step adds one whatever the state, when the Owner asks the
    tool to verify it with its descriptor, then preservation does not
    stand as 'proved' and the entry says why."""
    source, descriptor = induction.THE_MACHINE_THAT_IS_NOT_INDUCTIVE

    answered = induction.ask_to_verify(source, descriptor)

    entry = induction.the_three_obligations(answered).get(induction.PRESERVATION)
    assert entry is not None, (
        f"WHAT: the answer lists no preservation obligation at all: "
        f"{induction.listed_obligations(answered)}. "
        "WHY: an obligation nothing says anything about reads as one nobody "
        "owes, which for a machine that does leave its invariant is the one "
        "answer that misleads. HOW: list the preservation obligation and say "
        "what became of it."
    )
    assert entry.get("result") != induction.PROVED, (
        f"WHAT: preservation of a counter that steps from 10 to 11 stands as "
        f"{entry.get('result')!r}: {entry}. "
        "WHY: criterion 5 promises that an invariant which is not inductive "
        "on its own is not reported as preserved; the state after one step "
        "from the ceiling does not satisfy it. "
        "HOW: withhold the word and say what the solver answered."
    )
    assert (entry.get("reason") or entry.get("counterexample")), (
        f"WHAT: preservation stands as {entry.get('result')!r} with neither "
        f"a reason nor a counterexample beside it: {entry}. "
        "WHY: the Owner is left with a word and nothing to act on; every "
        "entry this tool does not prove says why. "
        "HOW: carry the reason the attempt gave, or the input that breaks it."
    )


def test_no_weaker_condition_is_put_in_the_place_of_the_invariant():
    """Given the same counter, which does satisfy the weaker condition of
    staying nonnegative, when the Owner reads the preservation entry,
    then it is about the invariant the descriptor names and the answer
    does not report the weaker condition as preserved."""
    source, descriptor = induction.THE_MACHINE_THAT_IS_NOT_INDUCTIVE

    answered = induction.ask_to_verify(source, descriptor)

    listed = induction.the_three_obligations(answered)
    assert induction.PRESERVATION in listed, (
        f"WHAT: the answer lists no preservation obligation: "
        f"{sorted(listed)}. "
        "WHY: this test reads which condition that obligation is about, and "
        "an absent entry is about none. HOW: list the preservation "
        "obligation."
    )
    said = induction.text_of(answered)
    assert induction.THE_WEAKER_PREDICATE_OF_THAT_MACHINE not in said, (
        f"WHAT: the answer carries the weaker condition "
        f"{induction.THE_WEAKER_PREDICATE_OF_THAT_MACHINE!r}, which the "
        "descriptor does not name as the invariant. "
        "WHY: SPEC.md lines 403-406 forbid substituting a weaker predicate "
        "for the one being checked; an answer that proved preservation of "
        "something else would read as the Owner's invariant preserved. "
        "HOW: state the obligation over the invariant the descriptor names."
    )
    entry = listed[induction.PRESERVATION]
    named = descriptor["roles"]["invariant"]
    assert named in str(entry), (
        f"WHAT: the preservation entry never names the invariant "
        f"{named!r} the descriptor gave: {entry}. "
        "WHY: the Owner reads the entry against the descriptor written; an "
        "entry that names no invariant says nothing about which condition "
        "was not shown to be preserved. HOW: name the invariant function."
    )


def test_a_machine_whose_invariant_is_not_inductive_is_not_verified():
    """Given the same counter, when the Owner asks the tool to verify it
    with its descriptor, then the word over the whole is 'not_verified'
    and its reason names the obligation left undischarged."""
    source, descriptor = induction.THE_MACHINE_THAT_IS_NOT_INDUCTIVE

    aggregate = induction.aggregate_of(induction.ask_to_verify(source, descriptor))

    assert aggregate.get("result") == induction.NOT_VERIFIED, (
        f"WHAT: a machine whose invariant the step can leave stands as "
        f"{aggregate.get('result')!r}: {aggregate}. "
        "WHY: the word over the whole is said when and only when every "
        "obligation is proved, and this machine's preservation is not. "
        "HOW: account for the machine obligations in that word."
    )
    undischarged = (aggregate.get("obligations") or {}).get("undischarged") or []
    assert any(induction.PRESERVATION in str(left) for left in undischarged), (
        f"WHAT: the word is withheld and the obligations left undischarged "
        f"are {undischarged}, naming no preservation obligation. "
        "WHY: the Owner must be sent to the obligation to repair; a withheld "
        "word that names something else sends the reader to the wrong place. "
        "HOW: name the undischarged machine obligation."
    )
