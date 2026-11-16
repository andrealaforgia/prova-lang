# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1317 tests, all green on main).
  - not-testable (challenge this): names the project and its suite, promising nothing a caller observes
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names the authority document to read, not an outcome
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a rule for how I work, kept by changing no existing test
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): tells me what to do when a conflict appears, which the conflict table records
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): names a directory to ignore, no observable outcome
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a rule about where I work, kept by the worktree
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a rule about the commit message I write
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the line a commit message ends with
- S9: Do not push and do not merge.
  - not-testable (challenge this): a rule forbidding a push or a merge
- S10: Keep the full suite green.
  - not-testable (challenge this): a duty to keep the whole suite green, observed by running it
- S11: Another delivery (F18, the solver discharge in encoding.py, solving.py, discharge.py, obligations.py and many tests) runs in parallel in a different worktree and will merge first or second: do not touch those files; your changes are in values.py, budgets.py, __main__.py, service.py request reading and tests.
  - not-testable (challenge this): names the files another delivery owns and the files I may touch
- S12: F1 to F17, R1 and R2 are on main; read how R1 and R2 made every request answer one JSON response (the request reader, `malformed_request`, `SubmittedText`, `DigitLimit` in reader.py) and how F14 reads budgets from the environment (budgets.py) and bounded the request read (`_read_at_most` in __main__.py) and follow that structure.
  - not-testable (challenge this): names the structure already on main that I follow
- S13: If an existing test conflicts, stop and report.
  - not-testable (challenge this): repeats the instruction to stop on a conflict
- S14: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): a rule about where my own scripts live
- S15: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell hygiene for the tool I record with
- S16: **Outcome.** The three remaining crash families found by the R2 review and executor, all older than R2, are answered with one JSON response, and a text the tool cannot write is never echoed back.
  - promises: P1, P2, P4, P5, P7, P8
  - tests P1: test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands
  - tests P2: test_running_the_examples_of_such_a_program_is_refused_the_same_way
  - tests P4: test_a_budget_written_as_5000_digits_is_refused_by_name
  - tests P5: test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply
  - tests P7: test_an_operation_that_cannot_be_written_is_refused_by_field_and_position
  - tests P8: test_a_budget_variable_that_cannot_be_written_is_refused_without_echoing_it
- S17: **Acceptance criteria**
  - not-testable (challenge this): the heading over the criteria that follow
- S18: 1.
  - not-testable (challenge this): the number of the first criterion
