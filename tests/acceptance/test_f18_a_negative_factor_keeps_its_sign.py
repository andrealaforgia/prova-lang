"""Multiplication by a literal whose sign, zero or width could be lost.

Added after a second independent review: a defect that dropped the sign
of a negative literal factor -- translating `(* -3 x)` as `3 * x` --
survived the whole suite and gave a wrong `proved`. Nothing in the
repository multiplied by a negative literal at all, so nothing could
have caught it.

Every shape a literal factor can take is here: negative on the left and
on the right, a promise the sign makes false, a promise the sign makes
true, a literal written `-0`, one written `+002`, and one of 30 digits,
which no machine word holds.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered proved for everything. The first case
requires a promise the sign of the factor makes false NOT to be proved,
and names the input that breaks it.
"""

from __future__ import annotations

from _f18_fixtures import completed, entry_named, evaluate, not_proved, verify

# Three times minus one is negative, so a promise of a positive answer
# is false for every number this function accepts. A translation that
# dropped the minus sign would call this promise kept.
THE_SIGN_MAKES_THE_PROMISE_FALSE = """(defn f
  (sig ((x Int)) -> Int ! pure)
  (requires (> x 0))
  (ensures (> result 0))
  (examples (example (f 1) => -3))
  (* -3 x))
"""

# The same body with the promise the sign really keeps.
THE_SIGN_MAKES_THE_PROMISE_TRUE = """(defn f
  (sig ((x Int)) -> Int ! pure)
  (requires (> x 0))
  (ensures (< result 0))
  (examples (example (f 1) => -3))
  (* -3 x))
"""

# The literal on the other side of the operator.
THE_LITERAL_ON_THE_RIGHT = """(defn g
  (sig ((x Int)) -> Int ! pure)
  (requires (> x 0))
  (ensures (< result 0))
  (examples (example (g 2) => -6))
  (* x -3))
"""

# Minus nothing is nothing: the promise names 0 rather than repeating
# the body, so a translation reading `-0` as anything else fails it.
A_LITERAL_WRITTEN_MINUS_ZERO = """(defn h
  (sig ((x Int)) -> Int ! pure)
  (ensures (= result 0))
  (examples (example (h 5) => 0))
  (* -0 x))
"""

# A literal written with a plus and leading zeros, promised against the
# same number written plainly.
A_LITERAL_WRITTEN_WITH_LEADING_ZEROS = """(defn k
  (sig ((x Int)) -> Int ! pure)
  (ensures (= result (* 2 x)))
  (examples (example (k 5) => 10))
  (* +002 x))
"""

# A negative factor of 30 digits, which is far past any machine word:
# Int here is the mathematical integers.
A_FACTOR_NO_MACHINE_WORD_HOLDS = """(defn wide
  (sig ((x Int)) -> Int ! pure)
  (requires (> x 0))
  (ensures (< result 0))
  (examples (example (wide 1) => -100000000000000000000000000000))
  (* -100000000000000000000000000000 x))
"""

# A call whose callee asks two things at once, reached through two
# tests: the condition that reaches it is both of them together, and
# neither alone would meet what the callee asks.
TWO_TESTS_REACH_THE_CALL = """(defn in-range
  (sig ((y Int)) -> Int ! pure)
  (requires (and (> y 100) (< y 300)))
  (ensures (> result 0))
  (examples (example (in-range 200) => 200))
  y)

(defn pick
  (sig ((x Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples
    (example (pick 200) => 200)
    (example (pick 5) => 0)
    (example (pick 400) => 0))
  (if (> x 100) (if (< x 300) (in-range x) 0) 0))
"""


def _all_proved(source: str, label: str, owed: int) -> None:
    answer = completed(verify(source), label)
    assert not not_proved(answer, label), (
        f"WHAT: {not_proved(answer, label)} did not come back proved for "
        f"{label}. "
        "WHY: every obligation of this program is true of it, and each is "
        "here because a defect in the translation would make it false. "
        f"HOW: inspect the answer: {answer}"
    )
    assert len(answer["result"]["inventory"]["obligations"]) == owed, (
        f"WHAT: {label} owes "
        f"{len(answer['result']['inventory']['obligations'])} obligations, "
        f"not {owed}. "
        "WHY: a program owing fewer than it should would pass the test above "
        "by owing nothing. "
        f"HOW: inspect the answer: {answer}"
    )


def test_a_promise_the_sign_of_the_factor_makes_false_is_disproved():
    """Given a function multiplying by minus three and promising a
    positive answer, when the Owner asks what it owes, then the promise
    is disproved and the input it names is refused when the program runs
    over it."""
    label = "a promise the sign makes false"
    answer = completed(verify(THE_SIGN_MAKES_THE_PROMISE_FALSE), label)
    entry = entry_named(answer, "body_postcondition:f:body", label)

    assert entry["result"] == "disproved", (
        f"WHAT: a promise of a positive answer by a function multiplying by "
        f"minus three is answered {entry['result']!r}. "
        "WHY: every number this function accepts is above 0, so every answer "
        "it gives is below 0; a tool that dropped the sign of the factor "
        "would call this promise kept, which is the worst defect it can have. "
        f"HOW: inspect the entry: {entry}"
    )
    replayed = evaluate(
        THE_SIGN_MAKES_THE_PROMISE_FALSE,
        entry["counterexample"]["function"],
        entry["counterexample"]["arguments"],
    )
    assert "postcondition_violation" in {
        d.get("category") for d in (replayed.get("diagnostics") or [])
    }, (
        f"WHAT: running f over {entry['counterexample']['arguments']} is not "
        f"refused for the promise it breaks: {replayed}. "
        "WHY: a witness that does not replay is not a counterexample. "
        f"HOW: inspect the run: {replayed}"
    )


