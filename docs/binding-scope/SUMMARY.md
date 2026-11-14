# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 857 tests, all green on main).
  - promises: P9
  - tests P9: test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it
- S2: Authority: SPEC.md.
  - not-testable (challenge this): it names the authority document, it promises no behaviour of the tool
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on the change itself, observable in the diff and not in the tool
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): an instruction for this delivery about what to do with a conflict
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): it excludes a directory from reading, it promises no behaviour
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): it names where the work happens, observable in git and not in the tool
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a requirement on the commit message, observable in git history
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the literal line the commit message must end with, checked in git
- S9: Do not push and do not merge.
  - not-testable (challenge this): a constraint on git remotes, nothing the tool answers
- S10: Keep the full suite green.
  - promises: P9
  - tests P9: test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it
- S11: Another delivery runs in parallel in a different worktree: F6 (names and markers, mostly src/prova/syntax.py plus the malformed-`sig` crash; do not touch the signature or name-shape parsing).
  - not-testable (challenge this): a file-level scope boundary against a parallel delivery
- S12: Existing categories already include `cyclic_dependency` (F2), `duplicate_declaration` (F3) and `recursive_type` (F4); read how F2-F4 were built in src/prova/checker.py and syntax.py and follow the same structure (small named values, one owner per rule, a published category if you need a new one, said in your oracle note with the reason).
  - promises: P8
  - tests P8: test_the_manifest_lists_the_two_refusals_this_rule_adds
- S13: Reuse an existing category if it fits.
  - promises: P8
  - tests P8: test_the_manifest_lists_the_two_refusals_this_rule_adds
- S14: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell quoting hygiene for the tooling of this delivery
- S15: **Outcome.** A `let` or pattern variable that would hide a parameter, a function or
  - promises: P1, P2, P3, P10
  - tests P1: test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it
  - tests P2: test_a_pattern_variable_spelled_like_a_declared_function_is_refused
  - tests P3: test_a_binder_is_refused_exactly_when_its_name_is_taken
  - tests P10: test_a_parameter_spelled_like_a_declared_function_is_refused
- S16: a builtin is refused, and `result` can only be read in a postcondition.
  - promises: P3, P4, P5
  - tests P3: test_a_binder_is_refused_exactly_when_its_name_is_taken
  - tests P4: test_a_binder_named_result_is_refused
  - tests P5: test_a_program_that_reads_result_in_its_body_and_precondition_is_refused
- S17: **Acceptance criteria**
  - not-testable (challenge this): a heading that introduces the list of criteria
- S18: 1.
  - not-testable (challenge this): the number of a list item, it carries no promise of its own
- S19: Given a `let` that binds a name already bound as a parameter, when the program
  - promises: P1
  - tests P1: test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it
- S20: is checked, then it is invalid and the diagnostic names the hidden binding.
  - promises: P1
  - tests P1: test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it
- S21: 2.
  - not-testable (challenge this): the number of a list item, it carries no promise of its own
- S22: Given a pattern variable that hides a declared function name, likewise.
  - promises: P2
  - tests P2: test_a_pattern_variable_spelled_like_a_declared_function_is_refused
- S23: 3.
  - not-testable (challenge this): the number of a list item, it carries no promise of its own
- S24: Given any binder named `result`, when the program is checked, then it is invalid.
  - promises: P4
  - tests P4: test_a_binder_named_result_is_refused
- S25: 4.
  - not-testable (challenge this): the number of a list item, it carries no promise of its own
- S26: Given `result` read in a body or in a precondition, then it is invalid.
  - promises: P5
  - tests P5: test_a_program_that_reads_result_in_its_body_and_precondition_is_refused
- S27: 5.
  - not-testable (challenge this): the number of a list item, it carries no promise of its own
- S28: Given a pattern that binds the same name twice, then it is invalid.
  - promises: P6
  - tests P6: test_a_pattern_that_binds_one_name_to_both_fields_is_refused
- S29: 6.
  - not-testable (challenge this): the number of a list item, it carries no promise of its own
- S30: Given the same variable name used in two different match clauses of one
  - promises: P7
  - tests P7: test_a_clause_variable_is_visible_only_inside_its_own_clause
- S31: expression, when the program is checked, then it is accepted.
  - promises: P7
  - tests P7: test_a_clause_variable_is_visible_only_inside_its_own_clause
- S32: **SPEC.md** lines 145-149, 156-161 (a pattern variable binds once).
  - not-testable (challenge this): a citation of the authority lines the rules come from
- S33: **Dependencies** none (serial with F3, F4, F7, F8).
  - not-testable (challenge this): it records that nothing blocks this work, no behaviour follows
- S34: **Size** M: three related rules
  - not-testable (challenge this): a size estimate for the delivery, not a behaviour
- S35: and the scope bookkeeping they share.
  - not-testable (challenge this): the rest of the size estimate sentence, no behaviour
- S36: **Touches** `src/prova/checker.py`, tests.
  - not-testable (challenge this): it names the files expected to change, observable in the diff
- S37: **Why it is a real expectation** probes T8, T10, T16 disagree today.
  - not-testable (challenge this): it names probes T8, T10 and T16, which are outside this repository

## Edge matrix

