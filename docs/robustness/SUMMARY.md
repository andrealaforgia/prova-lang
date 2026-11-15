# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1042 tests, all green on main).
  - not-testable (challenge this): states the project, its test command and its green baseline
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority this work answers to
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a process promise about what this delivery may edit
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): a process promise to stop and report a conflict with an existing test
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): a process promise to ignore one directory of the repository
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a process promise about which worktree and branch the work happens in
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a process promise about how a commit message ends
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line a commit message must end with
- S9: Do not push and do not merge.
  - not-testable (challenge this): a process promise not to push and not to merge
- S10: Keep the full suite green.
  - promises: P8
  - tests P8: test_the_limit_leaves_room_for_the_programs_this_repository_ships
- S11: Another small delivery (F2fix, tests and docs only) runs in parallel; no conflict expected.
  - not-testable (challenge this): states that another small delivery runs in parallel
- S12: F1 to F10 are on main.
  - not-testable (challenge this): states which earlier features are already on main
- S13: Read how F6 and F10 turned malformed input into located refusals (syntax.py boundary, service.py request validation and the table of diagnostic kinds in checker.py) and follow that structure.
  - not-testable (challenge this): tells the author which existing code to read before designing
- S14: If an existing test conflicts, stop and report.
  - not-testable (challenge this): repeats the process promise to stop and report a conflict
- S15: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): a process promise about where the author keeps its scripts
- S16: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): a process promise about shell quoting and leaving the tree clean
- S17: **Outcome.** Every request the tool can receive is answered with one JSON response.
  - promises: P1
  - tests P1: test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
- S18: Input that breaks a rule is answered with a located refusal in a published category, never a Python traceback and never exit code 1 with an empty stdout.
  - promises: P2
  - tests P2: test_an_argument_nested_past_the_limit_is_refused_the_same_way
- S19: Found by the F6, F9, F10 and F2/F3 independent reviews; each crash exists on main today.
  - not-testable (challenge this): says who found the defects and that each exists on main today
- S20: **Acceptance criteria**
  - not-testable (challenge this): the heading standing over the acceptance criteria
- S21: 1.
  - not-testable (challenge this): the number of the first acceptance criterion
- S22: Given `examples` on `examples/hour-clock.prova` with character 550 deleted, and again with character 1191 deleted, then the answer is JSON (a refusal or a result), not an `IndexError` from `src/prova/evaluator.py`.
  - promises: P1, P3
  - tests P1: test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - tests P3: test_a_record_written_with_the_wrong_number_of_values_is_refused
- S23: Find the cause (a malformed program the checker accepted that the evaluator cannot run, or an evaluator assumption): fix it where it lives.
  - promises: P3
  - tests P3: test_a_record_written_with_the_wrong_number_of_values_is_refused
- S24: If the program is invalid, the checker must refuse it with a located diagnostic; if it is valid, the evaluator must run it.
  - promises: P3
  - tests P3: test_a_record_written_with_the_wrong_number_of_values_is_refused
- S25: 2.
  - not-testable (challenge this): the number of the second acceptance criterion
- S26: Given `evaluate` with `"function": ["f"]` (or any non-string), then the answer is `invalid_input` with the `malformed_request` category (added by F10) naming the field.
  - promises: P4
  - tests P4: test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field
- S27: Likewise `"arguments": 7` and any non-list `arguments`, and non-string elements of `arguments`.
  - promises: P4
  - tests P4: test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field
- S28: 3.
  - not-testable (challenge this): the number of the third acceptance criterion
- S29: Given a source whose expression is nested deeper than the parser or reader can follow (about 700 levels in `syntax.parse_expr`, about 1000 in `reader._read_form`; 450 is answered today), then the answer is a refusal with a published category and a location that names an explicit nesting limit; below the limit the program is answered exactly as today.
  - promises: P5
  - tests P5: test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep
- S30: Choose the limit with a reason, publish it in `discover`, and keep it far below Python's recursion limit so the margin does not depend on the caller's stack depth.
  - promises: P5, P6
  - tests P5: test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep
  - tests P6: test_the_manifest_says_how_deeply_the_tool_reads
- S31: 4.
  - not-testable (challenge this): the number of the fourth acceptance criterion
- S32: Given any request object whose fields have the wrong JSON type (operation, source, function, arguments, anything the handlers read), then the answer is `invalid_input` or `unavailable`, never an exception.
  - promises: P7
  - tests P7: test_a_request_that_is_not_an_object_is_refused_as_the_request
- S33: Check every handler's reads, not only the ones named above.
  - promises: P7
  - tests P7: test_a_request_that_is_not_an_object_is_refused_as_the_request
- S34: 5.
  - not-testable (challenge this): the number of the fifth acceptance criterion
- S35: Given a fuzz over at least 500 mangled requests (field types swapped, fields missing, deep nesting, truncations of the shipped programs at every token and character boundary) across all operations, then 0 Python exceptions and 0 exit codes other than 0.
  - promises: P1
  - tests P1: test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
- S36: Keep a derandomised version of that fuzz in the test suite so a regression is caught.
  - promises: P1
  - tests P1: test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
- S37: 6.
  - not-testable (challenge this): the number of the sixth acceptance criterion
- S38: Given every program, request and answer that was accepted or produced before this change, then it is answered exactly as before (add fields or categories only; no existing test edited).
  - promises: P8
  - tests P8: test_the_limit_leaves_room_for_the_programs_this_repository_ships
- S39: **Authority** SPEC.md lines 463-482 and 503-508 (resource limits are declared, and an exceeded one gives a clean diagnostic), and the F6 rule that every source gets one answer.
  - not-testable (challenge this): names the authority lines and the earlier rule this work answers to
- S40: **Size** M.
  - not-testable (challenge this): declares the size of the delivery
- S41: **Touches** `src/prova/evaluator.py`, `src/prova/syntax.py`, `src/prova/reader.py`, `src/prova/service.py`, tests.
  - not-testable (challenge this): lists the files the work is expected to touch

## Edge matrix

