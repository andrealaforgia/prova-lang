"""F18.3 -- a program whose promise is false for some input of its own
declared types is not told that promise was shown.

The program promises that adding one to any whole number answers a
positive number. SPEC.md says `Int` is arbitrary precision and that both
branches of every typed input are checked, so -1 is an input of the
declared type and the promise is false there. The Owner is told so, with
the input that breaks it, and that input really does break it when the
same tool runs the function over it.

SPEC.md, "Results and evidence scope": disproof requires a validated
source-level witness satisfying the claim's assumptions and violating its
conclusion, and a witness that fails to replay yields unknown rather than
an invented disproof. So the witness this answer carries is sent straight
back to the tool as the arguments of a call.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered 'disproved' for every obligation of
every program. The second test requires the other three obligations of
this same program -- which are true of it -- to come back proved.
"""

from __future__ import annotations

from _f18_fixtures import (
    completed,
    entry_named,
    evaluate,
    results_by_identity,
    verify,
)

# Adding one to a whole number does not always answer a positive number:
# at -1 it answers 0. The example it declares is a true one, so the only
# false thing about this program is what it promises.
A_PROGRAM_THAT_PROMISES_TOO_MUCH = """(defn add-one
  (sig ((n Int)) -> Int ! pure)
  (ensures (> result 0))
  (examples (example (add-one 1) => 2))
  (+ n 1))
"""

LABEL = "a program promising a positive answer for every whole number"
THE_FALSE_PROMISE = "body_postcondition:add-one:body"
THE_TRUE_ONES = (
    "contract_definedness:add-one:contract",
    "example_validity:add-one:example[0]",
    "structural_termination:add-one:calls",
)


def test_a_promise_that_is_false_for_some_whole_number_is_not_proved():
    """Given a function promising that adding one answers a positive
    number, when the Owner asks what it owes, then that promise is not
    answered proved, and the answer names a whole number that breaks
    it."""
    answer = completed(verify(A_PROGRAM_THAT_PROMISES_TOO_MUCH), LABEL)
    entry = entry_named(answer, THE_FALSE_PROMISE, LABEL)

    assert entry["result"] != "proved", (
        f"WHAT: a promise that is false at -1 is answered {entry['result']!r}. "
        "WHY: a wrong 'proved' is the worst defect this tool can have: the "
        "Owner would ship a program on the strength of a promise that does "
        "not hold. "
        f"HOW: inspect the entry: {entry}"
    )
    assert entry["result"] == "disproved", (
        f"WHAT: the promise is answered {entry['result']!r} and a whole "
        "number breaking it exists. "
        "WHY: the Owner asked what this program owes; told only that nothing "
        "could be settled, they would look for a missing fragment rather than "
        "for the defect in their program. "
        f"HOW: inspect the entry: {entry}"
    )

    witness = entry.get("counterexample") or {}
    assert witness.get("function") == "add-one" and witness.get("arguments"), (
        f"WHAT: the entry carries {witness} as the input that breaks the "
        "promise. "
        "WHY: SPEC.md requires a disproof to carry a source-level witness "
        "that satisfies the assumptions and violates the conclusion; without "
        "the input, the Owner has nothing to reproduce. "
        f"HOW: inspect the entry: {entry}"
    )


def test_the_input_the_answer_names_really_breaks_the_promise():
    """Given the same program and the whole number the answer names, when
    the Owner runs the function over it, then the tool refuses the call
    for the promise it does not keep."""
    answer = completed(verify(A_PROGRAM_THAT_PROMISES_TOO_MUCH), LABEL)
    witness = entry_named(answer, THE_FALSE_PROMISE, LABEL)["counterexample"]

    replayed = evaluate(
        A_PROGRAM_THAT_PROMISES_TOO_MUCH,
        witness["function"],
        witness["arguments"],
    )

    categories = {
        diagnostic.get("category")
        for diagnostic in (replayed.get("diagnostics") or [])
    }
    assert "postcondition_violation" in categories, (
        f"WHAT: running add-one over {witness['arguments']} reports "
        f"{sorted(categories)} and answers {replayed.get('result')}. "
        "WHY: the answer named that input as one that breaks the promise; an "
        "input the same tool accepts there is an invented disproof, which "
        "SPEC.md forbids -- a witness that fails to replay yields unknown. "
        f"HOW: inspect the run: {replayed}"
    )


def test_what_is_true_of_the_same_program_is_still_proved():
    """Given the same program, when the Owner reads the rest of the
    answer, then its contract, its declared example and its ending come
    back proved."""
    stood = results_by_identity(verify(A_PROGRAM_THAT_PROMISES_TOO_MUCH), LABEL)

    unsettled = {
        identity: stood.get(identity)
        for identity in THE_TRUE_ONES
        if stood.get(identity) != "proved"
    }
    assert not unsettled, (
        f"WHAT: {unsettled} of a program whose only false part is what it "
        "promises. "
        "WHY: one false promise taints one obligation, not the program; a "
        "tool that refused everything beside it would tell the Owner nothing "
        "about where the defect is. "
        f"HOW: inspect the answer: {stood}"
    )
