# F16fix - what was built, and what it costs

## What changed

Two test files, and nothing else:

| File | Change |
|---|---|
| `tests/properties/test_obligation_inventory_laws.py` | the plan places a call in every position a body can hold; one program holds all of them at once; the ending entry's call count is read |
| `tests/acceptance/test_verify_lists_the_obligations_owed.py` | a program whose calls sit behind three match clauses and an `if` inside a `let`, read for the whole joined condition and for the calls each function makes |

`src/prova/obligations.py` is untouched. The walk over a body already visited
every position; only the tests were short-sighted. A delivery that closes a
hole in the tests does not need to move the product.

## The nine deletions, and the test each one now fails

Each deletion was applied to the file, the obligation tests were run, and the
file was put back. After every run the file is byte-identical to its committed
form.

| Deletion | Now fails |
|---|---|
| the else arm of an `if` is not walked | `test_a_call_in_every_position_a_body_can_hold_owes_its_entry`, `test_a_call_behind_several_conditions_is_owed_under_all_of_them`, `test_the_ending_entry_says_how_many_calls_the_function_makes` |
| a `let` binding is not walked | `test_a_call_in_every_position_a_body_can_hold_owes_its_entry`, `test_every_function_example_and_call_owes_its_entry` |
| the target of a field read is not walked | `test_a_call_in_every_position_a_body_can_hold_owes_its_entry`, `test_every_function_example_and_call_owes_its_entry` |
| the scrutinee of a `match` is not walked | `test_a_call_in_every_position_a_body_can_hold_owes_its_entry`, `test_every_function_example_and_call_owes_its_entry` |
| the condition of an `if` is not walked | `test_a_call_in_every_position_a_body_can_hold_owes_its_entry` |
| the earlier match clauses are not negated | `test_a_call_behind_several_conditions_is_owed_under_all_of_them` |
| every pattern is treated as one that can fail | `test_a_call_behind_several_conditions_is_owed_under_all_of_them` |
| a condition prints only its first clause | `test_a_call_behind_several_conditions_is_owed_under_all_of_them` |
| the ending entry counts no call | `test_a_call_in_every_position_a_body_can_hold_owes_its_entry`, `test_every_function_example_and_call_owes_its_entry`, `test_the_ending_entry_says_how_many_calls_the_function_makes` |

Nine of nine die. The script that does this lives under the run workspace and
is not committed.

## Decisions

**No formal model, no Quint.** The inventory keeps no state, runs no protocol,
spawns nothing and writes no file. It is a pure function from one syntax tree
to one list, so a state model would restate the code.

**No production change.** Findings 1 to 3 are gaps in the oracle. The fourth,
which does ask for a behaviour change, is the conflict recorded in
`oracle.md`; it is not applied and no existing test was edited.

**Jev was not consulted.** `TYPESAFE_API_KEY` is absent from this environment
and the client exits 3. The conflict was decided locally, from a measured run
of the whole suite rather than from reading alone.

## What it costs

Whole suite, after the change: **1010 passed, 0 failed, 113 s**. Before it:
1007 passed, 0 failed, 110 s. The three new tests add about 3 s.

The two changed files were then run nine times in a row. All nine runs passed
with the same 13 tests:

| | pytest | wall clock |
|---|---|---|
| median of 9 runs | 5.05 s | 5.15 s |
| slowest of 9 runs | 5.11 s | 5.22 s |

No run failed, so nothing here is flaky at nine runs. Each of these tests
starts the `prova` command as a separate process, so they are integration
tests and are measured in seconds, not in the 10 ms a unit test gets. The
slowest single test is the generated one at about 1.1 s; the three added tests
take about 0.04 s each.

The repository ships no linter and no type checker. The mechanical check run
beside the suite is that every module compiles, which it does, on this tree and
on the tree before the change.

## Not measured

- Whether a deletion the review did not make would also be noticed. Nine
  deletions were re-run, not a whole mutation sweep.
- The behaviour the fourth finding asks for. It is not implemented, so nothing
  about it is proved here beyond which three tests contradict it.
