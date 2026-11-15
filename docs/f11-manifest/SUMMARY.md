# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1136 tests, all green on main).
  - not-testable (challenge this): names the project, its test command and the count of tests on main; a setting, not an outcome a test can observe
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority this work answers to; no observable behaviour of the tool
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a process promise about what this delivery may edit, kept by the diff and not by a test
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): a process promise to stop and report a conflict rather than edit a test
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): a process promise about a directory this delivery leaves alone
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a process promise about where the work happens
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a process promise about the trailer of the commit message
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the literal trailer line the commit message ends with
- S9: Do not push and do not merge.
  - not-testable (challenge this): a process promise not to push and not to merge
- S10: Keep the full suite green.
  - not-testable (challenge this): a process promise about the suite, kept by running it, not by a new test
- S11: Another delivery (F12, `parse` and its tree schema, syntax.py and the dispatch in service.py) runs in parallel in a different worktree.
  - not-testable (challenge this): names a parallel delivery whose files this work keeps clear of
- S12: F1 to F10, F13, F16, F2fix and R1 (robustness: request reader, nesting and evaluation limits, `malformed_request`, `resource_exhausted`) are on main; read how `service.py`, the table of diagnostic kinds in `checker.py` and the manifest are built now and follow that structure.
  - not-testable (challenge this): tells which features are already on main and asks this work to follow their structure
- S13: Keep your service.py edits small and local to ease the rebase.
  - not-testable (challenge this): a process promise about the size of the service.py diff, read from the diff
- S14: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): a process promise about where this run keeps its own scripts
- S15: Known tool rules: oracle laws must name @given property tests; design invariant witnesses must be a `class` or `def`; an independent_review resolution needs at least 20 characters; prefactor commits must come first in history; process promises go in not-testable sentences; the tool must never end in a traceback and every new request field read goes through the request reader.
  - not-testable (challenge this): rules of the recording tool, kept by the records, not by the product
- S16: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell hygiene for the recording tool and a clean worktree at the end
- S17: **Outcome.** `discover` is enough to use the tool: every operation, whether it is
  - promises: P1, P2, P3, P4, P5
  - tests P1: test_every_operation_category_the_profile_names_is_there_with_its_word
  - tests P1: test_the_word_a_category_carries_is_the_one_the_operation_answers_with
  - tests P2: test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  - tests P2: test_every_field_an_answer_carries_is_one_the_shape_publishes
  - tests P3: test_every_type_core_0_has_is_named_with_what_it_is
  - tests P3: test_every_operator_is_named_with_the_types_it_takes_and_answers
  - tests P4: test_an_operation_advertised_as_available_answers_a_matching_request
  - tests P4: test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
  - tests P5: test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own
  - tests P5: test_every_operation_is_either_in_a_category_or_marked_as_beyond_it
- S18: available, its request and response shape, the diagnostic schema, the profile
  - promises: P2
  - tests P2: test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  - tests P2: test_every_field_an_answer_carries_is_one_the_shape_publishes
- S19: coverage and the limits.
  - promises: P2
  - tests P2: test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  - tests P2: test_every_field_an_answer_carries_is_one_the_shape_publishes
- S20: **Acceptance criteria**
  - not-testable (challenge this): a heading introducing the acceptance criteria below it
- S21: 1.
  - not-testable (challenge this): the numeral that introduces the first acceptance criterion
- S22: Given `discover`, when it runs, then every operation named in SPEC.md's initial
  - promises: P1
  - tests P1: test_every_operation_category_the_profile_names_is_there_with_its_word
  - tests P1: test_the_word_a_category_carries_is_the_one_the_operation_answers_with
- S23: categories appears with available or unavailable.
  - promises: P1
  - tests P1: test_every_operation_category_the_profile_names_is_there_with_its_word
  - tests P1: test_the_word_a_category_carries_is_the_one_the_operation_answers_with
- S24: 2.
  - not-testable (challenge this): the numeral that introduces the second acceptance criterion
- S25: Given `discover`, then each available operation carries its request and its
  - promises: P2
  - tests P2: test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  - tests P2: test_every_field_an_answer_carries_is_one_the_shape_publishes
- S26: response schema.
  - promises: P2
  - tests P2: test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  - tests P2: test_every_field_an_answer_carries_is_one_the_shape_publishes
- S27: 3.
  - not-testable (challenge this): the numeral that introduces the third acceptance criterion
- S28: Given `discover`, then each builtin type and operator appears with its argument
  - promises: P3
  - tests P3: test_every_type_core_0_has_is_named_with_what_it_is
  - tests P3: test_every_operator_is_named_with_the_types_it_takes_and_answers
- S29: and result types.
  - promises: P3
  - tests P3: test_every_type_core_0_has_is_named_with_what_it_is
  - tests P3: test_every_operator_is_named_with_the_types_it_takes_and_answers
- S30: 4.
  - not-testable (challenge this): the numeral that introduces the fourth acceptance criterion
- S31: Given an operation advertised as available, when it is called with a request
  - promises: P4
  - tests P4: test_an_operation_advertised_as_available_answers_a_matching_request
  - tests P4: test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