- I1.empty: an empty request object with no fields at all => status 'unavailable' with an 'unknown_operation' refusal, the answer a request naming no operation gets today | self-probe: not probed | pre-feature not probed
- I1.unknown: operation 'not-an-operation', and operation holding a list => status 'unavailable' with an 'unknown_operation' refusal | self-probe: not probed | pre-feature not probed
- I1.malformed: JSON that is a list, a number, a text or null rather than an object => status 'invalid_input' with a 'malformed_request' refusal naming 'request' | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the command reads standard input and calls one pure function; it opens no file, socket or process that could be gone
- I1.repeated: the same mangled request sent twice => the same answer both times, since the command keeps nothing between requests | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): one command answers one request and exits; two commands share no file, lock or state
- I1.crash: a request that used to raise inside a handler => the answer is a refusal and the exit code is 0, which is what every case of the fuzz observes | self-probe: not probed | pre-feature not probed
- I2.empty: source holding the empty text '' => status 'invalid_program' with a 'syntax' refusal, the answer it gets today | self-probe: not probed | pre-feature not probed
- I2.unknown: evaluate naming a function the program never declares => status 'invalid_input' with an 'unknown_function' refusal, as today | self-probe: not probed | pre-feature not probed
- I2.malformed: a shipped program cut off or dented at any 1 character => one JSON answer with a status, never a raise | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): a program carries its own declarations; core-0 has no import, so nothing it depends on can be missing
- I2.repeated: the same source checked twice => the same answer and the same source revision both times | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): reading a source changes nothing, so two readers of one source cannot interfere
- I2.crash: a source nested 2000 forms deep, and a record written with 0 of its 1 declared fields => a located refusal, never a RecursionError or an IndexError | self-probe: not probed | pre-feature not probed
- I3.empty: discover sent with no other field => the full manifest, as today | self-probe: not probed | pre-feature not probed
- I3.unknown: n/a (challenge this): discover reads no field of the request, so there is no unknown value it could be given
- I3.malformed: discover sent with every other field holding the wrong kind of value => the full manifest, since discover reads none of them | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): the manifest is built from the tables in the tool itself and reads nothing outside the process
- I3.repeated: discover asked twice => the same manifest both times, including the same published nesting limit | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): discover reads no mutable state, so two callers cannot observe each other
- I3.crash: n/a (challenge this): discover takes no input to be malformed; the fuzz sends it among all 5 operations and it never raises

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the shipped hour clock with character 550 deleted
  - WHEN a caller asks for its examples
  - THEN one JSON answer comes back and the command exits 0
  - test: test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands
- SC2 (P3): not-held (no held self-probe case)
  - GIVEN the hour clock with character 1191 deleted, so an example writes '(Clock)'
  - WHEN a caller asks for its examples
  - THEN the answer says the program is invalid, names 'Clock' with 1 expected and 0 written, at a line and a column
  - test: test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN a type declaring 1 field and an example writing '(Box 3 4)'
  - WHEN a caller asks for the examples
  - THEN the answer names 'Box' with 1 expected and 2 written, at a line and a column
  - test: test_a_record_written_with_the_wrong_number_of_fields_is_refused
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN an evaluate request whose function field holds the list ['valid-state']
  - WHEN the tool answers it
  - THEN the status is 'invalid_input' and one 'malformed_request' refusal names 'function'
  - test: test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field
- SC5 (P4): not-held (no held self-probe case)
  - GIVEN an evaluate request whose arguments field holds the number 7
  - WHEN the tool answers it
  - THEN the status is 'invalid_input' and one 'malformed_request' refusal names 'arguments'
  - test: test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field
- SC6 (P4): not-held (no held self-probe case)
  - GIVEN an evaluate request whose second argument holds the number 7
  - WHEN the tool answers it
  - THEN the status is 'invalid_input' and one 'malformed_request' refusal names 'arguments[1]'
  - test: test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list
- SC7 (P5): not-held (no held self-probe case)
  - GIVEN a program nested 129 forms deep against a published limit of 128
  - WHEN a caller checks it
  - THEN the status is 'resource_exhausted' with a 'nesting_limit_exceeded' refusal saying 128 allowed and 129 reached, at a line and a column
  - test: test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep
- SC8 (P5): not-held (no held self-probe case)
  - GIVEN a program nested exactly 128 forms deep
  - WHEN a caller checks it
  - THEN the status is 'completed', the answer it gets today
  - test: test_a_source_nested_exactly_at_the_limit_is_answered_as_before
- SC9 (P6): not-held (no held self-probe case)
  - GIVEN a caller reading the manifest, which publishes all 5 operations the tool answers
  - WHEN it reads the resource limits
  - THEN 'expression_nesting' publishes the maximum 128 with the status and the category an exceeded limit carries
  - test: test_the_manifest_says_how_deeply_the_tool_reads
- SC10 (P7): not-held (no held self-probe case)
  - GIVEN a request whose operation field holds the list ['check']
  - WHEN the tool answers it
  - THEN the status is 'unavailable' with one 'unknown_operation' refusal, the answer a misspelled operation gets
  - test: test_an_operation_that_is_not_a_name_is_answered_as_one_the_tool_does_not_have
- SC11 (P7): not-held (no held self-probe case)
  - GIVEN JSON that is the bare number 5 rather than an object with fields
  - WHEN the tool answers it
  - THEN the status is 'invalid_input' and one 'malformed_request' refusal names 'request'
  - test: test_a_request_that_is_not_an_object_is_refused_as_the_request
- SC12 (P1): not-held (no held self-probe case)
  - GIVEN a corpus of more than 500 mangled requests over all 5 operations, built from the 3 shipped programs cut and dented at every character
  - WHEN each one is sent
  - THEN 0 of them raise and 0 exit with a code other than 0
  - test: test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
- SC13 (P8): not-held (no held self-probe case)
  - GIVEN the 3 programs this repository ships, whose deepest nesting is 10, and a published limit of 128
  - WHEN each one is checked under the new rules
  - THEN the status is 'completed' for all 3 and the published limit stands at least 4 times above the deepest of them
  - test: test_the_limit_leaves_room_for_the_programs_this_repository_ships
- SC14 (P2): not-held (no held self-probe case)
  - GIVEN an evaluate request whose argument text nests 129 forms deep
  - WHEN the tool answers it
  - THEN a located 'nesting_limit_exceeded' refusal says its place stands in 'argument'
  - test: test_an_argument_nested_past_the_limit_is_refused_the_same_way

## Questions for the owner

- S26: Should a non-string function field carry malformed_request as criterion 2 states, even though a number and a null are answered unknown_function today?
  - existing behaviour: today evaluate with function 7 or null answers invalid_input with the unknown_function category, not malformed_request; a list or an object raises TypeError instead; no existing test sends a non-string function, which tests/properties/test_i1_s2_int_evaluate_arity_and_unknown_function.py confirms by drawing only names
  - status: decided at oracle
