# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1317 tests, all green on main).
  - not-testable (challenge this): states the project, its test command and the green baseline; context for the work, not a promise the product makes.
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority every rule here is read against.
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a process constraint on what may be edited; the conflict it raised is recorded and the owner decided it.
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): the process to follow on a conflicting test; followed, reported and decided before any code was written.
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): names a directory to ignore; nothing in this change reads or writes it.
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): says where the work happens, which is a constraint on the run and not on the product.
- S7: Commit with a message ending in the line
  - not-testable (challenge this): the form a commit message takes in this delivery.
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the exact attribution line every commit of this delivery ends with.
- S9: Do not push and do not merge.
  - not-testable (challenge this): forbids pushing and merging; a constraint on the run.
- S10: Keep the full suite green.
  - not-testable (challenge this): the whole suite stays green, which the delivery's recorded runs show rather than any test of the product.
- S11: No other delivery runs in parallel.
  - not-testable (challenge this): states that no other delivery runs beside this one.
- S12: Everything up to F17 and R1/R2 is on main.
  - not-testable (challenge this): says what is already on main before this change.
- S13: What you build on: F16 (`src/prova/obligations.py`) lists every obligation with `result: not_attempted` and `execution_status`, each with an identity, the condition that reaches it (path condition, seeded with the function's own `requires` for ensures and body sites) and the text of what must be shown; F17 added `stands_on` (compiler, encoding, solver, runtime versions: the solver and encoding are `not applicable` today and must now truthfully name the solver and the encoding version) and the separation of logical result from execution status; F14 budgets (time budget must bound the solver: map a solver timeout to the time budget refusal or to `unknown` with a timed-out execution status, see F19 criterion 2 in the roadmap); F11 manifest and its laws (published fields must equal emitted fields).
  - promises: P1, P2, P5, P7, P9
  - tests P1: test_every_obligation_of_the_hour_clock_comes_back_proved
  - tests P2: test_every_obligation_of_the_reservation_example_comes_back_proved
  - tests P5: test_the_answer_says_the_solver_is_trusted_and_not_checked_again
  - tests P7: test_what_the_translation_does_not_cover_comes_back_unknown
  - tests P9: test_every_obligation_stands_as_one_result_beside_one_status
- S14: Owner decision D1: the solver is a pinned Z3 (the `z3-solver` Python package, pin an exact version in pyproject.toml and uv.lock; the CI workflow runs `uv sync`, check that it installs there; the wheel must install on ubuntu-latest with Python 3.12 and on macOS).
  - promises: P5
  - tests P5: test_the_answer_says_the_solver_is_trusted_and_not_checked_again
- S15: A trusted-solver disclosure is required (SPEC.md lines 302-305): the answer states that its validity result is trusted from the solver, not re-checked.
  - promises: P5
  - tests P5: test_the_answer_says_the_solver_is_trusted_and_not_checked_again
- S16: Soundness is the whole point: a wrong `proved` is the worst possible defect.
  - promises: P3, P7
  - tests P3: test_a_promise_that_is_false_for_some_whole_number_is_not_proved
  - tests P7: test_what_the_translation_does_not_cover_comes_back_unknown
- S17: The encoder must refuse (answer `unknown` with the reason) anything outside its fragment and never translate unsoundly; integers are unbounded mathematical integers (not machine ints; SPEC.md says so, read the integer semantics around lines 120-180), division is not in the profile.
  - promises: P7
  - tests P7: test_what_the_translation_does_not_cover_comes_back_unknown
- S18: Quint is not installed: for the model step, if a formal model is warranted, state the capability limit; the real soundness evidence must come from differential tests: for random programs in the fragment and random inputs, whatever the solver says `proved` must never be contradicted by the evaluator (src/prova/evaluator.py), and every `disproved` must replay in the evaluator (that is F20, but you need the hook now for evidence).
  - promises: P3
  - tests P3: test_a_promise_that_is_false_for_some_whole_number_is_not_proved
- S19: Do not use Jev or any remote question service: settle open questions locally with a written reason.
  - not-testable (challenge this): forbids a remote question service; recorded as a decision of the run, with the local reasoning kept instead.
- S20: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): says where the scripts of this run live, which no product behaviour depends on.
- S21: Known tool rules: oracle laws must name @given property tests; design invariant witnesses must be a `class` or `def` (not a module-level constant), keep the design record in step with the code; an independent_review resolution needs at least 20 characters; prefactor commits must come first in history; process promises go in not-testable sentences; the oracle RED command must name only your new test files; a re-recorded design reopens a pause.
  - not-testable (challenge this): the rules the records of this tool obey; they shape the record, not the product.
- S22: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell hygiene for the commands this run types.
- S23: **Outcome.** The Owner runs `verify` on the hour clock and the reservation example
  - promises: P1, P2
  - tests P1: test_every_obligation_of_the_hour_clock_comes_back_proved
  - tests P2: test_every_obligation_of_the_reservation_example_comes_back_proved
- S24: and sees each in-fragment obligation come back `proved`, with the translation
  - promises: P1, P2, P6
  - tests P1: test_every_obligation_of_the_hour_clock_comes_back_proved
  - tests P2: test_every_obligation_of_the_reservation_example_comes_back_proved
  - tests P6: test_the_shipped_document_explains_every_primitive_the_tool_writes
- S25: written down.
  - promises: P6
  - tests P6: test_the_shipped_document_explains_every_primitive_the_tool_writes
- S26: **Acceptance criteria**
  - not-testable (challenge this): a heading announcing the list of criteria that follows it.
- S27: 1.
  - not-testable (challenge this): the number of the first criterion, carrying no promise of its own.
- S28: Given the hour clock, when `verify` runs, then every in-fragment obligation is
  - promises: P1
  - tests P1: test_every_obligation_of_the_hour_clock_comes_back_proved
- S29: `proved` and nothing is silently skipped.
  - promises: P1, P9
  - tests P1: test_every_obligation_of_the_hour_clock_comes_back_proved
  - tests P9: test_every_obligation_stands_as_one_result_beside_one_status
- S30: 2.
  - not-testable (challenge this): the number of the second criterion, carrying no promise of its own.
- S31: Given the reservation example, likewise, including the step precondition.
  - promises: P2
  - tests P2: test_every_obligation_of_the_reservation_example_comes_back_proved
- S32: 3.
  - not-testable (challenge this): the number of the third criterion, carrying no promise of its own.
- S33: Given a program with a postcondition that is false for some typed input, then
  - promises: P3
  - tests P3: test_a_promise_that_is_false_for_some_whole_number_is_not_proved
- S34: that obligation is not `proved`.
  - promises: P3
  - tests P3: test_a_promise_that_is_false_for_some_whole_number_is_not_proved
- S35: 4.
  - not-testable (challenge this): the number of the fourth criterion, carrying no promise of its own.
- S36: Given a conditional or a match, then the obligation keeps the path condition
  - promises: P4
  - tests P4: test_a_call_in_a_branch_is_proved_under_the_test_that_reaches_it
- S37: that reaches it.
  - promises: P4
  - tests P4: test_a_call_in_a_branch_is_proved_under_the_test_that_reaches_it
- S38: 5.
  - not-testable (challenge this): the number of the fifth criterion, carrying no promise of its own.
- S39: Given the answer, then it names the solver and its version, and discloses that
  - promises: P5
  - tests P5: test_the_answer_says_the_solver_is_trusted_and_not_checked_again
- S40: its validity result is trusted.
  - promises: P5
  - tests P5: test_the_answer_says_the_solver_is_trusted_and_not_checked_again
- S41: 6.
  - not-testable (challenge this): the number of the sixth criterion, carrying no promise of its own.
- S42: Given the delivered change, then it includes the document stating what each
  - promises: P6
  - tests P6: test_the_shipped_document_explains_every_primitive_the_tool_writes
- S43: emitted logical primitive means and why discharging an obligation establishes
  - promises: P6
  - tests P6: test_the_shipped_document_explains_every_primitive_the_tool_writes
- S44: the source claim.
  - promises: P6
  - tests P6: test_the_shipped_document_explains_every_primitive_the_tool_writes
- S45: **SPEC.md** lines 251-268, 302-305.
  - not-testable (challenge this): names the lines of SPEC.md this feature is read against.
- S46: **Dependencies** D1, F16, F17.
  - not-testable (challenge this): names the decisions and features this one depends on.
- S47: **Size** L: the
  - not-testable (challenge this): declares the size of the delivery and nothing the product does.
- S48: encoder is the single biggest unit of work in this roadmap, and SPEC.md lines
  - not-testable (challenge this): says why the encoder is the largest unit of work in the roadmap.
- S49: 264-265 require its written justification in the same delivery.
  - not-testable (challenge this): says the written justification ships in the same delivery, which P6 observes.
- S50: **Touches** new encoder and solver-adapter area, `src/prova/service.py`, new
  - not-testable (challenge this): lists the areas of the repository the change touches.
