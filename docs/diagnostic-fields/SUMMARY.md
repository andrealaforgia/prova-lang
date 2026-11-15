# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1007 tests, all green on main).
  - not-testable (challenge this): states the project and that its suite is green, a fact about the repository and not a promise of the tool.
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names the authority document to read; no observable behaviour follows from it alone.
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on this change, observed by running the 1007 tests already on main, which pass before and after.
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): a rule for the author of the change; it is discharged in the conflicts table and at the pause.
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): names a directory to ignore; nothing in the product observes it.
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): says where the work happens, which no answer of the tool shows.
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a rule about the commit message, not about the tool's behaviour.
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line of the commit message, not an observable of the product.
- S9: Do not push and do not merge.
  - not-testable (challenge this): a rule about git remotes, outside everything the tool answers.
- S10: Keep the full suite green.
  - not-testable (challenge this): a constraint on this change, observed by the existing suite, which passes before and after it.
- S11: No other delivery runs in parallel.
  - not-testable (challenge this): a fact about how the work is scheduled, not about the tool.
- S12: F2 to F9 are all on main; F10 changes the shared diagnostic type they add rows to, so read how each category is built before you design.
  - not-testable (challenge this): an instruction to read the existing construction sites before designing; its result is the conflicts table.
- S13: Keep existing category names, reasons and every field existing tests read: add fields, do not rename or remove.
  - not-testable (challenge this): a compatibility constraint on this change, observed by the 1007 existing tests, which read the categories, reasons and fields it protects.
- S14: If an existing test conflicts, stop and report.
  - not-testable (challenge this): a rule for the author of the change, discharged in the conflicts table and at the pause.
- S15: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): says where the author keeps scripts; nothing the tool answers shows it.
- S16: Decide what "source revision" means (the roadmap and SPEC.md lines 270-284 and 472-482 are the authority; the digest already published as source_digest is a candidate) and record the decision with its reason in your oracle note.
  - promises: P8
  - tests P8: test_two_sources_are_two_revisions_and_one_source_is_one
- S17: The unlocated diagnostics (recursive_type, unbound_type, and any others) must gain a position where the data has one; where the parsed tree keeps no position, say so as a stated limit.
  - promises: P6
  - tests P6: test_each_refusal_about_a_declaration_names_it_and_points_at_it
- S18: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell quoting and a clean working tree, which are properties of the author's session, not of the tool.
- S19: **Outcome.** A client can act on a failure without reading prose: which source
  - promises: P1, P8
  - tests P1: test_every_refusal_carries_the_revision_of_the_source_it_is_about
  - tests P8: test_two_sources_are_two_revisions_and_one_source_is_one
- S20: revision, which function or obligation, what was expected, what was found, and
  - promises: P1, P2
  - tests P1: test_every_refusal_carries_the_revision_of_the_source_it_is_about
  - tests P2: test_a_type_error_names_the_symbol_and_both_types
- S21: where.
  - promises: P3, P6
  - tests P3: test_a_refused_argument_says_where_in_the_argument_it_stands
  - tests P6: test_each_refusal_about_a_declaration_names_it_and_points_at_it
- S22: **Acceptance criteria**
  - not-testable (challenge this): a heading that introduces the list of criteria below it.
- S23: 1.
  - not-testable (challenge this): the number of the first list item, carrying no promise of its own.
- S24: Given any invalid program, when it is checked, then every diagnostic carries the
  - promises: P1
  - tests P1: test_every_refusal_carries_the_revision_of_the_source_it_is_about
- S25: source revision the answer is about.
  - promises: P1, P8
  - tests P1: test_every_refusal_carries_the_revision_of_the_source_it_is_about
  - tests P8: test_two_sources_are_two_revisions_and_one_source_is_one
- S26: 2.
  - not-testable (challenge this): the number of the second list item, carrying no promise of its own.
- S27: Given a type error, then the diagnostic names the symbol it is about and gives
  - promises: P2
  - tests P2: test_a_type_error_names_the_symbol_and_both_types
- S28: the expected and the actual type as separate fields.
  - promises: P2
  - tests P2: test_a_type_error_names_the_symbol_and_both_types
- S29: 3.
  - not-testable (challenge this): the number of the third list item, carrying no promise of its own.
- S30: Given a syntax error from the reader, then the diagnostic still carries a
  - promises: P3
  - tests P3: test_a_refused_argument_says_where_in_the_argument_it_stands
- S31: position.
  - promises: P3
  - tests P3: test_a_refused_argument_says_where_in_the_argument_it_stands
- S32: 4.
  - not-testable (challenge this): the number of the fourth list item, carrying no promise of its own.
- S33: Given the same failure with reworded prose, then the category and the fields are
  - promises: P4
  - tests P4: test_three_operations_answer_the_same_defect_with_the_same_fields
- S34: unchanged.
  - promises: P4
  - tests P4: test_three_operations_answer_the_same_defect_with_the_same_fields
- S35: 5.
  - not-testable (challenge this): the number of the fifth list item, carrying no promise of its own.
- S36: Given a repaired program, when it is checked again, then it is accepted and the
  - promises: P5
  - tests P5: test_the_repaired_program_is_accepted_with_the_revision_of_its_new_text
- S37: revision in the answer is the new one.
  - promises: P5, P8
  - tests P5: test_the_repaired_program_is_accepted_with_the_revision_of_its_new_text
  - tests P8: test_two_sources_are_two_revisions_and_one_source_is_one
- S38: **SPEC.md** lines 472-482, 270-278 (provenance).
  - promises: P7, P8
  - tests P7: test_the_manifest_describes_every_category_it_publishes
  - tests P8: test_two_sources_are_two_revisions_and_one_source_is_one
- S39: **Dependencies** F2-F9: it changes the diagnostic type those features add rows to,
  - not-testable (challenge this): says which features this one changes the shared type of, a fact about the order of the work.
- S40: so doing it first means redoing it.
  - not-testable (challenge this): gives the reason for that order, which no answer of the tool shows.
- S41: **Size** M.
  - not-testable (challenge this): declares the size of the delivery, which is recorded in the workspace, not in the product.
- S42: **Touches** `src/prova/checker.py` (the diagnostic type), `src/prova/service.py`,
  - not-testable (challenge this): names the files the change is expected to touch, not a behaviour a client observes.
- S43: tests.
  - not-testable (challenge this): continues the list of files the change touches; no observable behaviour.
- S44: **Why it is a real expectation** probes S4, S6 disagree; probe S5 shows location is
  - promises: P6
  - tests P6: test_each_refusal_about_a_declaration_names_it_and_points_at_it
- S45: only partly present.
  - promises: P3, P6
  - tests P3: test_a_refused_argument_says_where_in_the_argument_it_stands
  - tests P6: test_each_refusal_about_a_declaration_names_it_and_points_at_it

## Edge matrix

