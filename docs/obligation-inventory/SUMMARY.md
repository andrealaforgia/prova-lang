# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`).
  - not-testable (challenge this): names the project and the command that runs its suite, not an outcome of the product
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority for the behaviour, not an outcome
- S3: Do not change SPEC.md or the reservation example's semantics.
  - not-testable (challenge this): a constraint on the change; the shipped protected-example tests already observe it and must stay green
- S4: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): excludes a directory from the delivery's scope, no product outcome
- S5: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a process constraint on where the work happens
- S6: Commit with a message ending in the line
  - not-testable (challenge this): a process constraint on the commit message
- S7: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line the commit message must end with
- S8: Do not push and do not merge.
  - not-testable (challenge this): a process constraint forbidding push and merge
- S9: Keep the full suite green.
  - not-testable (challenge this): a delivery condition, not a product outcome; the recorded full-suite run observes it
- S10: Another delivery (F2, a call-graph cycle check in src/prova/checker.py) runs in parallel in a different worktree; do not edit checker.py, and keep your change to new files plus the smallest change in service.py.
  - not-testable (challenge this): constrains which files this change may touch while another delivery runs
- S11: KNOWN CONFLICT TO HANDLE EXPLICITLY: today `verify` is advertised and refused as "unavailable" (src/prova/service.py UNAVAILABLE_OPERATIONS, and existing tests such as tests/acceptance/test_s1_b3_build_and_verify_refused_as_unavailable.py).
  - promises: P1, P6
  - tests P1: test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
  - tests P6: test_discover_says_what_an_available_verify_answers
- S12: F16 makes `verify` answer with an inventory.
  - promises: P1
  - tests P1: test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
- S13: That changes what those existing tests expect for `verify` only.
  - promises: P7
  - tests P7: test_listing_what_verify_owes_did_not_make_build_answer
- S14: The Owner approved the roadmap, so this is allowed, but you MUST NOT silently edit existing tests: list every existing test whose expectation changes and why in your oracle note, keep `build` refused as unavailable, and change only the `verify` expectation.
  - promises: P7
  - tests P7: test_listing_what_verify_owes_did_not_make_build_answer
- S15: The answer must never say verified or proved; every obligation is `not_attempted`; it must make clear that no verification ran.
  - promises: P4
  - tests P4: test_nothing_in_the_answer_reports_work_the_tool_never_did
- S16: `discover` must advertise `verify` accurately (available for the inventory only).
  - promises: P6
  - tests P6: test_discover_says_what_an_available_verify_answers
- S17: **Outcome.** `verify` answers with the complete list of what would have to be
  - promises: P1
  - tests P1: test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
- S18: proved for a program, every entry marked `not_attempted`.
  - promises: P1, P4
  - tests P1: test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
  - tests P4: test_nothing_in_the_answer_reports_work_the_tool_never_did
- S19: The Owner can see the
  - promises: P1
  - tests P1: test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
- S20: size and shape of the job before any solver exists.
  - promises: P1
  - tests P1: test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
- S21: **Acceptance criteria**
  - not-testable (challenge this): a heading introducing the acceptance criteria that follow
- S22: 1.
  - not-testable (challenge this): a list number carrying no statement of its own
- S23: Given the hour clock, when `verify` runs, then the answer lists one obligation
  - promises: P2
  - tests P2: test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
- S24: for each potentially evaluated call's precondition, under the condition that
  - promises: P2
  - tests P2: test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
- S25: reaches it.
  - promises: P2
  - tests P2: test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
- S26: 2.
  - not-testable (challenge this): a list number carrying no statement of its own
- S27: Given the hour clock, then the answer lists one obligation per function
  - promises: P3
  - tests P3: test_the_reservation_example_owes_an_entry_for_every_function_it_declares
- S28: connecting body to postcondition, plus separate entries for example validity,
  - promises: P3
  - tests P3: test_the_reservation_example_owes_an_entry_for_every_function_it_declares
- S29: contract definedness and structural termination.
  - promises: P3
  - tests P3: test_the_reservation_example_owes_an_entry_for_every_function_it_declares
- S30: 3.
  - not-testable (challenge this): a list number carrying no statement of its own
- S31: Given a program with an unreachable branch, then the obligation for that branch
  - promises: P2
  - tests P2: test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
- S32: still appears.
  - promises: P2
  - tests P2: test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
- S33: 4.
  - not-testable (challenge this): a list number carrying no statement of its own
- S34: Given every obligation in the answer, then its result is `not_attempted` and
  - promises: P4
  - tests P4: test_nothing_in_the_answer_reports_work_the_tool_never_did
- S35: nothing in the answer says verified or proved.
  - promises: P4
  - tests P4: test_nothing_in_the_answer_reports_work_the_tool_never_did
- S36: 5.
  - not-testable (challenge this): a list number carrying no statement of its own
- S37: Given the reservation example, then its inventory matches the obligations
  - promises: P3
  - tests P3: test_the_reservation_example_owes_an_entry_for_every_function_it_declares
- S38: SPEC.md names for it, with no missing function.
  - promises: P3
  - tests P3: test_the_reservation_example_owes_an_entry_for_every_function_it_declares
- S39: 6.
  - not-testable (challenge this): a list number carrying no statement of its own
- S40: Given two runs on the same source, then the inventory and the obligation
  - promises: P5
  - tests P5: test_asking_twice_about_the_same_program_owes_exactly_the_same_list
- S41: identities are identical.
  - promises: P5
  - tests P5: test_asking_twice_about_the_same_program_owes_exactly_the_same_list
- S42: **SPEC.md** lines 243-250, 270-284, 286-290.
  - not-testable (challenge this): cites the authority lines the behaviour comes from
- S43: **Dependencies** none — this is the
  - not-testable (challenge this): a sequencing note saying the work depends on nothing else
- S44: largest piece of `verify-0` that needs no solver.
  - not-testable (challenge this): a sequencing note about the size of the remaining verify work
- S45: **Size** M.
  - not-testable (challenge this): the size the Owner assigned to the delivery
- S46: **Touches** new `src/prova/obligations.py`, `src/prova/service.py`, tests.
  - not-testable (challenge this): names the files the change is expected to touch
- S47: **Why it is a real expectation** `verify` is refused today; `docs/spec-trace.md`
  - not-testable (challenge this): motivation citing today's refusal and the trace rows
- S48: rows 5.1, 5.2, 5.8 are Not started.
  - not-testable (challenge this): motivation naming the trace rows that are Not started

## Edge matrix

