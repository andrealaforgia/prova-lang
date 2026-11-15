# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 899 tests, all green on main).
  - not-testable (challenge this): states the project, its test command and its green baseline; no outcome a reader can observe from the tool
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority for the rule, which is a source of truth and not an outcome
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on the change itself, read from the diff rather than from the tool behaviour
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): tells the author what to do when a conflict is found; it is a procedure, not an outcome
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): names a directory to leave alone, which no test of the tool can observe
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a constraint on where the work happens, read from the checkout and not from the tool
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a constraint on the commit message, read from the git history and not from the tool
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the literal line the commit message must end with; part of the same history constraint
- S9: Do not push and do not merge.
  - not-testable (challenge this): a constraint on what is done with the branch afterwards, outside the tool behaviour
- S10: Keep the full suite green.
  - promises: P4
  - tests P4: test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments
- S11: Another delivery (F6, mostly src/prova/syntax.py and service.py) runs in parallel in a different worktree and will merge after or before you; do not touch syntax.py.
  - not-testable (challenge this): a constraint on which files the change may touch, read from the diff and not from the tool
- S12: F5 (binding scope) is already on main; read how it is built in checker.py.
  - not-testable (challenge this): tells the author what to read first; reading is not an outcome a test can observe
- S13: Existing categories include cyclic_dependency, duplicate_declaration, recursive_type, shadowed_binding and reserved_name; reuse one if it fits, else name a new published category with the reason in your oracle note.
  - promises: P5
  - tests P5: test_the_refusal_a_wrongly_counted_operator_carries_is_published
- S14: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell quoting and working-copy hygiene for the author, with no effect on the tool
- S15: **Outcome.** A builtin operator applied to the wrong number of arguments is
  - promises: P1, P2, P3, P6
  - tests P1: test_negation_written_with_two_arguments_is_refused_with_both_counts
  - tests P2: test_a_sum_written_with_one_argument_is_refused_with_both_counts
  - tests P3: test_each_operator_written_with_a_wrong_number_of_arguments_is_refused
  - tests P6: test_running_that_program_answers_a_refusal_instead_of_stopping
- S16: refused, rather than quietly ignoring the extras.
  - promises: P1, P2, P3, P6
  - tests P1: test_negation_written_with_two_arguments_is_refused_with_both_counts
  - tests P2: test_a_sum_written_with_one_argument_is_refused_with_both_counts
  - tests P3: test_each_operator_written_with_a_wrong_number_of_arguments_is_refused
  - tests P6: test_running_that_program_answers_a_refusal_instead_of_stopping
- S17: **Acceptance criteria**
  - not-testable (challenge this): a heading that introduces the numbered criteria below it
- S18: 1.
  - not-testable (challenge this): the number of the first criterion, whose text is the sentences that follow
- S19: Given `not` with two arguments, when the program is checked, then it is invalid
  - promises: P1
  - tests P1: test_negation_written_with_two_arguments_is_refused_with_both_counts
- S20: and the diagnostic gives the expected and the actual count.
  - promises: P1
  - tests P1: test_negation_written_with_two_arguments_is_refused_with_both_counts
- S21: 2.
  - not-testable (challenge this): the number of the second criterion, whose text is the sentence that follows
- S22: Given `+` with one argument or three, likewise.
  - promises: P2
  - tests P2: test_a_sum_written_with_one_argument_is_refused_with_both_counts
- S23: 3.
  - not-testable (challenge this): the number of the third criterion, whose text is the sentences that follow
- S24: Given each comparison, equality and boolean operator with a wrong count,
  - promises: P3
  - tests P3: test_each_operator_written_with_a_wrong_number_of_arguments_is_refused
- S25: likewise.
  - promises: P3
  - tests P3: test_each_operator_written_with_a_wrong_number_of_arguments_is_refused
- S26: 4.
  - not-testable (challenge this): the number of the fourth criterion, whose text is the sentences that follow
- S27: Given every operator applied correctly, when the program is checked, then it is
  - promises: P4
  - tests P4: test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments
- S28: accepted.
  - promises: P4
  - tests P4: test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments
- S29: **SPEC.md** lines 178-189 (the operator table and "no variable arity").
  - not-testable (challenge this): cites the authority lines that fix the operator table; a citation, not an outcome
- S30: **Dependencies** none (serial with F3, F4, F5, F8).
  - not-testable (challenge this): states that nothing else must land first; a planning fact about other work
- S31: **Size** S: one arity table.
  - not-testable (challenge this): states the size of the delivery, which no observation of the tool can show
- S32: **Touches** `src/prova/checker.py`, tests.
  - not-testable (challenge this): names the files the work is expected to touch; read from the diff, not the tool
- S33: **Why it is a real expectation** probe E5 disagrees today.
  - promises: P1
  - tests P1: test_negation_written_with_two_arguments_is_refused_with_both_counts

## Edge matrix

