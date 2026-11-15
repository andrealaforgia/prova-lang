# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1045 tests, all green on main).
  - not-testable (challenge this): names the project, its runner and its suite size, and asks for no observable behaviour
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority to read, which is not a behaviour of the tool
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a promise about what this change does not edit, kept by the diff and not by a test
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): a process promise about stopping and reporting a conflict instead of editing a test
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): a process promise to leave one directory and its plans out of this work
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a process promise about which checkout and branch the work happens in
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a process promise about the shape of the commit message
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line the commit message ends with, a fact of the commit
- S9: Do not push and do not merge.
  - not-testable (challenge this): a process promise about not pushing and not merging this branch
- S10: Keep the full suite green.
  - not-testable (challenge this): a promise about the existing suite, kept by running it, not by a new test
- S11: Another delivery (R1, robustness: evaluator.py, syntax.py, reader.py and the request validation in service.py) runs in parallel in a different worktree; keep your service.py change small and local (a new report field) to ease the rebase.
  - not-testable (challenge this): a process constraint on how large the dispatch change may be, read from the diff
- S12: F1 to F10, F16 and F2fix are on main; F16 added the verify inventory (obligations.py) and F10 the table of diagnostic kinds (checker.py).
  - not-testable (challenge this): states which features are already on main and where their code lives
- S13: Decide where the report lives (the answer of check and/or verify) with a reason, and publish its shape in discover.
  - promises: P5
  - tests P5: test_the_manifest_says_what_the_report_holds_and_which_answer_carries_it
- S14: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): a process promise about where the scripts of this run are kept
- S15: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): a process promise about shell quoting and a clean status before reporting
- S16: **Outcome.** The Owner can see at a glance which functions promise nothing, so a
  - promises: P1, P2, P3
  - tests P1: test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted
  - tests P2: test_a_postcondition_written_as_true_is_recorded_as_trivial
  - tests P3: test_a_function_with_a_real_contract_is_recorded_as_neither
- S17: clean result is not mistaken for a meaningful one.
  - promises: P4
  - tests P4: test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct
- S18: **Acceptance criteria**
  - not-testable (challenge this): a heading announcing the list of criteria that follows it
- S19: 1.
  - not-testable (challenge this): the number of the first criterion, carrying no claim of its own
- S20: Given a function with no `requires`, when the program is checked, then the
  - promises: P1
  - tests P1: test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted
- S21: report records that precondition as omitted.
  - promises: P1
  - tests P1: test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted
- S22: 2.
  - not-testable (challenge this): the number of the second criterion, carrying no claim of its own
- S23: Given a function whose `ensures` is literally `true`, then the report records it
  - promises: P2
  - tests P2: test_a_postcondition_written_as_true_is_recorded_as_trivial
- S24: as trivial.
  - promises: P2
  - tests P2: test_a_postcondition_written_as_true_is_recorded_as_trivial
- S25: 3.
  - not-testable (challenge this): the number of the third criterion, carrying no claim of its own
- S26: Given a function with a real contract, then it is recorded as neither.
  - promises: P3
  - tests P3: test_a_function_with_a_real_contract_is_recorded_as_neither
- S27: 4.
  - not-testable (challenge this): the number of the fourth criterion, carrying no claim of its own
- S28: Given a program where every contract is omitted or trivial, then nothing in the
  - promises: P4
  - tests P4: test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct
- S29: answer describes the program as meaningfully correct.
  - promises: P4
  - tests P4: test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct
- S30: **SPEC.md** lines 204-206.
  - not-testable (challenge this): points at the lines of the authority this rule comes from
- S31: **Dependencies** none.
  - not-testable (challenge this): states that this work waits for no other delivery
- S32: **Size** S.
  - not-testable (challenge this): states the size of the delivery, which no answer of the tool shows
- S33: **Touches** `src/prova/service.py`, `src/prova/checker.py`, tests.
  - not-testable (challenge this): names the files the change is expected to touch, read from the diff