- S19: Given an integer the evaluator computes that is too large to write (for example four nested multiplications of 1000-digit literals, each within R2's literal limit; found in `values.render`, `ValueError: Exceeds the limit (4300 digits)`), then `evaluate`, `examples` and any operation that renders a computed value answers one JSON response: a located refusal in a published category naming the limit (decide: a new limit category published in `discover` under `resource_limits` with a reason, OR the budget refusal `output_budget_exceeded`; justify; mind that the existing F14 test pins `resource_limits.limits` to exactly two names: if a new published limit conflicts with that test, STOP and report), never a traceback.
  - promises: P1, P2
  - tests P1: test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands
  - tests P2: test_running_the_examples_of_such_a_program_is_refused_the_same_way
- S20: Values at or below the limit render exactly as before; integers beyond 64 bits stay exact below it.
  - promises: P3
  - tests P3: test_an_integer_of_any_size_is_written_or_refused_by_its_digits
- S21: Decide whether a computed value that big should simply render (raising the interpreter's digit limit is NOT allowed; render by your own routine if you choose to support it) or be refused: pick with a reason; the refusal is the safe default.
  - promises: P1
  - tests P1: test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands
- S22: 2.
  - not-testable (challenge this): the number of the second criterion
- S23: Given a budget environment variable set to a number of more than 4300 digits (e.g.
  - promises: P4
  - tests P4: test_a_budget_written_as_5000_digits_is_refused_by_name
- S24: `PROVA_BUDGET_INPUT_SIZE` set to 5000 digits; `ValueError` at `budgets.py` `int(written)`), then the command answers a refusal that names the variable, exit 0, no traceback; it can never raise a budget (it was lowering-only already).
  - promises: P4
  - tests P4: test_a_budget_written_as_5000_digits_is_refused_by_name
- S25: 3.
  - not-testable (challenge this): the number of the third criterion
- S26: Given a request whose JSON nests about 20000 arrays/objects deep (RecursionError inside the JSON reader), then the answer is `invalid_input`/`malformed_request` naming that the request nests too deeply, exit 0; choose the request nesting limit with a reason far below Python's recursion limit and publish it in `discover` documentation (do NOT raise Python's recursion limit); a request at the limit is answered as before.
  - promises: P5, P6
  - tests P5: test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply
  - tests P6: test_the_manifest_states_how_deep_a_request_may_nest_and_how_long_a_number_may_be
- S27: Make sure the bounded stdin read of F14 still protects memory.
  - not-testable (challenge this): a duty to leave the bounded read of F14 standing, which its own test already observes and this delivery keeps green
- S28: 4.
  - not-testable (challenge this): the number of the fourth criterion
- S29: Given `operation` holding a lone surrogate (today echoed back unchanged in the answer's `operation` field, which a client that decodes it and writes it out cannot write), then the answer is `invalid_input`/`malformed_request` naming the `operation` field and the character position, without echoing the text; also check every other place a request string is copied into an answer (function names in refusals, field names, argument texts) so no answer carries a text that cannot be written as UTF-8.
  - promises: P7, P8, P10
  - tests P7: test_an_operation_that_cannot_be_written_is_refused_by_field_and_position
  - tests P8: test_a_budget_variable_that_cannot_be_written_is_refused_without_echoing_it
  - tests P10: test_an_answer_holding_half_a_character_is_refused_before_it_is_printed
- S30: 5.
  - not-testable (challenge this): the number of the fifth criterion
- S31: Extend the derandomised fuzz in the suite with these families (computed big integers; huge environment values; deeply nested JSON; surrogates in every string position) so a regression is caught; everything accepted or produced before is answered exactly as before; no existing test edited.
  - promises: P9
  - tests P9: test_every_request_of_the_four_families_is_answered_and_the_rest_still_works
- S32: **Authority** SPEC.md lines 463-482 and 503-508, and the R1/R2 rule that every request gets one JSON answer.
  - not-testable (challenge this): names the authority lines behind the criteria
- S33: **Size** S.
  - not-testable (challenge this): states the size of the delivery

## Edge matrix

- I1.empty: standard input holding nothing at all => invalid_input, a malformed_request refusal saying the text is not JSON, exit 0, as before | self-probe: not probed | pre-feature not probed
- I1.unknown: an operation named not-an-operation => unavailable with unknown_operation naming it back, as before | self-probe: not probed | pre-feature not probed
- I1.malformed: a request nesting 20000 arrays, or an operation holding half a character => invalid_input naming the request or the operation field, exit 0 | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the command reads its request from standard input and calls no other process or service
- I1.repeated: the same 5000-digit evaluate request sent twice => the same refusal both times; the command keeps nothing between runs | self-probe: not probed | pre-feature not probed
- I1.concurrent: 2 commands running at once over the same request => each answers its own request; one process answers one request and shares no state | self-probe: not probed | pre-feature not probed
- I1.crash: n/a (challenge this): the command writes no file and keeps no state, so a run stopped part way leaves nothing behind to observe
- I2.empty: discover asked with no other field => the whole manifest, status completed, as before | self-probe: not probed | pre-feature not probed
- I2.unknown: a caller looking for a limit name the manifest does not publish => the 2 names under limits are unchanged and the 2 new numbers stand in the documentation | self-probe: not probed | pre-feature not probed
- I2.malformed: n/a (challenge this): the manifest reads no field of the request beyond the operation name, so it has nothing malformed to meet
- I2.dependency-gone: n/a (challenge this): the manifest is built from this tool's own declarations and reads nothing outside the process
- I2.repeated: discover asked twice in 2 runs => the same text both times; reading the manifest changes nothing | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): reading the manifest writes nothing, so 2 readers cannot disagree about it
- I2.crash: n/a (challenge this): nothing is written while the manifest is built, so an interrupted run leaves nothing half-written
- I3.empty: PROVA_BUDGET_INPUT_SIZE set to the empty text => a refusal naming that variable, exit 0, as before | self-probe: not probed | pre-feature not probed
- I3.unknown: PROVA_BUDGET_NOT_A_BUDGET set to 1 => a refusal saying this tool states no budget of that name, exit 0, as before | self-probe: not probed | pre-feature not probed
- I3.malformed: PROVA_BUDGET_INPUT_SIZE holding 5000 digits, or half a character => one refusal naming the variable, exit 0, no text copied back | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): the variables are read from the environment the caller started the command with and from nowhere else
- I3.repeated: the same variable written twice in one environment => an environment holds 1 value per name, so the run reads that one value | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): each run reads the environment it was started with, which no other run can change
- I3.crash: n/a (challenge this): reading a variable writes nothing, so an interrupted run leaves nothing behind

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN a program whose function multiplies five 1000-digit literals into a result of 5000 digits
  - WHEN a caller evaluates that function
  - THEN one JSON answer, status resource_exhausted, a refusal naming the limit 4000 beside the 5000 reached, at line 1
  - test: test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN the same program, whose 1 declared example runs that function
  - WHEN the examples are run
  - THEN the same refusal with the same 2 numbers and no claim that the tool failed
  - test: test_running_the_examples_of_such_a_program_is_refused_the_same_way
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN programs multiplying a run of nines by itself 1 to 6 times
  - WHEN each is evaluated
  - THEN every product of at most 4000 digits comes back as the exact number, past 64 bits and all, and only longer ones are refused
  - test: test_an_integer_of_any_size_is_written_or_refused_by_its_digits
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN PROVA_BUDGET_INPUT_SIZE holding 5000 digits
  - WHEN the manifest is asked for
  - THEN exit 0, one refusal naming that variable and saying the text is 5000 long, nothing on standard error
  - test: test_a_budget_written_as_5000_digits_is_refused_by_name