- I1.empty: the source '' => one syntax refusal placed at line 1 column 1, carrying the revision of the empty text | self-probe: not probed | pre-feature not probed
- I1.unknown: a signature naming the type 'Cents', which no declaration gives => one unbound_type refusal naming 'Cents', placed at the declaration it stands in | self-probe: not probed | pre-feature not probed
- I1.malformed: the source '(defn fare' with 1 form left unclosed => one syntax refusal placed at line 1 column 1 | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: a body calling a function no declaration gives => one unbound_name refusal placed at the call, and no crash | self-probe: not probed | pre-feature not probed
- I1.repeated: the same source checked twice => 2 identical answers carrying the same revision; nothing is kept between them | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): the command answers one request per process and keeps no state between runs, so 2 runs share nothing to overlap on
- I1.crash: n/a (challenge this): the command writes no file and keeps no state, so an interrupted run leaves nothing half-written
- I2.empty: the argument text '' => one malformed_value refusal placed at line 1 column 1 of that argument | self-probe: not probed | pre-feature not probed
- I2.unknown: the function name 'nope', which the program does not declare => one unknown_function refusal naming 'nope' and carrying the revision of the source | self-probe: not probed | pre-feature not probed
- I2.malformed: the argument text '(' => one malformed_value refusal placed at line 1 column 1 | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: a source whose body calls an undeclared function => the refusal of the check comes first with its place, and no evaluation is attempted | self-probe: not probed | pre-feature not probed
- I2.repeated: the same evaluate request sent twice => 2 identical answers carrying the same revision | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): one request per process and no shared state, so 2 evaluations cannot overlap on anything
- I2.crash: n/a (challenge this): evaluation writes nothing, so there is nothing to leave half-written
- I3.empty: a discover request carrying no source at all => the manifest is answered, with 1 schema for each published category | self-probe: not probed | pre-feature not probed
- I3.unknown: the operation name 'fly', which the tool does not know => one unknown_operation refusal carrying no revision, because no source was submitted | self-probe: not probed | pre-feature not probed
- I3.malformed: a request body that is not JSON => the command answers status 'tool_failure' and exits 1, exactly as it does today | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): the manifest is computed from the tool's own tables and reads nothing outside the process
- I3.repeated: discover called twice => 2 identical manifests | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): one request per process and nothing shared, so 2 manifests cannot interfere
- I3.crash: n/a (challenge this): discover writes nothing, so an interrupted run leaves nothing behind
- I4.empty: the source '' => the same 1 syntax refusal the check operation gives, with the same fields | self-probe: not probed | pre-feature not probed
- I4.unknown: an example value naming the constructor 'Cash', which no type declares => one unbound_constructor refusal naming 'Cash', placed at the declaration | self-probe: not probed | pre-feature not probed
- I4.malformed: the shipped program cut short after 20 characters => one syntax refusal placed where the reader stopped | self-probe: not probed | pre-feature not probed
- I4.dependency-gone: a body calling an undeclared function => one unbound_name refusal, identical in all 3 source-reading operations | self-probe: not probed | pre-feature not probed
- I4.repeated: 1 defective source sent to check, examples and verify => the 3 answers carry the identical fields | self-probe: not probed | pre-feature not probed
- I4.concurrent: n/a (challenge this): one request per process, so 2 of these operations share no state to overlap on
- I4.crash: n/a (challenge this): neither operation writes anything, so nothing can be left half-written

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the 9 refused programs of the F10 fixtures, each holding exactly 1 defect
  - WHEN each is checked
  - THEN every diagnostic carries source_revision equal to the SHA-256 the test computes from the submitted text
  - test: test_every_refusal_carries_the_revision_of_the_source_it_is_about
- SC2 (P8): not-held (no held self-probe case)
  - GIVEN 2 programs differing by 1 word, with bodies '(+ cents true)' and '(+ cents false)'
  - WHEN both are checked and the first is checked again
  - THEN the 2 refusals carry 2 different revisions and the repeat carries the first revision again
  - test: test_two_sources_are_two_revisions_and_one_source_is_one
- SC3 (P2): not-held (no held self-probe case)
  - GIVEN a function whose body has type Int under the declared return type 'Bool'
  - WHEN it is checked
  - THEN the refusal carries symbol 'fare', expected 'Bool' and actual 'Int' as 3 separate fields
  - test: test_the_two_types_are_separate_fields_not_one_sentence
- SC4 (P2): not-held (no held self-probe case)
  - GIVEN a call '(flagged cents)' whose parameter 'flag' is declared Bool and whose argument is Int
  - WHEN it is checked
  - THEN the refusal carries symbol 'flagged.flag', expected 'Bool' and actual 'Int'
  - test: test_a_type_error_names_the_symbol_and_both_types
- SC5 (P3): not-held (no held self-probe case)
  - GIVEN the argument text '1 2', which holds 2 values where 1 is read
  - WHEN fare is evaluated with it
  - THEN the refusal is placed at line 1 column 3, where the second value stands
  - test: test_a_refused_argument_says_where_in_the_argument_it_stands
- SC6 (P3): not-held (no held self-probe case)
  - GIVEN the source '(defn fare' with 1 form left unclosed
  - WHEN it is checked
  - THEN the refusal is placed at line 1 column 1 and carries the revision of that text
  - test: test_a_refused_source_still_says_where_it_stands
- SC7 (P4): not-held (no held self-probe case)
  - GIVEN 1 program whose body type is not its declared return type
  - WHEN it is checked, its examples are run and it is verified
  - THEN the 3 answers carry the identical 6 fields
  - test: test_three_operations_answer_the_same_defect_with_the_same_fields
- SC8 (P4): not-held (no held self-probe case)
  - GIVEN the same defect in a source that declares 1 more unrelated function after it
  - WHEN it is checked
  - THEN only source_revision differs and the other 5 fields are unchanged
  - test: test_other_text_in_the_source_does_not_change_the_fields
- SC9 (P5): not-held (no held self-probe case)
  - GIVEN 1 program refused for a type error and the same program with its return type repaired to 'Int'
  - WHEN the repaired text is checked
  - THEN the status is 'completed' and source_digest is the SHA-256 of the repaired text, not of the refused one
  - test: test_the_repaired_program_is_accepted_with_the_revision_of_its_new_text
- SC10 (P6): not-held (no held self-probe case)
  - GIVEN the 6 programs whose refusal carried no place at all, 1 for each of unbound_type, recursive_type, cyclic_dependency, unrelated_example, arity_mismatch and unbound_constructor
  - WHEN each is checked
  - THEN each of the 6 refusals names its symbol and stands at the line and column of its own declaration
  - test: test_each_refusal_about_a_declaration_names_it_and_points_at_it
- SC11 (P6): not-held (no held self-probe case)
  - GIVEN an example passing 2 arguments to a function that declares 1 parameter
  - WHEN it is checked
  - THEN the refusal carries expected 1 and actual 2 as numbers
  - test: test_an_example_counted_wrong_says_how_many_were_expected_and_found
- SC12 (P7): not-held (no held self-probe case)
  - GIVEN the manifest the discover operation answers, which publishes 22 categories
  - WHEN it is read
  - THEN each of the 22 published categories has a schema naming its fields, its place and whether it carries a revision
  - test: test_the_manifest_describes_every_category_it_publishes
- SC13 (P7): not-held (no held self-probe case)
  - GIVEN the 9 refused programs of the F10 fixtures
  - WHEN each is checked
  - THEN every field of every refusal is 1 the schema of its category names, and no named field is missing
  - test: test_every_refusal_matches_the_schema_published_for_its_category
- SC14 (P1): not-held (no held self-probe case)
  - GIVEN the shipped hour-clock program mutated at a drawn position, crossed with the 4 operations that read source
  - WHEN each mutation is submitted
  - THEN every diagnostic carries the revision of that exact text, computed in the test as SHA-256
  - test: test_law1_every_diagnostic_says_which_text_it_is_about

## Questions for the owner