- S34: **Why it is a real expectation** probe C8 disagrees today.
  - not-testable (challenge this): says why the expectation is real, a fact about the trace table

## Edge matrix

- I1.empty: a source holding no declaration at all => refused as invalid_program by the rule that is already there, and the refusal carries no report | self-probe: not probed | pre-feature not probed
- I1.unknown: a source calling a function nothing declares => refused as invalid_program, and the refusal carries no report | self-probe: not probed | pre-feature not probed
- I1.malformed: a source with an unclosed parenthesis => refused as invalid_program with a syntax diagnostic, and no report | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): check reads only the characters the request carries and opens no file, service or process
- I1.repeated: the same source checked twice in a row => the same report twice, since the operation keeps nothing between two requests | self-probe: not probed | pre-feature not probed
- I1.concurrent: two checks of two different sources at once => each answers about its own text, since the operation keeps no state | self-probe: not probed | pre-feature not probed
- I1.crash: n/a (challenge this): check writes nothing anywhere, so an interrupted run leaves no half written report behind
- I2.empty: a request naming discover and carrying no other field => the manifest, including the published shape of the report | self-probe: not probed | pre-feature not probed
- I2.unknown: a request naming discover and carrying a field the tool does not read => the same manifest, the extra field ignored | self-probe: not probed | pre-feature not probed
- I2.malformed: n/a (challenge this): discover reads no source, so there is no text of a program for it to find malformed
- I2.dependency-gone: n/a (challenge this): the manifest is read from the tables in the tool itself and from no file or service
- I2.repeated: the manifest asked for twice => the same answer twice, since it is read from the tables in the tool | self-probe: not probed | pre-feature not probed
- I2.concurrent: two manifests asked for at once => the same answer to each, since the manifest reads nothing that changes | self-probe: not probed | pre-feature not probed
- I2.crash: n/a (challenge this): discover writes nothing anywhere, so an interrupted run leaves nothing behind

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN a function "twice" that declares no requires block at all
  - WHEN the program is checked
  - THEN the report records the precondition of "twice" as "omitted"
  - test: test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN a function "twice" whose ensures block is written as the literal true
  - WHEN the program is checked
  - THEN the report records the postcondition of "twice" as "trivial"
  - test: test_a_postcondition_written_as_true_is_recorded_as_trivial
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN "twice" with (requires (> n 0)) and (ensures (= result (* n 2)))
  - WHEN the program is checked
  - THEN neither of its 2 blocks is recorded as omitted or trivial
  - test: test_a_function_with_a_real_contract_is_recorded_as_neither
- SC4 (P3): not-held (no held self-probe case)
  - GIVEN the shipped hour clock, whose 3 functions write 3 blocks and leave 3 absent
  - WHEN the program is checked
  - THEN valid-state reads "omitted"/"omitted", initial reads "omitted"/"stated" and step reads "stated"/"stated"
  - test: test_the_shipped_hour_clock_reads_the_way_a_human_reads_it
- SC5 (P4): not-held (no held self-probe case)
  - GIVEN 2 functions whose 4 contract blocks are all absent or written as the literal true
  - WHEN the program is checked
  - THEN the report says states_a_contract is false and no word of the whole answer calls the program correct or meaningful
  - test: test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct
- SC6 (P5): not-held (no held self-probe case)
  - GIVEN a request naming the operation "discover" and carrying no other field
  - WHEN the manifest is asked for
  - THEN it publishes the 3 entry fields, the 3 strengths, the totals fields and the list of operations whose answer carries the report
  - test: test_the_manifest_says_what_the_report_holds_and_which_answer_carries_it

## Questions for the owner

- none

## Observed side effects (git, BASE to HEAD)