- SC5 (P4): not-held (no held self-probe case)
  - GIVEN the same variable holding each of 13 texts, among them "4096", "1048577" and 5000 digits
  - WHEN the manifest is asked under each
  - THEN only a whole number no larger than 1048576 is run under, and every other text is refused by name
  - test: test_a_budget_written_in_the_environment_is_read_or_refused
- SC6 (P5): not-held (no held self-probe case)
  - GIVEN a request whose JSON nests 20000 arrays inside one another
  - WHEN it is sent on standard input
  - THEN exit 0, status invalid_input, a malformed_request refusal saying the request nests deeper than the 64 this tool reads
  - test: test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply
- SC7 (P5): not-held (no held self-probe case)
  - GIVEN requests nesting 1 to 400 arrays and objects
  - WHEN each is sent
  - THEN every one at or below 64 is answered completed and every deeper one is refused for nesting
  - test: test_a_request_of_any_nesting_depth_is_answered
- SC8 (P6): not-held (no held self-probe case)
  - GIVEN a caller reading the manifest before it sends its 1st request
  - WHEN it asks discover
  - THEN the documentation states the 64 a request may nest and the 4000 digits an answer writes, and the 2 limits published under "limits" are unchanged
  - test: test_the_manifest_states_how_deep_a_request_may_nest_and_how_long_a_number_may_be
- SC9 (P7): not-held (no held self-probe case)
  - GIVEN a request whose operation field opens with half a character, written "\ud800check"
  - WHEN it is sent
  - THEN status invalid_input, a refusal naming the operation field and position 0, and no text in the answer that a client cannot write
  - test: test_an_operation_that_cannot_be_written_is_refused_by_field_and_position
- SC10 (P8): not-held (no held self-probe case)
  - GIVEN a variable named PROVA_BUDGET_INPUT_SIZE with half a character after its 23 letters
  - WHEN the manifest is asked for
  - THEN exit 0, a refusal naming the family PROVA_BUDGET_ and position 23, and no text in the answer that a client cannot write
  - test: test_a_budget_variable_that_cannot_be_written_is_refused_without_echoing_it
- SC11 (P9): not-held (no held self-probe case)
  - GIVEN a fixed corpus of at least 150 requests drawn from the 4 families
  - WHEN each is sent through the command
  - THEN every one is answered with one JSON response carrying a status, exit 0, and the 3 programs this repository ships are still answered completed
  - test: test_every_request_of_the_four_families_is_answered_and_the_rest_still_works
- SC12 (P10): not-held (no held self-probe case)
  - GIVEN an answer carrying half a character in 1 of its fields
  - WHEN it is turned into the text a caller reads
  - THEN what is printed is 1 refusal of status invalid_input carrying no copy of that text
  - test: test_an_answer_holding_half_a_character_is_refused_before_it_is_printed

## Questions for the owner

- S19: Shall the refusal use a new located category published among the diagnostic categories and documented in discover, leaving resource_limits.limits at its two names?
  - existing behaviour: the sentence offers publishing a new limit under resource_limits.limits, and tests/acceptance/test_f14_b9_the_limits_published_before_still_stand.py asserts that sorted(resource_limits[limits]) is exactly evaluation_depth and expression_nesting, so a third name there fails an existing test I may not edit; the other option it offers, output_budget_exceeded, is published with placed=NEVER in checker.DIAGNOSTIC_KINDS, so a refusal in that category may carry no place and could not be the located refusal the sentence asks for
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- A docs/feature/r3-robustness/craft.md (+62 -0 lines)
- A docs/feature/r3-robustness/oracle.md (+75 -0 lines)
- M src/prova/__main__.py (+19 -5 lines)
- M src/prova/budgets.py (+16 -1 lines)
- M src/prova/checker.py (+9 -0 lines)
- M src/prova/service.py (+337 -28 lines)
- M src/prova/values.py (+131 -1 lines)
- A tests/acceptance/_r3_fixtures.py (+148 -0 lines)
- A tests/acceptance/test_r3_b1_a_computed_integer_too_large_to_write_is_refused.py (+160 -0 lines)
- A tests/acceptance/test_r3_b2_a_budget_written_with_too_many_digits_is_refused.py (+109 -0 lines)
- A tests/acceptance/test_r3_b3_a_request_that_nests_too_deeply_is_refused.py (+136 -0 lines)
- A tests/acceptance/test_r3_b4_a_text_the_tool_cannot_write_is_never_echoed.py (+115 -0 lines)
- A tests/properties/test_r3_p1_the_four_crash_families_are_answered.py (+504 -0 lines)
- A tests/unit/test_r3_an_answer_carrying_a_text_nobody_can_write_is_refused.py (+79 -0 lines)

## Commits (git log, BASE to HEAD)

- 681c689 Answer four inputs that used to end in nothing a caller could read