- I1.empty: a request whose source is the empty string => accepted with no diagnostics, exactly as before | self-probe: not probed | pre-feature not probed
- I1.unknown: a body `(mod cents cents)`, a name that is not one of the 11 operators => refused as an undeclared name, never as a wrong number of arguments | self-probe: not probed | pre-feature not probed
- I1.malformed: a body `(+ cents cents` that is never closed => refused as text the tool cannot read, never as a wrong number of arguments | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): checking reads only the source text inside the request and opens no other file
- I1.repeated: the same program with `(not flag flag)` checked twice => the same single refusal both times, and nothing is written anywhere | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): every request runs in its own process, reads only its own input and writes no shared state
- I1.crash: a body `(not)` with no operand at all => refused with both counts and an exit status of 0, where the pre-feature command stops with no answer | self-probe: not probed | pre-feature not probed
- I2.empty: evaluate asked against an empty source => the unchanged answer that no function of that name exists | self-probe: not probed | pre-feature not probed
- I2.unknown: evaluate naming a function the source does not declare => the unchanged answer that no function of that name exists | self-probe: not probed | pre-feature not probed
- I2.malformed: evaluate or examples on a program whose `not` has 0 arguments => refused as an invalid program before anything runs, instead of stopping the command | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): evaluating reads only the source text and the arguments inside the request
- I2.repeated: asking twice to evaluate the same wrongly counted program => the same refusal both times, with nothing kept between runs | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): every request runs in its own process and writes no shared state
- I2.crash: evaluate a program whose `not` has 0 arguments, the case that stops the pre-feature command with no answer => 1 refusal and an exit status of 0, because the wrong count is refused before anything is evaluated | self-probe: not probed | pre-feature not probed
- I3.empty: a describe request carries no program, so there is no empty program to answer => the same manifest as always | self-probe: not probed | pre-feature not probed
- I3.unknown: a request naming an operation the tool does not have => the unchanged answer that the operation is not recognised | self-probe: not probed | pre-feature not probed
- I3.malformed: a request that is not JSON at all => the unchanged tool_failure answer on standard output | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): the manifest is a fixed list the command holds itself and reads nothing to build
- I3.repeated: the manifest read twice => the same list both times, with the word for a wrong number of arguments in it exactly once | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): every request runs in its own process and the manifest is read-only
- I3.crash: n/a (challenge this): the manifest is a constant the command already holds, so there is nothing for it to fail on

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the function `unflagged?` whose body is `(not flag flag)`
  - WHEN the program is checked
  - THEN it is invalid and one refusal says `not` takes exactly 1 argument and got 2, at line 4 column 3
  - test: test_negation_written_with_two_arguments_is_refused_with_both_counts
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN the function `total` whose body is `(+ cents)`
  - WHEN the program is checked
  - THEN it is invalid and one refusal says `+` takes exactly 2 arguments and got 1
  - test: test_a_sum_written_with_one_argument_is_refused_with_both_counts
- SC3 (P2): not-held (no held self-probe case)
  - GIVEN the same function whose body is `(+ cents cents cents)`
  - WHEN the program is checked
  - THEN it is invalid and one refusal says `+` takes exactly 2 arguments and got 3
  - test: test_a_sum_written_with_three_arguments_is_refused_with_both_counts
- SC4 (P3): not-held (no held self-probe case)
  - GIVEN one program that writes each of the 11 operators once with 1 argument too few and once with 1 too many, 22 calls in all
  - WHEN the program is checked
  - THEN it is invalid with 22 refusals, each at its own line, each naming its operator and its 2 counts
  - test: test_each_operator_written_with_a_wrong_number_of_arguments_is_refused
- SC5 (P4): not-held (no held self-probe case)
  - GIVEN a program with 1 function per operator, each applying its operator to the number of arguments the language gives it
  - WHEN the program is checked and its examples are run
  - THEN it is accepted with 0 diagnostics and all 11 examples pass
  - test: test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments
- SC6 (P5): not-held (no held self-probe case)
  - GIVEN the refused program whose body is `(not flag flag)`
  - WHEN its refusal and the manifest are read together
  - THEN the word the refusal carries is 1 of the words the manifest publishes
  - test: test_the_refusal_a_wrongly_counted_operator_carries_is_published
- SC7 (P6): not-held (no held self-probe case)
  - GIVEN the function `unflagged?` whose body is `(not)`
  - WHEN the user asks to evaluate `unflagged?` for `true`
  - THEN the command exits 0 with 1 refusal saying `not` takes exactly 1 argument and got 0, instead of stopping with no answer
  - test: test_running_that_program_answers_a_refusal_instead_of_stopping

## Questions for the owner

- none

## Observed side effects (git, BASE to HEAD)