- S24: Should every diagnostic carry the revision of the submitted text, including the refusals of a source the tool never checked through, with the top-level source_digest still absent there?
  - existing behaviour: tests/acceptance/test_f9_b5_an_unsupported_refusal_claims_nothing_more.py requires an out-of-profile refusal to carry no digest of a source the tool did not check through; it pins the absence at the top level only, so stamping the revision inside the diagnostic keeps it passing but goes against the sentence its docstring states.
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- A docs/f16fix/DECISIONS.md (+13 -0 lines)
- A docs/f16fix/SUMMARY.md (+454 -0 lines)
- A docs/f16fix/TRACE.md (+7 -0 lines)
- A docs/feature/diagnostic-fields/craft.md (+106 -0 lines)
- A docs/feature/diagnostic-fields/design.md (+121 -0 lines)
- A docs/feature/diagnostic-fields/oracle.md (+100 -0 lines)
- A docs/feature/f16fix/craft.md (+85 -0 lines)
- A docs/feature/f16fix/handoff.md (+57 -0 lines)
- A docs/feature/f16fix/oracle.md (+71 -0 lines)
- A docs/feature/f16fix/selfreview.md (+99 -0 lines)
- M src/prova/checker.py (+419 -44 lines)
- M src/prova/obligations.py (+37 -4 lines)
- M src/prova/reader.py (+16 -4 lines)
- M src/prova/service.py (+239 -67 lines)
- A tests/acceptance/_f10_diagnostic_fixtures.py (+428 -0 lines)
- A tests/acceptance/test_f10_b1_every_refusal_names_the_revision_of_its_source.py (+72 -0 lines)
- A tests/acceptance/test_f10_b2_a_type_error_names_its_symbol_expected_and_actual.py (+60 -0 lines)
- A tests/acceptance/test_f10_b3_a_reader_refusal_still_says_where.py (+119 -0 lines)
- A tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py (+101 -0 lines)
- A tests/acceptance/test_f10_b5_a_repaired_program_is_accepted_with_its_new_revision.py (+65 -0 lines)
- A tests/acceptance/test_f10_b6_a_refusal_about_a_declaration_says_where_it_stands.py (+66 -0 lines)
- A tests/acceptance/test_f10_b7_the_manifest_says_what_each_refusal_carries.py (+79 -0 lines)
- A tests/acceptance/test_f10_b8_the_published_granularity_is_what_the_places_are.py (+95 -0 lines)
- A tests/acceptance/test_f10_b9_a_source_that_is_not_text_is_refused.py (+83 -0 lines)
- M tests/acceptance/test_verify_lists_the_obligations_owed.py (+187 -10 lines)
- A tests/properties/test_f10_diagnostic_fields.py (+194 -0 lines)
- M tests/properties/test_obligation_inventory_laws.py (+146 -5 lines)
- A tests/unit/test_diagnostic_refuses_what_its_kind_does_not_declare.py (+148 -0 lines)

## Commits (git log, BASE to HEAD)

- bd12621 [F16fix] notice when a call position loses its obligation
- e9163f4 [F16fix] record what the obligation tests now notice
- 23639bd [F16fix] state the condition a contract call is really reached under
- fde357c [F16fix] carry a function's own precondition into what its body owes
- b171e36 [F16fix] record the rule the Owner decided to apply
- 5498173 [F16fix] close the record with the review and what it left open
- 626f9be [F10] give every refusal one builder, before changing what it carries
- b4cba63 [F10] state what a diagnostic must carry, as checks that fail
- 00ad63c [F10] decide where it is said what a refusal carries
- 9712e47 [F10] say which revision, which symbol, expected and actual
- fe0b519 [F10] keep the laws off a crash that is older than them
- 0af2202 [F10] write down what the change cost and what it left alone
- bcec4ec [F10] refuse a source that is not text, and say which text a place is in
- ca7236a [F10] measure the record against the commits it describes

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f10/request.md
- **promises**:
  - P1: Every diagnostic a source-reading operation answers with carries the revision of the exact source text the request submitted.
  - P2: A type error names the symbol it is about and carries the expected and the actual type as two separate fields.
  - P3: A refusal that comes from the reader carries the place the reader stopped at, for a source and for a value supplied as an argument.
  - P4: The category and the structured fields of a refusal belong to the defect, not to its prose: the same defect answered by any operation, in any surrounding text, carries the same category and the same fields.
  - P5: A repaired program is accepted and the answer binds to the revision of the repaired text, not of the text that was refused.
  - P6: A refusal about a declaration names its symbol and carries the place of the declaration it is about; where the parsed tree keeps no finer place, the manifest says the place is the declaration's.
  - P7: The manifest publishes, for every diagnostic category, the fields a refusal of that category carries, whether it is placed and whether it carries a revision.
  - P8: The revision of a source is the SHA-256 of the exact bytes submitted, the value the tool already publishes as source_digest, so a client recomputes it without the tool.
- **sentence_map**:
  - S1 => not-testable: states the project and that its suite is green, a fact about the repository and not a promise of the tool.
  - S2 => not-testable: names the authority document to read; no observable behaviour follows from it alone.
  - S3 => not-testable: a constraint on this change, observed by running the 1007 tests already on main, which pass before and after.
  - S4 => not-testable: a rule for the author of the change; it is discharged in the conflicts table and at the pause.
  - S5 => not-testable: names a directory to ignore; nothing in the product observes it.
  - S6 => not-testable: says where the work happens, which no answer of the tool shows.
  - S7 => not-testable: a rule about the commit message, not about the tool's behaviour.
  - S8 => not-testable: the attribution line of the commit message, not an observable of the product.
  - S9 => not-testable: a rule about git remotes, outside everything the tool answers.
  - S10 => not-testable: a constraint on this change, observed by the existing suite, which passes before and after it.
  - S11 => not-testable: a fact about how the work is scheduled, not about the tool.
  - S12 => not-testable: an instruction to read the existing construction sites before designing; its result is the conflicts table.
  - S13 => not-testable: a compatibility constraint on this change, observed by the 1007 existing tests, which read the categories, reasons and fields it protects.
  - S14 => not-testable: a rule for the author of the change, discharged in the conflicts table and at the pause.
  - S15 => not-testable: says where the author keeps scripts; nothing the tool answers shows it.
  - S16 => P8
  - S17 => P6
  - S18 => not-testable: shell quoting and a clean working tree, which are properties of the author's session, not of the tool.
  - S19 => P1,P8
  - S20 => P1,P2
  - S21 => P3,P6
  - S22 => not-testable: a heading that introduces the list of criteria below it.
  - S23 => not-testable: the number of the first list item, carrying no promise of its own.
  - S24 => P1
  - S25 => P1,P8
  - S26 => not-testable: the number of the second list item, carrying no promise of its own.
  - S27 => P2
  - S28 => P2
  - S29 => not-testable: the number of the third list item, carrying no promise of its own.
  - S30 => P3
  - S31 => P3
  - S32 => not-testable: the number of the fourth list item, carrying no promise of its own.
  - S33 => P4
  - S34 => P4
  - S35 => not-testable: the number of the fifth list item, carrying no promise of its own.
  - S36 => P5
  - S37 => P5,P8
  - S38 => P7,P8
  - S39 => not-testable: says which features this one changes the shared type of, a fact about the order of the work.
  - S40 => not-testable: gives the reason for that order, which no answer of the tool shows.
  - S41 => not-testable: declares the size of the delivery, which is recorded in the workspace, not in the product.
  - S42 => not-testable: names the files the change is expected to touch, not a behaviour a client observes.
  - S43 => not-testable: continues the list of files the change touches; no observable behaviour.
  - S44 => P6
  - S45 => P3,P6