- I1.empty: an empty source => completed with 0 diagnostics: there is no binder to refuse | self-probe: not probed | pre-feature not probed
- I1.unknown: a let binding whose name the program never declares anywhere => accepted, and a body that reads a name nothing binds is still answered unbound_name | self-probe: not probed | pre-feature not probed
- I1.malformed: a source whose parentheses do not close => the syntax refusal the reader already gets, before any binding rule runs | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the check reads only the source text in the request and opens no file, process or service
- I1.repeated: the same hiding program checked twice in 2 runs => the same invalid_program answer both times; the operation keeps nothing | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): each request is answered in its own process from its own input and shares no state
- I1.crash: 40 nested let forms whose innermost one rebinds the outermost name => 1 refusal and no traceback; the walk descends the same tree the type inference already descends | self-probe: not probed | pre-feature not probed
- I2.empty: a discover request with no other field => the manifest, including the 2 new categories | self-probe: not probed | pre-feature not probed
- I2.unknown: a request naming an operation the tool does not have => unknown_operation, with the manifest unchanged | self-probe: not probed | pre-feature not probed
- I2.malformed: n/a (challenge this): discover reads no source, so this rule gives it nothing that can be malformed
- I2.dependency-gone: n/a (challenge this): the manifest is built from the tool own vocabulary and reads nothing outside the process
- I2.repeated: the manifest asked for twice => 2 identical lists of categories | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): the manifest is a constant answer and shares no state between requests
- I2.crash: n/a (challenge this): building a list of 13 published names cannot fail part way
- I3.empty: evaluate with an empty source => the existing refusal that no such function is declared, unchanged by this rule | self-probe: not probed | pre-feature not probed
- I3.unknown: evaluate naming a function the program does not declare => unknown_function, unchanged by this rule | self-probe: not probed | pre-feature not probed
- I3.malformed: evaluate whose argument text is not 1 readable value => malformed_value, unchanged by this rule | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): both operations read only the request and open no file, process or service
- I3.repeated: a hiding program evaluated twice => invalid_program both times, and the function is run 0 times | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): each request is answered in its own process and shares no state
- I3.crash: a hiding program sent to evaluate => refused before any evaluation, 1 JSON response and no traceback | self-probe: not probed | pre-feature not probed

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the function fare whose parameter is cents and whose body is (let ((cents (+ cents 10))) cents)
  - WHEN the program is checked
  - THEN the answer is invalid_program with exactly 1 shadowed_binding refusal naming cents and the parameter it hides
  - test: test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN a program that declares the function offset and 1 match clause ((Hour offset) offset)
  - WHEN the program is checked
  - THEN the answer is invalid_program with exactly 1 shadowed_binding refusal naming offset and the function it hides
  - test: test_a_pattern_variable_spelled_like_a_declared_function_is_refused
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN the body (let ((not (+ n 5))) not), where not is 1 of the builtin operators
  - WHEN the program is checked
  - THEN the answer is invalid_program with exactly 1 shadowed_binding refusal naming "not"
  - test: test_a_binder_is_refused_exactly_when_its_name_is_taken
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN 3 programs whose parameter, let binding and pattern variable are each named result
  - WHEN each of the 3 is checked
  - THEN each answer is invalid_program with exactly 1 reserved_name refusal naming "result" and the kind of binder
  - test: test_a_binder_named_result_is_refused
- SC5 (P5): not-held (no held self-probe case)
  - GIVEN the function doubled whose parameter is result, read in its body and in 1 requires clause
  - WHEN the program is checked
  - THEN the answer is invalid_program naming "result", while the twin that reads result in 1 ensures clause is completed with 0 diagnostics
  - test: test_a_program_that_reads_result_in_its_body_and_precondition_is_refused
- SC6 (P6): not-held (no held self-probe case)
  - GIVEN the record Pair of 2 Int fields and the pattern (Pair n n)
  - WHEN the program is checked
  - THEN the answer is invalid_program with exactly 1 shadowed_binding refusal naming "n"
  - test: test_a_pattern_that_binds_one_name_to_both_fields_is_refused
- SC7 (P7): not-held (no held self-probe case)
  - GIVEN the union Colour of 2 variants and the clauses ((Red tone) tone) ((Blue tone) tone)
  - WHEN the program is checked
  - THEN the answer is completed with 0 diagnostics
  - test: test_a_clause_variable_is_visible_only_inside_its_own_clause
- SC8 (P8): not-held (no held self-probe case)
  - GIVEN a caller that asks the tool which of its "diagnostic_categories" it can report
  - WHEN it reads the manifest of the discover operation
  - THEN diagnostic_categories lists shadowed_binding and reserved_name beside the 4 categories already published
  - test: test_the_manifest_lists_the_two_refusals_this_rule_adds
- SC10 (P10): not-held (no held self-probe case)
  - GIVEN a program that declares the function offset and a second function whose 1 parameter is also offset, and a function gap whose 2 parameters are both edge
  - WHEN each program is checked
  - THEN each answer is invalid_program with exactly 1 shadowed_binding refusal naming the parameter and what it hides
  - test: test_a_parameter_spelled_like_a_declared_function_is_refused
- SC9 (P9): not-held (no held self-probe case)
  - GIVEN the 2 programs the project ships, examples/hour-clock.prova and conformance/add-one.prova, 1 of which reads result in its postconditions
  - WHEN each is checked, and checked again with 1 added function whose let hides its own parameter
  - THEN both are accepted with 0 diagnostics and both copies with the added binding are invalid_program
  - test: test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it

## Questions for the owner

- none

## Observed side effects (git, BASE to HEAD)