- A docs/f6-names-and-markers/DECISIONS.md (+18 -0 lines)
- A docs/f6-names-and-markers/SUMMARY.md (+671 -0 lines)
- A docs/f6-names-and-markers/TRACE.md (+6 -0 lines)
- A docs/feature/f6-names-and-markers/craft.md (+66 -0 lines)
- A docs/feature/f6-names-and-markers/design.md (+90 -0 lines)
- A docs/feature/f6-names-and-markers/oracle.md (+94 -0 lines)
- A docs/feature/operator-arity/craft.md (+101 -0 lines)
- A docs/feature/operator-arity/oracle.md (+108 -0 lines)
- A docs/operator-arity/DECISIONS.md (+11 -0 lines)
- A docs/operator-arity/SUMMARY.md (+405 -0 lines)
- A docs/operator-arity/TRACE.md (+5 -0 lines)
- M docs/spec-trace.md (+1 -1 lines)
- M src/prova/checker.py (+78 -4 lines)
- M src/prova/service.py (+19 -4 lines)
- M src/prova/syntax.py (+427 -29 lines)
- A tests/acceptance/_f6_spelling_fixtures.py (+287 -0 lines)
- A tests/acceptance/_f7_operator_arity_fixtures.py (+486 -0 lines)
- M tests/acceptance/test_f5_b11_odd_but_parseable_binders_are_answered.py (+21 -5 lines)
- A tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py (+77 -0 lines)
- A tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py (+102 -0 lines)
- A tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py (+97 -0 lines)
- A tests/acceptance/test_f6_b4_an_example_with_the_wrong_arrow_is_refused.py (+50 -0 lines)
- A tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py (+66 -0 lines)
- A tests/acceptance/test_f6_b6_the_shipped_programs_still_check.py (+43 -0 lines)
- A tests/acceptance/test_f7_b1_an_operator_given_an_extra_argument_is_refused.py (+69 -0 lines)
- A tests/acceptance/test_f7_b2_a_sum_with_too_few_or_too_many_arguments_is_refused.py (+56 -0 lines)
- A tests/acceptance/test_f7_b3_every_operator_with_a_wrong_count_is_refused.py (+109 -0 lines)
- A tests/acceptance/test_f7_b4_every_operator_applied_correctly_is_accepted.py (+69 -0 lines)
- A tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py (+92 -0 lines)
- A tests/acceptance/test_f7_b6_a_wrong_count_and_a_wrong_operand_are_both_reported.py (+90 -0 lines)
- A tests/acceptance/test_f7_b7_the_refusal_uses_a_category_the_manifest_publishes.py (+65 -0 lines)
- A tests/acceptance/test_f7_b8_a_wrong_count_in_a_contract_or_a_clause_is_refused.py (+111 -0 lines)
- M tests/properties/test_f3_duplicate_declarations.py (+4 -1 lines)
- A tests/properties/test_f6_every_malformed_source_still_answers.py (+195 -0 lines)
- A tests/properties/test_f6_name_and_marker_spelling.py (+137 -0 lines)
- A tests/properties/test_f7_operator_arity.py (+170 -0 lines)
- A tests/unit/test_checker_operator_table.py (+69 -0 lines)
- M tests/unit/test_verify_inventory_edges.py (+29 -12 lines)

## Commits (git log, BASE to HEAD)

- 66aebff [F6] build a source refusal in one place
- 84d6e30 [F6] state in tests how names and markers must be spelled
- 6f0467c [F6] record who owns each spelling rule, before writing one
- 7170431 [F6] refuse a name or marker core-0 does not spell that way
- 1c43659 Correct two expectations the empty-program rule contradicts
- fce2918 [F6] answer every source the reader cannot read, never raise
- 0f22ce1 [F6] cover the pattern a constructor position must hold
- 6183193 [F6] record the delivery beside the change
- 6d74308 [F6] regenerate the record after the design step was recorded again
- 01e9411 [F6] regenerate the record after the craft step was recorded again
- e2d1f60 Narrow the diagnostic-location row to what the tool really does
- 93157d7 [F6] state the totality laws as the generated properties they are
- e9295ba [F6] record the self-review and the handoff beside the change
- fdce455 Leave the postcondition name to the rule that owns it
- d4ec9b6 Expect the empty source refused in the binding control too
- 5024bf2 [F6] say in the record which rule owns the postcondition name
- 8ae2b52 [F7] refuse an operator written with the wrong number of arguments
- 8b0abfa [F7] keep the delivery's record beside the change
- 8180a19 [F7] pin acceptance on a program with no operator, not on an empty one
- d5bbaeb [F7] let one table say which operators the language has
- 0b75c34 [F7] count an operator's arguments in a contract and in a clause too
- 6dacb88 [F7] restate the counts this branch actually measured

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - the delivery request, which lives in the run workspace outside this repository; its sentences are quoted in full in docs/operator-arity/SUMMARY.md
- **promises**:
  - P1: A program that applies `not` to two arguments is refused, and the refusal gives the number of arguments `not` takes and the number the program gave.
  - P2: A program that applies `+` to one argument, or to three, is refused the same way, with both counts.
  - P3: Every comparison, equality and boolean operator written with a wrong number of arguments is refused the same way, with both counts.
  - P4: Every builtin operator applied to its own number of arguments is still accepted and still answers what the language says it answers.
  - P5: The refusal carries a word the tool already publishes in its manifest, so a client can act on it without reading prose.
  - P6: A program whose operator has no arguments at all is answered with that same refusal instead of stopping the command without an answer.