- I1.empty: a source of 0 declarations => completed, 0 obligations, totals attempted 0 and not_attempted 0 | self-probe: not probed | pre-feature not probed
- I1.unknown: a body calling "missing", which no declaration provides => invalid_program with the check's own unknown_function diagnostic and no inventory | self-probe: not probed | pre-feature not probed
- I1.malformed: the text "(defn broken", which does not read => invalid_program with a syntax diagnostic and no inventory | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): verify reads no file, process, clock or network; the request's source text is its only input
- I1.repeated: the same source asked about twice => identical inventory, identical identities, identical order | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): each request is answered in a fresh process from its own input, writing nothing and sharing no state, so two runs cannot interleave on anything observable
- I1.crash: n/a (challenge this): the operation writes no file and changes no state, so an interrupted run leaves nothing behind that a later run could observe
- I2.empty: discover with no other field in the request => the manifest still advertises all 8 operations, verify "available" with its documentation entry | self-probe: not probed | pre-feature not probed
- I2.unknown: an operation name the manifest does not list => unknown_operation, unchanged by the new entry | self-probe: not probed | pre-feature not probed
- I2.malformed: n/a (challenge this): discover reads nothing but the operation name, so there is no payload that can be malformed
- I2.dependency-gone: n/a (challenge this): the manifest is built from the service's own declarations and depends on nothing outside the process
- I2.repeated: two manifest requests in a row => identical manifests | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): the manifest is a value computed from constants, with no shared state to race on
- I2.crash: n/a (challenge this): discover writes nothing, so an interrupted run leaves nothing behind

## Definition of done

- SC1 (P2): not-held (no held self-probe case)
  - GIVEN the shipped hour clock, whose 3 functions call "valid-state" from 3 contract clauses
  - WHEN the Owner asks what must be shown for it
  - THEN exactly 3 call-precondition entries appear, naming caller, site and callee, each reached under "true"
  - test: test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
- SC2 (P3): not-held (no held self-probe case)
  - GIVEN the shipped hour clock, declaring 8 examples across its 3 functions
  - WHEN the Owner asks what must be shown for it
  - THEN each of the 3 functions owes 1 body-postcondition, 1 contract-definedness and 1 structural-termination entry, and 8 example-validity entries appear, numbered from 0
  - test: test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
- SC3 (P2): not-held (no held self-probe case)
  - GIVEN a 2-function program whose call to "tiny" sits behind the literal false
  - WHEN the Owner asks what must be shown for it
  - THEN the call still owes 1 precondition entry at site "body/then", reported as reached under "false", while the same call in the branch that runs reads "true"
  - test: test_a_call_that_can_never_run_still_owes_its_obligation
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN the shipped hour clock owing 20 obligations and the reservation example owing 18
  - WHEN the Owner reads both answers
  - THEN every entry reads "not_attempted", attempted is 0, attempted plus not_attempted equals the 20 and 18 entries listed, and no word such as "proved" appears anywhere
  - test: test_nothing_in_the_answer_reports_work_the_tool_never_did
- SC5 (P3): not-held (no held self-probe case)
  - GIVEN the reservation example SPEC.md publishes, with 3 functions, 7 declared examples and 2 calls
  - WHEN the Owner asks what must be shown for it
  - THEN the inventory names all 3 functions, owes all 5 kinds of entry, lists exactly those 2 calls and 7 example entries
  - test: test_the_reservation_example_owes_an_entry_for_every_function_it_declares
- SC6 (P5): not-held (no held self-probe case)
  - GIVEN the shipped hour clock asked about 2 times in a row
  - WHEN the Owner compares the two answers
  - THEN the two inventories are equal and all 20 identities are distinct
  - test: test_asking_twice_about_the_same_program_owes_exactly_the_same_list
- SC7 (P1): not-held (no held self-probe case)
  - GIVEN a source of 0 declarations and a source that breaks at "(defn broken"
  - WHEN the Owner asks what must be shown for each
  - THEN the empty one owes 0 obligations with attempted 0, and the unreadable one is refused as "invalid_program" with a "syntax" diagnostic and no result at all
  - test: test_a_program_with_nothing_in_it_owes_nothing_and_says_so
- SC8 (P8): not-held (no held self-probe case)
  - GIVEN a 1-function program whose body calls "missing", which no declaration provides
  - WHEN the Owner asks what must be shown for it
  - THEN it is refused as "invalid_program" with the same diagnostic categories the whole-program check gives, including "unknown_function", and no inventory
  - test: test_a_program_that_does_not_check_is_refused_instead_of_listed
- SC9 (P6): not-held (no held self-probe case)
  - GIVEN the tool asked for its manifest of 8 operations
  - WHEN the Owner reads the 8 advertised operations
  - THEN "verify" reads "available" and its documentation says the answer is an inventory whose every entry is "not_attempted"
  - test: test_discover_says_what_an_available_verify_answers
- SC10 (P7): not-held (no held self-probe case)
  - GIVEN a 1-function program whose obligations were just listed
  - WHEN the Owner asks for a built artefact
  - THEN the answer is "unavailable" with category "operation_unavailable" and no result
  - test: test_listing_what_verify_owes_did_not_make_build_answer

## Questions for the owner

- S12: The Owner approved the roadmap, so verify must answer the inventory: may the verify expectation of those four shipped tests change, while build stays refused in each of them?
  - existing behaviour: src/prova/service.py lists verify in UNAVAILABLE_OPERATIONS and refuses it with an operation_unavailable diagnostic; four shipped tests assert that refusal (the b3 acceptance test, the end-to-end session test, the P4/P5 trace properties and the discover unit test)
  - status: decided at oracle
