# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 857 tests, all green on main).
  - not-testable (challenge this): names the project, its test command and its green baseline
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority for the rules
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on what the change may edit
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): tells me what to do if a conflict appears
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): excludes a directory from the work
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): names the worktree and branch to work in
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a constraint on the commit message
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line the commit message ends with
- S9: Do not push and do not merge.
  - not-testable (challenge this): forbids pushing and merging
- S10: Keep the full suite green.
  - not-testable (challenge this): preservation, not a change: the shipped programs check before and after, pinned by the characterisation tests in test_f6_b6, which prove no change and so carry no promise here
- S11: Another delivery runs in parallel in a different worktree: F5 (binding scope rules: shadowing, `result`, repeated pattern variables, in src/prova/checker.py; keep your own checker.py edits to the smallest possible and do not touch scope or binder logic).
  - not-testable (challenge this): names a parallel delivery and keeps me out of its code
- S12: Existing categories already include `cyclic_dependency` (F2), `duplicate_declaration` (F3) and `recursive_type` (F4); read how F2-F4 were built in src/prova/checker.py and syntax.py and follow the same structure (small named values, one owner per rule, a published category if you need a new one, said in your oracle note with the reason).
  - not-testable (challenge this): tells me which existing rules to read and imitate
- S13: Reuse an existing category if it fits.
  - not-testable (challenge this): tells me to reuse a category that fits
- S14: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell hygiene for recording the steps
- S15: Known bug that belongs to this feature: a malformed signature such as `(sig ((n Int)) Int)` crashes the parser with an unhandled IndexError at src/prova/syntax.py (`return_type = node.items[3].text`) instead of a `syntax` diagnostic; it also happens on main.
  - promises: P3, P8
  - tests P3: test_a_signature_with_no_arrow_is_refused_instead_of_crashing
  - tests P8: test_every_malformed_source_is_refused_by_every_operation_that_reads_source
- S16: Fix it as part of the marker checks and cover it with a test.
  - promises: P3, P8
  - tests P3: test_a_signature_with_no_arrow_is_refused_instead_of_crashing
  - tests P8: test_every_malformed_source_is_refused_by_every_operation_that_reads_source
- S17: The empty-program and empty-examples rules must not break the hour clock, the reservation example, or conformance/add-one.prova.
  - not-testable (challenge this): preservation, not a change: the three shipped programs check before and after, pinned by the characterisation tests in test_f6_b6
- S18: **Outcome.** Source that uses a reserved word as a name, an upper-case function
  - promises: P1, P2, P10
  - tests P1: test_a_function_named_let_is_refused_and_the_refusal_names_let
  - tests P2: test_a_function_named_with_a_capital_first_letter_is_refused
  - tests P10: test_a_constructor_named_as_a_builtin_type_is_refused
- S19: name, or a mangled `->` / `!` / `=>` marker is refused at the place it appears.
  - promises: P3, P4, P7
  - tests P3: test_a_signature_with_no_arrow_is_refused_instead_of_crashing
  - tests P4: test_an_example_whose_arrow_is_the_signature_arrow_is_refused
  - tests P7: test_the_refused_signature_is_placed_on_the_line_it_stands_on
- S20: **Acceptance criteria**
  - not-testable (challenge this): a heading that introduces the criteria
- S21: 1.
  - not-testable (challenge this): the number of the first criterion
- S22: Given a function named `let`, `if`, `match` or any other reserved word, when the
  - promises: P1
  - tests P1: test_a_function_named_let_is_refused_and_the_refusal_names_let
- S23: program is checked, then it is invalid and the diagnostic names the reserved word.
  - promises: P1
  - tests P1: test_a_function_named_let_is_refused_and_the_refusal_names_let
- S24: 2.
  - not-testable (challenge this): the number of the second criterion
- S25: Given a function or parameter whose name starts with a capital, then it is
  - promises: P2
  - tests P2: test_a_function_named_with_a_capital_first_letter_is_refused
- S26: invalid; given a type name that starts lower-case, then it is invalid.
  - promises: P2
  - tests P2: test_a_function_named_with_a_capital_first_letter_is_refused
- S27: 3.
  - not-testable (challenge this): the number of the third criterion
- S28: Given a signature whose arrow or effect marker is anything other than `->` and
  - promises: P3
  - tests P3: test_a_signature_with_no_arrow_is_refused_instead_of_crashing
- S29: `!
  - promises: P3
  - tests P3: test_a_signature_with_no_arrow_is_refused_instead_of_crashing
- S30: pure`, then it is invalid.
  - promises: P3
  - tests P3: test_a_signature_with_no_arrow_is_refused_instead_of_crashing
- S31: 4.
  - not-testable (challenge this): the number of the fourth criterion
- S32: Given an example whose arrow is not `=>`, then it is invalid.
  - promises: P4
  - tests P4: test_an_example_whose_arrow_is_the_signature_arrow_is_refused
- S33: 5.
  - not-testable (challenge this): the number of the fifth criterion
- S34: Given a source with no declarations at all, then it is invalid.
  - promises: P5, P9
  - tests P5: test_a_source_with_no_text_at_all_is_refused
  - tests P9: test_the_source_that_declares_nothing_gets_one_refusal_everywhere
- S35: 6.
  - not-testable (challenge this): the number of the sixth criterion
- S36: Given a function with an empty `(examples)` block, then it is invalid.
  - promises: P6
  - tests P6: test_a_function_whose_examples_block_is_empty_is_refused
- S37: 7.
  - not-testable (challenge this): the number of the seventh criterion
- S38: Given the hour clock and the reservation example, then both still check.
  - not-testable (challenge this): preservation, not a change: the hour clock and the reservation example check before and after, pinned by the characterisation tests in test_f6_b6
- S39: **SPEC.md** lines 65-74 (name shape, reserved words, marker tokens), 92, 99-106.
  - not-testable (challenge this): cites the specification lines the rules come from
- S40: **Dependencies** none, but it shares `src/prova/syntax.py` with F9.
  - not-testable (challenge this): names the files this work shares with another feature
- S41: **Size** M:
  - not-testable (challenge this): declares the size of the delivery
- S42: touches the reader-to-tree boundary where diagnostics currently lose their position.
  - promises: P7
  - tests P7: test_the_refused_signature_is_placed_on_the_line_it_stands_on
- S43: **Touches** `src/prova/syntax.py`, `src/prova/checker.py`, tests.
  - not-testable (challenge this): names the files the work is expected to touch
- S44: **Why it is a real expectation** probes L3, L4 disagree, plus the three marker and
  - not-testable (challenge this): says why the expectation is real
- S45: empty-block findings in section 1.
  - not-testable (challenge this): says why the expectation is real

## Edge matrix