- S51: dependency, tests, new document under `docs/`.
  - not-testable (challenge this): continues the list of areas the change touches.
- S52: Scope note from the Owner (standing instruction): deliver the smallest fragment that proves the hour clock and the reservation example completely (every in-fragment obligation proved, nothing silently skipped), state the fragment in the written justification document under docs/, and leave everything else unknown with a reason (F19 refines that).
  - promises: P1, P2, P7
  - tests P1: test_every_obligation_of_the_hour_clock_comes_back_proved
  - tests P2: test_every_obligation_of_the_reservation_example_comes_back_proved
  - tests P7: test_what_the_translation_does_not_cover_comes_back_unknown
- S53: If the fragment cannot cover both examples without an unsound shortcut, say so in your design report as a question: context, recommendation, options with consequences, one direct question.
  - not-testable (challenge this): the process for an unsound shortcut; the fragment covers both examples, so none was needed and the reason is recorded.

## Edge matrix

- I1.empty: a request whose source field holds the empty text => completed, an inventory of 0 obligations, 0 attempted and 0 proved | self-probe: held (exit 0) | pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
- I1.unknown: a program whose body multiplies 2 numbers neither of which is known => the obligation comes back unknown with the reason naming the multiplication, and never proved | self-probe: held (exit 0) | pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
- I1.malformed: the text (defn sent as the source => invalid_program with a syntax diagnostic at the place it stops, carrying no inventory and no disclosure | self-probe: held (exit 0) | pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
- I1.dependency-gone: the solver package cannot be imported => every obligation that needs it comes back unknown with the execution status tool_failure naming the missing solver, and the ones settled by a rule of core-0 still come back proved | self-probe: held (exit 0) | pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
- I1.repeated: the same request sent twice in 2 runs => the same answer both times; the operation reads one text, writes nothing and keeps nothing | self-probe: held (exit 0) | pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
- I1.concurrent: 2 commands answering their own requests at the same time => each answers its own, because a run holds its state in its own process and writes no file | self-probe: held (exit 0) | pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
- I1.crash: the command killed while the solver is running => nothing on standard output, no partial answer and no file written, because the answer is printed once at the end | self-probe: held (exit 0) | pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
- I2.empty: a discover request carrying no other field => the manifest, including the version of the translation, its primitives and the path of the document | self-probe: held (exit 0) | pre-feature NOT HELD: exit=1; cause 'not applicable' seen
- I2.unknown: n/a (challenge this): discover reads no source and no other field, so it has no input that can be outside what it knows
- I2.malformed: a request whose operation field holds the number 7 => unavailable with an unknown_operation diagnostic, as it already answers today | self-probe: held (exit 0) | pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
- I2.dependency-gone: the solver package cannot be imported => the manifest still answers, and the version of the solver says it could not be read with the reason instead of naming one | self-probe: held (exit 0) | pre-feature NOT HELD: exit=1; cause 'not applicable' seen
- I2.repeated: discover sent twice in 2 runs => the same manifest both times; it is read from the tool and from nothing a run keeps | self-probe: held (exit 0) | pre-feature NOT HELD: exit=1; cause 'not applicable' seen
- I2.concurrent: 2 discover commands answering at the same time => each prints the same manifest, because nothing is shared between 2 runs | self-probe: held (exit 0) | pre-feature NOT HELD: exit=1; cause 'not applicable' seen
- I2.crash: the command killed while it prints => nothing usable on standard output; the answer is 1 JSON object printed once, never half of one | self-probe: held (exit 0) | pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)

## Definition of done

- SC1 (P1): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN the shipped hour clock of examples/hour-clock.prova, whose 3 functions owe 20 obligations
  - WHEN the Owner sends the operation "verify" with that source
  - THEN all 20 come back "proved", 0 are left not attempted and each names what settled it
  - test: test_every_obligation_of_the_hour_clock_comes_back_proved
- SC2 (P2): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN the reservation example of SPEC.md, whose 3 functions owe 18 obligations
  - WHEN the Owner sends the operation "verify" with that source
  - THEN all 18 come back "proved" and what step promises keeps the condition "(valid-state current)"
  - test: test_every_obligation_of_the_reservation_example_comes_back_proved
- SC3 (P3): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN a function answering "(+ n 1)" and promising "(> result 0)" of every whole number
  - WHEN the Owner sends the operation "verify" with that source
  - THEN that promise is "disproved" with an input such as "-1" and the other 3 obligations stay "proved"
  - test: test_a_promise_that_is_false_for_some_whole_number_is_not_proved
- SC4 (P3): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN the hour clock with the wrap at 12 taken out of what step does and its promise left as shipped
  - WHEN the Owner sends the operation "verify" with that source
  - THEN what step does is not "proved" while at least 15 other obligations still are
  - test: test_the_same_clock_without_its_wrap_at_12_is_not_proved
- SC5 (P4): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN a call to a function asking "(> n 0)" standing in the branch of "(if (> n 0) ...)"
  - WHEN the Owner sends the operation "verify" with that source
  - THEN that call comes back "proved" under the path condition "(> n 0)"
  - test: test_a_call_in_a_branch_is_proved_under_the_test_that_reaches_it
- SC6 (P4): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN a call to a function asking "(= s (Plus))" standing in the clause "((Plus) ...)" of a match of 2 clauses
  - WHEN the Owner sends the operation "verify" with that source
  - THEN that call comes back "proved" under the path condition "(matches s (Plus))"
  - test: test_a_call_in_a_clause_is_proved_under_the_pattern_that_matched
- SC7 (P5): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN a function promising "(= result (* n 2))" of every number above 0
  - WHEN the Owner sends the operation "verify" with that source
  - THEN what it stands on names "z3" with a version and the answer discloses trusted_from "solver" with rechecked_by_this_tool false
  - test: test_the_answer_says_the_solver_is_trusted_and_not_checked_again
- SC8 (P6): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not applicable' seen
  - GIVEN the manifest naming at least 5 primitives of the translation and the path of the document
  - WHEN the Owner opens the document that path names
  - THEN every one of those 5 or more names has an entry of its own there
  - test: test_the_shipped_document_explains_every_primitive_the_tool_writes
- SC9 (P7): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN a function whose body is "(* n m)", multiplying 2 numbers neither of which is known
  - WHEN the Owner sends the operation "verify" with that source
  - THEN its promise comes back "unknown" with a reason of 1 or more characters and never "proved"
  - test: test_what_the_translation_does_not_cover_comes_back_unknown
- SC10 (P8): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not applicable' seen
  - GIVEN the 7 response fields the manifest describes for "verify"
  - WHEN a verify answer is read beside them
  - THEN every field the answer carries is one of them, "trust" included
  - test: test_the_manifest_names_every_field_the_verify_answer_carries
- SC11 (P9): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN any of the 75 one-function programs the plan writes
  - WHEN the Owner sends the operation "verify" with that source
  - THEN its 4 obligations are counted so that attempted is the number really settled and the counts by result add up to 4
  - test: test_every_obligation_stands_as_one_result_beside_one_status
- SC12 (P1): held by the self-probe (exit 0); pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - GIVEN 7 one-function programs whose promise holds for every number they accept
  - WHEN the Owner sends the operation "verify" with each source
  - THEN each promise comes back "proved" with the execution status "completed"
  - test: test_a_promise_that_holds_everywhere_comes_back_proved

## Questions for the owner

- S3: May the expected results of those 5 tests be updated as superseded by F18, each in its own commit, keeping the protective intent re-aimed at what is not shown?
  - existing behaviour: 5 existing expectations pin the opposite of this feature: tests/acceptance/test_verify_lists_the_obligations_owed.py, tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py, tests/properties/test_obligation_inventory_laws.py and tests/unit/test_obligation_inventory_refuses_what_it_cannot_list.py each require every obligation to stand as not_attempted beside unsupported, and tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py requires the solver and the encoding to say they do not apply
  - status: decided at oracle