- S38: Is a published nesting limit of 128 forms the right trade between a margin that does not depend on the caller stack and leaving every real program answered?
  - existing behaviour: a nesting limit kept far below Python recursion limit, as S30 requires, refuses programs nested between that limit and about 500 that this tool answers today, so S38 and S30 cannot both hold for those depths; no program this repository ships or tests nests deeper than 10
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- M docs/ROADMAP.md (+5 -2 lines)
- A docs/contract-report/DECISIONS.md (+11 -0 lines)
- A docs/contract-report/SUMMARY.md (+445 -0 lines)
- A docs/contract-report/TRACE.md (+5 -0 lines)
- A docs/f2fix/DECISIONS.md (+12 -0 lines)
- A docs/f2fix/SUMMARY.md (+425 -0 lines)
- A docs/f2fix/TRACE.md (+5 -0 lines)
- A docs/feature/contract-report/craft.md (+116 -0 lines)
- A docs/feature/contract-report/oracle.md (+61 -0 lines)
- A docs/feature/contract-report/selfreview.md (+50 -0 lines)
- A docs/feature/robustness/craft.md (+210 -0 lines)
- A docs/feature/robustness/design.md (+135 -0 lines)
- A docs/feature/robustness/oracle.md (+92 -0 lines)
- M docs/spec-trace.md (+9 -0 lines)
- M src/prova/__main__.py (+16 -2 lines)
- M src/prova/checker.py (+317 -8 lines)
- M src/prova/evaluator.py (+150 -33 lines)
- M src/prova/reader.py (+84 -2 lines)
- M src/prova/service.py (+360 -51 lines)
- M src/prova/syntax.py (+42 -0 lines)
- A tests/acceptance/_f13_contract_fixtures.py (+205 -0 lines)
- M tests/acceptance/_f2_cycle_fixtures.py (+70 -0 lines)
- A tests/acceptance/_r1_robustness_fixtures.py (+262 -0 lines)
- A tests/acceptance/test_f13_b1_a_function_without_a_precondition_is_recorded_as_omitted.py (+55 -0 lines)
- A tests/acceptance/test_f13_b2_a_contract_written_as_true_is_recorded_as_trivial.py (+92 -0 lines)
- A tests/acceptance/test_f13_b3_a_real_contract_is_recorded_as_neither.py (+102 -0 lines)
- A tests/acceptance/test_f13_b4_a_program_that_promises_nothing_is_not_called_meaningful.py (+125 -0 lines)
- A tests/acceptance/test_f13_b5_the_manifest_publishes_the_shape_of_the_report.py (+132 -0 lines)
- A tests/acceptance/test_f2fix_b1_a_cycle_is_named_in_declaration_order.py (+77 -0 lines)
- A tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py (+163 -0 lines)
- A tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py (+174 -0 lines)
- A tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py (+197 -0 lines)
- A tests/acceptance/test_r1_b4_a_program_too_deep_to_run_is_refused_not_crashed.py (+202 -0 lines)
- A tests/acceptance/test_r1_b5_text_that_is_not_a_request_is_answered_too.py (+133 -0 lines)
- A tests/properties/_r1_mangled_requests.py (+247 -0 lines)
- A tests/properties/test_f13_contract_report_laws.py (+186 -0 lines)
- M tests/properties/test_f2_call_graph_cycles.py (+82 -2 lines)
- A tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py (+180 -0 lines)
- A tests/properties/test_r1_p2_the_published_nesting_limit_is_the_one_enforced.py (+125 -0 lines)
- A tests/properties/test_r1_p3_a_written_record_carries_one_value_per_declared_field.py (+112 -0 lines)
- A tests/unit/test_f13_contract_report_refuses_what_it_cannot_say.py (+102 -0 lines)
- A tests/unit/test_r1_only_the_request_reader_reads_a_submitted_field.py (+193 -0 lines)

## Commits (git log, BASE to HEAD)

- c281805 [F2fix] notice when the cycle search names or orders the functions wrongly
- 39794d8 [F2fix] stop claiming that the cycle refusal carries no place
- 5a41451 [F2fix] hand the change over with its record
- 988db32 Roadmap: the location follow-up was delivered by F10
- 5b558e4 [F13] say which contracts are missing or trivial
- 7eceb90 [F13] hand the contract report over with its record
- fed906d [F13] read a contract block for its value, and publish every part of the report
- 6c91fee [F13] regenerate the record against the final tree
- cf6046c [F13] call the second review finding what it was: a test gap
- f389095 [F13] close the record: the self-review and the handoff
- 18d3066 Give one owner the number of fields a constructor declares
- eecd944 R1 oracle: say what every mangled request must come back as
- e0cb22e R1 design: name the three gates each crashing input is refused at
- 55b477a Answer every request instead of ending in a traceback
- 7f5a75b Write down what was built, what it cost and what it leaves open
- fa36a23 Answer a program too long to run, and text that is not a request
- c4e0717 Measure the record against the branch it describes
- c3e6331 Re-measure the cost of the tests over all of them
- 3d0eb88 Let a step count a place in a list it was handed
- 8b6cde4 Measure the record against the branch this work now sits on

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-robust/request.md
- **promises**:
  - P1: A caller who sends any request the tool can receive gets one JSON answer on standard output and the command exits 0.
  - P2: A caller whose input breaks a rule gets a located refusal in a published category instead of a Python traceback.
  - P3: A caller who writes a record in an example without one value per declared field is told which record, how many values it takes, how many were written and where to go.
  - P4: A caller whose function field is not a name, or whose arguments are not a list of texts, is answered invalid input naming the one field it must repair.
  - P5: A caller whose text nests deeper than the tool reads is told the limit, how deep the text went and where the form that went too deep stands.
  - P6: A caller reading the manifest learns the nesting limit, the status and the category it will meet before it sends anything.
  - P7: A caller whose request fields hold the wrong kind of JSON value, or whose request is not an object at all, is answered invalid input or unavailable, never an exception.
  - P8: A caller who sends any program, request or answer the tool accepted before this change gets exactly the answer it got before.
- **sentence_map**:
  - S1 => not-testable: states the project, its test command and its green baseline
  - S2 => not-testable: names SPEC.md as the authority this work answers to
  - S3 => not-testable: a process promise about what this delivery may edit
  - S4 => not-testable: a process promise to stop and report a conflict with an existing test
  - S5 => not-testable: a process promise to ignore one directory of the repository
  - S6 => not-testable: a process promise about which worktree and branch the work happens in
  - S7 => not-testable: a process promise about how a commit message ends
  - S8 => not-testable: the attribution line a commit message must end with
  - S9 => not-testable: a process promise not to push and not to merge
  - S10 => P8
  - S11 => not-testable: states that another small delivery runs in parallel
  - S12 => not-testable: states which earlier features are already on main
  - S13 => not-testable: tells the author which existing code to read before designing
  - S14 => not-testable: repeats the process promise to stop and report a conflict
  - S15 => not-testable: a process promise about where the author keeps its scripts
  - S16 => not-testable: a process promise about shell quoting and leaving the tree clean
  - S17 => P1
  - S18 => P2
  - S19 => not-testable: says who found the defects and that each exists on main today
  - S20 => not-testable: the heading standing over the acceptance criteria
  - S21 => not-testable: the number of the first acceptance criterion
  - S22 => P1,P3
  - S23 => P3
  - S24 => P3
  - S25 => not-testable: the number of the second acceptance criterion
  - S26 => P4
  - S27 => P4
  - S28 => not-testable: the number of the third acceptance criterion
  - S29 => P5
  - S30 => P5,P6
  - S31 => not-testable: the number of the fourth acceptance criterion
  - S32 => P7
  - S33 => P7
  - S34 => not-testable: the number of the fifth acceptance criterion
  - S35 => P1
  - S36 => P1
  - S37 => not-testable: the number of the sixth acceptance criterion
  - S38 => P8
  - S39 => not-testable: names the authority lines and the earlier rule this work answers to
  - S40 => not-testable: declares the size of the delivery
  - S41 => not-testable: lists the files the work is expected to touch