- S32: matching the published schema, then it answers; when it is called with a request
  - promises: P4
  - tests P4: test_an_operation_advertised_as_available_answers_a_matching_request
  - tests P4: test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
- S33: that violates the schema, then it is refused as invalid input.
  - promises: P4
  - tests P4: test_an_operation_advertised_as_available_answers_a_matching_request
  - tests P4: test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
- S34: 5.
  - not-testable (challenge this): the numeral that introduces the fifth acceptance criterion
- S35: Given an operation the tool runs that SPEC.md does not name as a profile
  - promises: P5
  - tests P5: test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own
  - tests P5: test_every_operation_is_either_in_a_category_or_marked_as_beyond_it
- S36: operation, then the manifest says so rather than presenting it as profile
  - promises: P5
  - tests P5: test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own
  - tests P5: test_every_operation_is_either_in_a_category_or_marked_as_beyond_it
- S37: conformance.
  - promises: P5
  - tests P5: test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own
  - tests P5: test_every_operation_is_either_in_a_category_or_marked_as_beyond_it
- S38: **SPEC.md** lines 463-470, 476-478.
  - not-testable (challenge this): the lines of SPEC.md this feature answers to, a citation and not an outcome
- S39: **Dependencies** none.
  - not-testable (challenge this): states that this feature depends on no other feature
- S40: **Size** M.
  - not-testable (challenge this): the size of the delivery, which decides the steps and not the behaviour
- S41: **Touches** `src/prova/service.py`, tests, new schema fixtures.
  - not-testable (challenge this): names the files the work is expected to touch
- S42: **Why it is a real expectation** `docs/spec-trace.md` rows 8.2 and 8.3 are Partial;
  - not-testable (challenge this): the evidence that the expectation is real, read from a trace document
- S43: 3 of 7 categories exist and `evaluate` is not one of SPEC.md's named categories
  - not-testable (challenge this): the counts behind that evidence, about the state of the tool before this work
- S44: (see proposal P1).
  - not-testable (challenge this): a pointer to a proposal that holds the background of the gap

## Edge matrix

- I1.empty: a request carrying only {"operation": "discover"} and no other field => the whole manifest with status completed | self-probe: not probed | pre-feature not probed
- I1.unknown: a request asking for the category name {"operation": "discovery"} => status unavailable with the category unknown_operation | self-probe: not probed | pre-feature not probed
- I1.malformed: the text {"operation": "disc which stops partway => status invalid_input with the category malformed_request | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): discover reads no file, no network and no other process; it answers from the tool itself
- I1.repeated: two discover requests one after the other => the same manifest twice and nothing written anywhere | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): each request is one process reading its own standard input and sharing no state with another
- I1.crash: n/a (challenge this): the command keeps no file and no state, so a run stopped halfway leaves nothing behind
- I2.empty: check with "source": "" => status completed over a program declaring 0 functions | self-probe: not probed | pre-feature not probed
- I2.unknown: evaluate naming "function": "absent", which the program does not declare => status invalid_input with the category unknown_function | self-probe: not probed | pre-feature not probed
- I2.malformed: check with "source": 7 => status invalid_input with the category malformed_request naming the field source | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): these operations read the source out of the request itself and open nothing else
- I2.repeated: the same evaluate request sent twice => the same answer twice, with the same source revision | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): one request per process, no shared file and no lock to contend for
- I2.crash: n/a (challenge this): nothing is written, so a run stopped halfway leaves no half written answer anywhere

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the tool as it ships, with the 7 operation categories SPEC.md lines 467-468 name
  - WHEN an agent sends the request {"operation": "discover"}
  - THEN all 7 categories are there, each naming its operation and the word "available" or "unavailable", and asking for an operation marked "unavailable" answers "unavailable"
  - test: test_every_operation_category_the_profile_names_is_there_with_its_word
  - test: test_the_word_a_category_carries_is_the_one_the_operation_answers_with
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN the 5 operations the tool advertises as available, among them "check" and "evaluate"
  - WHEN an agent sends {"operation": "discover"} and then one request built only out of the published shape of each
  - THEN each of the 5 carries its request fields and its answer fields, and each of the 5 requests is answered "completed"
  - test: test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  - test: test_a_request_built_only_from_the_published_shape_is_answered
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN core-0 with 3 type names and 11 operators (SPEC.md lines 98 and 178-189)
  - WHEN an agent sends {"operation": "discover"}
  - THEN "+" carries the arguments ["Int", "Int"] and the result "Int", "not" carries ["Bool"] and "Bool", and "=" carries one name in both argument places with a sentence saying it stands for any core type
  - test: test_every_operator_is_named_with_the_types_it_takes_and_answers
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN "evaluate", advertised as available, whose published request shape names "function" a text
  - WHEN an agent sends {"operation": "evaluate", "source": "(defn twice ...)", "function": "twice", "arguments": ["3"]}
  - THEN the answer is "completed" and carries the value 6
  - test: test_an_operation_advertised_as_available_answers_a_matching_request
