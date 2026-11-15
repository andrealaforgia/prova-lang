# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 932 tests, all green on main).
  - not-testable (challenge this): names the project, its test command and the green baseline it starts from.
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority to read, which no test can observe.
- S3: Do not change SPEC.md or any existing test's expected result.
  - promises: P12
  - tests P12: test_the_published_status_is_the_one_an_out_of_profile_source_gets
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): a process rule for this delivery, answered by the conflict record and the pause report, not by a test.
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): excludes a directory from the reading, which no test observes.
- S6: Work in this git worktree only, on its branch.
  - promises: P12
  - tests P12: test_the_published_status_is_the_one_an_out_of_profile_source_gets
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a commit message convention, read from the commit and not from the product.
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line of that same commit message convention.
- S9: Do not push and do not merge.
  - promises: P12
  - tests P12: test_the_published_status_is_the_one_an_out_of_profile_source_gets
- S10: Keep the full suite green.
  - promises: P12
  - tests P12: test_the_published_status_is_the_one_an_out_of_profile_source_gets
- S11: Another delivery (F7, operator arity, only src/prova/checker.py) runs in parallel in a different worktree; do not touch checker.py.
  - promises: P12
  - tests P12: test_the_published_status_is_the_one_an_out_of_profile_source_gets
- S12: F5 and F6 are already on main.
  - not-testable (challenge this): states which features are already on the trunk this branch started from.
- S13: Existing categories include syntax, unbound_name, cyclic_dependency, duplicate_declaration, recursive_type, shadowed_binding and reserved_name; the unsupported refusal needs a separate status alongside invalid_program as the roadmap says: publish it in the manifest and explain it in your oracle note.
  - promises: P1, P9
  - tests P1: test_a_program_that_divides_is_refused_as_outside_this_profile
  - tests P9: test_the_manifest_lists_the_status_and_the_category_this_rule_adds
- S14: If an existing test conflicts, stop and report.
  - not-testable (challenge this): repeats the process rule about stopping on a conflict with an existing test.
- S15: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell quoting and submission hygiene for the recording tool, not product behaviour.
- S16: **Outcome.** Source using something `core-0` does not have — division, a decimal
  - promises: P1, P3
  - tests P1: test_a_program_that_divides_is_refused_as_outside_this_profile
  - tests P3: test_a_program_that_divides_is_refused_as_outside_this_profile
- S17: literal, text, `fn`, `defspec`, `trust`, `module`, a trailing top-level expression —
  - promises: P4, P5, P6
  - tests P4: test_a_decimal_literal_is_refused_as_outside_this_profile
  - tests P5: test_a_call_after_the_declarations_is_refused_as_outside_this_profile
  - tests P6: test_a_declaration_word_core_0_does_not_have_is_refused_as_outside_this_profile
- S18: is refused with a message that says it is outside this profile.
  - promises: P2
  - tests P2: test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands
- S19: **Acceptance criteria**
  - not-testable (challenge this): a heading introducing the criteria that follow.
- S20: 1.
  - not-testable (challenge this): the number of the first acceptance criterion.
- S21: Given a program using division, when it is checked, then it is refused and the
  - promises: P3
  - tests P3: test_a_program_that_divides_is_refused_as_outside_this_profile
- S22: diagnostic says the construct is unsupported in this profile and names it.
  - promises: P2
  - tests P2: test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands
- S23: 2.
  - not-testable (challenge this): the number of the second acceptance criterion.
- S24: Given a decimal or text literal, then the refusal says unsupported, not that a
  - promises: P4
  - tests P4: test_a_decimal_literal_is_refused_as_outside_this_profile
- S25: name is unbound.
  - promises: P4
  - tests P4: test_a_decimal_literal_is_refused_as_outside_this_profile
- S26: 3.
  - not-testable (challenge this): the number of the third acceptance criterion.
- S27: Given a trailing top-level expression, then the refusal says unsupported, not a
  - promises: P5
  - tests P5: test_a_call_after_the_declarations_is_refused_as_outside_this_profile
- S28: generic syntax error.
  - promises: P5
  - tests P5: test_a_call_after_the_declarations_is_refused_as_outside_this_profile
- S29: 4.
  - not-testable (challenge this): the number of the fourth acceptance criterion.
- S30: Given each of the fourteen fixtures in `evidence/cases/`, when each is checked,
  - promises: P7
  - tests P7: test_every_preserved_counterexample_is_refused_for_the_construct_it_uses
- S31: then the ones meant to be refused are refused and the ones meant to pass pass.
  - promises: P7
  - tests P7: test_every_preserved_counterexample_is_refused_for_the_construct_it_uses
- S32: 5.
  - not-testable (challenge this): the number of the fifth acceptance criterion.
- S33: Given an unsupported refusal, then nothing in the response claims the program's
  - promises: P8
  - tests P8: test_an_out_of_profile_answer_claims_nothing_about_the_program
- S34: deeper meaning was checked.
  - promises: P8
  - tests P8: test_an_out_of_profile_answer_claims_nothing_about_the_program
- S35: **SPEC.md** lines 51-54, 79-80, 125-128, 191-196, 472-474 (the three kinds of
  - not-testable (challenge this): cites the authority lines the rule is read from.
- S36: failure are distinct).
  - promises: P1
  - tests P1: test_a_program_that_divides_is_refused_as_outside_this_profile
- S37: **Dependencies** none, but shares `src/prova/syntax.py` with F6.
  - not-testable (challenge this): names the dependency and the file shared with another feature.
- S38: **Size** M: needs a
  - promises: P1
  - tests P1: test_a_program_that_divides_is_refused_as_outside_this_profile
- S39: separate "unsupported" status alongside `invalid_program`.
  - promises: P1
  - tests P1: test_a_program_that_divides_is_refused_as_outside_this_profile
- S40: **Touches** `src/prova/syntax.py`, `src/prova/service.py`, `evidence/cases/` wired
  - not-testable (challenge this): lists the files the work is expected to touch.
- S41: into tests, tests.
  - not-testable (challenge this): continues the list of files the work is expected to touch.
- S42: **Why it is a real expectation** probes G4, L5 disagree; no test reads
  - promises: P3, P4
  - tests P3: test_a_program_that_divides_is_refused_as_outside_this_profile
  - tests P4: test_a_decimal_literal_is_refused_as_outside_this_profile
- S43: `evidence/cases/` today (section 1).
  - promises: P7
  - tests P7: test_every_preserved_counterexample_is_refused_for_the_construct_it_uses

## Edge matrix

