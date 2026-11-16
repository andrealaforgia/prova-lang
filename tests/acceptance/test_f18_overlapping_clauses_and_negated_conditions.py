"""Programs where the order of the clauses, or the negation of a
condition, decides the answer.

Added after an independent review: two defects in the translation
survived the whole suite, because every match in the oracle was over
patterns that cannot both take a value, and every condition in it was
assumed as written rather than negated.

Both families are here now:

* a match with two clauses writing the same pattern, where only the
  first may win;
* a call reached because a condition is false -- in the other branch of
  an `if`, and in the clause a pattern did not take -- and a `not` in
  what a function asks of its input.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered proved for everything. Three of the
cases below require an obligation NOT to be proved, each for a reason
the program really has.
"""

from __future__ import annotations

from _f18_fixtures import (
    completed,
    entry_named,
    evaluate,
    not_proved,
    results_by_identity,
    verify,
)

# The second clause writes the pattern the first one already wrote, so
# only the first may win: f answers 10 at 1, and a promise of 20 is
# false. A translation that let a later clause win would call this
# promise kept.
THE_LATER_CLAUSE_MUST_NOT_WIN = """(defn f
  (sig ((x Int)) -> Int ! pure)
  (ensures (= result 20))
  (examples (example (f 1) => 20))
  (match x (1 10) (1 20) (_ 10)))
"""

# The same shape with a promise that is true of the first clause
# winning: 10 at 1 and 30 elsewhere.
THE_FIRST_CLAUSE_WINS = """(defn first-wins
  (sig ((x Int)) -> Int ! pure)
  (ensures (= result (if (= x 1) 10 30)))
  (examples (example (first-wins 1) => 10) (example (first-wins 7) => 30))
  (match x (1 10) (1 20) (_ 30)))
"""

# A call that happens only where a test failed, and whose precondition
# is exactly what the failure of that test says.
REACHED_BECAUSE_A_TEST_FAILED = """(defn only-big
  (sig ((y Int)) -> Int ! pure)
  (requires (> y 100))
  (ensures (> result 0))
  (examples (example (only-big 101) => 101))
  y)

(defn above
  (sig ((x Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (above 5) => 0) (example (above 101) => 101))
  (if (<= x 100) 0 (only-big x)))
"""

# The same call where the failure of the test says the opposite of what
# the callee asks: nothing above 100 reaches it, and it takes only
# numbers above 100.
REACHED_WHERE_THE_CALLEE_REFUSES = """(defn only-big
  (sig ((y Int)) -> Int ! pure)
  (requires (> y 100))
  (ensures (> result 0))
  (examples (example (only-big 101) => 101))
  y)

(defn below
  (sig ((x Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (below 101) => 0))
  (if (> x 100) 0 (only-big x)))
"""

# A call in the clause a pattern did not take: with two variants, not
# being Plus is being Minus, which is what the callee asks for.
REACHED_BECAUSE_A_PATTERN_DID_NOT_MATCH = """(deftype Sign (union (Plus) (Minus)))

(defn only-minus
  (sig ((s Sign)) -> Int ! pure)
  (requires (= s (Minus)))
  (ensures (> result 0))
  (examples (example (only-minus (Minus)) => 1))
  1)

(defn second-clause
  (sig ((s Sign)) -> Int ! pure)
  (ensures (>= result 0))
  (examples
    (example (second-clause (Plus)) => 0)
    (example (second-clause (Minus)) => 1))
  (match s ((Plus) 0) (_ (only-minus s))))
"""

# A `not` in what a function asks of its input, where the promise
# follows from the negation and not from the condition inside it.
A_NEGATED_CONDITION = """(defn not-negative
  (sig ((n Int)) -> Bool ! pure)
  (requires (not (< n 0)))
  (ensures result)
  (examples (example (not-negative 0) => true))
  (>= n 0))
"""


def _all_proved(source: str, label: str, owed: int) -> None:
    answer = completed(verify(source), label)
    assert not not_proved(answer, label), (
        f"WHAT: {not_proved(answer, label)} did not come back proved for "
        f"{label}. "
        "WHY: every obligation of this program is true of it, and each one "
        "is in the oracle because a defect in the translation would make it "
        "false. "
        f"HOW: inspect the answer: {answer}"
    )
    assert len(results_by_identity(answer, label)) == owed, (
        f"WHAT: {label} owes {len(results_by_identity(answer, label))} "
        f"obligations, not the {owed} its declarations ask for. "
        "WHY: a program owing fewer than it should would pass the test above "
        "by owing nothing. "
        f"HOW: inspect the answer: {answer}"
    )


