# F21 — the oracle: one word for the whole program

This is the first step. Nothing of the feature is built yet. What exists
now is the set of tests that say what "done" means, and the ones that
state new behaviour all fail today. A check nobody has seen fail is not
evidence.

## What was audited before anything was written

The Owner asked for F19, F20 and F21 to be audited against what F18
already delivers, so that nothing is built twice. Each criterion below was
read against the code that answers it and against the test that observes
it; "observed how" names a test that runs today on this branch.

| Criterion | Delivered by F18 where | Observed how | Remaining |
|---|---|---|---|
| F19.1 an obligation needing the product of two unknown integers is `unknown` with the fragment as its reason | `encoding._product` declines it; `discharge._finding_for` turns a declined claim into `unknown` beside `unsupported` | `tests/acceptance/test_verify_lists_the_obligations_owed.py::test_an_obligation_the_tool_cannot_settle_claims_nothing`; `tests/acceptance/test_f18_the_answer_says_what_settled_each_entry.py::test_a_program_outside_the_fragment_is_answered_without_a_disclosure` | nothing |
| F19.2 a controlled solver timeout is `unknown` with a timed-out status, not `disproved` | `solving.could_not_tell`, and `PinnedZ3.asked` when the run has no time left | `tests/unit/test_f18_a_solver_verdict_becomes_a_finding.py::test_a_solver_that_runs_out_of_time_settles_nothing`, `::test_the_solver_is_never_given_more_time_than_the_run_has` | nothing |
| F19.3 a solver that fails to run is a tool failure and the program is not accepted | half of it: `discharge._asked_about` answers `unknown` beside `tool_failure` for every obligation that needed the solver | `tests/unit/test_f18_a_solver_verdict_becomes_a_finding.py::test_a_solver_that_cannot_be_loaded_is_a_failure_of_this_tool` | the other half. Nothing in an answer says the program was not accepted, and the failure had never been forced through the command itself |
| F19.4 a mix of in-fragment and out-of-fragment obligations is not verified, and the in-fragment results stay visible | the visible half: every obligation is listed with its own result | `tests/acceptance/test_verify_lists_the_obligations_owed.py::test_an_obligation_the_tool_cannot_settle_claims_nothing` | the aggregate |
| F19.5 multiplication by a literal constant is inside the fragment and gets a real result | `encoding._product` keeps a product with a literal operand | `tests/acceptance/test_f18_a_negative_factor_keeps_its_sign.py` | nothing |
| F20.1 a false postcondition is `disproved` with concrete argument values | `Finding.disproved_with`, `ValidatedWitness.published` | `tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py` | nothing |
| F20.2 the witness replays: the precondition holds and the postcondition fails | `discharge._validated` and `_if_confirmed` run the candidate through the evaluator | `tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py` | nothing |
| F20.3 a candidate that does not replay is `unknown`, not `disproved` | `discharge._candidate` | `tests/acceptance/test_f18_a_replay_that_runs_out_of_depth_is_not_a_disproof.py`; `tests/unit/test_f18_a_solver_verdict_becomes_a_finding.py::test_a_candidate_the_program_does_not_refuse_is_not_a_disproof` | nothing |
| F20.4 the replay happened inside a declared budget and the budget is stated | the bound: the replay runs inside `evaluator.EVALUATION_LIMIT`, which `discover` publishes under `resource_limits` | `tests/acceptance/test_f18_a_replay_that_runs_out_of_depth_is_not_a_disproof.py` | the statement: a reader looking at a counterexample is not told which budget the confirming run stood inside |
| F20.5 the reservation example unmodified produces no witness | every obligation of it is proved, and only a disproof can carry a witness | `tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py`; this change adds the direct observation, which passes today | nothing |
| F21.1 a fully discharged program with passing examples is verified, with its inventory | — | — | all of it |
| F21.2 one `unknown` obligation means not verified | — | — | all of it |
| F21.3 one failing example means not verified even if every obligation is proved | — | — | all of it |
| F21.4 an unsupported function does not remove obligations for the rest | the obligations of the rest are listed and settled | `tests/acceptance/test_verify_lists_the_obligations_owed.py` | the aggregate over them |
| F21.5 structurally discharged checks are distinguishable from solver-discharged ones | `discharged_by` carries `solver` or `structure` on every proved entry | `tests/acceptance/test_f18_the_answer_says_what_settled_each_entry.py::test_an_entry_says_whether_a_solver_or_a_rule_settled_it` | nothing for an entry; the aggregate counts the two apart as well |

