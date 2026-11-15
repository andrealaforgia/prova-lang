# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 962 tests, all green on main).
  - not-testable (challenge this): names the project and the command that runs its suite, not a behaviour of the tool
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority the promises are read from
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on this change, not an outcome a reader of the tool can observe
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): tells the executor what to do with a conflict; the conflict table below answers it
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): excludes a directory from this work, observable in no answer of the tool
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): says where the change is made, not what the tool does
- S7: Commit with a message ending in the line
  - not-testable (challenge this): prescribes the commit message, observable only in the repository history
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line of that commit message, again history and not behaviour
- S9: Do not push and do not merge.
  - not-testable (challenge this): forbids publishing the branch, which no answer of the tool shows
- S10: Keep the full suite green.
  - not-testable (challenge this): the whole suite staying green is a delivery obligation the verification command observes, not a promise of the tool
- S11: Another delivery (F9, unsupported-source status, src/prova/syntax.py and service.py) runs in parallel in a different worktree; do not touch syntax.py or service.py unless you must publish a category (then keep the change to one line).
  - not-testable (challenge this): limits which files this change may touch; the design step records how it is kept
- S12: F5, F6 and F7 are already on main; read how they are built in checker.py.
  - not-testable (challenge this): points at the features already delivered, read for how the checker is built
- S13: Scripts: keep them in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): says where the executor keeps its scripts
- S14: Existing categories include cyclic_dependency, duplicate_declaration, recursive_type, shadowed_binding and reserved_name; reuse one if it fits, else name a new published category with the reason in your oracle note.
  - promises: P5
  - tests P5: test_the_word_for_an_example_about_another_function_is_published
- S15: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): tells the executor how to quote its own commands in this shell
- S16: **Outcome.** An example that calls some other function no longer counts as that
  - promises: P1
  - tests P1: test_an_example_calling_a_different_function_is_refused_naming_both
- S17: function's example.
  - promises: P1
  - tests P1: test_an_example_calling_a_different_function_is_refused_naming_both
- S18: **Acceptance criteria**
  - not-testable (challenge this): a heading above the criteria that follow
- S19: 1.
  - not-testable (challenge this): the number of the first criterion, carrying no outcome of its own
- S20: Given a function whose only example calls a different function, when the program
  - promises: P1
  - tests P1: test_an_example_calling_a_different_function_is_refused_naming_both
- S21: is checked, then it is invalid and the diagnostic names both functions.
  - promises: P1
  - tests P1: test_an_example_calling_a_different_function_is_refused_naming_both
- S22: 2.
  - not-testable (challenge this): the number of the second criterion, carrying no outcome of its own
- S23: Given an example calling a function that does not exist, then it is invalid.
  - promises: P2
  - tests P2: test_an_example_naming_a_function_that_does_not_exist_is_refused
- S24: 3.
  - not-testable (challenge this): the number of the third criterion, carrying no outcome of its own
- S25: Given an example whose argument count does not match the function, then it is
  - promises: P3
  - tests P3: test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked
- S26: invalid at check time, not only when examples run.
  - promises: P3
  - tests P3: test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked
- S27: 4.
  - not-testable (challenge this): the number of the fourth criterion, carrying no outcome of its own
- S28: Given a function with one correct self-calling example, then it is accepted.
  - promises: P4
  - tests P4: test_a_program_is_accepted_exactly_when_every_example_is_about_its_own_function
- S29: **SPEC.md** lines 228-234.
  - not-testable (challenge this): cites the lines of SPEC.md the rule is read from
- S30: **Dependencies** none (serial with F3, F4, F5, F7).
  - not-testable (challenge this): states that this work waits for no other delivery
- S31: **Size** S.
  - not-testable (challenge this): declares the size of the delivery, recorded in the workspace
- S32: **Touches** `src/prova/checker.py`, tests.
  - not-testable (challenge this): names the files the change is expected to touch
- S33: **Why it is a real expectation** probe C3 disagrees today.
  - not-testable (challenge this): states that the tool disagrees today, which the recorded RED run shows

## Edge matrix

