# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1153 tests, all green on main).
  - not-testable (challenge this): names the project, its test command and the green suite this work starts from; context, not an outcome a caller can observe
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority behind every promise; a source of the promises, not one of them
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on this delivery, read from the diff rather than from any run of the tool
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): tells me what to do when an existing test disagrees; a process rule that shapes the conflict table below
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): names a directory to leave alone; nothing a caller of the tool can observe
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): says where the work happens; read from the worktree, not from the tool
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a rule about the commit message, read from the git history
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the line the commit message ends with, read from the git history
- S9: Do not push and do not merge.
  - not-testable (challenge this): forbids pushing and merging; read from the git history and the remote
- S10: Keep the full suite green.
  - not-testable (challenge this): requires the whole suite to stay green; a run of the suite, not a promise of the tool
- S11: Another delivery (F12, `parse` and its tree, in tree.py, syntax.py, reader.py and the dispatch in service.py) runs in parallel in a different worktree and will merge first or second; keep your service.py and __main__.py edits small and local.
  - not-testable (challenge this): asks me to keep two files lightly edited while another delivery runs; read from the diff
- S12: Existing limits you must build on, not duplicate: R1 added the published `resource_limits` block with `expression_nesting` (128 forms, `nesting_limit_exceeded`) and `evaluation_depth` (160 steps, `evaluation_depth_exceeded`), both answered with status `resource_exhausted` and a located refusal, and F11 published `resource_limits` and `statuses` through manifest.py.
  - promises: P7
  - tests P7: test_the_budgets_stand_in_the_same_block_as_the_limits
- S13: Owner decision D5: budgets are 1 MiB input, 10 s time, 512 MiB memory, 1 MiB output; the numbers are to be measured on CI first (the owner approved the product owner recommendation: read section 5 D5 and section 8 of docs/ROADMAP.md for the exact words), so publish them as the declared budgets, make them injectable in tests (a small limits object the tests can shrink; never make a test wait seconds or allocate hundreds of MiB), and say in your oracle note what is measured and what is only declared.
  - promises: P1, P6
  - tests P1: test_every_operation_this_tool_offers_states_four_budgets
  - tests P6: test_a_budget_a_caller_cannot_set_is_refused_by_name
- S14: A budget refusal must claim nothing semantic and must never describe the program domain as bounded (SPEC.md lines 503-508 and 280-284).
  - promises: P4
  - tests P4: test_a_run_stopped_by_a_budget_reports_only_that_budget
- S15: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell hygiene for the recording tool; nothing a caller of the compiler can observe
- S16: **Outcome.** Every operation declares an input, time, memory and output budget, and
  - promises: P1
  - tests P1: test_every_operation_this_tool_offers_states_four_budgets
- S17: exceeding one gives a clean diagnostic instead of a hang or a crash.
  - promises: P2, P3, P8, P9
  - tests P2: test_a_source_past_the_budget_a_caller_set_is_refused_by_name
  - tests P3: test_a_run_with_no_time_left_is_answered_with_the_time_budget
  - tests P8: test_an_answer_one_byte_too_large_is_replaced_by_the_budget_refusal
  - tests P9: test_a_run_whose_memory_is_already_past_the_budget_is_refused
- S18: **Acceptance criteria**
  - not-testable (challenge this): a heading introducing the criteria that follow
- S19: 1.
  - not-testable (challenge this): the number of the first acceptance criterion
- S20: Given `discover`, when it runs, then each operation's input, time, memory and
  - promises: P1
  - tests P1: test_every_operation_this_tool_offers_states_four_budgets
- S21: output budgets are stated and marked enforced.
  - promises: P1
  - tests P1: test_every_operation_this_tool_offers_states_four_budgets
- S22: 2.
  - not-testable (challenge this): the number of the second acceptance criterion
- S23: Given a source larger than the input budget, then the operation is refused for
  - promises: P2
  - tests P2: test_a_source_past_the_budget_a_caller_set_is_refused_by_name
- S24: exhausting that budget and names which one.
  - promises: P2
  - tests P2: test_a_source_past_the_budget_a_caller_set_is_refused_by_name
- S25: 3.
  - not-testable (challenge this): the number of the third acceptance criterion
- S26: Given work that exceeds the time budget, then the answer is a budget diagnostic,
  - promises: P3
  - tests P3: test_a_run_with_no_time_left_is_answered_with_the_time_budget
- S27: not a partial result and not a hang.
  - promises: P3
  - tests P3: test_a_run_with_no_time_left_is_answered_with_the_time_budget
- S28: 4.
  - not-testable (challenge this): the number of the fourth acceptance criterion
- S29: Given a budget refusal, then nothing in the answer claims a semantic result, and
  - promises: P4
  - tests P4: test_a_run_stopped_by_a_budget_reports_only_that_budget
- S30: the program's mathematical domain is not described as bounded.
  - promises: P4
  - tests P4: test_a_run_stopped_by_a_budget_reports_only_that_budget
- S31: 5.
  - not-testable (challenge this): the number of the fifth acceptance criterion
- S32: Given a program well inside every budget, then it completes normally.
  - promises: P5
  - tests P5: test_a_program_inside_every_budget_is_evaluated_and_answered
- S33: **SPEC.md** lines 503-508, 280-284.
  - not-testable (challenge this): cites the lines of SPEC.md the promises are drawn from
- S34: **Dependencies** D5.
  - not-testable (challenge this): names the Owner decision this work depends on
- S35: **Size** M.
  - not-testable (challenge this): states the size of the delivery; a planning fact
- S36: **Touches** `src/prova/service.py`, `src/prova/__main__.py`, tests.
  - not-testable (challenge this): names the files the work was expected to touch; read from the diff
- S37: **Why it is a real expectation** probe S7 shows `enforced: false`.
  - not-testable (challenge this): says why the expectation is real by citing an earlier probe of the tool

## Edge matrix

- I1.empty: a request whose source is the empty text, nothing lowered => answered as before: the text declares nothing and is refused by that rule of the language, not by a budget | self-probe: not probed | pre-feature not probed
- I1.unknown: a request naming an operation this tool does not have, carrying a source of 2 MiB => answered unavailable as before: no source is read, so no input budget is counted over it | self-probe: not probed | pre-feature not probed
- I1.malformed: text that is not JSON at all => answered invalid_input as before: the input budget sizes the program a request carries, not the text of the request | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: the platform offers no reading of this process's peak memory => the memory budget states enforced false with the reason, the other three are unchanged, and no run is refused for memory | self-probe: not probed | pre-feature not probed
- I1.repeated: the same request sent twice under the same lowered budget => the same refusal both times: the command keeps nothing between runs | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): each run is its own process, writing no file and sharing no state, so no overlap between two runs is observable from outside
- I1.crash: n/a (challenge this): the command writes no file and keeps nothing, so a kill leaves nothing half written for a later run to find
- I2.empty: a discover request carrying no other field => the budgets of every offered operation are stated, as the operation takes nothing else | self-probe: not probed | pre-feature not probed
- I2.unknown: a caller looks for a budget name the manifest does not state => it finds the 4 published names and nothing else; an unknown name is simply absent | self-probe: not probed | pre-feature not probed
- I2.malformed: n/a (challenge this): the manifest is written by the tool from one budgets object, and a caller sends no manifest of its own
- I2.dependency-gone: the platform offers no reading of peak memory => the memory entry itself says enforced false and why, so a caller reads the gap instead of trusting a budget | self-probe: not probed | pre-feature not probed
- I2.repeated: the discover operation run twice => the same block both times, number for number: it is built from one object and reads nothing else | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): reading the manifest changes nothing, and two readers share nothing to race over
- I2.crash: n/a (challenge this): the manifest is built fresh in each run, so a kill leaves nothing behind to repair
- I3.empty: a variable set to the empty text => refused by name: a caller that believes it lowered a budget and did not would read the run that follows as proof that its work fits | self-probe: not probed | pre-feature not probed
- I3.unknown: PROVA_BUDGET_DISK_SIZE=5, a budget name this tool does not publish => refused by name, so a mistyped budget never quietly does nothing | self-probe: not probed | pre-feature not probed
- I3.malformed: ten, -1, 1.5, or 10001 against a stated maximum of 10000 => refused by name, saying a whole number no larger than the stated maximum is read | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): the variables are read from this process's own environment, and there is nothing else for them to depend on
- I3.repeated: the same variable written twice in one environment => the environment keeps one value per name, so the tool reads one value and answers once | self-probe: not probed | pre-feature not probed
- I3.concurrent: two runs at once, each lowering a different budget => each reads its own environment and answers its own budget; nothing is shared between them | self-probe: not probed | pre-feature not probed
- I3.crash: n/a (challenge this): setting a variable changes nothing the tool keeps, so a kill leaves nothing to repair

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the tool as this repository ships it, offering 5 operations
  - WHEN a caller runs the "discover" operation
  - THEN each of the 5 operations states an "input_size", "operation_time", "peak_memory" and "answer_size" budget, every one of them marked enforced
  - test: test_every_operation_this_tool_offers_states_four_budgets