- S13: Should the solver and encoding rows of that test be updated for the answers that really used them, keeping the not-applicable sentence for the answers where none ran?
  - existing behaviour: tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py requires the encoding and the solver of every completed answer to begin with the words not applicable, which a truthful answer naming a pinned solver cannot do
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- A docs/feature/solver-discharge/craft.md (+110 -0 lines)
- A docs/feature/solver-discharge/design.md (+196 -0 lines)
- A docs/feature/solver-discharge/every-place-a-literal-is-read.md (+100 -0 lines)
- A docs/feature/solver-discharge/model.md (+52 -0 lines)
- A docs/feature/solver-discharge/mutation-survivors.md (+239 -0 lines)
- A docs/feature/solver-discharge/oracle.md (+96 -0 lines)
- A docs/feature/solver-discharge/probe.md (+102 -0 lines)
- A docs/feature/solver-discharge/refactor.md (+54 -0 lines)
- A docs/translation-to-the-solver.md (+206 -0 lines)
- M pyproject.toml (+6 -1 lines)
- M src/prova/budgets.py (+13 -0 lines)
- A src/prova/discharge.py (+318 -0 lines)
- A src/prova/encoding.py (+552 -0 lines)
- M src/prova/manifest.py (+27 -8 lines)
- M src/prova/obligations.py (+336 -31 lines)
- M src/prova/provenance.py (+150 -16 lines)
- M src/prova/service.py (+71 -14 lines)
- A src/prova/solving.py (+362 -0 lines)
- A tests/acceptance/_f18_fixtures.py (+158 -0 lines)
- M tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py (+43 -5 lines)
- M tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py (+24 -11 lines)
- A tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py (+134 -0 lines)
- A tests/acceptance/test_f18_a_guarded_call_keeps_its_path_condition.py (+188 -0 lines)
- A tests/acceptance/test_f18_a_negative_factor_keeps_its_sign.py (+436 -0 lines)
- A tests/acceptance/test_f18_a_pattern_that_carries_patterns_is_not_translated.py (+243 -0 lines)
- A tests/acceptance/test_f18_a_replay_that_runs_out_of_depth_is_not_a_disproof.py (+106 -0 lines)
- A tests/acceptance/test_f18_an_exact_value_is_settled.py (+99 -0 lines)
- A tests/acceptance/test_f18_overlapping_clauses_and_negated_conditions.py (+239 -0 lines)
- A tests/acceptance/test_f18_the_answer_names_the_solver_it_trusted.py (+134 -0 lines)
- A tests/acceptance/test_f18_the_answer_says_what_settled_each_entry.py (+232 -0 lines)
- A tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py (+251 -0 lines)
- A tests/acceptance/test_f18_the_translation_is_written_down.py (+108 -0 lines)
- M tests/acceptance/test_i1_int_checked_evaluator_end_to_end.py (+28 -5 lines)
- M tests/acceptance/test_r1_b4_a_program_too_deep_to_run_is_refused_not_crashed.py (+77 -9 lines)
- M tests/acceptance/test_verify_lists_the_obligations_owed.py (+58 -13 lines)
- A tests/properties/test_f18_a_literal_keeps_its_value_everywhere.py (+577 -0 lines)
- A tests/properties/test_f18_profile_laws.py (+184 -0 lines)
- A tests/properties/test_f18_solver_laws.py (+433 -0 lines)
- M tests/properties/test_obligation_inventory_laws.py (+13 -9 lines)
- A tests/unit/test_f18_a_solver_verdict_becomes_a_finding.py (+326 -0 lines)
- M tests/unit/test_obligation_inventory_refuses_what_it_cannot_list.py (+19 -2 lines)
- M tests/unit/test_service_discover.py (+33 -5 lines)
- A tools/mutate_encoder.py (+406 -0 lines)
- M uv.lock (+20 -0 lines)

## Commits (git log, BASE to HEAD)

- a7cbe68 Hold the condition that reaches a site as the condition it is
- e303afc Say what the Owner will see before building any of it
- a1e0b8a Say what a construct becomes before writing any of it
- 140010e Settle what a program owes, and say what that rests on
- d1ead03 Expect the two examples to be settled, not merely listed
- 391f6a0 Expect a proved obligation to carry a completed attempt
- 94c0bb8 Expect every listed obligation to be settled, for any program
- 39dad3a List what a program owes beside what became of each entry
- b39f724 Expect the answer that asked a solver to name it
- a276e0d Write a rule once instead of in every entry
- 7b81d9a Let the manifest say the word it must now publish
- 33da499 Walk through a session whose obligations are settled
- ee2548a Ask what a chain owes with an answer a caller can be given
- 1dbcfdf Put the new case beside the others, not inside one
- 7b0ece8 Write down what the build cost and what it narrowed
- c0d0376 Pin an exact value where the two sides could not both be wrong
- 6bc464a Let one place spell each word two units compare
- ec8dd59 Build every primitive from one table
- 7d026e1 Write down the two moves and what the probing found
- 0b2709e Close what two independent reviews found open
- 2b272c1 Read each of the three answers a solver can give on its own
- 5c30da7 Load the solver in one place, not two
- 4ce6fa1 Keep the sign, the zero and the width of a literal factor
- 5022940 Put a negative literal in every place the tables reach
- 3f9924a Make the literal a dimension instead of a case
- 69b3770 Pin two places the table found watched by nothing
- 2a6ba40 Put a pattern that always matches where it can be wrong
- 3f89120 Spell the number another way on the other side of every cell
- 0bf55aa Watch the one site a cell could not reach, and name the one it cannot
- 6235330 Guard the order of a call's arguments and the fields of a value
- 60b9a08 Count the table instead of estimating it
- 3e6d0d7 Ask every change the syntax allows, not the ones I thought of
- b767b14 Ask the whole suite once per survivor, not once per mutant
- b520cf2 Open the ledger a survivor has to be written into
- dab30d7 Write each verdict down before starting the next mutant
- 8e2a41a Record what the stopped run knows, and not one word more
- 815030d Watch the three places a seventh review found open
- 44fd5a6 Refuse to publish a run this tool could not finish as a refusal

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f18/request.md
- **promises**:
  - P1: Running verify on the hour clock answers every one of its 20 obligations as proved, each with a completed execution status and the way it was settled named.
  - P2: Running verify on the reservation example answers every one of its 18 obligations as proved, including the one about the state step asks for, whose entry keeps the condition that reaches it.
  - P3: An obligation whose promise is false for some input of the declared types is never answered proved; it is answered disproved with an input that the same tool really refuses when it runs the program over it.
  - P4: An obligation about a call standing in a branch or in a match clause keeps the condition that reaches it, and that condition is what settles it.
  - P5: A completed verify answer names the solver and its version and the translation and its version, and discloses that the solver's validity result is trusted and not checked again by this tool.
  - P6: The change ships a document, named by the manifest, that explains every logical primitive the translation emits and why discharging an obligation establishes the claim the source makes.
  - P7: An obligation outside the translated fragment is answered unknown with its reason and never proved.
  - P8: Everything a verify answer carries is described in the manifest, so a client can look it up before it sends a request.
  - P9: The counts in the answer partition the list: attempted is the number really settled, and the counts by result add up to the obligations listed.
- **sentence_map**:
  - S1 => not-testable: states the project, its test command and the green baseline; context for the work, not a promise the product makes.
  - S2 => not-testable: names SPEC.md as the authority every rule here is read against.
  - S3 => not-testable: a process constraint on what may be edited; the conflict it raised is recorded and the owner decided it.
  - S4 => not-testable: the process to follow on a conflicting test; followed, reported and decided before any code was written.
  - S5 => not-testable: names a directory to ignore; nothing in this change reads or writes it.
  - S6 => not-testable: says where the work happens, which is a constraint on the run and not on the product.
  - S7 => not-testable: the form a commit message takes in this delivery.
  - S8 => not-testable: the exact attribution line every commit of this delivery ends with.
  - S9 => not-testable: forbids pushing and merging; a constraint on the run.
  - S10 => not-testable: the whole suite stays green, which the delivery's recorded runs show rather than any test of the product.
  - S11 => not-testable: states that no other delivery runs beside this one.
  - S12 => not-testable: says what is already on main before this change.
  - S13 => P1,P2,P5,P7,P9
  - S14 => P5
  - S15 => P5
  - S16 => P3,P7
  - S17 => P7
  - S18 => P3
  - S19 => not-testable: forbids a remote question service; recorded as a decision of the run, with the local reasoning kept instead.
  - S20 => not-testable: says where the scripts of this run live, which no product behaviour depends on.
  - S21 => not-testable: the rules the records of this tool obey; they shape the record, not the product.
  - S22 => not-testable: shell hygiene for the commands this run types.
  - S23 => P1,P2
  - S24 => P1,P2,P6
  - S25 => P6
  - S26 => not-testable: a heading announcing the list of criteria that follows it.
  - S27 => not-testable: the number of the first criterion, carrying no promise of its own.
  - S28 => P1
  - S29 => P1,P9
  - S30 => not-testable: the number of the second criterion, carrying no promise of its own.
  - S31 => P2
  - S32 => not-testable: the number of the third criterion, carrying no promise of its own.
  - S33 => P3
  - S34 => P3
  - S35 => not-testable: the number of the fourth criterion, carrying no promise of its own.
  - S36 => P4
  - S37 => P4
  - S38 => not-testable: the number of the fifth criterion, carrying no promise of its own.
  - S39 => P5
  - S40 => P5
  - S41 => not-testable: the number of the sixth criterion, carrying no promise of its own.
  - S42 => P6
  - S43 => P6
  - S44 => P6
  - S45 => not-testable: names the lines of SPEC.md this feature is read against.
  - S46 => not-testable: names the decisions and features this one depends on.
  - S47 => not-testable: declares the size of the delivery and nothing the product does.
  - S48 => not-testable: says why the encoder is the largest unit of work in the roadmap.
  - S49 => not-testable: says the written justification ships in the same delivery, which P6 observes.
  - S50 => not-testable: lists the areas of the repository the change touches.
  - S51 => not-testable: continues the list of areas the change touches.
  - S52 => P1,P2,P7
  - S53 => not-testable: the process for an unsound shortcut; the fragment covers both examples, so none was needed and the reason is recorded.