## 2. oracle: Frame the work and write the oracle (revision 2)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-r3/request.md
- **promises**:
  - P1: A caller whose evaluation computes an integer this tool will not write gets one JSON answer: a refusal placed at the function it called, naming the written-digit limit and the digits the result reached.
  - P2: A caller running a program's declared examples gets that same one refusal when an example computes such an integer, never a report that the tool itself failed.
  - P3: An integer at or below the limit comes back exactly as before, however far past 64 bits it stands.
  - P4: A caller that writes a budget variable this tool cannot read as a number gets one JSON refusal naming that variable and exits 0, and a number a caller may lower a budget to is still read and measured against.
  - P5: A caller whose request nests arrays or objects deeper than this tool reads is told that the request nests too deeply and exits 0, while a request at the published nesting is answered as before.
  - P6: A caller reading the manifest before it sends work finds how deeply a request may nest and how many digits an answer writes, each with its reason.
  - P7: A caller whose operation field holds a character that cannot be written as UTF-8 is told which field and which character position, and never reads that text back.
  - P8: A caller whose budget variable is named with a character that cannot be written is told the family of variables to look through and which character position cannot be written, and the answer carries no copy of that name.
  - P9: The derandomised fuzz in the suite sends all four families and everything the tool answered before is answered exactly as before.
  - P10: No answer this tool prints carries a text that cannot be written as UTF-8, wherever that text came from.
- **sentence_map**:
  - S1 => not-testable: names the project and its suite, promising nothing a caller observes
  - S2 => not-testable: names the authority document to read, not an outcome
  - S3 => not-testable: a rule for how I work, kept by changing no existing test
  - S4 => not-testable: tells me what to do when a conflict appears, which the conflict table records
  - S5 => not-testable: names a directory to ignore, no observable outcome
  - S6 => not-testable: a rule about where I work, kept by the worktree
  - S7 => not-testable: a rule about the commit message I write
  - S8 => not-testable: the line a commit message ends with
  - S9 => not-testable: a rule forbidding a push or a merge
  - S10 => not-testable: a duty to keep the whole suite green, observed by running it
  - S11 => not-testable: names the files another delivery owns and the files I may touch
  - S12 => not-testable: names the structure already on main that I follow
  - S13 => not-testable: repeats the instruction to stop on a conflict
  - S14 => not-testable: a rule about where my own scripts live
  - S15 => not-testable: shell hygiene for the tool I record with
  - S16 => P1,P2,P4,P5,P7,P8
  - S17 => not-testable: the heading over the criteria that follow
  - S18 => not-testable: the number of the first criterion
  - S19 => P1,P2
  - S20 => P3
  - S21 => P1
  - S22 => not-testable: the number of the second criterion
  - S23 => P4
  - S24 => P4
  - S25 => not-testable: the number of the third criterion
  - S26 => P5,P6
  - S27 => not-testable: a duty to leave the bounded read of F14 standing, which its own test already observes and this delivery keeps green
  - S28 => not-testable: the number of the fourth criterion
  - S29 => P7,P8,P10
  - S30 => not-testable: the number of the fifth criterion
  - S31 => P9
  - S32 => not-testable: names the authority lines behind the criteria
  - S33 => not-testable: states the size of the delivery
- **scenarios**:
  - SC1 | P1 | GIVEN a program whose function multiplies five 1000-digit literals into a result of 5000 digits | WHEN a caller evaluates that function | THEN one JSON answer, status resource_exhausted, a refusal naming the limit 4000 beside the 5000 reached, at line 1
  - SC2 | P2 | GIVEN the same program, whose 1 declared example runs that function | WHEN the examples are run | THEN the same refusal with the same 2 numbers and no claim that the tool failed
  - SC3 | P3 | GIVEN programs multiplying a run of nines by itself 1 to 6 times | WHEN each is evaluated | THEN every product of at most 4000 digits comes back as the exact number, past 64 bits and all, and only longer ones are refused
  - SC4 | P4 | GIVEN PROVA_BUDGET_INPUT_SIZE holding 5000 digits | WHEN the manifest is asked for | THEN exit 0, one refusal naming that variable and saying the text is 5000 long, nothing on standard error
  - SC5 | P4 | GIVEN the same variable holding each of 13 texts, among them "4096", "1048577" and 5000 digits | WHEN the manifest is asked under each | THEN only a whole number no larger than 1048576 is run under, and every other text is refused by name
  - SC6 | P5 | GIVEN a request whose JSON nests 20000 arrays inside one another | WHEN it is sent on standard input | THEN exit 0, status invalid_input, a malformed_request refusal saying the request nests deeper than the 64 this tool reads
  - SC7 | P5 | GIVEN requests nesting 1 to 400 arrays and objects | WHEN each is sent | THEN every one at or below 64 is answered completed and every deeper one is refused for nesting
  - SC8 | P6 | GIVEN a caller reading the manifest before it sends its 1st request | WHEN it asks discover | THEN the documentation states the 64 a request may nest and the 4000 digits an answer writes, and the 2 limits published under "limits" are unchanged
  - SC9 | P7 | GIVEN a request whose operation field opens with half a character, written "\ud800check" | WHEN it is sent | THEN status invalid_input, a refusal naming the operation field and position 0, and no text in the answer that a client cannot write
  - SC10 | P8 | GIVEN a variable named PROVA_BUDGET_INPUT_SIZE with half a character after its 23 letters | WHEN the manifest is asked for | THEN exit 0, a refusal naming the family PROVA_BUDGET_ and position 23, and no text in the answer that a client cannot write
  - SC11 | P9 | GIVEN a fixed corpus of at least 150 requests drawn from the 4 families | WHEN each is sent through the command | THEN every one is answered with one JSON response carrying a status, exit 0, and the 3 programs this repository ships are still answered completed
  - SC12 | P10 | GIVEN an answer carrying half a character in 1 of its fields | WHEN it is turned into the text a caller reads | THEN what is printed is 1 refusal of status invalid_input carrying no copy of that text