- I1.empty: a source of 0 characters => invalid_program for core-0 asking for at least 1 declaration, never with the new word | self-probe: not probed | pre-feature not probed
- I1.unknown: an example of "double" naming "treble", which the program never declares => invalid_program, 1 refusal naming "double" and "treble" | self-probe: not probed | pre-feature not probed
- I1.malformed: a source whose (examples ... clause is never closed => the reading refusal syntax alone, reached before any rule about examples | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the check reads only the source in the request and no other store, file or service
- I1.repeated: 2 examples of "double" both calling "triple" => 2 refusals, 1 for each example | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): 1 request is read, answered and forgotten; 2 runs share no state
- I1.crash: an example writing 0 of the 1 arguments its function takes => invalid_program; the check evaluates no example, so none can end it | self-probe: not probed | pre-feature not probed
- I2.empty: a source of 0 characters => invalid_program and 0 example outcomes | self-probe: not probed | pre-feature not probed
- I2.unknown: an example naming the undeclared "treble" => invalid_program and 0 example outcomes, instead of an outcome about another function | self-probe: not probed | pre-feature not probed
- I2.malformed: the unclosed (examples ... clause => the same reading refusal, 0 example outcomes | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): the operation reads only the source in the request
- I2.repeated: 2 examples of "double" both calling "triple" => invalid_program with 2 refusals and 0 example outcomes | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): each request is answered in its own process from its own source; nothing is shared
- I2.crash: an example writing 0 of the 1 arguments its function takes, which ended the command before => exit 0 with 1 JSON refusal | self-probe: not probed | pre-feature not probed
- I3.empty: a request carrying no source at all => the manifest, whose list of categories names the new word | self-probe: not probed | pre-feature not probed
- I3.unknown: n/a (challenge this): discover reads no program, so no unknown name can reach it
- I3.malformed: n/a (challenge this): discover reads no source text at all
- I3.dependency-gone: n/a (challenge this): the manifest is built from the tool tables alone, with nothing to be gone
- I3.repeated: asking discover 2 times => the same list both times, naming the new word 1 time in each | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): the manifest is read-only and keeps no state between requests
- I3.crash: n/a (challenge this): discover writes nothing, so an interrupted run leaves nothing behind to repair

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN a program declaring "double" and "triple", whose only example of "double" is (example (triple 2) => 6)
  - WHEN the program is checked
  - THEN the answer is invalid_program with 1 refusal, and that refusal names "double" and "triple"
  - test: test_an_example_calling_a_different_function_is_refused_naming_both
- SC2 (P1): not-held (no held self-probe case)
  - GIVEN the same "double" declaring 2 examples, both of them (example (triple ...) => ...)
  - WHEN the program is checked
  - THEN the answer carries 2 refusals, 1 for each example, so no wrong example is hidden
  - test: test_two_examples_about_another_function_are_both_reported
- SC3 (P2): not-held (no held self-probe case)
  - GIVEN a program declaring only "double", whose example is (example (treble 2) => 4) and no "treble" anywhere
  - WHEN the program is checked
  - THEN the answer is invalid_program and the refusal names "double" and "treble"
  - test: test_an_example_naming_a_function_that_does_not_exist_is_refused
- SC4 (P3): not-held (no held self-probe case)
  - GIVEN "double", which takes 1 parameter, whose example is (example (double 2 3) => 4)
  - WHEN the program is checked
  - THEN the answer is invalid_program and the refusal says the example passes 2 arguments where 1 was expected
  - test: test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked
- SC5 (P3): not-held (no held self-probe case)
  - GIVEN the same "double" whose example is (example (double) => 4), which ended the command before
  - WHEN the declared examples are asked to run
  - THEN the command exits 0 with 1 JSON answer saying invalid_program and reports 0 example outcomes
  - test: test_asking_for_the_examples_of_a_program_with_too_few_arguments_is_answered
- SC6 (P4): not-held (no held self-probe case)
  - GIVEN "double" whose example is (example (double 2) => 4), beside "triple" with its own example
  - WHEN the program is checked
  - THEN the answer is completed with 0 diagnostics
  - test: test_a_program_is_accepted_exactly_when_every_example_is_about_its_own_function
- SC8 (P2): not-held (no held self-probe case)
  - GIVEN "double" whose only example is (example (Box 3) => 4), where "Box" is a declared constructor and no function
  - WHEN the program is checked
  - THEN the answer is invalid_program and the refusal says "Box" is not a function this program declares, offering no move of the example to it
  - test: test_an_example_calling_a_declared_constructor_is_refused_the_same_way
- SC7 (P5): not-held (no held self-probe case)
  - GIVEN a client that has read 0 refusals of this tool so far
  - WHEN it asks the tool what it answers with
  - THEN the published list of categories names "unrelated_example", the 1 word an example about another function carries
  - test: test_the_word_for_an_example_about_another_function_is_published

## Questions for the owner

- none

## Observed side effects (git, BASE to HEAD)

