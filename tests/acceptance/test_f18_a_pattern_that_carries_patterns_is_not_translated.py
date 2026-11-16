"""Three guards a seventh review round found missing, each demonstrated
by a change to the encoder that no test noticed.

The first is the serious one. A constructor pattern that carries
patterns of its own -- `(Only 0)` rather than `(Only)` -- is outside
what this translation covers, and the encoder refuses it. The refusal is
one condition made of two parts, and reading the `and` between them as
an `or` drops the test on the payload: the obligation is then translated
anyway, with the payload ignored, and comes back `proved` while running
the program over a value the pattern does not match is refused. Nothing
here watched that, because nothing asserted what such a program is
answered at all.

The second: every entry of every answer carries two words from two
closed vocabularies. Reversing the arguments of one call put a whole
sentence where one of the seven execution statuses belongs, and no test
read those fields over an answer about a program outside the fragment.

The third: a disproof names the function to run and the arguments to run
it over. Reversing the arguments of one call made it name the refusal
text as the function, which no caller could run, and nothing asserted
the witness's own fields.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered `unknown` for everything. The second
test requires the obligations that are inside the fragment in these same
programs to come back proved, and the third requires a real disproof.
"""

from __future__ import annotations

import pytest

from _f18_fixtures import (
    EXECUTION_STATUSES,
    LOGICAL_RESULTS,
    completed,
    entry_named,
    evaluate,
    obligations_of,
    results_by_identity,
    verify,
)

# A payload-carrying pattern in each shape the profile allows: a literal
# inside a union variant, a name inside one, a literal inside a record,
# and one constructor pattern inside another.
A_LITERAL_INSIDE_A_VARIANT = """(deftype W (union (Only (w Int))))

(defn f
  (sig ((u W)) -> Int ! pure)
  (ensures (> result 0))
  (examples (example (f (Only 0)) => 7))
  (match u ((Only 0) 7) (_ 0)))
"""

A_NAME_INSIDE_A_VARIANT = """(deftype W (union (Only (w Int))))

(defn f
  (sig ((u W)) -> Int ! pure)
  (ensures (> result 0))
  (examples (example (f (Only 2)) => 7))
  (match u ((Only n) 7) (_ 0)))
"""

A_LITERAL_INSIDE_A_RECORD = """(deftype Box (record (amount Int)))

(defn f
  (sig ((b Box)) -> Int ! pure)
  (ensures (> result 0))
  (examples (example (f (Box 0)) => 7))
  (match b ((Box 0) 7) (_ 0)))
"""

A_PATTERN_INSIDE_A_PATTERN = """(deftype W (union (Only (w Int))))
(deftype Wrapped (record (held W)))

(defn f
  (sig ((v Wrapped)) -> Int ! pure)
  (ensures (> result 0))
  (examples (example (f (Wrapped (Only 0))) => 7))
  (match v ((Wrapped (Only 0)) 7) (_ 0)))
"""

THE_PATTERNS_THAT_CARRY_PATTERNS = (
    (A_LITERAL_INSIDE_A_VARIANT, "a literal inside a union variant"),
    (A_NAME_INSIDE_A_VARIANT, "a name inside a union variant"),
    (A_LITERAL_INSIDE_A_RECORD, "a literal inside a record"),
    (A_PATTERN_INSIDE_A_PATTERN, "a pattern inside a pattern"),
)

# A promise about every whole number that is false of some of them, with
# the example stating a value the function does not answer.
AN_EXAMPLE_THAT_IS_WRONG = """(defn f
  (sig ((x Int)) -> Int ! pure)
  (examples (example (f 1) => 99))
  (+ x 1))
"""