- I1.empty: the empty source, and a source holding only a comment => unchanged: invalid_program with the syntax category saying a declaration is missing | self-probe: not probed | pre-feature not probed
- I1.unknown: an operation name the tool does not know => unchanged: unavailable with the unknown_operation category | self-probe: not probed | pre-feature not probed
- I1.malformed: a source whose body is (/ n 1), 1.5 or "ok", or that ends with a call => unsupported with the unsupported_construct category naming the construct and its line | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the operation reads one request from standard input and calls nothing outside the process
- I1.repeated: the same out-of-profile source asked twice in two runs => the identical response both times; nothing is written and nothing is kept | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): one request per process and no file or shared state is touched, so two runs cannot meet
- I1.crash: n/a (challenge this): the command writes no file, so an interruption leaves nothing half written to recover
- I2.empty: discover asked with no source field at all => unchanged: the manifest, now also listing the statuses the tool answers with | self-probe: not probed | pre-feature not probed
- I2.unknown: discover asked with an unknown extra field => unchanged: the manifest, which reads no field but the operation | self-probe: not probed | pre-feature not probed
- I2.malformed: a request body that is not JSON => unchanged: tool_failure with the reason from the JSON reader and exit 1 | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): the manifest is built from the service own tables and reads no file
- I2.repeated: discover asked twice => the identical manifest both times | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): the manifest is read only and holds no state two callers could share
- I2.crash: n/a (challenge this): discover writes nothing, so an interruption leaves nothing to recover

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the source "(defn f (sig ((n Int)) -> Int ! pure) (examples (example (f 1) => 1)) (/ n 1))"
  - WHEN the command checks it
  - THEN the status is "unsupported" and not "invalid_program"
  - test: test_a_program_that_divides_is_refused_as_outside_this_profile
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN that same source with "/" on line 4
  - WHEN the command checks it
  - THEN the reason says "unsupported", says "core-0" and names division, placed at line 4
  - test: test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN the source whose only body is "(/ n 1)" on line 4
  - WHEN the command checks it
  - THEN no diagnostic says the name "/" is unbound, and the twin body "(* n 1)" is answered "completed"
  - test: test_a_program_that_divides_is_refused_as_outside_this_profile
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN a function whose body is the decimal literal 1.5, and one whose body is the text literal "ok"
  - WHEN each is checked
  - THEN each is "unsupported" naming the literal, and the twin whose body is 1 is "completed"
  - test: test_a_text_literal_is_refused_as_outside_this_profile
- SC5 (P5): not-held (no held self-probe case)
  - GIVEN the in-profile program followed on line 6 by the call "(f 1)"
  - WHEN the command checks it
  - THEN the status is "unsupported", the reason says "top-level expression" and names f, and the same source without that call is "completed"
  - test: test_a_call_after_the_declarations_is_refused_as_outside_this_profile
- SC6 (P6): not-held (no held self-probe case)
  - GIVEN the same declaration written "(defspec f ...)" on line 1
  - WHEN the command checks it
  - THEN the status is "unsupported" and the reason names "defspec" as a declaration form core-0 does not have
  - test: test_a_declaration_word_core_0_does_not_have_is_refused_as_outside_this_profile
- SC7 (P7): not-held (no held self-probe case)
  - GIVEN each of the 14 files in evidence/cases/
  - WHEN each is checked
  - THEN each is "unsupported" naming its own construct, and each adaptation to core-0 is answered "completed" or "invalid_program", never "unsupported"
  - test: test_every_preserved_counterexample_is_refused_for_the_construct_it_uses
- SC8 (P8): not-held (no held self-probe case)
  - GIVEN the source with the trailing call "(f 1)"
  - WHEN the command checks it
  - THEN the response has no "claim", no "result" and no "source_digest" key and none of the 9 words that would claim something was established
  - test: test_an_out_of_profile_answer_claims_nothing_about_the_program
- SC9 (P9): not-held (no held self-probe case)
  - GIVEN a caller that asks "discover"
  - WHEN it reads the manifest
  - THEN result.statuses names "unsupported" with a meaning saying "core-0" and "profile", and diagnostic_categories lists "unsupported_construct" beside the 7 already published
  - test: test_the_manifest_lists_the_status_and_the_category_this_rule_adds
- SC10 (P10): not-held (no held self-probe case)
  - GIVEN the source whose body is "(/ n 1)"
  - WHEN each of check, examples, verify and evaluate reads it
  - THEN all 4 answer "unsupported" with that one category and no result
  - test: test_every_out_of_profile_source_is_refused_the_same_way_by_every_operation
- SC11 (P11): not-held (no held self-probe case)
  - GIVEN examples/hour-clock.prova, conformance/add-one.prova, a body "(+ n missing-name)" and "(deftypo T (record (x Int)))"
  - WHEN each is checked
  - THEN the first 2 stay "completed" and the other 2 stay "invalid_program" with the categories unbound_name and syntax
  - test: test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else
- SC12 (P12): not-held (no held self-probe case)
  - GIVEN the branch feat/f9 after the change
  - WHEN "uv run pytest -q tests" runs and "git status --short" runs
  - THEN all 932 existing tests and the new ones pass and the working tree is clean
  - test: test_the_published_status_is_the_one_an_out_of_profile_source_gets

## Questions for the owner

- none

## Observed side effects (git, BASE to HEAD)

- A docs/feature/f9/craft.md (+103 -0 lines)
- A docs/feature/f9/design.md (+106 -0 lines)
- A docs/feature/f9/oracle.md (+98 -0 lines)
- A docs/feature/operator-arity/craft.md (+101 -0 lines)
- A docs/feature/operator-arity/oracle.md (+108 -0 lines)
- A docs/operator-arity/DECISIONS.md (+11 -0 lines)
- A docs/operator-arity/SUMMARY.md (+499 -0 lines)
- A docs/operator-arity/TRACE.md (+5 -0 lines)
- M docs/spec-trace.md (+9 -0 lines)
- M docs/spec-trace/probe.py (+5 -1 lines)
- M src/prova/checker.py (+78 -4 lines)
- M src/prova/service.py (+113 -68 lines)
- M src/prova/syntax.py (+206 -0 lines)
- A tests/acceptance/_f7_operator_arity_fixtures.py (+486 -0 lines)
- A tests/acceptance/_f9_profile_fixtures.py (+408 -0 lines)
- A tests/acceptance/test_f7_b1_an_operator_given_an_extra_argument_is_refused.py (+69 -0 lines)
- A tests/acceptance/test_f7_b2_a_sum_with_too_few_or_too_many_arguments_is_refused.py (+56 -0 lines)
- A tests/acceptance/test_f7_b3_every_operator_with_a_wrong_count_is_refused.py (+109 -0 lines)
- A tests/acceptance/test_f7_b4_every_operator_applied_correctly_is_accepted.py (+69 -0 lines)
- A tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py (+92 -0 lines)
- A tests/acceptance/test_f7_b6_a_wrong_count_and_a_wrong_operand_are_both_reported.py (+90 -0 lines)
- A tests/acceptance/test_f7_b7_the_refusal_uses_a_category_the_manifest_publishes.py (+65 -0 lines)
- A tests/acceptance/test_f7_b8_a_wrong_count_in_a_contract_or_a_clause_is_refused.py (+111 -0 lines)
- A tests/acceptance/test_f9_b1_division_is_refused_as_unsupported.py (+70 -0 lines)
- A tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py (+102 -0 lines)
- A tests/acceptance/test_f9_b3_a_trailing_top_level_expression_is_refused_as_unsupported.py (+104 -0 lines)
- A tests/acceptance/test_f9_b4_a_preserved_counterexample_is_refused_as_unsupported.py (+63 -0 lines)
- A tests/acceptance/test_f9_b5_an_unsupported_refusal_claims_nothing_more.py (+81 -0 lines)
- A tests/acceptance/test_f9_b6_the_manifest_publishes_the_unsupported_answer.py (+134 -0 lines)
- M tests/properties/test_f5_binding_scope.py (+6 -2 lines)
- A tests/properties/test_f7_operator_arity.py (+170 -0 lines)
- A tests/properties/test_f9_out_of_profile_source.py (+289 -0 lines)
- A tests/unit/test_checker_operator_table.py (+69 -0 lines)

## Commits (git log, BASE to HEAD)