- A docs/feature/binding-scope/design.md (+94 -0 lines)
- A docs/feature/binding-scope/oracle.md (+89 -0 lines)
- M src/prova/checker.py (+227 -0 lines)
- M src/prova/service.py (+2 -0 lines)
- A tests/acceptance/_f5_binding_fixtures.py (+379 -0 lines)
- A tests/acceptance/test_f5_b1_a_let_hiding_a_parameter_is_refused.py (+46 -0 lines)
- A tests/acceptance/test_f5_b2_a_pattern_variable_hiding_a_function_is_refused.py (+46 -0 lines)
- A tests/acceptance/test_f5_b3_a_binder_named_result_is_refused.py (+66 -0 lines)
- A tests/acceptance/test_f5_b4_result_read_outside_a_postcondition_is_refused.py (+69 -0 lines)
- A tests/acceptance/test_f5_b5_a_pattern_binding_one_name_twice_is_refused.py (+40 -0 lines)
- A tests/acceptance/test_f5_b6_one_spelling_in_two_clauses_is_accepted.py (+43 -0 lines)
- A tests/acceptance/test_f5_b7_the_manifest_publishes_the_new_categories.py (+57 -0 lines)
- A tests/acceptance/test_f5_b8_a_parameter_hiding_another_binding_is_refused.py (+68 -0 lines)
- A tests/acceptance/test_f5_char1_shipped_programs_still_check.py (+87 -0 lines)
- A tests/properties/test_f5_binding_scope.py (+224 -0 lines)

## Commits (git log, BASE to HEAD)

- 37f1c04 [F5] state the binding rules as tests before the rule exists
- a8f08e8 [F5] a parameter hides nothing either, by the owner's reading
- 1442fa2 [F5] record where the binding rules will live
- 1370f04 [F5] refuse a binding that hides another, and keep result for postconditions

## 2. oracle: Frame the work and write the oracle (revision 2)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f5/request.md
- **promises**:
  - P1: A let binding whose name is already bound as a parameter makes the program invalid, and the refusal names the binding it hides.
  - P2: A pattern variable whose name is a declared function makes the program invalid, and the refusal names the function it hides.
  - P3: A binding whose name is a builtin operator makes the program invalid.
  - P4: Any binder named result, be it a parameter, a let binding or a pattern variable, makes the program invalid.
  - P5: result read in a body or in a precondition makes the program invalid, while a postcondition may still read it.
  - P6: A pattern that binds the same name twice makes the program invalid.
  - P7: The same variable name in two disjoint match clauses of one expression is accepted.
  - P8: The tool publishes the refusals this rule adds in its own manifest, beside the ones it already publishes.
  - P10: A parameter that hides a declared function, or an earlier parameter of its own signature, makes the program invalid.
  - P9: Every program the project ships, and every program the suite already accepts, is still accepted.
- **sentence_map**:
  - S1 => P9
  - S2 => not-testable: it names the authority document, it promises no behaviour of the tool
  - S3 => not-testable: a constraint on the change itself, observable in the diff and not in the tool
  - S4 => not-testable: an instruction for this delivery about what to do with a conflict
  - S5 => not-testable: it excludes a directory from reading, it promises no behaviour
  - S6 => not-testable: it names where the work happens, observable in git and not in the tool
  - S7 => not-testable: a requirement on the commit message, observable in git history
  - S8 => not-testable: the literal line the commit message must end with, checked in git
  - S9 => not-testable: a constraint on git remotes, nothing the tool answers
  - S10 => P9
  - S11 => not-testable: a file-level scope boundary against a parallel delivery
  - S12 => P8
  - S13 => P8
  - S14 => not-testable: shell quoting hygiene for the tooling of this delivery
  - S15 => P1,P2,P3,P10
  - S16 => P3,P4,P5
  - S17 => not-testable: a heading that introduces the list of criteria
  - S18 => not-testable: the number of a list item, it carries no promise of its own
  - S19 => P1
  - S20 => P1
  - S21 => not-testable: the number of a list item, it carries no promise of its own
  - S22 => P2
  - S23 => not-testable: the number of a list item, it carries no promise of its own
  - S24 => P4
  - S25 => not-testable: the number of a list item, it carries no promise of its own
  - S26 => P5
  - S27 => not-testable: the number of a list item, it carries no promise of its own
  - S28 => P6
  - S29 => not-testable: the number of a list item, it carries no promise of its own
  - S30 => P7
  - S31 => P7
  - S32 => not-testable: a citation of the authority lines the rules come from
  - S33 => not-testable: it records that nothing blocks this work, no behaviour follows
  - S34 => not-testable: a size estimate for the delivery, not a behaviour
  - S35 => not-testable: the rest of the size estimate sentence, no behaviour
  - S36 => not-testable: it names the files expected to change, observable in the diff
  - S37 => not-testable: it names probes T8, T10 and T16, which are outside this repository