- SC2 (P1): not-held (no held self-probe case)
  - GIVEN the numbers the Owner decided for D5: 1 MiB of source, 10 s, 512 MiB of memory and 1 MiB of answer
  - WHEN a caller reads the stated budgets
  - THEN the maximums are 1048576, 10000, 536870912 and 1048576, and each says its basis is "declared", not measured
  - test: test_the_stated_numbers_are_the_ones_the_owner_decided_and_say_so
- SC3 (P2): not-held (no held self-probe case)
  - GIVEN a source of 200 bytes and an input budget the caller lowered to 64
  - WHEN the caller checks that source
  - THEN status "resource_exhausted" with one "input_budget_exceeded" refusal naming "input_size", 64 allowed beside 200 sent
  - test: test_a_source_past_the_budget_a_caller_set_is_refused_by_name
- SC4 (P2): not-held (no held self-probe case)
  - GIVEN a source of 1048577 bytes and nothing lowered
  - WHEN the caller checks that source
  - THEN it is refused for "input_size" with 1048576 allowed beside 1048577 sent, and the answer carries no result
  - test: test_a_source_past_the_declared_budget_is_refused_with_no_budget_lowered
- SC5 (P3): not-held (no held self-probe case)
  - GIVEN the hour clock with its 8 declared examples and a time budget lowered to 0
  - WHEN the caller asks the tool to run those examples
  - THEN one "time_budget_exceeded" refusal naming "operation_time", no list of examples in the answer, and the command comes back
  - test: test_a_run_with_no_time_left_is_answered_with_the_time_budget
- SC6 (P9): not-held (no held self-probe case)
  - GIVEN a memory budget the caller lowered to 1 byte
  - WHEN the caller checks the 1474 byte hour clock
  - THEN one "memory_budget_exceeded" refusal naming "peak_memory", 1 allowed beside the memory already taken
  - test: test_a_run_whose_memory_is_already_past_the_budget_is_refused
- SC7 (P8): not-held (no held self-probe case)
  - GIVEN an answer budget 1 byte under the size of the manifest
  - WHEN the caller asks for the manifest
  - THEN one "output_budget_exceeded" refusal naming "answer_size", and no part of the manifest in the printed text
  - test: test_an_answer_one_byte_too_large_is_replaced_by_the_budget_refusal
- SC8 (P4): not-held (no held self-probe case)
  - GIVEN one run stopped by each of the 4 budgets
  - WHEN the caller reads each answer
  - THEN none of the 4 carries "claim", "result" or "source_digest", and no refusal says "bounded", "domain", "verified" or "proved"
  - test: test_a_run_stopped_by_a_budget_reports_only_that_budget
- SC9 (P5): not-held (no held self-probe case)
  - GIVEN the 1474 byte hour clock, far inside every stated budget
  - WHEN the caller steps it from "(Clock 11)"
  - THEN status "completed" with the value "(Outcome (Clock 12) true)" and 0 diagnostics
  - test: test_a_program_inside_every_budget_is_evaluated_and_answered
- SC10 (P7): not-held (no held self-probe case)
  - GIVEN a caller that read a nesting limit of 128 forms and an evaluation depth of 160 steps before this change
  - WHEN it reads the resource limits now
  - THEN both numbers are unchanged, with their categories, and the 4 budgets stand in that same block
  - test: test_the_budgets_stand_in_the_same_block_as_the_limits
- SC11 (P6): not-held (no held self-probe case)
  - GIVEN the name "PROVA_BUDGET_INPUT_SIZE" that the manifest publishes for lowering the input budget
  - WHEN a caller sets it to 50 and sends a source of 300 bytes
  - THEN the run is refused for "input_size" with 50 allowed, so the published name is the name the tool reads
  - test: test_the_published_way_to_lower_a_budget_is_the_way_that_works
- SC12 (P6): not-held (no held self-probe case)
  - GIVEN a caller that wrote the time budget as "ten"
  - WHEN it sends any request
  - THEN status "invalid_input" with one "malformed_request" refusal naming that variable and quoting "ten" back, and no result
  - test: test_a_budget_a_caller_cannot_set_is_refused_by_name

## Questions for the owner

- none

## Observed side effects (git, BASE to HEAD)

- A conformance/parse/comments.prova (+3 -0 lines)
- A conformance/parse/comments.tree.json (+28 -0 lines)
- A conformance/parse/let-and-match.prova (+6 -0 lines)
- A conformance/parse/let-and-match.tree.json (+77 -0 lines)
- A conformance/parse/record-and-function.prova (+5 -0 lines)
- A conformance/parse/record-and-function.tree.json (+45 -0 lines)
- A docs/feature/budgets/craft.md (+144 -0 lines)
- A docs/feature/budgets/design.md (+129 -0 lines)
- A docs/feature/budgets/oracle.md (+121 -0 lines)
- A docs/feature/published-tree/craft.md (+83 -0 lines)
- A docs/feature/published-tree/design.md (+69 -0 lines)
- A docs/feature/published-tree/handoff.md (+53 -0 lines)
- A docs/feature/published-tree/oracle.md (+62 -0 lines)
- A docs/published-tree/DECISIONS.md (+20 -0 lines)
- A docs/published-tree/SUMMARY.md (+699 -0 lines)
- A docs/published-tree/TRACE.md (+5 -0 lines)
- M src/prova/__main__.py (+48 -6 lines)
- A src/prova/budgets.py (+631 -0 lines)
- M src/prova/checker.py (+47 -17 lines)
- M src/prova/evaluator.py (+5 -3 lines)
- M src/prova/manifest.py (+18 -1 lines)
- M src/prova/obligations.py (+4 -3 lines)
- M src/prova/reader.py (+53 -6 lines)
- M src/prova/service.py (+138 -21 lines)
- M src/prova/syntax.py (+123 -25 lines)
- A src/prova/tree.py (+486 -0 lines)
- A tests/acceptance/_f12_tree_fixtures.py (+137 -0 lines)
- A tests/acceptance/_f14_budget_fixtures.py (+341 -0 lines)
- A tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py (+130 -0 lines)
- A tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py (+128 -0 lines)
- A tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py (+91 -0 lines)
- A tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py (+103 -0 lines)
- A tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py (+96 -0 lines)
- A tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py (+61 -0 lines)
- A tests/acceptance/test_f14_b10_a_request_too_long_to_read_is_refused_unread.py (+180 -0 lines)
- A tests/acceptance/test_f14_b1_every_operation_states_its_four_budgets.py (+137 -0 lines)
- A tests/acceptance/test_f14_b2_a_source_past_the_input_budget_is_refused.py (+90 -0 lines)
- A tests/acceptance/test_f14_b3_work_past_the_time_budget_is_answered_not_left_running.py (+75 -0 lines)
- A tests/acceptance/test_f14_b4_a_run_past_the_memory_budget_is_refused.py (+90 -0 lines)
- A tests/acceptance/test_f14_b5_an_answer_past_the_output_budget_is_refused.py (+101 -0 lines)
- A tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py (+80 -0 lines)
- A tests/acceptance/test_f14_b7_a_program_inside_every_budget_is_answered_as_before.py (+111 -0 lines)
- A tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py (+137 -0 lines)
- A tests/acceptance/test_f14_b9_the_limits_published_before_still_stand.py (+75 -0 lines)
- A tests/properties/_f14_budget_client.py (+122 -0 lines)
- M tests/properties/test_f11_manifest_laws.py (+1 -0 lines)
- A tests/properties/test_f12_published_tree_laws.py (+246 -0 lines)
- A tests/properties/test_f14_budget_laws.py (+188 -0 lines)
- A tests/unit/test_a_part_of_a_program_cannot_stand_nowhere.py (+54 -0 lines)
- M tests/unit/test_obligation_inventory_refuses_what_it_cannot_list.py (+4 -2 lines)
- M tests/unit/test_service_discover.py (+1 -1 lines)