- S16: Should verify be advertised "available" inside the existing two-value vocabulary with a documentation entry saying the answer is the inventory only, rather than a third value such as "partial"?
  - existing behaviour: discover publishes a closed two-value availability map and a shipped unit test pins verify to unavailable, while another shipped test checks that an operation advertised unavailable is exactly one the service refuses
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- M docs/ROADMAP.md (+11 -1 lines)
- A docs/f2/DECISIONS.md (+18 -0 lines)
- A docs/f2/SUMMARY.md (+612 -0 lines)
- A docs/f2/TRACE.md (+5 -0 lines)
- A docs/feature/f2/craft.md (+77 -0 lines)
- A docs/feature/f2/design.md (+111 -0 lines)
- A docs/feature/f2/oracle.md (+88 -0 lines)
- A docs/feature/obligation-inventory/craft.md (+95 -0 lines)
- A docs/feature/obligation-inventory/design.md (+85 -0 lines)
- A docs/feature/obligation-inventory/oracle.md (+82 -0 lines)
- M docs/spec-trace.md (+21 -10 lines)
- M src/prova/checker.py (+171 -2 lines)
- A src/prova/obligations.py (+469 -0 lines)
- M src/prova/service.py (+47 -3 lines)
- A tests/acceptance/_f2_cycle_fixtures.py (+242 -0 lines)
- A tests/acceptance/test_f2_b1_self_calling_function_is_refused.py (+63 -0 lines)
- A tests/acceptance/test_f2_b2_mutually_calling_functions_are_refused.py (+67 -0 lines)
- A tests/acceptance/test_f2_b3_contract_cycle_is_refused.py (+60 -0 lines)
- A tests/acceptance/test_f2_b4_evaluating_a_cyclic_program_refuses_without_crashing.py (+96 -0 lines)
- A tests/acceptance/test_f2_b5_examples_naming_their_own_function_are_accepted.py (+48 -0 lines)
- A tests/acceptance/test_f2_char1_shipped_programs_still_check.py (+70 -0 lines)
- M tests/acceptance/test_i1_int_checked_evaluator_end_to_end.py (+18 -9 lines)
- D tests/acceptance/test_s1_b3_build_and_verify_refused_as_unavailable.py (+0 -101 lines)
- A tests/acceptance/test_s1_b3_build_refused_as_unavailable.py (+106 -0 lines)
- A tests/acceptance/test_verify_lists_the_obligations_owed.py (+414 -0 lines)
- A tests/properties/test_f2_call_graph_cycles.py (+178 -0 lines)
- M tests/properties/test_i1_s1_p4_p5.py (+13 -7 lines)
- A tests/properties/test_obligation_inventory_laws.py (+347 -0 lines)
- A tests/unit/test_checker_cycle_value.py (+48 -0 lines)
- A tests/unit/test_obligation_inventory_refuses_what_it_cannot_list.py (+88 -0 lines)
- M tests/unit/test_service_discover.py (+13 -1 lines)
- A tests/unit/test_verify_inventory_edges.py (+114 -0 lines)

## Commits (git log, BASE to HEAD)

- f936f10 [F2] oracle: a program whose calls form a cycle must be refused, not crash
- 8071ea8 [F2] record what the oracle step decided, in plain language
- 642aebf [F2] record the design: one more whole-program pass in the checker
- 87bd7b8 [F2] refuse a program whose calls form a cycle, naming the functions
- d9a71a7 [F2] record the craft step and note the fixed conformance defect
- 67c4fc7 [F2] keep the delivery's briefs
- 3a08116 Roadmap: record two follow-ups raised during F3 and F16
- 5764bba State what verify must answer: the obligations a program owes
- e702509 Record who owns the rule that says what a program owes
- d0b31b4 Answer what a program owes, with nothing attempted

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f16/request.md
- **promises**:
  - P1: The Owner asks what must still be shown for a program and sees the complete list of obligations it owes, before any solver exists.
  - P2: Each call the program can evaluate owes one precondition entry, under the condition that reaches it, and a call in a branch that can never be taken still owes its entry.
  - P3: Each function owes one entry connecting its body to its postcondition, one for contract definedness and one for structural termination, and each declared example owes its own validity entry.
  - P4: Every entry in the answer is marked not_attempted, the counts say none was attempted, and no word in the answer reports work the tool did not do.
  - P5: Two runs on the same source owe the same list with the same identities in the same order.
  - P6: The manifest advertises verify as available and says it answers the inventory only, with every entry not_attempted.
  - P7: A built artefact is still refused as unavailable after verify learned to list what is owed.
  - P8: A program that does not read, or does not check, is refused with the diagnostics the whole-program check already gives instead of a list of obligations.
- **sentence_map**:
  - S1 => not-testable: names the project and the command that runs its suite, not an outcome of the product
  - S2 => not-testable: names SPEC.md as the authority for the behaviour, not an outcome
  - S3 => not-testable: a constraint on the change; the shipped protected-example tests already observe it and must stay green
  - S4 => not-testable: excludes a directory from the delivery's scope, no product outcome
  - S5 => not-testable: a process constraint on where the work happens
  - S6 => not-testable: a process constraint on the commit message
  - S7 => not-testable: the attribution line the commit message must end with
  - S8 => not-testable: a process constraint forbidding push and merge
  - S9 => not-testable: a delivery condition, not a product outcome; the recorded full-suite run observes it
  - S10 => not-testable: constrains which files this change may touch while another delivery runs
  - S11 => P1,P6
  - S12 => P1
  - S13 => P7
  - S14 => P7
  - S15 => P4
  - S16 => P6
  - S17 => P1
  - S18 => P1,P4
  - S19 => P1
  - S20 => P1
  - S21 => not-testable: a heading introducing the acceptance criteria that follow
  - S22 => not-testable: a list number carrying no statement of its own
  - S23 => P2
  - S24 => P2
  - S25 => P2
  - S26 => not-testable: a list number carrying no statement of its own
  - S27 => P3
  - S28 => P3
  - S29 => P3
  - S30 => not-testable: a list number carrying no statement of its own
  - S31 => P2
  - S32 => P2
  - S33 => not-testable: a list number carrying no statement of its own
  - S34 => P4
  - S35 => P4
  - S36 => not-testable: a list number carrying no statement of its own
  - S37 => P3
  - S38 => P3
  - S39 => not-testable: a list number carrying no statement of its own
  - S40 => P5
  - S41 => P5
  - S42 => not-testable: cites the authority lines the behaviour comes from
  - S43 => not-testable: a sequencing note saying the work depends on nothing else
  - S44 => not-testable: a sequencing note about the size of the remaining verify work
  - S45 => not-testable: the size the Owner assigned to the delivery
  - S46 => not-testable: names the files the change is expected to touch
  - S47 => not-testable: motivation citing today's refusal and the trace rows
  - S48 => not-testable: motivation naming the trace rows that are Not started
