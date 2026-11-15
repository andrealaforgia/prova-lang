# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1241 tests, all green on main).
  - not-testable (challenge this): context about the project and its green baseline
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names the authority document to read
- S3: Do not change SPEC.md or any existing test's expected result.
  - promises: P7
  - tests P7: test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - promises: P7
  - tests P7: test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): tells which directory to leave alone
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): process promise about where the work happens
- S7: Commit with a message ending in the line
  - not-testable (challenge this): process promise about the commit message
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): process promise, the co-author line itself
- S9: Do not push and do not merge.
  - not-testable (challenge this): process promise, nothing is pushed or merged
- S10: Keep the full suite green.
  - promises: P7
  - tests P7: test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- S11: Another delivery (F15, `format`, formatter.py and its fixtures) runs in parallel in a different worktree; this delivery changes reader.py or the request reader and tests only.
  - not-testable (challenge this): process promise about which files this delivery touches
- S12: F1 to F14 and R1 are on main; read how R1 made every request answer one JSON response (the request reader in service.py, `malformed_request`, the nesting and evaluation limits, `resource_exhausted`) and how F14 bounded the request read (budgets.py, __main__.py `_read_at_most`) and follow that structure.
  - not-testable (challenge this): tells which existing structure to follow
- S13: If an existing test conflicts, stop and report.
  - promises: P7
  - tests P7: test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- S14: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): process promise about where the scripts of this run live
- S15: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): process promise about shell quoting and a clean tree
- S16: **Outcome.** Two crashes found by the F11 and F15 independent reviews, both older than the features that found them, are answered with one JSON response and a located refusal.
  - promises: P1, P3
  - tests P1: test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
  - tests P3: test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
- S17: **Acceptance criteria**
  - not-testable (challenge this): a heading that introduces the criteria below
- S18: 1.
  - not-testable (challenge this): the number of the first criterion
- S19: Given a request whose `source` holds a character that cannot be encoded as UTF-8, such as a lone surrogate (`{"operation":"check","source":"\udccc"}` as JSON text), then every operation that reads source answers `invalid_input` with `malformed_request` naming the `source` field and saying which character position cannot be encoded, with exit 0 and no traceback.
  - promises: P1
  - tests P1: test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
- S20: Today `SourceDigest.of` in `src/prova/service.py` raises `UnicodeEncodeError` (about line 452 to 536).
  - not-testable (challenge this): says where the crash stands today, not a promise
- S21: Check also `arguments` elements and every other place the request text is encoded or hashed, and the F14 size check (it sizes in bytes: it must not raise either).
  - promises: P2
  - tests P2: test_an_argument_that_cannot_be_written_as_utf8_names_that_argument
- S22: 2.
  - not-testable (challenge this): the number of the second criterion
- S23: Given a source holding an integer literal longer than Python's digit limit (more than 4300 digits), then every operation that reads source answers a located refusal with a published category (`syntax` with a reason naming the limit, or a limit category; decide with a reason and publish it in `discover` if it is a limit), never `ValueError: Exceeds the limit (4300 digits)` from `reader.py` `int(self.text)` or from anywhere else a literal is converted (`syntax.IntLit`, `values.render`, the evaluator, `format`, `parse`).
  - promises: P3
  - tests P3: test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
- S24: Choose the limit so it is far from Python's own, state the reason, and answer a literal exactly at the limit as before; integers beyond 64 bits stay exact below it.
  - promises: P4, P5
  - tests P4: test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
  - tests P5: test_the_manifest_says_how_long_a_literal_this_tool_reads
- S25: 3.
  - not-testable (challenge this): the number of the third criterion
- S26: Given the crash search the R1 reviewers used (a fixed derandomised fuzz of at least 500 mangled requests exists in the suite): extend it with these two families (lone surrogates anywhere in a request string, long digit runs in every integer position, including `arguments` text and examples) so a regression is caught.
  - promises: P6
  - tests P6: test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- S27: 4.
  - not-testable (challenge this): the number of the fourth criterion