- a0db9aa Keep every reserved word out of the F5 free-name generator
- 33188fa [F7] refuse an operator written with the wrong number of arguments
- f8ae4a4 [F7] keep the delivery's record beside the change
- 2581941 [F7] pin acceptance on a program with no operator, not on an empty one
- 1d14959 [F7] let one table say which operators the language has
- 6836d6b [F7] count an operator's arguments in a contract and in a clause too
- 4dcbf74 [F7] restate the counts this branch actually measured
- 903f420 [F7] close the delivery's record beside the change
- 6ee913b Let one owner answer a source the tool cannot check
- f17fe1d Say what an out-of-profile source should be told, before saying it
- 7e79d26 Tell a source that core-0 has no such construct, instead of guessing
- d54c227 Record what F9 was measured at, beside the change
- 5701c86 Keep a misplaced parenthesis a misplaced parenthesis
- feb8130 Correct the craft record after the review and the rebase

## 2. oracle: Frame the work and write the oracle (revision 2)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f9/request.md
- **promises**:
  - P1: An out-of-profile source is refused with the status "unsupported", a status of its own beside "invalid_program".
  - P2: The refusal says the construct is unsupported in the core-0 profile and names the construct.
  - P3: Division is refused as unsupported, not reported as a call to an undeclared function.
  - P4: A decimal literal and a text literal are refused as unsupported, not as an unbound name and not as a value the tool cannot read.
  - P5: A trailing top-level expression is refused as unsupported, not with the general refusal for a form the reader cannot place at the top level.
  - P6: The declaration words fn, defspec, trust and module are refused as unsupported and named.
  - P7: Each of the fourteen preserved files in evidence/cases/ is refused for the construct it uses, and the same case written with only what core-0 has is answered by the ordinary rules instead.
  - P8: An unsupported answer carries no claim, no result and no source digest, and no word saying anything about the program was established.
  - P9: The manifest publishes the unsupported status with its meaning and the unsupported_construct category.
  - P10: Every operation that reads source - check, examples, verify, evaluate - gives an out-of-profile source the same refusal.
  - P11: A source core-0 already accepted is still accepted, and a mistake it already refused keeps the status and the categories its own rule owns.
  - P12: The delivery stays in this worktree and branch, edits neither SPEC.md nor checker.py nor any existing test expected result, and leaves the full suite green.
- **sentence_map**:
  - S1 => not-testable: names the project, its test command and the green baseline it starts from.
  - S2 => not-testable: names SPEC.md as the authority to read, which no test can observe.
  - S3 => P12
  - S4 => not-testable: a process rule for this delivery, answered by the conflict record and the pause report, not by a test.
  - S5 => not-testable: excludes a directory from the reading, which no test observes.
  - S6 => P12
  - S7 => not-testable: a commit message convention, read from the commit and not from the product.
  - S8 => not-testable: the attribution line of that same commit message convention.
  - S9 => P12
  - S10 => P12
  - S11 => P12
  - S12 => not-testable: states which features are already on the trunk this branch started from.
  - S13 => P1,P9
  - S14 => not-testable: repeats the process rule about stopping on a conflict with an existing test.
  - S15 => not-testable: shell quoting and submission hygiene for the recording tool, not product behaviour.
  - S16 => P1,P3
  - S17 => P4,P5,P6
  - S18 => P2
  - S19 => not-testable: a heading introducing the criteria that follow.
  - S20 => not-testable: the number of the first acceptance criterion.
  - S21 => P3
  - S22 => P2
  - S23 => not-testable: the number of the second acceptance criterion.
  - S24 => P4
  - S25 => P4
  - S26 => not-testable: the number of the third acceptance criterion.
  - S27 => P5
  - S28 => P5
  - S29 => not-testable: the number of the fourth acceptance criterion.
  - S30 => P7
  - S31 => P7
  - S32 => not-testable: the number of the fifth acceptance criterion.
  - S33 => P8
  - S34 => P8
  - S35 => not-testable: cites the authority lines the rule is read from.
  - S36 => P1
  - S37 => not-testable: names the dependency and the file shared with another feature.
  - S38 => P1
  - S39 => P1
  - S40 => not-testable: lists the files the work is expected to touch.
  - S41 => not-testable: continues the list of files the work is expected to touch.
  - S42 => P3,P4
  - S43 => P7
- **scenarios**:
  - SC1 | P1 | GIVEN the source "(defn f (sig ((n Int)) -> Int ! pure) (examples (example (f 1) => 1)) (/ n 1))" | WHEN the command checks it | THEN the status is "unsupported" and not "invalid_program"
  - SC2 | P2 | GIVEN that same source with "/" on line 4 | WHEN the command checks it | THEN the reason says "unsupported", says "core-0" and names division, placed at line 4
  - SC3 | P3 | GIVEN the source whose only body is "(/ n 1)" on line 4 | WHEN the command checks it | THEN no diagnostic says the name "/" is unbound, and the twin body "(* n 1)" is answered "completed"
  - SC4 | P4 | GIVEN a function whose body is the decimal literal 1.5, and one whose body is the text literal "ok" | WHEN each is checked | THEN each is "unsupported" naming the literal, and the twin whose body is 1 is "completed"
  - SC5 | P5 | GIVEN the in-profile program followed on line 6 by the call "(f 1)" | WHEN the command checks it | THEN the status is "unsupported", the reason says "top-level expression" and names f, and the same source without that call is "completed"
  - SC6 | P6 | GIVEN the same declaration written "(defspec f ...)" on line 1 | WHEN the command checks it | THEN the status is "unsupported" and the reason names "defspec" as a declaration form core-0 does not have
  - SC7 | P7 | GIVEN each of the 14 files in evidence/cases/ | WHEN each is checked | THEN each is "unsupported" naming its own construct, and each adaptation to core-0 is answered "completed" or "invalid_program", never "unsupported"
  - SC8 | P8 | GIVEN the source with the trailing call "(f 1)" | WHEN the command checks it | THEN the response has no "claim", no "result" and no "source_digest" key and none of the 9 words that would claim something was established
  - SC9 | P9 | GIVEN a caller that asks "discover" | WHEN it reads the manifest | THEN result.statuses names "unsupported" with a meaning saying "core-0" and "profile", and diagnostic_categories lists "unsupported_construct" beside the 7 already published
  - SC10 | P10 | GIVEN the source whose body is "(/ n 1)" | WHEN each of check, examples, verify and evaluate reads it | THEN all 4 answer "unsupported" with that one category and no result
  - SC11 | P11 | GIVEN examples/hour-clock.prova, conformance/add-one.prova, a body "(+ n missing-name)" and "(deftypo T (record (x Int)))" | WHEN each is checked | THEN the first 2 stay "completed" and the other 2 stay "invalid_program" with the categories unbound_name and syntax
  - SC12 | P12 | GIVEN the branch feat/f9 after the change | WHEN "uv run pytest -q tests" runs and "git status --short" runs | THEN all 932 existing tests and the new ones pass and the working tree is clean