- **scenarios**:
  - SC1 | P1 | GIVEN the 9 refused programs of the F10 fixtures, each holding exactly 1 defect | WHEN each is checked | THEN every diagnostic carries source_revision equal to the SHA-256 the test computes from the submitted text
  - SC2 | P8 | GIVEN 2 programs differing by 1 word, with bodies '(+ cents true)' and '(+ cents false)' | WHEN both are checked and the first is checked again | THEN the 2 refusals carry 2 different revisions and the repeat carries the first revision again
  - SC3 | P2 | GIVEN a function whose body has type Int under the declared return type 'Bool' | WHEN it is checked | THEN the refusal carries symbol 'fare', expected 'Bool' and actual 'Int' as 3 separate fields
  - SC4 | P2 | GIVEN a call '(flagged cents)' whose parameter 'flag' is declared Bool and whose argument is Int | WHEN it is checked | THEN the refusal carries symbol 'flagged.flag', expected 'Bool' and actual 'Int'
  - SC5 | P3 | GIVEN the argument text '1 2', which holds 2 values where 1 is read | WHEN fare is evaluated with it | THEN the refusal is placed at line 1 column 3, where the second value stands
  - SC6 | P3 | GIVEN the source '(defn fare' with 1 form left unclosed | WHEN it is checked | THEN the refusal is placed at line 1 column 1 and carries the revision of that text
  - SC7 | P4 | GIVEN 1 program whose body type is not its declared return type | WHEN it is checked, its examples are run and it is verified | THEN the 3 answers carry the identical 6 fields
  - SC8 | P4 | GIVEN the same defect in a source that declares 1 more unrelated function after it | WHEN it is checked | THEN only source_revision differs and the other 5 fields are unchanged
  - SC9 | P5 | GIVEN 1 program refused for a type error and the same program with its return type repaired to 'Int' | WHEN the repaired text is checked | THEN the status is 'completed' and source_digest is the SHA-256 of the repaired text, not of the refused one
  - SC10 | P6 | GIVEN the 6 programs whose refusal carried no place at all, 1 for each of unbound_type, recursive_type, cyclic_dependency, unrelated_example, arity_mismatch and unbound_constructor | WHEN each is checked | THEN each of the 6 refusals names its symbol and stands at the line and column of its own declaration
  - SC11 | P6 | GIVEN an example passing 2 arguments to a function that declares 1 parameter | WHEN it is checked | THEN the refusal carries expected 1 and actual 2 as numbers
  - SC12 | P7 | GIVEN the manifest the discover operation answers, which publishes 22 categories | WHEN it is read | THEN each of the 22 published categories has a schema naming its fields, its place and whether it carries a revision
  - SC13 | P7 | GIVEN the 9 refused programs of the F10 fixtures | WHEN each is checked | THEN every field of every refusal is 1 the schema of its category names, and no named field is missing
  - SC14 | P1 | GIVEN the shipped hour-clock program mutated at a drawn position, crossed with the 4 operations that read source | WHEN each mutation is submitted | THEN every diagnostic carries the revision of that exact text, computed in the test as SHA-256
- **conflicts**:
  - S1 | NONE | the suite on main is green and names 1007 tests; nothing in it contradicts a sentence that only states that fact.
  - S2 | NONE | SPEC.md lines 270-284 and 472-482 require provenance and diagnostic schemas; the tool publishes neither yet, so the authority asks for more, it does not contradict.
  - S3 | NONE | checked every test that reads a diagnostic: none compares a whole diagnostic or a key set, so adding fields changes no expected result.
  - S4 | NONE | a rule for the author; the one near-conflict found is recorded against S24 below and asked at the pause.
  - S5 | NONE | the .relay directory holds no code the tool reads and no test imports it; ignoring it contradicts nothing.
  - S6 | NONE | the worktree is a checkout of the same branch; no behaviour of the tool depends on where it stands.
  - S7 | NONE | nothing in the repository constrains the commit message beyond what this sentence asks.
  - S8 | NONE | no hook or test in this worktree reads the attribution line; there is nothing for it to contradict.
  - S9 | NONE | no test or tool in the repository pushes or merges, so the prohibition contradicts nothing.
  - S10 | NONE | ran the whole suite before the change: 1007 passed, so the green it asks to keep is the state it starts from.
  - S11 | NONE | the worktree holds one branch and no other delivery writes to it; nothing contradicts the sentence.
  - S12 | NONE | read every construction site of checker.Diagnostic and of the diagnostic dicts in service.py before designing; the categories are built in 5 places and none forbids a new field.
  - S13 | NONE | tests/properties/test_i1_s4_p6_transcript.py pins the top-level response keys to exactly 6, so no top-level field is added; inside a diagnostic no test pins the key set, so added fields break nothing.
  - S14 | NONE | the same rule as S4; the one near-conflict is recorded against S24 and carried to the pause.
  - S15 | NONE | the scripts of this run live under the workspace in f10-exec; no test reads them.
  - S16 | NONE | the tool already publishes source_digest as the SHA-256 of the submitted source, so naming that value the revision agrees with what exists instead of contradicting it.
  - S17 | NONE | probed the 6 unlocated categories: each is about a declaration whose name position the parsed tree keeps, so a place can be given without changing any existing placed refusal.
  - S18 | NONE | a rule about the author's shell; nothing in the repository contradicts it.
  - S19 | NONE | the answer already names the source by digest for an accepted program, so saying which source a failure is about extends that, it does not contradict it.
  - S20 | NONE | the reasons already name the function and both types in prose; lifting them into fields contradicts no test, because no test pins a diagnostic's key set.
  - S21 | NONE | 14 of the 22 categories are already placed and keep their places unchanged; the sentence asks the remaining ones to be placed too.
  - S22 | NONE | a heading; there is no behaviour it could contradict.
  - S23 | NONE | a list number; there is no behaviour it could contradict.
  - S24 | CONFLICT | tests/acceptance/test_f9_b5_an_unsupported_refusal_claims_nothing_more.py requires an out-of-profile refusal to carry no digest of a source the tool did not check through; it pins the absence at the top level only, so stamping the revision inside the diagnostic keeps it passing but goes against the sentence its docstring states. | Should every diagnostic carry the revision of the submitted text, including the refusals of a source the tool never checked through, with the top-level source_digest still absent there?
  - S25 | NONE | the phrase names the same revision as S24 and adds no further constraint that any existing behaviour contradicts.
  - S26 | NONE | a list number; there is no behaviour it could contradict.
  - S27 | NONE | no existing test reads a symbol field, because none exists; the reasons that name symbols are unchanged.
  - S28 | NONE | checked the 11 type_mismatch construction sites: each already holds both types, so reporting them separately contradicts nothing.
  - S29 | NONE | a list number; there is no behaviour it could contradict.
  - S30 | NONE | every syntax refusal of a source is already placed; the gap is the reader refusal of a supplied argument, which no test pins as unplaced.
  - S31 | NONE | fuzzed 200 mutated sources: all 113 syntax refusals carried a place, so adding a place where one is missing contradicts no observed behaviour.
  - S32 | NONE | a list number; there is no behaviour it could contradict.
  - S33 | NONE | the three source-reading operations already share one refusal builder, so equal fields across them agrees with what exists.
  - S34 | NONE | no test pins a reason to a category, so holding the fields steady while the prose is free contradicts nothing.
  - S35 | NONE | a list number; there is no behaviour it could contradict.
  - S36 | NONE | an accepted answer already carries source_digest of the text it read, which is what this sentence asks for.
  - S37 | NONE | the digest of an accepted answer already changes with the text, so the new revision agrees with the existing behaviour.
  - S38 | NONE | SPEC.md line 472 requires the manifest to list diagnostic schemas and it lists only category names today, so the authority asks for more rather than contradicting.
  - S39 | NONE | F2 to F9 are on main and their tests pass; none of them pins the shape of a diagnostic, only its category and its reason.
  - S40 | NONE | a statement about ordering the work; no behaviour of the tool contradicts it.
  - S41 | NONE | the declared size is recorded in the workspace and contradicts nothing in the repository.
  - S42 | NONE | checker.py owns the diagnostic type and service.py renders it, which is where the change falls; nothing contradicts that.
  - S43 | NONE | tests are added, never edited, so naming them as touched contradicts no existing expected result.
  - S44 | NONE | probed both: a type error carries no symbol field and a recursive type carries no place, so the probes that disagree describe the gap this feature closes.
  - S45 | NONE | measured it: 14 of 22 categories are placed and 6 that are about a declaration are not, so 'only partly present' matches what the tool does today.