- A docs/contract-report/DECISIONS.md (+11 -0 lines)
- A docs/contract-report/SUMMARY.md (+385 -0 lines)
- A docs/contract-report/TRACE.md (+5 -0 lines)
- A docs/feature/contract-report/craft.md (+113 -0 lines)
- A docs/feature/contract-report/oracle.md (+61 -0 lines)
- A docs/feature/contract-report/selfreview.md (+48 -0 lines)
- M src/prova/checker.py (+273 -0 lines)
- M src/prova/service.py (+13 -0 lines)
- A tests/acceptance/_f13_contract_fixtures.py (+205 -0 lines)
- A tests/acceptance/test_f13_b1_a_function_without_a_precondition_is_recorded_as_omitted.py (+55 -0 lines)
- A tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py (+92 -0 lines)
- A tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py (+102 -0 lines)
- A tests/acceptance/test_f13_b4_a_program_that_promises_nothing_is_not_called_meaningful.py (+125 -0 lines)
- A tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py (+132 -0 lines)
- A tests/properties/test_f13_contract_report_laws.py (+186 -0 lines)
- A tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py (+102 -0 lines)

## Commits (git log, BASE to HEAD)

- 5b558e4 [F13] say which contracts are missing or trivial
- 7eceb90 [F13] hand the contract report over with its record
- fed906d [F13] read a contract block for its value, and publish every part of the report

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f13/request.md
- **promises**:
  - P1: the Owner sees that a function which declares no requires block has its precondition recorded as omitted
  - P2: the Owner sees that a contract block written as the literal true is recorded as trivial
  - P3: the Owner sees that a function with a real contract is recorded as neither omitted nor trivial
  - P4: when every contract of a program is omitted or trivial, nothing in the answer describes that program as meaningfully correct
  - P5: the Owner reads from the tool itself which answer carries the report and what the report holds
- **sentence_map**:
  - S1 => not-testable: names the project, its runner and its suite size, and asks for no observable behaviour
  - S2 => not-testable: names SPEC.md as the authority to read, which is not a behaviour of the tool
  - S3 => not-testable: a promise about what this change does not edit, kept by the diff and not by a test
  - S4 => not-testable: a process promise about stopping and reporting a conflict instead of editing a test
  - S5 => not-testable: a process promise to leave one directory and its plans out of this work
  - S6 => not-testable: a process promise about which checkout and branch the work happens in
  - S7 => not-testable: a process promise about the shape of the commit message
  - S8 => not-testable: the attribution line the commit message ends with, a fact of the commit
  - S9 => not-testable: a process promise about not pushing and not merging this branch
  - S10 => not-testable: a promise about the existing suite, kept by running it, not by a new test
  - S11 => not-testable: a process constraint on how large the dispatch change may be, read from the diff
  - S12 => not-testable: states which features are already on main and where their code lives
  - S13 => P5
  - S14 => not-testable: a process promise about where the scripts of this run are kept
  - S15 => not-testable: a process promise about shell quoting and a clean status before reporting
  - S16 => P1,P2,P3
  - S17 => P4
  - S18 => not-testable: a heading announcing the list of criteria that follows it
  - S19 => not-testable: the number of the first criterion, carrying no claim of its own
  - S20 => P1
  - S21 => P1
  - S22 => not-testable: the number of the second criterion, carrying no claim of its own
  - S23 => P2
  - S24 => P2
  - S25 => not-testable: the number of the third criterion, carrying no claim of its own
  - S26 => P3
  - S27 => not-testable: the number of the fourth criterion, carrying no claim of its own
  - S28 => P4
  - S29 => P4
  - S30 => not-testable: points at the lines of the authority this rule comes from
  - S31 => not-testable: states that this work waits for no other delivery
  - S32 => not-testable: states the size of the delivery, which no answer of the tool shows
  - S33 => not-testable: names the files the change is expected to touch, read from the diff
  - S34 => not-testable: says why the expectation is real, a fact about the trace table