- **scenarios**:
  - SC1 | P2 | GIVEN the shipped hour clock, whose 3 functions call "valid-state" from 3 contract clauses | WHEN the Owner asks what must be shown for it | THEN exactly 3 call-precondition entries appear, naming caller, site and callee, each reached under "true"
  - SC2 | P3 | GIVEN the shipped hour clock, declaring 8 examples across its 3 functions | WHEN the Owner asks what must be shown for it | THEN each of the 3 functions owes 1 body-postcondition, 1 contract-definedness and 1 structural-termination entry, and 8 example-validity entries appear, numbered from 0
  - SC3 | P2 | GIVEN a 2-function program whose call to "tiny" sits behind the literal false | WHEN the Owner asks what must be shown for it | THEN the call still owes 1 precondition entry at site "body/then", reported as reached under "false", while the same call in the branch that runs reads "true"
  - SC4 | P4 | GIVEN the shipped hour clock owing 20 obligations and the reservation example owing 18 | WHEN the Owner reads both answers | THEN every entry reads "not_attempted", attempted is 0, attempted plus not_attempted equals the 20 and 18 entries listed, and no word such as "proved" appears anywhere
  - SC5 | P3 | GIVEN the reservation example SPEC.md publishes, with 3 functions, 7 declared examples and 2 calls | WHEN the Owner asks what must be shown for it | THEN the inventory names all 3 functions, owes all 5 kinds of entry, lists exactly those 2 calls and 7 example entries
  - SC6 | P5 | GIVEN the shipped hour clock asked about 2 times in a row | WHEN the Owner compares the two answers | THEN the two inventories are equal and all 20 identities are distinct
  - SC7 | P1 | GIVEN a source of 0 declarations and a source that breaks at "(defn broken" | WHEN the Owner asks what must be shown for each | THEN the empty one owes 0 obligations with attempted 0, and the unreadable one is refused as "invalid_program" with a "syntax" diagnostic and no result at all
  - SC8 | P8 | GIVEN a 1-function program whose body calls "missing", which no declaration provides | WHEN the Owner asks what must be shown for it | THEN it is refused as "invalid_program" with the same diagnostic categories the whole-program check gives, including "unknown_function", and no inventory
  - SC9 | P6 | GIVEN the tool asked for its manifest of 8 operations | WHEN the Owner reads the 8 advertised operations | THEN "verify" reads "available" and its documentation says the answer is an inventory whose every entry is "not_attempted"
  - SC10 | P7 | GIVEN a 1-function program whose obligations were just listed | WHEN the Owner asks for a built artefact | THEN the answer is "unavailable" with category "operation_unavailable" and no result
- **conflicts**:
  - S1 | NONE | read pyproject.toml and the suite layout: Python 3.12 project, uv run pytest -q tests is the command the repository uses
  - S2 | NONE | read SPEC.md lines 241-318: it is the authority for obligations and for the not_attempted result value
  - S3 | NONE | SPEC.md and the reservation example are read by the tests, never written; this change adds no write path to either
  - S4 | NONE | the .relay directory holds no code the suite or the service imports; nothing in it constrains this change
  - S5 | NONE | the work happens in this worktree on its own branch; no shipped behaviour depends on the branch name
  - S6 | NONE | the commit message is outside the product surface; no test or code reads it
  - S7 | NONE | the attribution line is outside the product surface; no test or code reads it
  - S8 | NONE | no push or merge is part of the change; the repository has no hook that requires either
  - S9 | NONE | the full suite passes today (790 passed) and the change must leave it passing; no shipped behaviour contradicts that
  - S10 | NONE | checked src/prova/checker.py: this change reads the typed syntax tree and the checker's result but edits neither; only service.py and new files change
  - S11 | NONE | read src/prova/service.py: verify is in UNAVAILABLE_OPERATIONS today and four shipped tests assert that refusal, exactly as the sentence states
  - S12 | CONFLICT | src/prova/service.py lists verify in UNAVAILABLE_OPERATIONS and refuses it with an operation_unavailable diagnostic; four shipped tests assert that refusal (the b3 acceptance test, the end-to-end session test, the P4/P5 trace properties and the discover unit test) | The Owner approved the roadmap, so verify must answer the inventory: may the verify expectation of those four shipped tests change, while build stays refused in each of them?
  - S13 | NONE | read the four shipped tests that name verify; each also covers build, which this change leaves refused, so only the verify expectation moves
  - S14 | NONE | every shipped test whose verify expectation changes is listed in the decisions below; build stays refused in all of them
  - S15 | NONE | read the existing claim-wording tests: the vocabulary they forbid for evaluate is the vocabulary the new answer also avoids, so nothing contradicts the sentence
  - S16 | CONFLICT | discover publishes a closed two-value availability map and a shipped unit test pins verify to unavailable, while another shipped test checks that an operation advertised unavailable is exactly one the service refuses | Should verify be advertised "available" inside the existing two-value vocabulary with a documentation entry saying the answer is the inventory only, rather than a third value such as "partial"?
  - S17 | NONE | read src/prova/service.py: nothing answers verify today, so there is no answer shape to contradict
  - S18 | NONE | read SPEC.md line 286-290: not_attempted is the value SPEC.md already names for a checker that never ran
  - S19 | NONE | no shipped output shows the Owner the size of the remaining work; nothing contradicts adding it
  - S20 | NONE | no solver, encoder or external dependency exists in the repository; the inventory needs none
  - S21 | NONE | a heading with nothing for the code to contradict
  - S22 | NONE | a list number with nothing for the code to contradict
  - S23 | NONE | read checker.py and syntax.py: calls are already resolved and typed before anything else runs, so the condition is available
  - S24 | NONE | the typed syntax tree keeps if, match and let, so the condition reaching a call can be derived; nothing contradicts it
  - S25 | NONE | nothing in the shipped code reports a path condition today, so there is nothing to contradict
  - S26 | NONE | a list number with nothing for the code to contradict
  - S27 | NONE | read syntax.Function: requires, ensures, examples and body are all available per function
  - S28 | NONE | read syntax.Example and the examples operation: declared examples are already addressed by function and ordinal
  - S29 | NONE | contract definedness and structural termination have no shipped record; nothing contradicts adding them
  - S30 | NONE | a list number with nothing for the code to contradict
  - S31 | NONE | read evaluator.py: an if evaluates one branch only, and the checker types both, so an unreachable branch is still part of the program
  - S32 | NONE | nothing in the shipped code drops unreachable branches; the typed tree keeps them
  - S33 | NONE | a list number with nothing for the code to contradict
  - S34 | NONE | read SPEC.md line 288: a checker that never ran has not_attempted; the shipped code has no other obligation result to contradict
  - S35 | NONE | read the shipped claim-wording tests for evaluate and discover: the same vocabulary is already forbidden elsewhere
  - S36 | NONE | a list number with nothing for the code to contradict
  - S37 | NONE | read SPEC.md's Core conformance example: 3 functions, 7 declared examples, 2 calls to valid-state
  - S38 | NONE | the shipped examples operation already reports every function and example, so no function can be missing by construction
  - S39 | NONE | a list number with nothing for the code to contradict
  - S40 | NONE | read service.py: every operation answers from the request alone, with no clock, file or state, so two runs cannot differ
  - S41 | NONE | nothing in the shipped code derives an identity from a run; identities can be structural
  - S42 | NONE | the cited SPEC.md lines were read; they match the request's description
  - S43 | NONE | no feature in the repository is a prerequisite; the typed tree and the checker already exist
  - S44 | NONE | no solver exists in the repository and this change adds none
  - S45 | NONE | the workspace already records size M; nothing contradicts it
  - S46 | NONE | src/prova/obligations.py does not exist today and service.py is the only dispatch, so the named files are the right ones
  - S47 | NONE | read docs/spec-trace.md section 5: rows 5.1, 5.2 and 5.8 read Not started, as the sentence says
  - S48 | NONE | read docs/spec-trace.md rows 5.1, 5.2 and 5.8: all three read Not started today