- **decisions**:
  - S24: stamp source_revision inside every diagnostic about a submitted source, including a refusal of a source the tool never checked through, and leave the top-level source_digest absent there exactly as today. A revision identifies which text the complaint is about and claims nothing about that text, which is what SPEC.md line 472 requires of a diagnostic, while the absent top-level digest keeps saying the tool did not check the source through. Carried to the pause as the one question for the owner.
  - DEC1: the source revision is the lowercase hexadecimal SHA-256 of the exact UTF-8 bytes of the source the request submitted, which is the value the tool already publishes as source_digest. SPEC.md lines 270-278 name source digests as the provenance of a result and lines 476-482 bind results to source revisions so stale evidence cannot certify a changed artefact. A content digest changes exactly when the text changes, needs no repository, clock or counter, and a client recomputes it from what it sent.
  - DEC2: no new top-level response field. tests/properties/test_i1_s4_p6_transcript.py pins the top-level keys of an answer to exactly six, so the answer-level revision stays source_digest and the diagnostic-level one is the new source_revision.
  - DEC3: a refusal about a declaration takes the place of the declared name it is about, because the parsed tree keeps no place for a type written inside a signature or a record field, for an example of its own, or for a value inside an example. The manifest publishes the granularity for each category, so a client is never told that a place is the offending word when it is the declaration.
  - DEC4: operation_unavailable and unknown_operation carry no revision, because no source was submitted for them to be about; the manifest publishes that as never.
  - DEC5: expected and actual carry a type name for type_mismatch and a count for arity_mismatch, and the manifest publishes the kind for each category, so one field name never means two things to a client that read the schema.
  - DEC6: a place on a malformed_value points into the argument text the request supplied, not into the source; the manifest publishes what each category's place points into.
  - DEC7: Jev is authorized for this run but unavailable: TYPESAFE_API_KEY is absent from the environment and the client exits 3. The four open semantic questions prepared for it (revision in a refusal of an unread source, the shape of the symbol field, expected and actual for counts, and a declaration place for an unlocated refusal) were decided locally and recorded above as S24, DEC5, DEC3.
  - DEC8: no formal model. F10 adds fields to an answer computed in one pass from one request; there is no state kept between requests, no protocol, no concurrency and nothing written, so a Quint model would have nothing to explore.
- **mapping**:
  - P1 => test_every_refusal_carries_the_revision_of_the_source_it_is_about
  - P2 => test_a_type_error_names_the_symbol_and_both_types
  - P3 => test_a_refused_argument_says_where_in_the_argument_it_stands
  - P4 => test_three_operations_answer_the_same_defect_with_the_same_fields
  - P5 => test_the_repaired_program_is_accepted_with_the_revision_of_its_new_text
  - P6 => test_each_refusal_about_a_declaration_names_it_and_points_at_it
  - P7 => test_the_manifest_describes_every_category_it_publishes
  - P8 => test_two_sources_are_two_revisions_and_one_source_is_one
- **covers_scenarios**:
  - SC1 => test_every_refusal_carries_the_revision_of_the_source_it_is_about
  - SC2 => test_two_sources_are_two_revisions_and_one_source_is_one
  - SC3 => test_the_two_types_are_separate_fields_not_one_sentence
  - SC4 => test_a_type_error_names_the_symbol_and_both_types
  - SC5 => test_a_refused_argument_says_where_in_the_argument_it_stands
  - SC6 => test_a_refused_source_still_says_where_it_stands
  - SC7 => test_three_operations_answer_the_same_defect_with_the_same_fields
  - SC8 => test_other_text_in_the_source_does_not_change_the_fields
  - SC9 => test_the_repaired_program_is_accepted_with_the_revision_of_its_new_text
  - SC10 => test_each_refusal_about_a_declaration_names_it_and_points_at_it
  - SC11 => test_an_example_counted_wrong_says_how_many_were_expected_and_found
  - SC12 => test_the_manifest_describes_every_category_it_publishes
  - SC13 => test_every_refusal_matches_the_schema_published_for_its_category
  - SC14 => test_law1_every_diagnostic_says_which_text_it_is_about
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
  - SC13 => base differs
  - SC14 => base differs
- **interfaces**:
  - I1: the prova command's JSON check operation, read from standard input and answered on standard output.
  - I2: the prova command's JSON evaluate operation, which reads a source and the values the request supplies as arguments.
  - I3: the prova command's JSON discover operation, the manifest a client reads the answer vocabulary from.
  - I4: the prova command's JSON examples and verify operations, the other two that read source and answer with the same diagnostics.
- **matrix**:
  - I1.empty => the source '' => one syntax refusal placed at line 1 column 1, carrying the revision of the empty text
  - I1.unknown => a signature naming the type 'Cents', which no declaration gives => one unbound_type refusal naming 'Cents', placed at the declaration it stands in
  - I1.malformed => the source '(defn fare' with 1 form left unclosed => one syntax refusal placed at line 1 column 1
  - I1.dependency-gone => a body calling a function no declaration gives => one unbound_name refusal placed at the call, and no crash
  - I1.repeated => the same source checked twice => 2 identical answers carrying the same revision; nothing is kept between them
  - I1.concurrent => n/a: the command answers one request per process and keeps no state between runs, so 2 runs share nothing to overlap on
  - I1.crash => n/a: the command writes no file and keeps no state, so an interrupted run leaves nothing half-written
  - I2.empty => the argument text '' => one malformed_value refusal placed at line 1 column 1 of that argument
  - I2.unknown => the function name 'nope', which the program does not declare => one unknown_function refusal naming 'nope' and carrying the revision of the source
  - I2.malformed => the argument text '(' => one malformed_value refusal placed at line 1 column 1
  - I2.dependency-gone => a source whose body calls an undeclared function => the refusal of the check comes first with its place, and no evaluation is attempted
  - I2.repeated => the same evaluate request sent twice => 2 identical answers carrying the same revision
  - I2.concurrent => n/a: one request per process and no shared state, so 2 evaluations cannot overlap on anything
  - I2.crash => n/a: evaluation writes nothing, so there is nothing to leave half-written
  - I3.empty => a discover request carrying no source at all => the manifest is answered, with 1 schema for each published category
  - I3.unknown => the operation name 'fly', which the tool does not know => one unknown_operation refusal carrying no revision, because no source was submitted
  - I3.malformed => a request body that is not JSON => the command answers status 'tool_failure' and exits 1, exactly as it does today
  - I3.dependency-gone => n/a: the manifest is computed from the tool's own tables and reads nothing outside the process
  - I3.repeated => discover called twice => 2 identical manifests
  - I3.concurrent => n/a: one request per process and nothing shared, so 2 manifests cannot interfere
  - I3.crash => n/a: discover writes nothing, so an interrupted run leaves nothing behind
  - I4.empty => the source '' => the same 1 syntax refusal the check operation gives, with the same fields
  - I4.unknown => an example value naming the constructor 'Cash', which no type declares => one unbound_constructor refusal naming 'Cash', placed at the declaration
  - I4.malformed => the shipped program cut short after 20 characters => one syntax refusal placed where the reader stopped
  - I4.dependency-gone => a body calling an undeclared function => one unbound_name refusal, identical in all 3 source-reading operations
  - I4.repeated => 1 defective source sent to check, examples and verify => the 3 answers carry the identical fields
  - I4.concurrent => n/a: one request per process, so 2 of these operations share no state to overlap on
  - I4.crash => n/a: neither operation writes anything, so nothing can be left half-written