- S28: Given everything accepted or produced before this change, then it is answered exactly as before (add fields or categories only; no existing test edited).
  - promises: P7
  - tests P7: test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- S29: **Authority** SPEC.md lines 463-482 and 503-508, and the R1 rule that every request gets one JSON answer.
  - not-testable (challenge this): names the authority lines behind these rules
- S30: **Size** S.
  - not-testable (challenge this): declares the size of this delivery

## Edge matrix

- I1.empty: a request whose source field is the empty text "" => answered as before, with no refusal about UTF-8 or about digits | self-probe: not probed | pre-feature not probed
- I1.unknown: an operation named "chec" with a lone surrogate inside it => answered "unavailable" with unknown_operation and exit 0 | self-probe: not probed | pre-feature not probed
- I1.malformed: {"operation":"check","source":"\udccc"} => "invalid_input" with 1 malformed_request naming "source" and position 0 | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the command reads 1 request from its own standard input and calls no other service
- I1.repeated: the same surrogate request sent 2 times => the same answer both times; the command keeps nothing between runs | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): 1 process answers 1 request and writes no shared file, so 2 runs share nothing
- I1.crash: n/a (challenge this): the command writes nothing but its 1 answer on standard output, so a run stopped part way leaves no state behind

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the request text {"operation":"check","source":"\udccc"}, whose source is 1 lone surrogate
  - WHEN it is sent to the prova command
  - THEN the answer is "invalid_input" with 1 malformed_request naming "source" and "position 0", and the command exits 0
  - test: test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
- SC2 (P1): not-held (no held self-probe case)
  - GIVEN a source written as "(defn" with a lone surrogate as its 6th character
  - WHEN the check operation is asked about it
  - THEN the refusal says "position 5" and not "position 0"
  - test: test_the_refusal_says_where_the_character_that_cannot_be_written_stands
- SC3 (P1): not-held (no held self-probe case)
  - GIVEN that same source and each of the 5 operations that read source
  - WHEN each one is sent
  - THEN each answers "invalid_input" naming "source", and none of them exits 1
  - test: test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
- SC4 (P2): not-held (no held self-probe case)
  - GIVEN an evaluate request whose arguments are ["(Clock 1)", "\udccc"]
  - WHEN it is sent to the prova command
  - THEN the refusal names "arguments[1]" and "position 0", not the source
  - test: test_an_argument_that_cannot_be_written_as_utf8_names_that_argument
- SC5 (P2): not-held (no held self-probe case)
  - GIVEN a source of 100001 characters whose last one is a lone surrogate
  - WHEN the check operation is asked about it
  - THEN 1 JSON answer comes back, "invalid_input" or "resource_exhausted", with exit 0
  - test: test_a_source_large_enough_to_be_sized_still_answers_when_it_holds_one
- SC6 (P3): not-held (no held self-probe case)
  - GIVEN a program whose body on line 4 writes 4301 digits
  - WHEN the check operation is asked about it
  - THEN the answer is "invalid_program" with 1 syntax refusal at line 4 naming 4301 and 1000, and the 4301 digits are not repeated in the answer
  - test: test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
- SC7 (P3): not-held (no held self-probe case)
  - GIVEN an evaluate request whose 1 argument is written as 4301 digits
  - WHEN it is sent to the prova command
  - THEN the answer is "invalid_input" with a located malformed_value naming 1000
  - test: test_a_literal_too_long_in_an_argument_is_refused_where_it_stands
- SC8 (P4): not-held (no held self-probe case)
  - GIVEN the same program written with exactly 1000 digits
  - WHEN its examples are run and it is evaluated
  - THEN both are "completed", the example passed is true, and the value answered is the same 1000 digits
  - test: test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
- SC9 (P5): not-held (no held self-probe case)
  - GIVEN a caller reading the 1 answer the "discover" operation gives
  - WHEN it reads the documentation it publishes
  - THEN the "integer_literals" entry names 1000
  - test: test_the_manifest_says_how_long_a_literal_this_tool_reads
