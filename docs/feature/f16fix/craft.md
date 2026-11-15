# F16fix - what was built, and what it costs

## What changed

| File | Change |
|---|---|
| `src/prova/obligations.py` | a call in a postcondition or a body is reached under the function's own precondition; a call inside the precondition still under nothing |
| `tests/properties/test_obligation_inventory_laws.py` | the plan places a call in every position a body can hold, derives the expected condition from the plan's own precondition, and reads the ending entry's call count |
| `tests/acceptance/test_verify_lists_the_obligations_owed.py` | the nested-condition program, the call-count case, and the chain of preconditions the review described |

The three commits, in order:

1. the tests that were not looking (findings 1 to 3) - no production change;
2. the three tests whose expected condition had to change - **red on its own**,
   and its message says so;
3. the rule itself, with the chain case that reads it.

## The ten deletions, and the test each one now fails

Each deletion was applied to the file, the obligation tests were run, and the
file was put back. After every run the file is byte-identical to its committed
form. The first nine are the ones the review measured as surviving; the tenth
removes the rule this delivery adds.

| Deletion | Now fails |
|---|---|
| the else arm of an `if` is not walked | `test_a_call_in_every_position_a_body_can_hold_owes_its_entry`, `test_a_call_behind_several_conditions_is_owed_under_all_of_them`, `test_the_ending_entry_says_how_many_calls_the_function_makes` |
| a `let` binding is not walked | `test_a_call_in_every_position...`, `test_every_function_example_and_call_owes_its_entry` |
| the target of a field read is not walked | the same two |
| the scrutinee of a `match` is not walked | the same two |
| the condition of an `if` is not walked | `test_a_call_in_every_position...` |
| the earlier match clauses are not negated | `test_a_call_behind_several_conditions...` |
| every pattern is treated as one that can fail | `test_a_call_behind_several_conditions...` |
| a condition prints only its first clause | `test_a_call_behind_several_conditions...`, `test_a_call_in_a_contract_or_a_body_is_owed_under_the_functions_own_precondition`, `test_every_function...`, `test_putting_a_call_out_of_reach_keeps_what_it_owes` |
| the ending entry counts no call | `test_a_call_in_every_position...`, `test_every_function...`, `test_the_ending_entry...` |
| **a body is reached without the function's own precondition** | `test_a_call_in_a_contract_or_a_body_is_owed_under_the_functions_own_precondition`, `test_each_call_owes_its_precondition_under_the_condition_that_reaches_it`, `test_every_function...`, `test_putting_a_call_out_of_reach_keeps_what_it_owes` |

Ten of ten die. The script that does this lives under the run workspace and is
not committed.

## Decisions

**No formal model, no Quint.** The inventory keeps no state, runs no protocol,
spawns nothing and writes no file. It is a pure function from one syntax tree
to one list, so a state model would restate the code.

**The conflict went to the Owner before anything was edited.** Three tests
stated the old condition. The measurement went up with one question; the Owner
decided they may be rewritten to the new text and nothing else in them. Those
three edits are their own commit, so what each test now states can be read
without the code that satisfies it.

**Jev was not consulted.** `TYPESAFE_API_KEY` is absent from this environment
and the client exits 3. Every choice was made locally, from measured runs.

## What it costs

Whole suite after the change: **1011 passed, 0 failed, 100 s**. Before the
delivery: 1007 passed, 0 failed, 110 s. Four tests were added.

The two changed files were then run nine times in a row. All nine passed with
the same 14 tests:

| | pytest | wall clock |
|---|---|---|
| median of 9 runs | 4.89 s | 4.99 s |
| slowest of 9 runs | 4.91 s | 5.02 s |

No run failed, so nothing here is flaky at nine runs. Each of these tests
starts the `prova` command as a separate process, so they are integration tests
and are measured in seconds, not in the 10 ms a unit test gets. The slowest
single test is a generated one at about 1.1 s.

The repository ships no linter and no type checker. The mechanical check run
beside the suite is that every module compiles, which it does, on this tree and
on the tree before the change.

## Not measured

- Whether a deletion other than the ten re-run here would go unnoticed. Ten
  deletions were re-run; this is not a whole mutation sweep.
- Whether the condition now reported is the one a solver would need. Nothing
  attempts an obligation: every entry is still `not_attempted`.
- Path conditions still name let-bound values whose definition is in no entry.
  That belongs to another delivery and was left alone.