## Commits (git log, BASE to HEAD)

- 5a60586 Let every part of a read program say where it stands
- e5d9c2d Refuse a part of a read program that cannot say where it stands
- 2fc9a5f Say what reading a program must answer, before it answers it
- 678936f Expect the manifest to advertise reading a program
- 2893245 Write down where the published tree comes from
- 5661c47 Answer a read program with the tree the tool built
- da59b66 Hand out the comments at the end of a document once
- 6ff4a1a Observe the promises a reader found nothing watching
- 36657c2 Say what the review found and what was done about it
- e14cfed Say where a program built by hand stands
- 7903daa Refuse a signature, an example or a function with no place
- 8d869be Publish what reading a program takes and what it answers
- 5851fe7 Hold reading a program to the laws every operation obeys
- c28a3db Say how reading a program stands in the manifest now
- ab28b70 Fix where a let, a match and its patterns stand
- ed403e3 Observe that a part of a program cannot stand nowhere
- 4e4bf34 Close the gap a repair left in the published table
- 16175eb Record the delivery and what it leaves unverified
- 04d4101 Say what the budgets must do, in tests that fail without them
- 1040097 Write down who owns each budget and where a run is measured
- b639ab5 Stop a run inside the budget it passed, and say which one
- 6d72ada Record what the budget work ran and what it leaves declared
- 6c44a68 Refuse a budget written in any other digits, and stop reading a request this tool cannot answer
- 553ad68 Observe the memory a refused request costs, and bring the documents back in step
- 5c2a473 Record what the review found, what it cost in memory, and what proved it
- ea3a64c Say which outcomes the review added, and how many cases cover them

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f14/request.md
- **promises**:
  - P1: A caller reading the manifest sees, for every operation this tool offers, the input, time, memory and answer budget it runs under, each marked enforced.
  - P2: A caller that sends a source larger than the input budget is refused for that budget by name, with the size allowed beside the size sent.
  - P3: A run that has no time left is answered with the time budget, not with half an answer and not with a command that never comes back.
  - P4: A budget refusal reports the budget and nothing about the program: no claim, no result, no digest of the source, and no word that makes the mathematics of the program a matter of this tool's budgets.
  - P5: A program well inside every budget is answered exactly as it was answered before any budget was declared.
  - P6: A caller lowers any budget for one run the way the manifest publishes, and a budget it cannot set is refused by name instead of quietly ignored.
  - P7: The nesting limit and the evaluation depth published before stand unchanged, and the four budgets join them in the same block.
  - P8: A caller whose answer would be larger than the answer budget gets one complete refusal naming that budget, never part of the answer it asked for.
  - P9: A run that has taken more memory than its budget allows is refused for the memory budget by name.
- **sentence_map**:
  - S1 => not-testable: names the project, its test command and the green suite this work starts from; context, not an outcome a caller can observe
  - S2 => not-testable: names SPEC.md as the authority behind every promise; a source of the promises, not one of them
  - S3 => not-testable: a constraint on this delivery, read from the diff rather than from any run of the tool
  - S4 => not-testable: tells me what to do when an existing test disagrees; a process rule that shapes the conflict table below
  - S5 => not-testable: names a directory to leave alone; nothing a caller of the tool can observe
  - S6 => not-testable: says where the work happens; read from the worktree, not from the tool
  - S7 => not-testable: a rule about the commit message, read from the git history
  - S8 => not-testable: the line the commit message ends with, read from the git history
  - S9 => not-testable: forbids pushing and merging; read from the git history and the remote
  - S10 => not-testable: requires the whole suite to stay green; a run of the suite, not a promise of the tool
  - S11 => not-testable: asks me to keep two files lightly edited while another delivery runs; read from the diff
  - S12 => P7
  - S13 => P1,P6
  - S14 => P4
  - S15 => not-testable: shell hygiene for the recording tool; nothing a caller of the compiler can observe
  - S16 => P1
  - S17 => P2,P3,P8,P9
  - S18 => not-testable: a heading introducing the criteria that follow
  - S19 => not-testable: the number of the first acceptance criterion
  - S20 => P1
  - S21 => P1
  - S22 => not-testable: the number of the second acceptance criterion
  - S23 => P2
  - S24 => P2
  - S25 => not-testable: the number of the third acceptance criterion
  - S26 => P3
  - S27 => P3
  - S28 => not-testable: the number of the fourth acceptance criterion
  - S29 => P4
  - S30 => P4
  - S31 => not-testable: the number of the fifth acceptance criterion
  - S32 => P5
  - S33 => not-testable: cites the lines of SPEC.md the promises are drawn from
  - S34 => not-testable: names the Owner decision this work depends on
  - S35 => not-testable: states the size of the delivery; a planning fact
  - S36 => not-testable: names the files the work was expected to touch; read from the diff
  - S37 => not-testable: says why the expectation is real by citing an earlier probe of the tool