- **scenarios**:
  - SC1 | P1 | GIVEN the shipped hour clock with character 550 deleted | WHEN a caller asks for its examples | THEN one JSON answer comes back and the command exits 0
  - SC2 | P3 | GIVEN the hour clock with character 1191 deleted, so an example writes '(Clock)' | WHEN a caller asks for its examples | THEN the answer says the program is invalid, names 'Clock' with 1 expected and 0 written, at a line and a column
  - SC3 | P3 | GIVEN a type declaring 1 field and an example writing '(Box 3 4)' | WHEN a caller asks for the examples | THEN the answer names 'Box' with 1 expected and 2 written, at a line and a column
  - SC4 | P4 | GIVEN an evaluate request whose function field holds the list ['valid-state'] | WHEN the tool answers it | THEN the status is 'invalid_input' and one 'malformed_request' refusal names 'function'
  - SC5 | P4 | GIVEN an evaluate request whose arguments field holds the number 7 | WHEN the tool answers it | THEN the status is 'invalid_input' and one 'malformed_request' refusal names 'arguments'
  - SC6 | P4 | GIVEN an evaluate request whose second argument holds the number 7 | WHEN the tool answers it | THEN the status is 'invalid_input' and one 'malformed_request' refusal names 'arguments[1]'
  - SC7 | P5 | GIVEN a program nested 129 forms deep against a published limit of 128 | WHEN a caller checks it | THEN the status is 'resource_exhausted' with a 'nesting_limit_exceeded' refusal saying 128 allowed and 129 reached, at a line and a column
  - SC8 | P5 | GIVEN a program nested exactly 128 forms deep | WHEN a caller checks it | THEN the status is 'completed', the answer it gets today
  - SC9 | P6 | GIVEN a caller reading the manifest, which publishes all 5 operations the tool answers | WHEN it reads the resource limits | THEN 'expression_nesting' publishes the maximum 128 with the status and the category an exceeded limit carries
  - SC10 | P7 | GIVEN a request whose operation field holds the list ['check'] | WHEN the tool answers it | THEN the status is 'unavailable' with one 'unknown_operation' refusal, the answer a misspelled operation gets
  - SC11 | P7 | GIVEN JSON that is the bare number 5 rather than an object with fields | WHEN the tool answers it | THEN the status is 'invalid_input' and one 'malformed_request' refusal names 'request'
  - SC12 | P1 | GIVEN a corpus of more than 500 mangled requests over all 5 operations, built from the 3 shipped programs cut and dented at every character | WHEN each one is sent | THEN 0 of them raise and 0 exit with a code other than 0
  - SC13 | P8 | GIVEN the 3 programs this repository ships, whose deepest nesting is 10, and a published limit of 128 | WHEN each one is checked under the new rules | THEN the status is 'completed' for all 3 and the published limit stands at least 4 times above the deepest of them
  - SC14 | P2 | GIVEN an evaluate request whose argument text nests 129 forms deep | WHEN the tool answers it | THEN a located 'nesting_limit_exceeded' refusal says its place stands in 'argument'
- **conflicts**:
  - S1 | NONE | ran uv run pytest -q tests on this worktree before any change: 1042 passed in 116.59s, the baseline the sentence states
  - S2 | NONE | read SPEC.md lines 455 to 515; nothing in this work changes what the specification says
  - S3 | NONE | this work adds test files only and edits no existing test and no line of SPEC.md
  - S4 | NONE | a process promise about reporting, which this record and the pause that follows it carry out
  - S5 | NONE | the .relay directory is not read and no test added here opens it
  - S6 | NONE | every file written so far is inside the worktree at /Users/andrealaforgia/dev/prova-wt-robust
  - S7 | NONE | a process promise about the commit message, carried out when the work is committed
  - S8 | NONE | a process promise about the attribution line, carried out when the work is committed
  - S9 | NONE | a process promise about pushing and merging, which this work does not do
  - S10 | NONE | the whole suite was run green before any change and is run again after each commit
  - S11 | NONE | the parallel delivery touches tests and docs of F2; this work adds new test files under new names
  - S12 | NONE | git log shows F1 to F10 on the branch this worktree was cut from, at 5d3a90f
  - S13 | NONE | read syntax.py, service.py and the diagnostic kinds table in checker.py; the new refusals follow the same table
  - S14 | NONE | the same process promise as S4, carried out by this conflict table and the pause
  - S15 | NONE | every script written for this work is under the nwstep workspace, never in the repository
  - S16 | NONE | the record is passed as a script file and git status is read before the final message
  - S17 | NONE | no handler promises anything other than one JSON answer today; the sentence states what the crashes break
  - S18 | NONE | the existing refusals already carry a published category and a place; the sentence extends that to the crashing inputs
  - S19 | NONE | reproduced all four crash families on this worktree before any change, in the workspace probe scripts
  - S20 | NONE | a heading over the criteria, which contradicts no behaviour of the system
  - S21 | NONE | the number of a criterion, which contradicts no behaviour of the system
  - S22 | NONE | reproduced: both deletions end in IndexError at evaluator.py line 154 reading a field off a record with no fields
  - S23 | NONE | the cause is in the checker: the value check for an example tests the constructor name and never its field count
  - S24 | NONE | the checker already refuses a constructor call expression with the wrong count under arity_mismatch; the value path simply does not
  - S25 | NONE | the number of a criterion, which contradicts no behaviour of the system
  - S26 | CONFLICT | today evaluate with function 7 or null answers invalid_input with the unknown_function category, not malformed_request; a list or an object raises TypeError instead; no existing test sends a non-string function, which tests/properties/test_i1_s2_int_evaluate_arity_and_unknown_function.py confirms by drawing only names | Should a non-string function field carry malformed_request as criterion 2 states, even though a number and a null are answered unknown_function today?
  - S27 | NONE | today a non-list arguments field raises TypeError and a non-string element raises in the reader; no existing test sends either
  - S28 | NONE | the number of a criterion, which contradicts no behaviour of the system
  - S29 | NONE | measured on this worktree: a bare text nests to 999 before RecursionError and a checked program to about 500; no limit is declared anywhere today
  - S30 | NONE | discover publishes resource_limits with enforced false and no number, so publishing a limit fills a field that already exists
  - S31 | NONE | the number of a criterion, which contradicts no behaviour of the system
  - S32 | NONE | reproduced every wrong-kind field crash listed in the criterion on this worktree before any change
  - S33 | NONE | read every handler in service.py and every field each one reads; the fuzz covers all 5 operations and all 4 request fields
  - S34 | NONE | the number of a criterion, which contradicts no behaviour of the system
  - S35 | NONE | ran a corpus of 10249 mangled requests on this worktree before any change: 56 raised, 0 exited non-zero
  - S36 | NONE | the suite has no fuzz today; the corpus added here is built from one fixed seed and the shipped programs
  - S37 | NONE | the number of a criterion, which contradicts no behaviour of the system
  - S38 | CONFLICT | a nesting limit kept far below Python recursion limit, as S30 requires, refuses programs nested between that limit and about 500 that this tool answers today, so S38 and S30 cannot both hold for those depths; no program this repository ships or tests nests deeper than 10 | Is a published nesting limit of 128 forms the right trade between a margin that does not depend on the caller stack and leaving every real program answered?
  - S39 | NONE | read SPEC.md lines 463 to 482 and 503 to 508; they declare resource budgets with controlled diagnostic failure, which this work supplies
  - S40 | NONE | the size is declared in the workspace as M and this record does not change it
  - S41 | NONE | the files listed are the ones the design touches, plus checker.py where the value rule lives, which the touches list calls out through syntax.py