- SC10 (P6): not-held (no held self-probe case)
  - GIVEN the 543 fixed mangled requests of the 2 families
  - WHEN each is sent through the entry point of the command
  - THEN each is 1 JSON answer carrying a status, with exit 0
  - test: test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- SC11 (P7): not-held (no held self-probe case)
  - GIVEN the 3 programs this repository ships and the 1241 tests already in the suite
  - WHEN the whole suite is run
  - THEN every shipped program is still answered "completed" and no existing test file is edited
  - test: test_every_request_of_the_two_families_is_answered_and_the_rest_still_works

## Questions for the owner

- S23: Shall the over-long literal be answered with the published syntax category and its length documented in discover, rather than as a third published resource limit that would break test_f14_b9?
  - existing behaviour: the sentence offers a new limit category published among the resource limits, and tests/acceptance/test_f14_b9 pins the published limits to exactly the 2 names evaluation_depth and expression_nesting, so publishing a third entry fails an existing test that S3 forbids editing
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- M src/prova/reader.py (+74 -0 lines)
- M src/prova/service.py (+121 -39 lines)
- A tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py (+195 -0 lines)
- A tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py (+221 -0 lines)
- A tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py (+338 -0 lines)

## Commits (git log, BASE to HEAD)

- 89f6657 Refuse half a character and an over-long run of digits

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-r2/request.md
- **promises**:
  - P1: Every operation that reads source answers a source holding a character that cannot be written as UTF-8 with invalid_input and one malformed_request naming the source field and the character position, exits 0 and writes nothing on standard error.
  - P2: Every other text a request carries, each arguments element and the function name, is refused the same way by name, and a source long enough to be measured in bytes is answered rather than measured into a failure.
  - P3: An integer literal longer than the 1000 digits this tool reads is refused where it stands, with a published category and a reason naming both lengths, in every operation that reads source and in the argument of an evaluate request.
  - P4: A literal of exactly 1000 digits is answered as it was before and kept exactly, far past 64 bits.
  - P5: The manifest documents how long an integer literal this tool reads, so a caller learns the length without meeting it.
  - P6: The fixed crash search of the suite covers both families: a lone surrogate anywhere in a text a request carries, and a run of digits in every integer position a request has.
  - P7: Everything the tool accepted or produced before this change is answered exactly as before, and no existing test is edited.
- **sentence_map**:
  - S1 => not-testable: context about the project and its green baseline
  - S2 => not-testable: names the authority document to read
  - S3 => P7
  - S4 => P7
  - S5 => not-testable: tells which directory to leave alone
  - S6 => not-testable: process promise about where the work happens
  - S7 => not-testable: process promise about the commit message
  - S8 => not-testable: process promise, the co-author line itself
  - S9 => not-testable: process promise, nothing is pushed or merged
  - S10 => P7
  - S11 => not-testable: process promise about which files this delivery touches
  - S12 => not-testable: tells which existing structure to follow
  - S13 => P7
  - S14 => not-testable: process promise about where the scripts of this run live
  - S15 => not-testable: process promise about shell quoting and a clean tree
  - S16 => P1,P3
  - S17 => not-testable: a heading that introduces the criteria below
  - S18 => not-testable: the number of the first criterion
  - S19 => P1
  - S20 => not-testable: says where the crash stands today, not a promise
  - S21 => P2
  - S22 => not-testable: the number of the second criterion
  - S23 => P3
  - S24 => P4,P5
  - S25 => not-testable: the number of the third criterion
  - S26 => P6
  - S27 => not-testable: the number of the fourth criterion
  - S28 => P7
  - S29 => not-testable: names the authority lines behind these rules
  - S30 => not-testable: declares the size of this delivery