So the work is: the aggregate, the second half of F19.3, and the
statement half of F20.4. Nothing else is built again.

## What the feature promises

| | Promise |
|---|---|
| P1 | A completed `verify` answer says in one word whether the whole program was shown, and says `verified` only when every obligation is discharged, every declared example passes and the static checks passed. |
| P2 | An obligation that is not discharged withholds the word and is named, and the obligations of the rest of the program keep their own results. |
| P3 | A declared example that does not pass withholds the word and is named; the examples are run, not read off the obligations. |
| P4 | A solver that cannot run leaves the program unaccepted and says the attempt failed in this tool, not in the program. |
| P5 | The aggregate counts what a rule of core-0 settled apart from what a solver answered. |
| P6 | A counterexample says which declared budget the run that confirmed it stood inside. |
| P7 | The word and everything it rests on are described in the manifest before a client sends a request. |

A program the static checks refuse gets no aggregate at all. That is part
of P1 rather than a promise of its own: it is already true today, because
there is no aggregate at all, and the observation added for it passes
now. It is kept as regression evidence.

## The conflicts, and what they need from the Owner

Two existing tests forbid the word this feature has to say. Neither has
been edited; both are reported here first.

1. `tests/unit/test_service_discover.py::test_discover_makes_no_verification_or_build_claim`
   forbids `verified`, `built` and `holds` anywhere in the manifest. The
   manifest has to describe the new field, so it has to use the word. F18
   met exactly this and re-aimed the same test for `proved`: the word is
   allowed only where the fields that justify it are published. The same
   re-aim fits here.
2. `tests/acceptance/test_i1_int_checked_evaluator_end_to_end.py`
   scans every answer of a whole session — which includes a `verify`
   answer — for the same three words, and already carries F18's re-aim
   for `proved` beside it ("a response says an obligation is proved and
   does not say what that rests on"). The same shape fits the aggregate.

A third question is not about a test but about what the Owner will read.
F19 criterion 3 says "the answer is a tool failure". Today a `verify`
answer whose solver could not load has status `completed` and says so per
obligation, and the manifest publishes that behaviour in writing. The
recommendation is to read the criterion as the aggregate's own execution
status rather than as the answer's status.

## The tests

Four files state the new behaviour, and all of them drive the real
`prova` command over its JSON surface, except the table, which is the
soundness-critical part and is read as a pure function.

- `tests/acceptance/test_f21_the_word_verified_covers_the_whole_program.py`
- `tests/acceptance/test_f19_a_solver_that_cannot_run_leaves_the_program_unaccepted.py`
- `tests/acceptance/test_f20_a_witness_says_the_budget_it_replayed_inside.py`
- `tests/properties/test_f21_aggregate_laws.py`
- `tests/unit/test_f21_the_aggregate_is_one_closed_table.py`

The table in the unit file is written out by hand from the criteria and
from SPEC.md, eleven rows of it, before any of the code existed. A table
copied from what the tool answers would agree with the tool however wrong
both were.

The solver that cannot run is forced from outside with no hook inside the
tool: a module named `z3` that refuses to be imported is put first on the
path of the command's own process, and the test reads the answer's own
entries to confirm that this is what happened, with a control run that
comes back verified.

Two of the observations added here pass already. They are the two rows of
the audit that F18 delivered and that nothing had yet observed directly:
a refused program carries no aggregate and never says the word, and the
unmodified reservation example offers no witness. They are kept as
regression evidence and are not counted as work this change does.

## What is still open

- The three conflicts above are the Owner's to settle.
- Running the declared examples inside `verify` is new work for that
  operation. A program too deep to run its examples within the evaluation
  budget must not turn the inventory into a refusal; it is one input to
  the aggregate, which is then not verified for that reason.
- Whether the aggregate belongs beside `trust` at the top of the answer
  or inside `result` is a design question, taken at the design step.