- SC5 (P4): not-held (no held self-probe case)
  - GIVEN the same published shape of "evaluate"
  - WHEN an agent sends the same request with "function": 7
  - THEN the answer is "invalid_input" and the refusal names the field "function"
  - test: test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
- SC6 (P5): not-held (no held self-probe case)
  - GIVEN "evaluate", which the tool answers and which SPEC.md names in none of its 7 categories
  - WHEN an agent sends {"operation": "discover"}
  - THEN "evaluate" is listed as beyond the profile with a reason, no category names it, and every 1 of the advertised operations is in exactly one of the two lists
  - test: test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own
  - test: test_every_operation_is_either_in_a_category_or_marked_as_beyond_it

## Questions for the owner

- S28: May the manifest publish the types and operators of core-0 under a name that avoids the word builtin, as language with types and operators inside it, keeping the existing no-claim test as it stands?
  - existing behaviour: tests/unit/test_service_discover.py::test_discover_makes_no_verification_proof_or_build_claim asserts that the lowercased JSON of the whole discover answer carries none of the words verified, proved, built and holds; the words builtin and builtins carry the letters of built, so publishing this part under that name turns that existing test red
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- A docs/f11-manifest/DECISIONS.md (+17 -0 lines)
- A docs/f11-manifest/SUMMARY.md (+502 -0 lines)
- A docs/f11-manifest/TRACE.md (+5 -0 lines)
- A docs/feature/f11/craft.md (+115 -0 lines)
- A docs/feature/f11/design.md (+101 -0 lines)
- A docs/feature/f11/oracle.md (+69 -0 lines)
- M src/prova/checker.py (+171 -76 lines)
- A src/prova/manifest.py (+469 -0 lines)
- M src/prova/service.py (+20 -8 lines)
- A tests/acceptance/_f11_manifest_fixtures.py (+163 -0 lines)
- A tests/acceptance/test_f11_b1_the_manifest_names_every_operation_category.py (+80 -0 lines)
- A tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py (+171 -0 lines)
- A tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py (+105 -0 lines)
- A tests/acceptance/test_f11_b4_a_request_that_breaks_the_published_shape_is_refused.py (+87 -0 lines)
- A tests/acceptance/test_f11_b5_an_operation_the_profile_does_not_name_says_so.py (+73 -0 lines)
- A tests/properties/test_f11_manifest_laws.py (+265 -0 lines)
- A tests/unit/test_manifest_catalogue.py (+56 -0 lines)

## Commits (git log, BASE to HEAD)

- 80d766b Let an operator say which types it takes and answers
- 9b5754c Say what an agent may call, and what it may write
- 22d34fb Write down what the manifest now says and what it cost
- 73a25ad Draw the same cases twice, and refuse a category claimed twice

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f11/request.md
- **promises**:
  - P1: An agent asking `discover` sees every operation category SPEC.md names, each with the operation that covers it and whether it is available or unavailable.
  - P2: An agent asking `discover` sees, for every operation it may call, the fields its request takes and the fields its answer carries, beside the diagnostic schema, the profile coverage and the resource limits it already carries.
  - P3: An agent asking `discover` sees every type core-0 has and every operator, with the types each operator takes and the type it answers.
  - P4: An operation advertised as available answers a request that matches its published shape, and refuses a request that carries a published field as another kind of value as invalid input, naming the field.
  - P5: An operation this tool answers that SPEC.md names in none of its operation categories is shown as the tool own extension, not as profile conformance.
- **sentence_map**:
  - S1 => not-testable: names the project, its test command and the count of tests on main; a setting, not an outcome a test can observe
  - S2 => not-testable: names SPEC.md as the authority this work answers to; no observable behaviour of the tool
  - S3 => not-testable: a process promise about what this delivery may edit, kept by the diff and not by a test
  - S4 => not-testable: a process promise to stop and report a conflict rather than edit a test
  - S5 => not-testable: a process promise about a directory this delivery leaves alone
  - S6 => not-testable: a process promise about where the work happens
  - S7 => not-testable: a process promise about the trailer of the commit message
  - S8 => not-testable: the literal trailer line the commit message ends with
  - S9 => not-testable: a process promise not to push and not to merge
  - S10 => not-testable: a process promise about the suite, kept by running it, not by a new test
  - S11 => not-testable: names a parallel delivery whose files this work keeps clear of
  - S12 => not-testable: tells which features are already on main and asks this work to follow their structure
  - S13 => not-testable: a process promise about the size of the service.py diff, read from the diff
  - S14 => not-testable: a process promise about where this run keeps its own scripts
  - S15 => not-testable: rules of the recording tool, kept by the records, not by the product
  - S16 => not-testable: shell hygiene for the recording tool and a clean worktree at the end
  - S17 => P1,P2,P3,P4,P5
  - S18 => P2
  - S19 => P2
  - S20 => not-testable: a heading introducing the acceptance criteria below it
  - S21 => not-testable: the numeral that introduces the first acceptance criterion
  - S22 => P1
  - S23 => P1
  - S24 => not-testable: the numeral that introduces the second acceptance criterion
  - S25 => P2
  - S26 => P2
  - S27 => not-testable: the numeral that introduces the third acceptance criterion
  - S28 => P3
  - S29 => P3
  - S30 => not-testable: the numeral that introduces the fourth acceptance criterion
  - S31 => P4
  - S32 => P4
  - S33 => P4
  - S34 => not-testable: the numeral that introduces the fifth acceptance criterion
  - S35 => P5
  - S36 => P5
  - S37 => P5
  - S38 => not-testable: the lines of SPEC.md this feature answers to, a citation and not an outcome
  - S39 => not-testable: states that this feature depends on no other feature
  - S40 => not-testable: the size of the delivery, which decides the steps and not the behaviour
  - S41 => not-testable: names the files the work is expected to touch
  - S42 => not-testable: the evidence that the expectation is real, read from a trace document
  - S43 => not-testable: the counts behind that evidence, about the state of the tool before this work
  - S44 => not-testable: a pointer to a proposal that holds the background of the gap