- **sentence_map**:
  - S1 => not-testable: states the project, its test command and its green baseline; no outcome a reader can observe from the tool
  - S2 => not-testable: names SPEC.md as the authority for the rule, which is a source of truth and not an outcome
  - S3 => not-testable: a constraint on the change itself, read from the diff rather than from the tool behaviour
  - S4 => not-testable: tells the author what to do when a conflict is found; it is a procedure, not an outcome
  - S5 => not-testable: names a directory to leave alone, which no test of the tool can observe
  - S6 => not-testable: a constraint on where the work happens, read from the checkout and not from the tool
  - S7 => not-testable: a constraint on the commit message, read from the git history and not from the tool
  - S8 => not-testable: the literal line the commit message must end with; part of the same history constraint
  - S9 => not-testable: a constraint on what is done with the branch afterwards, outside the tool behaviour
  - S10 => P4
  - S11 => not-testable: a constraint on which files the change may touch, read from the diff and not from the tool
  - S12 => not-testable: tells the author what to read first; reading is not an outcome a test can observe
  - S13 => P5
  - S14 => not-testable: shell quoting and working-copy hygiene for the author, with no effect on the tool
  - S15 => P1,P2,P3,P6
  - S16 => P1,P2,P3,P6
  - S17 => not-testable: a heading that introduces the numbered criteria below it
  - S18 => not-testable: the number of the first criterion, whose text is the sentences that follow
  - S19 => P1
  - S20 => P1
  - S21 => not-testable: the number of the second criterion, whose text is the sentence that follows
  - S22 => P2
  - S23 => not-testable: the number of the third criterion, whose text is the sentences that follow
  - S24 => P3
  - S25 => P3
  - S26 => not-testable: the number of the fourth criterion, whose text is the sentences that follow
  - S27 => P4
  - S28 => P4
  - S29 => not-testable: cites the authority lines that fix the operator table; a citation, not an outcome
  - S30 => not-testable: states that nothing else must land first; a planning fact about other work
  - S31 => not-testable: states the size of the delivery, which no observation of the tool can show
  - S32 => not-testable: names the files the work is expected to touch; read from the diff, not the tool
  - S33 => P1
- **scenarios**:
  - SC1 | P1 | GIVEN the function `unflagged?` whose body is `(not flag flag)` | WHEN the program is checked | THEN it is invalid and one refusal says `not` takes exactly 1 argument and got 2, at line 4 column 3
  - SC2 | P2 | GIVEN the function `total` whose body is `(+ cents)` | WHEN the program is checked | THEN it is invalid and one refusal says `+` takes exactly 2 arguments and got 1
  - SC3 | P2 | GIVEN the same function whose body is `(+ cents cents cents)` | WHEN the program is checked | THEN it is invalid and one refusal says `+` takes exactly 2 arguments and got 3
  - SC4 | P3 | GIVEN one program that writes each of the 11 operators once with 1 argument too few and once with 1 too many, 22 calls in all | WHEN the program is checked | THEN it is invalid with 22 refusals, each at its own line, each naming its operator and its 2 counts
  - SC5 | P4 | GIVEN a program with 1 function per operator, each applying its operator to the number of arguments the language gives it | WHEN the program is checked and its examples are run | THEN it is accepted with 0 diagnostics and all 11 examples pass
  - SC6 | P5 | GIVEN the refused program whose body is `(not flag flag)` | WHEN its refusal and the manifest are read together | THEN the word the refusal carries is 1 of the words the manifest publishes
  - SC7 | P6 | GIVEN the function `unflagged?` whose body is `(not)` | WHEN the user asks to evaluate `unflagged?` for `true` | THEN the command exits 0 with 1 refusal saying `not` takes exactly 1 argument and got 0, instead of stopping with no answer
- **conflicts**:
  - S1 | NONE | ran the suite command on the pre-feature tree and read its green count; nothing in it asserts an operator may take a free number of arguments
  - S2 | NONE | read SPEC.md lines 170-190: the operator table fixes one argument for `not` and two for the rest, and says operators have no variable arity
  - S3 | NONE | this change adds test files and leaves SPEC.md and every existing test file untouched; no existing expected result is restated
  - S4 | NONE | searched for an existing test or shipped program that applies an operator to a wrong count, parsing every repository source and every program literal in the tests; found none, with a positive control proving the search reports one when it exists
  - S5 | NONE | the .relay directory is absent from this worktree and nothing in the change reads it
  - S6 | NONE | every file written is under the worktree on its own branch, confirmed by the status of that checkout
  - S7 | NONE | the commit message of this change ends with the line the request gives; nothing in the repository forbids it
  - S8 | NONE | that attribution line is text in a commit message and contradicts nothing the repository already does
  - S9 | NONE | nothing in the change pushes or merges; the branch stays where it is
  - S10 | NONE | checked that no shipped example, conformance program or test program applies an operator to a count other than its own, so refusing those counts leaves the existing suite green
  - S11 | NONE | the rule is about how many arguments a call has, which the checker reads from the parsed call; the parser already accepts any count, so syntax.py needs no change
  - S12 | NONE | read how F5 builds its rules in checker.py: a category constant, a diagnostic with a reason and a place, and the published list in service.py
  - S13 | NONE | the published vocabulary already has a word for a wrong number of arguments, used for a call to a declared function and for a constructor, and the probe in docs/spec-trace already expects that word here
  - S14 | NONE | the recorded submissions are written as files and the quoted arrows are passed as single arguments; this constrains the author, not the tool
  - S15 | NONE | the pre-feature tool accepts every one of the 22 wrong counts, so refusing them changes no behaviour any authority promises
  - S16 | NONE | the pre-feature tool ignores the extra arguments silently, which is exactly what SPEC.md lines 178-189 forbid
  - S17 | NONE | a heading contradicts nothing in the system; read it and moved on to the criteria
  - S18 | NONE | a list number contradicts nothing in the system
  - S19 | NONE | ran `(not flag flag)` through the real command on the pre-feature tree: accepted today, and no authority says it should be
  - S20 | NONE | the two sibling refusals about a wrong number of arguments already state both counts, so saying both here follows what the tool already does
  - S21 | NONE | a list number contradicts nothing in the system
  - S22 | NONE | ran `(+ cents)` and `(+ cents cents cents)` through the real command on the pre-feature tree: both accepted today, promised by nothing
  - S23 | NONE | a list number contradicts nothing in the system
  - S24 | NONE | ran every comparison, equality and boolean operator with a wrong count through the real command: all accepted today, promised by nothing
  - S25 | NONE | the same two counts are asked for in every one of those cases, which the sibling refusals already provide
  - S26 | NONE | a list number contradicts nothing in the system
  - S27 | NONE | ran all 11 operators applied correctly through the real command: accepted today and still accepted after the rule, which only counts arguments
  - S28 | NONE | acceptance of correctly written programs is what the existing suite already pins, and the rule reads only the number of arguments
  - S29 | NONE | read those SPEC.md lines; the table and the no-variable-arity sentence agree with the criteria above
  - S30 | NONE | nothing in this change depends on other delivered work, and it touches neither syntax.py nor service.py
  - S31 | NONE | one table of 11 entries and one rule beside the existing count rules; nothing in the code makes that larger
  - S32 | NONE | the rule belongs where the operator is already checked for operand types, which is checker.py, and the tests live beside the other feature tests
  - S33 | NONE | ran the probe case `(not b b)` on the pre-feature tree and saw it accepted, which is the disagreement the sentence reports