- **conflicts**:
  - S1 | NONE | ran the suite command named here on the pre-feature tree: it collects and the baseline is green, so nothing contradicts it.
  - S2 | NONE | read SPEC.md lines 51-54, 79-80, 96-99 and 125-128: they require the unsupported refusal this feature adds.
  - S3 | NONE | the change adds test files and edits no existing test file and no line of SPEC.md.
  - S4 | NONE | read every test that asserts a status or a category for a source: none sends a source using a construct outside core-0.
  - S5 | NONE | the .relay directory is absent from this worktree and no test or source reads it.
  - S6 | NONE | all writes in this delivery are inside /Users/andrealaforgia/dev/prova-wt-f9 on branch feat/f9.
  - S7 | NONE | nothing in the repository constrains the commit message, so the required trailer can be written.
  - S8 | NONE | the worktree installs no commit hook, so the attribution line is written as given.
  - S9 | NONE | no step of this delivery pushes or merges; the branch stays local.
  - S10 | NONE | the baseline suite is green and the feature adds a status rather than changing an existing one.
  - S11 | NONE | the design puts the whole rule in syntax.py and service.py; checker.py is read but not edited.
  - S12 | NONE | the branch starts at 5024bf2, which carries the F5 and F6 tests and their source.
  - S13 | NONE | read service.DIAGNOSTIC_CATEGORIES and the manifest tests: the 7 named categories are published and the manifest has no status list yet to contradict.
  - S14 | NONE | the F6 malformed family, the F5 odd-binder family and the discover tests were each read; none uses an out-of-profile construct.
  - S15 | NONE | every nwstep submission in this delivery is passed from a script file with the arrows quoted.
  - S16 | NONE | division is answered today as unbound_name, which this sentence requires to change and no test asserts.
  - S17 | NONE | decimal, text, the four declaration words and the trailing expression are each answered today as syntax or unbound_name, and no existing test asserts any of them.
  - S18 | NONE | no existing test asserts the wording of a refusal for a source outside the profile.
  - S19 | NONE | a heading contradicts nothing the system does.
  - S20 | NONE | the number of a criterion contradicts nothing the system does.
  - S21 | NONE | checked the answer for a dividing program on the pre-feature tree: unbound_name, which no test asserts.
  - S22 | NONE | no existing test requires a refusal to leave the construct unnamed.
  - S23 | NONE | the number of a criterion contradicts nothing the system does.
  - S24 | NONE | checked the answers for 1.5 and for a text literal on the pre-feature tree: unbound_name and syntax, asserted by no test.
  - S25 | NONE | the unbound_name category stays owned by the checker for names core-0 does have.
  - S26 | NONE | the number of a criterion contradicts nothing the system does.
  - S27 | NONE | checked the answer for a trailing call on the pre-feature tree: the general top-level syntax refusal, asserted by no test.
  - S28 | NONE | the F6 malformed family keeps that general refusal for every shape it enumerates, none of which is a trailing expression.
  - S29 | NONE | the number of a criterion contradicts nothing the system does.
  - S30 | NONE | ran all 14 preserved files through the pre-feature tree and read evidence/README.md: no test reads them today.
  - S31 | NONE | every one of the 14 carries a construct core-0 does not have, so under this profile none can pass; recorded as DEC4 rather than as a contradiction with the system.
  - S32 | NONE | the number of a criterion contradicts nothing the system does.
  - S33 | NONE | an invalid_program answer already carries no claim and no result, so the new status can keep that shape.
  - S34 | NONE | no existing test requires a refused source to carry a digest or a claim.
  - S35 | NONE | read those SPEC.md lines: they say the three kinds of failure are distinct, which the new status implements.
  - S36 | NONE | the tool today has one refusal status for a readable source, which this sentence requires to be split and no test fixes.
  - S37 | NONE | F6 is already on the trunk, so syntax.py is free; F7 owns checker.py, which this change leaves alone.
  - S38 | NONE | the size declared in the workspace is already M, matching this sentence.
  - S39 | NONE | the status name is taken verbatim from this sentence, so no naming choice is left open.
  - S40 | NONE | the design touches exactly syntax.py and service.py and reads evidence/cases/ from the tests.
  - S41 | NONE | the change adds test files only and edits no existing one.
  - S42 | NONE | ran probes G4 and L5 by hand against the pre-feature tree: both disagree with SPEC.md exactly as the sentence says.
  - S43 | NONE | grepped the test tree for evidence/cases: no test reads the directory today.
- **decisions**:
  - DEC1: The status is spelled "unsupported" and the category "unsupported_construct", the status name taken verbatim from the request (S39) rather than chosen, so no naming question is open.
  - DEC2: A top-level form that is not a declaration is refused as a trailing top-level expression only when its head is recognisably an expression head - an operator, a special form, a selector, a capitalised constructor, or the name of a function the same source declares. A misspelled declaration word such as deftypo keeps the refusal it has today, because sending a reader to wait for a later profile when the repair is one letter is a worse answer.
  - DEC3: The manifest publishes a statuses map, every status the tool answers with and its one-line meaning, beside the operation and category lists it already publishes. A category alone would not tell a caller that a second refusal status exists.
  - DEC4: Every one of the 14 preserved files uses a construct core-0 does not have, so under this profile all 14 are refused and none passes. The half of criterion 4 that says the ones meant to pass pass is kept by deriving from each file a core-0 adaptation, by recorded substitutions on the file text, and requiring each adaptation to be answered by the ordinary rules and never as unsupported; 6 of them are accepted outright. The files themselves stay byte-for-byte unchanged as provenance.
  - DEC5: The profile boundary is decided in syntax.py, in one pass over the reader tree before the typed tree is built, so the out-of-profile answer precedes any spelling or checking refusal and all four source-reading operations get it from the one place they share. checker.py is not edited.
  - DEC6: Decimal and Text used as type names keep the unbound_type answer the checker gives them. A program may declare a record of either name today, and refusing the spelling everywhere would make a program that is valid now invalid. Recorded as a named limit of this feature.
  - DEC7: A value supplied as an evaluate argument keeps its malformed_value refusal. The profile boundary is read over source text; a supplied argument is not source.
  - DEC8: No formal model (Quint). The change is a pure function from one source text to one response, with no state, protocol, concurrency or crash behaviour for a model to describe.
- **mapping**:
  - P1 => test_a_program_that_divides_is_refused_as_outside_this_profile
  - P2 => test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands
  - P3 => test_a_program_that_divides_is_refused_as_outside_this_profile
  - P4 => test_a_decimal_literal_is_refused_as_outside_this_profile
  - P5 => test_a_call_after_the_declarations_is_refused_as_outside_this_profile
  - P6 => test_a_declaration_word_core_0_does_not_have_is_refused_as_outside_this_profile
  - P7 => test_every_preserved_counterexample_is_refused_for_the_construct_it_uses
  - P8 => test_an_out_of_profile_answer_claims_nothing_about_the_program
  - P9 => test_the_manifest_lists_the_status_and_the_category_this_rule_adds
  - P10 => test_every_out_of_profile_source_is_refused_the_same_way_by_every_operation
  - P11 => test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else
  - P12 => test_the_published_status_is_the_one_an_out_of_profile_source_gets
- **covers_scenarios**:
  - SC1 => test_a_program_that_divides_is_refused_as_outside_this_profile
  - SC2 => test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands
  - SC3 => test_a_program_that_divides_is_refused_as_outside_this_profile
  - SC4 => test_a_text_literal_is_refused_as_outside_this_profile
  - SC5 => test_a_call_after_the_declarations_is_refused_as_outside_this_profile
  - SC6 => test_a_declaration_word_core_0_does_not_have_is_refused_as_outside_this_profile
  - SC7 => test_every_preserved_counterexample_is_refused_for_the_construct_it_uses
  - SC8 => test_an_out_of_profile_answer_claims_nothing_about_the_program
  - SC9 => test_the_manifest_lists_the_status_and_the_category_this_rule_adds
  - SC10 => test_every_out_of_profile_source_is_refused_the_same_way_by_every_operation
  - SC11 => test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else
  - SC12 => test_the_published_status_is_the_one_an_out_of_profile_source_gets