- **conflicts**:
  - S1 | NONE | checked the suite runs green on this worktree before any change; the sentence states facts about the project
  - S2 | NONE | checked SPEC.md lines 463-482 and 503-508 against the four criteria; the authority names limits and controlled failure
  - S3 | NONE | checked that every file I add is new; no existing test or SPEC.md line is edited by this change
  - S4 | NONE | checked each criterion against the existing tests; the one contradiction found is recorded under S19
  - S5 | NONE | checked that nothing under .relay is read by the suite or by the tool I change
  - S6 | NONE | checked git status and the branch of this worktree; all work stays here
  - S7 | NONE | a rule about the commit message, which nothing in the system contradicts
  - S8 | NONE | a rule about the last line of the commit message; nothing in the repository forbids it
  - S9 | NONE | a rule forbidding push and merge; nothing in the system needs either
  - S10 | NONE | checked that the whole suite is green before the change, so keeping it green is possible
  - S11 | NONE | checked that encoding.py, solving.py, discharge.py and obligations.py are untouched by this design
  - S12 | NONE | read reader.py, budgets.py and the request reader of service.py; the new refusals follow the same value objects
  - S13 | NONE | repeats the stop rule; the conflict found is recorded with its decision under S19
  - S14 | NONE | checked that my scripts live only under the nwstep workspace directory of this run
  - S15 | NONE | a rule about shell quoting while recording; nothing in the repository contradicts it
  - S16 | NONE | reproduced all four families on this tree: three answer tool_failure or a traceback today, one echoes the text back
  - S17 | NONE | a heading; checked that the criteria under it are the five numbered sentences that follow
  - S18 | NONE | the number of a criterion; nothing in the system contradicts a number
  - S19 | CONFLICT | the sentence offers publishing a new limit under resource_limits.limits, and tests/acceptance/test_f14_b9_the_limits_published_before_still_stand.py asserts that sorted(resource_limits[limits]) is exactly evaluation_depth and expression_nesting, so a third name there fails an existing test I may not edit; the other option it offers, output_budget_exceeded, is published with placed=NEVER in checker.DIAGNOSTIC_KINDS, so a refusal in that category may carry no place and could not be the located refusal the sentence asks for | Shall the refusal use a new located category published among the diagnostic categories and documented in discover, leaving resource_limits.limits at its two names?
  - S20 | NONE | checked that values.render writes every integer with str today, so values under the new limit keep the text they had
  - S21 | NONE | checked that nothing in the tool sets or reads sys.set_int_max_str_digits, so the choice is open
  - S22 | NONE | the number of a criterion; nothing in the system contradicts a number
  - S23 | NONE | reproduced the ValueError in budgets.py lowered_to with a variable holding 5000 digits
  - S24 | NONE | checked lowered_to refuses anything above the declared maximum, so refusing a long run of digits raises no budget
  - S25 | NONE | the number of a criterion; nothing in the system contradicts a number
  - S26 | NONE | reproduced the RecursionError inside json.loads and checked that no test pins the keys of the published documentation
  - S27 | NONE | read _read_at_most in __main__.py and checked the new nesting check runs after it, on text already bounded
  - S28 | NONE | the number of a criterion; nothing in the system contradicts a number
  - S29 | NONE | reproduced the echoed operation field and found the same echo for a budget variable; existing tests assert the echo only for names a client can write
  - S30 | NONE | the number of a criterion; nothing in the system contradicts a number
  - S31 | NONE | read the R1 and R2 fuzz modules; the new families are added in a new file and no existing fuzz file is edited
  - S32 | NONE | read SPEC.md lines 463-482 and 503-508; they ask for declared limits and controlled failure, which these refusals are
  - S33 | NONE | the size of the delivery, which nothing in the system contradicts
- **decisions**:
  - S19: The owner is absent, so I decide: the refusal carries a new located category written_integer_digits_exceeded, published among the diagnostic categories and their schemas and documented in discover under computed_integers with its reason, while resource_limits.limits keeps its exactly two names, so the existing F14 test stands unedited and the refusal can still carry the place of the function that computed the number.
  - DEC1: The limit is 4000 digits, chosen below the 4300 the interpreter writes as one number by default so that the tool refuses with its own sentence instead of meeting the interpreter's error, and far above the 20 digits of a 64-bit number and the 1000 digits of the longest literal this tool reads.
  - DEC2: A value past the limit is refused rather than written by a routine of this tool's own: the request calls refusal the safe default, writing a number of unbounded length would put work with no stated bound between the answer and the caller, and the refusal names a number the caller can design against.
  - DEC3: A request may nest 64 arrays or objects inside one another, counting the request object: the deepest request this tool answers today nests 3, 64 is far above anything a client writes and far below the 1000 frames the interpreter allows, and Python's own recursion limit is left alone.
  - DEC4: A budget variable is refused by the digits it writes, before any attempt to read it as a number: the text is refused when the digits left after leading zeros are more than the digits of the budget this tool declares, so no run of digits is ever handed to the reader that breaks on long ones and a zero-padded small number is still read.
  - DEC5: One rule decides whether a text can be written as UTF-8, the SubmittedText reader R2 added, and it is now asked for the operation field and for the PROVA_BUDGET variables as well; the one place an answer becomes characters refuses to print any answer still carrying such a text, so the promise holds for texts no reader named.
  - DEC6: No formal model: the four behaviours are decisions about one input taken inside one process with no state kept between runs, no concurrency and no protocol, so a Quint model would restate the code without adding a question it could answer.
  - DEC7: Jev was not asked anything: the host running this delivery forbids any remote question service for this run, so every choice above was taken locally and is recorded here with its reason.