- **scenarios**:
  - SC1 | P1 | GIVEN the request text {"operation":"check","source":"\udccc"}, whose source is 1 lone surrogate | WHEN it is sent to the prova command | THEN the answer is "invalid_input" with 1 malformed_request naming "source" and "position 0", and the command exits 0
  - SC2 | P1 | GIVEN a source written as "(defn" with a lone surrogate as its 6th character | WHEN the check operation is asked about it | THEN the refusal says "position 5" and not "position 0"
  - SC3 | P1 | GIVEN that same source and each of the 5 operations that read source | WHEN each one is sent | THEN each answers "invalid_input" naming "source", and none of them exits 1
  - SC4 | P2 | GIVEN an evaluate request whose arguments are ["(Clock 1)", "\udccc"] | WHEN it is sent to the prova command | THEN the refusal names "arguments[1]" and "position 0", not the source
  - SC5 | P2 | GIVEN a source of 100001 characters whose last one is a lone surrogate | WHEN the check operation is asked about it | THEN 1 JSON answer comes back, "invalid_input" or "resource_exhausted", with exit 0
  - SC6 | P3 | GIVEN a program whose body on line 4 writes 4301 digits | WHEN the check operation is asked about it | THEN the answer is "invalid_program" with 1 syntax refusal at line 4 naming 4301 and 1000, and the 4301 digits are not repeated in the answer
  - SC7 | P3 | GIVEN an evaluate request whose 1 argument is written as 4301 digits | WHEN it is sent to the prova command | THEN the answer is "invalid_input" with a located malformed_value naming 1000
  - SC8 | P4 | GIVEN the same program written with exactly 1000 digits | WHEN its examples are run and it is evaluated | THEN both are "completed", the example passed is true, and the value answered is the same 1000 digits
  - SC9 | P5 | GIVEN a caller reading the 1 answer the "discover" operation gives | WHEN it reads the documentation it publishes | THEN the "integer_literals" entry names 1000
  - SC10 | P6 | GIVEN the 543 fixed mangled requests of the 2 families | WHEN each is sent through the entry point of the command | THEN each is 1 JSON answer carrying a status, with exit 0
  - SC11 | P7 | GIVEN the 3 programs this repository ships and the 1241 tests already in the suite | WHEN the whole suite is run | THEN every shipped program is still answered "completed" and no existing test file is edited
- **conflicts**:
  - S1 | NONE | read the suite on the branch: 1241 tests, green, nothing about surrogates or digit runs
  - S2 | NONE | read SPEC.md lines 463-508: limits are published and must not silently bound what a program may mean
  - S3 | NONE | no existing test states an expected result for a surrogate or an over-long literal
  - S4 | NONE | the one conflict found is recorded against S23, where the sentence offers two answers
  - S5 | NONE | nothing of this change reads or writes the .relay directory at all
  - S6 | NONE | the work happens only in the worktree at prova-wt-r2 on its own branch
  - S7 | NONE | the repository has no commit-message hook that would refuse the co-author line
  - S8 | NONE | the line is appended as written; no hook in this worktree rewrites it
  - S9 | NONE | nothing in this delivery pushes or merges; the branch stays local
  - S10 | NONE | the whole suite was run before the change and after it, green both times
  - S11 | NONE | the change touches reader.py, the request reader in service.py and tests, not formatter.py
  - S12 | NONE | the refusal follows malformed_request of R1 and the one-object limit of the nesting limit
  - S13 | NONE | the same check as S4; the only conflict found stands at S23
  - S14 | NONE | every script of this run lives under the nwstep workspace directory
  - S15 | NONE | arrows and redirections are quoted in this script, and the tree is left clean
  - S16 | NONE | both crashes reproduced on the branch before the change, each exiting 1
  - S17 | NONE | a heading; nothing in the system contradicts it
  - S18 | NONE | a criterion number; nothing in the system contradicts it
  - S19 | NONE | the source field is read in one place today and refuses only a value of another kind
  - S20 | NONE | reproduced: SourceRevision.of at service.py line 536 raises UnicodeEncodeError
  - S21 | NONE | budgets.py sizes a text with surrogatepass already, so the size check raises nothing
  - S22 | NONE | a criterion number; nothing in the system contradicts it
  - S23 | CONFLICT | the sentence offers a new limit category published among the resource limits, and tests/acceptance/test_f14_b9 pins the published limits to exactly the 2 names evaluation_depth and expression_nesting, so publishing a third entry fails an existing test that S3 forbids editing | Shall the over-long literal be answered with the published syntax category and its length documented in discover, rather than as a third published resource limit that would break test_f14_b9?
  - S24 | NONE | 1000 digits is read and converted today; nothing in the tool refuses a literal for its length
  - S25 | NONE | a criterion number; nothing in the system contradicts it
  - S26 | NONE | the R1 corpus holds 1000 or so requests and no surrogate and no long digit run
  - S27 | NONE | a criterion number; nothing in the system contradicts it
  - S28 | NONE | the full suite passes unchanged after the change, so nothing answered before moved
  - S29 | NONE | SPEC.md lines 463-508 agree: every limit is observable and no limit silently bounds meaning
  - S30 | NONE | the size declared for this run is S, which is what the workspace holds