- **decisions**:
  - S26: Follow criterion 2 exactly: any non-string function field is answered invalid_input with a malformed_request refusal naming 'function', because unknown_function means the program declares no such name while a list or a number is not a name at all; no existing test is edited, since none sends a non-string function.
  - S38: Publish a nesting limit of 128 forms. Measured on this worktree, the deepest path through reader, parser, checker and evaluator costs 2 CPython frames per nesting level (peak frames = 2d + 13), so 128 costs 269 of the default 1000 and leaves over 700 frames for the caller's own stack. It is also about 12 times the deepest nesting of any program this repository ships or tests, measured at 10.
  - DEC1: The cause of the IndexError is in the checker, not the evaluator: the check over a value written in an example tests that the constructor is declared and never that it carries one value per declared field. It is repaired there, under the arity_mismatch category the same defect already carries when it appears in an expression, so one rule answers it wherever it is written.
  - DEC2: A text past the nesting limit is answered with the status resource_exhausted and a new nesting_limit_exceeded category, not invalid_program, because SPEC.md line 505 says a limit must not silently become a semantic bound on the program's domain; resource_exhausted is already the name the suite's own status vocabulary uses for an exhausted budget.
  - DEC3: No formal model (Quint). Every behaviour here is one request answered by a pure function, with no protocol, no concurrency, no stored state and no sequence of steps, so there is no state space a model would explore that the generated properties do not already cover directly.
  - DEC4: typesafe: unavailable: TYPESAFE_API_KEY is absent from this process environment, so jev_decide.py exited 3 without transmitting anything; the choices of owner, category and status were settled locally against the existing diagnostic kinds table and the suite's own status vocabulary.
  - DEC5: The damaged-program domain is closed and finite, so an exhaustive loop over every character of every shipped program owns it rather than a generated property; the properties are kept for the open domains of request shape and nesting depth.
- **mapping**:
  - P1 => test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - P2 => test_an_argument_nested_past_the_limit_is_refused_the_same_way
  - P3 => test_a_record_written_with_the_wrong_number_of_values_is_refused
  - P4 => test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field
  - P5 => test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep
  - P6 => test_the_manifest_says_how_deeply_the_tool_reads
  - P7 => test_a_request_that_is_not_an_object_is_refused_as_the_request
  - P8 => test_the_limit_leaves_room_for_the_programs_this_repository_ships
- **covers_scenarios**:
  - SC1 => test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands
  - SC2 => test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands
  - SC3 => test_a_record_written_with_the_wrong_number_of_fields_is_refused
  - SC4 => test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field
  - SC5 => test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field
  - SC6 => test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list
  - SC7 => test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep
  - SC8 => test_a_source_nested_exactly_at_the_limit_is_answered_as_before
  - SC9 => test_the_manifest_says_how_deeply_the_tool_reads
  - SC10 => test_an_operation_that_is_not_a_name_is_answered_as_one_the_tool_does_not_have
  - SC11 => test_a_request_that_is_not_an_object_is_refused_as_the_request
  - SC12 => test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - SC13 => test_the_limit_leaves_room_for_the_programs_this_repository_ships
  - SC14 => test_an_argument_nested_past_the_limit_is_refused_the_same_way
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC6 => base differs
  - SC7 => base differs
  - SC8 => base held
  - SC9 => base differs
  - SC10 => base differs
  - SC11 => base differs
  - SC12 => base differs
  - SC13 => base differs
  - SC14 => base differs
- **interfaces**:
  - I1: the prova command, which reads one JSON request on standard input and writes one JSON answer on standard output
  - I2: the operations that read a program from the request source field: check, examples, evaluate and verify
  - I3: the discover operation, which publishes the statuses, the diagnostic categories and the resource limits of the tool
- **matrix**:
  - I1.empty => an empty request object with no fields at all => status 'unavailable' with an 'unknown_operation' refusal, the answer a request naming no operation gets today
  - I1.unknown => operation 'not-an-operation', and operation holding a list => status 'unavailable' with an 'unknown_operation' refusal
  - I1.malformed => JSON that is a list, a number, a text or null rather than an object => status 'invalid_input' with a 'malformed_request' refusal naming 'request'
  - I1.dependency-gone => n/a: the command reads standard input and calls one pure function; it opens no file, socket or process that could be gone
  - I1.repeated => the same mangled request sent twice => the same answer both times, since the command keeps nothing between requests
  - I1.concurrent => n/a: one command answers one request and exits; two commands share no file, lock or state
  - I1.crash => a request that used to raise inside a handler => the answer is a refusal and the exit code is 0, which is what every case of the fuzz observes
  - I2.empty => source holding the empty text '' => status 'invalid_program' with a 'syntax' refusal, the answer it gets today
  - I2.unknown => evaluate naming a function the program never declares => status 'invalid_input' with an 'unknown_function' refusal, as today
  - I2.malformed => a shipped program cut off or dented at any 1 character => one JSON answer with a status, never a raise
  - I2.dependency-gone => n/a: a program carries its own declarations; core-0 has no import, so nothing it depends on can be missing
  - I2.repeated => the same source checked twice => the same answer and the same source revision both times
  - I2.concurrent => n/a: reading a source changes nothing, so two readers of one source cannot interfere
  - I2.crash => a source nested 2000 forms deep, and a record written with 0 of its 1 declared fields => a located refusal, never a RecursionError or an IndexError
  - I3.empty => discover sent with no other field => the full manifest, as today
  - I3.unknown => n/a: discover reads no field of the request, so there is no unknown value it could be given
  - I3.malformed => discover sent with every other field holding the wrong kind of value => the full manifest, since discover reads none of them
  - I3.dependency-gone => n/a: the manifest is built from the tables in the tool itself and reads nothing outside the process
  - I3.repeated => discover asked twice => the same manifest both times, including the same published nesting limit
  - I3.concurrent => n/a: discover reads no mutable state, so two callers cannot observe each other
  - I3.crash => n/a: discover takes no input to be malformed; the fuzz sends it among all 5 operations and it never raises
- **laws**:
  - LAW1 | Every request the tool can receive is answered with one JSON object carrying a status, printed on standard output, and the command exits 0 | generator=test_no_generated_request_ever_comes_back_as_an_exception | observation=the exit code, the bytes on standard output parsed as JSON, and the presence of a status field | mutant=a handler that reads a field without checking its kind lets a TypeError out, so nothing is printed and the command exits non-zero
  - LAW2 | The greatest nesting the manifest publishes is exactly the greatest nesting the tool reads: every depth at or under it is answered as before and every depth past it is refused with that same number | generator=test_every_depth_past_the_published_limit_is_refused_for_its_nesting | observation=the status and the expected and actual counts of the nesting refusal, compared with the maximum read from the manifest | mutant=publishing one number while enforcing another makes a caller that obeys the manifest still meet a refusal
  - LAW3 | A record written in an example carries exactly one value per field its type declares, or the program is refused naming the record with the count declared beside the count written | generator=test_a_record_written_with_the_wrong_number_of_values_is_refused | observation=the status, and the symbol, expected and actual of the count refusal, against the counts the test itself wrote into the program | mutant=accepting a record with too few values lets the evaluator reach for a field that is not there