- A docs/f9-out-of-profile/DECISIONS.md (+20 -0 lines)
- A docs/f9-out-of-profile/SUMMARY.md (+671 -0 lines)
- A docs/f9-out-of-profile/TRACE.md (+6 -0 lines)
- A docs/feature/f9/craft.md (+103 -0 lines)
- A docs/feature/f9/design.md (+106 -0 lines)
- A docs/feature/f9/oracle.md (+98 -0 lines)
- A docs/feature/function-examples/craft.md (+112 -0 lines)
- A docs/feature/function-examples/oracle.md (+94 -0 lines)
- A docs/feature/function-examples/selfreview.md (+35 -0 lines)
- A docs/function-examples/DECISIONS.md (+13 -0 lines)
- A docs/function-examples/SUMMARY.md (+406 -0 lines)
- A docs/function-examples/TRACE.md (+5 -0 lines)
- M docs/spec-trace.md (+9 -0 lines)
- M docs/spec-trace/probe.py (+5 -1 lines)
- M src/prova/checker.py (+114 -2 lines)
- M src/prova/service.py (+114 -68 lines)
- M src/prova/syntax.py (+206 -0 lines)
- A tests/acceptance/_f8_example_subject_fixtures.py (+406 -0 lines)
- A tests/acceptance/_f9_profile_fixtures.py (+408 -0 lines)
- A tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py (+84 -0 lines)
- A tests/acceptance/test_f8_b2_an_example_naming_an_undeclared_function_is_refused.py (+77 -0 lines)
- A tests/acceptance/test_f8_b3_an_example_with_the_wrong_number_of_arguments_is_refused.py (+88 -0 lines)
- A tests/acceptance/test_f8_b4_running_the_examples_answers_instead_of_crashing.py (+72 -0 lines)
- A tests/acceptance/test_f8_b5_the_manifest_publishes_the_new_category.py (+58 -0 lines)
- A tests/acceptance/test_f8_b6_sources_this_rule_leaves_alone.py (+58 -0 lines)
- A tests/acceptance/test_f8_char1_shipped_programs_still_check.py (+91 -0 lines)
- A tests/acceptance/test_f9_b1_division_is_refused_as_unsupported.py (+70 -0 lines)
- A tests/acceptance/test_f9_b2_a_decimal_or_text_literal_is_refused_as_unsupported.py (+102 -0 lines)
- A tests/acceptance/test_f9_b3_a_trailing_top_level_expression_is_refused_as_unsupported.py (+104 -0 lines)
- A tests/acceptance/test_f9_b4_a_preserved_counterexample_is_refused_as_unsupported.py (+63 -0 lines)
- A tests/acceptance/test_f9_b5_an_unsupported_refusal_claims_nothing_more.py (+81 -0 lines)
- A tests/acceptance/test_f9_b6_the_manifest_publishes_the_unsupported_answer.py (+134 -0 lines)
- A tests/properties/test_f8_example_subject.py (+211 -0 lines)
- A tests/properties/test_f9_out_of_profile_source.py (+289 -0 lines)

## Commits (git log, BASE to HEAD)

- 6ee913b Let one owner answer a source the tool cannot check
- f17fe1d Say what an out-of-profile source should be told, before saying it
- 7e79d26 Tell a source that core-0 has no such construct, instead of guessing
- d54c227 Record what F9 was measured at, beside the change
- 5701c86 Keep a misplaced parenthesis a misplaced parenthesis
- feb8130 Correct the craft record after the review and the rebase
- 56faab9 Generate F9's delivery record from the journal
- b5540f4 [F8] read whose example a declared example is
- e749fec [F8] close the delivery's record beside the change
- a42e3b2 [F8] say what a name that is no function is

## 3. oracle: Frame the work and write the oracle (revision 2)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f8/request.md
- **promises**:
  - P1: A function whose only example calls a different function is refused, and the refusal names the function left without an example of its own and the function the example calls.
  - P2: An example calling a function the program does not declare is refused.
  - P3: An example whose number of arguments is not the number its function takes is refused when the program is checked, and asking for the examples answers with that refusal instead of running them.
  - P4: A function whose example calls that same function with the number of arguments it takes stays accepted.
  - P5: The word such a refusal carries is one the tool's manifest publishes, so a client reads it before meeting it.
- **sentence_map**:
  - S1 => not-testable: names the project and the command that runs its suite, not a behaviour of the tool
  - S2 => not-testable: names SPEC.md as the authority the promises are read from
  - S3 => not-testable: a constraint on this change, not an outcome a reader of the tool can observe
  - S4 => not-testable: tells the executor what to do with a conflict; the conflict table below answers it
  - S5 => not-testable: excludes a directory from this work, observable in no answer of the tool
  - S6 => not-testable: says where the change is made, not what the tool does
  - S7 => not-testable: prescribes the commit message, observable only in the repository history
  - S8 => not-testable: the attribution line of that commit message, again history and not behaviour
  - S9 => not-testable: forbids publishing the branch, which no answer of the tool shows
  - S10 => not-testable: the whole suite staying green is a delivery obligation the verification command observes, not a promise of the tool
  - S11 => not-testable: limits which files this change may touch; the design step records how it is kept
  - S12 => not-testable: points at the features already delivered, read for how the checker is built
  - S13 => not-testable: says where the executor keeps its scripts
  - S14 => P5
  - S15 => not-testable: tells the executor how to quote its own commands in this shell
  - S16 => P1
  - S17 => P1
  - S18 => not-testable: a heading above the criteria that follow
  - S19 => not-testable: the number of the first criterion, carrying no outcome of its own
  - S20 => P1
  - S21 => P1
  - S22 => not-testable: the number of the second criterion, carrying no outcome of its own
  - S23 => P2
  - S24 => not-testable: the number of the third criterion, carrying no outcome of its own
  - S25 => P3
  - S26 => P3
  - S27 => not-testable: the number of the fourth criterion, carrying no outcome of its own
  - S28 => P4
  - S29 => not-testable: cites the lines of SPEC.md the rule is read from
  - S30 => not-testable: states that this work waits for no other delivery
  - S31 => not-testable: declares the size of the delivery, recorded in the workspace
  - S32 => not-testable: names the files the change is expected to touch
  - S33 => not-testable: states that the tool disagrees today, which the recorded RED run shows