- **scenarios**:
  - SC1 | P1 | GIVEN the tool as this repository ships it, offering 5 operations | WHEN a caller runs the "discover" operation | THEN each of the 5 operations states an "input_size", "operation_time", "peak_memory" and "answer_size" budget, every one of them marked enforced
  - SC2 | P1 | GIVEN the numbers the Owner decided for D5: 1 MiB of source, 10 s, 512 MiB of memory and 1 MiB of answer | WHEN a caller reads the stated budgets | THEN the maximums are 1048576, 10000, 536870912 and 1048576, and each says its basis is "declared", not measured
  - SC3 | P2 | GIVEN a source of 200 bytes and an input budget the caller lowered to 64 | WHEN the caller checks that source | THEN status "resource_exhausted" with one "input_budget_exceeded" refusal naming "input_size", 64 allowed beside 200 sent
  - SC4 | P2 | GIVEN a source of 1048577 bytes and nothing lowered | WHEN the caller checks that source | THEN it is refused for "input_size" with 1048576 allowed beside 1048577 sent, and the answer carries no result
  - SC5 | P3 | GIVEN the hour clock with its 8 declared examples and a time budget lowered to 0 | WHEN the caller asks the tool to run those examples | THEN one "time_budget_exceeded" refusal naming "operation_time", no list of examples in the answer, and the command comes back
  - SC6 | P9 | GIVEN a memory budget the caller lowered to 1 byte | WHEN the caller checks the 1474 byte hour clock | THEN one "memory_budget_exceeded" refusal naming "peak_memory", 1 allowed beside the memory already taken
  - SC7 | P8 | GIVEN an answer budget 1 byte under the size of the manifest | WHEN the caller asks for the manifest | THEN one "output_budget_exceeded" refusal naming "answer_size", and no part of the manifest in the printed text
  - SC8 | P4 | GIVEN one run stopped by each of the 4 budgets | WHEN the caller reads each answer | THEN none of the 4 carries "claim", "result" or "source_digest", and no refusal says "bounded", "domain", "verified" or "proved"
  - SC9 | P5 | GIVEN the 1474 byte hour clock, far inside every stated budget | WHEN the caller steps it from "(Clock 11)" | THEN status "completed" with the value "(Outcome (Clock 12) true)" and 0 diagnostics
  - SC10 | P7 | GIVEN a caller that read a nesting limit of 128 forms and an evaluation depth of 160 steps before this change | WHEN it reads the resource limits now | THEN both numbers are unchanged, with their categories, and the 4 budgets stand in that same block
  - SC11 | P6 | GIVEN the name "PROVA_BUDGET_INPUT_SIZE" that the manifest publishes for lowering the input budget | WHEN a caller sets it to 50 and sends a source of 300 bytes | THEN the run is refused for "input_size" with 50 allowed, so the published name is the name the tool reads
  - SC12 | P6 | GIVEN a caller that wrote the time budget as "ten" | WHEN it sends any request | THEN status "invalid_input" with one "malformed_request" refusal naming that variable and quoting "ten" back, and no result
- **conflicts**:
  - S1 | NONE | ran the suite on this worktree: 1153 tests collected and green, so the baseline the sentence states is the one I start from
  - S2 | NONE | read SPEC.md lines 280-284 and 503-508; they require declared budgets with controlled failure and forbid a limit becoming a semantic rule, which is what the criteria ask for
  - S3 | NONE | SPEC.md and every existing test stay as they are; the new behaviour is published beside the two limits R1 added, changing no expected result
  - S4 | NONE | no existing test expects an operation to run without a budget; this table is the result of looking for one
  - S5 | NONE | nothing under .relay/ is read by the tool or by any test in tests/, checked by grep over tests/ and src/
  - S6 | NONE | the work happens in the worktree named by the task and nothing outside it is written
  - S7 | NONE | the commit message is mine to write and no test reads it
  - S8 | NONE | the co-author line is mine to write and no test reads it
  - S9 | NONE | nothing in this delivery pushes or merges
  - S10 | NONE | the full suite is run before and after; every existing expectation is left as it is
  - S11 | NONE | the budget work lives in a new module; service.py gains a parameter and five calls, __main__.py four lines, so the parallel delivery meets small additive edits
  - S12 | NONE | the published block is built in service._run_discover and the two limit objects live in reader.py and evaluator.py; the budgets join that same block rather than opening a second one, and neither existing limit changes
  - S13 | NONE | docs/ROADMAP.md section 5 D5 and section 8 state exactly these four numbers and that they are to be measured on CI first; nothing in the code states a different number
  - S14 | NONE | tests/properties/test_s1_b2_no_forbidden_claim_property.py already forbids claim wording in an answer; the budget refusals carry no claim at all, so the two agree
  - S15 | NONE | a rule for how I drive the recording tool; nothing in the repository contradicts it
  - S16 | NONE | no operation declares a budget today, so the criterion adds a statement where there is none and contradicts no existing answer
  - S17 | NONE | checked tests/properties/test_i1_s1_p4_p5.py, which forbids entering the checker or the evaluator for an unavailable operation: the budget check for such a request enters neither
  - S18 | NONE | a heading; nothing in the repository contradicts it
  - S19 | NONE | a criterion number; nothing in the repository contradicts it
  - S20 | NONE | tests/unit/test_service_discover.py and the F11 acceptance tests read named parts of the manifest, never a closed set of keys, so a new budgets entry breaks none of them
  - S21 | NONE | the resource limits block already says enforced true for the two limits R1 added, so marking each budget enforced agrees with what is published
  - S22 | NONE | a criterion number; nothing in the repository contradicts it
  - S23 | NONE | no test sends a source near 1 MiB: the largest generated source is a program nested about 520 forms deep, a few kilobytes
  - S24 | NONE | the nesting refusal already names its limit in a symbol field, so naming the budget the same way follows the shape callers already read
  - S25 | NONE | a criterion number; nothing in the repository contradicts it
  - S26 | NONE | no existing test waits on this tool: every run in the suite answers in milliseconds, far inside a 10 s budget
  - S27 | NONE | no operation returns a partial answer today; every refusal replaces the whole answer, which is what the criterion asks for
  - S28 | NONE | a criterion number; nothing in the repository contradicts it
  - S29 | NONE | the Refusal type in service.py already carries status and diagnostics only, with no field for a claim or a result
  - S30 | NONE | SPEC.md line 505 forbids a limit becoming a semantic bound and no existing message does so; the new messages are checked against a list of forbidden words
  - S31 | NONE | a criterion number; nothing in the repository contradicts it
  - S32 | NONE | ran the suite: every existing expectation is answered well inside all four declared numbers, so none of them changes an answer
  - S33 | NONE | read both ranges of SPEC.md; they state the requirement the criteria repeat
  - S34 | NONE | D5 is recorded as approved in docs/ROADMAP.md section 8, so the dependency is met
  - S35 | NONE | a planning fact; nothing in the repository contradicts it
  - S36 | NONE | service.py and __main__.py are the two files the dispatch and the command live in, and the budget work touches both
  - S37 | NONE | the manifest does not state any input, time, memory or answer budget today, so the expectation is real and nothing contradicts it
- **decisions**:
  - DEC1: each budget gets its own refusal category (input_budget_exceeded, time_budget_exceeded, memory_budget_exceeded, output_budget_exceeded), the way every other distinct refusal of this tool has one, so a caller can handle one budget differently from another without reading prose.
  - DEC2: a caller lowers a budget for one run through an environment variable named in the manifest (PROVA_BUDGET_INPUT_SIZE and its three siblings). A request field would let any caller change the budgets of the published protocol, and an in-process argument alone could not be reached from a test that drives the real command. Owner absent: recorded as my decision.
  - DEC3: the answer budget is enforced where the answer is rendered and printed, so one renderer owns the bytes a caller reads. A refusal is always delivered even when it is itself larger than the budget: the budget sizes the answer an operation produced, and the refusal that replaces it is this tool's smallest answer.
  - DEC4: the time and memory budgets are observed at the boundaries between the stages of an operation and before each declared example is run. A stage already running is not interrupted part way; the input budget is what keeps a stage short. Published as enforced with that granularity stated, rather than as not enforced.
  - DEC5: the four numbers are published as declared, not measured: each entry carries basis declared and the reason says so. Measured on this delivery: the sizes (input and answer, counted in bytes) and that every shipped program and every test in the suite completes inside all four. Only declared: that 10 s and 512 MiB are the right numbers for a machine other than mine; no CI measurement of time or memory was taken.
  - DEC6: the budgets live in one new module, src/prova/budgets.py, which owns the numbers, their published shape and the refusals. service.py gains one parameter and the calls that check at a stage boundary; __main__.py reads the environment and prints through the renderer. This keeps both contended files lightly edited while F12 runs in parallel.
  - DEC7: the time budget is published in milliseconds so that every budget states a whole number in a published unit, and every refusal reports expected and actual as whole numbers, the way the two limits published before already do.
  - DEC8: no formal model (Quint) for this work: there is no protocol, no concurrency and no stored state here; a budget is a comparison of one number with another inside one process, and the properties cover it.
  - DEC9: the budget refusals carry no source revision. Three of the four are not about a submitted text at all, and the input budget refusal is answered before the text is read, so hashing it would be work the budget exists to refuse.
