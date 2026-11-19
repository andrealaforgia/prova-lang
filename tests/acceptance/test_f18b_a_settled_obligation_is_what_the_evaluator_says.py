"""F18b -- the evaluator is the authority over every word 'verify' takes.

SPEC.md, "Results and evidence scope": only a completed justified result
may be `proved`, and a disproof needs a source-level witness that really
replays against the reference semantics. The reference semantics is the
evaluator this tool ships, which the `evaluate` operation runs. So for
every program below the two operations are asked, and the word the
inventory carries must be the word a run of the program supports: a
`proved` no run contradicts, a `disproved` whose witness the run really
refuses for that very obligation, and no answer that ends the tool.

One table, eight programs, each a shape where the two can disagree:

  1 an example whose function breaks its own promise over it,
  2 a contract clause that calls a partial function,
  3 a call behind `and`, which short-circuit never reaches,
  4 a contract clause guarded by the clause written before it,
  5 a clause of a `match` standing after a catch-all,
  6 a function of no arguments whose witness is the empty tuple,
  7 a witness carrying more digits than this tool writes,
  8 a program whose translation nests deeper than this tool walks.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered every obligation 'unknown'. Rows 1, 2
and 6 require the word 'disproved' and rows 3, 4 and 5 require 'proved',
so an inventory of nothing but 'unknown' fails six of the eight rows.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pytest

from _f18_fixtures import completed, entry_named, evaluate, verify

# The two helpers rows 3 and 5 share: one refuses a number that is not
# positive and answers false, the other refuses the same and answers
# true. Neither is ever reached by the programs that call them second.
A_FALSE_HELPER_AND_A_TRUE_ONE = """(defn g
  (sig ((x Int)) -> Bool ! pure)
  (requires (> x 0))
  (examples (example (g 1) => false))
  false)

(defn h
  (sig ((x Int)) -> Bool ! pure)
  (requires (> x 0))
  (examples (example (h 1) => true))
  true)
"""

# A function whose answer breaks its own postcondition over the very
# arguments its declared example states.
AN_EXAMPLE_ITS_FUNCTION_REFUSES = """(defn f
  (sig ((x Int)) -> Int ! pure)
  (ensures (> result 0))
  (examples (example (f 0) => 0))
  x)
"""

# A precondition that calls a function which does not accept every
# number: the contract itself cannot be run at 0.
A_CONTRACT_THAT_CALLS_A_PARTIAL_FUNCTION = """(defn g
  (sig ((x Int)) -> Bool ! pure)
  (requires (> x 0))
  (examples (example (g 1) => true))
  true)

(defn f
  (sig ((x Int)) -> Int ! pure)
  (requires (g x))
  (examples (example (f 1) => 1))
  x)
"""

# The second operand of an `and` whose first operand never lets it run.
A_CALL_BEHIND_AN_AND = A_FALSE_HELPER_AND_A_TRUE_ONE + """
(defn f
  (sig ((x Int)) -> Bool ! pure)
  (examples (example (f 1) => false))
  (and (g x) (h x)))
"""

# A second contract clause that only runs where the first one held.
A_CONTRACT_CLAUSE_GUARDED_BY_THE_ONE_BEFORE_IT = """(defn g
  (sig ((x Int)) -> Bool ! pure)
  (requires (> x 0))
  (examples (example (g 1) => true))
  true)

(defn f
  (sig ((x Int)) -> Int ! pure)
  (requires (> x 0) (g x))
  (examples (example (f 1) => 1))
  x)
"""

# A clause written after a catch-all, which no value reaches.
A_CLAUSE_AFTER_A_CATCH_ALL = A_FALSE_HELPER_AND_A_TRUE_ONE + """
(defn f
  (sig ((x Int)) -> Bool ! pure)
  (examples (example (f 1) => false))
  (match x (_ (g x)) (0 (h x))))
"""

# A function of no arguments that breaks its own promise.
A_FUNCTION_OF_NO_ARGUMENTS = """(defn f
  (sig () -> Int ! pure)
  (ensures (> result 0))
  (examples (example (f) => 0))
  0)