- **scenarios**:
  - SC1 | P1 | GIVEN a function "twice" that declares no requires block at all | WHEN the program is checked | THEN the report records the precondition of "twice" as "omitted"
  - SC2 | P2 | GIVEN a function "twice" whose ensures block is written as the literal true | WHEN the program is checked | THEN the report records the postcondition of "twice" as "trivial"
  - SC3 | P3 | GIVEN "twice" with (requires (> n 0)) and (ensures (= result (* n 2))) | WHEN the program is checked | THEN neither of its 2 blocks is recorded as omitted or trivial
  - SC4 | P3 | GIVEN the shipped hour clock, whose 3 functions write 3 blocks and leave 3 absent | WHEN the program is checked | THEN valid-state reads "omitted"/"omitted", initial reads "omitted"/"stated" and step reads "stated"/"stated"
  - SC5 | P4 | GIVEN 2 functions whose 4 contract blocks are all absent or written as the literal true | WHEN the program is checked | THEN the report says states_a_contract is false and no word of the whole answer calls the program correct or meaningful
  - SC6 | P5 | GIVEN a request naming the operation "discover" and carrying no other field | WHEN the manifest is asked for | THEN it publishes the 3 entry fields, the 3 strengths, the totals fields and the list of operations whose answer carries the report
- **conflicts**:
  - S1 | NONE | ran the suite command named here and read its 1045 passing tests before writing anything
  - S2 | NONE | read SPEC.md lines 204 to 206, which ask reports to identify omitted and trivial contracts
  - S3 | NONE | this change adds files under tests and edits no existing test and no line of SPEC.md
  - S4 | NONE | searched the suite for a test pinning the key set of a check or discover answer and found none
  - S5 | NONE | the .relay directory is untouched and nothing here reads it
  - S6 | NONE | every edit of this change is made inside the worktree named by the task
  - S7 | NONE | nothing in the repository constrains the commit message beyond this line
  - S8 | NONE | the worktree has no commit-msg hook that would refuse this attribution line
  - S9 | NONE | nothing in this change pushes or merges, and no hook here does either
  - S10 | NONE | the suite was green before this change and the new field adds a key no existing test pins
  - S11 | NONE | read _run_check and _run_discover: one new key in each is enough, the rule itself lives in checker.py
  - S12 | NONE | read obligations.py and the diagnostic kinds table in checker.py before choosing where the rule lives
  - S13 | NONE | read the answers of check and of verify: verify already says nothing was attempted, check is the clean answer at risk
  - S14 | NONE | the only scripts of this run live under the workspace directory of this run
  - S15 | NONE | every nwstep argument of this run is passed from a script file with single quotes
  - S16 | NONE | no answer of the tool records today which functions promise nothing, so nothing contradicts it
  - S17 | NONE | the check answer today carries only a claim of a static check over this input
  - S18 | NONE | a heading contradicts no behaviour the tool already has
  - S19 | NONE | a list number contradicts no behaviour the tool already has
  - S20 | NONE | checked that a program with no requires block is accepted today and carries no report
  - S21 | NONE | the word omitted is used by no answer of the tool today, so it collides with nothing
  - S22 | NONE | a list number contradicts no behaviour the tool already has
  - S23 | NONE | checked that (ensures true) is accepted today, with no word about how much it promises
  - S24 | NONE | the word trivial is used by no answer of the tool today, so it collides with nothing
  - S25 | NONE | a list number contradicts no behaviour the tool already has
  - S26 | NONE | a real contract is accepted today exactly as an empty one is, which is the gap this rule closes
  - S27 | NONE | a list number contradicts no behaviour the tool already has
  - S28 | NONE | checked a program whose every block is empty: it is answered completed, with a static check claim
  - S29 | NONE | read the existing wording rules: the evaluate claim scan forbids these words already and check uses none
  - S30 | NONE | read those lines of SPEC.md and the rule here says what they ask for
  - S31 | NONE | nothing in this change waits for another delivery or reads its files
  - S32 | NONE | the size of the delivery contradicts no behaviour of the tool
  - S33 | NONE | both named files exist and the rule fits checker.py beside the other whole-program rules
  - S34 | NONE | read docs/spec-trace.md row 4.3, which records this reports obligation as missing today