- **scenarios**:
  - SC1 | P1 | GIVEN the function fare whose parameter is cents and whose body is (let ((cents (+ cents 10))) cents) | WHEN the program is checked | THEN the answer is invalid_program with exactly 1 shadowed_binding refusal naming cents and the parameter it hides
  - SC2 | P2 | GIVEN a program that declares the function offset and 1 match clause ((Hour offset) offset) | WHEN the program is checked | THEN the answer is invalid_program with exactly 1 shadowed_binding refusal naming offset and the function it hides
  - SC3 | P3 | GIVEN the body (let ((not (+ n 5))) not), where not is 1 of the builtin operators | WHEN the program is checked | THEN the answer is invalid_program with exactly 1 shadowed_binding refusal naming "not"
  - SC4 | P4 | GIVEN 3 programs whose parameter, let binding and pattern variable are each named result | WHEN each of the 3 is checked | THEN each answer is invalid_program with exactly 1 reserved_name refusal naming "result" and the kind of binder
  - SC5 | P5 | GIVEN the function doubled whose parameter is result, read in its body and in 1 requires clause | WHEN the program is checked | THEN the answer is invalid_program naming "result", while the twin that reads result in 1 ensures clause is completed with 0 diagnostics
  - SC6 | P6 | GIVEN the record Pair of 2 Int fields and the pattern (Pair n n) | WHEN the program is checked | THEN the answer is invalid_program with exactly 1 shadowed_binding refusal naming "n"
  - SC7 | P7 | GIVEN the union Colour of 2 variants and the clauses ((Red tone) tone) ((Blue tone) tone) | WHEN the program is checked | THEN the answer is completed with 0 diagnostics
  - SC8 | P8 | GIVEN a caller that asks the tool which of its "diagnostic_categories" it can report | WHEN it reads the manifest of the discover operation | THEN diagnostic_categories lists shadowed_binding and reserved_name beside the 4 categories already published
  - SC10 | P10 | GIVEN a program that declares the function offset and a second function whose 1 parameter is also offset, and a function gap whose 2 parameters are both edge | WHEN each program is checked | THEN each answer is invalid_program with exactly 1 shadowed_binding refusal naming the parameter and what it hides
  - SC9 | P9 | GIVEN the 2 programs the project ships, examples/hour-clock.prova and conformance/add-one.prova, 1 of which reads result in its postconditions | WHEN each is checked, and checked again with 1 added function whose let hides its own parameter | THEN both are accepted with 0 diagnostics and both copies with the added binding are invalid_program
- **conflicts**:
  - S1 | NONE | ran the suite on this worktree before writing anything: 857 tests, all green, so the baseline the sentence states holds here
  - S2 | NONE | read SPEC.md lines 145-149 and 156-161: they state the no-shadowing rule, the reserved result and one binding per pattern, which is what the criteria ask for
  - S3 | NONE | this change adds test files only and edits no existing test and not SPEC.md; checked with git status that no tracked test file is modified
  - S4 | NONE | searched every program text in tests, examples and conformance for a binder that the new rules would refuse and found none, so no existing test conflicts
  - S5 | NONE | the .relay directory is not read by this delivery and no test of this feature opens it
  - S6 | NONE | all work happens in the worktree at /Users/andrealaforgia/dev/prova-wt-f5 on branch feat/f5
  - S7 | NONE | nothing in the repository constrains commit messages in a way that contradicts the required trailer
  - S8 | NONE | the trailer line is free text in the commit message and contradicts no repository rule
  - S9 | NONE | no automation in this repository pushes or merges on commit; checked that no commit hook exists in the worktree
  - S10 | NONE | the only programs the suite checks that contain a let or a pattern variable are in tests/unit, tests/properties and tests/acceptance, and none of their binders hides a visible name
  - S11 | NONE | this change edits src/prova/checker.py and new test files only, and touches neither the signature parsing nor the name-shape parsing in syntax.py
  - S12 | NONE | read the F2, F3 and F4 rules in checker.py: each owns a small frozen value that carries its refusal, and each new category is published in service.DIAGNOSTIC_CATEGORIES
  - S13 | NONE | checked the 11 published categories: duplicate_declaration reports a top-level name declared twice, with a place and a uniqueness rule for a declaration, and unbound_name reports a name nothing binds; neither states that a binder hides a visible binding or uses a reserved word
  - S14 | NONE | every nwstep argument of this delivery is passed from a file with single quotes around it
  - S15 | NONE | the checker accepts such a program today, so the sentence adds a rule and contradicts nothing that is promised
  - S16 | NONE | result is bound today only in the environment of an ensures clause, so reading it in a postcondition already works and the sentence keeps that
  - S17 | NONE | a heading contradicts nothing in the code
  - S18 | NONE | a list number contradicts nothing in the code
  - S19 | NONE | a let that rebinds a parameter is accepted today and no test asserts that it must be
  - S20 | NONE | no existing diagnostic of the tool names a hidden binding, so naming one adds a sentence and changes none
  - S21 | NONE | a list number contradicts nothing in the code
  - S22 | NONE | a pattern variable spelled like a function is accepted today and no test asserts that it must be
  - S23 | NONE | a list number contradicts nothing in the code
  - S24 | NONE | a parameter, a let binding or a pattern variable named result is accepted today; no test in the suite declares one
  - S25 | NONE | a list number contradicts nothing in the code
  - S26 | NONE | reading result where nothing binds it is already refused as unbound_name; the sentence is about the case where a binder makes it readable
  - S27 | NONE | a list number contradicts nothing in the code
  - S28 | NONE | the pattern bindings of the checker merge a repeated spelling into one binding today, so such a pattern is accepted and no test asserts that
  - S29 | NONE | a list number contradicts nothing in the code
  - S30 | NONE | clause environments are built per clause today, so disjoint clauses already share a spelling and the match tests rely on it
  - S31 | NONE | the exhaustiveness property tests check many clause sets and none of them is refused for a repeated spelling
  - S32 | NONE | read the cited SPEC.md lines; they say exactly what the criteria ask for and contradict no code
  - S33 | NONE | this work needs nothing from F3, F4, F7 or F8 and shares no file with them beyond checker.py
  - S34 | NONE | a size estimate contradicts nothing in the code
  - S35 | NONE | the rest of the size sentence contradicts nothing in the code
  - S36 | NONE | the rules live in checker.py, with the two new categories published in service.DIAGNOSTIC_CATEGORIES, which the request did not name but F3 and F4 both required
  - S37 | NONE | probes T8, T10 and T16 are not in this repository, so nothing here can contradict them