- **laws**:
  - LAW1 | every diagnostic a source-reading operation answers with carries the revision of the exact source submitted, which is the SHA-256 of its bytes | generator=test_law1_every_diagnostic_says_which_text_it_is_about | observation=over mutations of the shipped hour-clock program crossed with check, examples, verify and evaluate, every diagnostic's source_revision equals the digest the test computes from the submitted text | mutant=a construction site that builds a diagnostic without stamping the revision, or stamps the digest of a different text
  - LAW2 | every diagnostic carries exactly the fields the manifest publishes for its category: nothing undeclared and nothing missing | generator=test_law2_every_diagnostic_carries_the_fields_its_category_publishes | observation=for every diagnostic drawn, the key set minus category and reason equals the set its published schema names | mutant=a field added at one construction site and not to the schema, or a category answered that the manifest does not publish
  - LAW3 | a category the manifest declares always placed carries a place, and every place carried stands in the text, counted from line 1 and column 1 | generator=test_law3_a_placed_diagnostic_stands_somewhere_in_the_text | observation=for every diagnostic drawn, a category published as always placed has a location, and no location has line 0 or column 0 | mutant=a refusal placed at line 0 column 0 when the reader did not find the place, or a published always-placed category left unplaced
- **messages**:
  - MSG0 | none: F10 adds no refusal and rewords none. Every refusal keeps the sentence the rule that owns it writes, and this feature adds only the structured fields beside that sentence, so there is no new message to state.
- **red**: `uv run pytest -q tests/acceptance/test_f10_b1_every_refusal_names_the_revision_of_its_source.py tests/acceptance/test_f10_b2_a_type_error_names_its_symbol_expected_and_actual.py tests/acceptance/test_f10_b3_a_reader_refusal_still_says_where.py tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py tests/acceptance/test_f10_b5_a_repaired_program_is_accepted_with_its_new_revision.py tests/acceptance/test_f10_b6_a_refusal_about_a_declaration_says_where_it_stands.py tests/acceptance/test_f10_b7_the_manifest_says_what_each_refusal_carries.py tests/properties/test_f10_diagnostic_fields.py` exited 1 in 2.598s
  - failing on the pre-feature tree (19): tests/acceptance/test_f10_b1_every_refusal_names_the_revision_of_its_source.py::test_every_refusal_carries_the_revision_of_the_source_it_is_about, tests/acceptance/test_f10_b1_every_refusal_names_the_revision_of_its_source.py::test_two_sources_are_two_revisions_and_one_source_is_one, tests/acceptance/test_f10_b2_a_type_error_names_its_symbol_expected_and_actual.py::test_a_type_error_names_the_symbol_and_both_types, tests/acceptance/test_f10_b2_a_type_error_names_its_symbol_expected_and_actual.py::test_the_two_types_are_separate_fields_not_one_sentence, tests/acceptance/test_f10_b3_a_reader_refusal_still_says_where.py::test_a_refused_argument_says_where_in_the_argument_it_stands, tests/acceptance/test_f10_b3_a_reader_refusal_still_says_where.py::test_a_refused_source_still_says_where_it_stands, tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py::test_three_operations_answer_the_same_defect_with_the_same_fields, tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py::test_other_text_in_the_source_does_not_change_the_fields, tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py::test_two_different_defects_do_not_carry_the_same_fields, tests/acceptance/test_f10_b5_a_repaired_program_is_accepted_with_its_new_revision.py::test_the_repaired_program_is_accepted_with_the_revision_of_its_new_text, tests/acceptance/test_f10_b5_a_repaired_program_is_accepted_with_its_new_revision.py::test_the_refused_text_is_still_refused_after_the_repair, tests/acceptance/test_f10_b6_a_refusal_about_a_declaration_says_where_it_stands.py::test_each_refusal_about_a_declaration_names_it_and_points_at_it, tests/acceptance/test_f10_b6_a_refusal_about_a_declaration_says_where_it_stands.py::test_an_example_counted_wrong_says_how_many_were_expected_and_found, tests/acceptance/test_f10_b7_the_manifest_says_what_each_refusal_carries.py::test_the_manifest_describes_every_category_it_publishes, tests/acceptance/test_f10_b7_the_manifest_says_what_each_refusal_carries.py::test_every_refusal_matches_the_schema_published_for_its_category, tests/properties/test_f10_diagnostic_fields.py::test_law1_every_diagnostic_says_which_text_it_is_about, tests/properties/test_f10_diagnostic_fields.py::test_law2_every_diagnostic_carries_the_fields_its_category_publishes, tests/properties/test_f10_diagnostic_fields.py::test_law3_a_placed_diagnostic_stands_somewhere_in_the_text, tests/properties/test_f10_diagnostic_fields.py::test_the_laws_are_capable_of_failing
  - tests (read from the run): 19 failed in 1.77s
  ```text
                   ^^^^^^^^^

  tests/properties/test_f10_diagnostic_fields.py:167:
  _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

      def schemas() -> dict:
          """What the manifest publishes about the shape of each diagnostic
          category, read from the tool at the moment of the check."""
          manifest = service.handle({"operation": "discover"})["result"]
          published = manifest.get("diagnostic_schemas")
  >       assert isinstance(published, dict), (
              "the manifest publishes no diagnostic schemas, so a client cannot read "
              f"the shape of a refusal from the tool: {sorted(manifest)}"
          )
  E       AssertionError: the manifest publishes no diagnostic schemas, so a client cannot read the shape of a refusal from the tool: ['diagnostic_categories', 'documentation', 'operations', 'profile', 'resource_limits', 'statuses']
  E       assert False
  E        +  where False = isinstance(None, dict)

  tests/properties/test_f10_diagnostic_fields.py:51: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f10_b1_every_refusal_names_the_revision_of_its_source.py::test_every_refusal_carries_the_revision_of_the_source_it_is_about
  FAILED tests/acceptance/test_f10_b1_every_refusal_names_the_revision_of_its_source.py::test_two_sources_are_two_revisions_and_one_source_is_one
  FAILED tests/acceptance/test_f10_b2_a_type_error_names_its_symbol_expected_and_actual.py::test_a_type_error_names_the_symbol_and_both_types
  FAILED tests/acceptance/test_f10_b2_a_type_error_names_its_symbol_expected_and_actual.py::test_the_two_types_are_separate_fields_not_one_sentence
  FAILED tests/acceptance/test_f10_b3_a_reader_refusal_still_says_where.py::test_a_refused_argument_says_where_in_the_argument_it_stands
  FAILED tests/acceptance/test_f10_b3_a_reader_refusal_still_says_where.py::test_a_refused_source_still_says_where_it_stands
  FAILED tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py::test_three_operations_answer_the_same_defect_with_the_same_fields
  FAILED tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py::test_other_text_in_the_source_does_not_change_the_fields
  FAILED tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py::test_two_different_defects_do_not_carry_the_same_fields
  FAILED tests/acceptance/test_f10_b5_a_repaired_program_is_accepted_with_its_new_revision.py::test_the_repaired_program_is_accepted_with_the_revision_of_its_new_text
  FAILED tests/acceptance/test_f10_b5_a_repaired_program_is_accepted_with_its_new_revision.py::test_the_refused_text_is_still_refused_after_the_repair
  FAILED tests/acceptance/test_f10_b6_a_refusal_about_a_declaration_says_where_it_stands.py::test_each_refusal_about_a_declaration_names_it_and_points_at_it
  FAILED tests/acceptance/test_f10_b6_a_refusal_about_a_declaration_says_where_it_stands.py::test_an_example_counted_wrong_says_how_many_were_expected_and_found
  FAILED tests/acceptance/test_f10_b7_the_manifest_says_what_each_refusal_carries.py::test_the_manifest_describes_every_category_it_publishes
  FAILED tests/acceptance/test_f10_b7_the_manifest_says_what_each_refusal_carries.py::test_every_refusal_matches_the_schema_published_for_its_category
  FAILED tests/properties/test_f10_diagnostic_fields.py::test_law1_every_diagnostic_says_which_text_it_is_about
  FAILED tests/properties/test_f10_diagnostic_fields.py::test_law2_every_diagnostic_carries_the_fields_its_category_publishes
  FAILED tests/properties/test_f10_diagnostic_fields.py::test_law3_a_placed_diagnostic_stands_somewhere_in_the_text
  FAILED tests/properties/test_f10_diagnostic_fields.py::test_the_laws_are_capable_of_failing
  19 failed in 1.77s
  ```