- **decisions**:
  - DEC1: Reuse the published word for a wrong number of arguments rather than publish a twelfth one. It already answers a call to a declared function and a constructor given the wrong number, both of which state the expected and the actual count, and the repository probe for this rule already expects that word. Reusing it also leaves the manifest in service.py untouched, which keeps this change clear of the delivery running in parallel there.
  - DEC2: When an operator has both a wrong number of operands and an operand of the wrong type, report both, as the sibling rule for a call to a declared function already does, so a reader repairs the expression in one pass. An operand of the right type never adds a second refusal.
  - DEC3: The owner is absent for this run. DEC1 and DEC2 are the author decisions taken in the owner place, both inside what the request already allows: the request lets an existing category be reused when it fits, and the sibling behaviour settles the second.
  - DEC4: No formal model. The rule is a pure comparison of two numbers in one expression, with no state, protocol, concurrency or crash sequence for a model to explore.
- **mapping**:
  - P1 => test_negation_written_with_two_arguments_is_refused_with_both_counts
  - P2 => test_a_sum_written_with_one_argument_is_refused_with_both_counts
  - P3 => test_each_operator_written_with_a_wrong_number_of_arguments_is_refused
  - P4 => test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments
  - P5 => test_the_refusal_a_wrongly_counted_operator_carries_is_published
  - P6 => test_running_that_program_answers_a_refusal_instead_of_stopping
- **covers_scenarios**:
  - SC1 => test_negation_written_with_two_arguments_is_refused_with_both_counts
  - SC2 => test_a_sum_written_with_one_argument_is_refused_with_both_counts
  - SC3 => test_a_sum_written_with_three_arguments_is_refused_with_both_counts
  - SC4 => test_each_operator_written_with_a_wrong_number_of_arguments_is_refused
  - SC5 => test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments
  - SC6 => test_the_refusal_a_wrongly_counted_operator_carries_is_published
  - SC7 => test_running_that_program_answers_a_refusal_instead_of_stopping
- **interfaces**:
  - I1: the `prova` command asked to check a program, over one JSON request on standard input and one JSON response on standard output
  - I2: the `prova` command asked to evaluate a function or to run a program declared examples, both of which check the program before running anything
  - I3: the `prova` command asked to describe itself, whose answer publishes the words a refusal may carry
- **matrix**:
  - I1.empty => a request whose source is the empty string => accepted with no diagnostics, exactly as before
  - I1.unknown => a body `(mod cents cents)`, a name that is not one of the 11 operators => refused as an undeclared name, never as a wrong number of arguments
  - I1.malformed => a body `(+ cents cents` that is never closed => refused as text the tool cannot read, never as a wrong number of arguments
  - I1.dependency-gone => n/a: checking reads only the source text inside the request and opens no other file
  - I1.repeated => the same program with `(not flag flag)` checked twice => the same single refusal both times, and nothing is written anywhere
  - I1.concurrent => n/a: every request runs in its own process, reads only its own input and writes no shared state
  - I1.crash => a body `(not)` with no operand at all => refused with both counts and an exit status of 0, where the pre-feature command stops with no answer
  - I2.empty => evaluate asked against an empty source => the unchanged answer that no function of that name exists
  - I2.unknown => evaluate naming a function the source does not declare => the unchanged answer that no function of that name exists
  - I2.malformed => evaluate or examples on a program whose `not` has 0 arguments => refused as an invalid program before anything runs, instead of stopping the command
  - I2.dependency-gone => n/a: evaluating reads only the source text and the arguments inside the request
  - I2.repeated => asking twice to evaluate the same wrongly counted program => the same refusal both times, with nothing kept between runs
  - I2.concurrent => n/a: every request runs in its own process and writes no shared state
  - I2.crash => evaluate a program whose `not` has 0 arguments, the case that stops the pre-feature command with no answer => 1 refusal and an exit status of 0, because the wrong count is refused before anything is evaluated
  - I3.empty => a describe request carries no program, so there is no empty program to answer => the same manifest as always
  - I3.unknown => a request naming an operation the tool does not have => the unchanged answer that the operation is not recognised
  - I3.malformed => a request that is not JSON at all => the unchanged tool_failure answer on standard output
  - I3.dependency-gone => n/a: the manifest is a fixed list the command holds itself and reads nothing to build
  - I3.repeated => the manifest read twice => the same list both times, with the word for a wrong number of arguments in it exactly once
  - I3.concurrent => n/a: every request runs in its own process and the manifest is read-only
  - I3.crash => n/a: the manifest is a constant the command already holds, so there is nothing for it to fail on