- I1.empty: the empty source text with no declaration => invalid_program with a syntax refusal asking for at least one deftype or defn | self-probe: not probed | pre-feature not probed
- I1.unknown: a function named with the reserved word let, a word the grammar never allows as a name => invalid_program with a syntax refusal naming let as reserved | self-probe: not probed | pre-feature not probed
- I1.malformed: the signature (sig ((n Int)) Int), which leaves out both marker tokens => invalid_program with a syntax refusal naming the missing arrow, exit code 0 | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): check reads only the source text in the request and opens no file, service or other program
- I1.repeated: the same misspelled source checked twice => the identical refusal both times, and nothing written or kept between the two runs | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): each run is one process reading one request and writing one response, sharing no state with another run
- I1.crash: n/a (challenge this): the command holds no state across runs, so an interrupted run leaves nothing to recover and the next run starts from the request alone
- I2.empty: the empty source text sent to examples, evaluate and verify => invalid_program with the same syntax refusal, never unavailable and never a crash | self-probe: not probed | pre-feature not probed
- I2.unknown: a function named with the reserved word if sent to verify => invalid_program with the syntax refusal naming if, and no obligation inventory | self-probe: not probed | pre-feature not probed
- I2.malformed: the arrowless signature sent to examples => invalid_program with the syntax refusal, and no example run | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): these operations read only the source text and the arguments in the request and open no file or service
- I2.repeated: the same source sent twice to verify => the identical answer both times, with nothing written or kept between them | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): each run is one process reading one request and writing one response, sharing no state with another run
- I2.crash: n/a (challenge this): these operations keep nothing across runs, so an interrupted run leaves nothing half-applied

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN a program whose 1 function is named 'let'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' with 1 syntax refusal naming 'let' as reserved
  - test: test_a_function_named_let_is_refused_and_the_refusal_names_let
- SC2 (P1): not-held (no held self-probe case)
  - GIVEN each of the 27 words the language reserves as that function's name
  - WHEN each source is checked
  - THEN all 27 are 'invalid_program' and each refusal names its own word
  - test: test_every_word_the_language_reserves_is_refused_as_a_function_name
- SC3 (P2): not-held (no held self-probe case)
  - GIVEN a program whose 1 function is named 'Add-one'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names 'Add-one'
  - test: test_a_function_named_with_a_capital_first_letter_is_refused
- SC4 (P2): not-held (no held self-probe case)
  - GIVEN a signature whose 1 parameter is named 'N'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names 'N'
  - test: test_a_parameter_named_with_a_capital_first_letter_is_refused
- SC5 (P2): not-held (no held self-probe case)
  - GIVEN 1 declared type named 'point'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names 'point'
  - test: test_a_type_named_with_a_lower_case_first_letter_is_refused
- SC6 (P2): not-held (no held self-probe case)
  - GIVEN a union with 2 variants, the first named 'red'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names 'red'
  - test: test_a_constructor_named_with_a_lower_case_first_letter_is_refused
- SC7 (P3): not-held (no held self-probe case)
  - GIVEN the signature '(sig ((n Int)) Int)' with 0 marker tokens
  - WHEN the source is checked
  - THEN the command exits 0 with 1 syntax refusal naming the missing arrow
  - test: test_a_signature_with_no_arrow_is_refused_instead_of_crashing
- SC8 (P3): not-held (no held self-probe case)
  - GIVEN a signature whose arrow is the example arrow '=' followed by '>'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names both arrows
  - test: test_a_signature_whose_arrow_is_the_example_arrow_is_refused
- SC9 (P3): not-held (no held self-probe case)
  - GIVEN a signature whose effect marker is '?'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names '?' and the marker it must be
  - test: test_a_signature_whose_effect_marker_is_not_the_bang_is_refused
- SC10 (P3): not-held (no held self-probe case)
  - GIVEN a signature declaring the effect 'impure'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names 'impure' and 'pure'
  - test: test_a_signature_declaring_an_effect_other_than_pure_is_refused
- SC11 (P4): not-held (no held self-probe case)
  - GIVEN the example '(example (add-one 41) -' plus '> 42)'
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names the example arrow
  - test: test_an_example_whose_arrow_is_the_signature_arrow_is_refused
- SC12 (P5): not-held (no held self-probe case)
  - GIVEN the empty source text with 0 declarations
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal asks for at least one 'deftype' or 'defn'
  - test: test_a_source_with_no_text_at_all_is_refused
- SC13 (P5): not-held (no held self-probe case)
  - GIVEN a source of 1 comment line and blank space only
  - WHEN the source is checked
  - THEN the status is 'invalid_program' with that same refusal
  - test: test_a_source_of_only_a_comment_is_refused
- SC14 (P6): not-held (no held self-probe case)
  - GIVEN the function 'add-one' whose examples clause holds 0 examples
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names 'add-one' and asks for at least one example
  - test: test_a_function_whose_examples_block_is_empty_is_refused
- SC17 (P8): not-held (no held self-probe case)
  - GIVEN the 29 enumerated truncated or mangled sources, among them '(defn)', '(deftype T ())' and '(sig ((n)) -> Int ! pure)'
  - WHEN each is sent to check, examples, verify and evaluate
  - THEN all 116 answers are 'invalid_program' with 1 syntax refusal placed on a line of the source, and none raises
  - test: test_every_malformed_source_is_refused_by_every_operation_that_reads_source
- SC18 (P9): not-held (no held self-probe case)
  - GIVEN the empty source text with 0 declarations
  - WHEN it is sent to check, examples, verify and evaluate
  - THEN the 4 diagnostics are equal, each 1 syntax refusal at line 1
  - test: test_the_source_that_declares_nothing_gets_one_refusal_everywhere
- SC19 (P10): not-held (no held self-probe case)
  - GIVEN the union '(deftype Measure (union (Int) (Bool)))' whose first variant is named for a builtin type
  - WHEN the source is checked
  - THEN the status is 'invalid_program' and the refusal names 'Int' as reserved
  - test: test_a_constructor_named_as_a_builtin_type_is_refused
- SC15 (P7): not-held (no held self-probe case)
  - GIVEN a program whose misspelled signature stands on line 2
  - WHEN the source is checked
  - THEN the refusal reports location line 2
  - test: test_the_refused_signature_is_placed_on_the_line_it_stands_on
- SC16 (P7): not-held (no held self-probe case)
  - GIVEN a program whose misspelled example stands on line 3
  - WHEN the source is checked
  - THEN the refusal reports location line 3
  - test: test_the_refused_example_is_placed_on_its_own_line

## Questions for the owner

- S34: Should a source that declares nothing be invalid for every operation that reads source, or only for check?
  - existing behaviour: one unit test sends the empty source to every advertised operation and reads the status back, so the empty source already has an answer
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- A docs/f6-names-and-markers/DECISIONS.md (+18 -0 lines)
- A docs/f6-names-and-markers/SUMMARY.md (+620 -0 lines)
- A docs/f6-names-and-markers/TRACE.md (+6 -0 lines)
- A docs/feature/f6-names-and-markers/craft.md (+66 -0 lines)
- A docs/feature/f6-names-and-markers/design.md (+90 -0 lines)
- A docs/feature/f6-names-and-markers/oracle.md (+88 -0 lines)
- M docs/spec-trace.md (+1 -1 lines)
- M src/prova/service.py (+19 -4 lines)
- M src/prova/syntax.py (+422 -29 lines)
- A tests/acceptance/_f6_spelling_fixtures.py (+282 -0 lines)
- A tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py (+77 -0 lines)
- A tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py (+102 -0 lines)
- A tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py (+97 -0 lines)
- A tests/acceptance/test_f6_b4_an_example_with_the_wrong_arrow_is_refused.py (+50 -0 lines)
- A tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py (+66 -0 lines)
- A tests/acceptance/test_f6_b6_the_shipped_programs_still_check.py (+43 -0 lines)
- M tests/properties/test_f3_duplicate_declarations.py (+4 -1 lines)
- A tests/properties/test_f6_every_malformed_source_still_answers.py (+195 -0 lines)
- A tests/properties/test_f6_name_and_marker_spelling.py (+134 -0 lines)
- M tests/unit/test_verify_inventory_edges.py (+29 -12 lines)