- **messages**:
  - MSG1 | a program whose body nests 129 forms deep | the text nests more deeply than this tool reads | the tool reads a nested form by calling itself once per form and declares a maximum of 128 so that it refuses instead of exhausting the interpreter stack | write the inner forms as separate let bindings so that no form stands more than 128 forms inside the text, or read the maximum from the resource limits the discover operation publishes | test=test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep
  - MSG2 | an evaluate request whose function field holds the list ['valid-state'] | the function field of the request holds a list, not the name of a function | this tool looks a function up by its name and a value of another kind names nothing to look up | send the function as one JSON string, and read the names the program declares from the check operation | test=test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field
  - MSG3 | an example writing '(Clock)' where Clock declares one field hr | the record Clock is written with 0 values and declares 1 field | an example supplies one closed value for each field the type declares so that the example can be run, and a record with fewer has no value for the field a reader of it asks for | write the record with 1 value, as (Clock 12), or declare the field it is missing on the type | test=test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands
- **red**: `uv run pytest -q tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py tests/properties/test_r1_p2_the_published_nesting_limit_is_the_one_enforced.py tests/properties/test_r1_p3_a_written_record_carries_one_value_per_declared_field.py` exited 1 in 8.816s
  - failing on the pre-feature tree (29): tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py::test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands[550], tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py::test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands[1191], tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py::test_a_record_written_with_the_wrong_number_of_fields_is_refused[no, tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py::test_a_record_written_with_the_wrong_number_of_fields_is_refused[two, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field[a, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field[an, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field[nothing, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field[a, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field[an, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field[nothing, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field[one, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list[a, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list[an, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list[nothing, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_operation_that_is_not_a_name_is_answered_as_one_the_tool_does_not_have[a, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_operation_that_is_not_a_name_is_answered_as_one_the_tool_does_not_have[an, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_request_that_is_not_an_object_is_refused_as_the_request[a, tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_request_that_is_not_an_object_is_refused_as_the_request[nothing, tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_the_manifest_says_how_deeply_the_tool_reads, tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep, tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_a_source_nested_exactly_at_the_limit_is_answered_as_before, tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_the_limit_leaves_room_for_the_programs_this_repository_ships, tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_an_argument_nested_past_the_limit_is_refused_the_same_way, tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly, tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_no_generated_request_ever_comes_back_as_an_exception, tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_no_generated_depth_ever_comes_back_as_an_exception, tests/properties/test_r1_p2_the_published_nesting_limit_is_the_one_enforced.py::test_every_depth_up_to_the_published_limit_is_accepted, tests/properties/test_r1_p2_the_published_nesting_limit_is_the_one_enforced.py::test_every_depth_past_the_published_limit_is_refused_for_its_nesting, tests/properties/test_r1_p3_a_written_record_carries_one_value_per_declared_field.py::test_a_record_written_with_the_wrong_number_of_values_is_refused
  - tests (read from the run): 35 failed, 9 passed in 8.24s
  ```text
  E               /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-robust/red-tree/tests/properties/test_r1_p3_a_written_record_carries_one_value_per_declared_field.py:86

  tests/properties/test_r1_p3_a_written_record_carries_one_value_per_declared_field.py:86: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py::test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands[550]
  FAILED tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py::test_the_hour_clock_with_an_emptied_record_is_refused_where_it_stands[1191]
  FAILED tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py::test_a_record_written_with_the_wrong_number_of_fields_is_refused[no field where one is declared]
  FAILED tests/acceptance/test_r1_b1_a_value_missing_a_field_is_refused_not_crashed.py::test_a_record_written_with_the_wrong_number_of_fields_is_refused[two fields where one is declared]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field[a list holding the name]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field[a true/false value]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field[a whole number]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field[an object holding the name]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_function_that_is_not_a_name_is_refused_by_the_name_of_the_field[nothing at all]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field[a whole number]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field[an object]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field[nothing at all]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_arguments_that_are_not_a_list_are_refused_by_the_name_of_the_field[one text, not wrapped in a list]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list[a list]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list[a whole number]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list[an object]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_argument_that_is_not_a_text_is_refused_by_its_place_in_the_list[nothing at all]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_operation_that_is_not_a_name_is_answered_as_one_the_tool_does_not_have[a list holding the name]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_an_operation_that_is_not_a_name_is_answered_as_one_the_tool_does_not_have[an object holding the name]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_request_that_is_not_an_object_is_refused_as_the_request[a bare number]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_request_that_is_not_an_object_is_refused_as_the_request[a bare text]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_request_that_is_not_an_object_is_refused_as_the_request[a list of requests]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_request_that_is_not_an_object_is_refused_as_the_request[a true/false value]
  FAILED tests/acceptance/test_r1_b2_a_request_field_of_the_wrong_kind_is_refused_by_name.py::test_a_request_that_is_not_an_object_is_refused_as_the_request[nothing at all]
  FAILED tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_the_manifest_says_how_deeply_the_tool_reads
  FAILED tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep
  FAILED tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_a_source_nested_exactly_at_the_limit_is_answered_as_before
  FAILED tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_the_limit_leaves_room_for_the_programs_this_repository_ships
  FAILED tests/acceptance/test_r1_b3_a_source_nested_past_the_published_limit_is_refused.py::test_an_argument_nested_past_the_limit_is_refused_the_same_way
  FAILED tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  FAILED tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_no_generated_request_ever_comes_back_as_an_exception
  FAILED tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_no_generated_depth_ever_comes_back_as_an_exception
  FAILED tests/properties/test_r1_p2_the_published_nesting_limit_is_the_one_enforced.py::test_every_depth_up_to_the_published_limit_is_accepted
  FAILED tests/properties/test_r1_p2_the_published_nesting_limit_is_the_one_enforced.py::test_every_depth_past_the_published_limit_is_refused_for_its_nesting
  FAILED tests/properties/test_r1_p3_a_written_record_carries_one_value_per_declared_field.py::test_a_record_written_with_the_wrong_number_of_values_is_refused
  35 failed, 9 passed in 8.24s
  ```

## 3. craft: Craft the change (revision 1, STALE: an earlier step was recorded again after it; record it again or say why it still holds)

- **refactor_commits**:
  - 33167eb
- **refactor_check**: the check ran on the parent and on each refactor commit
  - 33167ebaf3f8 (Give one owner the number of fields a constructor declares): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 123.987s
  - tests (read from the run): 1088 passed in 123.84s
  - slowest: 6.51s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.25s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.76s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.33s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 3.15s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 2.99s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 1.92s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.58s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.56s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.39s call tests/properties/test_obligation_inventory_laws.py::test_putting_a_call_out_of_reach_keeps_what_it_owes
  ```text
  ........................................................................ [  6%]
  ........................................................................ [ 13%]
  ........................................................................ [ 19%]
  ........................................................................ [ 26%]
  ........................................................................ [ 33%]
  ........................................................................ [ 39%]
  ........................................................................ [ 46%]
  ........................................................................ [ 52%]
  ........................................................................ [ 59%]
  ........................................................................ [ 66%]
  ........................................................................ [ 72%]
  ........................................................................ [ 79%]
  ........................................................................ [ 86%]
  ........................................................................ [ 92%]
  ........................................................................ [ 99%]
  ........                                                                 [100%]
  ============================= slowest 10 durations =============================
  6.51s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.25s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.76s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.33s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  3.15s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  2.99s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  1.92s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.58s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.56s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.39s call     tests/properties/test_obligation_inventory_laws.py::test_putting_a_call_out_of_reach_keeps_what_it_owes
  1088 passed in 123.84s (0:02:03)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.07s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this process environment, so jev_decide.py exited 3 and nothing was transmitted; the open choices (which component owns the refusal, which published category it carries, which status an exceeded budget gets) were settled locally against the diagnostic kinds table, the existing arity rule over expressions and the status vocabulary the suite already names

## 4. design: Find the owners and design the change (revision 2)

- **owners**:
  - how deep a text may nest => new: src/prova/reader.py, because read_program is the one gate every text passes through, for a program source and for a value in a request alike, and nothing declares a limit anywhere today
  - refusing a text that nests too deep => src/prova/reader.py, where the depth grows, raised as its own refusal and translated where every other refusal of the reader is translated, in src/prova/service.py
  - what a refusal of each category carries => src/prova/checker.py DIAGNOSTIC_KINDS, the existing table the manifest is written from; the new category joins it rather than starting a second table
  - every status an answered request carries => src/prova/service.py STATUSES, the existing table; resource_exhausted joins it
  - a value written in a program carries one value per declared field => src/prova/checker.py _check_value, which already owns what a value written in an example must satisfy and today checks only that its constructor is declared
  - how many fields a constructor declares => src/prova/syntax.py, where resolve_constructor already answers what a constructor is; it becomes a named owner so the checker and the evaluator stop deciding it apart
  - which field of a request holds which kind of value => src/prova/service.py, extending the request validation F10 opened with the source field, so one reader answers for every field instead of one field having a reader and the rest none
  - how far a run of a program may stand inside itself => new: src/prova/evaluator.py, where the evaluator stands inside itself, counted over every evaluation step rather than over calls alone because a call and an expression written inside it stand on the same stack
  - answering text that is not a JSON request at all => src/prova/__main__.py reads the text and src/prova/service.py builds the refusal, the one place every malformed-request refusal is built
  - the limits a caller reads before it sends anything => src/prova/service.py _run_discover, which already publishes a resource_limits field saying none is enforced
- **reuse_decision**: Reused: the diagnostic kinds table and the Diagnostic value object in checker.py, which already refuse a category no kind declares; the arity_mismatch category and AboutTwoCounts, which already say a declared thing took one count and was given another; the STATUSES table; the Refusal value object in service.py; syntax.resolve_constructor; and the F10 request check, which the new request reader absorbs rather than sits beside. Created new: NestingLimit and TooDeeplyNested in reader.py, because no existing owner declares or enforces a budget and the reader is the one place depth grows; Request, FunctionName and ArgumentTexts in service.py, because today every handler reads raw request fields itself and there is no owner to extend; DeclaredConstructor in syntax.py, because the fact it answers is decided in two places that do not know about each other. No new diagnostic table, no new status table, no second refusal shape.
- **paradigm**: oo
- **boundaries**:
  - B1 the command boundary: src/prova/__main__.py owns standard input and standard output; it decides text that is JSON from text that is not, and everything that parses goes to the service as one value
  - B2 the request boundary: service.Request is the one reader of a raw JSON field; after this change no handler calls get on the request, so a field of the wrong kind is refused once, by name, before any work starts
  - B3 the text boundary: reader.read_program is the one place a text becomes a tree and the one place nesting grows, so the limit holds for a program source and for an argument value without either knowing about the other
  - B4 the published vocabulary boundary: checker.DIAGNOSTIC_KINDS and service.STATUSES are what discover publishes; nothing outside them names a category or a status, which Diagnostic already enforces at construction
  - B5 the program boundary: checker.check_program decides whether a program may be run, and the evaluator runs only what it passed; a value the evaluator cannot read is therefore refused before it, not caught inside it
- **domain_types**:
  - NestingLimit (new, src/prova/reader.py): the greatest nesting this tool reads. Holds the number and the name the manifest publishes it under, and builds the refusal when a depth passes it. One object, read by the reader when it enforces and by discover when it publishes
  - TooDeeplyNested (new, src/prova/reader.py): the refusal a text that nests too deep raises, carrying the limit, the depth reached and the place the form that went too deep stands at. Not a ReaderError, so it cannot be answered as a syntax refusal by mistake
  - Request (new, src/prova/service.py): the one reader of a raw JSON request. Refuses anything that is not an object, naming request; answers each field with its value or with the refusal naming that field
  - FunctionName (new, src/prova/service.py): the name of a function a request asks for. Its constructor refuses anything that is not a string, so no later step can be reached with a list
  - ArgumentTexts (new, src/prova/service.py): the texts of the arguments a request supplies. Its constructor refuses a value that is not a list and any element that is not a string, naming the place in the list
  - DeclaredConstructor (new, src/prova/syntax.py): what one constructor declares, its owning type and its fields. The one answer to how many values it takes, asked by the rule over expressions and by the rule over values instead of each counting for itself
  - EvaluationDepthLimit (new, src/prova/evaluator.py): how many evaluation steps this tool lets stand inside one another. Holds the number and the name the manifest publishes it under; the evaluator asks it and discover publishes it, so the two cannot drift apart
  - EvaluationTooDeep (new, src/prova/evaluator.py): the refusal a program too long to run raises, carrying the limit, the depth reached and the step that would have gone past it
  - checker.DIAGNOSTIC_KINDS (changed): gains nesting_limit_exceeded and evaluation_depth_exceeded, each carrying two counts and always placed; the first points into a source or an argument, the second always into the source
  - service.STATUSES (changed): gains resource_exhausted, for an answer where a declared budget was passed and no rule of core-0 was read over the text
- **invariants**:
  - INV1 | No text is read into a tree more deeply than the published limit, whether it is the source of a program or a value a request supplies, so no later stage can be reached with a tree deeper than the limit | witness=src/prova/reader.py:NestingLimit | bypass=a caller that imports the private form reader and drives it itself bypasses the count; nothing in this repository does, and the public read_program cannot
  - INV2 | The number the manifest publishes and the number a refusal reports are the same number, because both read it from the one limit object rather than each holding a copy | witness=src/prova/service.py:_run_discover | bypass=none
  - INV3 | No handler reads a field of a raw request: every field is read once through the one request reader, which answers with the value or with the refusal naming the field | witness=src/prova/service.py:Request | bypass=none; an architectural test checks the whole service module, not a fixed list of handlers
  - INV4 | The step that evaluates receives a function name and argument texts already proven to be a string and a list of strings, so it cannot be reached with anything else and does not check again | witness=src/prova/service.py:FunctionName | bypass=Python lets a caller build the value object around any object by hand; the smart constructor is the only path the service uses and it refuses
  - INV5 | A value written in a program carries exactly one value per field its constructor declares, or check_program refuses the program, so the evaluator never meets a record with a field that is not there | witness=src/prova/checker.py:_check_value | bypass=the evaluator can still be called directly with a hand-built value; the service calls it only after check_program has passed the program
  - INV6 | One object answers how many fields a constructor declares, and every rule that compares that count asks it rather than counting for itself | witness=src/prova/syntax.py:DeclaredConstructor | bypass=none
  - INV7 | The evaluator stands inside itself no more times than the published number, counted over every evaluation step rather than over calls alone, so a chain of calls, an expression written inside an expression and any mixture of the two are bounded by one number on one stack | witness=src/prova/evaluator.py:EvaluationDepthLimit | bypass=a caller that imports the evaluator and calls it with a depth of its own choosing; the service always starts at zero
  - INV8 | Text this tool cannot read as a JSON request is answered like any other unreadable input, by name and with the place the text stopped at, and the command exits 0; the name reserved for a failure of the tool itself is kept for that and stays out of the published statuses | witness=src/prova/__main__.py:_unreadable_text | bypass=none
- **prefactoring**: yes
- **prefactoring_reason**: The fact that a constructor declares a given number of fields is decided today in two places that do not know about each other: the checker's rule over an expression and the evaluator's check of a value a request supplies. The new rule over a value written in an example would be a third copy of the same comparison. One behaviour-preserving commit first extracts that fact into DeclaredConstructor beside resolve_constructor in syntax.py and makes both existing callers ask it; the counts, the messages and the categories they produce are unchanged, no test is edited and the suite stays green, so the new rule joins one owner instead of adding a third decider.

## 5. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the three gates design.md names are the three places the code refuses, and the fourth, how far a program is run, was recorded as design revision 2 with the owner's confirmation before it was built
  - D2: pass - how many fields a constructor declares has one owner in syntax.py, asked by the rule over expressions, the rule over values and the evaluator's check; each limit's number is held in one object that both the code enforcing it and the manifest publishing it read
  - D3: pass - the reader knows nothing of the service, the service translates the reader's and the evaluator's refusals into published categories, and the command owns standard input and output while building no refusal of its own
  - D4: pass - src/prova/service.py:205 refuses anything that is not a name, so the step that evaluates cannot be reached with a list; src/prova/service.py:232 and src/prova/service.py:284 do the same for the argument texts and for the request itself
  - D5: pass - src/prova/reader.py:45 holds two values and answers two questions; the one class holding three, DeclaredConstructor, is recorded in craft.md as a deliberate break with its reason and its cost
  - D6: pass - no pattern was introduced; the new types are value objects with smart constructors, the shape this repository already uses for a diagnostic, its kind and a source revision
  - D7: pass - every name comes from what a caller sees, a limit, a refusal, a request, a declared constructor, and none from mechanics; no Manager, Helper or Data anywhere in the change
  - D8: pass - the only infrastructure is standard input and output in the command; the service, the reader, the checker and the evaluator open no file, socket or process, which is why no fake was needed anywhere
  - D9: pass - tests/acceptance/_r1_robustness_fixtures.py:87 drives the real prova command over its standard input and output and reads its exit code, and no acceptance test imports from src; the sweep calls the command's own entry point in process, recorded with its reason and its cost
  - D10: pass - every test name is a sentence about what a caller gets, such as a request field of the wrong kind is refused by name, and none holds a production symbol, a step number or a layer word
  - D11: pass - one fixtures module per layer, the acceptance one driving the real command and the property one building the corpus; no test re-implements a step and none shares state with another
  - D12: pass - tests/properties/test_r1_p3_a_written_record_carries_one_value_per_declared_field.py:64 generates the count declared and the count written and compares the refusal against the numbers the test itself wrote, never against the production rule
  - D13: pass - all nine new files run nine times green, 68 tests, median 6.83s and slowest 6.86s, with no run a tenth of a second from another; one test costs 3.29s and every other is under 0.2s
  - D14: pass - the damaged-program domain is finite and owned by one exhaustive loop over every character of every shipped program, so no property repeats it; the properties cover the open domains of request shape, nesting depth and field counts
  - D15: pass - src/prova/reader.py:72 says what went wrong, why the tool stops there and how to repair it, naming the limit, and src/prova/evaluator.py:65 does the same for a program too long to run
  - D16: n/a: every behaviour here is one request answered by a pure function, with no shared state, no protocol of more than one step, no concurrency and no crash window, so there is no state space a model would explore
  - D17: fixed: the records cited commits and counts from before the branch moved; re-measured against the current history, with the two answers that changed stated with worked examples checked against the branch point, and a test of another feature whose docstring now describes replaced behaviour reported rather than edited
- **independent_review**:
  - REV1 | reviewer=rev-r1 | findings=6 (verdict APPROVE at ae40238) | resolution=all six fixed in b64f259 and 025a94a
  - REV2 | reviewer=rev-r1 | findings=2 (verdict REJECT at 025a94a, none a product defect) | resolution=both fixed after the review, checked by the owner: the law narrowed and the baseline count corrected

## 6. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
  - Both limits are held as one number that the code enforcing them and the manifest publishing them read, so a caller that obeys what it read cannot still meet a refusal.
  - Two answers deliberately differ from before and are stated with worked examples in the record: a record written with the wrong number of values is now refused, and a field of the request is now refused before the program is read.
- **not_verified**:
  - The frame counts behind both limits were measured only on the Python this repository pins. A build with a different frame layout would need them measured again, and neither number was checked on another interpreter.
  - Nothing here is proved. Building a function name and the argument texts is centralised, not proved: Python lets a caller construct those objects around any value by hand. The claim is that this tool has one path and that path refuses.
  - The limits bound the stack the reader and the evaluator use. They are not a claim about memory or about time: a program inside both limits can still build a very large value, and nothing here measures how long a run takes.
  - A record written with the right number of values but the wrong kind of value in one of them is still accepted and run. It does not crash, so it was left alone; it is a gap in the same rule about values and is reported to whoever owns the checker's value rules.
  - The craft step is recorded but marked stale. Its submission could not be replayed because the tool requires the behaviour-preserving commit to be the first commit after the workspace baseline, and a rebase placed another delivery's commits between them. The commit is still the first of this delivery's own commits. The owner decided to leave the record as it stands; nothing about the change itself is affected.
  - A test belonging to an earlier feature still passes unchanged, but its docstring now describes behaviour this change replaced. It was not edited, and is reported to its owner.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit 8b6cde48aa2c397150ef37efd86844f7f4443c60
  - no checks declared

## Not backed by the diff

- The tool now answers every request it can receive with one JSON answer and exit code 0, where before four kinds of input ended in a Python traceback with nothing on standard output.: a guarantee names no test function of the change
- Each is refused at one gate that owns its rule: a submitted request is read in one place, so a field holding the wrong kind of value is named before any work starts and text that is not JSON at all is answered too; a text is read no deeper than the published nesting limit of 128 forms; a program is run no further than the published limit of 160 evaluation steps standing inside one another; and a value written without one value per declared field is refused where it stands, which was the cause of the shipped hour clock crash.: a guarantee names no test function of the change
- The evaluation limit counts every step rather than calls alone, because a call and the expression written inside it stand on the same stack; counting calls would have left the mixture unbounded.: a guarantee names no test function of the change
- Checked by a sweep of mangled requests that is kept in the suite, by a deliberate break of each new behaviour, and by two independent reviews.: a guarantee names no test function of the change