- **mapping**:
  - P1 => test_every_operation_this_tool_offers_states_four_budgets
  - P2 => test_a_source_past_the_budget_a_caller_set_is_refused_by_name
  - P3 => test_a_run_with_no_time_left_is_answered_with_the_time_budget
  - P4 => test_a_run_stopped_by_a_budget_reports_only_that_budget
  - P5 => test_a_program_inside_every_budget_is_evaluated_and_answered
  - P6 => test_a_budget_a_caller_cannot_set_is_refused_by_name
  - P7 => test_the_budgets_stand_in_the_same_block_as_the_limits
  - P8 => test_an_answer_one_byte_too_large_is_replaced_by_the_budget_refusal
  - P9 => test_a_run_whose_memory_is_already_past_the_budget_is_refused
- **covers_scenarios**:
  - SC1 => test_every_operation_this_tool_offers_states_four_budgets
  - SC2 => test_the_stated_numbers_are_the_ones_the_owner_decided_and_say_so
  - SC3 => test_a_source_past_the_budget_a_caller_set_is_refused_by_name
  - SC4 => test_a_source_past_the_declared_budget_is_refused_with_no_budget_lowered
  - SC5 => test_a_run_with_no_time_left_is_answered_with_the_time_budget
  - SC6 => test_a_run_whose_memory_is_already_past_the_budget_is_refused
  - SC7 => test_an_answer_one_byte_too_large_is_replaced_by_the_budget_refusal
  - SC8 => test_a_run_stopped_by_a_budget_reports_only_that_budget
  - SC9 => test_a_program_inside_every_budget_is_evaluated_and_answered
  - SC10 => test_the_budgets_stand_in_the_same_block_as_the_limits
  - SC11 => test_the_published_way_to_lower_a_budget_is_the_way_that_works
  - SC12 => test_a_budget_a_caller_cannot_set_is_refused_by_name
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC6 => base differs
  - SC7 => base differs
  - SC8 => base differs
  - SC9 => base held
  - SC10 => base differs
  - SC11 => base differs
  - SC12 => base differs
- **interfaces**:
  - I1: the prova command: one JSON request on standard input, one complete JSON answer on standard output, exit 0.
  - I2: the manifest the discover operation answers with, where a caller reads the budgets before it sends work.
  - I3: the four environment variables a caller sets to lower one budget for one run.
- **matrix**:
  - I1.empty => a request whose source is the empty text, nothing lowered => answered as before: the text declares nothing and is refused by that rule of the language, not by a budget
  - I1.unknown => a request naming an operation this tool does not have, carrying a source of 2 MiB => answered unavailable as before: no source is read, so no input budget is counted over it
  - I1.malformed => text that is not JSON at all => answered invalid_input as before: the input budget sizes the program a request carries, not the text of the request
  - I1.dependency-gone => the platform offers no reading of this process's peak memory => the memory budget states enforced false with the reason, the other three are unchanged, and no run is refused for memory
  - I1.repeated => the same request sent twice under the same lowered budget => the same refusal both times: the command keeps nothing between runs
  - I1.concurrent => n/a: each run is its own process, writing no file and sharing no state, so no overlap between two runs is observable from outside
  - I1.crash => n/a: the command writes no file and keeps nothing, so a kill leaves nothing half written for a later run to find
  - I2.empty => a discover request carrying no other field => the budgets of every offered operation are stated, as the operation takes nothing else
  - I2.unknown => a caller looks for a budget name the manifest does not state => it finds the 4 published names and nothing else; an unknown name is simply absent
  - I2.malformed => n/a: the manifest is written by the tool from one budgets object, and a caller sends no manifest of its own
  - I2.dependency-gone => the platform offers no reading of peak memory => the memory entry itself says enforced false and why, so a caller reads the gap instead of trusting a budget
  - I2.repeated => the discover operation run twice => the same block both times, number for number: it is built from one object and reads nothing else
  - I2.concurrent => n/a: reading the manifest changes nothing, and two readers share nothing to race over
  - I2.crash => n/a: the manifest is built fresh in each run, so a kill leaves nothing behind to repair
  - I3.empty => a variable set to the empty text => refused by name: a caller that believes it lowered a budget and did not would read the run that follows as proof that its work fits
  - I3.unknown => PROVA_BUDGET_DISK_SIZE=5, a budget name this tool does not publish => refused by name, so a mistyped budget never quietly does nothing
  - I3.malformed => ten, -1, 1.5, or 10001 against a stated maximum of 10000 => refused by name, saying a whole number no larger than the stated maximum is read
  - I3.dependency-gone => n/a: the variables are read from this process's own environment, and there is nothing else for them to depend on
  - I3.repeated => the same variable written twice in one environment => the environment keeps one value per name, so the tool reads one value and answers once
  - I3.concurrent => two runs at once, each lowering a different budget => each reads its own environment and answers its own budget; nothing is shared between them
  - I3.crash => n/a: setting a variable changes nothing the tool keeps, so a kill leaves nothing to repair
- **laws**:
  - LAW1 | the input budget a caller sets is the size that refuses: a source of exactly that many bytes is read, and any source past it is refused with that number beside the size sent | generator=test_the_input_budget_a_caller_sets_is_the_size_that_refuses | observation=the refusal reports expected equal to the budget the run was given and actual equal to the bytes sent, and a source of exactly the budget carries no input budget refusal | mutant=publishing one number and enforcing another, or refusing at the number instead of past it
  - LAW2 | whichever budget stops whichever operation, the answer reports the budget and nothing about the program | generator=test_a_run_stopped_by_any_budget_reports_no_result | observation=the answer carries one refusal of that budget's category and none of claim, result, source_digest or contract_report, and no forbidden word | mutant=a refusal that keeps the claim of the operation it interrupted
  - LAW3 | stating the declared budgets changes no answer: a run inside them answers exactly as a run with nothing stated | generator=test_a_run_inside_the_declared_budgets_answers_as_if_none_were_set | observation=the two answers are equal, field for field, and both are completed | mutant=a budget check that refuses a run it should admit, or that changes what a completed answer carries
  - LAW4 | an answer past the answer budget is replaced whole, never cut short | generator=test_an_answer_past_the_output_budget_is_replaced_whole | observation=the printed text parses as one JSON answer carrying the answer budget refusal, and no part of the withheld manifest appears in it | mutant=printing the first bytes of the oversized answer
- **messages**:
  - MSG1 | a source of 200 bytes with the input budget lowered to 64 | the source is larger than the input budget this run allows | the tool stopped before reading it, so no rule of the language was read over it | send a smaller source, or raise the input budget to the maximum the manifest states for this operation | test=test_a_source_past_the_budget_a_caller_set_is_refused_by_name
  - MSG2 | a run with the time budget lowered to 0 milliseconds | the run has no time left of the time budget it was given | this tool stops where it stands rather than leaving a caller waiting | give the run more time, up to the maximum the manifest states, or send less work | test=test_a_run_with_no_time_left_is_answered_with_the_time_budget
  - MSG3 | a run with the memory budget lowered to 1 byte | the run has already taken more memory than its budget allows | this tool stops first rather than being killed by the machine with nothing to say | raise the memory budget to the maximum the manifest states, or send a smaller program | test=test_a_run_whose_memory_is_already_past_the_budget_is_refused
  - MSG4 | a manifest request with the answer budget one byte under the size of the answer | the answer this operation produced is larger than the answer budget allows | an answer a caller cannot read whole is withheld whole, because half of one carries no outcome | raise the answer budget to the maximum the manifest states, or ask for less in one request | test=test_an_answer_one_byte_too_large_is_replaced_by_the_budget_refusal
  - MSG5 | PROVA_BUDGET_OPERATION_TIME=ten | the value written for this budget is not a whole number | a budget that cannot be read would leave the run under a budget the caller did not choose | write the budget as a whole number of the unit the manifest states for it, as 2000 | test=test_a_budget_a_caller_cannot_set_is_refused_by_name
  - MSG6 | PROVA_BUDGET_OPERATION_TIME=10001 against a stated maximum of 10000 | the value written is above the maximum this tool declares for that budget | a caller may lower a budget for its own run and may not raise the one this tool answers for | write a value no larger than the maximum the manifest states for that budget | test=test_a_budget_a_caller_cannot_set_is_refused_by_name
  - MSG7 | PROVA_BUDGET_DISK_SIZE=5 | this tool publishes no budget of that name | a name it does not read would leave the caller believing it had set a budget | set one of the four names the manifest publishes under lower_with, or unset this one | test=test_a_budget_a_caller_cannot_set_is_refused_by_name