- **laws**:
  - LAW1 | A program is accepted exactly when every builtin operator in it is written with the number of arguments SPEC.md gives that operator, and refused for the number of arguments otherwise | generator=test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments | observation=the status and the list of categories the published check operation answers with, for a drawn operator and a drawn count from 0 to 6 | mutant=a checker that refuses only too many arguments, so a call with one operand too few stays accepted
  - LAW2 | Every refusal of a wrong number of arguments states the number the operator takes and the number the program gave, at the place of the call | generator=test_a_refusal_states_the_number_taken_and_the_number_given | observation=the reason sentence and the location of the single refusal, for a drawn operator and a drawn wrong count on either side of its own | mutant=a refusal that names the operator and one of the two counts only
- **messages**:
  - MSG1 | a program whose body is `(not flag flag)` | operator not takes exactly 1 argument(s), got 2 | operators have no variable arity, so a second argument has nowhere to go | write the call with exactly 1 argument | test=test_negation_written_with_two_arguments_is_refused_with_both_counts
  - MSG2 | a program whose body is `(+ cents)` | operator + takes exactly 2 argument(s), got 1 | operators have no variable arity, so a missing operand is not a shorter sum | write the call with exactly 2 arguments | test=test_a_sum_written_with_one_argument_is_refused_with_both_counts
  - MSG3 | a program whose body is `(not)`, asked to be evaluated | operator not takes exactly 1 argument(s), got 0 | the operator has nothing to work on, so the program cannot be run | write the call with exactly 1 argument | test=test_running_that_program_answers_a_refusal_instead_of_stopping
- **red**: `uv run pytest -q tests/acceptance/test_f7_b1_an_operator_given_an_extra_argument_is_refused.py tests/acceptance/test_f7_b2_a_sum_with_too_few_or_too_many_arguments_is_refused.py tests/acceptance/test_f7_b3_every_operator_with_a_wrong_count_is_refused.py tests/acceptance/test_f7_b4_every_operator_applied_correctly_is_accepted.py tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py tests/acceptance/test_f7_b6_a_wrong_count_and_a_wrong_operand_are_both_reported.py tests/acceptance/test_f7_b7_the_refusal_uses_a_category_the_manifest_publishes.py tests/properties/test_f7_operator_arity.py` exited 1 in 2.73s
  - failing on the pre-feature tree (13): tests/acceptance/test_f7_b1_an_operator_given_an_extra_argument_is_refused.py::test_negation_written_with_two_arguments_is_refused_with_both_counts, tests/acceptance/test_f7_b1_an_operator_given_an_extra_argument_is_refused.py::test_an_extra_argument_written_inside_another_expression_is_refused_too, tests/acceptance/test_f7_b2_a_sum_with_too_few_or_too_many_arguments_is_refused.py::test_a_sum_written_with_one_argument_is_refused_with_both_counts, tests/acceptance/test_f7_b2_a_sum_with_too_few_or_too_many_arguments_is_refused.py::test_a_sum_written_with_three_arguments_is_refused_with_both_counts, tests/acceptance/test_f7_b3_every_operator_with_a_wrong_count_is_refused.py::test_each_operator_written_with_a_wrong_number_of_arguments_is_refused, tests/acceptance/test_f7_b3_every_operator_with_a_wrong_count_is_refused.py::test_nothing_but_the_wrong_counts_is_held_against_that_program, tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py::test_a_program_whose_operator_has_no_arguments_is_refused_with_both_counts, tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py::test_running_that_program_answers_a_refusal_instead_of_stopping, tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py::test_asking_for_its_examples_answers_a_refusal_instead_of_stopping, tests/acceptance/test_f7_b6_a_wrong_count_and_a_wrong_operand_are_both_reported.py::test_a_sum_with_three_arguments_one_of_them_a_flag_is_told_both_things, tests/acceptance/test_f7_b7_the_refusal_uses_a_category_the_manifest_publishes.py::test_the_refusal_a_wrongly_counted_operator_carries_is_published, tests/properties/test_f7_operator_arity.py::test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments, tests/properties/test_f7_operator_arity.py::test_a_refusal_states_the_number_taken_and_the_number_given
  - tests (read from the run): 13 failed, 9 passed in 1.95s
  ```text
          given_count = max(takes - offset, 0) if fewer else takes + offset

          response = _check(_program_applying(operator, given_count))

          refusals = [
              d
              for d in response.get("diagnostics") or []
              if d.get("category") == ARITY_MISMATCH_CATEGORY
          ]
  >       assert len(refusals) == 1, (
              f"a program applying {operator!r} to {given_count} argument(s) instead of "
              f"{takes} drew {len(refusals)} refusal(s) about the number of arguments: "
              f"{response}. One wrong call is one defect with one repair."
          )
  E       AssertionError: a program applying '*' to 3 argument(s) instead of 2 drew 0 refusal(s) about the number of arguments: {'operation': 'check', 'status': 'completed', 'claim': {'kind': 'static_check', 'scope': 'this input'}, 'source_digest': '027dc5f1c30c241aeca69fc2231e77ed3bd53121a620cbc55da642e852975b47', 'diagnostics': []}. One wrong call is one defect with one repair.
  E       assert 0 == 1
  E        +  where 0 = len([])
  E       Failing test case: test_a_refusal_states_the_number_taken_and_the_number_given(
  E           # The test always failed when commented parts were varied together.
  E           operator='*',  # or any other generated value
  E           offset=1,  # or any other generated value
  E           fewer=False,  # or any other generated value
  E       )

  tests/properties/test_f7_operator_arity.py:151: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f7_b1_an_operator_given_an_extra_argument_is_refused.py::test_negation_written_with_two_arguments_is_refused_with_both_counts
  FAILED tests/acceptance/test_f7_b1_an_operator_given_an_extra_argument_is_refused.py::test_an_extra_argument_written_inside_another_expression_is_refused_too
  FAILED tests/acceptance/test_f7_b2_a_sum_with_too_few_or_too_many_arguments_is_refused.py::test_a_sum_written_with_one_argument_is_refused_with_both_counts
  FAILED tests/acceptance/test_f7_b2_a_sum_with_too_few_or_too_many_arguments_is_refused.py::test_a_sum_written_with_three_arguments_is_refused_with_both_counts
  FAILED tests/acceptance/test_f7_b3_every_operator_with_a_wrong_count_is_refused.py::test_each_operator_written_with_a_wrong_number_of_arguments_is_refused
  FAILED tests/acceptance/test_f7_b3_every_operator_with_a_wrong_count_is_refused.py::test_nothing_but_the_wrong_counts_is_held_against_that_program
  FAILED tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py::test_a_program_whose_operator_has_no_arguments_is_refused_with_both_counts
  FAILED tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py::test_running_that_program_answers_a_refusal_instead_of_stopping
  FAILED tests/acceptance/test_f7_b5_an_operator_with_no_arguments_is_answered_not_crashed.py::test_asking_for_its_examples_answers_a_refusal_instead_of_stopping
  FAILED tests/acceptance/test_f7_b6_a_wrong_count_and_a_wrong_operand_are_both_reported.py::test_a_sum_with_three_arguments_one_of_them_a_flag_is_told_both_things
  FAILED tests/acceptance/test_f7_b7_the_refusal_uses_a_category_the_manifest_publishes.py::test_the_refusal_a_wrongly_counted_operator_carries_is_published
  FAILED tests/properties/test_f7_operator_arity.py::test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments
  FAILED tests/properties/test_f7_operator_arity.py::test_a_refusal_states_the_number_taken_and_the_number_given
  13 failed, 9 passed in 1.95s
  ```