- **decisions**:
  - S23: Answer the over-long literal with the published syntax category, whose reason names both lengths, and document the length in the discover answer under integer_literals: a third entry under resource_limits.limits would fail tests/acceptance/test_f14_b9, which the request forbids editing, and the sentence itself offers the syntax category as the other answer. The owner is absent, so this is recorded as my decision.
  - DEC1: The limit is 1000 digits. It stands far below the 4300 of the interpreter, so every conversion this tool makes is well inside the interpreter own limit, and far above the 20 digits a value that fills 64 bits is written with; an integer below it is answered exactly.
  - DEC2: The UTF-8 rule is enforced once, in the request reader, by the SubmittedText value object every text field of a request is built through; SourceRevision.of now takes that object, so the hashing site cannot be reached with a text that has no bytes.
  - DEC3: An arguments element or a function name holding a lone surrogate is now refused as malformed_request naming that element, where a surrogate argument used to be answered malformed_value: one rule for every text a request carries. No existing test covered that case.
  - DEC4: No formal model, Quint or otherwise, pays here: the change adds no state, no protocol, no concurrency and no crash behaviour; it is one refusal decided from the text of one request.
  - DEC5: Found and not fixed, for the owner: an integer the evaluator computes, as three multiplications over 1000-digit literals, still ends in ValueError from values.render with exit 1. It is not a literal being converted, answering it needs a refusal for a value too large to write, and values.py is outside the files this delivery changes.
  - DEC6: Found and not fixed, for the owner: a budget variable set to a 5000-digit number ends in ValueError at budgets.py int(written). It enters from the environment and not from a request, so it is outside both families of this request.
  - DEC7: No prefactor commit was needed: service.py is the adapter that reads the request, the domain modules already take value objects, and the one text threaded through it became the SubmittedText value object inside this change.
- **mapping**:
  - P1 => test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
  - P2 => test_an_argument_that_cannot_be_written_as_utf8_names_that_argument
  - P3 => test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
  - P4 => test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
  - P5 => test_the_manifest_says_how_long_a_literal_this_tool_reads
  - P6 => test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
  - P7 => test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- **covers_scenarios**:
  - SC1 => test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
  - SC2 => test_the_refusal_says_where_the_character_that_cannot_be_written_stands
  - SC3 => test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
  - SC4 => test_an_argument_that_cannot_be_written_as_utf8_names_that_argument
  - SC5 => test_a_source_large_enough_to_be_sized_still_answers_when_it_holds_one
  - SC6 => test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
  - SC7 => test_a_literal_too_long_in_an_argument_is_refused_where_it_stands
  - SC8 => test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
  - SC9 => test_the_manifest_says_how_long_a_literal_this_tool_reads
  - SC10 => test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
  - SC11 => test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
- **predictions**:
  - SC1 => base differs
  - SC5 => base differs
  - SC6 => base differs
  - SC8 => base held
  - SC10 => base differs
  - SC11 => base held
- **interfaces**:
  - I1: the prova command standard input and standard output: one JSON request in, one JSON answer out, exit 0
- **matrix**:
  - I1.empty => a request whose source field is the empty text "" => answered as before, with no refusal about UTF-8 or about digits
  - I1.unknown => an operation named "chec" with a lone surrogate inside it => answered "unavailable" with unknown_operation and exit 0
  - I1.malformed => {"operation":"check","source":"\udccc"} => "invalid_input" with 1 malformed_request naming "source" and position 0
  - I1.dependency-gone => n/a: the command reads 1 request from its own standard input and calls no other service
  - I1.repeated => the same surrogate request sent 2 times => the same answer both times; the command keeps nothing between runs
  - I1.concurrent => n/a: 1 process answers 1 request and writes no shared file, so 2 runs share nothing
  - I1.crash => n/a: the command writes nothing but its 1 answer on standard output, so a run stopped part way leaves no state behind