- **decisions**:
  - DEC1: Two new published categories, not one and not a reuse. shadowed_binding carries every binding that hides a name already visible, including a pattern that binds one spelling twice, because the second binder hides the first. reserved_name carries a binder that uses result. duplicate_declaration was not reused: it reports a top-level declaration with a place and a declaration uniqueness rule, and a caller filtering on it would start receiving local binder defects.
  - DEC2: builtin in the SPEC sentence is read as the builtin operator names (+ - * < <= > >= = and or not), because they are the only builtins reachable where a value binding is visible; the builtin type names live in the type namespace and a value binding cannot hide them.
  - DEC3: the owner answered option A on this delivery: a parameter is a binding too, so a parameter may hide neither a declared function nor an earlier parameter of its own signature, and a parameter named result is refused; SPEC.md line 145 lists parameters among the bindings the rule governs, and the request outcome sentence alone would have stopped at let bindings and pattern variables.
  - DEC4: service.DIAGNOSTIC_CATEGORIES is edited although the request names only checker.py and tests, because F3 and F4 both published their category there and a category the manifest hides cannot be relied on by a caller.
  - DEC5: no formal model (Quint). The rules are pure functions of one parsed program, with no state, protocol, concurrency or crash: the two generated properties over binder names and clause counts carry the laws.
  - DEC6: typesafe: unavailable: TYPESAFE_API_KEY is absent from this process environment, so jev_decide.py exited 3 before sending anything; the four open questions behind DEC1, DEC2 and DEC3 were settled locally against SPEC.md lines 145-149 and the F3 and F4 code.
- **mapping**:
  - P1 => test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it
  - P2 => test_a_pattern_variable_spelled_like_a_declared_function_is_refused
  - P3 => test_a_binder_is_refused_exactly_when_its_name_is_taken
  - P4 => test_a_binder_named_result_is_refused
  - P5 => test_a_program_that_reads_result_in_its_body_and_precondition_is_refused
  - P6 => test_a_pattern_that_binds_one_name_to_both_fields_is_refused
  - P7 => test_a_clause_variable_is_visible_only_inside_its_own_clause
  - P8 => test_the_manifest_lists_the_two_refusals_this_rule_adds
  - P10 => test_a_parameter_spelled_like_a_declared_function_is_refused
  - P9 => test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it
- **covers_scenarios**:
  - SC1 => test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it
  - SC2 => test_a_pattern_variable_spelled_like_a_declared_function_is_refused
  - SC3 => test_a_binder_is_refused_exactly_when_its_name_is_taken
  - SC4 => test_a_binder_named_result_is_refused
  - SC5 => test_a_program_that_reads_result_in_its_body_and_precondition_is_refused
  - SC6 => test_a_pattern_that_binds_one_name_to_both_fields_is_refused
  - SC7 => test_a_clause_variable_is_visible_only_inside_its_own_clause
  - SC8 => test_the_manifest_lists_the_two_refusals_this_rule_adds
  - SC10 => test_a_parameter_spelled_like_a_declared_function_is_refused
  - SC9 => test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC6 => base differs
  - SC7 => base held
  - SC8 => base differs
  - SC10 => base differs
  - SC9 => base held
- **interfaces**:
  - I1: the check operation of the prova command, a JSON request on standard input answered with one JSON response on standard output
  - I2: the discover operation, whose manifest publishes the categories the tool can answer with
  - I3: the examples and evaluate operations, which check the whole program before running anything
- **matrix**:
  - I1.empty => an empty source => completed with 0 diagnostics: there is no binder to refuse
  - I1.unknown => a let binding whose name the program never declares anywhere => accepted, and a body that reads a name nothing binds is still answered unbound_name
  - I1.malformed => a source whose parentheses do not close => the syntax refusal the reader already gets, before any binding rule runs
  - I1.dependency-gone => n/a: the check reads only the source text in the request and opens no file, process or service
  - I1.repeated => the same hiding program checked twice in 2 runs => the same invalid_program answer both times; the operation keeps nothing
  - I1.concurrent => n/a: each request is answered in its own process from its own input and shares no state
  - I1.crash => 40 nested let forms whose innermost one rebinds the outermost name => 1 refusal and no traceback; the walk descends the same tree the type inference already descends
  - I2.empty => a discover request with no other field => the manifest, including the 2 new categories
  - I2.unknown => a request naming an operation the tool does not have => unknown_operation, with the manifest unchanged
  - I2.malformed => n/a: discover reads no source, so this rule gives it nothing that can be malformed
  - I2.dependency-gone => n/a: the manifest is built from the tool own vocabulary and reads nothing outside the process
  - I2.repeated => the manifest asked for twice => 2 identical lists of categories
  - I2.concurrent => n/a: the manifest is a constant answer and shares no state between requests
  - I2.crash => n/a: building a list of 13 published names cannot fail part way
  - I3.empty => evaluate with an empty source => the existing refusal that no such function is declared, unchanged by this rule
  - I3.unknown => evaluate naming a function the program does not declare => unknown_function, unchanged by this rule
  - I3.malformed => evaluate whose argument text is not 1 readable value => malformed_value, unchanged by this rule
  - I3.dependency-gone => n/a: both operations read only the request and open no file, process or service
  - I3.repeated => a hiding program evaluated twice => invalid_program both times, and the function is run 0 times
  - I3.concurrent => n/a: each request is answered in its own process and shares no state
  - I3.crash => a hiding program sent to evaluate => refused before any evaluation, 1 JSON response and no traceback