## Commits (git log, BASE to HEAD)

- 2021b0d [F6] build a source refusal in one place
- 0b39ca3 [F6] state in tests how names and markers must be spelled
- f18410f [F6] record who owns each spelling rule, before writing one
- 9a61da2 [F6] refuse a name or marker core-0 does not spell that way
- 070f06c Correct two expectations the empty-program rule contradicts
- a96b17f [F6] answer every source the reader cannot read, never raise
- f017243 [F6] cover the pattern a constructor position must hold
- 5ac07fb [F6] record the delivery beside the change
- 7948627 [F6] regenerate the record after the design step was recorded again
- 12fe06b [F6] regenerate the record after the craft step was recorded again
- f16931c Narrow the diagnostic-location row to what the tool really does
- 73d7e7f [F6] state the totality laws as the generated properties they are

## 4. oracle: Frame the work and write the oracle (revision 2)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f6/request.md
- **promises**:
  - P1: A function declared with a word the language reserves is refused, and the refusal names that word.
  - P2: A function or parameter name that starts with a capital is refused, and a type or constructor name that starts lower-case is refused.
  - P3: A signature whose arrow or effect marker is anything other than the arrow and the pure effect marker is refused, and the signature that leaves them out answers with that refusal instead of crashing.
  - P4: A declared example whose arrow is not the example arrow is refused.
  - P5: A source that declares nothing at all is refused.
  - P6: A function whose examples clause holds no example is refused.
  - P8: Every source, however truncated or mangled, gets one answer from every operation that reads source: a refusal carrying its place, never a traceback and never a half-built result.
  - P9: The source that declares nothing gets the identical refusal from every operation that reads source.
  - P10: A declared constructor may not be named for one of the builtin type names core-0 reserves.
  - P7: Every refusal of a misspelled name or marker is placed at the line the misspelling stands on.
- **sentence_map**:
  - S1 => not-testable: names the project, its test command and its green baseline
  - S2 => not-testable: names SPEC.md as the authority for the rules
  - S3 => not-testable: a constraint on what the change may edit
  - S4 => not-testable: tells me what to do if a conflict appears
  - S5 => not-testable: excludes a directory from the work
  - S6 => not-testable: names the worktree and branch to work in
  - S7 => not-testable: a constraint on the commit message
  - S8 => not-testable: the attribution line the commit message ends with
  - S9 => not-testable: forbids pushing and merging
  - S10 => not-testable: preservation, not a change: the shipped programs check before and after, pinned by the characterisation tests in test_f6_b6, which prove no change and so carry no promise here
  - S11 => not-testable: names a parallel delivery and keeps me out of its code
  - S12 => not-testable: tells me which existing rules to read and imitate
  - S13 => not-testable: tells me to reuse a category that fits
  - S14 => not-testable: shell hygiene for recording the steps
  - S15 => P3,P8
  - S16 => P3,P8
  - S17 => not-testable: preservation, not a change: the three shipped programs check before and after, pinned by the characterisation tests in test_f6_b6
  - S18 => P1,P2,P10
  - S19 => P3,P4,P7
  - S20 => not-testable: a heading that introduces the criteria
  - S21 => not-testable: the number of the first criterion
  - S22 => P1
  - S23 => P1
  - S24 => not-testable: the number of the second criterion
  - S25 => P2
  - S26 => P2
  - S27 => not-testable: the number of the third criterion
  - S28 => P3
  - S29 => P3
  - S30 => P3
  - S31 => not-testable: the number of the fourth criterion
  - S32 => P4
  - S33 => not-testable: the number of the fifth criterion
  - S34 => P5,P9
  - S35 => not-testable: the number of the sixth criterion
  - S36 => P6
  - S37 => not-testable: the number of the seventh criterion
  - S38 => not-testable: preservation, not a change: the hour clock and the reservation example check before and after, pinned by the characterisation tests in test_f6_b6
  - S39 => not-testable: cites the specification lines the rules come from
  - S40 => not-testable: names the files this work shares with another feature
  - S41 => not-testable: declares the size of the delivery
  - S42 => P7
  - S43 => not-testable: names the files the work is expected to touch
  - S44 => not-testable: says why the expectation is real
  - S45 => not-testable: says why the expectation is real
- **scenarios**:
  - SC1 | P1 | GIVEN a program whose 1 function is named 'let' | WHEN the source is checked | THEN the status is 'invalid_program' with 1 syntax refusal naming 'let' as reserved
  - SC2 | P1 | GIVEN each of the 27 words the language reserves as that function's name | WHEN each source is checked | THEN all 27 are 'invalid_program' and each refusal names its own word
  - SC3 | P2 | GIVEN a program whose 1 function is named 'Add-one' | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names 'Add-one'
  - SC4 | P2 | GIVEN a signature whose 1 parameter is named 'N' | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names 'N'
  - SC5 | P2 | GIVEN 1 declared type named 'point' | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names 'point'
  - SC6 | P2 | GIVEN a union with 2 variants, the first named 'red' | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names 'red'
  - SC7 | P3 | GIVEN the signature '(sig ((n Int)) Int)' with 0 marker tokens | WHEN the source is checked | THEN the command exits 0 with 1 syntax refusal naming the missing arrow
  - SC8 | P3 | GIVEN a signature whose arrow is the example arrow '=' followed by '>' | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names both arrows
  - SC9 | P3 | GIVEN a signature whose effect marker is '?' | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names '?' and the marker it must be
  - SC10 | P3 | GIVEN a signature declaring the effect 'impure' | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names 'impure' and 'pure'
  - SC11 | P4 | GIVEN the example '(example (add-one 41) -' plus '> 42)' | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names the example arrow
  - SC12 | P5 | GIVEN the empty source text with 0 declarations | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal asks for at least one 'deftype' or 'defn'
  - SC13 | P5 | GIVEN a source of 1 comment line and blank space only | WHEN the source is checked | THEN the status is 'invalid_program' with that same refusal
  - SC14 | P6 | GIVEN the function 'add-one' whose examples clause holds 0 examples | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names 'add-one' and asks for at least one example
  - SC17 | P8 | GIVEN the 29 enumerated truncated or mangled sources, among them '(defn)', '(deftype T ())' and '(sig ((n)) -> Int ! pure)' | WHEN each is sent to check, examples, verify and evaluate | THEN all 116 answers are 'invalid_program' with 1 syntax refusal placed on a line of the source, and none raises
  - SC18 | P9 | GIVEN the empty source text with 0 declarations | WHEN it is sent to check, examples, verify and evaluate | THEN the 4 diagnostics are equal, each 1 syntax refusal at line 1
  - SC19 | P10 | GIVEN the union '(deftype Measure (union (Int) (Bool)))' whose first variant is named for a builtin type | WHEN the source is checked | THEN the status is 'invalid_program' and the refusal names 'Int' as reserved
  - SC15 | P7 | GIVEN a program whose misspelled signature stands on line 2 | WHEN the source is checked | THEN the refusal reports location line 2
  - SC16 | P7 | GIVEN a program whose misspelled example stands on line 3 | WHEN the source is checked | THEN the refusal reports location line 3