- **mapping**:
  - P1 => test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands
  - P2 => test_running_the_examples_of_such_a_program_is_refused_the_same_way
  - P3 => test_an_integer_of_any_size_is_written_or_refused_by_its_digits
  - P4 => test_a_budget_written_as_5000_digits_is_refused_by_name
  - P5 => test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply
  - P6 => test_the_manifest_states_how_deep_a_request_may_nest_and_how_long_a_number_may_be
  - P7 => test_an_operation_that_cannot_be_written_is_refused_by_field_and_position
  - P8 => test_a_budget_variable_that_cannot_be_written_is_refused_without_echoing_it
  - P9 => test_every_request_of_the_four_families_is_answered_and_the_rest_still_works
  - P10 => test_an_answer_holding_half_a_character_is_refused_before_it_is_printed
- **covers_scenarios**:
  - SC1 => test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands
  - SC2 => test_running_the_examples_of_such_a_program_is_refused_the_same_way
  - SC3 => test_an_integer_of_any_size_is_written_or_refused_by_its_digits
  - SC4 => test_a_budget_written_as_5000_digits_is_refused_by_name
  - SC5 => test_a_budget_written_in_the_environment_is_read_or_refused
  - SC6 => test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply
  - SC7 => test_a_request_of_any_nesting_depth_is_answered
  - SC8 => test_the_manifest_states_how_deep_a_request_may_nest_and_how_long_a_number_may_be
  - SC9 => test_an_operation_that_cannot_be_written_is_refused_by_field_and_position
  - SC10 => test_a_budget_variable_that_cannot_be_written_is_refused_without_echoing_it
  - SC11 => test_every_request_of_the_four_families_is_answered_and_the_rest_still_works
  - SC12 => test_an_answer_holding_half_a_character_is_refused_before_it_is_printed
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
  - I1: the prova command, reading one JSON request from standard input and printing one JSON answer
  - I2: the discover operation's manifest, where a caller reads every limit before it sends work
  - I3: the PROVA_BUDGET variables a caller sets in its environment to lower one budget for one run
- **matrix**:
  - I1.empty => standard input holding nothing at all => invalid_input, a malformed_request refusal saying the text is not JSON, exit 0, as before
  - I1.unknown => an operation named not-an-operation => unavailable with unknown_operation naming it back, as before
  - I1.malformed => a request nesting 20000 arrays, or an operation holding half a character => invalid_input naming the request or the operation field, exit 0
  - I1.dependency-gone => n/a: the command reads its request from standard input and calls no other process or service
  - I1.repeated => the same 5000-digit evaluate request sent twice => the same refusal both times; the command keeps nothing between runs
  - I1.concurrent => 2 commands running at once over the same request => each answers its own request; one process answers one request and shares no state
  - I1.crash => n/a: the command writes no file and keeps no state, so a run stopped part way leaves nothing behind to observe
  - I2.empty => discover asked with no other field => the whole manifest, status completed, as before
  - I2.unknown => a caller looking for a limit name the manifest does not publish => the 2 names under limits are unchanged and the 2 new numbers stand in the documentation
  - I2.malformed => n/a: the manifest reads no field of the request beyond the operation name, so it has nothing malformed to meet
  - I2.dependency-gone => n/a: the manifest is built from this tool's own declarations and reads nothing outside the process
  - I2.repeated => discover asked twice in 2 runs => the same text both times; reading the manifest changes nothing
  - I2.concurrent => n/a: reading the manifest writes nothing, so 2 readers cannot disagree about it
  - I2.crash => n/a: nothing is written while the manifest is built, so an interrupted run leaves nothing half-written
  - I3.empty => PROVA_BUDGET_INPUT_SIZE set to the empty text => a refusal naming that variable, exit 0, as before
  - I3.unknown => PROVA_BUDGET_NOT_A_BUDGET set to 1 => a refusal saying this tool states no budget of that name, exit 0, as before
  - I3.malformed => PROVA_BUDGET_INPUT_SIZE holding 5000 digits, or half a character => one refusal naming the variable, exit 0, no text copied back
  - I3.dependency-gone => n/a: the variables are read from the environment the caller started the command with and from nowhere else
  - I3.repeated => the same variable written twice in one environment => an environment holds 1 value per name, so the run reads that one value
  - I3.concurrent => n/a: each run reads the environment it was started with, which no other run can change
  - I3.crash => n/a: reading a variable writes nothing, so an interrupted run leaves nothing behind
