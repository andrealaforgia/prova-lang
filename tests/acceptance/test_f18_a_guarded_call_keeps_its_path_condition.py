"""F18.4 -- a call standing behind a condition is answered under that
condition, and the condition is what settles it.

SPEC.md, "Verification obligations and the initial fragment":
conditionals and matches retain their path conditions. A call that only
happens when a test succeeded may rely on that test; the same call
written without the test may not. Both shapes core-0 has for reaching a
call that way are here: the branch of an `if`, and the clause of a
`match`.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered 'proved' for every call precondition
whatever reached it. Each test below sends a second program where the
same call stands with nothing in front of it, and requires that one not
to come back proved.
"""

from __future__ import annotations

from _f18_fixtures import completed, entry_named, verify

# A function that takes only a positive number, called where a test has
# just shown the number is positive.
BEHIND_A_TEST = """(defn positive-only
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (> result 0))
  (examples (example (positive-only 1) => 1))
  n)

(defn guarded
  (sig ((n Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (guarded 5) => 5))
  (if (> n 0) (positive-only n) 0))
"""

# The same call with no test in front of it.
WITH_NOTHING_IN_FRONT = """(defn positive-only
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (> result 0))
  (examples (example (positive-only 1) => 1))
  n)

(defn unguarded
  (sig ((n Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (unguarded 5) => 5))
  (positive-only n))
"""

# A function that takes only one of the two signs, called in the clause
# that matched that sign.
INSIDE_THE_CLAUSE_THAT_MATCHED = """(deftype Sign (union (Plus) (Minus)))

(defn only-plus
  (sig ((s Sign)) -> Int ! pure)
  (requires (= s (Plus)))
  (ensures (> result 0))
  (examples (example (only-plus (Plus)) => 1))
  1)

(defn describe
  (sig ((s Sign)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (describe (Plus)) => 1) (example (describe (Minus)) => 0))
  (match s ((Plus) (only-plus s)) ((Minus) 0)))
"""

# The same call outside any clause.
OUTSIDE_EVERY_CLAUSE = """(deftype Sign (union (Plus) (Minus)))

(defn only-plus
  (sig ((s Sign)) -> Int ! pure)
  (requires (= s (Plus)))
  (ensures (> result 0))
  (examples (example (only-plus (Plus)) => 1))
  1)

(defn describe
  (sig ((s Sign)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (describe (Plus)) => 1))
  (only-plus s))
"""

THE_GUARDED_CALL = "call_precondition:guarded:body/then"
THE_UNGUARDED_CALL = "call_precondition:unguarded:body"
THE_MATCHED_CALL = "call_precondition:describe:body/case[0]"
THE_UNMATCHED_CALL = "call_precondition:describe:body"

THE_TEST_IN_FRONT = "(> n 0)"
THE_CLAUSE_THAT_MATCHED = "(matches s (Plus))"


def _settled_under(source: str, identity: str, label: str) -> dict:
    return entry_named(completed(verify(source), label), identity, label)


def test_a_call_in_a_branch_is_proved_under_the_test_that_reaches_it():
    """Given a call to a function that takes only a positive number,
    standing in the branch taken when the number is positive, when the
    Owner asks what the program owes, then that call comes back proved
    under the test `(> n 0)` that reaches it."""
    label = "a call behind a test"
    entry = _settled_under(BEHIND_A_TEST, THE_GUARDED_CALL, label)

    assert entry["path_condition"] == THE_TEST_IN_FRONT, (
        f"WHAT: the call is answered under {entry.get('path_condition')!r} "
        f"and the branch it stands in is reached when {THE_TEST_IN_FRONT}. "
        "WHY: the Owner reads what an obligation was shown about; a lost "
        "condition would report a claim about inputs that never reach the "
        "call. "
        f"HOW: inspect the entry: {entry}"
    )
    assert entry["result"] == "proved", (
        f"WHAT: the call is answered {entry['result']!r} although nothing "
        "but a positive number reaches it. "
        "WHY: a condition carried beside an obligation and not used to settle "
        "it is decoration; the Owner would have to show by hand what the "
        "program already says. "
        f"HOW: inspect the entry: {entry}"
    )


def test_the_same_call_with_nothing_in_front_of_it_is_not_proved():
    """Given the same call written outside any test, when the Owner asks
    what that program owes, then the call is not answered proved."""
    label = "the same call with nothing in front of it"
    entry = _settled_under(WITH_NOTHING_IN_FRONT, THE_UNGUARDED_CALL, label)

    assert entry["path_condition"] == "true"
    assert entry["result"] != "proved", (
        f"WHAT: a call reached by every whole number, to a function that "
        f"takes only positive ones, is answered {entry['result']!r}. "
        "WHY: at -1 this program calls a function that does not accept -1; a "
        "proved here would mean the condition reaching a call is ignored, and "
        "the test above would pass for a tool that proves every call. "
        f"HOW: inspect the entry: {entry}"
    )


def test_a_call_in_a_clause_is_proved_under_the_pattern_that_matched():
    """Given a call to a function that takes only the sign Plus,
    standing in the clause that matched Plus, when the Owner asks what
    the program owes, then that call comes back proved under the match
    that reaches it."""
    label = "a call inside the clause that matched"
    entry = _settled_under(INSIDE_THE_CLAUSE_THAT_MATCHED, THE_MATCHED_CALL, label)

    assert entry["path_condition"] == THE_CLAUSE_THAT_MATCHED, (
        f"WHAT: the call is answered under {entry.get('path_condition')!r} "
        f"and the clause it stands in is reached when "
        f"{THE_CLAUSE_THAT_MATCHED}. "
        "WHY: a clause of a match is as much a condition as a branch of an "
        "if; a lost one reports a claim about values that never reach the "
        "call. "
        f"HOW: inspect the entry: {entry}"
    )
    assert entry["result"] == "proved", (
        f"WHAT: the call is answered {entry['result']!r} although only the "
        "sign Plus reaches it. "
        "WHY: the clause that matched says which value the call is made with; "
        "a tool that cannot use it leaves the Owner to show by hand what the "
        "program already says. "
        f"HOW: inspect the entry: {entry}"
    )


def test_the_same_call_outside_every_clause_is_not_proved():
    """Given the same call written outside the match, when the Owner asks
    what that program owes, then the call is not answered proved."""
    label = "the same call outside every clause"
    entry = _settled_under(OUTSIDE_EVERY_CLAUSE, THE_UNMATCHED_CALL, label)

    assert entry["path_condition"] == "true"
    assert entry["result"] != "proved", (
        f"WHAT: a call reached by either sign, to a function that takes only "
        f"Plus, is answered {entry['result']!r}. "
        "WHY: with the sign Minus this program calls a function that does not "
        "accept it; a proved here would mean the clause that matched is "
        "ignored, and the test above would pass for a tool that proves every "
        "call. "
        f"HOW: inspect the entry: {entry}"
    )