- **conflicts**:
  - S1 | NONE | ran the named suite on the branch point: 857 tests pass, so the baseline the sentence states is the one I measured
  - S2 | NONE | read SPEC.md lines 55-115: the lexical rules and the core grammar state every rule this feature refuses, and nothing in them contradicts a criterion
  - S3 | NONE | the change adds new test files only and edits no existing test and no line of SPEC.md
  - S4 | NONE | searched the test corpus for names and markers the new rules would refuse and found none, so no existing test asks for the opposite result
  - S5 | NONE | nothing outside the .relay directory is read by the work, and no test reads that directory
  - S6 | NONE | all work happens in the worktree at prova-wt-f6 on branch feat/f6, which git reports as its branch
  - S7 | NONE | no commit hook in the worktree forbids the attribution line, since the worktree declares no commit hooks at all
  - S8 | NONE | the attribution line is plain text in a commit message and contradicts nothing the repository checks
  - S9 | NONE | no step of the work needs a push or a merge, and the branch tracks nothing
  - S10 | NONE | the whole suite is green at the branch point and the new rules are additions, so keeping it green stays possible
  - S11 | NONE | the spelling rules live at the reader-to-tree boundary in syntax.py and need no scope or binder logic from checker.py
  - S12 | NONE | read the F2, F3 and F4 rules in checker.py and syntax.py: each owns one rule in a small named value, and this feature follows that structure
  - S13 | NONE | the published syntax category already means source the tool cannot read as a program, which is what each new rule reports
  - S14 | NONE | every submission is written to a file and run from it, so no shell expands a marker token
  - S15 | NONE | reproduced the crash on the branch point: the command exits 1 and prints a traceback instead of one JSON refusal
  - S16 | NONE | the fix belongs to the same signature rule as the other marker checks, and no existing test observes the crash
  - S17 | NONE | checked all 3 shipped programs: each declares at least one function and every examples clause holds at least one example
  - S18 | NONE | no existing test declares a reserved word or a capitalised function name, so refusing them contradicts nothing
  - S19 | NONE | existing syntax refusals carry no location although the error already holds one, so adding it widens a response and removes nothing
  - S20 | NONE | a heading introduces the criteria and states no behaviour that could contradict the system
  - S21 | NONE | a criterion number states no behaviour that could contradict the system
  - S22 | NONE | searched every declared function name in the tests, examples and conformance programs: none is a reserved word
  - S23 | NONE | no existing test asserts the wording of a syntax refusal, so naming the reserved word breaks no assertion
  - S24 | NONE | a criterion number states no behaviour that could contradict the system
  - S25 | NONE | every declared function and parameter name in the repository starts lower-case, so the capital rule refuses none of them
  - S26 | NONE | every declared type and constructor name in the repository starts upper-case, so the lower-case rule refuses none of them
  - S27 | NONE | a criterion number states no behaviour that could contradict the system
  - S28 | NONE | every signature in the repository is written with the arrow and the pure effect marker the grammar gives
  - S29 | NONE | the effect marker in every existing signature is the one the grammar gives
  - S30 | NONE | pure is the only effect any existing signature declares, so refusing another one contradicts nothing
  - S31 | NONE | a criterion number states no behaviour that could contradict the system
  - S32 | NONE | every declared example in the repository uses the example arrow, so refusing another arrow refuses no existing program
  - S33 | NONE | a criterion number states no behaviour that could contradict the system
  - S34 | CONFLICT | one unit test sends the empty source to every advertised operation and reads the status back, so the empty source already has an answer | Should a source that declares nothing be invalid for every operation that reads source, or only for check?
  - S35 | NONE | a criterion number states no behaviour that could contradict the system
  - S36 | NONE | searched the repository for an examples clause with no example and found none, so refusing it refuses no existing program
  - S37 | NONE | a criterion number states no behaviour that could contradict the system
  - S38 | NONE | checked the hour clock and the reservation example against every new rule by hand: both are spelled as the language defines
  - S39 | NONE | read the cited specification lines: they state the name shapes, the reserved words, the marker tokens and the two plus-one repetitions
  - S40 | NONE | the parallel feature named for syntax.py is not running in this worktree, so no edit of it can collide here
  - S41 | NONE | the declared size decides which steps are due and contradicts no behaviour of the system
  - S42 | NONE | confirmed at the branch point that a syntax refusal carries no location, which is the loss the sentence describes
  - S43 | NONE | the rules belong in syntax.py, and the manifest in service.py needs no new category, so the touched files are the named ones and one more
  - S44 | NONE | a reason for the expectation states no behaviour that could contradict the system
  - S45 | NONE | a reason for the expectation states no behaviour that could contradict the system
- **decisions**:
  - S34: A source that declares nothing is refused wherever a program is read, which is every operation that takes source, because the grammar says a program is one or more declarations and the four operations all build the same tree; the existing unit test only requires that such an operation does not answer unavailable, and an invalid program is not unavailable, so it keeps passing.
  - DEC1: All seven rules are reported in the published syntax category instead of a new one, because the specification places every one of them in its lexical rules and core grammar and the syntax category already means source the tool cannot read as a program; a new category would split one meaning in two and oblige every caller to learn a word for the same defect.
  - DEC2: A syntax refusal now carries the location the error already holds, because the outcome asks for the refusal at the place it appears; this adds a field to a response and removes nothing, so no caller that reads the old fields breaks.
  - DEC3: The reserved-word and name-shape rules are applied to declared function names, parameter names, type names and constructor names only. Field names are a value-name position too, but no criterion names them and the parallel delivery owns the result name in binding positions, so widening there stays out of this change.
  - DEC4: Type references inside a signature or a field keep their present answer, an unknown-type refusal from the checker, because no criterion asks for a spelling rule on a use of a name and existing tests observe that answer.
  - DEC5: Jev was asked the two open semantic questions (which category carries the new refusals, and which component owns the empty-program rule) and answered typesafe: unavailable, because TYPESAFE_API_KEY is absent from the environment; both questions were then decided locally in DEC1 and in the owner decision for S34.
- **mapping**:
  - P1 => test_a_function_named_let_is_refused_and_the_refusal_names_let
  - P2 => test_a_function_named_with_a_capital_first_letter_is_refused
  - P3 => test_a_signature_with_no_arrow_is_refused_instead_of_crashing
  - P4 => test_an_example_whose_arrow_is_the_signature_arrow_is_refused
  - P5 => test_a_source_with_no_text_at_all_is_refused
  - P6 => test_a_function_whose_examples_block_is_empty_is_refused
  - P8 => test_every_malformed_source_is_refused_by_every_operation_that_reads_source
  - P9 => test_the_source_that_declares_nothing_gets_one_refusal_everywhere
  - P10 => test_a_constructor_named_as_a_builtin_type_is_refused
  - P7 => test_the_refused_signature_is_placed_on_the_line_it_stands_on