- **scenarios**:
  - SC1 | P1 | GIVEN the tool as it ships, with the 7 operation categories SPEC.md lines 467-468 name | WHEN an agent sends the request {"operation": "discover"} | THEN all 7 categories are there, each naming its operation and the word "available" or "unavailable", and asking for an operation marked "unavailable" answers "unavailable"
  - SC2 | P2 | GIVEN the 5 operations the tool advertises as available, among them "check" and "evaluate" | WHEN an agent sends {"operation": "discover"} and then one request built only out of the published shape of each | THEN each of the 5 carries its request fields and its answer fields, and each of the 5 requests is answered "completed"
  - SC3 | P3 | GIVEN core-0 with 3 type names and 11 operators (SPEC.md lines 98 and 178-189) | WHEN an agent sends {"operation": "discover"} | THEN "+" carries the arguments ["Int", "Int"] and the result "Int", "not" carries ["Bool"] and "Bool", and "=" carries one name in both argument places with a sentence saying it stands for any core type
  - SC4 | P4 | GIVEN "evaluate", advertised as available, whose published request shape names "function" a text | WHEN an agent sends {"operation": "evaluate", "source": "(defn twice ...)", "function": "twice", "arguments": ["3"]} | THEN the answer is "completed" and carries the value 6
  - SC5 | P4 | GIVEN the same published shape of "evaluate" | WHEN an agent sends the same request with "function": 7 | THEN the answer is "invalid_input" and the refusal names the field "function"
  - SC6 | P5 | GIVEN "evaluate", which the tool answers and which SPEC.md names in none of its 7 categories | WHEN an agent sends {"operation": "discover"} | THEN "evaluate" is listed as beyond the profile with a reason, no category names it, and every 1 of the advertised operations is in exactly one of the two lists
- **conflicts**:
  - S1 | NONE | checked the suite runs with uv run pytest and that this work adds files, it changes no runner
  - S2 | NONE | checked SPEC.md lines 463-478 against the manifest service.py builds today; nothing in SPEC.md is contradicted
  - S3 | NONE | this work adds test files and leaves SPEC.md and every existing test file untouched
  - S4 | NONE | the one existing test this work bumps into is reported below at S28 rather than edited
  - S5 | NONE | nothing under .relay is read, written or depended on by this work
  - S6 | NONE | all edits are made in the prova-wt-f11 worktree on its own branch feat/f11
  - S7 | NONE | the commit message trailer is written at commit time and contradicts nothing in the tree
  - S8 | NONE | the trailer line is a literal and contradicts no behaviour of the tool
  - S9 | NONE | no push and no merge is made; the branch keeps its own history
  - S10 | NONE | ran the whole suite command once before starting and read which tests touch discover
  - S11 | NONE | F12 owns syntax.py and the parse dispatch; this work adds a module and 3 keys to the manifest
  - S12 | NONE | read service.py, checker.DIAGNOSTIC_KINDS and _run_discover and follow their published-shape structure
  - S13 | NONE | the planned service.py edit is an import and three keys in the manifest result
  - S14 | NONE | the scripts of this run live under the nwstep workspace in their own directory
  - S15 | NONE | the laws below name @given tests and the witnesses of the design step will be a class or a def
  - S16 | NONE | submissions are passed from a script in this run directory and the worktree is left clean
  - S17 | NONE | discover answers today with the profile, the operations, the statuses, the diagnostic schemas and the limits, and nothing there contradicts carrying more
  - S18 | NONE | the diagnostic schemas, the profile coverage and the resource limits are already published and this work keeps them as they are
  - S19 | NONE | the resource limits block already carries the two limits and is not changed by this work
  - S20 | NONE | a heading contradicts nothing the tool does today
  - S21 | NONE | a numeral contradicts nothing the tool does today
  - S22 | NONE | the manifest names 8 operations today and names no category at all, so a category list adds a reading and contradicts none
  - S23 | NONE | parse, format and build are already advertised as unavailable, which is the word this sentence asks for
  - S24 | NONE | a numeral contradicts nothing the tool does today
  - S25 | NONE | no request or answer shape is published today, so publishing one contradicts nothing
  - S26 | NONE | the answers of the 5 available operations were read and each one can be described as it stands
  - S27 | NONE | a numeral contradicts nothing the tool does today
  - S28 | CONFLICT | tests/unit/test_service_discover.py::test_discover_makes_no_verification_proof_or_build_claim asserts that the lowercased JSON of the whole discover answer carries none of the words verified, proved, built and holds; the words builtin and builtins carry the letters of built, so publishing this part under that name turns that existing test red | May the manifest publish the types and operators of core-0 under a name that avoids the word builtin, as language with types and operators inside it, keeping the existing no-claim test as it stands?
  - S29 | NONE | the argument and result types of every operator are fixed by SPEC.md lines 178-189 and are the ones the checker keeps today
  - S30 | NONE | a numeral contradicts nothing the tool does today
  - S31 | NONE | the 5 available operations each answer a well formed request today, which is what this sentence asks of them
  - S32 | NONE | the source field is read as the text of a program and already answers a well formed request
  - S33 | NONE | a field of the request holding another kind of value is already refused with invalid_input and malformed_request
  - S34 | NONE | a numeral contradicts nothing the tool does today
  - S35 | NONE | evaluate is answered today and is named in none of the 7 categories of SPEC.md lines 467-468
  - S36 | NONE | the manifest says nothing today about which operations the profile names, so saying it contradicts nothing
  - S37 | NONE | the profile block says coverage partial and claims no conformance for any single operation
  - S38 | NONE | read SPEC.md lines 463-478 whole; they ask for exactly the parts this feature publishes
  - S39 | NONE | nothing in this work waits on another feature of this delivery
  - S40 | NONE | the size decides which steps are due and contradicts no behaviour
  - S41 | NONE | service.py, the tests and the fixtures are the files this work touches, plus one new module
  - S42 | NONE | read docs/spec-trace.md rows 8.2 and 8.3 and both are still Partial in the tree
  - S43 | NONE | counted the categories against SPEC.md lines 467-468 and the operations against the manifest
  - S44 | NONE | proposal P1 is background and asks for nothing this work contradicts