- **predictions**:
  - SC1 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC7 => base differs
  - SC9 => base differs
  - SC11 => base held
- **interfaces**:
  - I1: the prova command JSON request and response over stdin and stdout for the operations that read source - check, examples, verify and evaluate.
  - I2: the discover operation of that same command, which answers the manifest a caller reads the vocabulary from.
- **matrix**:
  - I1.empty => the empty source, and a source holding only a comment => unchanged: invalid_program with the syntax category saying a declaration is missing
  - I1.unknown => an operation name the tool does not know => unchanged: unavailable with the unknown_operation category
  - I1.malformed => a source whose body is (/ n 1), 1.5 or "ok", or that ends with a call => unsupported with the unsupported_construct category naming the construct and its line
  - I1.dependency-gone => n/a: the operation reads one request from standard input and calls nothing outside the process
  - I1.repeated => the same out-of-profile source asked twice in two runs => the identical response both times; nothing is written and nothing is kept
  - I1.concurrent => n/a: one request per process and no file or shared state is touched, so two runs cannot meet
  - I1.crash => n/a: the command writes no file, so an interruption leaves nothing half written to recover
  - I2.empty => discover asked with no source field at all => unchanged: the manifest, now also listing the statuses the tool answers with
  - I2.unknown => discover asked with an unknown extra field => unchanged: the manifest, which reads no field but the operation
  - I2.malformed => a request body that is not JSON => unchanged: tool_failure with the reason from the JSON reader and exit 1
  - I2.dependency-gone => n/a: the manifest is built from the service own tables and reads no file
  - I2.repeated => discover asked twice => the identical manifest both times
  - I2.concurrent => n/a: the manifest is read only and holds no state two callers could share
  - I2.crash => n/a: discover writes nothing, so an interruption leaves nothing to recover
- **laws**:
  - LAW1 | For every construct core-0 does not have and every operation that reads source, the answer is the unsupported status carrying that category alone, with no claim and no result | generator=test_every_out_of_profile_source_is_refused_the_same_way_by_every_operation | observation=the status and the set of diagnostic categories of the JSON response, and the absence of the claim and result keys | mutant=one operation answers invalid_program with the syntax category
  - LAW2 | Every out-of-profile refusal names its construct and stands at the line and column the construct occupies | generator=test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands | observation=the words of the reason and the location of the diagnostic | mutant=the reason drops the construct name, or the refusal is placed at line 1
  - LAW3 | Each of the fourteen preserved counterexamples is refused for the construct it uses, and the same case written with only what core-0 has is answered by the ordinary rules and never as unsupported | generator=test_every_preserved_counterexample_is_refused_for_the_construct_it_uses | observation=the status and the reason for each file, and the status and categories for its derived adaptation | mutant=every source is refused as unsupported
  - LAW4 | A source gets the unsupported status exactly when it uses a construct core-0 does not have: everything core-0 already accepted is still accepted and every mistake it refused keeps its own categories | generator=test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else | observation=the status and the categories for the shipped programs, an unbound name, a misspelled declaration word and each out-of-profile source | mutant=every top-level form that is not a declaration is called an out-of-profile expression
- **messages**:
  - MSG1 | a function whose body is (/ n 1) | division is unsupported in the core-0 profile | core-0 declares no division operator, so the tool can give / no meaning here | write the calculation with an operator core-0 has, + - or *, and name the line and column it stands at | test=test_a_program_that_divides_is_refused_as_outside_this_profile
  - MSG2 | a function whose body is 1.5 | the decimal literal 1.5 is unsupported in the core-0 profile | the core-0 literals are true, false, the unit value and whole numbers | write a whole number, such as 1, at the line and column named | test=test_a_decimal_literal_is_refused_as_outside_this_profile
  - MSG3 | a function whose body is the text literal "ok" | the text literal "ok" is unsupported in the core-0 profile | core-0 has no text values and no text operators | remove it, or carry the information as a declared type core-0 has | test=test_a_text_literal_is_refused_as_outside_this_profile
  - MSG4 | the in-profile program followed by the call (f 1) | a top-level expression calling f is unsupported in the core-0 profile | core-0 writes only deftype and defn forms at the top level, so a trailing call has no place to run | move the call into a function body, or ask for it with the evaluate operation | test=test_a_call_after_the_declarations_is_refused_as_outside_this_profile
  - MSG5 | a declaration written (defspec f ...) | the declaration form defspec is unsupported in the core-0 profile | core-0 declares only deftype and defn | write the declaration as (defn name (sig (parameters) -> Type ! pure) (examples ...) body) | test=test_a_declaration_word_core_0_does_not_have_is_refused_as_outside_this_profile