- **scenarios**:
  - SC1 | P1 | GIVEN the shipped hour clock of examples/hour-clock.prova, whose 3 functions owe 20 obligations | WHEN the Owner sends the operation "verify" with that source | THEN all 20 come back "proved", 0 are left not attempted and each names what settled it
  - SC2 | P2 | GIVEN the reservation example of SPEC.md, whose 3 functions owe 18 obligations | WHEN the Owner sends the operation "verify" with that source | THEN all 18 come back "proved" and what step promises keeps the condition "(valid-state current)"
  - SC3 | P3 | GIVEN a function answering "(+ n 1)" and promising "(> result 0)" of every whole number | WHEN the Owner sends the operation "verify" with that source | THEN that promise is "disproved" with an input such as "-1" and the other 3 obligations stay "proved"
  - SC4 | P3 | GIVEN the hour clock with the wrap at 12 taken out of what step does and its promise left as shipped | WHEN the Owner sends the operation "verify" with that source | THEN what step does is not "proved" while at least 15 other obligations still are
  - SC5 | P4 | GIVEN a call to a function asking "(> n 0)" standing in the branch of "(if (> n 0) ...)" | WHEN the Owner sends the operation "verify" with that source | THEN that call comes back "proved" under the path condition "(> n 0)"
  - SC6 | P4 | GIVEN a call to a function asking "(= s (Plus))" standing in the clause "((Plus) ...)" of a match of 2 clauses | WHEN the Owner sends the operation "verify" with that source | THEN that call comes back "proved" under the path condition "(matches s (Plus))"
  - SC7 | P5 | GIVEN a function promising "(= result (* n 2))" of every number above 0 | WHEN the Owner sends the operation "verify" with that source | THEN what it stands on names "z3" with a version and the answer discloses trusted_from "solver" with rechecked_by_this_tool false
  - SC8 | P6 | GIVEN the manifest naming at least 5 primitives of the translation and the path of the document | WHEN the Owner opens the document that path names | THEN every one of those 5 or more names has an entry of its own there
  - SC9 | P7 | GIVEN a function whose body is "(* n m)", multiplying 2 numbers neither of which is known | WHEN the Owner sends the operation "verify" with that source | THEN its promise comes back "unknown" with a reason of 1 or more characters and never "proved"
  - SC10 | P8 | GIVEN the 7 response fields the manifest describes for "verify" | WHEN a verify answer is read beside them | THEN every field the answer carries is one of them, "trust" included
  - SC11 | P9 | GIVEN any of the 75 one-function programs the plan writes | WHEN the Owner sends the operation "verify" with that source | THEN its 4 obligations are counted so that attempted is the number really settled and the counts by result add up to 4
  - SC12 | P1 | GIVEN 7 one-function programs whose promise holds for every number they accept | WHEN the Owner sends the operation "verify" with each source | THEN each promise comes back "proved" with the execution status "completed"
- **conflicts**:
  - S1 | NONE | ran the suite's own command on the worktree before writing anything; the baseline is green and the count matches.
  - S2 | NONE | read SPEC.md lines 120-180, 251-268 and 302-305; every rule used here is stated there.
  - S3 | CONFLICT | 5 existing expectations pin the opposite of this feature: tests/acceptance/test_verify_lists_the_obligations_owed.py, tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py, tests/properties/test_obligation_inventory_laws.py and tests/unit/test_obligation_inventory_refuses_what_it_cannot_list.py each require every obligation to stand as not_attempted beside unsupported, and tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py requires the solver and the encoding to say they do not apply | May the expected results of those 5 tests be updated as superseded by F18, each in its own commit, keeping the protective intent re-aimed at what is not shown?
  - S4 | NONE | the conflict S3 names was reported before any code was written and the owner answered it.
  - S5 | NONE | checked that no test and no module of this change reads the .relay directory.
  - S6 | NONE | all work happens in the worktree named for this branch; git status was clean at the start.
  - S7 | NONE | read the recent commit messages; the attribution line is the repository's own habit.
  - S8 | NONE | the line is written verbatim; no existing commit rule contradicts it.
  - S9 | NONE | nothing in this delivery pushes or merges; the remote is untouched.
  - S10 | NONE | the suite is green at the start and is the gate at the end; S3 names the only tests this change makes false.
  - S11 | NONE | the worktree holds one branch and nothing else is running against it.
  - S12 | NONE | read the log of main: F17 and R1/R2 are in it and F18 is not.
  - S13 | CONFLICT | tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py requires the encoding and the solver of every completed answer to begin with the words not applicable, which a truthful answer naming a pinned solver cannot do | Should the solver and encoding rows of that test be updated for the answers that really used them, keeping the not-applicable sentence for the answers where none ran?
  - S14 | NONE | installed the z3-solver wheel into a clean Python 3.12 environment on this machine; nothing in the repository pins another solver.
  - S15 | NONE | read SPEC.md lines 302-305; no existing answer discloses trust, so nothing contradicts adding it.
  - S16 | NONE | read the evaluator and the checker; neither reports a proved result today, so nothing claims one already.
  - S17 | NONE | read the out-of-profile refusals and the operator table; division is already refused as unsupported.
  - S18 | NONE | read src/prova/evaluator.py: it runs a function over values and refuses a broken contract, which is what a replay needs.
  - S19 | NONE | no remote question service is called anywhere in this run; every open point is settled with a written reason.
  - S20 | NONE | the scripts of this run live under the workspace; nothing was written to a shared scratchpad.
  - S21 | NONE | the records of this run follow those rules; none of them contradicts a rule of the repository.
  - S22 | NONE | every nwstep argument is passed from a file in the workspace, with the arrow quoted.
  - S23 | NONE | the verify operation already exists and already reads both of those programs; only its answer changes.
  - S24 | NONE | no document of the repository states the translation today, so nothing contradicts adding one.
  - S25 | NONE | checked docs/ for an existing translation document; there is none to disagree with.
  - S26 | NONE | a heading; nothing in the repository disagrees with it.
  - S27 | NONE | the number of a criterion; it states no behaviour to contradict.
  - S28 | NONE | ran verify on the hour clock: it lists exactly the 20 obligations this criterion is about.
  - S29 | NONE | the totals already partition the list; only the words in them change.
  - S30 | NONE | the number of a criterion; it states no behaviour to contradict.
  - S31 | NONE | ran verify on the reservation example: the entry for what step promises already carries the condition that reaches it.
  - S32 | NONE | the number of a criterion; it states no behaviour to contradict.
  - S33 | NONE | no rule of the checker rejects a program whose promise is false, so such a program reaches verify.
  - S34 | NONE | nothing in the repository answers proved today, so no existing answer disagrees.
  - S35 | NONE | the number of a criterion; it states no behaviour to contradict.
  - S36 | NONE | the inventory already carries a path condition for every call obligation; this criterion keeps it.
  - S37 | NONE | ran verify on an if and on a match: the conditions reported are the ones the programs write.
  - S38 | NONE | the number of a criterion; it states no behaviour to contradict.
  - S39 | NONE | the solver row of what an answer stands on is the one S13 names; nothing else reports a solver.
  - S40 | NONE | no answer of the tool discloses trust today, so nothing contradicts the disclosure.
  - S41 | NONE | the number of a criterion; it states no behaviour to contradict.
  - S42 | NONE | the manifest publishes no translation today, so nothing contradicts publishing one.
  - S43 | NONE | no primitive is emitted anywhere today, so no published meaning disagrees.
  - S44 | NONE | nothing in the repository justifies a discharged obligation, so no justification disagrees.
  - S45 | NONE | read those lines of SPEC.md; they are the rules this change implements.
  - S46 | NONE | F16 and F17 are on main and D1 is the owner's decision recorded in the request.
  - S47 | NONE | the size is declared in the workspace and matches the work this change does.
  - S48 | NONE | read the modules the change touches; the encoder is new and the largest of them.
  - S49 | NONE | SPEC.md lines 264-265 ask for the written justification in the same delivery and nothing forbids it.
  - S50 | NONE | read src/prova/service.py: verify is dispatched there and no other operation would move.
  - S51 | NONE | the dependency list of pyproject.toml is empty today, so adding one contradicts nothing.
  - S52 | NONE | ran verify on both examples and checked every construct they use against the fragment SPEC.md names.
  - S53 | NONE | worked the two examples through by hand first: every obligation of both is linear, so no unsound shortcut is needed.