- **red**: `uv run pytest -q tests/acceptance/test_f14_b1_every_operation_states_its_four_budgets.py tests/acceptance/test_f14_b2_a_source_past_the_input_budget_is_refused.py tests/acceptance/test_f14_b3_work_past_the_time_budget_is_answered_not_left_running.py tests/acceptance/test_f14_b4_a_run_past_the_memory_budget_is_refused.py tests/acceptance/test_f14_b5_an_answer_past_the_output_budget_is_refused.py tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py tests/acceptance/test_f14_b7_a_program_inside_every_budget_is_answered_as_before.py tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py tests/acceptance/test_f14_b9_the_limits_published_before_still_stand.py tests/properties/test_f14_budget_laws.py` exited 1 in 40.666s
  - failing on the pre-feature tree (21): tests/acceptance/test_f14_b1_every_operation_states_its_four_budgets.py::test_every_operation_this_tool_offers_states_four_budgets, tests/acceptance/test_f14_b1_every_operation_states_its_four_budgets.py::test_each_budget_is_marked_enforced_with_the_refusal_it_answers_with, tests/acceptance/test_f14_b1_every_operation_states_its_four_budgets.py::test_the_stated_numbers_are_the_ones_the_owner_decided_and_say_so, tests/acceptance/test_f14_b2_a_source_past_the_input_budget_is_refused.py::test_a_source_past_the_budget_a_caller_set_is_refused_by_name, tests/acceptance/test_f14_b2_a_source_past_the_input_budget_is_refused.py::test_a_source_past_the_declared_budget_is_refused_with_no_budget_lowered, tests/acceptance/test_f14_b3_work_past_the_time_budget_is_answered_not_left_running.py::test_a_run_with_no_time_left_is_answered_with_the_time_budget, tests/acceptance/test_f14_b4_a_run_past_the_memory_budget_is_refused.py::test_a_run_whose_memory_is_already_past_the_budget_is_refused, tests/acceptance/test_f14_b5_an_answer_past_the_output_budget_is_refused.py::test_an_answer_one_byte_too_large_is_replaced_by_the_budget_refusal, tests/acceptance/test_f14_b5_an_answer_past_the_output_budget_is_refused.py::test_a_refusal_is_delivered_even_when_it_is_larger_than_the_budget, tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py::test_a_run_stopped_by_a_budget_reports_only_that_budget[input_size], tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py::test_a_run_stopped_by_a_budget_reports_only_that_budget[operation_time], tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py::test_a_run_stopped_by_a_budget_reports_only_that_budget[peak_memory], tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py::test_a_run_stopped_by_a_budget_reports_only_that_budget[answer_size], tests/acceptance/test_f14_b7_a_program_inside_every_budget_is_answered_as_before.py::test_a_program_inside_every_budget_is_evaluated_and_answered, tests/acceptance/test_f14_b7_a_program_inside_every_budget_is_answered_as_before.py::test_the_same_step_with_every_budget_lowered_is_refused, tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py::test_the_published_way_to_lower_a_budget_is_the_way_that_works, tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py::test_a_budget_a_caller_cannot_set_is_refused_by_name[a, tests/acceptance/test_f14_b9_the_limits_published_before_still_stand.py::test_the_budgets_stand_in_the_same_block_as_the_limits, tests/properties/test_f14_budget_laws.py::test_the_input_budget_a_caller_sets_is_the_size_that_refuses, tests/properties/test_f14_budget_laws.py::test_a_run_stopped_by_any_budget_reports_no_result, tests/properties/test_f14_budget_laws.py::test_an_answer_past_the_output_budget_is_replaced_whole
  - tests (read from the run): 25 failed, 7 passed in 40.07s
  ```text
              f"{response.get('status')!r}: {str(response)[:300]}. The manifest is "
              "thousands of bytes, so no answer budget this small can hold it."
          )
  E       AssertionError: the manifest under an answer budget of 1 bytes was answered 'completed': {'operation': 'discover', 'status': 'completed', 'claim': {'kind': 'manifest', 'scope': 'this tool'}, 'diagnostics': [], 'result': {'profile': {'name': 'core-0', 'coverage': 'partial'}, 'operations': {'check': 'available', 'examples': 'available', 'evaluate': 'available', 'discover': 'available', 'v. The manifest is thousands of bytes, so no answer budget this small can hold it.
  E       assert 'completed' == 'resource_exhausted'
  E
  E         - resource_exhausted
  E         + completed
  E       Failing test case: test_an_answer_past_the_output_budget_is_replaced_whole(
  E           allowed=1,  # or any other generated value
  E       )

  tests/properties/test_f14_budget_laws.py:169: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f14_b1_every_operation_states_its_four_budgets.py::test_every_operation_this_tool_offers_states_four_budgets
  FAILED tests/acceptance/test_f14_b1_every_operation_states_its_four_budgets.py::test_each_budget_is_marked_enforced_with_the_refusal_it_answers_with
  FAILED tests/acceptance/test_f14_b1_every_operation_states_its_four_budgets.py::test_the_stated_numbers_are_the_ones_the_owner_decided_and_say_so
  FAILED tests/acceptance/test_f14_b2_a_source_past_the_input_budget_is_refused.py::test_a_source_past_the_budget_a_caller_set_is_refused_by_name
  FAILED tests/acceptance/test_f14_b2_a_source_past_the_input_budget_is_refused.py::test_a_source_past_the_declared_budget_is_refused_with_no_budget_lowered
  FAILED tests/acceptance/test_f14_b3_work_past_the_time_budget_is_answered_not_left_running.py::test_a_run_with_no_time_left_is_answered_with_the_time_budget
  FAILED tests/acceptance/test_f14_b4_a_run_past_the_memory_budget_is_refused.py::test_a_run_whose_memory_is_already_past_the_budget_is_refused
  FAILED tests/acceptance/test_f14_b5_an_answer_past_the_output_budget_is_refused.py::test_an_answer_one_byte_too_large_is_replaced_by_the_budget_refusal
  FAILED tests/acceptance/test_f14_b5_an_answer_past_the_output_budget_is_refused.py::test_a_refusal_is_delivered_even_when_it_is_larger_than_the_budget
  FAILED tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py::test_a_run_stopped_by_a_budget_reports_only_that_budget[input_size]
  FAILED tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py::test_a_run_stopped_by_a_budget_reports_only_that_budget[operation_time]
  FAILED tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py::test_a_run_stopped_by_a_budget_reports_only_that_budget[peak_memory]
  FAILED tests/acceptance/test_f14_b6_a_budget_refusal_claims_nothing_about_the_program.py::test_a_run_stopped_by_a_budget_reports_only_that_budget[answer_size]
  FAILED tests/acceptance/test_f14_b7_a_program_inside_every_budget_is_answered_as_before.py::test_a_program_inside_every_budget_is_evaluated_and_answered
  FAILED tests/acceptance/test_f14_b7_a_program_inside_every_budget_is_answered_as_before.py::test_the_same_step_with_every_budget_lowered_is_refused
  FAILED tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py::test_the_published_way_to_lower_a_budget_is_the_way_that_works
  FAILED tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py::test_a_budget_a_caller_cannot_set_is_refused_by_name[a budget name this tool does not publish]
  FAILED tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py::test_a_budget_a_caller_cannot_set_is_refused_by_name[a negative value]
  FAILED tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py::test_a_budget_a_caller_cannot_set_is_refused_by_name[a value above the number this tool declares]
  FAILED tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py::test_a_budget_a_caller_cannot_set_is_refused_by_name[a value that is not a whole number]
  FAILED tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py::test_a_budget_a_caller_cannot_set_is_refused_by_name[a value with nothing in it]
  FAILED tests/acceptance/test_f14_b9_the_limits_published_before_still_stand.py::test_the_budgets_stand_in_the_same_block_as_the_limits
  FAILED tests/properties/test_f14_budget_laws.py::test_the_input_budget_a_caller_sets_is_the_size_that_refuses
  FAILED tests/properties/test_f14_budget_laws.py::test_a_run_stopped_by_any_budget_reports_no_result
  FAILED tests/properties/test_f14_budget_laws.py::test_an_answer_past_the_output_budget_is_replaced_whole
  25 failed, 7 passed in 40.07s
  ```

## 4. design: Find the owners and design the change (revision 2)

- **owners**:
  - how large a source this tool reads => new: src/prova/budgets.py; reader.py owns how deeply a text nests and evaluator.py owns how far a run stands inside itself, and neither is a size in bytes
  - how much of a request this tool reads at all => new: src/prova/budgets.py states the ceiling, src/prova/__main__.py reads no more than it
  - how long one run may take => new: src/prova/budgets.py; nothing in this tool reads a clock today
  - how much memory one run may take => new: src/prova/budgets.py; nothing in this tool reads its own memory today
  - how large an answer may be => new: src/prova/budgets.py; nothing measures what the command prints today
  - whether a budget a caller lowered can be read => new: src/prova/budgets.py, from the environment the command hands it
  - the status a passed budget is answered with => src/prova/service.py: RESOURCE_EXHAUSTED, the status the two limits already use
  - what a refusal of each new category carries => src/prova/checker.py: DIAGNOSTIC_KINDS, the one table of published shapes
  - turning one refusal into the dictionary a caller reads => src/prova/service.py: _diagnostic_dict, unchanged
  - the block the manifest states the limits in => src/prova/service.py: _run_discover; the budgets join that block rather than opening a second one
  - the text of the one answer the command prints => src/prova/service.py: a new answer_text, which __main__.py calls instead of rendering its own
  - naming a field of a request that cannot be read => src/prova/service.py: MalformedRequest, reused for a budget variable that cannot be read
  - how deeply a text may nest and how far a run may stand inside itself => src/prova/reader.py and src/prova/evaluator.py, untouched
- **reuse_decision**: Reused: the resource_exhausted status, the Diagnostic and its published-shape table, _diagnostic_dict as the one builder of a refusal, MalformedRequest for a value this tool cannot read, and the resource_limits block the manifest already answers with. Created new: one module, src/prova/budgets.py, because no existing owner holds a size in bytes, a span of time or an amount of memory: the nesting limit lives in the reader because the reader is what nests, and the evaluation depth lives in the evaluator for the same reason, while a budget on the whole run belongs to none of them. Putting the four numbers in service.py would make the dispatcher the owner of four rules it does not apply, and would grow the one file another delivery is editing. The four budgets share one shape, so they are four small classes over one base rather than four copies of the same arithmetic.
- **paradigm**: oo
- **boundaries**:
  - the command (src/prova/__main__.py) is the only place that reads the environment and writes to standard output; it resolves the budgets once and hands them in, so nothing below reads a global
  - service.handle takes the budgets as a parameter whose default is the declared ones, so a caller inside this process is never surprised and no module-level state is kept
  - budgets.py knows no operation name, builds no answer and reads no request; service.py holds no budget number
  - checker.py keeps the published shape of every refusal, including the four new categories, so the manifest and the refusals cannot drift apart
  - the answer budget is applied where the answer is written, in service.answer_text, the one path the command prints through; service.handle still answers a dictionary for a caller inside this process
  - reader.py and evaluator.py are not touched: their two limits stay where they are and keep their numbers
- **domain_types**:
  - Budget: one number this tool declares, with the name a caller reads it under, the unit it is counted in, the category of the refusal it answers with and the reason for its value; it answers whether an amount has passed it. Four of them: InputBudget, TimeBudget, MemoryBudget, AnswerBudget
  - Budgets: the four budgets of one run held together, built from the Owner's numbers and lowered only from the environment; it states them per operation for the manifest and starts a run
  - Run: one run under those budgets -- when it started and how much memory this process has taken -- answering at each checkpoint which budget, if any, has been passed
  - Exhaustion: which budget was passed, its maximum, the amount reached and the sentence that says so; it carries nothing about the program
  - UnreadableBudget: a budget variable this tool cannot read, with the name a caller must repair and why
  - PeakMemory: the greatest memory this process has taken, in bytes, and whether this platform can say at all
- **invariants**:
  - INV1 | A budget refusal reports the budget, its maximum and the amount reached, and nothing about the program: it has no field for a claim, a result or a digest of a source | witness=src/prova/budgets.py:Exhaustion | bypass=none
  - INV2 | The number the manifest states for a budget is the number the run enforces, because the entry and the check read the same object | witness=src/prova/budgets.py:Budget | bypass=none
  - INV3 | The environment may only lower a budget: a value above the declared maximum, a value that is not a whole number and a name this tool does not publish are each refused by name, never ignored | witness=src/prova/budgets.py:Budgets | bypass=a caller inside this process may hand service.handle any Budgets it builds; the command builds them only from the declared numbers and the environment
  - INV4 | Every answer the command prints is one complete JSON answer inside the answer budget, or one refusal naming that budget; no answer is ever cut short | witness=src/prova/service.py:answer_text | bypass=the refusal itself is delivered even when it is larger than the budget the caller set, which the manifest states
  - INV5 | The memory budget claims only what it read: where this platform cannot report peak memory the entry says it is not enforced and why, and no answer says the budget was met | witness=src/prova/budgets.py:PeakMemory | bypass=none
  - INV6 | The nesting limit and the evaluation depth keep their numbers and their place; the budgets join the same block | witness=src/prova/service.py:_run_discover | bypass=none
  - INV7 | This tool reads at most the input budget plus a stated allowance of 65536 bytes of any request before it answers, so a request too large to answer is never held in memory whole to be refused afterwards; such a request is answered against the input budget and names no operation, because none was read | witness=src/prova/__main__.py:_read_at_most | bypass=a caller inside this process that hands service.handle a text it already holds has already paid for it; the command, which is the public port, reads no more than the ceiling
- **prefactoring**: no
- **prefactoring_reason**: No refactor is owed first. The change adds one parameter to the dispatcher and its five handlers and calls the new module at the boundaries between stages; every line it touches keeps its behaviour, and no existing code must be prepared to receive it. The one refactor this file has recorded as owed -- extracting the parse-and-check preamble the four handlers repeat -- is owed for a time when no other delivery is editing service.py, and another delivery is editing it now.

## 6. craft: Craft the change (revision 2)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 165.887s
  - tests (read from the run): 1241 passed in 165.74s
  - slowest: 8.17s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 5.30s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 4.72s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.97s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 3.69s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 3.24s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 2.36s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.96s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.85s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.75s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  5%]
  ........................................................................ [ 11%]
  ........................................................................ [ 17%]
  ........................................................................ [ 23%]
  ........................................................................ [ 29%]
  ........................................................................ [ 34%]
  ........................................................................ [ 40%]
  ........................................................................ [ 46%]
  ........................................................................ [ 52%]
  ........................................................................ [ 58%]
  ........................................................................ [ 63%]
  ........................................................................ [ 69%]
  ........................................................................ [ 75%]
  ........................................................................ [ 81%]
  ........................................................................ [ 87%]
  ........................................................................ [ 92%]
  ........................................................................ [ 98%]
  .................                                                        [100%]
  ============================= slowest 10 durations =============================
  8.17s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  5.30s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  4.72s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.97s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  3.69s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  3.24s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  2.36s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.96s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.85s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.75s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1241 passed in 165.74s (0:02:45)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.063s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this environment; the client exited 3 when the four design questions were put to it, and every choice was settled locally and recorded as a decision