- **red**: `uv run pytest -q tests/acceptance/test_f9_b1_division_is_refused_as_unsupported.py tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py tests/acceptance/test_f9_b3_a_trailing_top_level_expression_is_refused_as_unsupported.py tests/acceptance/test_f9_b4_a_preserved_counterexample_is_refused_as_unsupported.py tests/acceptance/test_f9_b5_an_unsupported_refusal_claims_nothing_more.py tests/acceptance/test_f9_b6_the_manifest_publishes_the_unsupported_answer.py tests/properties/test_f9_out_of_profile_source.py` exited 1 in 2.42s
  - failing on the pre-feature tree (14): tests/acceptance/test_f9_b1_division_is_refused_as_unsupported.py::test_a_program_that_divides_is_refused_as_outside_this_profile, tests/acceptance/test_f9_b1_division_is_refused_as_unsupported.py::test_a_declaration_word_core_0_does_not_have_is_refused_as_outside_this_profile, tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py::test_a_decimal_literal_is_refused_as_outside_this_profile, tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py::test_a_decimal_literal_in_a_declared_example_is_refused_as_outside_this_profile, tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py::test_a_text_literal_is_refused_as_outside_this_profile, tests/acceptance/test_f9_b3_a_trailing_top_level_expression_is_refused_as_unsupported.py::test_a_call_after_the_declarations_is_refused_as_outside_this_profile, tests/acceptance/test_f9_b4_a_preserved_counterexample_is_refused_as_unsupported.py::test_a_preserved_counterexample_is_refused_by_the_command_as_out_of_profile, tests/acceptance/test_f9_b5_an_unsupported_refusal_claims_nothing_more.py::test_an_out_of_profile_answer_claims_nothing_about_the_program, tests/acceptance/test_f9_b6_the_manifest_publishes_the_unsupported_answer.py::test_the_manifest_lists_the_status_and_the_category_this_rule_adds, tests/acceptance/test_f9_b6_the_manifest_publishes_the_unsupported_answer.py::test_the_published_status_is_the_one_an_out_of_profile_source_gets, tests/properties/test_f9_out_of_profile_source.py::test_every_out_of_profile_source_is_refused_the_same_way_by_every_operation, tests/properties/test_f9_out_of_profile_source.py::test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands, tests/properties/test_f9_out_of_profile_source.py::test_every_preserved_counterexample_is_refused_for_the_construct_it_uses, tests/properties/test_f9_out_of_profile_source.py::test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else
  - tests (read from the run): 14 failed, 3 passed in 1.63s
  ```text
          )
          response = _answer_for("check", source, described)
          answered = {d.get("category") for d in response.get("diagnostics") or []}

          if out_of_profile:
  >           assert response.get("status") == UNSUPPORTED_STATUS, (
                  f"WHAT: {described} is answered {response.get('status')!r}, not "
                  f"{UNSUPPORTED_STATUS!r}: {response}. "
                  "WHY: it uses a construct core-0 does not have. "
                  "HOW: refuse it at the profile boundary."
              )
  E           AssertionError: WHAT: a decimal literal is answered 'invalid_program', not 'unsupported': {'operation': 'check', 'status': 'invalid_program', 'diagnostics': [{'category': 'unbound_name', 'reason': "unbound name '1.5'", 'location': {'line': 4, 'column': 3}}]}. WHY: it uses a construct core-0 does not have. HOW: refuse it at the profile boundary.
  E           assert 'invalid_program' == 'unsupported'
  E
  E             - unsupported
  E             + invalid_program
  E           Failing test case: test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else(
  E               described='a decimal literal',
  E           )
  E           Explanation:
  E               These lines were always and only run by failing test cases:
  E                   /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f9/red-tree/tests/properties/test_f9_out_of_profile_source.py:238

  tests/properties/test_f9_out_of_profile_source.py:246: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f9_b1_division_is_refused_as_unsupported.py::test_a_program_that_divides_is_refused_as_outside_this_profile
  FAILED tests/acceptance/test_f9_b1_division_is_refused_as_unsupported.py::test_a_declaration_word_core_0_does_not_have_is_refused_as_outside_this_profile
  FAILED tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py::test_a_decimal_literal_is_refused_as_outside_this_profile
  FAILED tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py::test_a_decimal_literal_in_a_declared_example_is_refused_as_outside_this_profile
  FAILED tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py::test_a_text_literal_is_refused_as_outside_this_profile
  FAILED tests/acceptance/test_f9_b3_a_trailing_top_level_expression_is_refused_as_unsupported.py::test_a_call_after_the_declarations_is_refused_as_outside_this_profile
  FAILED tests/acceptance/test_f9_b4_a_preserved_counterexample_is_refused_as_unsupported.py::test_a_preserved_counterexample_is_refused_by_the_command_as_out_of_profile
  FAILED tests/acceptance/test_f9_b5_an_unsupported_refusal_claims_nothing_more.py::test_an_out_of_profile_answer_claims_nothing_about_the_program
  FAILED tests/acceptance/test_f9_b6_the_manifest_publishes_the_unsupported_answer.py::test_the_manifest_lists_the_status_and_the_category_this_rule_adds
  FAILED tests/acceptance/test_f9_b6_the_manifest_publishes_the_unsupported_answer.py::test_the_published_status_is_the_one_an_out_of_profile_source_gets
  FAILED tests/properties/test_f9_out_of_profile_source.py::test_every_out_of_profile_source_is_refused_the_same_way_by_every_operation
  FAILED tests/properties/test_f9_out_of_profile_source.py::test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands
  FAILED tests/properties/test_f9_out_of_profile_source.py::test_every_preserved_counterexample_is_refused_for_the_construct_it_uses
  FAILED tests/properties/test_f9_out_of_profile_source.py::test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else
  14 failed, 3 passed in 1.63s
  ```

## 3. design: Find the owners and design the change (revision 1)

- **owners**:
  - how source text becomes a parenthesised tree carrying the place of every token => src/prova/reader.py, reused unchanged
  - how a core-0 name, marker and declaration is spelled, and the typed tree they build => src/prova/syntax.py
  - what core-0 does not have at all, read over one source => new: no file decides it today. syntax.py owns what core-0 does have, so the boundary of the profile lives beside it, in the one call every operation that reads source already makes
  - whether a name resolves, whether types agree, whether a declaration repeats => src/prova/checker.py, read but not edited (F7 owns that file)
  - which status, which category and which claim every answer carries, and the manifest that publishes them => src/prova/service.py
  - how an operation answers a source it cannot check => src/prova/service.py, where the four source-reading operations repeat it today and one owner will hold it after the prefactor
  - the fourteen preserved counterexamples and the core-0 adaptation of each => tests/acceptance/_f9_profile_fixtures.py
- **reuse_decision**: Reused: the reader unchanged, including the line and column it already carries for every token, so no refusal has to re-find a place; MarkerToken and AtLeastOne as the shape every new value object copies, so syntax.py keeps one way of saying "core-0 fixes this and here is the repair"; the existing diagnostic builder and location shape in service.py; checker.py untouched. Created new: OutOfProfileConstruct, UnsupportedConstruct and ProfileBoundary in syntax.py, because no existing owner answers "what does core-0 not have at all" - ValueName and TypeName answer how a name is spelled, MarkerToken answers which token stands at a grammar position, and the checker answers what a name means once the tree exists; all three presuppose a construct the profile has. Created new in service.py: Refusal, the one answer for a source that is not a checkable program, extracted from the four operations that repeat it today so the new status is decided in one place instead of four.
- **paradigm**: oo
- **boundaries**:
  - reader -> syntax: the parenthesised tree with its places. Owned by syntax.py, which now reads the profile boundary over that tree before building the typed tree, so an out-of-profile source never reaches the typed tree or the checker.
  - syntax -> service: two refusal types now cross it, SyntaxError_ for a source core-0 cannot read and UnsupportedConstruct for a source core-0 does not define. service.py translates each into one status; no exception type reaches a caller.
  - service -> the command: one JSON response per request. The four operations that read source answer through one Refusal owner, so they cannot drift apart.
  - service -> a caller reading the manifest: discover publishes the statuses and the diagnostic categories, so the vocabulary is learned from the tool and not from a document.
  - the evaluate argument path stays outside this boundary: _parse_value_text reads a supplied value with parse_value, not parse_program, so a supplied argument keeps its malformed_value refusal (DEC7).
- **domain_types**:
  - OutOfProfileConstruct (new, syntax.py): one construct core-0 does not have - how to say what is absent and how to repair it. Mirrors MarkerToken, the existing owner of "one token core-0 fixes", and builds its own refusal rather than letting callers compose a sentence.
  - UnsupportedConstruct (new, syntax.py): the refusal itself, carrying the construct it names and the line and column it stands at. It refuses to be built without a construct name, so a refusal that does not say what to repair cannot exist.
  - ProfileBoundary (new, syntax.py): what core-0 does not have, read over one source. It holds the function names that source declares, which is what lets it tell a trailing call from a declaration word the reader cannot place (DEC2).
  - Refusal (new, service.py): the one answer every operation that reads source gives when the source is not a program it can check - a status and its diagnostics, and nothing else. It has no field for a claim, a result or a source digest, so an out-of-profile answer cannot carry one.
  - The manifest gains a statuses map: every status service.handle answers with and its one-line meaning (DEC3, owner accepted).