- **decisions**:
  - S3: The owner decided Option A: the discharge lands on verify itself and the expected results of those 5 tests are updated as superseded by F18, each in its own commit, keeping each test's protective intent re-aimed at what was not shown.
  - S13: The owner decided that the solver and encoding rows state the real versions for an answer that used them and keep a not-applicable sentence only where none ran, so no answer reports work nobody did.
  - DEC1: No remote question service is used in this run, as the request requires; every open point is settled locally with its reason written in these records.
  - DEC2: The fragment is the smallest that covers both shipped examples: quantifier-free Boolean reasoning, linear integer arithmetic over unbounded integers, the non-recursive records and unions of core-0, and semantics-preserving expansion of acyclic calls, with multiplication only where one operand is a literal.
  - DEC3: Both examples were worked through by hand before any code: every obligation of each is linear, so the fragment covers them with no unsound shortcut and there is nothing to ask the owner about it.
  - DEC4: The time budget bounding the solver is implemented and recorded, but no acceptance test forces it: the fragment admits no instance slow enough to time out without racing the wall clock, so it is probed at the adapter's own contract during craft instead.
- **mapping**:
  - P1 => test_every_obligation_of_the_hour_clock_comes_back_proved
  - P2 => test_every_obligation_of_the_reservation_example_comes_back_proved
  - P3 => test_a_promise_that_is_false_for_some_whole_number_is_not_proved
  - P4 => test_a_call_in_a_branch_is_proved_under_the_test_that_reaches_it
  - P5 => test_the_answer_says_the_solver_is_trusted_and_not_checked_again
  - P6 => test_the_shipped_document_explains_every_primitive_the_tool_writes
  - P7 => test_what_the_translation_does_not_cover_comes_back_unknown
  - P8 => test_the_manifest_names_every_field_the_verify_answer_carries
  - P9 => test_every_obligation_stands_as_one_result_beside_one_status
- **covers_scenarios**:
  - SC1 => test_every_obligation_of_the_hour_clock_comes_back_proved
  - SC2 => test_every_obligation_of_the_reservation_example_comes_back_proved
  - SC3 => test_a_promise_that_is_false_for_some_whole_number_is_not_proved
  - SC4 => test_the_same_clock_without_its_wrap_at_12_is_not_proved
  - SC5 => test_a_call_in_a_branch_is_proved_under_the_test_that_reaches_it
  - SC6 => test_a_call_in_a_clause_is_proved_under_the_pattern_that_matched
  - SC7 => test_the_answer_says_the_solver_is_trusted_and_not_checked_again
  - SC8 => test_the_shipped_document_explains_every_primitive_the_tool_writes
  - SC9 => test_what_the_translation_does_not_cover_comes_back_unknown
  - SC10 => test_the_manifest_names_every_field_the_verify_answer_carries
  - SC11 => test_every_obligation_stands_as_one_result_beside_one_status
  - SC12 => test_a_promise_that_holds_everywhere_comes_back_proved
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC6 => base differs
  - SC7 => base differs
  - SC8 => base differs
  - SC9 => base differs
  - SC10 => base differs
  - SC11 => base differs
  - SC12 => base differs
- **interfaces**:
  - I1: the verify operation of the prova command, which takes one JSON request on standard input and prints one JSON answer on standard output
  - I2: the discover operation of the same command, whose manifest publishes what a verify answer carries, the translation and its version, the primitives it writes and where the translation is written down