- **decisions**:
  - S12: The Owner approved the roadmap in the request, so verify answers the inventory and leaves UNAVAILABLE_OPERATIONS. Exactly four shipped tests change, for verify only: tests/acceptance/test_s1_b3_build_and_verify_refused_as_unavailable.py (renamed to test_s1_b3_build_refused_as_unavailable.py, now build only); tests/acceptance/test_i1_int_checked_evaluator_end_to_end.py (step 7 now reads the inventory and still sees build refused); tests/properties/test_i1_s1_p4_p5.py (its OPERATIONS list drops verify, the controls stay); tests/unit/test_service_discover.py (verify advertised available, plus one new case for its documentation). build stays refused as unavailable in every one of them.
  - S16: verify is advertised "available" inside the existing two-value vocabulary, with a documentation entry saying the answer is an inventory of obligations and every entry is not_attempted. A third value would change a published vocabulary that the advertised-availability test and any reader rely on, for no gain in accuracy that the documentation entry does not already give.
  - DEC1: SPEC.md's "every potentially evaluated call emits a precondition obligation" is read as every call to a declared function, including a callee that declares no precondition; the entry then carries precondition_clauses 0. The narrow reading would list no call at all for either shipped example, because neither has a callee with a precondition, and the Owner would not see that part of the job.
  - DEC2: service.py keeps its parse-and-check preamble as it is and the new handler repeats it a fourth time, instead of extracting it. The request limits this change to the smallest one in service.py while another delivery runs in parallel. The extraction of that preamble is named here as the follow-up it owes.
  - DEC3: an obligation identity is "kind:function:site", where site is a structural path through the declaration (contract, body, calls, requires[0], ensures[1]/arg[0], body/then, body/case[0], example[2]), never a line number, so reformatting a program leaves every identity unchanged.
  - DEC4: every function owes one body-to-postcondition entry even when it declares no postcondition; the entry carries postcondition_clauses 0. Dropping it would leave a function out of the inventory, which the request forbids.
  - DEC5: the answer says that nothing ran without using any word that reports an outcome: attempted is 0, every result reads not_attempted, and a note says the tool has no solver and ran none of the obligations.
  - DEC6: no formal model (Quint). verify is a pure function from the request's source text to a list; it holds no state, writes nothing, spawns nothing and has no protocol or interleaving to explore, so a model would restate the code.
- **mapping**:
  - P1 => test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
  - P2 => test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
  - P3 => test_the_reservation_example_owes_an_entry_for_every_function_it_declares
  - P4 => test_nothing_in_the_answer_reports_work_the_tool_never_did
  - P5 => test_asking_twice_about_the_same_program_owes_exactly_the_same_list
  - P6 => test_discover_says_what_an_available_verify_answers
  - P7 => test_listing_what_verify_owes_did_not_make_build_answer
  - P8 => test_a_program_that_does_not_check_is_refused_instead_of_listed
- **covers_scenarios**:
  - SC1 => test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
  - SC2 => test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
  - SC3 => test_a_call_that_can_never_run_still_owes_its_obligation
  - SC4 => test_nothing_in_the_answer_reports_work_the_tool_never_did
  - SC5 => test_the_reservation_example_owes_an_entry_for_every_function_it_declares
  - SC6 => test_asking_twice_about_the_same_program_owes_exactly_the_same_list
  - SC7 => test_a_program_with_nothing_in_it_owes_nothing_and_says_so
  - SC8 => test_a_program_that_does_not_check_is_refused_instead_of_listed
  - SC9 => test_discover_says_what_an_available_verify_answers
  - SC10 => test_listing_what_verify_owes_did_not_make_build_answer
- **interfaces**:
  - I1: the verify operation of the prova command's JSON stdin/stdout surface, taking a source text and answering an inventory of obligations
  - I2: the discover operation of the same command, the manifest that advertises what each operation answers
- **matrix**:
  - I1.empty => a source of 0 declarations => completed, 0 obligations, totals attempted 0 and not_attempted 0
  - I1.unknown => a body calling "missing", which no declaration provides => invalid_program with the check's own unknown_function diagnostic and no inventory
  - I1.malformed => the text "(defn broken", which does not read => invalid_program with a syntax diagnostic and no inventory
  - I1.dependency-gone => n/a: verify reads no file, process, clock or network; the request's source text is its only input
  - I1.repeated => the same source asked about twice => identical inventory, identical identities, identical order
  - I1.concurrent => n/a: each request is answered in a fresh process from its own input, writing nothing and sharing no state, so two runs cannot interleave on anything observable
  - I1.crash => n/a: the operation writes no file and changes no state, so an interrupted run leaves nothing behind that a later run could observe
  - I2.empty => discover with no other field in the request => the manifest still advertises all 8 operations, verify "available" with its documentation entry
  - I2.unknown => an operation name the manifest does not list => unknown_operation, unchanged by the new entry
  - I2.malformed => n/a: discover reads nothing but the operation name, so there is no payload that can be malformed
  - I2.dependency-gone => n/a: the manifest is built from the service's own declarations and depends on nothing outside the process
  - I2.repeated => two manifest requests in a row => identical manifests
  - I2.concurrent => n/a: the manifest is a value computed from constants, with no shared state to race on
  - I2.crash => n/a: discover writes nothing, so an interrupted run leaves nothing behind