- **laws**:
  - LAW1 | A binding is accepted exactly when its name is not already visible where it is introduced, as a parameter, an enclosing let binding, a declared function or a builtin operator, and is not the reserved word result | generator=test_a_binder_is_refused_exactly_when_its_name_is_taken | observation=for each of 12 binder names across the let and pattern shapes, the response status and its categories | mutant=a rule that compares a binder only with the parameters accepts the binder named offset and the law fails
  - LAW2 | A pattern variable is visible only inside its own clause, so any number of disjoint clauses may bind one spelling | generator=test_one_spelling_is_free_in_every_disjoint_clause | observation=for 2, 3, 4 and 5 clauses, that all-clauses-bind-tone is completed and that one clause binding the parameter name is refused once | mutant=a rule that collects the bindings of every clause into one scope refuses the accepted program and the law fails
  - LAW3 | A let nested inside another may bind any name of its own at any depth, but not a name an enclosing let already binds | generator=test_a_nested_let_may_not_rebind_an_enclosing_binding | observation=at depths 2, 8 and 40, that distinct names are completed and that rebinding the outermost name is refused once | mutant=a rule that checks a binder only against the parameters and the declarations accepts the rebinding and the law fails
- **messages**:
  - MSG1 | a function with parameter cents whose body is (let ((cents (+ cents 10))) cents) | the let binding cents hides the parameter cents of the same function | core-0 forbids a binding that shadows a visible value binding, so a reader cannot tell which cents a use means | rename the let binding to a name that is not visible there | test=test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it
  - MSG2 | a function whose parameter is named result | the parameter result uses the word core-0 reserves | only a postcondition may read result, where it names the function return value, so no binder may use it | rename the binder and read result in a postcondition only | test=test_a_binder_named_result_is_refused
  - MSG3 | the pattern (Pair n n) over a record of 2 Int fields | the pattern variable n is bound twice in one pattern | a pattern variable binds once per pattern, so the tool cannot tell which field a use of n means | give the second field a name of its own | test=test_a_pattern_that_binds_one_name_to_both_fields_is_refused