def test_a_promise_the_sign_of_the_factor_keeps_is_proved():
    """Given the same body promising the negative answer it really
    gives, when the Owner asks what it owes, then all 4 obligations come
    back proved."""
    _all_proved(THE_SIGN_MAKES_THE_PROMISE_TRUE, "a promise the sign keeps", 4)


def test_a_negative_literal_on_the_right_of_the_operator_is_proved():
    """Given the literal written after the number rather than before it,
    when the Owner asks what the program owes, then all 4 obligations
    come back proved."""
    _all_proved(THE_LITERAL_ON_THE_RIGHT, "a literal on the right", 4)


def test_a_factor_written_minus_zero_is_nothing():
    """Given a function multiplying by a literal written `-0` and
    promising its answer is 0, when the Owner asks what it owes, then
    all 4 obligations come back proved."""
    _all_proved(A_LITERAL_WRITTEN_MINUS_ZERO, "a factor written minus zero", 4)


def test_a_factor_written_with_a_plus_and_leading_zeros_is_that_number():
    """Given a function multiplying by a literal written `+002` and
    promising the same answer as multiplying by 2, when the Owner asks
    what it owes, then all 4 obligations come back proved."""
    _all_proved(
        A_LITERAL_WRITTEN_WITH_LEADING_ZEROS, "a factor written with zeros", 4
    )


def test_a_factor_no_machine_word_holds_keeps_its_sign():
    """Given a function multiplying by a negative literal of 30 digits,
    when the Owner asks what it owes, then all 4 obligations come back
    proved."""
    _all_proved(
        A_FACTOR_NO_MACHINE_WORD_HOLDS, "a factor of 30 digits", 4
    )


def test_a_call_reached_through_two_tests_is_proved_under_both():
    """Given a call whose callee asks two things at once, reached through
    one test inside another, when the Owner asks what the program owes,
    then the call is proved under both conditions together."""
    label = "a call reached through two tests"
    entry = entry_named(
        completed(verify(TWO_TESTS_REACH_THE_CALL), label),
        "call_precondition:pick:body/then/then",
        label,
    )

    assert entry["path_condition"] == "(and (> x 100) (< x 300))", (
        f"WHAT: the call is answered under {entry.get('path_condition')!r}. "
        "WHY: both tests must hold to reach it, and the callee asks for both; "
        "either one alone would leave its precondition unmet. "
        f"HOW: inspect the entry: {entry}"
    )
    assert entry["result"] == "proved", (
        f"WHAT: the call is answered {entry['result']!r} although both tests "
        "that reach it say exactly what the callee asks for. "
        "WHY: the conditions that reach a site are assumed together; joined "
        "any other way they would prove less than the program says. "
        f"HOW: inspect the entry: {entry}"
    )


# A bound five below zero, written with a negative literal. Nothing
# about it promises a positive answer: a translation that lost the sign
# of the literal would read it as a bound five above zero and call the
# promise kept.
A_BOUND_BELOW_ZERO = """(defn f
  (sig ((x Int)) -> Int ! pure)
  (requires (> x -5))
  (ensures (> result 0))
  (examples (example (f 7) => 7))
  x)
"""

# The same program with the bound the promise really needs.
A_BOUND_AT_ZERO = """(defn f
  (sig ((x Int)) -> Int ! pure)
  (requires (> x 0))
  (ensures (> result 0))
  (examples (example (f 7) => 7))
  x)
"""


def test_a_bound_five_below_zero_does_not_promise_a_positive_answer():
    """Given a function accepting every number above minus five and
    promising a positive answer, when the Owner asks what it owes, then
    the promise is disproved and the input it names is refused when the
    program runs over it."""
    label = "a bound five below zero"
    entry = entry_named(
        completed(verify(A_BOUND_BELOW_ZERO), label),
        "body_postcondition:f:body",
        label,
    )

    assert entry["result"] == "disproved", (
        f"WHAT: a promise of a positive answer by a function that accepts "
        f"minus four is answered {entry['result']!r}. "
        "WHY: a bound five below zero is not a bound at zero; a translation "
        "that lost the sign of the literal would read the two as one and "
        "call this promise kept, which is a wrong proved. "
        f"HOW: inspect the entry: {entry}"
    )
    arguments = entry["counterexample"]["arguments"]
    assert all(int(written) <= 0 for written in arguments), (
        f"WHAT: the input named is {arguments}, which is above zero. "
        "WHY: every number above zero keeps this promise; only one between "
        "minus five and zero breaks it. "
        f"HOW: inspect the entry: {entry}"
    )
    replayed = evaluate(A_BOUND_BELOW_ZERO, "f", arguments)
    assert "postcondition_violation" in {
        d.get("category") for d in (replayed.get("diagnostics") or [])
    }, (
        f"WHAT: running f over {arguments} is not refused for the promise it "
        f"breaks: {replayed}. "
        "WHY: a witness that does not replay is not a counterexample. "
        f"HOW: inspect the run: {replayed}"
    )


def test_the_same_promise_under_a_bound_at_zero_is_proved():
    """Given the same function accepting only numbers above zero, when
    the Owner asks what it owes, then all 4 obligations come back
    proved."""
    _all_proved(A_BOUND_AT_ZERO, "a bound at zero", 4)