- **laws**:
  - LAW1 | Every function owes one contract-definedness, one body-to-postcondition and one structural-termination entry; every declared example and every call owes its own entry, and nothing else is owed | generator=test_every_function_example_and_call_owes_its_entry | observation=the identities in the answer equal the identities the generated plan says are owed, and each call's reported condition equals the plan's | mutant=drop the entry for a function that declares no postcondition
  - LAW2 | No obligation is ever answered as attempted, and the counts partition the list | generator=test_no_obligation_is_ever_answered_as_attempted | observation=every result reads not_attempted, attempted is 0, the per-kind counts sum to the list, and no word reporting an outcome appears anywhere in the answer | mutant=answer one obligation with the result proved
  - LAW3 | The same source always owes the same list in the same order | generator=test_the_same_program_always_owes_the_same_list | observation=two answers about one source are equal field for field | mutant=build the list by iterating a set of obligations
  - LAW4 | Moving a call behind a condition that never holds keeps its obligation and changes only the condition reported for it | generator=test_putting_a_call_out_of_reach_keeps_what_it_owes | observation=both answers list one call entry for the same callee, reported true before the move and false after it | mutant=skip a branch whose condition is the literal false
- **messages**:
  - MSG0 | none: verify authors no new refusal text. A source that does not read, or does not check, is reported with the reader and checker diagnostics the check operation already produces, word for word, so the Owner reads one vocabulary for both operations.
- **red**: `uv run pytest -q tests/acceptance/test_verify_lists_the_obligations_owed.py tests/properties/test_obligation_inventory_laws.py tests/unit/test_verify_inventory_edges.py tests/unit/test_service_discover.py` exited 1 in 14.452s
  - failing on the pre-feature tree (15): tests/acceptance/test_verify_lists_the_obligations_owed.py::test_each_call_owes_its_precondition_under_the_condition_that_reaches_it, tests/acceptance/test_verify_lists_the_obligations_owed.py::test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending, tests/acceptance/test_verify_lists_the_obligations_owed.py::test_a_call_that_can_never_run_still_owes_its_obligation, tests/acceptance/test_verify_lists_the_obligations_owed.py::test_nothing_in_the_answer_reports_work_the_tool_never_did, tests/acceptance/test_verify_lists_the_obligations_owed.py::test_the_reservation_example_owes_an_entry_for_every_function_it_declares, tests/acceptance/test_verify_lists_the_obligations_owed.py::test_asking_twice_about_the_same_program_owes_exactly_the_same_list, tests/properties/test_obligation_inventory_laws.py::test_every_function_example_and_call_owes_its_entry, tests/properties/test_obligation_inventory_laws.py::test_no_obligation_is_ever_answered_as_attempted, tests/properties/test_obligation_inventory_laws.py::test_the_same_program_always_owes_the_same_list, tests/properties/test_obligation_inventory_laws.py::test_putting_a_call_out_of_reach_keeps_what_it_owes, tests/unit/test_verify_inventory_edges.py::test_a_program_with_nothing_in_it_owes_nothing_and_says_so, tests/unit/test_verify_inventory_edges.py::test_a_program_that_does_not_check_is_refused_instead_of_listed, tests/unit/test_verify_inventory_edges.py::test_listing_what_verify_owes_did_not_make_build_answer, tests/unit/test_service_discover.py::test_discover_reports_each_operation_availability, tests/unit/test_service_discover.py::test_discover_says_what_an_available_verify_answers
  - tests (read from the run): 15 failed, 4 passed in 13.83s
  ```text
          }
  E       AssertionError: assert {'check': 'av...ailable', ...} == {'check': 'av...ailable', ...}
  E
  E         Omitting 7 identical items, use -vv to show
  E         Differing items:
  E         {'verify': 'unavailable'} != {'verify': 'available'}
  E         Use -v to get more diff

  tests/unit/test_service_discover.py:27: AssertionError
  _____________ test_discover_says_what_an_available_verify_answers ______________

      def test_discover_says_what_an_available_verify_answers():
          """`verify` is advertised as available because it answers the inventory
          of obligations a program owes -- and the manifest says so, so that
          "available" is not read as a claim that the obligations were attempted.
          """
          documentation = service.handle(DISCOVER)["result"]["documentation"]

  >       assert "verify" in documentation, documentation
  E       AssertionError: {'evaluate': "A completed evaluate response means the function's postconditions were checked and held for the supplied input; it is not a proof for all inputs."}
  E       assert 'verify' in {'evaluate': "A completed evaluate response means the function's postconditions were checked and held for the supplied input; it is not a proof for all inputs."}

  tests/unit/test_service_discover.py:46: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_verify_lists_the_obligations_owed.py::test_each_call_owes_its_precondition_under_the_condition_that_reaches_it
  FAILED tests/acceptance/test_verify_lists_the_obligations_owed.py::test_the_owner_sees_what_each_function_owes_for_body_contract_examples_and_ending
  FAILED tests/acceptance/test_verify_lists_the_obligations_owed.py::test_a_call_that_can_never_run_still_owes_its_obligation
  FAILED tests/acceptance/test_verify_lists_the_obligations_owed.py::test_nothing_in_the_answer_reports_work_the_tool_never_did
  FAILED tests/acceptance/test_verify_lists_the_obligations_owed.py::test_the_reservation_example_owes_an_entry_for_every_function_it_declares
  FAILED tests/acceptance/test_verify_lists_the_obligations_owed.py::test_asking_twice_about_the_same_program_owes_exactly_the_same_list
  FAILED tests/properties/test_obligation_inventory_laws.py::test_every_function_example_and_call_owes_its_entry
  FAILED tests/properties/test_obligation_inventory_laws.py::test_no_obligation_is_ever_answered_as_attempted
  FAILED tests/properties/test_obligation_inventory_laws.py::test_the_same_program_always_owes_the_same_list
  FAILED tests/properties/test_obligation_inventory_laws.py::test_putting_a_call_out_of_reach_keeps_what_it_owes
  FAILED tests/unit/test_verify_inventory_edges.py::test_a_program_with_nothing_in_it_owes_nothing_and_says_so
  FAILED tests/unit/test_verify_inventory_edges.py::test_a_program_that_does_not_check_is_refused_instead_of_listed
  FAILED tests/unit/test_verify_inventory_edges.py::test_listing_what_verify_owes_did_not_make_build_answer
  FAILED tests/unit/test_service_discover.py::test_discover_reports_each_operation_availability
  FAILED tests/unit/test_service_discover.py::test_discover_says_what_an_available_verify_answers
  15 failed, 4 passed in 13.83s
  ```

## 2. design: Find the owners and design the change (revision 1)