- **decisions**:
  - S28: The types and operators are published under the key language, holding types and operators, and the words builtin and builtins are kept out of the discover answer. The existing no-claim test is left exactly as it is, acceptance criterion 3 is met in full, and the owner is asked at the pause whether the name language is the one an agent should read.
  - DEC1: The operation list that discover already carries keeps its exact shape, a name to the word available or unavailable, because tests/unit/test_service_discover.py compares it with equality. The categories, the shapes and the language are published beside it as new parts of the manifest.
  - DEC2: The source field is published as optional, because a request without it is answered today as a program with nothing in it. Publishing it as required would make the tool refuse requests it answers today and turn existing tests red. Acceptance criterion 4 is read as being about the kind of value a published field carries.
  - DEC3: Request and answer shapes are published only for the operations advertised as available. An operation that is refused has no shape fixed yet, and publishing one would promise a request nobody can send.
  - DEC4: The operation field itself is not one of the per operation request fields. A request whose operation field carries another kind of value names no operation at all and is answered unavailable with unknown_operation, which is the existing behaviour and is not a refusal of a field of a known operation.
- **mapping**:
  - P1 => test_every_operation_category_the_profile_names_is_there_with_its_word
  - P1 => test_the_word_a_category_carries_is_the_one_the_operation_answers_with
  - P2 => test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  - P2 => test_every_field_an_answer_carries_is_one_the_shape_publishes
  - P3 => test_every_type_core_0_has_is_named_with_what_it_is
  - P3 => test_every_operator_is_named_with_the_types_it_takes_and_answers
  - P4 => test_an_operation_advertised_as_available_answers_a_matching_request
  - P4 => test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
  - P5 => test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own
  - P5 => test_every_operation_is_either_in_a_category_or_marked_as_beyond_it
- **covers_scenarios**:
  - SC1 => test_every_operation_category_the_profile_names_is_there_with_its_word
  - SC1 => test_the_word_a_category_carries_is_the_one_the_operation_answers_with
  - SC2 => test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  - SC2 => test_a_request_built_only_from_the_published_shape_is_answered
  - SC3 => test_every_operator_is_named_with_the_types_it_takes_and_answers
  - SC4 => test_an_operation_advertised_as_available_answers_a_matching_request
  - SC5 => test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
  - SC6 => test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own
  - SC6 => test_every_operation_is_either_in_a_category_or_marked_as_beyond_it
- **interfaces**:
  - I1: the prova command answering the discover operation, read as one JSON request on standard input and one JSON answer on standard output
  - I2: the prova command answering check, verify, examples and evaluate, each called as the manifest describes it