# The programs whose every entry must carry words from the two closed
# vocabularies: one wholly inside the fragment, one outside it for a
# product of two unknown numbers, one outside it for a let binding, and
# one outside it for a pattern carrying a pattern.
A_PROGRAM_INSIDE_THE_FRAGMENT = """(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""

A_PRODUCT_OF_TWO_UNKNOWNS = """(defn product
  (sig ((n Int) (m Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (product 2 3) => 6))
  (* n m))
"""

A_LET_BINDING = """(defn f
  (sig ((n Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (f 1) => 1))
  (let ((m n)) m))
"""


@pytest.mark.parametrize("source,label", THE_PATTERNS_THAT_CARRY_PATTERNS)
def test_a_pattern_carrying_patterns_is_left_unsettled_with_its_reason(
    source, label
):
    """Given a program whose match reads inside a constructor, when the
    Owner asks what it owes, then what the body and the example owe is
    unsettled with the reason, and neither is proved or disproved."""
    answer = completed(verify(source), label)

    for identity in ("body_postcondition:f:body", "example_validity:f:example[0]"):
        entry = entry_named(answer, identity, label)
        assert entry["result"] == "unknown", (
            f"WHAT: with {label}, {identity} is answered "
            f"{entry['result']!r}. "
            "WHY: this translation does not read inside a constructor "
            "pattern, so it must say so rather than settle the obligation; a "
            "tool that dropped the test on the payload would answer proved "
            "here while the program refuses the very input the pattern is "
            "about. "
            f"HOW: inspect the entry: {entry}"
        )
        assert entry["execution_status"] == "unsupported", entry
        assert "pattern" in entry["reason"], (
            f"WHAT: the reason given is {entry['reason']!r}. "
            "WHY: the Owner has to learn which construct was not covered, "
            "not merely that something was not. "
            f"HOW: inspect the entry: {entry}"
        )

    settled = results_by_identity(answer, label)
    assert settled["contract_definedness:f:contract"] == "proved", (
        f"WHAT: nothing at all is settled for {label}: {settled}. "
        "WHY: a rule of core-0 settles the contract and the ending whatever "
        "the body contains; a tool that gave up on the whole program would "
        "pass the test above by settling nothing. "
        f"HOW: inspect the answer: {answer}"
    )
    assert settled["structural_termination:f:calls"] == "proved", settled


@pytest.mark.parametrize(
    "source,label",
    [
        (A_PROGRAM_INSIDE_THE_FRAGMENT, "a program inside the fragment"),
        (A_PRODUCT_OF_TWO_UNKNOWNS, "a product of two unknown numbers"),
        (A_LET_BINDING, "a let binding"),
        (A_LITERAL_INSIDE_A_VARIANT, "a pattern carrying a pattern"),
        (AN_EXAMPLE_THAT_IS_WRONG, "an example stating the wrong value"),
    ],
)
def test_every_entry_carries_one_word_from_each_vocabulary(source, label):
    """Given programs inside and outside the fragment, when the Owner
    reads every entry of the answer, then each carries one of the four
    results and one of the seven execution statuses, and nothing else."""
    answer = completed(verify(source), label)

    for entry in obligations_of(answer, label):
        assert entry["result"] in LOGICAL_RESULTS, (
            f"WHAT: {entry['id']} of {label} stands as {entry['result']!r}, "
            f"which is not one of {sorted(LOGICAL_RESULTS)}. "
            "WHY: SPEC.md fixes the four words a logical result may carry; a "
            "word outside them cannot be read by any client. "
            f"HOW: inspect the entry: {entry}"
        )
        assert entry["execution_status"] in EXECUTION_STATUSES, (
            f"WHAT: {entry['id']} of {label} reports the attempt as "
            f"{entry['execution_status']!r}, which is not one of "
            f"{sorted(EXECUTION_STATUSES)}. "
            "WHY: SPEC.md fixes the seven words an execution status may "
            "carry; a sentence there is not a status a client can branch on. "
            f"HOW: inspect the entry: {entry}"
        )


def test_a_disproof_names_a_function_a_caller_can_run():
    """Given a program whose declared example states a value the
    function does not answer, when the Owner reads the disproof, then it
    names that function, the arguments to run it over, and what the
    program really answers -- and running it over them is refused."""
    label = "an example stating the wrong value"
    entry = entry_named(
        completed(verify(AN_EXAMPLE_THAT_IS_WRONG), label),
        "example_validity:f:example[0]",
        label,
    )

    assert entry["result"] == "disproved", entry
    witness = entry["counterexample"]
    assert witness["function"] == "f", (
        f"WHAT: the disproof names {witness['function']!r} as the function to "
        "run. "
        "WHY: the Owner is sent to run it; a name the program does not "
        "declare sends them nowhere, and no caller could reproduce the "
        f"defect. HOW: inspect the witness: {witness}"
    )
    assert witness["arguments"] == ["1"], (
        f"WHAT: the disproof names {witness['arguments']} as the arguments. "
        "WHY: the example is declared at 1, and that is the input that shows "
        f"the defect. HOW: inspect the witness: {witness}"
    )
    assert "99" in witness["refused_when_run"], (
        f"WHAT: the refusal reads {witness['refused_when_run']!r} and does "
        "not name the value the example states. "
        "WHY: the Owner has to see what was expected beside what was "
        f"answered. HOW: inspect the witness: {witness}"
    )

    replayed = evaluate(AN_EXAMPLE_THAT_IS_WRONG, witness["function"], witness["arguments"])
    assert (replayed.get("result") or {}).get("value") == "2", (
        f"WHAT: running the function the disproof names over the arguments "
        f"it names answers {replayed.get('result')}. "
        "WHY: a witness that cannot be run, or that answers what the example "
        "states, is not a counterexample. "
        f"HOW: inspect the run: {replayed}"
    )