## 2. craft: Craft the change (revision 1)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 97.601s
  - tests (read from the run): 921 passed in 97.45s
  - slowest: 6.12s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 3.89s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.84s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 2.97s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.61s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.77s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.59s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.41s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.35s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 1.27s call tests/properties/test_i1_s4_p2_comparison.py::test_p2_guard_specific_domain_is_the_single_pair_and_it_fails_at_runtime
  ```text
  ........................................................................ [  7%]
  ........................................................................ [ 15%]
  ........................................................................ [ 23%]
  ........................................................................ [ 31%]
  ........................................................................ [ 39%]
  ........................................................................ [ 46%]
  ........................................................................ [ 54%]
  ........................................................................ [ 62%]
  ........................................................................ [ 70%]
  ........................................................................ [ 78%]
  ........................................................................ [ 85%]
  ........................................................................ [ 93%]
  .........................................................                [100%]
  ============================= slowest 10 durations =============================
  6.12s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  3.89s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.84s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  2.97s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.61s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.77s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.59s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.41s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.35s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1.27s call     tests/properties/test_i1_s4_p2_comparison.py::test_p2_guard_specific_domain_is_the_single_pair_and_it_fails_at_runtime
  921 passed in 97.45s (0:01:37)
  ```
- **scorecard**: `uv run python -m compileall -q src` exited 0 in 0.032s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this run environment; the client was invoked from a shell command and exited 3, so the two open choices (reuse the published word for a wrong number of arguments, and report a wrong count beside a wrong operand) were decided locally and recorded as DEC1 and DEC2 in the oracle record