- **covers_scenarios**:
  - SC1 => test_a_function_named_let_is_refused_and_the_refusal_names_let
  - SC2 => test_every_word_the_language_reserves_is_refused_as_a_function_name
  - SC3 => test_a_function_named_with_a_capital_first_letter_is_refused
  - SC4 => test_a_parameter_named_with_a_capital_first_letter_is_refused
  - SC5 => test_a_type_named_with_a_lower_case_first_letter_is_refused
  - SC6 => test_a_constructor_named_with_a_lower_case_first_letter_is_refused
  - SC7 => test_a_signature_with_no_arrow_is_refused_instead_of_crashing
  - SC8 => test_a_signature_whose_arrow_is_the_example_arrow_is_refused
  - SC9 => test_a_signature_whose_effect_marker_is_not_the_bang_is_refused
  - SC10 => test_a_signature_declaring_an_effect_other_than_pure_is_refused
  - SC11 => test_an_example_whose_arrow_is_the_signature_arrow_is_refused
  - SC12 => test_a_source_with_no_text_at_all_is_refused
  - SC13 => test_a_source_of_only_a_comment_is_refused
  - SC14 => test_a_function_whose_examples_block_is_empty_is_refused
  - SC17 => test_every_malformed_source_is_refused_by_every_operation_that_reads_source
  - SC18 => test_the_source_that_declares_nothing_gets_one_refusal_everywhere
  - SC19 => test_a_constructor_named_as_a_builtin_type_is_refused
  - SC15 => test_the_refused_signature_is_placed_on_the_line_it_stands_on
  - SC16 => test_the_refused_example_is_placed_on_its_own_line
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
  - SC17 => base differs
  - SC18 => base differs
  - SC19 => base differs
  - SC15 => base differs
  - SC16 => base differs
- **interfaces**:
  - I1: the installed prova command's JSON stdin and stdout surface, operation check, which reads a source text and answers with a status and diagnostics
  - I2: the same command's operations examples, evaluate and verify, which read a source text through the same reader-to-tree boundary before doing their own work
- **matrix**:
  - I1.empty => the empty source text with no declaration => invalid_program with a syntax refusal asking for at least one deftype or defn
  - I1.unknown => a function named with the reserved word let, a word the grammar never allows as a name => invalid_program with a syntax refusal naming let as reserved
  - I1.malformed => the signature (sig ((n Int)) Int), which leaves out both marker tokens => invalid_program with a syntax refusal naming the missing arrow, exit code 0
  - I1.dependency-gone => n/a: check reads only the source text in the request and opens no file, service or other program
  - I1.repeated => the same misspelled source checked twice => the identical refusal both times, and nothing written or kept between the two runs
  - I1.concurrent => n/a: each run is one process reading one request and writing one response, sharing no state with another run
  - I1.crash => n/a: the command holds no state across runs, so an interrupted run leaves nothing to recover and the next run starts from the request alone
  - I2.empty => the empty source text sent to examples, evaluate and verify => invalid_program with the same syntax refusal, never unavailable and never a crash
  - I2.unknown => a function named with the reserved word if sent to verify => invalid_program with the syntax refusal naming if, and no obligation inventory
  - I2.malformed => the arrowless signature sent to examples => invalid_program with the syntax refusal, and no example run
  - I2.dependency-gone => n/a: these operations read only the source text and the arguments in the request and open no file or service
  - I2.repeated => the same source sent twice to verify => the identical answer both times, with nothing written or kept between them
  - I2.concurrent => n/a: each run is one process reading one request and writing one response, sharing no state with another run
  - I2.crash => n/a: these operations keep nothing across runs, so an interrupted run leaves nothing half-applied
- **laws**:
  - LAW4 | every source, however truncated or mangled, gets one refusal with a place from every operation that reads source, and none raises | generator=test_every_malformed_source_is_refused_by_every_operation_that_reads_source | observation=the status, the diagnostic categories and the location every source-reading operation answers for each enumerated malformed source | mutant=indexing a fixed grammar position without reading what stands there, which ends in a traceback instead of an answer
  - LAW5 | the source that declares nothing is refused identically by every operation that reads source | generator=test_the_source_that_declares_nothing_gets_one_refusal_everywhere | observation=the diagnostics list each of the four operations answers for the empty source | mutant=deciding the rule in one operation only, which answers the same source two ways
  - LAW1 | a declared function name is accepted exactly when it has the value-name shape the specification states and is not a word the language reserves | generator=test_a_function_name_is_accepted_exactly_when_it_has_the_defined_shape | observation=the status and the syntax diagnostics the check operation answers for a program whose only difference is that name | mutant=accepting any name whose first character is a lower-case letter, which lets a reserved word and a name holding a capital through
  - LAW2 | a signature is accepted exactly when its arrow and its effect marker and effect are the three tokens the grammar gives | generator=test_a_signature_is_accepted_exactly_when_its_markers_are_the_defined_ones | observation=the status and the syntax diagnostics the check operation answers for a program whose only difference is those three tokens | mutant=reading the return type by position without looking at the tokens around it, which accepts every marker and crashes when one is missing
  - LAW3 | a declared example is accepted exactly when its arrow is the example arrow | generator=test_an_example_is_accepted_exactly_when_its_arrow_is_the_defined_one | observation=the status and the syntax diagnostics the check operation answers for a program whose only difference is the example arrow | mutant=checking only that the example form has four members, which accepts any token in the arrow position
- **messages**:
  - MSG8 | the form (deftype T) with no body | the body of type 'T' is missing | core-0 fixes what stands at that position, so the tool cannot read the form without it | write it as (deftype TypeName (record (field Type) ...)) or with a union body | test=test_every_malformed_source_is_refused_by_every_operation_that_reads_source
  - MSG9 | a union variant named Int | the constructor name Int is one of the builtin type names core-0 reserves | a reserved type name already means a builtin type wherever it appears, so a declaration cannot introduce it again | give the constructor a name of its own, such as Whole | test=test_a_constructor_named_as_a_builtin_type_is_refused
  - MSG1 | a function named let | the name let is a reserved word of the language | a reserved word already means something else wherever it appears, so a declaration of that name would be ambiguous | rename the function to a name the language does not reserve, such as step-one | test=test_a_function_named_let_is_refused_and_the_refusal_names_let
  - MSG2 | a function named Add-one | the function name Add-one starts with a capital letter | a value or function name must have the shape the specification gives, so that the first letter says whether a name means a value or a type | spell the name in lower case, as add-one | test=test_a_function_named_with_a_capital_first_letter_is_refused
  - MSG3 | a declared type named point | the type name point starts lower-case | a type or constructor name must start with a capital, so that a reader and the checker can tell a type from a value | spell the type name with a capital first letter, as Point | test=test_a_type_named_with_a_lower_case_first_letter_is_refused
  - MSG4 | the signature (sig ((n Int)) Int) | the signature carries no return arrow and no effect marker | a signature is read by its marker tokens, so without them the tool cannot tell which word is the return type | write the signature with the arrow before the return type and the pure effect marker after it | test=test_a_signature_with_no_arrow_is_refused_instead_of_crashing
  - MSG5 | an example whose arrow is the signature arrow | the example carries the wrong arrow between its call and its expected value | each marker token stands at one grammar position only, so the example arrow is the only token allowed there | write the example arrow between the call and the expected value | test=test_an_example_whose_arrow_is_the_signature_arrow_is_refused
  - MSG6 | the empty source text | the source declares no type and no function | a program is one or more declarations, so there is nothing for the tool to check | add at least one deftype or defn form to the source | test=test_a_source_with_no_text_at_all_is_refused
  - MSG7 | a function whose examples clause is written with no example | the function add-one declares an examples clause holding no example | an examples clause must hold at least one example, because the examples are how a function states what it does | add at least one example to the clause, or remove the function | test=test_a_function_whose_examples_block_is_empty_is_refused