- **scenarios**:
  - SC1 | P1 | GIVEN a program declaring "double" and "triple", whose only example of "double" is (example (triple 2) => 6) | WHEN the program is checked | THEN the answer is invalid_program with 1 refusal, and that refusal names "double" and "triple"
  - SC2 | P1 | GIVEN the same "double" declaring 2 examples, both of them (example (triple ...) => ...) | WHEN the program is checked | THEN the answer carries 2 refusals, 1 for each example, so no wrong example is hidden
  - SC3 | P2 | GIVEN a program declaring only "double", whose example is (example (treble 2) => 4) and no "treble" anywhere | WHEN the program is checked | THEN the answer is invalid_program and the refusal names "double" and "treble"
  - SC4 | P3 | GIVEN "double", which takes 1 parameter, whose example is (example (double 2 3) => 4) | WHEN the program is checked | THEN the answer is invalid_program and the refusal says the example passes 2 arguments where 1 was expected
  - SC5 | P3 | GIVEN the same "double" whose example is (example (double) => 4), which ended the command before | WHEN the declared examples are asked to run | THEN the command exits 0 with 1 JSON answer saying invalid_program and reports 0 example outcomes
  - SC6 | P4 | GIVEN "double" whose example is (example (double 2) => 4), beside "triple" with its own example | WHEN the program is checked | THEN the answer is completed with 0 diagnostics
  - SC8 | P2 | GIVEN "double" whose only example is (example (Box 3) => 4), where "Box" is a declared constructor and no function | WHEN the program is checked | THEN the answer is invalid_program and the refusal says "Box" is not a function this program declares, offering no move of the example to it
  - SC7 | P5 | GIVEN a client that has read 0 refusals of this tool so far | WHEN it asks the tool what it answers with | THEN the published list of categories names "unrelated_example", the 1 word an example about another function carries