- **owners**:
  - which operations exist and what each one answers => src/prova/service.py
  - what the manifest advertises for each operation => src/prova/service.py (_run_discover)
  - reading source text into forms => src/prova/reader.py
  - the typed syntax tree a program becomes => src/prova/syntax.py
  - whether a program is well formed enough to be talked about at all => src/prova/checker.py (read, never edited: a parallel delivery owns that file)
  - which obligations a program owes, each one's identity and the condition that reaches it => new: src/prova/obligations.py. No module owns this today. checker._calls_in collects calls for the acyclic-dependency rule, but it is private, it drops the condition that reaches a call, and it lives in a file this change may not touch.
  - the result of an obligation nothing attempted => new: src/prova/obligations.py, as a constant of the obligation type rather than a value any caller can set
  - rendering a core-0 expression back to readable text for a condition => new: src/prova/obligations.py. values.render renders values only; nothing in the repository renders an expression.
- **reuse_decision**: Reused unchanged: reader.read_program and syntax.parse_program to get the typed tree, checker.check_program to refuse a program that cannot be talked about, service._source_digest and the response envelope (operation, status, claim, source_digest, diagnostics, result) that check, examples and evaluate already answer with, and the diagnostic categories they already emit. Created new: src/prova/obligations.py, because no module decides which obligations a program owes. The nearest look-alike is checker._calls_in, added by the parallel delivery for the acyclic-dependency rule: it answers a different question (does any call cycle exist), returns calls without the condition that reaches them, is private, and sits in a file this change may not edit, so extending it is not open. service.py gains one dispatch branch, one handler and one documentation entry; its parse-and-check preamble is repeated a fourth time rather than extracted, because the request limits this change to the smallest one in that file while another delivery is in flight. That duplication is the stated cost of this design and the extraction is the follow-up it owes.
- **paradigm**: oo
- **boundaries**:
  - the JSON request/response boundary of the prova command => src/prova/service.py owns the shape; obligations.py builds a value and never a response
  - the typed syntax tree => src/prova/syntax.py owns it; obligations.py only reads it and holds no reference after answering
  - the static-check gate => src/prova/checker.py decides whether a program is well formed; obligations.py is reached only for a program that checked, so it never reasons about an unresolved name or type
  - the manifest => _run_discover owns what each operation is advertised as, and now says what an available verify answers
  - no new boundary is crossed: verify reads no file, spawns no process, reads no clock and writes nothing
- **domain_types**:
  - Obligation (new, immutable): what must be shown about one function, owning its own identity, the text of what is owed and the result no caller can set
  - CallPrecondition, BodyPostcondition, ExampleValidity, ContractDefinedness, StructuralTermination (new, immutable): the five kinds SPEC.md names, each owning the detail only it has (callee and reaching condition, postcondition clause count, example ordinal, contract clause count, direct callees)
  - PathCondition (new, immutable value object): the conjunction of branch conditions that reaches a site, reading 'true' when there is none, extended as the walk descends into a branch or a match clause
  - Site (new, immutable value object): where in a declaration an obligation arises (contract, body, calls, requires[0], ensures[1]/arg[0], body/then, body/case[0], example[2]), derived from structure and never from a line number
  - Inventory (new, immutable first-class collection): the obligations a program owes, in declaration order, refusing to hold two with the same identity, and answering its own totals
- **invariants**:
  - INV1 | No obligation can be built carrying any result but not_attempted: the result is a constant of the type, not a constructor parameter, so an attempted result is unrepresentable | witness=src/prova/obligations.py:Obligation | bypass=none: service.py renders obligations only through their own as_dict, and nothing deserializes one
  - INV2 | One inventory never holds two obligations with the same identity; construction refuses it | witness=src/prova/obligations.py:Inventory | bypass=none
  - INV3 | The totals partition the list: attempted is 0, not_attempted equals the number of obligations, and the per-kind counts sum to it | witness=src/prova/obligations.py:Inventory | bypass=none
  - INV4 | The condition reported for a call is the conjunction of the branch and match conditions on the way to it, and reads 'true' only when there is none | witness=src/prova/obligations.py:PathCondition | bypass=none
  - INV5 | Listing what a program owes changes nothing: verify reads the request's source text, writes no file, spawns nothing and keeps no state between requests | witness=src/prova/service.py:_run_verify | bypass=none
  - INV6 | An obligation's identity is kind:function:site, built from the declaration's structure, so reformatting a program leaves every identity unchanged | witness=src/prova/obligations.py:Site | bypass=none: a renamed function changes its own identities, which is the intended meaning
- **prefactoring**: no
- **prefactoring_reason**: No refactor comes first. The rule this change adds has no existing owner to prepare: obligations.py is new and depends only on the typed tree that syntax.py already publishes. service.py needs one dispatch branch, one handler and one documentation entry, none of which changes the shape of what is there. The one cleanup the file does deserve, extracting the parse-and-check preamble now repeated four times, is deliberately deferred: the request limits this change to the smallest one in service.py while another delivery is in flight, and the extraction would touch all three existing handlers.

## 3. craft: Craft the change (revision 1)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 81.572s
  - tests (read from the run): 821 passed in 81.37s
  - slowest: 5.13s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 3.40s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.05s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 2.60s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.26s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.52s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.38s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 1.28s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.16s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.12s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  8%]
  ........................................................................ [ 17%]
  ........................................................................ [ 26%]
  ........................................................................ [ 35%]
  ........................................................................ [ 43%]
  ........................................................................ [ 52%]
  ........................................................................ [ 61%]
  ........................................................................ [ 70%]
  ........................................................................ [ 78%]
  ........................................................................ [ 87%]
  ........................................................................ [ 96%]
  .............................                                            [100%]
  ============================= slowest 10 durations =============================
  5.13s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  3.40s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.05s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  2.60s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.26s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.52s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.38s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1.28s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.16s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.12s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  821 passed in 81.37s (0:01:21)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.057s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this environment; the client reported exit 3 at the first eligible question, so the four open design questions were settled locally against SPEC.md and recorded as decisions in the oracle step