## 3. craft: Craft the change (revision 1, STALE: an earlier step was recorded again after it; record it again or say why it still holds)

- **refactor_commits**:
  - 72d5875
- **refactor_check**: the check ran on the parent and on each refactor commit
  - 72d5875b1a22 ([F10] give every refusal one builder, before changing what it carries): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 115.951s
  - tests (read from the run): 1026 passed in 115.81s
  - slowest: 6.77s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.48s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.96s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.47s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.74s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.96s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.66s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.56s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.43s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 1.36s call tests/properties/test_i1_s4_p7_pinned_snapshots.py::test_p7_protected_snapshots_agree_before_after_construction_and_after_execution
  ```text
  ........................................................................ [  7%]
  ........................................................................ [ 14%]
  ........................................................................ [ 21%]
  ........................................................................ [ 28%]
  ........................................................................ [ 35%]
  ........................................................................ [ 42%]
  ........................................................................ [ 49%]
  ........................................................................ [ 56%]
  ........................................................................ [ 63%]
  ........................................................................ [ 70%]
  ........................................................................ [ 77%]
  ........................................................................ [ 84%]
  ........................................................................ [ 91%]
  ........................................................................ [ 98%]
  ..................                                                       [100%]
  ============================= slowest 10 durations =============================
  6.77s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.48s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.96s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.47s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.74s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.96s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.66s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.56s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.43s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1.36s call     tests/properties/test_i1_s4_p7_pinned_snapshots.py::test_p7_protected_snapshots_agree_before_after_construction_and_after_execution
  1026 passed in 115.81s (0:01:55)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.056s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from the environment, so the client exits 3; the four open semantic questions were decided locally and recorded in the oracle note

## 4. design: Find the owners and design the change (revision 2)

- **owners**:
  - what a diagnostic is and what it carries => src/prova/checker.py, which defines Diagnostic and every rule that builds one
  - what a refusal is about, its symbol and the expectation it broke => new: nothing owns it today; a small family of value objects in src/prova/checker.py, because the facts live where the refusal is built and nowhere else
  - which fields a category carries, whether it is placed and whether it carries a revision => new: one table of kinds in src/prova/checker.py, read both when a diagnostic is built and when the manifest is published, so the two cannot disagree
  - the revision of a submitted source => src/prova/service.py, which already computes it as _source_digest and will own it as a value object
  - turning a diagnostic into the JSON a client reads => src/prova/service.py, the only place that writes a response dict
  - the published answer vocabulary a client reads the shape from => src/prova/service.py, the discover operation that already publishes statuses and categories
  - the place a declared name stands at => src/prova/syntax.py, which already records it on DeclaredName; the checker reads it and never re-derives a position
  - the place the reader stopped at => src/prova/reader.py, which already carries line and column on ReaderError and must carry one for the end of the input too
  - the place a value supplied as an argument stands at => src/prova/service.py, where the argument text is read into a value
- **reuse_decision**: Reused: checker.Diagnostic stays the one type every refusal is; syntax.DeclaredName keeps owning the place of a declared name, so the six refusals that gain a place read it from the declarations the parser already recorded instead of re-deriving one; reader.ReaderError keeps owning the place the reader stopped at; service._source_digest keeps owning the SHA-256 of a submitted source. Created new: a family of 'about' value objects (a symbol alone, a symbol with an expected and an actual type, a symbol with two counts, a named construct), because no existing unit owns what a refusal is about and today each of the 40 construction sites writes it into prose only; one table of diagnostic kinds, because no existing unit says which fields a category carries, and a client must read that shape from the manifest; and a SourceRevision value object, because the digest is a bare function today and the revision must now be stamped on every diagnostic, which is a responsibility rather than a calculation. Nothing else is created: the places, the categories and the reasons all keep their existing owners.
- **paradigm**: oo
- **boundaries**:
  - the JSON answer: service.py is the only unit that writes the dict a client reads, and no production type crosses it. Owner: service.py.
  - checker to service: the checker hands over Diagnostic objects and never a dict; service renders them. Owner: service.py, which translates at the boundary.
  - reader to service: a ReaderError or a syntax refusal is translated into a Diagnostic at the boundary, so a refusal of the reader and a refusal of a rule reach a client in the same shape. Owner: service.py.
  - parsed tree to checker: a place comes from syntax.DeclaredName and from the nodes, never from a second walk over the text. Owner: syntax.py.
  - the manifest: discover publishes the shape of every category from the same table the renderer reads, so the published shape and the built shape have one owner. Owner: service.py for the publishing, checker.py for the table.
  - evaluator to service: a precondition or postcondition violation and a value the evaluator refuses are translated into a Diagnostic naming the function they are about. Owner: service.py.
- **domain_types**:
  - Diagnostic (changed): gains what it is about, and refuses at construction a combination its category does not declare.
  - AboutASymbol (new): the refusal is about one named thing, such as a type no declaration gives or the function an example belongs to.
  - AboutTwoTypes (new): the refusal is about one symbol, the type expected there and the type found there.
  - AboutTwoCounts (new): the refusal is about one symbol, how many were expected and how many were given.
  - AboutAConstruct (new): the refusal is about a construct the profile does not have; keeps the existing 'construct' field.
  - AboutNothingNamed (new): the refusal names nothing, as a reader refusal does; the absence is a value instead of None, so every category has an answer.
  - DiagnosticKind and the table of kinds (new): for one category, what it is about, whether it is placed, what its place points into and at what granularity, and whether it carries a revision.
  - SourceRevision (new): the revision of one submitted source text, built from the text, rendered as the hexadecimal SHA-256.
  - Refusal (changed): carries the revision of the text it refused, so every diagnostic it renders is stamped in one place.
  - Place (new, reader.py): the line and column the reader stopped at, including the end of the input, so no refusal of the reader is built without one.
- **invariants**:
  - INV1 | a Diagnostic cannot be built whose subject is not the kind its category declares, nor with a category the table of kinds does not name | witness=src/prova/checker.py:Diagnostic | bypass=none inside the tool: service.py renders only Diagnostic objects, so no path writes a diagnostic dict by hand
  - INV2 | a Diagnostic of a category the table declares placed cannot be built without a place | witness=src/prova/checker.py:DiagnosticKind | bypass=none
  - INV3 | every diagnostic rendered for an operation that read a source carries the revision of that exact text, and the categories declared to carry none are the two that answer about the request itself | witness=src/prova/service.py:SourceRevision | bypass=none: one renderer stamps it and no other unit writes a diagnostic
  - INV4 | the shape the manifest publishes for a category and the shape a diagnostic of that category is built with are read from the same kind, so they cannot disagree | witness=src/prova/checker.py:DiagnosticKind | bypass=none
  - INV5 | no category name, no reason and no field that exists today is renamed or removed; the one builder of a diagnostic only adds fields beside them | witness=src/prova/service.py:_diagnostic_dict | bypass=none: the 1007 existing tests read those names and reasons and stay unedited
- **prefactoring**: yes
- **prefactoring_reason**: service.py builds eight diagnostic dictionaries by hand beside the one builder that renders checker Diagnostics, so the shape of a refusal has two owners and no table can bind both. The prefactor moves every hand-written dictionary to a checker.Diagnostic rendered by the single builder, and turns the bare _source_digest function into the SourceRevision value object. Behaviour is preserved exactly: the same categories, the same reasons and the same keys come out, which the 1007 existing tests observe; no test is edited. Only after that does the feature add the subject, the table of kinds and the places, because each of those must be stated once for all refusals rather than once per construction site.

## 5. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the change is the design: one table of kinds in checker.py, one renderer in service.py, the manifest published from that same table. The one departure, the two request-level refusals left written in the dispatch, is recorded with its reason in docs/feature/diagnostic-fields/craft.md and in a comment above handle().
  - D2: pass - DIAGNOSTIC_CATEGORIES is now read from DIAGNOSTIC_KINDS and the manifest schemas are rendered from it, so the published list, the published shape and the shape a refusal is built with are one table. The revision is computed in one value object and stamped in the one builder every refusal passes.
  - D3: pass - the checker hands over Diagnostic values and never a dictionary; service.py is the only unit that writes the dict a client reads; places come from syntax.DeclaredName and reader.ReaderError, so nothing re-derives a position. No hashing, parsing or JSON reaches the checker.
  - D4: pass - src/prova/checker.py:324 refuses, at construction, a refusal whose category no kind declares, whose subject is not the kind declared, which is unplaced where every one of them is placed, which stands at line or column 0, which carries a cycle its category does not name, or which names a text its category does not point into. src/prova/checker.py:141 replaces a type written into prose with a value object carrying the symbol and both types.
  - D5: pass - the subjects are small immutable value objects that answer for themselves (src/prova/checker.py:141, AboutTwoTypes with fields() and kinds()), and the kind answers which text a refusal must name rather than a caller reading its list (src/prova/checker.py:216). Diagnostic and DiagnosticKind hold more than two fields: they are the published payload shape at the JSON boundary, which the skill exempts, and each field is one the manifest names.
  - D6: pass - a family of subject types answering one question each, chosen over a flag or an optional pair, so a category's fields are read from its own type; and one table keyed by category, read by the constructor and by the manifest. No pattern is added that no accepted outcome reads.
  - D7: pass - the names are the words of this domain: a refusal, what it is about, the place it stands at, the revision of a source, the declarations of a cycle. No Manager, Helper or Data, and no abbreviation.
  - D8: pass - the checker computes no digest, opens no file and writes no JSON; the SHA-256 lives in service.py beside the boundary that answers, and the reader owns the place it stopped at.
  - D9: pass - every acceptance check drives the real prova command over its JSON stdin and stdout and imports nothing from src/prova (tests/acceptance/test_f10_b9_a_source_that_is_not_text_is_refused.py:47 reads the exit code and the answer, nothing else). The laws drive service.handle, the service's public operation contract, as the other property tests of this repository do. The one file that touches a production type is the unit check of the construction rules, which is the narrowest surface that carries a rule no program can draw.
  - D10: pass - each check is named as the sentence it proves, in the words of a client: a type error names its symbol expected and actual, a reader refusal still says where, a repaired program is accepted with its new revision.
  - D11: pass - one fixtures module holds the programs, their twins and the readers of an answer; every case is declared once in a table and every test walks it, so a new case is one line.
  - D12: pass - tests/properties/test_f10_diagnostic_fields.py:134 walks mutations of the shipped program, a character deleted, a character inserted or the text cut short, crossed with the operations that read source, and requires every diagnostic to carry exactly the fields its category publishes; two more laws require the revision of the submitted text and a place that stands in it.
  - D13: pass - the eleven new files run nine times in a row green, 31 passed, median 6.03s and slowest 6.10s; none of them is among the ten slowest of the suite, which runs 1042 in 109s. No test sleeps and none reads the clock.
  - D14: pass - the programs, their accepted twins and the helpers that read an answer are declared once in _f10_diagnostic_fixtures.py; the tests differ in what they assert, not in what they set up.
  - D15: pass - every refusal this change adds says what failed, why the rule exists and what to do: src/prova/service.py:126 names the kind of value the source field held, says the tool reads a program from its characters, and tells the client to send one JSON string with its line breaks written as an escape. The construction refusals name the category, the shape it declares and the repair.
  - D16: n/a: the tool answers one request in one pass, keeps nothing between requests and writes nothing, so there is no shared state, no protocol of more than one step, no retry and no crash window for a model to explore. Recorded with that reason in the design.
  - D17: pass - the craft record was measured again against the branch as it stands and now cites the commits that are in it; every number in it names the command that produced it, the stated limits on place granularity match the table the code publishes, and the three crashes older than this feature are named with what reproduces them.
- **independent_review**:
  - REV1 | reviewer=rev-f10 | findings=8 (verdict REJECT at 0af2202) | resolution=findings 1-5 and 8 fixed in bcec4ec and ca7236a, 6 and 7 logged as follow-ups
  - REV2 | reviewer=rev-f10 | findings=0 (verdict APPROVE at ca7236a) | resolution=none needed, the reviewer recorded no finding to resolve

## 6. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
  - A client can now act on a failure without reading the sentence it carries.
  - A request whose source is not text is refused instead of ending in a traceback.
- **not_verified**:
  - The role of 'symbol' is not the same within one category: a malformed_value from the reader names the function the request called, while one from the evaluator names the same function but stands at its declaration. Logged as a follow-up by the reviewer, not repaired here.
  - The function a refusal stands in is threaded through the checker as a bare 'within: str' through about 25 call sites rather than as a value object. Logged as a follow-up by the reviewer, not repaired here.
  - src/prova/evaluator.py raises IndexError when a program the checker accepts is then run: delete character 550 or character 1191 of examples/hour-clock.prova and ask for 'examples'. The pre-feature tree raises the same traceback, so it is not a regression of this change; it belongs to the evaluator's owner. The generated laws therefore ask the two operations that run a program only for a source the checker refuses.
  - evaluate with 'function' set to a list raises TypeError: unhashable type, and with 'arguments' set to a number raises TypeError: 'int' object is not iterable. Both raise on the pre-feature tree too. The review asked for the 'source' field, which is repaired and tested; these two are reported and left.
  - The craft record stays at revision 1, recorded before the branch was rebased onto main and before the review's repairs. The workspace's archived baseline predates that rebase, so the tool refuses a new craft revision with 'refactor commits must be the first commits from BASE to HEAD, oldest first, before any feature commit; the history starts with bd12621e92fe'. The owner accepted it as is; the measured receipts for the candidate as it stands are in docs/feature/diagnostic-fields/craft.md and were run by hand.
  - The question service was authorized but unavailable for the whole run: TYPESAFE_API_KEY is absent from the environment and the client exits 3. The four open semantic questions were decided locally and recorded in the oracle note, so no judgment of that service stands behind them.
  - Whether a place that stands at a declaration is the finest place the parsed tree could ever give is not established: the tree keeps no position for a type written inside a signature or a record field, for an individual example, or for a value inside an example, and this change did not add one. The manifest publishes that granularity per category so a client is not told otherwise.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit ca7236a80119c337a4602742e683480eea50ff86
  - no checks declared

## Not backed by the diff

- Every diagnostic says which text the answer is about, by the SHA-256 of the exact source the request submitted; a type error names the symbol it is about and carries the expected and the found type as separate fields; a wrong number of arguments carries both counts; six refusals that carried no place at all now stand at the declaration they are about, and a refusal from the reader says where it stopped in the argument text too.: a guarantee names no test function of the change
- One table of kinds says what each category carries: the diagnostic type reads it when a refusal is built and refuses a subject, a place, a cycle or a text the category does not declare, and the manifest publishes the same table as diagnostic_schemas, so the shape a client is promised and the shape the tool builds cannot drift apart.: a guarantee names no test function of the change
- It was checked by the oracle written before the code, all of it seen failing first, by three generated laws over mutations of the shipped program, by the construction rules' own refused and accepted demonstrations, and by deleting each repair in turn to watch a check go red.: a guarantee names no test function of the change
- An independent reviewer rejected the first candidate with eight findings and approved the repaired one with none.: a guarantee names no test function of the change
