"""F18b -- what an answer says about a program is in the program's own
order.

Two orders a reader relies on and nothing else pins:

The order of the clauses of a condition that reaches a call. A reader
compares the condition the answer prints with the text in front of
them; a condition whose clauses arrive in another order says the same
thing to a solver and is something else to read. The clauses of a
`match` are tried in source order, so the condition reaching a clause
reads in source order too: the patterns before it that did not take the
value, then its own.

The order of the obligations of one function. A contract is read before
a body, so the calls a contract makes are owed before the calls a body
makes, and a reader following the answer down follows the declaration
down.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool printed one clause instead of two. Each
condition below is given in full and compared whole.
"""

from __future__ import annotations

from _f18_fixtures import completed, entry_named, obligations_of, verify

# A function taking only the number 1, called from two clauses of a
# match, so the condition reaching each clause carries the patterns
# before it.
TWO_CLAUSES_BEHIND_EARLIER_PATTERNS = """(defn only-one
  (sig ((x Int)) -> Int ! pure)
  (requires (= x 1))
  (examples (example (only-one 1) => 1))
  1)

(defn pick
  (sig ((x Int)) -> Int ! pure)
  (examples (example (pick 0) => 0))
  (match x (0 0) (1 (only-one x)) (_ (only-one 1))))
"""

# A function calling one function in its contract and another in its
# body.
A_CALL_IN_THE_CONTRACT_AND_A_CALL_IN_THE_BODY = """(defn positive
  (sig ((x Int)) -> Bool ! pure)
  (examples (example (positive 1) => true))
  (> x 0))

(defn twice
  (sig ((x Int)) -> Int ! pure)
  (examples (example (twice 1) => 2))
  (+ x x))

(defn f
  (sig ((x Int)) -> Int ! pure)
  (requires (positive x))
  (examples (example (f 1) => 2))
  (twice x))
"""

THE_SECOND_CLAUSE = "call_precondition:pick:body/case[1]"
THE_THIRD_CLAUSE = "call_precondition:pick:body/case[2]"
REACHING_THE_SECOND = "(and (not (matches x 0)) (matches x 1))"
REACHING_THE_THIRD = "(and (not (matches x 0)) (not (matches x 1)))"

THE_CONTRACT_CALL = "call_precondition:f:requires[0]"
THE_BODY_CALL = "call_precondition:f:body"

LABEL = "two clauses standing behind earlier patterns"


def _reaching(identity: str) -> str:
    entry = entry_named(
        completed(verify(TWO_CLAUSES_BEHIND_EARLIER_PATTERNS), LABEL),
        identity,
        LABEL,
    )
    return entry["path_condition"]


def test_the_condition_reaching_a_clause_names_the_earlier_patterns_first():
    """Given a call in the second clause of a match, when the Owner
    reads what reaches it, then the pattern before it that did not take
    the value is named first and its own pattern second, as the program
    writes them."""
    reaching = _reaching(THE_SECOND_CLAUSE)

    assert reaching == REACHING_THE_SECOND, (
        f"WHAT: the second clause is reached under {reaching!r} and the "
        f"program reaches it under {REACHING_THE_SECOND!r}. "
        "WHY: a reader checks the printed condition against the text in "
        "front of them; clauses arriving in another order say the same "
        "thing to a solver and are something else to read. "
        "HOW: inspect the path_condition of that entry."
    )


def test_the_condition_reaching_a_later_clause_names_every_pattern_in_order():
    """Given a call in the third clause of the same match, when the
    Owner reads what reaches it, then both patterns before it are named
    in the order the program writes them."""
    reaching = _reaching(THE_THIRD_CLAUSE)

    assert reaching == REACHING_THE_THIRD, (
        f"WHAT: the third clause is reached under {reaching!r} and the "
        f"program reaches it under {REACHING_THE_THIRD!r}. "
        "WHY: the patterns a value got past are what makes a later clause "
        "reachable at all, and a reader follows them down the match. "
        "HOW: inspect the path_condition of that entry."
    )


def test_a_call_in_the_contract_is_owed_before_a_call_in_the_body():
    """Given a function calling one function in its contract and another
    in its body, when the Owner reads what it owes, then the contract's
    call stands before the body's, as the declaration does."""
    about = "a call in the contract and a call in the body"
    listed = [
        entry["id"]
        for entry in obligations_of(
            completed(verify(A_CALL_IN_THE_CONTRACT_AND_A_CALL_IN_THE_BODY), about),
            about,
        )
    ]

    assert THE_CONTRACT_CALL in listed and THE_BODY_CALL in listed, (
        f"WHAT: {listed} does not carry both {THE_CONTRACT_CALL!r} and "
        f"{THE_BODY_CALL!r}. "
        "WHY: this test is about the order of those two; an answer missing "
        "one of them has dropped an obligation. "
        "HOW: inspect the inventory."
    )
    assert listed.index(THE_CONTRACT_CALL) < listed.index(THE_BODY_CALL), (
        f"WHAT: the body's call is owed before the contract's: {listed}. "
        "WHY: a contract is read before a body, and a reader following the "
        "answer down follows the declaration down. "
        "HOW: inspect the inventory."
    )