- **decisions**:
  - DEC1: the report is carried by the answer of check and by no other operation. check is the answer whose completed status a reader can mistake for a meaningful result, the criteria say when the program is checked, and the verify answer already states that nothing was attempted. The owner is absent, so this is the executor decision.
  - DEC2: a block whose every clause is the literal true is recorded trivial, and a block holding one clause that is not the literal true is recorded stated, because SPEC.md reads the clauses of a block as a conjunction and a conjunction with one real clause promises that clause.
  - DEC3: an empty block written as (requires) is recorded omitted, because the parsed program keeps no mark that tells it from an absent block; this limit is written in the documents.
  - DEC4: triviality is recognised only for the literal true, as SPEC.md asks for explicitly trivial contracts; a clause such as (or p (not p)) is recorded stated and that limit is written in the documents.
- **mapping**:
  - P1 => test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted
  - P2 => test_a_postcondition_written_as_true_is_recorded_as_trivial
  - P3 => test_a_function_with_a_real_contract_is_recorded_as_neither
  - P4 => test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct
  - P5 => test_the_manifest_says_what_the_report_holds_and_which_answer_carries_it
- **covers_scenarios**:
  - SC1 => test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted
  - SC2 => test_a_postcondition_written_as_true_is_recorded_as_trivial
  - SC3 => test_a_function_with_a_real_contract_is_recorded_as_neither
  - SC4 => test_the_shipped_hour_clock_reads_the_way_a_human_reads_it
  - SC5 => test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct
  - SC6 => test_the_manifest_says_what_the_report_holds_and_which_answer_carries_it
- **predictions**:
  - C1 => base differs
  - C2 => base differs
  - C3 => base differs
  - C4 => base held
- **interfaces**:
  - I1: the check operation of the prova command, asked over JSON on stdin and answered on stdout
  - I2: the discover operation of the same command, which publishes what the tool answers and in which shape
- **matrix**:
  - I1.empty => a source holding no declaration at all => refused as invalid_program by the rule that is already there, and the refusal carries no report
  - I1.unknown => a source calling a function nothing declares => refused as invalid_program, and the refusal carries no report
  - I1.malformed => a source with an unclosed parenthesis => refused as invalid_program with a syntax diagnostic, and no report
  - I1.dependency-gone => n/a: check reads only the characters the request carries and opens no file, service or process
  - I1.repeated => the same source checked twice in a row => the same report twice, since the operation keeps nothing between two requests
  - I1.concurrent => two checks of two different sources at once => each answers about its own text, since the operation keeps no state
  - I1.crash => n/a: check writes nothing anywhere, so an interrupted run leaves no half written report behind
  - I2.empty => a request naming discover and carrying no other field => the manifest, including the published shape of the report
  - I2.unknown => a request naming discover and carrying a field the tool does not read => the same manifest, the extra field ignored
  - I2.malformed => n/a: discover reads no source, so there is no text of a program for it to find malformed
  - I2.dependency-gone => n/a: the manifest is read from the tables in the tool itself and from no file or service
  - I2.repeated => the manifest asked for twice => the same answer twice, since it is read from the tables in the tool
  - I2.concurrent => two manifests asked for at once => the same answer to each, since the manifest reads nothing that changes
  - I2.crash => n/a: discover writes nothing anywhere, so an interrupted run leaves nothing behind