- **conflicts**:
  - S1 | NONE | ran the named command on this worktree before any change: 962 tests, all green, so the baseline the sentence states holds here
  - S2 | NONE | read SPEC.md lines 228-234, which state the rule this delivery adds; nothing there contradicts the request
  - S3 | NONE | read every program text in the repository (188 candidate sources parsed with the project's own reader, plus every program the suite builds at run time) and found no example naming another function and no example with a count its signature does not take, so no existing test's expected result has to change
  - S4 | NONE | no conflict was found to report; every sentence below is NONE for the reason it gives
  - S5 | NONE | the .relay directory holds no program source and no test this delivery reads
  - S6 | NONE | the worktree is the only tree this work writes in and holds its own branch
  - S7 | NONE | the commit message is written by this delivery and contradicts nothing in the repository
  - S8 | NONE | the attribution line is appended to that message and nothing in the repository forbids it
  - S9 | NONE | nothing in this delivery pushes or merges; the remote is left as it stands
  - S10 | NONE | the suite is green before the change, so keeping it green is possible and is the verification command
  - S11 | NONE | the rule lives in checker.py; only the published list of categories in service.py needs one line added, which the sentence allows
  - S12 | NONE | read F5, F6 and F7 in checker.py: each adds a table or a small owner and its diagnostic, the shape this rule follows
  - S13 | NONE | the scripts of this delivery live under the workspace, in a directory of their own
  - S14 | NONE | compared all 13 published categories with this defect: none of them says an example demonstrates another function, so a new word is named with its reason
  - S15 | NONE | the submissions of this delivery are built as argument lists, so no shell reads an arrow
  - S16 | NONE | read every program text in the repository (188 candidate sources parsed with the project's own reader, plus every program the suite builds at run time) and found no example naming another function and no example with a count its signature does not take
  - S17 | NONE | the same reading of the repository covers the second half of the outcome sentence
  - S18 | NONE | a heading contradicts no behaviour of the tool
  - S19 | NONE | the number of a criterion contradicts no behaviour of the tool
  - S20 | NONE | probed the tool before the change: such a program is accepted today, which is the absence of the rule and not a contrary rule
  - S21 | NONE | no existing refusal names two functions, so naming both breaks no published message
  - S22 | NONE | the number of a criterion contradicts no behaviour of the tool
  - S23 | NONE | probed the tool: an example naming an undeclared function is accepted today and no test states that it should be
  - S24 | NONE | the number of a criterion contradicts no behaviour of the tool
  - S25 | NONE | probed the tool: an example with 1 argument too many is accepted and silently reported as passing, which no test asserts
  - S26 | NONE | probed the tool: an example with 1 argument too few ends the command while the examples run, which no test asserts either
  - S27 | NONE | the number of a criterion contradicts no behaviour of the tool
  - S28 | NONE | every program the repository ships and every program its tests build has examples about their own functions, so they all stay accepted
  - S29 | NONE | SPEC.md lines 228-234 are the lines the rule is read from and they say what the request says
  - S30 | NONE | F3, F4, F5 and F7 are already on the branch this worktree started from
  - S31 | NONE | the size declared in the workspace is S, as the sentence says
  - S32 | NONE | the rule fits in checker.py and the tests; only the published category list is touched elsewhere
  - S33 | NONE | the recorded RED run shows the disagreement the sentence names
- **decisions**:
  - DEC1: the refusal of an example about another function carries a new published word, unrelated_example, because none of the 13 published categories states that defect: they report a name that does not resolve, a count, a type, a repeated declaration, a cycle, a hidden binding or a reserved word. SPEC.md line 233 calls such an example unrelated, so the word is the language's own.
  - DEC2: an example that names its own function but writes another number of arguments is answered with the published word arity_mismatch, which the tool already answers with for a call, a constructor and a builtin operator written with the wrong number of arguments. One defect, one word.
  - DEC3: an example naming an undeclared function and an example naming another declared function are one defect with one word: in both the example is not about the function that declares it. The refusal adds that the name is not declared when it is not.
  - DEC4: these refusals carry no line and column. A parsed example keeps no position, and giving it one would change syntax.py, which a parallel delivery holds; the refusal names the function and the ordinal of the example instead.
  - DEC5: no owner is present in this run. Every decision above was taken by the executor and is recorded here for the reviewer.
  - DEC6: no formal model (Quint). The rule is a pure whole-program check over a parsed source: no state, no protocol, no concurrency and no crash window for a model to explore.
- **mapping**:
  - P1 => test_an_example_calling_a_different_function_is_refused_naming_both
  - P2 => test_an_example_naming_a_function_that_does_not_exist_is_refused
  - P3 => test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked
  - P4 => test_a_program_is_accepted_exactly_when_every_example_is_about_its_own_function
  - P5 => test_the_word_for_an_example_about_another_function_is_published
- **covers_scenarios**:
  - SC1 => test_an_example_calling_a_different_function_is_refused_naming_both
  - SC2 => test_two_examples_about_another_function_are_both_reported
  - SC3 => test_an_example_naming_a_function_that_does_not_exist_is_refused
  - SC4 => test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked
  - SC5 => test_asking_for_the_examples_of_a_program_with_too_few_arguments_is_answered
  - SC6 => test_a_program_is_accepted_exactly_when_every_example_is_about_its_own_function
  - SC7 => test_the_word_for_an_example_about_another_function_is_published
  - SC8 => test_an_example_calling_a_declared_constructor_is_refused_the_same_way
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC6 => base held
  - SC7 => base differs
  - SC8 => base differs
- **interfaces**:
  - I1: the `check` operation of the prova command's JSON request surface, which answers whether a program is valid
  - I2: the `examples` operation of that same surface, which runs the examples a program declares
  - I3: the `discover` operation of that same surface, which publishes the words refusals carry
- **matrix**:
  - I1.empty => a source of 0 characters => invalid_program for core-0 asking for at least 1 declaration, never with the new word
  - I1.unknown => an example of "double" naming "treble", which the program never declares => invalid_program, 1 refusal naming "double" and "treble"
  - I1.malformed => a source whose (examples ... clause is never closed => the reading refusal syntax alone, reached before any rule about examples
  - I1.dependency-gone => n/a: the check reads only the source in the request and no other store, file or service
  - I1.repeated => 2 examples of "double" both calling "triple" => 2 refusals, 1 for each example
  - I1.concurrent => n/a: 1 request is read, answered and forgotten; 2 runs share no state
  - I1.crash => an example writing 0 of the 1 arguments its function takes => invalid_program; the check evaluates no example, so none can end it
  - I2.empty => a source of 0 characters => invalid_program and 0 example outcomes
  - I2.unknown => an example naming the undeclared "treble" => invalid_program and 0 example outcomes, instead of an outcome about another function
  - I2.malformed => the unclosed (examples ... clause => the same reading refusal, 0 example outcomes
  - I2.dependency-gone => n/a: the operation reads only the source in the request
  - I2.repeated => 2 examples of "double" both calling "triple" => invalid_program with 2 refusals and 0 example outcomes
  - I2.concurrent => n/a: each request is answered in its own process from its own source; nothing is shared
  - I2.crash => an example writing 0 of the 1 arguments its function takes, which ended the command before => exit 0 with 1 JSON refusal
  - I3.empty => a request carrying no source at all => the manifest, whose list of categories names the new word
  - I3.unknown => n/a: discover reads no program, so no unknown name can reach it
  - I3.malformed => n/a: discover reads no source text at all
  - I3.dependency-gone => n/a: the manifest is built from the tool tables alone, with nothing to be gone
  - I3.repeated => asking discover 2 times => the same list both times, naming the new word 1 time in each
  - I3.concurrent => n/a: the manifest is read-only and keeps no state between requests
  - I3.crash => n/a: discover writes nothing, so an interrupted run leaves nothing behind to repair
- **laws**:
  - LAW1 | a program is accepted exactly when every declared example calls the function declaring it with the number of arguments that function takes | generator=test_a_program_is_accepted_exactly_when_every_example_is_about_its_own_function | observation=the list of categories the check answers with, empty for an accepted program | mutant=a checker that reads an example's arguments but never the name it calls accepts a program whose example of 'double' calls 'triple'
  - LAW2 | a refusal of an example about another function names both the function left without an example of its own and the function the example calls | generator=test_a_refusal_names_the_function_left_without_an_example_and_the_one_called | observation=the reason text of the refusal | mutant=a refusal naming only the function that declares the example
- **messages**:
  - MSG1 | a program declaring 'double' and 'triple' whose only example of 'double' is (example (triple 2) => 6) | example 0 of function 'double' calls 'triple' | core-0 requires every function to have an example directly calling that same function, so this example demonstrates 'triple' and leaves 'double' with no example of its own | write the example as a call to 'double', or declare it among the examples of 'triple' | test=test_an_example_calling_a_different_function_is_refused_naming_both
  - MSG2 | a program whose only example of 'double' is (example (treble 2) => 4) and which declares no function 'treble', or one whose example is (example (Box 3) => 4) with 'Box' a declared constructor | example 0 of function 'double' calls the name it writes, which is not a function this program declares | core-0 requires every function to have an example directly calling that same function, so 'double' is left with no example of its own, and no repair may send a reader to a function that is not there | write the example as a call to 'double' | test=test_an_example_naming_a_function_that_does_not_exist_is_refused
  - MSG3 | a program whose 'double' takes 1 parameter and whose example is (example (double 2 3) => 4) | example 0 of function 'double' passes 2 argument(s), expected 1 | an example supplies 1 closed value for each parameter the function declares, so this example cannot be run against 'double' | write exactly 1 argument in the example | test=test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked
- **red**: `uv run pytest -q tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py tests/acceptance/test_f8_b2_an_example_naming_an_undeclared_function_is_refused.py tests/acceptance/test_f8_b3_an_example_with_the_wrong_number_of_arguments_is_refused.py tests/acceptance/test_f8_b4_running_the_examples_answers_instead_of_crashing.py tests/acceptance/test_f8_b5_the_manifest_publishes_the_new_category.py tests/acceptance/test_f8_b6_sources_this_rule_leaves_alone.py tests/acceptance/test_f8_char1_shipped_programs_still_check.py tests/properties/test_f8_example_subject.py` exited 1 in 2.55s
  - failing on the pre-feature tree (16): tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py::test_an_example_calling_a_different_function_is_refused_naming_both, tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py::test_two_examples_about_another_function_are_both_reported, tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py::test_running_the_examples_refuses_the_same_program, tests/acceptance/test_f8_b2_an_example_naming_an_undeclared_function_is_refused.py::test_an_example_naming_a_function_that_does_not_exist_is_refused, tests/acceptance/test_f8_b2_an_example_naming_an_undeclared_function_is_refused.py::test_an_example_calling_a_declared_constructor_is_refused_the_same_way, tests/acceptance/test_f8_b2_an_example_naming_an_undeclared_function_is_refused.py::test_an_example_whose_call_is_a_builtin_operator_is_refused_the_same_way, tests/acceptance/test_f8_b3_an_example_with_the_wrong_number_of_arguments_is_refused.py::test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked, tests/acceptance/test_f8_b3_an_example_with_the_wrong_number_of_arguments_is_refused.py::test_an_example_with_no_argument_for_a_function_that_takes_one_is_refused, tests/acceptance/test_f8_b3_an_example_with_the_wrong_number_of_arguments_is_refused.py::test_an_example_leaving_out_the_second_argument_is_refused, tests/acceptance/test_f8_b4_running_the_examples_answers_instead_of_crashing.py::test_asking_for_the_examples_of_a_program_with_too_few_arguments_is_answered, tests/acceptance/test_f8_b5_the_manifest_publishes_the_new_category.py::test_the_word_for_an_example_about_another_function_is_published, tests/acceptance/test_f8_b5_the_manifest_publishes_the_new_category.py::test_the_word_a_real_refusal_carries_is_one_the_manifest_publishes, tests/acceptance/test_f8_char1_shipped_programs_still_check.py::test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it[examples/hour-clock.prova], tests/acceptance/test_f8_char1_shipped_programs_still_check.py::test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it[conformance/add-one.prova], tests/properties/test_f8_example_subject.py::test_a_program_is_accepted_exactly_when_every_example_is_about_its_own_function, tests/properties/test_f8_example_subject.py::test_a_refusal_names_the_function_left_without_an_example_and_the_one_called
  - tests (read from the run): 16 failed, 10 passed in 1.77s
  ```text
  E       AssertionError: the refusal '' does not name both 'probe-0', the function left without an example of its own, and 'probe-1', the function its example calls. Source:
  E         (defn probe-0
  E           (sig () -> Int ! pure)
  E           (examples (example (probe-1) => 1))
  E           1)
  E
  E         (defn probe-1
  E           (sig () -> Int ! pure)
  E           (examples (example (probe-1) => 1))
  E           1)
  E
  E         Name both, so a reader can repair the example without searching the program.
  E       assert ("'probe-0'" in '')
  E        +  where "'probe-0'" = repr('probe-0')
  E       Failing test case: test_a_refusal_names_the_function_left_without_an_example_and_the_one_called(
  E           drawn=('(defn probe-0\n  (sig () -> Int ! pure)\n  (examples (example (probe-1) => 1))\n  1)\n\n(defn probe-1\n  (sig () -> Int ! pure)\n  (examples (example (probe-1) => 1))\n  1)\n',
  E            'about another declared function',
  E            'probe-0',
  E            'probe-1'),  # or any other generated value
  E       )

  tests/properties/test_f8_example_subject.py:206: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py::test_an_example_calling_a_different_function_is_refused_naming_both
  FAILED tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py::test_two_examples_about_another_function_are_both_reported
  FAILED tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py::test_running_the_examples_refuses_the_same_program
  FAILED tests/acceptance/test_f8_b2_an_example_naming_an_undeclared_function_is_refused.py::test_an_example_naming_a_function_that_does_not_exist_is_refused
  FAILED tests/acceptance/test_f8_b2_an_example_naming_an_undeclared_function_is_refused.py::test_an_example_calling_a_declared_constructor_is_refused_the_same_way
  FAILED tests/acceptance/test_f8_b2_an_example_naming_an_undeclared_function_is_refused.py::test_an_example_whose_call_is_a_builtin_operator_is_refused_the_same_way
  FAILED tests/acceptance/test_f8_b3_an_example_with_the_wrong_number_of_arguments_is_refused.py::test_an_example_with_one_argument_too_many_is_refused_when_the_program_is_checked
  FAILED tests/acceptance/test_f8_b3_an_example_with_the_wrong_number_of_arguments_is_refused.py::test_an_example_with_no_argument_for_a_function_that_takes_one_is_refused
  FAILED tests/acceptance/test_f8_b3_an_example_with_the_wrong_number_of_arguments_is_refused.py::test_an_example_leaving_out_the_second_argument_is_refused
  FAILED tests/acceptance/test_f8_b4_running_the_examples_answers_instead_of_crashing.py::test_asking_for_the_examples_of_a_program_with_too_few_arguments_is_answered
  FAILED tests/acceptance/test_f8_b5_the_manifest_publishes_the_new_category.py::test_the_word_for_an_example_about_another_function_is_published
  FAILED tests/acceptance/test_f8_b5_the_manifest_publishes_the_new_category.py::test_the_word_a_real_refusal_carries_is_one_the_manifest_publishes
  FAILED tests/acceptance/test_f8_char1_shipped_programs_still_check.py::test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it[examples/hour-clock.prova]
  FAILED tests/acceptance/test_f8_char1_shipped_programs_still_check.py::test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it[conformance/add-one.prova]
  FAILED tests/properties/test_f8_example_subject.py::test_a_program_is_accepted_exactly_when_every_example_is_about_its_own_function
  FAILED tests/properties/test_f8_example_subject.py::test_a_refusal_names_the_function_left_without_an_example_and_the_one_called
  16 failed, 10 passed in 1.77s
  ```

## 4. craft: Craft the change (revision 2)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 106.289s
  - tests (read from the run): 1007 passed in 106.17s
  - slowest: 6.37s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.14s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.70s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.29s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.52s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.85s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.53s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.43s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.33s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 1.28s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  7%]
  ........................................................................ [ 14%]
  ........................................................................ [ 21%]
  ........................................................................ [ 28%]
  ........................................................................ [ 35%]
  ........................................................................ [ 42%]
  ........................................................................ [ 50%]
  ........................................................................ [ 57%]
  ........................................................................ [ 64%]
  ........................................................................ [ 71%]
  ........................................................................ [ 78%]
  ........................................................................ [ 85%]
  ........................................................................ [ 92%]
  .......................................................................  [100%]
  ============================= slowest 10 durations =============================
  6.37s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.14s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.70s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.29s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.52s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.85s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.53s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.43s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.33s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1.28s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1007 passed in 106.17s (0:01:46)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.061s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this process environment, so jev_decide.py exited 3 on the three open questions (category for an example about another function, whether an undeclared name is the same defect, category for a wrong argument count); the request kept at mine/jev/request.json, decided locally as DEC1, DEC2 and DEC3

## 5. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the rule lives where the oracle's decisions put it: one owner in checker.py and one published word in service.py (src/prova/service.py:31), as decisions DEC1 to DEC4 of the oracle record say; no other file is touched
  - D2: pass - the number of parameters, the name called and the ordinal are read once, in DeclaredExample.of (src/prova/checker.py:572); check_program asks that owner and decides nothing itself (src/prova/checker.py:704); the published word is written once (src/prova/checker.py:97) and read from there by service.py
  - D3: pass - the rule reads only parsed syntax and answers a Diagnostic; it calls no reader, no evaluator and no service, and service.py only names the word the checker owns
  - D4: pass - src/prova/checker.py:544 gives the example its own type holding the six facts the rule needs, built only by DeclaredExample.of from a function, its example and the program, so a caller cannot ask the question with a count that belongs to another function; the refusals are returned as Diagnostic values, not booleans (src/prova/checker.py:591)
  - D5: pass - src/prova/checker.py:544 is one frozen dataclass with one responsibility, 6 fields, 5 short methods and no branch deeper than one level; is_about_its_own_function (src/prova/checker.py:588) names the question instead of comparing strings at the call site
  - D6: n/a: no pattern was added; the change follows the shape Cycle and TypeCycle already use, a small value that carries its own refusal
  - D7: pass - the owner speaks the language of SPEC.md (an example, the function that declares it, the function it calls) and the refusals quote the rule the program breaks, at src/prova/checker.py:609 and src/prova/checker.py:634
  - D8: pass - no file, no process, no clock and no network is read by the rule; it is a pure function of a parsed program
  - D9: pass - the acceptance tests drive only the real `prova` command over JSON (tests/acceptance/_f8_example_subject_fixtures.py:275 reads only a response dict) and import nothing from src/prova; the property tests use the published service.handle request surface and its published words, no internal symbol
  - D10: pass - every test name is a sentence about what a reader of the tool gets, for example tests/acceptance/test_f8_b1_an_example_about_another_function_is_refused.py:32; no production symbol, process id or layer term appears in a name
  - D11: pass - the programs and the two assertion helpers live once in tests/acceptance/_f8_example_subject_fixtures.py and every test file calls them; no test re-implements an assertion about a refusal
  - D12: pass - tests/properties/test_f8_example_subject.py:108 draws the case first from a closed set of 5 and then builds a program that is in that case by construction, with no filtering; the oracle is the case drawn, not the checker's answer, and the bounds (3 functions, 2 parameters) are declared in the module
  - D13: pass - 9 runs of the 8 new files in a row: 26 passed every time, pytest-reported 1.22-1.24s; the full suite is 1007 passed in 100.11s; the acceptance tests are integration tests that start the real command once each, about 40 ms, and no test sleeps or reads a clock
  - D14: pass - each test adds a distinct observation: the four names that are not the function's own, the three wrong counts, the crash case, the manifest, the sources the rule leaves alone and the shipped programs; no finite example repeats the property's pair
  - D15: pass - every refusal says what, why and how with the facts it holds (src/prova/checker.py:609 names both functions and the repair; src/prova/checker.py:634 gives both counts), and every assertion message states expected, actual and the contract, for example tests/acceptance/_f8_example_subject_fixtures.py:343
  - D16: n/a: the rule is a pure whole-program check with no state, protocol, concurrency or crash window, so a formal model would have nothing to explore; recorded as decision DEC6 of the oracle
  - D17: pass - docs/feature/function-examples/oracle.md, craft.md and selfreview.md state the measured numbers, the two review findings and the checks that turn red without their fixes, and name what the tests do not prove (argument types, programs larger than the generated bounds, the pre-feature collection limit of 4 unrelated property modules)
- **independent_review**:
  - REV1 | reviewer=rev1-impl-review | findings=2 (verdict APPROVE at e749fec, non-blocking): the branch for a name that is no function had no falsifier, and the refusal's wording was false of a declared constructor and of a builtin operator | resolution=both fixed in a42e3b2: the tests now state both halves of the refusal and observe an example calling a constructor and one calling an operator, and the wording became 'is not a function this program declares'; removing either fix turns 3 tests red, and the converse mutant turns 2 red

## 6. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
  - A declared example is now read as what it demonstrates.
  - An example that names its own function with another number of arguments is refused with the word the tool already uses for a call, a constructor and an operator given the wrong number of arguments, at check time: asking such a program for its examples used to end the command with a traceback and now comes back as one JSON refusal.
  - The rule lives in one owner in the checker beside the refusals it carries; the published list of categories in the service gained one line.
  - Checked through the real prova command over JSON for the examples, the constructor and the operator cases, with a generated property for the law over small programs, and with the two shipped programs kept accepted and their examples passing.
- **not_verified**:
  - that an example's arguments have the types its function declares: the rule reads the name called and the number of arguments only, and the value checks that existed before are unchanged
  - any program larger than the generated bounds: the property samples programs of at most 3 functions of at most 2 parameters, which is evidence and not proof
  - the refusals carry no line and column, so nothing here was checked about where a reader is sent inside the file; a parsed example keeps no position and giving it one would change syntax.py, which a parallel delivery holds
  - no linter and no type checker ran: the repository declares none, and the scorecard command is a byte-compilation of the sources
  - the pre-feature tree cannot collect 4 unrelated property modules (git show of an older SPEC revision exits 128 there), so the recorded red run names the 8 new test files directly instead of the whole suite
  - Jev answered none of the three open questions: TYPESAFE_API_KEY is absent from this environment and the client exited 3; the categories were decided locally
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit a42e3b2ecc51ed7c2ad54a388e6952e0da0398ff
  - no checks declared

## Not backed by the diff

- An example whose call names anything but the function that declares it is refused with a word the manifest publishes, naming the function left without an example of its own and the name the example calls; the refusal offers to move the example only when that name is a function able to own one, and otherwise says it is not a function this program declares, which is true of a name declared nowhere, of a declared constructor and of a builtin operator alike.: a guarantee names no test function of the change
- Each refusal and each half of its message was removed in turn and the tests were watched to fail, then restored.: a guarantee names no test function of the change