- **laws**:
  - LAW1 | wherever a character that cannot be written as UTF-8 stands in a text a request carries, the tool answers with one JSON response carrying a status and exits 0, and a source holding one is refused by name with the position it stands at | generator=test_a_lone_surrogate_anywhere_in_a_request_is_answered | observation=the JSON printed, the exit code, and the symbol and reason of the refusal | mutant=a reader that refuses only a surrogate at position 0, or that names the request instead of the source field
  - LAW2 | a run of digits is refused for its length when, and only when, it is longer than the 1000 digits this tool reads | generator=test_a_run_of_digits_meets_the_limit_only_when_it_passes_it | observation=whether any refusal in the answer names at most 1000 digits | mutant=a limit that refuses every literal, or one that lets a 4301-digit literal reach the interpreter conversion
- **messages**:
  - MSG1 | {"operation":"check","source":"\udccc"} | the source field of the request holds a character at position 0 that cannot be written as UTF-8 | this tool reads every text a request carries as the bytes it is written in, and half of a character has none | send the field as text whose characters can all be written as UTF-8, writing a character outside the basic plane as the one character it is | test=test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
  - MSG2 | a program whose body writes 4301 digits | the integer literal written here is 4301 digits long and this tool reads an integer literal of at most 1000 digits | a longer run meets the 4300-digit refusal of the interpreter itself, which is not an answer to the caller | write the number with at most 1000 digits, and read that length from the integer_literals entry the discover operation documents | test=test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