## 7. selfreview: Self-review (revision 2)

- **answers**:
  - D1: pass - the change is the design record at revision 2: one new module owning the four numbers, the command resolving them, the dispatcher measuring the run, and INV7 for the bounded read added when that rule appeared (docs/feature/budgets/design.md)
  - D2: pass - the four numbers exist once, in Budgets.declared(); the manifest entry and every check read the same objects, and one sizer (budgets._size_of) measures a source, a request and an answer alike
  - D3: pass - budgets.py names no operation, reads no request and writes no answer; service.py holds no number; __main__.py is the only reader of the environment and the only writer of the answer
  - D4: fixed: a decision carries its evidence rather than a flag: Budget.lowered_to returns the lowered budget or an UnreadableBudget naming the variable and why, so no caller can mistake a refusal for a number (src/prova/budgets.py:153). The first version guarded with isdigit() and then called int(), which a superscript digit broke; it now admits only the ten ASCII digits
  - D5: pass - Run holds two things, the budgets and when it began, and answers questions rather than exposing them (src/prova/budgets.py:579); each budget holds one number and its own words; no class here has a getter or a setter
  - D6: n/a: no pattern was introduced. Four budgets share one small base because they answer the same question about different quantities; anything more would be a framework for one caller
  - D7: pass - the words are the domain's: budget, maximum, reached, exhaustion, run, peak memory. No type here is named for a mechanism, and the one rule each budget owns lives on the budget
  - D8: pass - the two platform readings are the one adapter in the module: PeakMemory asks the operating system and Run asks the clock, both behind methods, while every number and every comparison is pure and testable without either
  - D9: fixed: every case drives the real command as a child process over its own stdin and stdout and imports nothing from src/prova (tests/acceptance/_f14_budget_fixtures.py:121). The one case that measures memory reads what the operating system reports about those children, not about the tool's internals
  - D10: pass - each test is named for what a caller gets: a source past the input budget is refused, a run with no time left is answered, a request too long to read is refused unread. The only production words in a name are the published budget names, which are the protocol
  - D11: pass - one fixtures module per test directory, reusing the shipped-program helpers R1 already had rather than copying them; every assertion message is built by the same two helpers, so a refusal reads the same way in every case
  - D12: pass - four laws over generated input: every input budget a caller sets against every size of source, every budget against every operation, every program inside the declared numbers, every answer budget under the manifest (tests/properties/test_f14_budget_laws.py:48)
  - D13: pass - 43 cases in a median of 4.94 s over nine runs, slowest 4.98 s, none flaky; no case sleeps or reads the clock to decide, and the one 20 MiB case costs about a third of a second
  - D14: pass - each case observes something no other does; the twins beside the refusals pin today's answers rather than repeating them, and the one table of caller mistakes is parametrised instead of copied six times
  - D15: fixed: every refusal says what failed, why it matters and what to do, with the numbers in the sentence a person reads (src/prova/budgets.py:261). The memory remedy used to say send a smaller program, which is false for a high-water mark, and now says start again in a new process
  - D16: n/a: no formal model pays here. There is no shared state, no protocol of more than one step, no concurrency and no crash window: a budget is one number compared with another inside one process, and the four laws cover the comparison
  - D17: pass - the three documents were brought back in step as the code changed: the counts, the operations, the allowance and its reason, what is measured against what is only declared, and the four delete-checks that showed each repair is load-bearing