- **red**: `uv run pytest -q tests/properties/test_f6_every_malformed_source_still_answers.py tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py tests/acceptance/test_f6_b4_an_example_with_the_wrong_arrow_is_refused.py tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py tests/properties/test_f6_name_and_marker_spelling.py` exited 1 in 3.181s
  - failing on the pre-feature tree (24): tests/properties/test_f6_every_malformed_source_still_answers.py::test_every_malformed_source_is_refused_by_every_operation_that_reads_source, tests/properties/test_f6_every_malformed_source_still_answers.py::test_every_malformed_source_says_where_it_went_wrong, tests/properties/test_f6_every_malformed_source_still_answers.py::test_the_source_that_declares_nothing_gets_one_refusal_everywhere, tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py::test_a_function_named_let_is_refused_and_the_refusal_names_let, tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py::test_a_function_named_if_or_match_is_refused_naming_the_word, tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py::test_every_word_the_language_reserves_is_refused_as_a_function_name, tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_function_named_with_a_capital_first_letter_is_refused, tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_parameter_named_with_a_capital_first_letter_is_refused, tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_type_named_with_a_lower_case_first_letter_is_refused, tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_constructor_named_with_a_lower_case_first_letter_is_refused, tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_constructor_named_as_a_builtin_type_is_refused, tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_a_signature_with_no_arrow_is_refused_instead_of_crashing, tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_a_signature_whose_arrow_is_the_example_arrow_is_refused, tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_a_signature_whose_effect_marker_is_not_the_bang_is_refused, tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_a_signature_declaring_an_effect_other_than_pure_is_refused, tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_the_refused_signature_is_placed_on_the_line_it_stands_on, tests/acceptance/test_f6_b4_an_example_with_the_wrong_arrow_is_refused.py::test_an_example_whose_arrow_is_the_signature_arrow_is_refused, tests/acceptance/test_f6_b4_an_example_with_the_wrong_arrow_is_refused.py::test_the_refused_example_is_placed_on_its_own_line, tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py::test_a_source_with_no_text_at_all_is_refused, tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py::test_a_source_of_only_a_comment_is_refused, tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py::test_a_function_whose_examples_block_is_empty_is_refused, tests/properties/test_f6_name_and_marker_spelling.py::test_a_function_name_is_accepted_exactly_when_it_has_the_defined_shape, tests/properties/test_f6_name_and_marker_spelling.py::test_a_signature_is_accepted_exactly_when_its_markers_are_the_defined_ones, tests/properties/test_f6_name_and_marker_spelling.py::test_an_example_is_accepted_exactly_when_its_arrow_is_the_defined_one
  - tests (read from the run): 24 failed, 6 passed in 2.43s
  ```text
              "program the language does not define must be invalid, and say so in that "
              "category."
          )
  E       AssertionError: the example arrow '=' is not spelled as the language defines it but was not refused as an invalid program with a 'syntax' diagnostic: {'operation': 'check', 'status': 'completed', 'claim': {'kind': 'static_check', 'scope': 'this input'}, 'source_digest': 'a932a3815aebfdc20da21569d96ffab373edd5e4b5b3d3925420cb523428ed58', 'diagnostics': []}. A program the language does not define must be invalid, and say so in that category.
  E       assert False
  E        +  where False = _refused_for_spelling({'operation': 'check', 'status': 'completed', 'claim': {'kind': 'static_check', 'scope': 'this input'}, 'source_digest': 'a932a3815aebfdc20da21569d96ffab373edd5e4b5b3d3925420cb523428ed58', ...})
  E       Failing test case: test_an_example_is_accepted_exactly_when_its_arrow_is_the_defined_one(
  E           arrow='=',
  E       )
  E       Explanation:
  E           These lines were always and only run by failing test cases:
  E               /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f6/red-tree/tests/properties/test_f6_name_and_marker_spelling.py:83

  tests/properties/test_f6_name_and_marker_spelling.py:83: AssertionError
  =========================== short test summary info ============================
  FAILED tests/properties/test_f6_every_malformed_source_still_answers.py::test_every_malformed_source_is_refused_by_every_operation_that_reads_source
  FAILED tests/properties/test_f6_every_malformed_source_still_answers.py::test_every_malformed_source_says_where_it_went_wrong
  FAILED tests/properties/test_f6_every_malformed_source_still_answers.py::test_the_source_that_declares_nothing_gets_one_refusal_everywhere
  FAILED tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py::test_a_function_named_let_is_refused_and_the_refusal_names_let
  FAILED tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py::test_a_function_named_if_or_match_is_refused_naming_the_word
  FAILED tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py::test_every_word_the_language_reserves_is_refused_as_a_function_name
  FAILED tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_function_named_with_a_capital_first_letter_is_refused
  FAILED tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_parameter_named_with_a_capital_first_letter_is_refused
  FAILED tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_type_named_with_a_lower_case_first_letter_is_refused
  FAILED tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_constructor_named_with_a_lower_case_first_letter_is_refused
  FAILED tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py::test_a_constructor_named_as_a_builtin_type_is_refused
  FAILED tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_a_signature_with_no_arrow_is_refused_instead_of_crashing
  FAILED tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_a_signature_whose_arrow_is_the_example_arrow_is_refused
  FAILED tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_a_signature_whose_effect_marker_is_not_the_bang_is_refused
  FAILED tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_a_signature_declaring_an_effect_other_than_pure_is_refused
  FAILED tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py::test_the_refused_signature_is_placed_on_the_line_it_stands_on
  FAILED tests/acceptance/test_f6_b4_an_example_with_the_wrong_arrow_is_refused.py::test_an_example_whose_arrow_is_the_signature_arrow_is_refused
  FAILED tests/acceptance/test_f6_b4_an_example_with_the_wrong_arrow_is_refused.py::test_the_refused_example_is_placed_on_its_own_line
  FAILED tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py::test_a_source_with_no_text_at_all_is_refused
  FAILED tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py::test_a_source_of_only_a_comment_is_refused
  FAILED tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py::test_a_function_whose_examples_block_is_empty_is_refused
  FAILED tests/properties/test_f6_name_and_marker_spelling.py::test_a_function_name_is_accepted_exactly_when_it_has_the_defined_shape
  FAILED tests/properties/test_f6_name_and_marker_spelling.py::test_a_signature_is_accepted_exactly_when_its_markers_are_the_defined_ones
  FAILED tests/properties/test_f6_name_and_marker_spelling.py::test_an_example_is_accepted_exactly_when_its_arrow_is_the_defined_one
  24 failed, 6 passed in 2.43s
  ```