- **invariants**:
  - INV1 | A source using a construct core-0 does not have never reaches the typed tree or the checker: the profile boundary is read first, over the reader tree, inside the one call every source-reading operation makes | witness=src/prova/syntax.py:ProfileBoundary | bypass=a caller that calls parse_expr or parse_value directly is not scanned; that is the evaluate argument path, which keeps malformed_value by DEC7
  - INV2 | All four operations that read source answer an out-of-profile source identically, because one owner builds that answer and each operation only names itself | witness=src/prova/service.py:Refusal | bypass=none
  - INV3 | An out-of-profile answer carries no claim, no result and no source digest: the type that builds it has no field for any of them | witness=src/prova/service.py:Refusal | bypass=none
  - INV4 | Every out-of-profile refusal names its construct and the place it stands at: the refusal cannot be built with an empty construct name | witness=src/prova/syntax.py:UnsupportedConstruct | bypass=none
  - INV5 | The unsupported answer is given to a construct core-0 does not have and to nothing else: a misspelled declaration word keeps the refusal it has today, and every source core-0 already accepted stays accepted | witness=src/prova/syntax.py:ProfileBoundary | bypass=none
- **prefactoring**: yes
- **prefactoring_reason**: The four source-reading operations (check, verify, examples, evaluate) each repeat the same four steps - read, parse, check, and build the same two refusals - so a new status added where they stand would be written four times and could drift in three. One commit first extracts that repeated sequence into a single Refusal owner in service.py, with no test edited and no response changed: the status, the diagnostics and their order are the ones the four operations already build, so the suite that pins them stays green. The feature commit then adds the new status in that one place, which is what makes INV2 hold by construction rather than by four copies agreeing.

## 4. craft: Craft the change (revision 1)

- **refactor_commits**:
  - 3bc187d