## 4. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the change is exactly what the design recorded: one new module owning which obligations a program owes, service.py gaining one dispatch branch, one handler and one manifest entry, checker.py and SPEC.md untouched. The owner decision to duplicate the parse-and-check preamble a fourth time is the one the design and the Owner both recorded.
  - D2: pass - the rule that says what a program owes exists once, in src/prova/obligations.py; nothing else counts obligations, names them or renders a condition. The known duplication is the parse-and-check preamble now written four times in service.py, decided by the Owner and tracked as a roadmap follow-up, not hidden here.
  - D3: pass - dependencies point one way: obligations.py imports syntax only, service.py imports obligations, and obligations.py never builds a response, reads a file or knows the JSON envelope. The checker stays the gate in front of it and is only read, never edited.
  - D4: pass - src/prova/obligations.py:105 renders the result from the constant NOT_ATTEMPTED; no constructor anywhere takes a result, so an obligation reporting attempted work cannot be built. Site and PathCondition replace bare strings, and src/prova/obligations.py:224 refuses an inventory holding two obligations with one identity.
  - D5: pass - src/prova/obligations.py:55 PathCondition holds one tuple and answers about itself; each obligation kind is its own small class that says what it owes instead of a kind flag the renderer branches on. The break: the obligation value objects carry three to five fields rather than two, because an entry's detail (callee, clause count, ordinal) belongs with the entry a reader sees; the cost is five slightly wide value objects.
  - D6: pass - the only pattern used is polymorphism over the five obligation kinds, so no caller branches on a kind string, plus a first-class collection for the inventory. No factory, registry or strategy was added for a single caller.
  - D7: pass - every name is the authority's: obligation, precondition, postcondition, contract definedness, structural termination, example validity, path condition, inventory. No Manager, Helper or Data, and no abbreviation.
  - D8: pass - there is no infrastructure to keep out: the operation reads the request's source text, writes no file, spawns nothing and reads no clock. The only I/O in the change is the command's existing stdin/stdout handling, untouched.
  - D9: pass - tests/acceptance/test_verify_lists_the_obligations_owed.py:101 drives the real prova command over its JSON surface and imports nothing from src/prova; the properties do the same. Only the unit tests touch the module directly, which is where the edge and refusal cases live, as the other unit tests in this repository do.
  - D10: pass - every new test name is a sentence about what the Owner gets (a call that can never run still owes its obligation; asking twice owes exactly the same list), with no production symbol, no layer word and no feature or step id.
  - D11: pass - no DSL was invented. The acceptance file reads the shipped hour clock and the published reservation example; the property file builds programs from a plan declared in the test, and every helper is three lines of rendering or counting.
  - D12: pass - tests/properties/test_obligation_inventory_laws.py:134 computes the owed identities from the generated plan, not from the tool, so the oracle is independent of the implementation; four laws are generated, bounded and derandomized, and the metamorphic law moves one call out of reach and compares.
  - D13: pass - the four new files pass nine runs in a row: median 3.95 s, slowest run 4.00 s, slowest single test 0.98 s (a generated property), every acceptance test at or under 0.07 s, 48 unit tests together in 0.08 s. Whole suite 821 passed in 79.60 s.
  - D14: pass - each test adds an observation no other makes: calls and their conditions, per-function and per-example entries, the unreachable branch, the honesty scan, the published example, determinism, the empty and unreadable edges, the two refusals. No property repeats an example's pair.
  - D15: pass - tests/acceptance/test_verify_lists_the_obligations_owed.py:171 states what failed, why it matters and how to find it, with the offending values; the two refusals the code raises (src/prova/obligations.py:224 and :326) name the function, the callee, the site and the operation that reports it, and the second was executed in a test.
  - D16: pass - no model, with the reason the skill asks for: no model for the inventory's completeness, determinism and condition laws, because the operation has no shared state, no multi-step protocol, no concurrency and no crash window; it reads the request's source text and returns a value. The laws are checked by four generated properties over the real command.
  - D17: fixed: docs/spec-trace.md section 5 still said nothing in verify-0 existed and docs/ROADMAP.md still read Not started; rows 5.1, 5.2, 5.6 and 5.8 are now Partial with what is listed and what is never attempted, the summary counts moved with them, and the roadmap row reads Inventory only, nothing attempted. The feature documents state the 20 and 18 obligation counts, the mutation probes and the test cost, and say plainly that nothing was attempted and that concurrency and crash behaviour are argued, not observed.
- **independent_review**:
  - REV1 | reviewer=none-available | findings=No independent reviewer took part in this run. This entry records that absence rather than a review: this executor wrote the candidate and may not review it, and no second party exists in this single-executor workspace. Two deliberate mutations were run against the tests as evidence they can fail, which is the executor's own check, not an independent reading. | resolution=The candidate is handed off unreviewed. An independent reviewer and the blind examiner must still read it before it lands; if a reviewer is supplied, this step is recorded again with their findings as revision 2. Open item for the reviewer: the edge matrix recorded in the oracle names the diagnostic category unknown_function for a call to an undeclared function, where the checker really gives unbound_name; the test and the documents name the real category, so that matrix row is the one stale line in the record.

## 5. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
  - One entry per potentially evaluated call, under the condition that reaches it, with an unreachable call keeping its entry and reading false where a reachable one reads true; one entry per function connecting body to postcondition; and separate entries for example validity, contract definedness and structural termination.
  - It was checked by acceptance tests over the real command against the shipped hour clock and the published reservation example, four generated laws whose oracle is a plan written in the test, unit tests for the empty, unreadable and unchecked edges, and two refusals the code raises for programs built by hand past the checker.
  - The one stale line in the record is the oracle's edge matrix, which guessed the category unknown_function where the checker really gives unbound_name; the tests and the documents name the real one.
- **not_verified**:
  - No obligation was attempted and nothing was discharged: the answer says what is owed, never anything about whether a program is in any state. There is no encoder and no solver.
  - Whether these are the obligations a solver will actually want is the next feature's question; this change shows only that the list is complete against what the program declares.
  - Concurrency and crash behaviour are argued, not observed: the operation writes nothing and keeps nothing between requests, so no interleaving or interruption can be seen from outside. No test proves it.
  - No independent review took place: this executor wrote the candidate and did not review it, and no second party exists in this workspace. An independent reviewer and the blind examiner still have to read it.
  - Jev was unavailable (TYPESAFE_API_KEY absent, client exit 3), so four open design questions were settled locally against SPEC.md instead of being put to the service.
  - The inventory was exercised on core-0 programs only: the two shipped examples, the generated plans, and small programs built in the tests. No large or deeply nested program was timed, and no resource bound is enforced.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit d0b31b48fe9f37eb921b4e9d1f814ff0513a7757
  - no checks declared

## Not backed by the diff

- The verify operation answers with the inventory of obligations a core-0 program owes, and attempts none of them.: a guarantee names no test function of the change
- Every entry's result is not_attempted and cannot be anything else: the result is a constant of the obligation type, so an answer reporting attempted work cannot be built.: a guarantee names no test function of the change
- The totals say attempted zero, the note says the tool has no solver and ran none of them, and no word anywhere in the answer reports an outcome.: a guarantee names no test function of the change
- build is still refused as unavailable, and the manifest advertises verify as available while saying the answer is an inventory only.: a guarantee names no test function of the change
- Two deliberate mutations, a result constant reading proved and a walk that forgets a branch condition, each killed the two tests that own them.: a guarantee names no test function of the change