- **matrix**:
  - I1.empty => a request whose source field holds the empty text => completed, an inventory of 0 obligations, 0 attempted and 0 proved
  - I1.unknown => a program whose body multiplies 2 numbers neither of which is known => the obligation comes back unknown with the reason naming the multiplication, and never proved
  - I1.malformed => the text (defn sent as the source => invalid_program with a syntax diagnostic at the place it stops, carrying no inventory and no disclosure
  - I1.dependency-gone => the solver package cannot be imported => every obligation that needs it comes back unknown with the execution status tool_failure naming the missing solver, and the ones settled by a rule of core-0 still come back proved
  - I1.repeated => the same request sent twice in 2 runs => the same answer both times; the operation reads one text, writes nothing and keeps nothing
  - I1.concurrent => 2 commands answering their own requests at the same time => each answers its own, because a run holds its state in its own process and writes no file
  - I1.crash => the command killed while the solver is running => nothing on standard output, no partial answer and no file written, because the answer is printed once at the end
  - I2.empty => a discover request carrying no other field => the manifest, including the version of the translation, its primitives and the path of the document
  - I2.unknown => n/a: discover reads no source and no other field, so it has no input that can be outside what it knows
  - I2.malformed => a request whose operation field holds the number 7 => unavailable with an unknown_operation diagnostic, as it already answers today
  - I2.dependency-gone => the solver package cannot be imported => the manifest still answers, and the version of the solver says it could not be read with the reason instead of naming one
  - I2.repeated => discover sent twice in 2 runs => the same manifest both times; it is read from the tool and from nothing a run keeps
  - I2.concurrent => 2 discover commands answering at the same time => each prints the same manifest, because nothing is shared between 2 runs
  - I2.crash => the command killed while it prints => nothing usable on standard output; the answer is 1 JSON object printed once, never half of one
- **laws**:
  - LAW1 | whatever is answered proved is never contradicted by running the program: for an input meeting what the function asks for, the tool's own evaluator never refuses the call for the promise that was proved | generator=test_what_is_proved_is_never_contradicted_by_running_the_program | observation=the evaluator reports no postcondition_violation for 2 accepted inputs of every program whose promise came back proved | mutant=an encoder that drops the function's precondition proves a promise that fails on an input the evaluator refuses
  - LAW2 | every obligation answered disproved carries an input that the evaluator really refuses for that same promise | generator=test_what_is_disproved_names_an_input_that_really_breaks_the_promise | observation=replaying the reported arguments through the evaluate operation reports a postcondition_violation | mutant=a disproof built from the solver's model without replaying it reports an input the evaluator accepts
  - LAW3 | every obligation stands as one of the 4 logical results beside one of the 7 execution statuses, anything unsettled says why, and the counts partition the list | generator=test_every_obligation_stands_as_one_result_beside_one_status | observation=each entry's 2 words come from their own vocabularies, each unknown carries a reason, and attempted plus not_attempted is the number of entries | mutant=an answer reporting an unknown with no reason, or a total that counts an entry nothing tried as attempted
  - LAW4 | an obligation the translation does not cover comes back unknown with its reason and never proved | generator=test_what_the_translation_does_not_cover_comes_back_unknown | observation=a body multiplying 2 unknown numbers is answered unknown with a reason of at least 1 character | mutant=an encoder that hands general multiplication to the solver anyway and reports proved
  - LAW5 | a promise that holds for every input the function accepts comes back proved | generator=test_a_promise_that_holds_everywhere_comes_back_proved | observation=each of 7 programs whose promise is true by construction is answered proved with the execution status completed | mutant=an encoder that answers unknown for everything, which satisfies LAW1 while settling nothing
- **messages**:
  - MSG1 | a program whose body multiplies 2 numbers neither of which is known | the obligation could not be settled | the translation covers no multiplication of 2 unknown numbers, which SPEC.md puts outside the automation required here | write one of the operands as a literal, or read the fragment in the document the manifest names | test=test_what_the_translation_does_not_cover_comes_back_unknown
  - MSG2 | a function answering (+ n 1) and promising (> result 0) | the promise does not hold | an input of the declared type breaks it, and the answer names that input | run the function over that input to see the refusal, then repair the promise or the body | test=test_the_input_the_answer_names_really_breaks_the_promise
  - MSG3 | any completed verify answer a client reads | which solver was trusted and that this tool did not check its result again | this tool keeps no proof certificate and runs no checking kernel, so a defect in that solver reaches the reader | read the solver and its version from what the answer stands on and judge the word it gives | test=test_the_answer_says_the_solver_is_trusted_and_not_checked_again
- **red**: `uv run pytest -q tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py tests/acceptance/test_f18_a_guarded_call_keeps_its_path_condition.py tests/acceptance/test_f18_the_answer_names_the_solver_it_trusted.py tests/acceptance/test_f18_the_translation_is_written_down.py tests/properties/test_f18_solver_laws.py` exited 1 in 9.602s
  - failing on the pre-feature tree (17): tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py::test_every_obligation_of_the_hour_clock_comes_back_proved, tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py::test_every_obligation_of_the_reservation_example_comes_back_proved, tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py::test_the_same_clock_without_its_wrap_at_12_is_not_proved, tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py::test_a_promise_that_is_false_for_some_whole_number_is_not_proved, tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py::test_the_input_the_answer_names_really_breaks_the_promise, tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py::test_what_is_true_of_the_same_program_is_still_proved, tests/acceptance/test_f18_a_guarded_call_keeps_its_path_condition.py::test_a_call_in_a_branch_is_proved_under_the_test_that_reaches_it, tests/acceptance/test_f18_a_guarded_call_keeps_its_path_condition.py::test_a_call_in_a_clause_is_proved_under_the_pattern_that_matched, tests/acceptance/test_f18_the_answer_names_the_solver_it_trusted.py::test_the_answer_names_the_solver_and_the_translation_it_used, tests/acceptance/test_f18_the_answer_names_the_solver_it_trusted.py::test_the_answer_says_the_solver_is_trusted_and_not_checked_again, tests/acceptance/test_f18_the_answer_names_the_solver_it_trusted.py::test_the_manifest_names_every_field_the_verify_answer_carries, tests/acceptance/test_f18_the_translation_is_written_down.py::test_the_tool_publishes_the_primitives_it_writes_for_the_solver, tests/acceptance/test_f18_the_translation_is_written_down.py::test_the_shipped_document_explains_every_primitive_the_tool_writes, tests/properties/test_f18_solver_laws.py::test_what_is_disproved_names_an_input_that_really_breaks_the_promise, tests/properties/test_f18_solver_laws.py::test_a_promise_that_holds_everywhere_comes_back_proved, tests/properties/test_f18_solver_laws.py::test_every_obligation_stands_as_one_result_beside_one_status, tests/properties/test_f18_solver_laws.py::test_what_the_translation_does_not_cover_comes_back_unknown
  - tests (read from the run): 17 failed, 3 passed in 8.88s
  ```text
              "unknown with that reason and must not be translated unsoundly. "
              f"HOW: the program was:\n{source}"
          )
  E       AssertionError: WHAT: a promise about (* n m) is answered 'not_attempted'. WHY: SPEC.md puts general Int multiplication outside the automation required here; an obligation remaining outside the fragment returns unknown with that reason and must not be translated unsoundly. HOW: the program was:
  E         (defn f
  E           (sig ((n Int) (m Int)) -> Int ! pure)
  E           (ensures (>= result 0))
  E           (examples (example (f 2 3) => 6))
  E           (* n m))
  E
  E       assert 'not_attempted' == 'unknown'
  E
  E         - unknown
  E         + not_attempted
  E       Failing test case: test_what_the_translation_does_not_cover_comes_back_unknown(
  E           # The test always failed when commented parts were varied together.
  E           multiplied=('(* n m)', 6),  # or any other generated value
  E           promise='(>= result 0)',  # or any other generated value
  E       )

  tests/properties/test_f18_solver_laws.py:364: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py::test_every_obligation_of_the_hour_clock_comes_back_proved
  FAILED tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py::test_every_obligation_of_the_reservation_example_comes_back_proved
  FAILED tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py::test_the_same_clock_without_its_wrap_at_12_is_not_proved
  FAILED tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py::test_a_promise_that_is_false_for_some_whole_number_is_not_proved
  FAILED tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py::test_the_input_the_answer_names_really_breaks_the_promise
  FAILED tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py::test_what_is_true_of_the_same_program_is_still_proved
  FAILED tests/acceptance/test_f18_a_guarded_call_keeps_its_path_condition.py::test_a_call_in_a_branch_is_proved_under_the_test_that_reaches_it
  FAILED tests/acceptance/test_f18_a_guarded_call_keeps_its_path_condition.py::test_a_call_in_a_clause_is_proved_under_the_pattern_that_matched
  FAILED tests/acceptance/test_f18_the_answer_names_the_solver_it_trusted.py::test_the_answer_names_the_solver_and_the_translation_it_used
  FAILED tests/acceptance/test_f18_the_answer_names_the_solver_it_trusted.py::test_the_answer_says_the_solver_is_trusted_and_not_checked_again
  FAILED tests/acceptance/test_f18_the_answer_names_the_solver_it_trusted.py::test_the_manifest_names_every_field_the_verify_answer_carries
  FAILED tests/acceptance/test_f18_the_translation_is_written_down.py::test_the_tool_publishes_the_primitives_it_writes_for_the_solver
  FAILED tests/acceptance/test_f18_the_translation_is_written_down.py::test_the_shipped_document_explains_every_primitive_the_tool_writes
  FAILED tests/properties/test_f18_solver_laws.py::test_what_is_disproved_names_an_input_that_really_breaks_the_promise
  FAILED tests/properties/test_f18_solver_laws.py::test_a_promise_that_holds_everywhere_comes_back_proved
  FAILED tests/properties/test_f18_solver_laws.py::test_every_obligation_stands_as_one_result_beside_one_status
  FAILED tests/properties/test_f18_solver_laws.py::test_what_the_translation_does_not_cover_comes_back_unknown
  17 failed, 3 passed in 8.88s
  ```

## 2. design: Find the owners and design the change (revision 1)

- **owners**:
  - what obligations a program owes, their identity, their site and the condition that reaches each one => src/prova/obligations.py
  - the condition that reaches a site, held as the expressions it is made of rather than as text => src/prova/obligations.py (prepared first, behaviour unchanged)
  - what each core-0 construct means as a logical term, and which constructs the fragment covers => new: no module turns a program into anything but a value or a report about it today, and the fragment boundary has no owner at all
  - asking a solver one question and bounding it by the time the run has left => new: nothing in this tool has ever asked a solver, and the dependency must stay behind one port that loads it lazily
  - deciding proved, disproved or unknown for one obligation, and validating a witness before calling anything disproved => new: the decision joins three existing owners (the inventory, the translation and the reference semantics) and belongs to none of them
  - running a function of a program over values, which is the reference semantics a witness is replayed against => src/prova/evaluator.py
  - the time and memory a run may take, and the refusal when one is passed => src/prova/budgets.py
  - what a completed answer stands on: the digest of the tool and the four versions behind the answer => src/prova/provenance.py
  - what the manifest publishes about an operation's request and answer => src/prova/manifest.py
  - dispatching the verify operation and building the answer a client reads => src/prova/service.py
  - the exact version of the solver this tool stands on => pyproject.toml and uv.lock
  - the written justification of the translation and the meaning of every primitive it writes => new: docs/translation-to-the-solver.md, which the manifest points at
- **reuse_decision**: Reused where they stand: the inventory and its path conditions (src/prova/obligations.py), the evaluator as the reference semantics a witness is replayed against (src/prova/evaluator.py), the budgets of a run (src/prova/budgets.py), what an answer stands on (src/prova/provenance.py), the manifest (src/prova/manifest.py) and the dispatcher (src/prova/service.py). Three units are new because no existing owner answers their question: encoding.py says what a core-0 construct means logically and where the fragment ends, which nothing in this tool has ever decided; solving.py asks a solver and bounds it, which nothing has ever done and which must stay behind one port so the dependency is loaded lazily and a machine without it still answers; discharge.py decides the three answers and validates a witness, a decision that joins the inventory, the translation and the reference semantics and belongs inside none of them. A term language of its own stands between the translation and the solver so that the whole translation can be decided, tested and published with no solver installed, and so the primitives the manifest publishes and the document explains are read from the one declaration that defines them.
- **paradigm**: oo
- **boundaries**:
  - the driving port: one JSON request on standard input and one JSON answer on standard output, for the verify operation => src/prova/service.py owns it, as it already owns every other operation
  - the driven solver port: a claim goes out as a term and a verdict comes back => src/prova/solving.py owns the adapter; the unit that decides the three answers depends on the port and never on the solver package
  - the reference semantics: a candidate witness goes out as values and a refusal or a value comes back => src/prova/evaluator.py owns it and is called through the public function the service already calls
  - the published surface: every field a verify answer carries and the translation it names => src/prova/manifest.py owns what is published, and the answer carries nothing the manifest does not describe
  - the dependency boundary: the exact solver version => pyproject.toml and uv.lock own the pin, and the CI workflow installs it with uv sync
  - the document boundary: the written justification is found by the path the manifest publishes, never by a path a reader has to know
- **domain_types**:
  - Term, the closed language of logical primitives the translation emits, with one declaration from which the manifest and the document are both read
  - Claim, the assumptions and the one conclusion of a single obligation
  - OutsideTheFragment, a construct the translation declines by name with its reason, which is the only way the translation can decline
  - Verdict, what the solver port answers: refuted with a model, unrefutable, or undecided with its reason and execution status
  - Witness, a solver's model read back as values of the program, written the way a program writes them
  - ValidatedWitness, a witness the reference evaluator really refused, which is the only thing a disproof may carry
  - Finding, the settled standing of one obligation: a logical result and the execution status that belongs with it, built only by named constructors
  - Condition, one clause of the condition that reaches a site: a holding, a failing, a matching or a not-matching of an expression, each writing itself out exactly as the text does today
  - SolverStanding, what an answer says about the solver behind it: the one it asked with its version, or the reason it asked none
- **invariants**:
  - INV1 | A logical result is never paired with an execution status by a caller: each of the five settled standings is built by its own named constructor, which fixes both words, so proved beside timed_out or unknown beside completed-with-no-reason cannot be built at all | witness=src/prova/discharge.py:Finding | bypass=none
  - INV2 | Nothing outside the fragment is ever translated: every translation answers either a term or a refusal naming the construct, and there is no third way out, so a construct the fragment does not cover cannot be dropped quietly or guessed at | witness=src/prova/encoding.py:OutsideTheFragment | bypass=none
  - INV3 | A disproof carries only a witness the reference evaluator really refused; a candidate the evaluator accepts, or one it cannot run to the end, becomes unknown with that reason | witness=src/prova/discharge.py:ValidatedWitness | bypass=the evaluator's own depth limit, which stops a replay rather than confirming it; that case answers unknown
  - INV4 | The solver package is reached only inside the call that asks it and only with the time the run has left, so no other operation loads it, a refused build enters no solver work, and no query can outlive the budget | witness=src/prova/solving.py:PinnedZ3 | bypass=any future module importing z3 directly instead of asking this port
  - INV5 | Every logical primitive the translation can emit is published and documented from the one declaration that defines it, so a primitive added later cannot reach an answer without its meaning | witness=src/prova/encoding.py:published_primitives | bypass=none
  - INV6 | What an answer stands on names the solver this answer asked, or says it asked none and why, while the digest of the tool itself stays one for every answer | witness=src/prova/provenance.py:SolverStanding | bypass=none
- **prefactoring**: yes
- **prefactoring_reason**: The condition that reaches a site is held today as a tuple of strings, built by writing each branch and clause out as text. Text cannot be translated, and the feature must assume that condition in the solver. One commit, before any behaviour, replaces those strings with the conditions they already are -- a holding, a failing, a matching or a not-matching of an expression -- each of which writes itself out exactly as today. Behaviour is unchanged: every path condition reported in an answer is the same characters, which the existing inventory tests and laws already pin, and no test is edited.

## 10. model: Decide and prove the formal model (revision 2)

- **formal_model**: not_needed
- **no_state_reason**:
  - This change writes no file, takes no lock, starts no thread and keeps nothing between runs: the verify operation reads one text, settles each obligation in the one process that was asked, and prints one answer at the end. There is no shared state, no protocol of more than one step, no concurrency and no window in which an interrupted run could leave anything half done.
  - subprocess appears only in the test files and in the mutation harness, which run the shipped prova command over its JSON surface the way the Owner does. No module of the product spawns a process, renames, locks or threads: the solver is a library call inside the same process, so there is no child to race, to crash or to leave behind.
  - write_text appears only in tools/mutate_encoder.py, a developer tool that no module imports, that the wheel and the sdist do not carry and that CI does not run. What it writes is a copy of the source tree in a temporary directory of its own and its own report beside it, both outside the repository and both removed when the mutant it belongs to has been judged. The product itself writes nothing at all: no module of src/prova opens a file for writing, so there is no file to leave half written, to lock or to recover.
  - The one claim here that would warrant a checker is not about state but about a pure translation: that whatever is answered proved is never contradicted by the reference evaluator. Quint is not installed on this machine, so that check cannot be run and is recorded as a capability limit, INDETERMINATE rather than passed. Standing beside it as evidence of another kind, each a bounded counterexample search through the real command and never a proof: the soundness law over generated programs at the integer extremes, its positive control, the law that every contract clause is defined for every typed value, and the law that a program the checker accepted ends.

## 11. craft: Craft the change (revision 2)

- **refactor_commits**:
  - a7cbe68
- **refactor_check**: the check ran on the parent and on each refactor commit
  - a7cbe6814915 (Hold the condition that reaches a site as the condition it is): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 264.663s
  - tests (read from the run): 1920 passed in 264.46s
  - slowest: 11.03s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 7.22s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 7.16s call tests/properties/test_f18_solver_laws.py::test_what_is_proved_is_never_contradicted_by_running_the_program
  - slowest: 6.43s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 5.57s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 5.12s call tests/properties/test_f18_solver_laws.py::test_every_obligation_stands_as_one_result_beside_one_status
  - slowest: 4.62s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 4.54s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 3.30s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 2.69s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  ```text
  ........................................................................ [  3%]
  ........................................................................ [  7%]
  ........................................................................ [ 11%]
  ........................................................................ [ 15%]
  ........................................................................ [ 18%]
  ........................................................................ [ 22%]
  ........................................................................ [ 26%]
  ........................................................................ [ 30%]
  ........................................................................ [ 33%]
  ........................................................................ [ 37%]
  ........................................................................ [ 41%]
  ........................................................................ [ 45%]
  ........................................................................ [ 48%]
  ........................................................................ [ 52%]
  ........................................................................ [ 56%]
  ........................................................................ [ 60%]
  ........................................................................ [ 63%]
  ........................................................................ [ 67%]
  ........................................................................ [ 71%]
  ........................................................................ [ 75%]
  ........................................................................ [ 78%]
  ........................................................................ [ 82%]
  ........................................................................ [ 86%]
  ........................................................................ [ 90%]
  ........................................................................ [ 93%]
  ........................................................................ [ 97%]
  ................................................                         [100%]
  ============================= slowest 10 durations =============================
  11.03s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  7.22s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  7.16s call     tests/properties/test_f18_solver_laws.py::test_what_is_proved_is_never_contradicted_by_running_the_program
  6.43s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  5.57s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  5.12s call     tests/properties/test_f18_solver_laws.py::test_every_obligation_stands_as_one_result_beside_one_status
  4.62s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  4.54s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  3.30s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  2.69s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1920 passed in 264.46s (0:04:24)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.168s
- **typesafe**: refused: the request forbids any remote question service for this run, so no question was put to Jev and every open point was settled locally with its reason written in these records

## 12. refactor: Refactor the code you wrote (revision 5)

- **units**:
  - src/prova/solving.py:PinnedZ3 | applied: L1, the solver was loaded inside each of the 2 calls that need it with the same try, the same refusal and the same sentence written twice; one place loads it now and both callers read either the library or the reason it could not be loaded, still inside the call that needs it (commit 5c30da7)
  - src/prova/solving.py:verdict_for | applied: L3, the third answer a solver can give was read inside the question that asked it, where no program of this fragment can reach it; the three answers are now read in one place a test can hand an answer to directly (commit 2b272c1)
  - src/prova/solving.py:_Question | applied: L3, one table with one row per primitive in place of a chain of 8 tests beside a table of 12 (commit ec8dd59); the 3 readers the rows use are a deliberate break of the no-getters rule, taken because this unit is the solver adapter, which nw-code-design-oo exempts
  - src/prova/discharge.py:Finding | applied: L1, a method nothing called is removed, and the word for an obligation nobody attempted is read from the module that has owned it since F16 (commit 6bc464a)
  - src/prova/obligations.py:Obligation | applied: L1, the four words naming which refusal confirms a candidate counterexample are named once beside the kinds that carry them (commit 6bc464a)
  - src/prova/solving.py:could_not_tell | none: one responsibility, 3 lines, mapping a solver's own reason to the status that belongs with it
  - src/prova/solving.py:_Sorts | none: one responsibility, the types of one claim in the solver's terms, with 3 lookups over one table it builds in its constructor
  - src/prova/encoding.py:Translation | none: one method per kind of expression, each 1 to 6 lines, dispatched once from a single table of expression kinds
  - src/prova/encoding.py:Term | none: a value with named constructors and no behaviour to move
  - src/prova/encoding.py:published_primitives | none: the one declaration the manifest and the shipped document both read
  - src/prova/discharge.py:Discharge | none: one obligation settled at a time, with the replay gate the only path to a disproof
  - src/prova/discharge.py:ValidatedWitness | none: a value built in one place, by the replay that confirmed it
  - src/prova/obligations.py:Inventory | none: one responsibility, and its refusal of an obligation with no finding is the rule that nothing is silently skipped
  - src/prova/obligations.py:PathCondition | none: prepared before the feature, in its own commit
  - src/prova/provenance.py:SolverStanding | none: 2 constructors and 4 small readers, refusing the state that names a solver and a reason at once
  - src/prova/provenance.py:the_solver_it_requires | none: one responsibility, read from the installed metadata so the pin lives in pyproject.toml alone
  - src/prova/budgets.py:Run | none: one method added, 1 line
  - src/prova/service.py:_run_verify | none: the dispatcher's one new branch

## 14. probe: Probe the build (revision 2)

- **cases** (self-probe: run by the executor, not an independent review):
  - I1.empty: held; expected exit=0,kind=preserve,protects=tests/properties/test_f18_profile_laws.py; observed exit=0; pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
  - I1.unknown: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - I1.malformed: held; expected exit=0,kind=preserve,protects=tests/properties/test_f18_profile_laws.py; observed exit=0; pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
  - I1.dependency-gone: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - I1.repeated: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - I1.concurrent: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - I1.crash: held; expected exit=0,kind=preserve,protects=tests/properties/test_f18_profile_laws.py; observed exit=0; pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
  - I2.empty: held; expected exit=0,kind=new,baseline-contains=not applicable; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not applicable' seen
  - I2.malformed: held; expected exit=0,kind=preserve,protects=tests/properties/test_f18_profile_laws.py; observed exit=0; pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
  - I2.dependency-gone: held; expected exit=0,kind=new,baseline-contains=not applicable; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not applicable' seen
  - I2.repeated: held; expected exit=0,kind=new,baseline-contains=not applicable; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not applicable' seen
  - I2.concurrent: held; expected exit=0,kind=new,baseline-contains=not applicable; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not applicable' seen
  - I2.crash: held; expected exit=0,kind=preserve,protects=tests/properties/test_f18_profile_laws.py; observed exit=0; pre-feature held: exit=0; protects tests/properties/test_f18_profile_laws.py: executed (56 line(s) ran)
  - SC1: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC2: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC3: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC4: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC5: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC6: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC7: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC9: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC11: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC12: held; expected exit=0,kind=new,baseline-contains=not_attempted; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not_attempted' seen
  - SC8: held; expected exit=0,kind=new,baseline-contains=not applicable; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not applicable' seen
  - SC10: held; expected exit=0,kind=new,baseline-contains=not applicable; observed exit=0; pre-feature NOT HELD: exit=1; cause 'not applicable' seen

## 15. selfreview: Self-review (revision 2)

- **answers**:
  - D1: pass - the three new units are the three the design record names, each owning what it said: encoding.py the meaning of a construct and the fragment, solving.py the one place a solver is asked, discharge.py the three answers; the inlining and never-assume-a-postcondition rule is the one the design argued
  - D2: fixed:the word for an unattempted obligation was spelled in two modules and the four witness-confirmation words were bare strings in two; each now has one owner (e741e3e), the two rules of the profile are written once per answer instead of once per entry (a276e0d), and the solver is loaded in one place instead of two (5c30da7)
  - D3: pass - the unit that decides the three answers depends on the solver port and never on the solver package; solving.py is the only module that names z3 and it names it inside the call that asks, which the trace property over a refused build still observes from outside
  - D4: fixed:a logical result could be paired with any execution status by a caller; each of the five standings is now built by its own named constructor that fixes both words, so proved beside timed_out cannot be built, at src/prova/discharge.py:95, and src/prova/provenance.py:101 refuses a standing that names a solver and a reason at once
  - D5: pass - every new unit is small and cohesive; the one deliberate break is the three readers the primitive table uses at src/prova/solving.py:117 and around it, taken because this unit is the solver adapter, which nw-code-design-oo exempts, and recorded with its cost in the refactor step
  - D6: pass - no pattern was imported for its own sake: a port with one adapter, a value with named constructors, and one table per dispatch; nothing was generalised for a single caller
  - D7: pass - the words are the language of the profile: an obligation, what reaches a site, a witness, a finding, what an answer stands on; no Manager, Helper or Data anywhere in the change
  - D8: pass - the domain units read no file and spawn nothing; the solver library is behind one port, the manifest is published by the module that owns what is published, and the pin lives in pyproject.toml alone
  - D9: pass - every acceptance test drives the installed prova command over its JSON surface through one runner at tests/acceptance/_f18_fixtures.py:44 and imports nothing from src; the two unit files reach the public contract of a non-exported module, which the mandates allow for a unit test and which is the only way to hand the solver port an answer no program of this fragment produces
  - D10: pass - every test name is a sentence about what the Owner sees, carries no process id, layer term or production symbol, and the files are named for the promise
  - D11: pass - one shared runner and one set of readers in _f18_fixtures.py; no test re-implements the request, and every source a test sends is written out in the test that sends it
  - D12: fixed:the soundness law at tests/properties/test_f18_solver_laws.py:219 now draws distances past any machine word as well as small ones, and a positive control beside it fails for a tool that settles nothing; two laws about the premises the structural discharge rests on were added in a file of their own
  - D13: pass - the full suite runs in about 222 seconds against a ceiling the repository does not raise; the slowest tests are older property files, and the F18 laws finish in about 10 seconds together
  - D14: pass - each new test adds a distinct observation: the two examples, a false promise, a guarded call, an exact value, overlapping clauses, negated conditions, a negative factor, what settled each entry, and the verdicts a solver can give
  - D15: fixed:every assertion this change adds says what failed, why it matters and how to act, including the one explaining why a wrong proved is the worst defect this tool can have at tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py:64; the production refusals name the limit, the construct and the document to read
  - D16: pass - the change has no state, protocol, concurrency or crash window: one request, one process, nothing written. The claim a checker would be right for is the soundness of a pure translation, Quint is not installed, and that is recorded as a capability limit with the generated differential laws beside it rather than as a pass
  - D17: fixed:three texts were wrong rather than thin and are repaired in 4ce6fa1: the published rule and the shipped document said the disclosure is carried when a solver was asked rather than answered and named only two of the three answers that carry none; the document's premise paragraph named one of the three ways a run refuses; the probe document claimed no survivors when two reviews later found four, and now says so
- **independent_review**:
  - REV1 | reviewer=soundness-rev1-f18 | findings=30 over eight rounds (REV1-REV7 REJECT, each closing an oracle gap with no change to src/; REV8 APPROVE at 815030d) | resolution=every finding closed with a cell or an argued equivalence; the REV8 residual P1 (a replay exceeding the evaluator depth budget published as a disproof) closed by an acceptance case after the review; ledger counts corrected
  - REV2 | reviewer=rev-f18b | findings=16 over five rounds (REV1 APPROVE, REV2 REJECT, REV3 APPROVE, REV4 APPROVE, REV5 APPROVE at 815030d) | resolution=all findings closed or recorded as stated limits; the REV5 note on the ledger arithmetic fixed after the review

## 16. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
- **not_verified**:
  - The whole-suite pass of the mutation harness was stopped part way through on the Owner's instruction. It cannot say how many of its 135 cheap-pass survivors it reached, only that none of those it did reach survived the suite; the harness printed nothing for a mutant a pass killed, which is a defect of the harness, now closed by a ledger that records each verdict before the next mutant starts.
  - 127 distinct changes that survived the two cheap passes are listed unclassified in their own section of docs/feature/solver-discharge/mutation-survivors.md. A change no close cell notices may well be caught by a test outside those passes, so none of them is called a survivor. An independent review examined 36 of the mutants that matter and every one of those is accounted for.
  - The solver, the parser, the type checker, the encoder described in the document and the runtime are trusted components, and this delivery adds a solver to that list rather than removing anything from it. A defect in any of them reaches the reader as a proved. The trusted computing base is not empty and the answer says so.
  - The refactor record is marked stale by the ordering rule of the tool, which requires the named refactor commits to be the last code commits; later commits closed review findings in tests and documents. The two behaviour-preserving moves are real and are named in the record with their commit ids; no refactor was manufactured to clear the mark.
  - My first report of a soundness defect in this delivery was wrong: a mutation that kept a file the same length and was undone within the same second left CPython reading the mutant, so the tool appeared to answer proved for a promise that is false. The committed product was sound throughout; the harness now writes no bytecode, clears the cache and touches the restored file, and proves with a control that it carries nothing between runs.
  - No instance in this fragment makes the real solver run out of time, so the mapping from a solver timeout to unknown with a timed-out attempt is observed at the seam the design declares and not end to end through the command.
  - Whether the pinned solver wheel installs in CI on Linux is unverified: it installs here on macOS from a clean uv sync, and uv.lock carries a manylinux wheel for it, but no CI run has happened on this branch.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit 44fd5a658433929892031a80723836af2c05dbf3
  - no checks declared

## Not backed by the diff

- The Owner can now ask what a program owes and be told that each obligation is owed no longer, or exactly why one is not.: a guarantee names no test function of the change
- Every obligation of the shipped hour clock and of the reservation example comes back proved, nothing skipped; a promise false for some input of its declared types is disproved with an input that the tool itself refuses when it runs the program over it; a call standing behind a test or a match clause is settled under the condition that reaches it, and the same call with nothing in front of it is not; and the answer names the pinned Z3 and says plainly that the word proved is the solver's and is not checked again here.: a guarantee names no test function of the change
- The claim is valid exactly when its denial has no solution, and a solution the solver finds is only a candidate until the reference evaluator refuses it.: a guarantee names no test function of the change
- Anything the translation does not cover is answered unknown with the construct named, never translated.: a guarantee names no test function of the change
- The shipped document says what every emitted primitive means and why settling the formula settles the claim the source makes, and the manifest publishes where it lives, the version of the translation and the solver this tool requires.: a guarantee names no test function of the change
- Two kinds of obligation rest on a written rule of core-0 rather than on a solver, and every entry says which of the two settled it.: a guarantee names no test function of the change