- **laws**:
  - LAW1 | every block is recorded with the strength of its own text: absent is omitted, every clause the literal true is trivial, and one clause that is not the literal true is stated | generator=test_every_block_is_recorded_with_the_strength_its_own_text_has | observation=the entries of the report equal the strengths the plan wrote for each generated function | mutant=reading only the first clause of a block records (ensures true (= result (* n 2))) as trivial
  - LAW2 | the report names every declared function exactly once, in the order the program declares them | generator=test_the_report_names_every_declared_function_once_in_declaration_order | observation=the names listed by the report equal the names the plan declared, in that order | mutant=walking the functions of the program as a set drops the declaration order
  - LAW3 | the report says the program states a contract exactly when at least one block of one function is stated | generator=test_the_program_states_a_contract_exactly_when_one_block_says_something | observation=the states_a_contract field equals whether any generated block was written as a stated one | mutant=reading the flag from the preconditions alone misses a program whose only promise is a postcondition
  - LAW4 | the counts partition the blocks: omitted, trivial and stated sum back to two per declared function and agree with the listed entries | generator=test_the_counts_partition_the_blocks_of_the_declared_functions | observation=the three counts equal the counts of the plan and their sum is twice the number of declared functions | mutant=counting a function once instead of its two blocks makes the parts stop summing to the whole
- **messages**:
  - MSG1 | a strength built from the word meaningful, which the tool does not publish | the word is not one of the three strengths a report may record | a reader of an answer must be able to look up every word in it in the manifest | use omitted, trivial or stated, or publish the new word in the manifest first | test=test_a_strength_the_tool_does_not_publish_is_refused
  - MSG2 | a report built from two entries that both name the function twice | one function is recorded twice in one report | a reader counts each declared function once, and a repeated entry makes the totals unreadable | record one entry per declared function, as the walk over the declared functions does | test=test_one_function_recorded_twice_in_one_report_is_refused
