"""What each verdict a solver can give becomes, read at the seam the
design declares: `Discharge(program, solver, run)`.

Added after an independent review. Three of the four verdicts cannot be
reached from outside with a real solver: a solver that runs out of time,
a solver that answers it cannot tell, and a solver that cannot be loaded
at all. Nothing exercised them, so a tool that called a timed-out query
proved, or read "cannot tell" as "nothing refutes it", would have passed
the whole suite.

The solver here is a stub standing in for the one driven port of this
unit, and it answers one verdict per test. It is not a mock of the
decision under test: what each verdict becomes is exactly what is being
read.

This is a unit test and reaches the public contract of a module the
package does not export, which the test mandates allow for a unit test;
the acceptance tests beside it drive the command itself.
"""

from __future__ import annotations

from dataclasses import dataclass

from prova import discharge, obligations, solving, syntax
from prova.budgets import Budgets
from prova.reader import read_program

A_PROGRAM = """(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""

# The obligation every test below reads: the one the solver is asked
# about, as against the two a rule of core-0 settles without one.
THE_ONE_A_SOLVER_IS_ASKED_ABOUT = "body_postcondition:twice:body"


@dataclass
class ASolverThatAnswers:
    """The one driven port of this unit, answering the verdict it was
    built with and recording the time it was given."""

    verdict: object
    given: list

    def name(self) -> str:
        return "a stub solver"

    def version(self) -> str:
        return "0"

    def asked(self, claim, milliseconds_left: int):
        self.given.append(milliseconds_left)
        return self.verdict


def _settled(verdict) -> tuple[dict, ASolverThatAnswers]:
    program = syntax.parse_program(read_program(A_PROGRAM))
    owed = obligations.inventory_for(program)
    solver = ASolverThatAnswers(verdict, [])
    settlement = discharge.Discharge(
        program, solver, Budgets.declared().start()
    ).settle(owed)
    return settlement.inventory_of(owed), solver


def _the_entry(inventory: dict) -> dict:
    for entry in inventory["obligations"]:
        if entry["id"] == THE_ONE_A_SOLVER_IS_ASKED_ABOUT:
            return entry
    raise AssertionError(
        f"WHAT: no entry {THE_ONE_A_SOLVER_IS_ASKED_ABOUT!r} in "
        f"{[e['id'] for e in inventory['obligations']]}. "
        "WHY: this test reads what became of that obligation. "
        "HOW: inspect the inventory."
    )


def test_a_solver_that_refutes_nothing_settles_the_obligation():
    """Given a solver answering that the denial of the claim has no
    solution, then the obligation is proved, its attempt completed, and
    the solver is named as what settled it."""
    entry = _the_entry(_settled(solving.Unrefutable())[0])

    assert (entry["result"], entry["execution_status"]) == ("proved", "completed"), (
        f"WHAT: a claim whose denial has no solution is answered {entry}. "
        "WHY: that is what validity is, and SPEC.md lines 275-277 let only a "
        "completed justified result be proved. "
        "HOW: map an unrefutable denial to proved beside completed."
    )
    assert entry["discharged_by"] == "solver", entry


def test_a_solver_that_runs_out_of_time_settles_nothing():
    """Given a solver answering that it could not tell because it ran
    out of time, then the obligation is unknown with the time named, and
    it is neither proved nor disproved."""
    entry = _the_entry(
        _settled(solving.Undecided("the solver ran out of time", "timed_out"))[0]
    )

    assert entry["result"] == "unknown", (
        f"WHAT: a query that ran out of time is answered {entry['result']!r}. "
        "WHY: SPEC.md says an interrupted or timed-out proof is unknown with "
        "its execution reason retained; reading it as proved would be the "
        "worst defect this tool can have, and reading it as disproved would "
        "report a counterexample nobody found. "
        f"HOW: inspect the entry: {entry}"
    )
    assert entry["execution_status"] == "timed_out", entry
    assert entry["reason"].strip() and "counterexample" not in entry, entry


def test_a_solver_that_cannot_tell_settles_nothing():
    """Given a solver answering that it could not tell, for a reason of
    its own, then the obligation is unknown with that reason and its
    attempt is reported as completed."""
    entry = _the_entry(
        _settled(solving.Undecided("the solver said incomplete", "completed"))[0]
    )

    assert (entry["result"], entry["execution_status"]) == ("unknown", "completed"), (
        f"WHAT: a solver that could not tell is answered {entry}. "
        "WHY: 'nothing refutes it' and 'I cannot tell' are different "
        "answers; reading the second as the first would prove a claim no "
        "search settled. "
        "HOW: map an undecided verdict to unknown, never to proved."
    )
    assert "incomplete" in entry["reason"], entry


def test_a_solver_that_cannot_be_loaded_is_a_failure_of_this_tool():
    """Given a solver that could not be loaded, then the obligation is
    unknown, the failure is reported as this tool's own, and the counts
    do not call it settled."""
    inventory, _ = _settled(
        solving.SolverUnavailable("the solver could not be loaded here")
    )
    entry = _the_entry(inventory)

    assert (entry["result"], entry["execution_status"]) == (
        "unknown",
        "tool_failure",
    ), (
        f"WHAT: an obligation nothing could be asked about is answered "
        f"{entry}. "
        "WHY: SPEC.md keeps tool failures apart from semantic outcomes; a "
        "missing solver is a failure of this installation and not a "
        "statement about the program. "
        "HOW: map an unavailable solver to unknown beside tool_failure."
    )
    assert "could not be loaded" in entry["reason"], entry
    note = inventory["note"]
    assert note.startswith("2 of the 4 obligations"), (
        f"WHAT: the note says {note!r} for an answer whose 2 solver "
        "obligations could not be attempted at all. "
        "WHY: only the 2 a rule of core-0 settles were settled here; a note "
        "counting the other 2 as settled would say work was done that was "
        "not. "
        "HOW: count what was settled, not what was reached for."
    )
    assert inventory["totals"]["by_result"] == {"proved": 2, "unknown": 2}, (
        f"WHAT: the counts say {inventory['totals']['by_result']}. "
        "WHY: a reader of the summary alone must read the same verdict as a "
        "reader of the entries. "
        "HOW: count each entry under the word it carries."
    )


def test_a_candidate_the_program_does_not_refuse_is_not_a_disproof():
    """Given a solver answering that the denial of the claim has a
    solution at an input the program answers happily, then the
    obligation is unknown with its attempt completed and no
    counterexample."""
    entry = _the_entry(
        _settled(solving.Refuted((("n", "3"),)))[0]
    )

    assert (entry["result"], entry["execution_status"]) == ("unknown", "completed"), (
        f"WHAT: a candidate the program does not refuse is answered {entry}. "
        "WHY: SPEC.md requires a validated source-level witness for a "
        "disproof and says a failed validation yields unknown; twice(3) "
        "answers 6 and keeps its promise, so 3 refutes nothing. "
        "HOW: replay every candidate before calling anything disproved."
    )
    assert "counterexample" not in entry, entry


def test_a_candidate_the_program_refuses_is_a_disproof():
    """Given a solver answering with an input the program really refuses
    for this obligation, then the obligation is disproved and the answer
    carries that input."""
    broken = """(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (> n 0))
  (ensures (> result 10))
  (examples (example (twice 2) => 4))
  (* n 2))