## 5. design: Find the owners and design the change (revision 2)

- **owners**:
  - the shape of a declared value or function name, and the words the language reserves => src/prova/syntax.py, in a new ValueName value read at every value-name position
  - the shape of a declared type or constructor name => src/prova/syntax.py, in a new TypeName value read at every type-name position
  - the three reserved marker tokens, each at the one grammar position it stands at => src/prova/syntax.py, in a new MarkerToken value used by the signature reader and the example reader
  - a grammar repetition written with a plus must have at least one member (program declarations, function examples) => src/prova/syntax.py, in a new AtLeastOne value with one named instance per repetition
  - the list of words the language reserves => src/prova/syntax.py, composed from the SPECIAL_FORMS and OPERATORS sets already defined there plus the remaining core keywords, so no second list exists
  - how a refusal the reader raises becomes one JSON diagnostic, with its category and its place => src/prova/service.py, in one syntax-diagnostic builder the four source-reading operations all call
  - which categories the manifest publishes => src/prova/service.py, unchanged: the published syntax category already carries every new refusal, so nothing is added there
  - that a name is declared only once, and the rules of the checker => src/prova/checker.py and syntax.DeclaredName, unchanged: uniqueness and scope are a different question from spelling, and the delivery running beside this one owns that file
- **reuse_decision**: Reused: SyntaxError_ as the one refusal the reader raises, with the line and column it already carries; the published syntax diagnostic category, because SPEC.md places all seven rules in its lexical rules and core grammar and that category already means source the tool cannot read as a program; the SPECIAL_FORMS and OPERATORS sets already in syntax.py, so the reserved words are composed from them instead of written out a second time; the shape of the existing DeclaredName value, so the new values read like their siblings. New: ValueName, TypeName, MarkerToken and AtLeastOne, because no existing unit owns the spelling of a name or a marker. DeclaredName is the nearest candidate and does not fit: it is built after a declaration is parsed, it covers functions, types, constructors and fields but never a parameter, and it owns whether a name is declared twice, not how a name is spelled. Keeping the two questions in two owners leaves one decider for each. Nothing is added to checker.py, so the parallel delivery's scope and binder logic is untouched.
- **paradigm**: oo
- **boundaries**:
  - the reader-to-tree boundary, from the generic Atom and SList nodes to the typed core-0 tree: owned by src/prova/syntax.py, which is where every new rule is decided and where the place of a misspelling is still known
  - the tool's JSON response boundary, the category, reason and location of a diagnostic: owned by src/prova/service.py, which is the only place that turns a refusal into a response
  - the published manifest of diagnostic categories: owned by src/prova/service.py and crossed by nothing in this change, because no new category is published
  - the whole-program checking boundary in src/prova/checker.py: not crossed by this change, because a misspelling is refused before a tree exists to check
- **domain_types**:
  - ValueName: the spelling of a declared value or function name, refused at construction unless it has the shape SPEC.md gives and is none of the words the language reserves; carries the place it stands at, so the refusal can say where
  - TypeName: the spelling of a declared type or constructor name, refused at construction unless it starts with a capital and holds only letters and digits; carries its place
  - MarkerToken: one reserved marker token together with the single grammar position it stands at and the repair a reader needs; three named instances, the return arrow, the effect marker and the example arrow, and one method that demands it at that position
  - AtLeastOne: a grammar repetition written with a plus, holding what it repeats and how to repair a source that writes none; two named instances, the declarations of a program and the examples of a function
  - Signature and Function, unchanged in shape: they keep holding plain spellings, because the reader now refuses every spelling they could not hold
- **invariants**:
  - INV1 | a ValueName exists only for a spelling that has the value-name shape of SPEC.md and is not a reserved word, so no misspelled function or parameter name can reach the typed tree | witness=src/prova/syntax.py:ValueName | bypass=a caller that builds a Function value by hand, bypassing the reader, still passes a plain string; the reader is the only producer of a Function in this tool
  - INV2 | a TypeName exists only for a spelling that starts with a capital and holds only letters and digits, so no lower-case type or constructor name can reach the typed tree | witness=src/prova/syntax.py:TypeName | bypass=the same hand-built value bypass as INV1; type references inside a signature keep the checker's unknown-type answer and are not read as a TypeName
  - INV3 | each of the three reserved marker tokens is demanded by one owner at the one grammar position it stands at, so a signature or an example with a mangled or missing marker is refused instead of being read by position | witness=src/prova/syntax.py:MarkerToken | bypass=none
  - INV4 | every grammar repetition written with a plus is read through one owner that refuses an empty one, so a program with no declaration and a function with no example are both refused | witness=src/prova/syntax.py:AtLeastOne | bypass=none
  - INV5 | every syntax refusal in a response is built in one place and carries the place the refusal holds, so the four operations that read source answer alike and none loses the position | witness=src/prova/service.py:_syntax_diagnostic | bypass=none
- **prefactoring**: yes
- **prefactoring_reason**: The four operations that read source each build their own syntax diagnostic dictionary from the same two fields, so the response shape is decided in four places. A first commit extracts those four literals into one builder and changes no behaviour: the same category and the same reason come back, no test is edited and the suite stays green. Only then does the behaviour commit add the location to that single builder, so the place arrives in all four answers at once instead of being added four times.

## 6. craft: Craft the change (revision 2)

- **refactor_commits**:
  - 2021b0da308c5e70f314c2fa253a3ded01605059