- **red**: `uv run pytest -q tests/acceptance/test_f5_b1_a_let_hiding_a_parameter_is_refused.py tests/acceptance/test_f5_b2_a_pattern_variable_hiding_a_function_is_refused.py tests/acceptance/test_f5_b3_a_binder_named_result_is_refused.py tests/acceptance/test_f5_b4_result_read_outside_a_postcondition_is_refused.py tests/acceptance/test_f5_b5_a_pattern_binding_one_name_twice_is_refused.py tests/acceptance/test_f5_b6_one_spelling_in_two_clauses_is_accepted.py tests/acceptance/test_f5_b7_the_manifest_publishes_the_new_categories.py tests/properties/test_f5_binding_scope.py tests/acceptance/test_f5_char1_shipped_programs_still_check.py tests/acceptance/test_f5_b8_a_parameter_hiding_another_binding_is_refused.py` exited 1 in 1.711s
  - failing on the pre-feature tree (28): tests/acceptance/test_f5_b1_a_let_hiding_a_parameter_is_refused.py::test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it, tests/acceptance/test_f5_b2_a_pattern_variable_hiding_a_function_is_refused.py::test_a_pattern_variable_spelled_like_a_declared_function_is_refused, tests/acceptance/test_f5_b3_a_binder_named_result_is_refused.py::test_a_binder_named_result_is_refused[parameter], tests/acceptance/test_f5_b3_a_binder_named_result_is_refused.py::test_a_binder_named_result_is_refused[let-binding], tests/acceptance/test_f5_b3_a_binder_named_result_is_refused.py::test_a_binder_named_result_is_refused[pattern-variable], tests/acceptance/test_f5_b4_result_read_outside_a_postcondition_is_refused.py::test_a_program_that_reads_result_in_its_body_and_precondition_is_refused, tests/acceptance/test_f5_b5_a_pattern_binding_one_name_twice_is_refused.py::test_a_pattern_that_binds_one_name_to_both_fields_is_refused, tests/acceptance/test_f5_b6_one_spelling_in_two_clauses_is_accepted.py::test_a_clause_variable_is_visible_only_inside_its_own_clause, tests/acceptance/test_f5_b7_the_manifest_publishes_the_new_categories.py::test_the_manifest_lists_the_two_refusals_this_rule_adds, tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[let-cents], tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[let-offset], tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[let-not], tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[let-result], tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[pattern-b], tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[pattern-offset], tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[pattern-not], tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[pattern-result], tests/properties/test_f5_binding_scope.py::test_one_spelling_is_free_in_every_disjoint_clause[2], tests/properties/test_f5_binding_scope.py::test_one_spelling_is_free_in_every_disjoint_clause[3], tests/properties/test_f5_binding_scope.py::test_one_spelling_is_free_in_every_disjoint_clause[4], tests/properties/test_f5_binding_scope.py::test_one_spelling_is_free_in_every_disjoint_clause[5], tests/properties/test_f5_binding_scope.py::test_a_nested_let_may_not_rebind_an_enclosing_binding[2], tests/properties/test_f5_binding_scope.py::test_a_nested_let_may_not_rebind_an_enclosing_binding[8], tests/properties/test_f5_binding_scope.py::test_a_nested_let_may_not_rebind_an_enclosing_binding[40], tests/acceptance/test_f5_char1_shipped_programs_still_check.py::test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it[examples/hour-clock.prova], tests/acceptance/test_f5_char1_shipped_programs_still_check.py::test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it[conformance/add-one.prova], tests/acceptance/test_f5_b8_a_parameter_hiding_another_binding_is_refused.py::test_a_parameter_spelled_like_a_declared_function_is_refused, tests/acceptance/test_f5_b8_a_parameter_hiding_another_binding_is_refused.py::test_a_signature_whose_second_parameter_repeats_the_first_is_refused
  - tests (read from the run): 28 failed, 16 passed in 1.32s
  ```text
          response = run_result.response()
  >       assert response.get("status") == "invalid_program", (
                 ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
              f"a program whose binding breaks the {category!r} rule was not refused: "
              f"{response}. A binding that may not be introduced must make the program "
              "invalid; report it as an invalid program."
          )
  E       AssertionError: a program whose binding breaks the 'shadowed_binding' rule was not refused: {'operation': 'check', 'status': 'completed', 'claim': {'kind': 'static_check', 'scope': 'this input'}, 'source_digest': '02a169a41ba5842206ad9bb915171692d9d5a930574d8c9b9511de9eb33de258', 'diagnostics': []}. A binding that may not be introduced must make the program invalid; report it as an invalid program.

  tests/acceptance/_f5_binding_fixtures.py:316: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f5_b1_a_let_hiding_a_parameter_is_refused.py::test_a_let_that_binds_the_name_of_a_parameter_is_refused_naming_it
  FAILED tests/acceptance/test_f5_b2_a_pattern_variable_hiding_a_function_is_refused.py::test_a_pattern_variable_spelled_like_a_declared_function_is_refused
  FAILED tests/acceptance/test_f5_b3_a_binder_named_result_is_refused.py::test_a_binder_named_result_is_refused[parameter]
  FAILED tests/acceptance/test_f5_b3_a_binder_named_result_is_refused.py::test_a_binder_named_result_is_refused[let-binding]
  FAILED tests/acceptance/test_f5_b3_a_binder_named_result_is_refused.py::test_a_binder_named_result_is_refused[pattern-variable]
  FAILED tests/acceptance/test_f5_b4_result_read_outside_a_postcondition_is_refused.py::test_a_program_that_reads_result_in_its_body_and_precondition_is_refused
  FAILED tests/acceptance/test_f5_b5_a_pattern_binding_one_name_twice_is_refused.py::test_a_pattern_that_binds_one_name_to_both_fields_is_refused
  FAILED tests/acceptance/test_f5_b6_one_spelling_in_two_clauses_is_accepted.py::test_a_clause_variable_is_visible_only_inside_its_own_clause
  FAILED tests/acceptance/test_f5_b7_the_manifest_publishes_the_new_categories.py::test_the_manifest_lists_the_two_refusals_this_rule_adds
  FAILED tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[let-cents]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[let-offset]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[let-not]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[let-result]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[pattern-b]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[pattern-offset]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[pattern-not]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken[pattern-result]
  FAILED tests/properties/test_f5_binding_scope.py::test_one_spelling_is_free_in_every_disjoint_clause[2]
  FAILED tests/properties/test_f5_binding_scope.py::test_one_spelling_is_free_in_every_disjoint_clause[3]
  FAILED tests/properties/test_f5_binding_scope.py::test_one_spelling_is_free_in_every_disjoint_clause[4]
  FAILED tests/properties/test_f5_binding_scope.py::test_one_spelling_is_free_in_every_disjoint_clause[5]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_nested_let_may_not_rebind_an_enclosing_binding[2]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_nested_let_may_not_rebind_an_enclosing_binding[8]
  FAILED tests/properties/test_f5_binding_scope.py::test_a_nested_let_may_not_rebind_an_enclosing_binding[40]
  FAILED tests/acceptance/test_f5_char1_shipped_programs_still_check.py::test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it[examples/hour-clock.prova]
  FAILED tests/acceptance/test_f5_char1_shipped_programs_still_check.py::test_a_shipped_program_is_still_accepted_and_the_rule_runs_on_it[conformance/add-one.prova]
  FAILED tests/acceptance/test_f5_b8_a_parameter_hiding_another_binding_is_refused.py::test_a_parameter_spelled_like_a_declared_function_is_refused
  FAILED tests/acceptance/test_f5_b8_a_parameter_hiding_another_binding_is_refused.py::test_a_signature_whose_second_parameter_repeats_the_first_is_refused
  28 failed, 16 passed in 1.32s
  ```

## 3. design: Find the owners and design the change (revision 1)