- **red**: `uv run pytest -q tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py` exited 1 in 3.733s
  - failing on the pre-feature tree (12): tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it, tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_the_refusal_says_where_the_character_that_cannot_be_written_stands, tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_an_argument_that_cannot_be_written_as_utf8_names_that_argument, tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_a_request_whose_function_cannot_be_written_as_utf8_names_the_function, tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_a_source_large_enough_to_be_sized_still_answers_when_it_holds_one, tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py::test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact, tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py::test_every_operation_that_reads_source_refuses_the_same_literal, tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py::test_a_literal_too_long_in_an_argument_is_refused_where_it_stands, tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py::test_the_manifest_says_how_long_a_literal_this_tool_reads, tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py::test_every_request_of_the_two_families_is_answered_and_the_rest_still_works, tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py::test_a_lone_surrogate_anywhere_in_a_request_is_answered, tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py::test_a_run_of_digits_meets_the_limit_only_when_it_passes_it
  - tests (read from the run): 12 failed, 1 passed in 3.05s
  ```text
      |     assert answer.crash is None, (
      | AssertionError: a run of 4301 digits as the body came back as ValueError: Exceeds the limit (4300 digits) for integer string conversion: value has 4301 digits; use sys.set_int_max_str_digits() to increase the limit. An exception is not an answer: the client reads nothing on standard output and cannot tell whether its request or the tool was at fault.
      | assert ValueError('Exceeds the limit (4300 digits) for integer string conversion: value has 4301 digits; use sys.set_int_max_str_digits() to increase the limit') is None
      |  +  where ValueError('Exceeds the limit (4300 digits) for integer string conversion: value has 4301 digits; use sys.set_int_max_str_digits() to increase the limit') = Answer(exit_code=-1, stdout='', crash=ValueError('Exceeds the limit (4300 digits) for integer string conversion: value has 4301 digits; use sys.set_int_max_str_digits() to increase the limit')).crash
      | Failing test case: test_a_run_of_digits_meets_the_limit_only_when_it_passes_it(
      |     length=4301,
      |     shape='the body',  # or any other generated value
      | )
      | Explanation:
      |     These lines were always and only run by failing test cases:
      |         /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-r2/red-tree/src/prova/service.py:103
      +---------------- 2 ----------------
      | Traceback (most recent call last):
      |   File "/Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-r2/red-tree/tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py", line 312, in test_a_run_of_digits_meets_the_limit_only_when_it_passes_it
      |     assert _names_the_limit(response), (
      | AssertionError: a run of 1001 digits as the body was answered {'operation': 'check', 'status': 'completed', 'claim': {'kind': 'static_check', 'scope': 'this input'}, 'source_digest': '862c8bc8f1b5c167b9bb4af8acaced7ad217d1c3147ea3cb3355bf084e10b8eb', 'diagnostics': [], 'contract_report': {'functions': [{'function': 'big', 'precondition': 'omitted', 'postcondit, which does not name the 1000-digit limit. A caller that must shorten its number is told the length this tool reads.
      | assert False
      |  +  where False = _names_the_limit({'operation': 'check', 'status': 'completed', 'claim': {'kind': 'static_check', 'scope': 'this input'}, 'source_digest': '862c8bc8f1b5c167b9bb4af8acaced7ad217d1c3147ea3cb3355bf084e10b8eb', ...})
      | Failing test case: test_a_run_of_digits_meets_the_limit_only_when_it_passes_it(
      |     length=1001,
      |     shape='the body',  # or any other generated value
      | )
      | Explanation:
      |     These lines were always and only run by failing test cases:
      |         /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-r2/red-tree/tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py:312
      +------------------------------------
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_every_operation_that_reads_source_refuses_a_lone_surrogate_in_it
  FAILED tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_the_refusal_says_where_the_character_that_cannot_be_written_stands
  FAILED tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_an_argument_that_cannot_be_written_as_utf8_names_that_argument
  FAILED tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_a_request_whose_function_cannot_be_written_as_utf8_names_the_function
  FAILED tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py::test_a_source_large_enough_to_be_sized_still_answers_when_it_holds_one
  FAILED tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py::test_a_literal_past_the_limit_is_refused_and_one_at_the_limit_is_kept_exact
  FAILED tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py::test_every_operation_that_reads_source_refuses_the_same_literal
  FAILED tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py::test_a_literal_too_long_in_an_argument_is_refused_where_it_stands
  FAILED tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py::test_the_manifest_says_how_long_a_literal_this_tool_reads
  FAILED tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py::test_every_request_of_the_two_families_is_answered_and_the_rest_still_works
  FAILED tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py::test_a_lone_surrogate_anywhere_in_a_request_is_answered
  FAILED tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py::test_a_run_of_digits_meets_the_limit_only_when_it_passes_it
  12 failed, 1 passed in 3.05s
  ```

## 2. craft: Craft the change (revision 1)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 162.915s
  - tests (read from the run): 1254 passed in 162.76s
  - slowest: 7.96s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 5.41s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 4.68s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.92s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 3.58s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 3.24s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 2.29s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.95s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.82s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.62s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  5%]
  ........................................................................ [ 11%]
  ........................................................................ [ 17%]
  ........................................................................ [ 22%]
  ........................................................................ [ 28%]
  ........................................................................ [ 34%]
  ........................................................................ [ 40%]
  ........................................................................ [ 45%]
  ........................................................................ [ 51%]
  ........................................................................ [ 57%]
  ........................................................................ [ 63%]
  ........................................................................ [ 68%]
  ........................................................................ [ 74%]
  ........................................................................ [ 80%]
  ........................................................................ [ 86%]
  ........................................................................ [ 91%]
  ........................................................................ [ 97%]
  ..............................                                           [100%]
  ============================= slowest 10 durations =============================
  7.96s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  5.41s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  4.68s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.92s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  3.58s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  3.24s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  2.29s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.95s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.82s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.62s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1254 passed in 162.76s (0:02:42)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.138s
- **typesafe**: unavailable: the client exited 3 because TYPESAFE_API_KEY is absent from this environment; the 3 questions it would have carried (the category for an over-long literal, the one place the UTF-8 rule is enforced, and whether an arguments element follows the same rule) were decided locally and recorded as S23, DEC2 and DEC3