- **matrix**:
  - I1.empty => a request carrying only {"operation": "discover"} and no other field => the whole manifest with status completed
  - I1.unknown => a request asking for the category name {"operation": "discovery"} => status unavailable with the category unknown_operation
  - I1.malformed => the text {"operation": "disc which stops partway => status invalid_input with the category malformed_request
  - I1.dependency-gone => n/a: discover reads no file, no network and no other process; it answers from the tool itself
  - I1.repeated => two discover requests one after the other => the same manifest twice and nothing written anywhere
  - I1.concurrent => n/a: each request is one process reading its own standard input and sharing no state with another
  - I1.crash => n/a: the command keeps no file and no state, so a run stopped halfway leaves nothing behind
  - I2.empty => check with "source": "" => status completed over a program declaring 0 functions
  - I2.unknown => evaluate naming "function": "absent", which the program does not declare => status invalid_input with the category unknown_function
  - I2.malformed => check with "source": 7 => status invalid_input with the category malformed_request naming the field source
  - I2.dependency-gone => n/a: these operations read the source out of the request itself and open nothing else
  - I2.repeated => the same evaluate request sent twice => the same answer twice, with the same source revision
  - I2.concurrent => n/a: one request per process, no shared file and no lock to contend for
  - I2.crash => n/a: nothing is written, so a run stopped halfway leaves no half written answer anywhere
- **laws**:
  - LAW1 | a field the manifest publishes for an operation, sent as a value of any kind the published shape does not name, is always refused as invalid input and the refusal names that field | generator=test_a_published_field_of_another_kind_is_always_refused_by_name | observation=the status of the answer and the symbol each diagnostic names | mutant=a field read with a default instead of being refused leaves the status completed and the law fails
  - LAW2 | every field an answer carries is published for that operation, every field published as always is in every answer, and every field published as when completed is in exactly the completed answers | generator=test_every_answer_carries_the_fields_the_manifest_publishes | observation=the key set of the answer against the published fields and their presence | mutant=an answer that carries a result key on a refusal, or a shape that leaves source_digest out, fails the law
  - LAW3 | the signature the manifest publishes for an operator is the one the tool keeps: operands of the published types are checked and an operand of another type is refused with a type mismatch | generator=test_the_published_signature_of_an_operator_is_the_one_the_tool_keeps | observation=the status and the diagnostic categories of two programs per operator | mutant=publishing Int operands for and or not makes the checked program draw a type mismatch and the law fails
- **messages**:
  - MSG1 | {"operation": "evaluate", "source": "(defn twice ...)", "function": 7} | the function field of the request holds int, not the name of a function | this tool looks a function up by the name its program declares for it, and a value of another kind names nothing to look up | send the function as one JSON string, and read the names a program declares by sending it to the check operation first | test=test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
  - MSG2 | {"operation": "check", "source": 7} | the source field of the request holds int, not the text of a program | this tool reads a program from the characters of that field, and a value of another kind holds no characters to read | send the program as one JSON string, writing a line break as a backslash n | test=test_a_published_field_of_another_kind_is_always_refused_by_name
  - MSG3 | {"operation": "discovery"} | operation discovery is not recognized | discovery is the name of a category of SPEC.md and not the name of an operation this tool answers | read the operation of each category from the categories block of the discover answer and send that name | test=test_every_operation_category_the_profile_names_is_there_with_its_word
- **red**: `uv run pytest -q tests/acceptance/test_f11_b1_the_manifest_names_every_operation_category.py tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py tests/acceptance/test_f11_b4_a_request_that_breaks_the_published_shape_is_refused.py tests/acceptance/test_f11_b5_an_operation_the_profile_does_not_name_says_so.py tests/properties/test_f11_manifest_laws.py` exited 1 in 2.556s
  - failing on the pre-feature tree (15): tests/acceptance/test_f11_b1_the_manifest_names_every_operation_category.py::test_every_operation_category_the_profile_names_is_there_with_its_word, tests/acceptance/test_f11_b1_the_manifest_names_every_operation_category.py::test_the_word_a_category_carries_is_the_one_the_operation_answers_with, tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py::test_every_operation_an_agent_may_call_publishes_both_of_its_shapes, tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py::test_a_request_built_only_from_the_published_shape_is_answered, tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py::test_every_field_an_answer_carries_is_one_the_shape_publishes, tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py::test_every_type_core_0_has_is_named_with_what_it_is, tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py::test_every_operator_is_named_with_the_types_it_takes_and_answers, tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py::test_no_operator_is_published_over_a_type_the_manifest_never_names, tests/acceptance/test_f11_b4_a_request_that_breaks_the_published_shape_is_refused.py::test_an_operation_advertised_as_available_answers_a_matching_request, tests/acceptance/test_f11_b4_a_request_that_breaks_the_published_shape_is_refused.py::test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name, tests/acceptance/test_f11_b5_an_operation_the_profile_does_not_name_says_so.py::test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own, tests/acceptance/test_f11_b5_an_operation_the_profile_does_not_name_says_so.py::test_every_operation_is_either_in_a_category_or_marked_as_beyond_it, tests/properties/test_f11_manifest_laws.py::test_a_published_field_of_another_kind_is_always_refused_by_name, tests/properties/test_f11_manifest_laws.py::test_every_answer_carries_the_fields_the_manifest_publishes, tests/properties/test_f11_manifest_laws.py::test_the_published_signature_of_an_operator_is_the_one_the_tool_keeps
  - tests (read from the run): 15 failed in 1.95s
  ```text

  operator = '+'

      @given(operator=st.sampled_from(THE_OPERATORS))
      @settings(max_examples=11, deadline=None)
      def test_the_published_signature_of_an_operator_is_the_one_the_tool_keeps(operator):
          """LAW3: a program applying an operator to operands of its published
          argument types is checked, and the same program with one operand of
          another type is refused with a type mismatch."""
          operators = (_manifest().get("language") or {}).get("operators")
  >       assert isinstance(operators, dict) and operator in operators, (
              f"the manifest publishes the operators {sorted(operators or {})} and "
              f"nothing about {operator!r}, which core-0 has (SPEC.md lines "
              "178-189). An agent writing a program has to guess it."
          )
  E       AssertionError: the manifest publishes the operators [] and nothing about '+', which core-0 has (SPEC.md lines 178-189). An agent writing a program has to guess it.
  E       assert (False)
  E        +  where False = isinstance(None, dict)
  E       Failing test case: test_the_published_signature_of_an_operator_is_the_one_the_tool_keeps(
  E           operator='+',  # or any other generated value
  E       )

  tests/properties/test_f11_manifest_laws.py:220: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f11_b1_the_manifest_names_every_operation_category.py::test_every_operation_category_the_profile_names_is_there_with_its_word
  FAILED tests/acceptance/test_f11_b1_the_manifest_names_every_operation_category.py::test_the_word_a_category_carries_is_the_one_the_operation_answers_with
  FAILED tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py::test_every_operation_an_agent_may_call_publishes_both_of_its_shapes
  FAILED tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py::test_a_request_built_only_from_the_published_shape_is_answered
  FAILED tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py::test_every_field_an_answer_carries_is_one_the_shape_publishes
  FAILED tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py::test_every_type_core_0_has_is_named_with_what_it_is
  FAILED tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py::test_every_operator_is_named_with_the_types_it_takes_and_answers
  FAILED tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py::test_no_operator_is_published_over_a_type_the_manifest_never_names
  FAILED tests/acceptance/test_f11_b4_a_request_that_breaks_the_published_shape_is_refused.py::test_an_operation_advertised_as_available_answers_a_matching_request
  FAILED tests/acceptance/test_f11_b4_a_request_that_breaks_the_published_shape_is_refused.py::test_a_published_field_sent_as_another_kind_of_value_is_refused_by_name
  FAILED tests/acceptance/test_f11_b5_an_operation_the_profile_does_not_name_says_so.py::test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own
  FAILED tests/acceptance/test_f11_b5_an_operation_the_profile_does_not_name_says_so.py::test_every_operation_is_either_in_a_category_or_marked_as_beyond_it
  FAILED tests/properties/test_f11_manifest_laws.py::test_a_published_field_of_another_kind_is_always_refused_by_name
  FAILED tests/properties/test_f11_manifest_laws.py::test_every_answer_carries_the_fields_the_manifest_publishes
  FAILED tests/properties/test_f11_manifest_laws.py::test_the_published_signature_of_an_operator_is_the_one_the_tool_keeps
  15 failed in 1.95s
  ```

## 2. design: Find the owners and design the change (revision 1)

- **owners**:
  - which operations this tool has and whether each one is available => src/prova/service.py, in AVAILABLE_OPERATIONS and UNAVAILABLE_OPERATIONS, left exactly where they are so the parallel delivery rebases cleanly
  - which of the 7 categories of SPEC.md an operation covers, and which operations are this tool own => new: src/prova/manifest.py, because no module answers that question today
  - the fields a request of an operation takes and the fields its answer carries => new: src/prova/manifest.py, beside the standing of the same operation, so one object answers both
  - how many arguments an operator takes and how its operands are read => src/prova/checker.py, in BUILTIN_OPERATORS, extended so the entry also carries the types it takes and the type it answers
  - which type names core-0 has => src/prova/checker.py, in BUILTIN_TYPES, restated as one table of entries that also say what the values of each type are
  - what a diagnostic of each category carries => src/prova/checker.py, in DIAGNOSTIC_KINDS, reused unchanged: the manifest already publishes it
  - the answer of the discover operation => src/prova/service.py, in _run_discover, which gains three keys read from the catalogue and changes nothing else
  - the name of a field the request reader reads => new: src/prova/manifest.py, read by the reader in service.py so that the name published and the name a refusal carries are one value
- **reuse_decision**: Reused: the request reader, the diagnostic kinds and their published shapes, the contract report publisher and the two operation tuples of the dispatcher, all unchanged. Extended: the operator table and the type names of checker.py, which already own what an operator takes and which types exist; the argument and result types belong there and nowhere else, so no second table decides them. Created new: src/prova/manifest.py, for the catalogue of operations with their categories and their request and answer shapes. No existing module owns that question: the dispatcher owns which names exist and the checker owns the language, and neither knows what a request for an operation looks like. The new module also keeps the diff of service.py to one import and three keys, which the parallel delivery on the dispatch needs.
- **paradigm**: oo
- **boundaries**:
  - the JSON answer of the prova command: service.py builds it and owns its keys; manifest.py owns the shape of the three new parts and never writes the answer itself
  - the operator and type tables of core-0: checker.py owns them; manifest.py asks each entry to publish itself and declares no signature of its own
  - which operations are available: service.py owns the two tuples and passes them in; manifest.py refuses to build a catalogue that does not describe exactly those names
  - the request reader: service.py owns the reading and the refusal messages; manifest.py owns the names of the fields that are read, so the published name and the refused name cannot drift
- **domain_types**:
  - Operation: one operation this tool has, carrying its standing in the profile and the two shapes of its traffic, and answering whether an agent may call it
  - InACategory and BeyondTheProfile: the two standings an operation can have, written as one choice, so that an operation in both lists and an operation in neither cannot be built
  - Catalogue: the collection of operations and nothing else; built only from the names the dispatcher advertises, and refusing any other set
  - RequestField: one field of a request, with its name, the kind of value it carries, whether it must be sent and what it is for
  - AnswerField: one field of an answer, with the same parts, where whether it is there is always, when completed, or a sentence of its own
  - BuiltinType: one type name of core-0 beside what its values are, so the name the checker knows and the name an agent reads are one entry
  - OperandsOfOneType and OperandsOfOneAndTheSameType: the two rules an operator reads its operands by; each one refuses the operands that break it and publishes the argument types of its operator
- **invariants**:
  - INV1 | the catalogue describes exactly the operations the dispatcher advertises: a catalogue built over a different set of names cannot be built at all, so the manifest can never leave out an operation the tool answers or advertise one it does not have | witness=src/prova/manifest.py:Catalogue | bypass=none
  - INV2 | every operation an agent may call carries a request shape and an answer shape, and an operation that is refused carries neither, so an agent never reads a shape for a request it cannot send | witness=src/prova/manifest.py:Operation | bypass=none
  - INV3 | an operation stands in exactly one of SPEC.md categories or is marked as this tool own, never in both and never in neither, because the standing is one value of a choice and not two lists | witness=src/prova/manifest.py:BeyondTheProfile | bypass=none
  - INV4 | the argument and result types published for an operator are the ones the checker reads when it checks a call, because the operand rule that refuses a wrong operand is the same object that publishes the types | witness=src/prova/checker.py:BuiltinOperator | bypass=none
  - INV5 | the type names the checker knows and the type names the manifest publishes are one table, so a type can never be known to the checker and absent from the manifest | witness=src/prova/checker.py:BuiltinType | bypass=none
  - INV6 | the name a published request field carries is the name the reader looks the field up under and the name its refusal carries; the kind of value named there is bound to the refusal by the generated law LAW1 and not by construction, because the refusal messages are owned by the robustness work and are not rewritten here | witness=src/prova/manifest.py:RequestField | bypass=the message text of each refusal still writes the field name in its own sentence; a message edited without the published name would read oddly but could not change which field the refusal names
- **prefactoring**: yes
- **prefactoring_reason**: The operator table carries a number of arguments and the name of a group today, and the operand rules stand in a chain of four branches that reads that group name. Publishing the argument and result types from a second table would make two units decide one fact, so first the table learns its operand rule and its result type as an object, and the four branches are replaced by asking that object. The type names are restated the same way, as one table of entries that keeps BUILTIN_TYPES as the set of their names. Behaviour is unchanged: every refusal keeps its category, its sentence, the place it stands at and the two types it names, the group names and the four sets stay exactly as the existing table test reads them, and no test is edited.

## 4. craft: Craft the change (revision 2)

- **refactor_commits**:
  - 80d766b
- **refactor_check**: the check ran on the parent and on each refactor commit
  - 80d766b578cd (Let an operator say which types it takes and answers): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 137.22s
  - tests (read from the run): 1153 passed in 137.09s
  - slowest: 6.97s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.54s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 4.06s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.46s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 3.25s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 2.85s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 2.04s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.72s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.60s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.45s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  ```text
  ........................................................................ [  6%]
  ........................................................................ [ 12%]
  ........................................................................ [ 18%]
  ........................................................................ [ 24%]
  ........................................................................ [ 31%]
  ........................................................................ [ 37%]
  ........................................................................ [ 43%]
  ........................................................................ [ 49%]
  ........................................................................ [ 56%]
  ........................................................................ [ 62%]
  ........................................................................ [ 68%]
  ........................................................................ [ 74%]
  ........................................................................ [ 81%]
  ........................................................................ [ 87%]
  ........................................................................ [ 93%]
  ........................................................................ [ 99%]
  .                                                                        [100%]
  ============================= slowest 10 durations =============================
  6.97s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.54s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  4.06s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.46s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  3.25s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  2.85s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  2.04s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.72s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.60s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.45s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1153 passed in 137.09s (0:02:17)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.052s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this process environment and from the login shell, so the client exits 3 before any call; the design choices it would have been asked (where the catalogue lives, where the operator signatures come from, whether a formal model pays) were settled locally and written in docs/feature/f11/design.md