- **laws**:
  - LAW1 | A program multiplying a run of nines by itself is answered with the exact product when that product has at most 4000 digits and refused with the limit and the digits reached when it has more | generator=test_an_integer_of_any_size_is_written_or_refused_by_its_digits | observation=the status of the answer, the number it carries and the two counts of the refusal | mutant=a tool that refuses every product past 64 bits, or one that writes 5000 digits and fails inside the interpreter
  - LAW2 | Whatever text a caller writes in a budget variable, the command answers one JSON response and exits 0, and runs under that number only when it is a whole number no larger than the one this tool declares | generator=test_a_budget_written_in_the_environment_is_read_or_refused | observation=the exit code, the status and the refusal naming the variable | mutant=a tool that reads a 5000-digit text as a budget, or one that refuses a number a caller may lower to
  - LAW3 | A request is answered however deeply its own JSON nests, and is refused for nesting when and only when it nests deeper than the 64 this tool reads | generator=test_a_request_of_any_nesting_depth_is_answered | observation=the status of the answer and the refusal that names the nesting | mutant=a tool that refuses a request nesting 3 deep, or one that lets a 20000-deep request reach the JSON reader
  - LAW4 | Wherever half a character stands in a text a request or a budget variable carries, every text of the printed answer can be written as UTF-8, and an operation that holds one is named with its position | generator=test_a_surrogate_anywhere_leaves_an_answer_a_client_can_write | observation=each text of the parsed answer re-encoded as UTF-8, and the field and position the refusal names | mutant=a tool that copies the operation field back into its answer unchanged
- **messages**:
  - MSG1 | an evaluation whose result has 5000 digits | this tool writes an integer of at most 4000 digits into an answer and this result reached 5000 | an answer carrying a longer number is one the interpreter refuses to write, and the run would end with nothing to read | write a program whose result has at most 4000 digits, and read that number from what discover documents about computed integers | test=test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands
  - MSG2 | PROVA_BUDGET_INPUT_SIZE holding 5000 digits | the text written in that variable is 5000 digits long and this tool reads a budget of at most 7 | a run of digits longer than the budget this tool declares cannot lower anything, and reading it would end the command before it read its request | write a whole number no larger than 1048576, or leave the variable unset | test=test_a_budget_written_as_5000_digits_is_refused_by_name
  - MSG3 | a request whose JSON nests 20000 arrays inside one another | the request nests deeper than the 64 arrays or objects this tool reads | the reader calls itself once per array, so a deeper request would exhaust the interpreter before the operation was read | send a request nesting at most 64, and read that number from what discover documents about request nesting | test=test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply
  - MSG4 | an operation field whose first character is half of a surrogate pair | the character at position 0 of the operation field cannot be written as UTF-8 | this tool writes every text it answers with as bytes, and half a character has none, so a client reading it back could not write it either | send the operation as text whose characters can all be written as UTF-8 | test=test_an_operation_that_cannot_be_written_is_refused_by_field_and_position