- **independent_review**:
  - REV1 | reviewer=rev-f14 | findings=7 (verdict REJECT at 6d72ada) | resolution=D1 and D2 fixed in 6c44a68 and 553ad68, N1 N2 N3 N5 fixed, the revised oracle case judged not a weakening
  - REV2 | reviewer=rev-f14 | findings=3 (verdict APPROVE at 5c2a473, notes only) | resolution=N8 corrected, N6 and N7 recorded as stated limits in the handoff

## 8. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
- **not_verified**:
  - The paging in the sizer that measures a text a page at a time has no case through the command: the command reads at most the ceiling, so no request can reach a text long enough to page. Only a caller inside this process that hands service.handle a text it already holds reaches it, and that path is kept for exactly that caller.
  - The refusal for a request longer than this tool reads reports the input budget as what was allowed, not the larger ceiling it was actually measured against. That is deliberate -- the budget is the thing a caller sizes against and can lower -- and the oracle pins it; a reader comparing the two numbers in that one refusal is reading a budget and a ceiling, which the manifest states separately.
  - No run was observed passing a budget in the middle of a single stage. Nothing can be built from outside that does: the checker refuses a cyclic call graph, so a program of this profile has neither loop nor recursion, and the input budget holds a stage short.
  - The memory figure is the greatest memory the whole process has taken, not the memory one operation added, and it never falls. The command answers one request per process, so a run of the command is measured against its own work; a caller using this as a library inside a longer process is measured against everything that process has done.
  - That 10 s and 512 MiB are the right numbers was not measured anywhere: no timing and no memory figure was taken on CI, which is what the Owner's decision asks for before the numbers are fixed. The two sizes were measured, in bytes, by the cases themselves.
  - A platform that cannot report the memory a process has taken was not run. The code answers such a platform by stating the memory budget as not enforced and saying why, and no answer there claims the budget was met; macOS and Linux both report it, so neither path was exercised.
  - The memory measurements of a very large request were taken on this machine only, with the operating system's own figures; nothing was measured on CI.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit ea3a64caee79d543711aa1f3938f64101aaac798
  - no checks declared

## Not backed by the diff

- Every operation this tool offers now states, before it is asked for anything, the input, time, memory and answer budget it runs under, and a run that passes one is stopped where it stands and told which budget stopped it, what that budget allowed and how much was reached -- and nothing else, because a tool that stopped inside its own budget read no rule of the language over anything.: a guarantee names no test function of the change
- The four numbers are the Owner's (1 MiB of source, 10 s, 512 MiB of memory, 1 MiB of answer); they are published as declared, not measured, and each entry says so.: a guarantee names no test function of the change
- A caller lowers any of them for one run through the environment variable the manifest names beside it; it may only lower, and a name this tool does not publish, a value that is not written in the digits 0 to 9, or a value above the declared maximum is refused by name rather than quietly ignored.: a guarantee names no test function of the change
- A request longer than the input budget plus a stated allowance for what a request carries around its source is answered against the input budget without being read at all, and says that it never learned which operation was asked for.: a guarantee names no test function of the change
- The nesting limit and the evaluation depth published before keep their numbers and their place beside the new budgets.: a guarantee names no test function of the change
- Checked by cases that drive the real command over its own standard input and output, by four generated laws, by measuring with the operating system what refusing a very large request costs, and by removing each repair again to watch its case fail.: a guarantee names no test function of the change