- **owners**:
  - a binding may not hide a name already visible => new: src/prova/checker.py has no owner for lexical scope; the rule arrives as a value that carries its own refusal, beside the F2, F3 and F4 rules
  - no binder may use result => new: src/prova/checker.py, a second small value beside the first; today result is only a key put into the environment of an ensures clause and nothing refuses a binder that takes it
  - which names are visible where a binding is introduced => new: src/prova/checker.py; the existing environment of _infer carries the TYPE of each name, not what introduced it, and the refusal must say parameter, let binding, pattern variable or function
  - the builtin operator names => src/prova/syntax.py OPERATORS, reused and not changed
  - the builtin type names => src/prova/checker.py BUILTIN_TYPES, reused and not changed
  - the type of every name and expression => src/prova/checker.py _infer and _pattern_bindings, reused and not changed: the new rule decides no type
  - the parsed shape of a program, its signatures and its patterns => src/prova/syntax.py, read only; feature F6 owns changes there
  - the categories the tool publishes => src/prova/service.py DIAGNOSTIC_CATEGORIES, extended by the 2 new names
  - how one diagnostic becomes a JSON response entry => src/prova/service.py _diagnostic_dict, reused and not changed
- **reuse_decision**: Reused: the Diagnostic value and its category, reason and location fields, so the response shape does not change; syntax.OPERATORS as the one list of builtin operator names; the existing walks of _infer and _pattern_bindings, which keep deciding types. Created new: three small frozen values in checker.py (the names visible at a binding, a binding that hides one of them, a binder that uses the reserved word) and one walk that visits every binder of every function, placed beside the declaration, function-cycle and type-cycle rules. No existing owner fits because nothing in the program today knows what introduced a name: the environment of the type inference maps a name to its type, which cannot say parameter or function, and the duplicate-declaration rule reads top-level declarations only, never a local binder.
- **paradigm**: oo
- **boundaries**:
  - checker to service: a list of Diagnostic values with a category, a reason and a place; owned by service, whose response construction is unchanged
  - service to the caller: the one JSON response of an operation; owned by service and the command entry point, unchanged by this rule
  - checker to syntax: the parsed program is read and never built or changed here; owned by syntax, where feature F6 works in parallel
  - the published vocabulary: the manifest of the discover operation, owned by service, which gains the 2 new category names
- **domain_types**:
  - VisibleNames: the names in scope where a binding is introduced, each with what introduced it (a parameter, an enclosing let binding, a pattern variable of the same pattern, a declared function, a builtin operator), able to say what a new binder would hide and to answer with a new scope for a clause or a let body
  - HiddenBinding: one binder that takes a visible name, holding the binder, what it hides and the place; it carries the shadowed_binding refusal
  - ReservedBinder: one binder that uses result, holding the kind of binder and the place; it carries the reserved_name refusal
  - Binder: the name a parameter, a let binding or a pattern variable introduces, with the kind of binder it is and where it is written, so a refusal can name it
- **invariants**:
  - INV1 | Every refusal of this rule names the binder, what it hides and the line and column where the binder is written | witness=src/prova/checker.py:HiddenBinding | bypass=none
  - INV2 | A binder is refused as reserved exactly when it introduces the name result; reading result where no binder introduces it stays the unbound-name refusal the tool already gives | witness=src/prova/checker.py:ReservedBinder | bypass=none
  - INV3 | A pattern variable is visible only inside its own clause, so no clause sees the bindings of a sibling clause, while the variables of one pattern are visible to each other and a repeat is refused | witness=src/prova/checker.py:VisibleNames | bypass=none
  - INV4 | Every category this rule can answer with is published by the manifest, so a caller can read the vocabulary from the tool | witness=src/prova/service.py:DIAGNOSTIC_CATEGORIES | bypass=none
  - INV5 | The rule changes no type decision and no other refusal: a program that breaks none of these rules gets the answer it gets today | witness=src/prova/checker.py:check_program | bypass=none
- **prefactoring**: no
- **prefactoring_reason**: The existing code needs no preparation. The rule is a walk over the parsed program that returns its own refusals, added beside the declaration rule, the function-cycle rule and the type-cycle rule in check_program, exactly as F2, F3 and F4 were added; no existing function changes its signature, its result or its behaviour, and no primitive has to be wrapped first because the new values are built from the names and places syntax already carries.

## 4. craft: Craft the change (revision 1)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 91.742s
  - tests (read from the run): 901 passed in 91.62s
  - slowest: 5.75s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 3.77s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.30s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 2.85s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.34s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.68s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.41s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.31s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.22s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  - slowest: 1.21s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  ```text
  ........................................................................ [  7%]
  ........................................................................ [ 15%]
  ........................................................................ [ 23%]
  ........................................................................ [ 31%]
  ........................................................................ [ 39%]
  ........................................................................ [ 47%]
  ........................................................................ [ 55%]
  ........................................................................ [ 63%]
  ........................................................................ [ 71%]
  ........................................................................ [ 79%]
  ........................................................................ [ 87%]
  ........................................................................ [ 95%]
  .....................................                                    [100%]
  ============================= slowest 10 durations =============================
  5.75s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  3.77s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.30s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  2.85s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.34s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.68s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.41s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.31s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.22s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1.21s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  901 passed in 91.62s (0:01:31)
  ```
- **scorecard**: `uv run python -m compileall -q src` exited 0 in 0.031s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this process environment, so jev_decide.py exited 3 before sending anything; the category, builtin-scope and parameter questions were settled locally against SPEC.md lines 145-149 and the F3 and F4 code. No linter or type checker is configured in this project (nothing in pyproject.toml and no .nwave config), so the scorecard compiles the package instead.