- **refactor_check**: the check ran on the parent and on each refactor commit
  - 2021b0da308c ([F6] build a source refusal in one place): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 102.519s
  - tests (read from the run): 890 passed in 102.37s
  - slowest: 6.36s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.29s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.82s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.20s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.40s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.92s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.61s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.43s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.38s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 1.37s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  8%]
  ........................................................................ [ 16%]
  ........................................................................ [ 24%]
  ........................................................................ [ 32%]
  ........................................................................ [ 40%]
  ........................................................................ [ 48%]
  ........................................................................ [ 56%]
  ........................................................................ [ 64%]
  ........................................................................ [ 72%]
  ........................................................................ [ 80%]
  ........................................................................ [ 88%]
  ........................................................................ [ 97%]
  ..........................                                               [100%]
  ============================= slowest 10 durations =============================
  6.36s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.29s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.82s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.20s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.40s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.92s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.61s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.43s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.38s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1.37s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  890 passed in 102.37s (0:01:42)
  ```
- **scorecard**: `uv run python -m compileall -q src/prova tests` exited 0 in 0.058s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this process environment, so the client exited 3 when the two open semantic questions (which category carries the new refusals, which component owns the empty-program rule) were sent; both were then decided locally, in design decision DEC1 and in the owner's Option A answer

## 7. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the four owners the design named are the four values built, and no fifth decider appeared: ValueName, TypeName, MarkerToken and AtLeastOne in src/prova/syntax.py, with one syntax-diagnostic builder in src/prova/service.py:124; checker.py stayed untouched as the design said
  - D2: fixed:the reserved words are composed from the SPECIAL_FORMS and OPERATORS sets already in the module instead of a second list, and the four source-reading operations build their refusal in one place after the prefactor commit; the one duplication left, syntax.BUILTIN_TYPE_NAMES against checker.BUILTIN_TYPES, carries a comment at its definition naming why it waits for the file's owner, and is recorded as a follow-up in the handoff
  - D3: pass - every rule is decided at the reader-to-tree boundary in syntax.py, which depends on reader.py only; service.py depends on syntax and never the other way, and no response shape reached the reader
  - D4: fixed:a misspelled name cannot be built at all, because the refusal is in the constructor and not at each call site: src/prova/syntax.py:44 for a value name and :86 for a type name, so no misspelled name reaches the typed tree; the open bypass is a Function value built by hand, which no path in this tool does
  - D5: pass - each new value holds one reason to change and names it from the grammar, the longest being MarkerToken.demand at src/prova/syntax.py:146; the break from the two-instance rule is deliberate and shared with the sibling DeclaredName, because a refusal needs the place it stands at (role, text, line, column)
  - D6: n/a: no pattern was introduced: the change is four value objects with smart constructors and one builder, and the nearest pattern candidate, a visitor over the tree, would add a layer no accepted outcome reads
  - D7: pass - the names come from the language the specification speaks (value name, type name, marker token, declaration, example, clause, effect) and none from mechanics; the refusals are stated in the same words a reader of SPEC.md uses
  - D8: pass - no filesystem, process, clock or transport entered syntax.py; the reader hands it nodes and it hands back a tree or a refusal, and the only I/O in the change is the tests reading the shipped programs
  - D9: fixed:every acceptance test drives the installed command over its real JSON stdin and stdout, at tests/acceptance/_f6_spelling_fixtures.py:212, and imports nothing from src/prova; the property tests use the service's public operation contract in process, as the sibling property tests do
  - D10: pass - each test name is a sentence about what a reader of a program gets (a function named as a reserved word is refused, the shipped programs still check) and carries no production symbol, layer term or process id
  - D11: pass - the shared fixtures own the programs and the readers of a refusal once, and each test states only its own stimulus and observation; no helper owns a whole scenario
  - D12: fixed:three generated properties state the laws over spellings and markers no table can carry, at tests/properties/test_f6_name_and_marker_spelling.py:92, each with its expected verdict computed from the specification and not from the tool; the closed sets, the reserved words and the malformed family, are walked exhaustively instead, at tests/properties/test_f6_every_malformed_source_still_answers.py:47
  - D13: pass - nine consecutive runs of the eight F6 files all gave 33 passed, median 2.22 s and slowest run 2.30 s, with no flake; the one test above the unit budget, 0.93 to 1.04 s, starts the real command once per reserved word and is listed with that reason in docs/feature/f6-names-and-markers/craft.md
  - D14: pass - each test adds an observation no other makes: one refusal per rule with its own accepted twin, the enumerated family for totality, and the three properties for the laws; no property repeats a finite example's pair
  - D15: fixed:every refusal says what failed, why it matters and how to repair it, with the offending spelling quoted and its place carried, for example src/prova/syntax.py:699 for a missing grammar position and :62 for a reserved word; each assertion message in the new tests is worded the same way
  - D16: n/a: no model for the spelling rules: they name no shared state, no multi-step protocol, no concurrency and no crash window; each is a total function from one source text to one answer, and the laws it does claim are checked by the generated properties and the enumerated family
  - D17: fixed:the specification trace row about diagnostic locations claimed Done while recursive_type and unbound_type still carry none, and was narrowed to Partial with that reason in f16931c, documents only; oracle.md names the promises added after the first review, and craft.md states the test cost, the probe and what is still open
- **independent_review**:
  - REV1 | reviewer=implementation-review | findings=7, verdict REJECT at 070f06c | resolution=all 7 fixed in a96b17f, f017243
  - REV2 | reviewer=implementation-review | findings=1, verdict REJECT at f017243 (6 of 7 verified: 3800 fuzz requests 0 exceptions, 10/10 guard deletions red, 890 passed) | resolution=spec-trace row 8.6 narrowed to Partial in f16931c, documents only, checked by owner

## 8. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
  - Two expectations written before the empty-program rule contradicted it and were corrected with the owner's authorisation, minimally and in their own commit.
- **not_verified**:
  - The duplication between syntax.BUILTIN_TYPE_NAMES and checker.BUILTIN_TYPES is not resolved: the same three builtin type names are declared in two modules, because checker.py belongs to the delivery running beside this one. Reconciling them is one line once that file is free, and a comment at the definition says so.
  - Four forms are still accepted with text silently dropped, as they are on the branch point: (deftype T (record (x Int)) extra), (requires), (ensures) and (if true 1 2 3). They are not crashes and no rule of this feature covers them; refusing a form that carries more than the grammar fixes is a rule of its own.
  - recursive_type and unbound_type diagnostics still carry no location, so only reader and syntax refusals say where they happened. The specification trace row about diagnostic locations is Partial for that reason.
  - Whether the spelling rules hold for every name position of the language: field names are a value-name position too and are not read for their spelling here, and a use of a type name keeps the checker's unknown-type answer. Both are recorded design decisions, not measurements.
  - The Jev question service was never reached: its key is absent from this environment, so the two open semantic questions were decided locally and recorded instead of being put to it.
  - No formal model was written or run. The spelling rules name no shared state, no protocol and no crash window, so the claim rests on the generated properties and the enumerated family, which are evidence and not proof.
  - The malformed family is an enumerated set of twenty-nine shapes, not an exhaustive search of every source text. A shape nobody wrote down could still be read raw somewhere, and the ten guard deletions show only that each guard the change added is load-bearing.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit 73d7e7fcb2ffc002cb21ed157b6c31c5bf7a5019
  - no checks declared

## Not backed by the diff

- A program is now refused when it spells a name or a marker other than core-0 defines it: a reserved word as a function name, a function or parameter starting with a capital, a type or constructor starting lower-case, a constructor named for a builtin type, an arrow or effect marker that is not the one the grammar fixes, a source that declares nothing, and an examples clause with no example.: a guarantee names no test function of the change
- Each refusal is answered in the published syntax category, says what is wrong and how to repair it, and carries the line and column it stands at, built in the one place every operation that reads source calls.: a guarantee names no test function of the change
- The same reader is now total: every grammar position it fixes is read through one owner that refuses what is missing or of the wrong kind, so the malformed signature that used to end the command in a traceback, and twenty-eight further truncated or mangled shapes, now come back as one answer.: a guarantee names no test function of the change
- Four values own the rules, each refusing its invalid spelling at construction, so no misspelled name reaches the typed tree; the checker was not touched.: a guarantee names no test function of the change
- Checked through the installed command's real JSON surface for each rule with its accepted twin, by generated properties for the spelling, marker and totality laws, by an enumerated family of malformed shapes read by all four source-reading operations, and by the three shipped programs, which still check.: a guarantee names no test function of the change