## 3. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the change is the one table and one rule the decisions named: checker.py only, no new published category, service.py and syntax.py untouched
  - D2: pass - src/prova/checker.py:58 is the single table; the four operand groups and arity_of:1107 are derived from it, and a unit test holds it to the language list
  - D3: pass - the rule sits in the checker beside the other whole-program rules; it reads parsed syntax and writes diagnostics, and touches no transport, file or command code
  - D4: pass - src/prova/checker.py:39 the frozen BuiltinOperator carries the arity with the operand group, so an entry cannot say one without the other, and arity_of refuses an unknown name instead of defaulting; the operator itself stays the string the parser produces, which this change may not alter
  - D5: pass - src/prova/checker.py:73 _operators_of is one short derivation with one reason to change, and arity_of:1107 answers one question; the module keeps the procedural style of the file it sits in, as the paradigm of the touched code requires
  - D6: n/a: no pattern was introduced; a dict of value objects read by a guard clause is the simplest thing that works here
  - D7: pass - the words are the language own: operator, argument, takes exactly, got, and the refusal names the construct a reader repairs
  - D8: pass - no file, process, clock or transport is reached by the rule; the checker stays a pure function from a parsed program to diagnostics
  - D9: pass - tests/acceptance/_f7_operator_arity_fixtures.py:352 drives the real prova command over its JSON surface, and tests/properties/test_f7_operator_arity.py:98 uses the published request interface; the one unit test reads the checker own published table and nothing private
  - D10: pass - every name is a sentence about what a reader observes, with no production symbol beyond the published vocabulary the promise is about
  - D11: pass - one fixtures module owns the programs, the command runs and the two assertion helpers; no test re-implements them, and site_of works out a place from the program text the test wrote
  - D12: pass - tests/properties/test_f7_operator_arity.py:98 draws an operator and a count from none to six and observes both halves of the law; its companion observes that both counts are stated, and both failed on the pre-feature tree
  - D13: pass - ten files, 30 observations, nine runs of nine green, median 1.22 s, slowest single observation 0.07 s, recorded in the craft note with the method
  - D14: pass - each observation adds a distinct one: a single wrong call, 22 wrong calls answered in one pass, the three contract and clause places, the crash path, the manifest word, and the two generated laws
  - D15: pass - src/prova/checker.py:1128 says what failed, how many the operator takes, how many were given and that operators have no variable arity, at the place of the call; every added assertion carries what, why and how
  - D16: n/a: the rule compares two numbers inside one expression, with no state, protocol, concurrency or interruption for a model to explore, as DEC4 recorded
  - D17: fixed: the notes claimed 899 and 921, which were the counts before the rebase; measured again (932 on the tree this branch started from, 962 here, one failure in both belonging to another feature property generator) and restated in 6dacb88
- **independent_review**:
  - REV1 | reviewer=impl-review-f7 | findings=4 (verdict APPROVE at 8180a19, all non-blocking): operator names enumerated in three places; stale suite counts in the notes; no observation of a wrong count in a contract or a match clause; generated brief duplicating the record home and carrying a machine-local path | resolution=all four fixed - d5bbaeb one table with the groups and the arity derived from it plus a unit test holding it to the language list, 6dacb88 counts measured again and restated, 0b75c34 three refusals in a precondition, a postcondition and a match clause body with one nested control, and the brief regenerated with its path made repo-relative in the commit that closes this delivery

## 4. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
- **not_verified**:
  - The one failing test in the whole-suite run is not this feature: tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken draws a free binder name from any lower-case word of one to eight letters without excluding the word-shaped builtin operators, so when it draws and, or or not the tool refuses the binding correctly and the test reads that as a defect. It failed 5 of 10 runs here before its example database learned the case and 6 of 6 after, and it fails the same way on the commit this branch started from. Reported to its owner, not fixed here, and not re-verified as green.
  - The recorded edge case for an empty source was not re-recorded after the rule that a program is one or more declarations landed, so that one line of the oracle record contradicts the tool as it stands today.
  - docs/spec-trace.md still records this clause as missing. It is a snapshot measured at a named commit and already carried rows an earlier delivery overtook, so it was left to its owner and no row was rewritten.
  - No linter and no type checker are configured in this project, so the mechanical check compiles the package and nothing more. No style, typing or security claim is made.
  - The question service was unavailable for this run, the key being absent from the environment, so the two open choices were decided locally against the sibling rules and recorded as decisions rather than put to it.
  - The generated laws sample the eleven operators and counts from none to six. They are evidence over those bounds and over no larger program, not proof, and nothing was mutation tested beyond the three deliberate breaks named in the notes.
  - Nothing was pushed, nothing was merged, and the branch was not run in continuous integration; every figure here comes from this machine, on Python 3.12.13.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit 6dacb880cf41bc0b2d55b08eeef2506ec85b676d
  - no checks declared

## Not backed by the diff

- A builtin operator written with a number of arguments other than the one SPEC.md gives it is now refused, where it used to be accepted with the extras quietly ignored and where asking to run such a program stopped the command with no answer at all.: a guarantee names no test function of the change
- The refusal names the operator, says how many arguments it takes and how many the program gave, points at the call, and carries the word the manifest already publishes for a wrong number of arguments, so no new category was published and the manifest file was left alone.: a guarantee names no test function of the change
- One table in the checker now holds every operator with its number of arguments and the group whose operands it reads; the operand groups and the answer to how many it takes are derived from that table, and a unit test holds it to the language own list of operators so adding one to the language alone cannot make the checker raise a fault instead of answering.: a guarantee names no test function of the change
- Checked through the real command over its JSON surface for every operator, with a wrong count in a body, in a precondition, in a postcondition and in a match clause body, with controls that accept almost the same programs, and with two generated laws over the eleven operators and counts from none to six.: a guarantee names no test function of the change
- Three deliberate breaks were run and restored: refusing only extra arguments, switching the comparison off, and removing an operator from the table; each was caught.: a guarantee names no test function of the change
- One thing the next reader must know: the edge case recorded in the oracle as an empty source accepted with no diagnostics is stale, because the rule that a program is one or more declarations landed beside this work and now refuses an empty source for a reason of its own; the control that pinned it was moved onto a whole valid program that writes no operator anywhere, and the recorded edge line itself was not re-recorded.: a guarantee names no test function of the change