"""


def _a_postcondition_no_witness_can_be_written_for() -> str:
    """A program whose only counterexample is a number longer than this
    tool writes: five literals of a thousand digits multiplied together
    bound the result, so the smallest value above the bound has five
    thousand digits. Every literal in the text meets the published
    reading limit.
    """
    thousand_digits = "9" * 1000
    bound = thousand_digits
    for _ in range(4):
        bound = f"(* {thousand_digits} {bound})"
    return (
        "(defn f\n"
        "  (sig ((x Int)) -> Int ! pure)\n"
        f"  (ensures (<= result {bound}))\n"
        "  (examples (example (f 0) => 0))\n"
        "  x)\n"
    )


def _a_chain_that_nests_deeper_than_the_tool_walks() -> str:
    """Twenty-one functions, each calling the one before it inside twenty
    nested additions. Twenty-one calls stand far below the expansion
    bound this tool declares, and the expression they expand into nests
    far above the depth it walks.
    """
    written = [
        "(defn f0\n"
        "  (sig ((x Int)) -> Int ! pure)\n"
        "  (examples (example (f0 0) => 0))\n"
        "  x)\n"
    ]
    for step in range(1, 21):
        body = f"(f{step - 1} x)"
        for _ in range(20):
            body = f"(+ 0 {body})"
        written.append(
            f"(defn f{step}\n"
            "  (sig ((x Int)) -> Int ! pure)\n"
            "  (ensures (= result x))\n"
            f"  (examples (example (f{step} 0) => 0))\n"
            f"  {body})\n"
        )
    return "\n".join(written)


A_WITNESS_TOO_LONG_TO_WRITE = _a_postcondition_no_witness_can_be_written_for()
A_TRANSLATION_THAT_NESTS_TOO_DEEP = _a_chain_that_nests_deeper_than_the_tool_walks()


@dataclass(frozen=True)
class ARun:
    """One run of the program over values written the way a program
    writes them, and what the Owner is told it did."""

    function: str
    arguments: tuple[str, ...]
    status: str
    says: str

    def observed(self, source: str, about: str) -> None:
        answer = evaluate(source, self.function, list(self.arguments))
        assert answer.get("status") == self.status, (
            f"WHAT: running {self.function}{list(self.arguments)} of {about} "
            f"has status {answer.get('status')!r} and this row stands on "
            f"{self.status!r}. "
            "WHY: the row below reads the evaluator as the authority over "
            "the word the inventory carries; a run that did something else "
            "settles nothing. "
            f"HOW: inspect the answer: {answer}"
        )
        written = str(answer.get("result")) + str(answer.get("diagnostics"))
        assert self.says in written, (
            f"WHAT: running {self.function}{list(self.arguments)} of {about} "
            f"does not say {self.says!r}. "
            "WHY: this row is about what the reference semantics really "
            "does with that input; the assertion below means nothing if it "
            "does something else. "
            f"HOW: inspect the answer: {answer}"
        )


@dataclass(frozen=True)
class ACase:
    """One program, one obligation of it, the word the evaluator forces
    on that obligation, and the runs that force it."""

    about: str
    source: str
    identity: str
    result: str
    because: str
    runs: tuple[ARun, ...] = field(default=())


THE_EVALUATOR_FORCES = (
    ACase(
        about="an example its own function refuses",
        source=AN_EXAMPLE_ITS_FUNCTION_REFUSES,
        identity="example_validity:f:example[0]",
        result="disproved",
        because=(
            "running f over the arguments the example states breaks the "
            "postcondition, so the example is not a valid example of f"
        ),
        runs=(
            ARun("f", ("0",), "completed", "postcondition violated calling 'f'"),
        ),
    ),
    ACase(
        about="a contract that calls a partial function",
        source=A_CONTRACT_THAT_CALLS_A_PARTIAL_FUNCTION,
        identity="contract_definedness:f:contract",
        result="disproved",
        because=(
            "the precondition of f calls g, and at 0 that call is refused, "
            "so the contract of f is not defined for every typed input"
        ),
        runs=(
            ARun("f", ("0",), "completed", "precondition violated calling 'g'"),
        ),
    ),
    ACase(
        about="a call behind an and that never reaches it",
        source=A_CALL_BEHIND_AN_AND,
        identity="call_precondition:f:body/arg[1]",
        result="proved",
        because=(
            "the first operand refuses or answers false, so h is never "
            "called at all and no input reaches its precondition"
        ),
        runs=(
            ARun("f", ("1",), "completed", "false"),
            ARun("f", ("0",), "completed", "precondition violated calling 'g'"),
        ),
    ),
    ACase(
        about="a contract clause guarded by the clause before it",
        source=A_CONTRACT_CLAUSE_GUARDED_BY_THE_ONE_BEFORE_IT,
        identity="call_precondition:f:requires[1]",
        result="proved",
        because=(
            "the first clause is checked first and refuses every number "
            "that is not positive, so every input reaching g is positive"
        ),
        runs=(
            ARun("f", ("1",), "completed", "1"),
            ARun("f", ("0",), "completed", "precondition violated calling 'f'"),
        ),
    ),
    ACase(
        about="a clause standing after a catch-all",
        source=A_CLAUSE_AFTER_A_CATCH_ALL,
        identity="call_precondition:f:body/case[1]",
        result="proved",
        because=(
            "the catch-all takes every value, so the clause after it is "
            "never taken and h is never called"
        ),
        runs=(
            ARun("f", ("1",), "completed", "false"),
            ARun("f", ("0",), "completed", "precondition violated calling 'g'"),
        ),
    ),
    ACase(
        about="a function of no arguments that breaks its promise",
        source=A_FUNCTION_OF_NO_ARGUMENTS,
        identity="body_postcondition:f:body",
        result="disproved",
        because=(
            "running f with no arguments at all breaks its postcondition, "
            "and the empty argument tuple is a witness like any other"
        ),
        runs=(
            ARun("f", (), "completed", "postcondition violated calling 'f'"),
        ),
    ),
    ACase(
        about="a witness carrying more digits than this tool writes",
        source=A_WITNESS_TOO_LONG_TO_WRITE,
        identity="body_postcondition:f:body",
        result="unknown",
        because=(
            "the only counterexample is a number this tool will not write, "
            "so the obligation is left unsettled and the program itself is "
            "answered as usual"
        ),
        runs=(ARun("f", ("0",), "completed", "0"),),
    ),
    ACase(
        about="a translation that nests deeper than this tool walks",
        source=A_TRANSLATION_THAT_NESTS_TOO_DEEP,
        identity="body_postcondition:f20:body",
        result="unknown",
        because=(
            "expanding the calls of this obligation nests deeper than this "
            "tool walks, which is a bound it declares and not a statement "
            "about the program"
        ),
        runs=(
            ARun("f20", ("0",), "resource_exhausted", "evaluation_depth_exceeded"),
        ),
    ),
)


@pytest.mark.parametrize(
    "case", THE_EVALUATOR_FORCES, ids=[case.about for case in THE_EVALUATOR_FORCES]
)
def test_the_inventory_carries_the_word_the_evaluator_supports(case: ACase):
    """Given a program where the inventory and a run of the program can
    disagree, when the Owner asks what the program owes and runs it over
    the inputs that matter, then the obligation carries the word the run
    supports and the answer still lists the whole inventory."""
    for run in case.runs:
        run.observed(case.source, case.about)

    entry = entry_named(completed(verify(case.source), case.about), case.identity, case.about)

    assert entry["result"] == case.result, (
        f"WHAT: {case.identity} of {case.about} is answered "
        f"{entry['result']!r} and the evaluator supports {case.result!r}: "
        f"{case.because}. "
        "WHY: SPEC.md lets only a justified result carry 'proved' and only "
        "a witness the reference semantics refuses carry 'disproved'; a "
        "word the evaluator does not support is a wrong answer about a "
        "program, which is the one thing this tool may never give. "
        f"HOW: inspect the entry: {entry}"
    )


@pytest.mark.parametrize(
    "case", THE_EVALUATOR_FORCES, ids=[case.about for case in THE_EVALUATOR_FORCES]
)
def test_a_disproved_obligation_names_the_refusal_that_confirms_it(case: ACase):
    """Given the same programs, when an obligation of one comes back
    disproved, then it carries a counterexample saying which input it
    was confirmed over and what the run refused."""
    entry = entry_named(completed(verify(case.source), case.about), case.identity, case.about)
    if entry["result"] != "disproved":
        pytest.skip(f"{case.identity} is {entry['result']!r}, not a disproof")

    counterexample = entry.get("counterexample")
    assert counterexample is not None, (
        f"WHAT: {case.identity} of {case.about} is disproved and carries no "
        "counterexample. "
        "WHY: SPEC.md lets a disproof carry only a validated witness; a "
        "disproof with nothing beside it cannot be checked by anyone. "
        f"HOW: inspect the entry: {entry}"
    )
    assert "refused_when_run" in counterexample, (
        f"WHAT: the counterexample of {case.identity} does not say what the "
        f"run refused: {counterexample}. "
        "WHY: the refusal is what turns a solution the solver found into a "
        "counterexample. "
        "HOW: inspect the entry."
    )