def test_a_promise_true_only_of_a_later_clause_is_disproved():
    """Given a function whose second clause writes the pattern the first
    already wrote, and which promises the answer the second one would
    give, when the Owner asks what it owes, then the promise and the
    declared example are both disproved, and the input named for the
    example is refused when the program runs over it."""
    label = "a promise true only if a later clause won"
    answer = completed(verify(THE_LATER_CLAUSE_MUST_NOT_WIN), label)
    stood = results_by_identity(answer, label)

    assert stood["body_postcondition:f:body"] == "disproved", stood
    declared = entry_named(answer, "example_validity:f:example[0]", label)
    assert declared["result"] == "disproved", (
        f"WHAT: the declared example is answered {declared['result']!r}. "
        "WHY: the first clause that matches wins, so f answers 10 at 1 and "
        "the example states 20; a tool that called this example valid would "
        "be reading the clauses in the wrong order. "
        f"HOW: inspect the entry: {declared}"
    )

    replayed = evaluate(
        THE_LATER_CLAUSE_MUST_NOT_WIN,
        declared["counterexample"]["function"],
        declared["counterexample"]["arguments"],
    )
    assert not (replayed.get("result") or {}).get("value"), (
        f"WHAT: running f over {declared['counterexample']['arguments']} "
        f"answers {replayed.get('result')}, so that input does not break "
        "anything. "
        "WHY: the answer named it as the input the example is wrong at; an "
        "input the program answers happily would make this a false disproof. "
        f"HOW: inspect the run: {replayed}"
    )
    assert "postcondition_violation" in {
        d.get("category") for d in (replayed.get("diagnostics") or [])
    }, (
        f"WHAT: running f over {declared['counterexample']['arguments']} is "
        f"not refused for the promise it breaks: {replayed}. "
        "WHY: the first clause that matches wins, so f answers 10 there, "
        "which is neither the 20 its promise states nor the 20 its example "
        "states. "
        f"HOW: inspect the run: {replayed}"
    )


def test_a_promise_true_of_the_first_clause_winning_is_proved():
    """Given the same shape of program, promising what the first
    matching clause really answers, when the Owner asks what it owes,
    then all 5 obligations come back proved."""
    _all_proved(THE_FIRST_CLAUSE_WINS, "a promise the first clause keeps", 5)


def test_a_call_reached_because_a_test_failed_is_proved():
    """Given a call that happens only where a test failed, and whose
    precondition is what that failure says, when the Owner asks what the
    program owes, then all 10 obligations come back proved."""
    _all_proved(
        REACHED_BECAUSE_A_TEST_FAILED, "a call reached because a test failed", 10
    )


def test_a_call_reached_where_the_callee_refuses_is_not_proved():
    """Given the same call where the failure of the test says the
    opposite of what the callee asks, when the Owner asks what the
    program owes, then that call is not proved."""
    label = "a call reached where the callee refuses"
    entry = entry_named(
        completed(verify(REACHED_WHERE_THE_CALLEE_REFUSES), label),
        "call_precondition:below:body/else",
        label,
    )

    assert entry["path_condition"] == "(not (> x 100))", entry
    assert entry["result"] != "proved", (
        f"WHAT: a call reached only by numbers that are not above 100, to a "
        f"function taking only numbers above 100, is answered "
        f"{entry['result']!r}. "
        "WHY: a translation that assumed the test rather than its failure "
        "would prove this, and would then prove a call the program really "
        "makes wrongly. "
        f"HOW: inspect the entry: {entry}"
    )


def test_a_call_in_the_clause_a_pattern_did_not_take_is_proved():
    """Given a call in the clause a pattern did not take, whose
    precondition is what not matching that pattern says, when the Owner
    asks what the program owes, then all 10 obligations come back
    proved."""
    _all_proved(
        REACHED_BECAUSE_A_PATTERN_DID_NOT_MATCH,
        "a call in the clause a pattern did not take",
        10,
    )


def test_a_promise_following_from_a_negated_condition_is_proved():
    """Given a function asking that its input is not negative and
    promising what follows from that, when the Owner asks what it owes,
    then all 4 obligations come back proved."""
    _all_proved(A_NEGATED_CONDITION, "a promise under a negated condition", 4)