- **refactor_check**: the check ran on the parent and on each refactor commit
  - 3bc187d9e97b (Let one owner answer a source the tool cannot check): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 103.075s
  - tests (read from the run): 949 passed in 102.93s
  - slowest: 6.34s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.12s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.64s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.12s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.49s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.84s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.53s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.40s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.34s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 1.33s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  7%]
  ........................................................................ [ 15%]
  ........................................................................ [ 22%]
  ........................................................................ [ 30%]
  ........................................................................ [ 37%]
  ........................................................................ [ 45%]
  ........................................................................ [ 53%]
  ........................................................................ [ 60%]
  ........................................................................ [ 68%]
  ........................................................................ [ 75%]
  ........................................................................ [ 83%]
  ........................................................................ [ 91%]
  ........................................................................ [ 98%]
  .............                                                            [100%]
  ============================= slowest 10 durations =============================
  6.34s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.12s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.64s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.12s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.49s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.84s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.53s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.40s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.34s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1.33s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  949 passed in 102.93s (0:01:42)
  ```
- **scorecard**: `uvx ruff check --output-format=concise src tests docs` exited 1 in 0.298s
  ```text
  tests/properties/test_i1_s4_p1_structural.py:12:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s4_p2_comparison.py:8:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s4_p3_full_evidence.py:7:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s4_p4_full_evidence.py:8:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s4_p5_documented_semantics.py:76:9: ISC004 Unparenthesized implicit string concatenation in collection
  tests/properties/test_i1_s4_p5_documented_semantics.py:89:105: FURB167 [*] Use of regular expression alias `re.I`
  tests/properties/test_i1_s4_p5_twelve_controls.py:8:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s4_p7_pinned_snapshots.py:9:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_match_exhaustiveness_property.py:19:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_p2.py:13:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_p3.py:20:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_p4.py:19:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_p4.py:50:12: PIE810 Call `startswith` once with a `tuple`
  tests/properties/test_i1_s5_p5.py:12:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_p6.py:16:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_p7.py:8:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_p8.py:7:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s5_p8.py:14:5: F401 [*] `_i1_s5_b5_fixtures.OPERATIONS` imported but unused
  tests/properties/test_i1_s5_p8.py:15:5: F401 [*] `_i1_s5_b5_fixtures.PLACEMENTS` imported but unused
  tests/properties/test_i1_s5_p8.py:38:33: UP031 Use format specifiers instead of percent format
  tests/properties/test_i1_s5_p9.py:7:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s6_p1.py:14:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s6_p2.py:13:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s6_p3.py:14:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s6_p5.py:19:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s6_p5_representations.py:16:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s6_p7.py:11:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s6_p8.py:17:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_i1_s6_p8.py:20:24: F401 [*] `hypothesis.example` imported but unused
  tests/properties/test_i1_s6_p8.py:103:5: RUF059 Unpacked variable `state_ctor` is never used
  tests/properties/test_i1_s6_p8_interleaved.py:7:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_obligation_inventory_laws.py:61:42: UP037 [*] Remove quotes from type annotation
  tests/properties/test_obligation_inventory_laws.py:167:12: PLW1510 `subprocess.run` without explicit `check` argument
  tests/properties/test_s1_b2_no_forbidden_claim_property.py:20:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_s1_b2_no_forbidden_claim_property.py:104:12: PLW1510 `subprocess.run` without explicit `check` argument
  tests/properties/test_s1_b2_no_forbidden_claim_property.py:134:5: RUF059 Unpacked variable `returncode` is never used
  tests/properties/test_s5_b2_checker_node_kinds_property.py:17:1: I001 [*] Import block is un-sorted or un-formatted
  tests/properties/test_s5_b2_type_mismatch_property.py:25:1: I001 [*] Import block is un-sorted or un-formatted
  Found 158 errors.
  [*] 111 fixable with `--fix` (11 unsafe fixes available with `--fix --unsafe-fixes`).
  ```
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from the environment; the client was run from a shell command and exited 3. The four open questions (status name, the top-level rule, how the manifest publishes the status, how to read acceptance criterion 4) were decided locally and recorded as DEC1-DEC4, and the owner accepted them at the oracle pause.

## 5. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the change is the design: ProfileBoundary reads the boundary before the typed tree (syntax.py:330), the four operations share one Refusal (service.py:198), checker.py is untouched, and DEC2, DEC6 and DEC7 are each visible in the code they describe.
  - D2: pass - the five constructs core-0 lacks are declared once as OutOfProfileConstruct values and read nowhere else; the fourteen preserved cases and their adaptations are described once in tests/acceptance/_f9_profile_fixtures.py and loaded from there by the property module rather than copied.
  - D3: pass - the reader is unchanged, syntax.py raises and service.py translates; no exception type reaches a caller and nothing in syntax.py knows about statuses, categories or JSON.
  - D4: fixed:src/prova/syntax.py:46 UnsupportedConstruct now carries the OutOfProfileConstruct itself rather than a name copied out of it, so an empty construct name cannot exist and the unreachable guard the reviewer found is gone; Refusal (service.py:198) has no field for a claim, a result or a digest, so an out-of-profile answer cannot carry one.
  - D5: fixed:src/prova/syntax.py:373 _is_an_expression had grown a fourth answer it got wrong (a non-symbol head); it now answers one question in guard clauses with no else, one indentation level per branch. ProfileBoundary holds one instance variable, OutOfProfileConstruct three like its sibling MarkerToken, and that deliberate break is recorded in the design.
  - D6: pass - no pattern was added. The two-case union of Refusal and Program is read with isinstance, the way syntax.py already reads RecordType against UnionType; a visitor or a strategy here would be an abstraction for one caller.
  - D7: pass - the words are the domain language of SPEC.md: profile, construct, unsupported, out of profile, declaration form, top-level expression. No Manager, Helper or Data, and no abbreviation.
  - D8: pass - no infrastructure was added. The boundary reads a tree already in memory, writes nothing, reads no file, no clock and no environment, so there is nothing to inject.
  - D9: fixed:every check drives the published surface: the real prova command over stdin and stdout in the acceptance tests (tests/acceptance/test_f9_b1_division_is_refused_as_unsupported.py:28), and service.handle, the public API the other property modules already use, for the generated families. The review found one gap of this kind - the construct field was reachable from the surface but observed by nothing - and tests/properties/test_f9_out_of_profile_source.py:91 and the preserved-case law now pin it.
  - D10: pass - each file and function says what a reader gets, in their words: a_trailing_top_level_expression_is_refused_as_unsupported, a_misplaced_parenthesis_keeps_the_refusal_it_has_today. No production symbol and no process id appears in a name.
  - D11: pass - the helpers assert_unsupported_naming, assert_refused_at and assert_answered_without_the_unsupported_status carry the sentence a failure needs, so the tests themselves read as the promise; the adaptation of each preserved file is derived from that file by recorded substitutions that refuse to apply silently.
  - D12: fixed:four laws are generated over closed families rather than written out: 9 constructs crossed with the 4 operations that read source (tests/properties/test_f9_out_of_profile_source.py:91), the construct name and place, the fourteen preserved cases with their adaptations, and the partition law. The partition law was the fix for review finding 1: it now draws from both families and holds that the new answer is given to out-of-profile sources and to nothing else.
  - D13: pass - measured, not guessed: nine consecutive runs of the new checks, 17 passed each time with median 1.07s and slowest 1.09s, now 19 checks in 1.07s; the slowest single new test is 0.08s and every generated law is 0.02s or less because it asks the service in process. No sleep and no clock anywhere in them.
  - D14: pass - each refusal family is observed once through the command and once by the law that generates it, and the two differ on purpose: the first proves the real command carries the answer, the second proves it holds over the whole family. The fourteen preserved cases are walked by one law, not fourteen tests.
  - D15: fixed:every refusal says what, why and how with the offending token and its place: src/prova/syntax.py:285 gives division its absence and its repair, and the location and construct fields carry the facts a caller reads without prose. The review found the opposite defect in finding 1 - a how no reader could follow, because moving a parenthesis cannot repair a profile - and that source now keeps the refusal that can be followed.
  - D16: n/a: the change is a pure function from one source text to one response. No model for the profile boundary: there is no shared state, no multi-step protocol, no concurrency and no crash window for a model to describe, and the totality law is checked by the generated properties instead.
  - D17: fixed:docs/feature/f9/craft.md now carries the commit ids after the rebase, 981 green rather than 949, and the four review findings with the probe that proves each fix; docs/spec-trace.md says its table is a snapshot older than the code and names the two rows F9 changed; probe.py counted only invalid_program as a refusal and now counts both refusing statuses.
- **independent_review**:
  - REV1 | reviewer=implementation-review | findings=4 (verdict REJECT at 1ea859a): 1 HIGH, a valid defn wrapped in one pair of parentheses too many, ((f) 1) and () moved from the syntax refusal to unsupported, offering a remedy no respelling can follow; 2 MEDIUM, the construct response field had no observation and deleting it kept every test green; 3 MEDIUM, the empty-name guard in UnsupportedConstruct was unreachable and unobserved; 4 LOW, the manifest did not say that its list of statuses covers an answered request, while tool_failure is answered by the command wrapper. All other criteria passed, 949 green at that candidate. | resolution=all four fixed in 5701c86, rebased onto 903f420 as 5701c86 with the record corrected in feb8130. A form whose head is not a symbol is no longer read as an expression and keeps the syntax refusal, with 3 controls pinning it; one observation per construct family pins the now-stable construct tokens; the guard is deleted and UnsupportedConstruct carries the OutOfProfileConstruct itself; the manifest states what its status list covers and a check pins that sentence. Each fix was probed by putting the defect back: 2 tests red for finding 1, 2 for finding 2, 13 for finding 3, 1 for finding 4. Full suite 981 passed after the rebase.

## 6. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
  - A source that uses something core-0 does not have - division, a decimal or text literal, defspec, fn, trust, module, or a call written after the declarations - is now refused with its own status, unsupported, beside invalid_program.
  - One says this program breaks a rule of core-0; the other says this is not a program of this profile, which is the distinction SPEC.md asks for and the tool could not make before: division was an unbound name, a decimal literal was an unbound name or "not a value", a trailing call was a form the reader could not place.
  - That single point exists because a prefactoring commit put it there first, behaviour unchanged.
  - The manifest now publishes the statuses an answered request carries, so a caller reads the vocabulary from the tool.
  - The fourteen counterexamples preserved in evidence/cases/ are wired into the checks for the first time.
- **not_verified**:
  - Only the first out-of-profile construct in a source is reported. A reader repairing a file that uses several must run the tool again after each. The owner accepted this as a stated limit.
  - Decimal and Text written as type names are still answered unbound_type, not unsupported (DEC6). A program may declare a record of either name today, and refusing the spelling would make a program that is valid now invalid. A signature naming Decimal with no decimal literal in it therefore still gets the older, less honest answer.
  - A value supplied as an evaluate argument keeps its malformed_value refusal (DEC7). The boundary is read over source text only; nothing checks a supplied argument against the profile.
  - A trailing call to a function the source does not declare keeps the older spelling refusal (DEC2), because nothing in the source tells it apart from a misspelled declaration word.
  - The tool_failure status the command answers an unreadable request with is not in the published statuses; the manifest says what its list covers instead. Nothing checks the command wrapper itself against that sentence.
  - The refactor check that ran on the exported trees is tests/unit, not the whole suite: fifteen existing tests read the repository git history, which an exported tree does not have, so they fail there identically before and after. The whole-suite evidence for the prefactoring commit was run in the worktree instead and is recorded in docs/feature/f9/craft.md. That pre-existing coupling of tests to git history was reported, not repaired.
  - The craft step was recorded before the rebase onto 903f420 and names the commit ids of that time. Re-recording it refuses, because the workspace baseline is still 5024bf2 and the history from that base now starts with the F7 commits. docs/feature/f9/craft.md carries both the pre-rebase and post-rebase numbers; the journal entry is stale on ids only.
  - Jev was never reached: TYPESAFE_API_KEY is absent from this environment and the client exits 3. The four questions it would have been asked were decided locally as DEC1-DEC4 and accepted by the owner.
  - No formal model was written. The change is a pure function from one source text to one response, with no shared state, protocol, concurrency or crash window for a model to describe.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit feb813052d4cacdc8216729c15cf29607c55fcfd
  - no checks declared

## Not backed by the diff

- The refusal names the construct, says core-0 has no such thing, gives a repair a reader can follow, and points at the line and column it stands on.: a guarantee names no test function of the change
- The boundary is read over the reader tree before the typed tree is built, so nothing can answer first, and it is read inside the one call every source-reading operation makes, so check, examples, verify and evaluate cannot drift apart.: a guarantee names no test function of the change
- All fourteen are outside core-0, so all fourteen are refused; the half of the criterion about files that pass is kept by deriving a core-0 adaptation of each from its own text and requiring the ordinary rules, never the new status, to answer it.: a guarantee names no test function of the change
- An independent review rejected the first candidate with four findings, all fixed and each probed by putting the defect back.: a guarantee names no test function of the change
- The one that mattered: a valid declaration wrapped in one pair of parentheses too many was being told core-0 will never have what it wrote - untrue, and a remedy no respelling can follow.: a guarantee names no test function of the change
- A form whose head is not a symbol is no longer read as an expression and keeps the refusal that owns it.: a guarantee names no test function of the change
