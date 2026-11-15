"""Two programs whose promise pins an exact value, which the rest of the
oracle does not.

Both were added because a deliberate defect survived everything else.

The first multiplies by a literal and promises the exact product. Every
other program here that multiplies writes the same product on both sides
of its promise, so a translation that got multiplication wrong by the
same amount in both places agreed with itself and was never caught.

The second matches a whole number against a literal clause and then a
catch-all, so the clause that is tried first decides the answer. Every
other match here is over a union of variants that cannot both match, so
a translation that tried the clauses in the wrong order answered the
same thing either way and was never caught.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered proved for everything. The file
beside this one sends a promise that is false and requires it not to be
proved.
"""

from __future__ import annotations

from _f18_fixtures import completed, not_proved, obligations_of, verify

# Three times two is six, written as the promise and as a literal, so
# the two sides of the promise cannot both be wrong in the same way.
THE_EXACT_PRODUCT = """(defn tripled
  (sig ((n Int)) -> Int ! pure)
  (requires (= n 2))
  (ensures (= result 6))
  (examples (example (tripled 2) => 6))
  (* n 3))
"""

# A whole number matched against a literal clause and then a catch-all:
# both clauses match 0, and the first one wins.
THE_FIRST_CLAUSE_THAT_MATCHES = """(defn classify
  (sig ((n Int)) -> Int ! pure)
  (ensures (= result (if (= n 0) 7 9)))
  (examples (example (classify 0) => 7) (example (classify 5) => 9))
  (match n
    (0 7)
    (_ 9)))
"""


def test_a_product_against_a_literal_is_proved():
    """Given a function that triples the number 2 and promises its
    answer is 6, when the Owner asks what it owes, then every obligation
    comes back proved."""
    label = "a promise pinning the exact product"
    answer = completed(verify(THE_EXACT_PRODUCT), label)

    assert not not_proved(answer, label), (
        f"WHAT: {not_proved(answer, label)} did not come back proved for a "
        "function that triples 2 and promises 6. "
        "WHY: the promise names the product as a literal, so a translation "
        "that works the product out wrongly cannot agree with itself here -- "
        "which is the whole reason this program is in the oracle. "
        f"HOW: inspect the answer: {answer}"
    )
    assert len(obligations_of(answer, label)) == 4, (
        f"WHAT: this one function owes "
        f"{len(obligations_of(answer, label))} obligations, not the 4 it "
        "declares: its contract, its body, its 1 example and its ending. "
        "WHY: a program that owes fewer than it should would pass the test "
        "above by owing nothing. "
        f"HOW: inspect the answer: {answer}"
    )


def test_the_first_clause_that_matches_decides_the_answer():
    """Given a function matching 0 against a literal clause and then a
    catch-all, and promising the answer the first of them gives, when the
    Owner asks what it owes, then every obligation comes back proved."""
    label = "a match whose first clause wins"
    answer = completed(verify(THE_FIRST_CLAUSE_THAT_MATCHES), label)

    assert not not_proved(answer, label), (
        f"WHAT: {not_proved(answer, label)} did not come back proved for a "
        "function whose promise is exactly what its first matching clause "
        "answers. "
        "WHY: both clauses match 0 and the first wins, so a translation that "
        "tried them in another order answers 9 where this program answers 7 "
        "-- which is the whole reason this program is in the oracle. "
        f"HOW: inspect the answer: {answer}"
    )
    assert len(obligations_of(answer, label)) == 5, (
        f"WHAT: this one function owes "
        f"{len(obligations_of(answer, label))} obligations, not the 5 it "
        "declares: its contract, its body, its 2 examples and its ending. "
        "WHY: a program that owes fewer than it should would pass the test "
        "above by owing nothing. "
        f"HOW: inspect the answer: {answer}"
    )