"""
    program = syntax.parse_program(read_program(broken))
    owed = obligations.inventory_for(program)
    settlement = discharge.Discharge(
        program,
        ASolverThatAnswers(solving.Refuted((("n", "1"),)), []),
        Budgets.declared().start(),
    ).settle(owed)
    entry = _the_entry(settlement.inventory_of(owed))

    assert entry["result"] == "disproved", (
        f"WHAT: an input the program refuses for this very promise is "
        f"answered {entry['result']!r}. "
        "WHY: twice(1) answers 2, which is not above 10, so the evaluator "
        "refuses it for the postcondition this obligation is about -- a "
        "witness that replays, which is what a disproof needs. "
        f"HOW: inspect the entry: {entry}"
    )
    assert entry["counterexample"]["arguments"] == ["1"], entry


def test_the_solver_is_never_given_more_time_than_the_run_has():
    """Given a run under the budgets this tool declares, then every
    question put to the solver is given no more milliseconds than the
    whole run may take."""
    _, solver = _settled(solving.Unrefutable())

    assert solver.given, "no question was put to the solver at all"
    assert max(solver.given) <= 10_000, (
        f"WHAT: a question was given {max(solver.given)} milliseconds and "
        "the run may take 10000 in all. "
        "WHY: the time budget bounds the solver, so a query can never "
        "outlive the run that asked it. "
        f"HOW: inspect what was given: {solver.given}"
    )