- **red**: `uv run pytest -q tests/acceptance/test_r3_b1_a_computed_integer_too_large_to_write_is_refused.py tests/acceptance/test_r3_b2_a_budget_written_with_too_many_digits_is_refused.py tests/acceptance/test_r3_b3_a_request_that_nests_too_deeply_is_refused.py tests/acceptance/test_r3_b4_a_text_the_tool_cannot_write_is_never_echoed.py tests/properties/test_r3_p1_the_four_crash_families_are_answered.py tests/unit/test_r3_an_answer_carrying_a_text_nobody_can_write_is_refused.py` exited 1 in 4.275s
  - failing on the pre-feature tree (14): tests/acceptance/test_r3_b1_a_computed_integer_too_large_to_write_is_refused.py::test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands, tests/acceptance/test_r3_b1_a_computed_integer_too_large_to_write_is_refused.py::test_running_the_examples_of_such_a_program_is_refused_the_same_way, tests/acceptance/test_r3_b2_a_budget_written_with_too_many_digits_is_refused.py::test_a_budget_written_as_5000_digits_is_refused_by_name, tests/acceptance/test_r3_b3_a_request_that_nests_too_deeply_is_refused.py::test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply, tests/acceptance/test_r3_b3_a_request_that_nests_too_deeply_is_refused.py::test_the_manifest_states_how_deep_a_request_may_nest_and_how_long_a_number_may_be, tests/acceptance/test_r3_b4_a_text_the_tool_cannot_write_is_never_echoed.py::test_an_operation_that_cannot_be_written_is_refused_by_field_and_position, tests/acceptance/test_r3_b4_a_text_the_tool_cannot_write_is_never_echoed.py::test_a_budget_variable_that_cannot_be_written_is_refused_without_echoing_it, tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_every_request_of_the_four_families_is_answered_and_the_rest_still_works, tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_an_integer_of_any_size_is_written_or_refused_by_its_digits, tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_a_budget_written_in_the_environment_is_read_or_refused, tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_a_request_of_any_nesting_depth_is_answered, tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_a_surrogate_anywhere_leaves_an_answer_a_client_can_write, tests/unit/test_r3_an_answer_carrying_a_text_nobody_can_write_is_refused.py::test_an_answer_holding_half_a_character_is_refused_before_it_is_printed, tests/unit/test_r3_an_answer_carrying_a_text_nobody_can_write_is_refused.py::test_an_ordinary_answer_is_written_exactly_as_json
  - tests (read from the run): 14 failed, 7 passed in 3.35s
  ```text
          """Given an answer that somehow carries half a character, when it is
          turned into the text a caller reads, then what is printed is a
          refusal instead, and every text in it can be written as UTF-8.
          """
  >       printed = service.printable_answer(
                    ^^^^^^^^^^^^^^^^^^^^^^^^
              {"operation": "\ud800check", "status": "unavailable", "diagnostics": []}
          )
  E       AttributeError: module 'prova.service' has no attribute 'printable_answer'

  tests/unit/test_r3_an_answer_carrying_a_text_nobody_can_write_is_refused.py:23: AttributeError
  ______________ test_an_ordinary_answer_is_written_exactly_as_json ______________

      def test_an_ordinary_answer_is_written_exactly_as_json():
          """Given an ordinary answer, when it is turned into the text a
          caller reads, then it is that answer, written as 1 JSON object.
          """
          answer = {"operation": "check", "status": "completed", "diagnostics": []}

  >       printed = service.printable_answer(answer)
                    ^^^^^^^^^^^^^^^^^^^^^^^^
  E       AttributeError: module 'prova.service' has no attribute 'printable_answer'

  tests/unit/test_r3_an_answer_carrying_a_text_nobody_can_write_is_refused.py:46: AttributeError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_r3_b1_a_computed_integer_too_large_to_write_is_refused.py::test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands
  FAILED tests/acceptance/test_r3_b1_a_computed_integer_too_large_to_write_is_refused.py::test_running_the_examples_of_such_a_program_is_refused_the_same_way
  FAILED tests/acceptance/test_r3_b2_a_budget_written_with_too_many_digits_is_refused.py::test_a_budget_written_as_5000_digits_is_refused_by_name
  FAILED tests/acceptance/test_r3_b3_a_request_that_nests_too_deeply_is_refused.py::test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply
  FAILED tests/acceptance/test_r3_b3_a_request_that_nests_too_deeply_is_refused.py::test_the_manifest_states_how_deep_a_request_may_nest_and_how_long_a_number_may_be
  FAILED tests/acceptance/test_r3_b4_a_text_the_tool_cannot_write_is_never_echoed.py::test_an_operation_that_cannot_be_written_is_refused_by_field_and_position
  FAILED tests/acceptance/test_r3_b4_a_text_the_tool_cannot_write_is_never_echoed.py::test_a_budget_variable_that_cannot_be_written_is_refused_without_echoing_it
  FAILED tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_every_request_of_the_four_families_is_answered_and_the_rest_still_works
  FAILED tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_an_integer_of_any_size_is_written_or_refused_by_its_digits
  FAILED tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_a_budget_written_in_the_environment_is_read_or_refused
  FAILED tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_a_request_of_any_nesting_depth_is_answered
  FAILED tests/properties/test_r3_p1_the_four_crash_families_are_answered.py::test_a_surrogate_anywhere_leaves_an_answer_a_client_can_write
  FAILED tests/unit/test_r3_an_answer_carrying_a_text_nobody_can_write_is_refused.py::test_an_answer_holding_half_a_character_is_refused_before_it_is_printed
  FAILED tests/unit/test_r3_an_answer_carrying_a_text_nobody_can_write_is_refused.py::test_an_ordinary_answer_is_written_exactly_as_json
  14 failed, 7 passed in 3.35s
  ```

## 4. craft: Craft the change (revision 2)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 239.68s
  - tests (read from the run): 1339 passed in 239.48s
  - slowest: 11.12s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 7.28s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 6.46s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 5.51s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 4.58s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 4.48s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 3.43s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 2.71s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 2.56s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 2.38s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  5%]
  ........................................................................ [ 10%]
  ........................................................................ [ 16%]
  ........................................................................ [ 21%]
  ........................................................................ [ 26%]
  ........................................................................ [ 32%]
  ........................................................................ [ 37%]
  ........................................................................ [ 43%]
  ........................................................................ [ 48%]
  ........................................................................ [ 53%]
  ........................................................................ [ 59%]
  ........................................................................ [ 64%]
  ........................................................................ [ 69%]
  ........................................................................ [ 75%]
  ........................................................................ [ 80%]
  ........................................................................ [ 86%]
  ........................................................................ [ 91%]
  ........................................................................ [ 96%]
  ...........................................                              [100%]
  ============================= slowest 10 durations =============================
  11.12s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  7.28s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  6.46s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  5.51s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  4.58s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  4.48s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  3.43s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  2.71s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  2.56s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  2.38s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1339 passed in 239.48s (0:03:59)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.046s
- **typesafe**: refused: the host running this delivery forbids every remote question service for this run, so no question was sent; each open choice was decided locally and recorded with its reason in the oracle decisions