- **red**: `uv run pytest -q tests/acceptance/test_f13_b1_a_function_without_a_precondition_is_recorded_as_omitted.py tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py tests/acceptance/test_f13_b4_a_program_that_promises_nothing_is_not_called_meaningful.py tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py tests/properties/test_f13_contract_report_laws.py tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py` exited 1 in 17.185s
  - failing on the pre-feature tree (20): tests/acceptance/test_f13_b1_a_function_without_a_precondition_is_recorded_as_omitted.py::test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted, tests/acceptance/test_f13_b1_a_function_without_a_precondition_is_recorded_as_omitted.py::test_a_demand_the_function_states_is_not_recorded_as_omitted, tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py::test_a_postcondition_written_as_true_is_recorded_as_trivial, tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py::test_a_postcondition_that_states_a_relation_is_not_recorded_as_trivial, tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py::test_a_block_written_as_true_reads_differently_from_a_block_never_written, tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py::test_a_function_with_a_real_contract_is_recorded_as_neither, tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py::test_the_shipped_hour_clock_reads_the_way_a_human_reads_it, tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py::test_the_totals_count_every_block_of_every_declared_function, tests/acceptance/test_f13_b4_a_program_that_promises_nothing_is_not_called_meaningful.py::test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct, tests/acceptance/test_f13_b4_a_program_that_promises_nothing_is_not_called_meaningful.py::test_a_program_that_states_a_contract_is_told_apart_from_one_that_does_not, tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py::test_the_manifest_says_what_the_report_holds_and_which_answer_carries_it, tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py::test_every_answer_carries_the_report_exactly_where_the_manifest_says, tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py::test_every_word_and_field_the_report_uses_is_one_the_manifest_publishes, tests/properties/test_f13_contract_report_laws.py::test_every_block_is_recorded_with_the_strength_its_own_text_has, tests/properties/test_f13_contract_report_laws.py::test_the_report_names_every_declared_function_once_in_declaration_order, tests/properties/test_f13_contract_report_laws.py::test_the_program_states_a_contract_exactly_when_one_block_says_something, tests/properties/test_f13_contract_report_laws.py::test_the_counts_partition_the_blocks_of_the_declared_functions, tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py::test_a_strength_the_tool_does_not_publish_is_refused, tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py::test_one_function_recorded_twice_in_one_report_is_refused, tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py::test_a_report_about_two_functions_reads_back_both_of_them
  - tests (read from the run): 20 failed, 1 passed in 16.73s
  ```text
                  _contracts_of("twice", "omitted", "trivial"),
                  _contracts_of("thrice", "stated", "stated"),
              )
          )

  tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py:85:
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

      def _report():
          kind = getattr(checker, "ContractReport", None)
  >       assert kind is not None, (
              "the checker has no value holding the contract report, so nothing "
              "can say which functions promise nothing."
          )
  E       AssertionError: the checker has no value holding the contract report, so nothing can say which functions promise nothing.
  E       assert None is not None

  tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py:33: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f13_b1_a_function_without_a_precondition_is_recorded_as_omitted.py::test_a_function_that_demands_nothing_has_its_precondition_recorded_as_omitted
  FAILED tests/acceptance/test_f13_b1_a_function_without_a_precondition_is_recorded_as_omitted.py::test_a_demand_the_function_states_is_not_recorded_as_omitted
  FAILED tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py::test_a_postcondition_written_as_true_is_recorded_as_trivial
  FAILED tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py::test_a_postcondition_that_states_a_relation_is_not_recorded_as_trivial
  FAILED tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py::test_a_block_written_as_true_reads_differently_from_a_block_never_written
  FAILED tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py::test_a_function_with_a_real_contract_is_recorded_as_neither
  FAILED tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py::test_the_shipped_hour_clock_reads_the_way_a_human_reads_it
  FAILED tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py::test_the_totals_count_every_block_of_every_declared_function
  FAILED tests/acceptance/test_f13_b4_a_program_that_promises_nothing_is_not_called_meaningful.py::test_a_program_whose_every_contract_is_empty_is_not_called_meaningfully_correct
  FAILED tests/acceptance/test_f13_b4_a_program_that_promises_nothing_is_not_called_meaningful.py::test_a_program_that_states_a_contract_is_told_apart_from_one_that_does_not
  FAILED tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py::test_the_manifest_says_what_the_report_holds_and_which_answer_carries_it
  FAILED tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py::test_every_answer_carries_the_report_exactly_where_the_manifest_says
  FAILED tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py::test_every_word_and_field_the_report_uses_is_one_the_manifest_publishes
  FAILED tests/properties/test_f13_contract_report_laws.py::test_every_block_is_recorded_with_the_strength_its_own_text_has
  FAILED tests/properties/test_f13_contract_report_laws.py::test_the_report_names_every_declared_function_once_in_declaration_order
  FAILED tests/properties/test_f13_contract_report_laws.py::test_the_program_states_a_contract_exactly_when_one_block_says_something
  FAILED tests/properties/test_f13_contract_report_laws.py::test_the_counts_partition_the_blocks_of_the_declared_functions
  FAILED tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py::test_a_strength_the_tool_does_not_publish_is_refused
  FAILED tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py::test_one_function_recorded_twice_in_one_report_is_refused
  FAILED tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py::test_a_report_about_two_functions_reads_back_both_of_them
  20 failed, 1 passed in 16.73s
  ```

## 3. craft: Craft the change (revision 2)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 122.195s
  - tests (read from the run): 1067 passed in 122.06s
  - slowest: 6.78s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.40s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.93s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.40s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.74s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 2.00s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.65s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.57s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.44s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  - slowest: 1.43s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  ```text
  ........................................................................ [  6%]
  ........................................................................ [ 13%]
  ........................................................................ [ 20%]
  ........................................................................ [ 26%]
  ........................................................................ [ 33%]
  ........................................................................ [ 40%]
  ........................................................................ [ 47%]
  ........................................................................ [ 53%]
  ........................................................................ [ 60%]
  ........................................................................ [ 67%]
  ........................................................................ [ 74%]
  ........................................................................ [ 80%]
  ........................................................................ [ 87%]
  ........................................................................ [ 94%]
  ...........................................................              [100%]
  ============================= slowest 10 durations =============================
  6.78s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.40s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.93s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.40s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.74s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  2.00s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.65s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.57s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.44s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1.43s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1067 passed in 122.06s (0:02:02)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.057s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this environment, checked from a shell command and from a login shell; the client answered exit 3 before any question was sent, so the two open choices were decided locally and recorded as DEC1 and DEC2 of the oracle step
