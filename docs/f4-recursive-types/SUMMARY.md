# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 824 tests, all green on main).
  - not-testable (challenge this): a constraint on the delivery, proved by the recorded green run of the whole suite, not by a new test
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names the authority document, states no behaviour of the tool
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on the delivery, proved by the recorded green run of the whole suite, not by a new test
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): an instruction to the executor about conflicts, not a behaviour
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): tells the executor which directory to ignore, no behaviour
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): names the worktree to work in, no behaviour of the tool
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a commit message requirement, nothing a test can observe
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line of the commit message, not behaviour
- S9: Do not push and do not merge.
  - not-testable (challenge this): forbids push and merge, no behaviour of the tool
- S10: Keep the full suite green.
  - not-testable (challenge this): a constraint on the delivery, proved by the recorded green run of the whole suite, not by a new test
- S11: Another delivery (F16: a new obligations module plus a `verify` handler in src/prova/service.py) runs in parallel in a different worktree; keep your service.py change to the smallest possible edit (a category if you need one; reuse an existing category if it fits and say why) and do not touch obligation or verify code.
  - promises: P5
  - tests P5: test_the_manifest_publishes_the_recursive_data_category
- S12: Existing categories already include `cyclic_dependency` (F2) and `duplicate_declaration` (F3); read how F2 and F3 were built in src/prova/checker.py and syntax.py and follow the same structure.
  - promises: P1, P2
  - tests P1: test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
  - tests P2: test_two_records_that_each_hold_the_other_are_refused_naming_both
- S13: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments (an earlier executor created stray files that way); run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell quoting hygiene for the executor, not a behaviour
- S14: **Outcome.** A record or union whose fields lead back to itself is refused, because
  - promises: P1
  - tests P1: test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
- S15: recursive data belongs to a later profile.
  - promises: P3
  - tests P3: test_the_refusal_sends_the_reader_to_a_later_profile
- S16: **Acceptance criteria**
  - not-testable (challenge this): a heading above the criteria, states nothing
- S17: 1.
  - not-testable (challenge this): a list number introducing the first criterion
- S18: Given a record with a field of its own type, when the program is checked, then
  - promises: P1
  - tests P1: test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
- S19: it is invalid and the diagnostic names the cycle.
  - promises: P1, P2
  - tests P1: test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
  - tests P2: test_two_records_that_each_hold_the_other_are_refused_naming_both
- S20: 2.
  - not-testable (challenge this): a list number introducing the second criterion
- S21: Given two records that each hold the other, likewise.
  - promises: P1, P2
  - tests P1: test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
  - tests P2: test_two_records_that_each_hold_the_other_are_refused_naming_both
- S22: 3.
  - not-testable (challenge this): a list number introducing the third criterion
- S23: Given a union whose variant payload closes a cycle, likewise.
  - promises: P1, P2
  - tests P1: test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
  - tests P2: test_two_records_that_each_hold_the_other_are_refused_naming_both
- S24: 4.
  - not-testable (challenge this): a list number introducing the fourth criterion
- S25: Given three types in a chain with no cycle, when the program is checked, then it
  - promises: P4
  - tests P4: test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself
- S26: is accepted.
  - promises: P4
  - tests P4: test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself
- S27: 5.
  - not-testable (challenge this): a list number introducing the fifth criterion
- S28: Given the refusal, then it says recursive data is outside this profile, not that
  - promises: P3
  - tests P3: test_the_refusal_sends_the_reader_to_a_later_profile
- S29: a type is unknown.
  - promises: P3
  - tests P3: test_the_refusal_sends_the_reader_to_a_later_profile
- S30: **SPEC.md** lines 135-136, 51-54 (unsupported must not be misdiagnosed).
  - promises: P3
  - tests P3: test_the_refusal_sends_the_reader_to_a_later_profile
- S31: **Dependencies** none (serial with F3, F5, F7, F8).
  - not-testable (challenge this): a sequencing note about other features, no behaviour
- S32: **Size** S.
  - not-testable (challenge this): declares the delivery size, no behaviour of the tool
- S33: **Touches** `src/prova/checker.py`, tests.
  - not-testable (challenge this): names the files the work touches, no behaviour
- S34: **Why it is a real expectation** probe T2 disagrees today.
  - promises: P1
  - tests P1: test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle

## Edge matrix

- I1.empty: a source with 0 declarations => status "completed" with 0 diagnostics | self-probe: not probed | pre-feature not probed
- I1.unknown: a record field whose declared type Ghost is never declared => 1 unbound_type diagnostic and 0 recursive_type diagnostics | self-probe: not probed | pre-feature not probed
- I1.malformed: an unbalanced (deftype Node (record => 1 syntax diagnostic and status "invalid_program" | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the check reads only the source text of its own request and has no external dependency to lose
- I1.repeated: the same recursive program checked in 2 separate runs => both runs answer identically, no state is kept | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): one process answers one request and shares no state between requests
- I1.crash: a recursive union read by a function that matches on it => exit code 0, 1 JSON refusal, no traceback on standard error | self-probe: not probed | pre-feature not probed
- I2.empty: discover carries no source at all => the manifest lists recursive_type among its categories | self-probe: not probed | pre-feature not probed
- I2.unknown: n/a (challenge this): discover reads no name from the caller that could be unknown to it
- I2.malformed: n/a (challenge this): discover carries no source field that could be malformed
- I2.dependency-gone: n/a (challenge this): the manifest is built from constants inside the process
- I2.repeated: 2 discover requests in 2 runs => both answer the identical manifest | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): discover reads no shared state, so 2 callers cannot interfere
- I2.crash: n/a (challenge this): discover walks no graph and cannot exhaust the stack
- I3.empty: TypeCycle built with 0 members => ValueError naming what was wrong and what to build it from | self-probe: not probed | pre-feature not probed
- I3.unknown: n/a (challenge this): the value holds names the search produced and resolves nothing itself
- I3.malformed: n/a (challenge this): its only field is the tuple of names the dependency search produced
- I3.dependency-gone: n/a (challenge this): a frozen value object with no collaborator to lose
- I3.repeated: 2 values built from the same 2 members => equal values, since it is a frozen dataclass | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): a frozen value cannot change, so 2 readers see the same members
- I3.crash: n/a (challenge this): the constructor does no recursion, no IO and no graph walk

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the program (deftype Node (record (value Int) (next Node))) with 1 record
  - WHEN it is checked through the prova command
  - THEN the status is "invalid_program" with 1 recursive_type diagnostic
  - test: test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN 2 records Invoice and Payment that each declare a field of the type of the other
  - WHEN the program is checked
  - THEN the refusal names Invoice and Payment and its cycle list holds exactly those 2 names
  - test: test_two_records_that_each_hold_the_other_are_refused_naming_both
- SC3 (P1): not-held (no held self-probe case)
  - GIVEN the union (deftype Stack (union (Empty) (Pushed (top Int) (rest Stack))))
  - WHEN the program is checked
  - THEN the status is "invalid_program" with 1 recursive_type diagnostic naming Stack
  - test: test_a_union_whose_variant_payload_closes_a_cycle_is_refused
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN 3 types where Invoice holds a Line and Line holds a Money
  - WHEN the program is checked
  - THEN the status is "completed" and the diagnostics list is empty
  - test: test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself
- SC5 (P3): not-held (no held self-probe case)
  - GIVEN the refused record Node that holds 1 field of its own type
  - WHEN the reason is read
  - THEN it contains "later profile" and "acyclic" and 0 unbound_type diagnostics are reported
  - test: test_the_refusal_sends_the_reader_to_a_later_profile
- SC6 (P5): not-held (no held self-probe case)
  - GIVEN the manifest the tool publishes for the operation "discover"
  - WHEN it is asked for
  - THEN its diagnostic_categories list contains "recursive_type"
  - test: test_the_manifest_publishes_the_recursive_data_category
- SC7 (P1): not-held (no held self-probe case)
  - GIVEN the recursive union Stack read by 1 function whose body matches on it
  - WHEN the program is checked
  - THEN the command exits 0 with 1 JSON refusal and prints no traceback
  - test: test_a_function_that_matches_on_recursive_data_is_refused_not_crashed

## Questions for the owner

- none

## Observed side effects (git, BASE to HEAD)

- M docs/ROADMAP.md (+1 -1 lines)
- A docs/f4-recursive-types/DECISIONS.md (+12 -0 lines)
- A docs/f4-recursive-types/SUMMARY.md (+439 -0 lines)
- A docs/f4-recursive-types/TRACE.md (+5 -0 lines)
- A docs/feature/obligation-inventory/craft.md (+95 -0 lines)
- A docs/feature/obligation-inventory/design.md (+85 -0 lines)
- A docs/feature/obligation-inventory/handoff.md (+42 -0 lines)
- A docs/feature/obligation-inventory/oracle.md (+82 -0 lines)
- A docs/feature/obligation-inventory/selfreview.md (+39 -0 lines)
- A docs/obligation-inventory/DECISIONS.md (+20 -0 lines)
- A docs/obligation-inventory/SUMMARY.md (+603 -0 lines)
- A docs/obligation-inventory/TRACE.md (+5 -0 lines)
- M docs/spec-trace.md (+14 -10 lines)
- M src/prova/checker.py (+116 -26 lines)
- A src/prova/obligations.py (+469 -0 lines)
- M src/prova/service.py (+45 -3 lines)
- A tests/acceptance/_f4_recursive_type_fixtures.py (+187 -0 lines)
- A tests/acceptance/test_f4_b1_a_record_holding_itself_is_refused.py (+39 -0 lines)
- A tests/acceptance/test_f4_b2_two_records_holding_each_other_are_refused.py (+40 -0 lines)
- A tests/acceptance/test_f4_b3_a_union_variant_closing_a_cycle_is_refused.py (+40 -0 lines)
- A tests/acceptance/test_f4_b4_three_types_in_a_chain_are_accepted.py (+34 -0 lines)
- A tests/acceptance/test_f4_b5_the_refusal_says_recursive_data_is_outside_this_profile.py (+74 -0 lines)
- A tests/acceptance/test_f4_b6_a_function_reading_recursive_data_is_refused_without_crashing.py (+43 -0 lines)
- A tests/acceptance/test_f4_b7_the_manifest_publishes_the_new_category.py (+30 -0 lines)
- M tests/acceptance/test_i1_int_checked_evaluator_end_to_end.py (+18 -9 lines)
- D tests/acceptance/test_s1_b3_build_and_verify_refused_as_unavailable.py (+0 -101 lines)
- A tests/acceptance/test_s1_b3_build_refused_as_unavailable.py (+106 -0 lines)
- A tests/acceptance/test_verify_lists_the_obligations_owed.py (+414 -0 lines)
- A tests/properties/test_f4_type_dependency_cycles.py (+143 -0 lines)
- M tests/properties/test_i1_s1_p4_p5.py (+13 -7 lines)
- A tests/properties/test_obligation_inventory_laws.py (+347 -0 lines)
- A tests/unit/test_checker_type_cycle_value.py (+49 -0 lines)
- A tests/unit/test_obligation_inventory_refuses_what_it_cannot_list.py (+88 -0 lines)
- M tests/unit/test_service_discover.py (+13 -1 lines)
- A tests/unit/test_verify_inventory_edges.py (+114 -0 lines)

## Commits (git log, BASE to HEAD)

- 652eec4 State what verify must answer: the obligations a program owes
- a4c2123 Record who owns the rule that says what a program owes
- e1eff8f Answer what a program owes, with nothing attempted
- 6c12e91 Keep the delivery's record beside the change
- 186988f [F4] read a dependency cycle and a type's fields in one place each
- 5df6a20 [F4] refuse data that leads back to itself, naming the types on the cycle
- ac6f43a [F4] keep the delivery's record beside the change

## 3. oracle: Frame the work and write the oracle (revision 2)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f4/request.md
- **promises**:
  - P1: A record or union whose field types lead back to itself is refused as an invalid program.
  - P2: The refusal names every type on the cycle, both in its sentence and in a machine-readable member list.
  - P3: The refusal says recursive data belongs to a later profile and states the acyclicity rule, and never calls a declared type unknown.
  - P4: A program is refused for recursion exactly when a declared type can lead back to itself, so 3 types in a chain stay accepted.
  - P5: The new diagnostic category is published by the discover manifest, and service.py grows by that one name only.
- **sentence_map**:
  - S1 => not-testable: a constraint on the delivery, proved by the recorded green run of the whole suite, not by a new test
  - S2 => not-testable: names the authority document, states no behaviour of the tool
  - S3 => not-testable: a constraint on the delivery, proved by the recorded green run of the whole suite, not by a new test
  - S4 => not-testable: an instruction to the executor about conflicts, not a behaviour
  - S5 => not-testable: tells the executor which directory to ignore, no behaviour
  - S6 => not-testable: names the worktree to work in, no behaviour of the tool
  - S7 => not-testable: a commit message requirement, nothing a test can observe
  - S8 => not-testable: the attribution line of the commit message, not behaviour
  - S9 => not-testable: forbids push and merge, no behaviour of the tool
  - S10 => not-testable: a constraint on the delivery, proved by the recorded green run of the whole suite, not by a new test
  - S11 => P5
  - S12 => P1,P2
  - S13 => not-testable: shell quoting hygiene for the executor, not a behaviour
  - S14 => P1
  - S15 => P3
  - S16 => not-testable: a heading above the criteria, states nothing
  - S17 => not-testable: a list number introducing the first criterion
  - S18 => P1
  - S19 => P1,P2
  - S20 => not-testable: a list number introducing the second criterion
  - S21 => P1,P2
  - S22 => not-testable: a list number introducing the third criterion
  - S23 => P1,P2
  - S24 => not-testable: a list number introducing the fourth criterion
  - S25 => P4
  - S26 => P4
  - S27 => not-testable: a list number introducing the fifth criterion
  - S28 => P3
  - S29 => P3
  - S30 => P3
  - S31 => not-testable: a sequencing note about other features, no behaviour
  - S32 => not-testable: declares the delivery size, no behaviour of the tool
  - S33 => not-testable: names the files the work touches, no behaviour
  - S34 => P1
- **scenarios**:
  - SC1 | P1 | GIVEN the program (deftype Node (record (value Int) (next Node))) with 1 record | WHEN it is checked through the prova command | THEN the status is "invalid_program" with 1 recursive_type diagnostic
  - SC2 | P2 | GIVEN 2 records Invoice and Payment that each declare a field of the type of the other | WHEN the program is checked | THEN the refusal names Invoice and Payment and its cycle list holds exactly those 2 names
  - SC3 | P1 | GIVEN the union (deftype Stack (union (Empty) (Pushed (top Int) (rest Stack)))) | WHEN the program is checked | THEN the status is "invalid_program" with 1 recursive_type diagnostic naming Stack
  - SC4 | P4 | GIVEN 3 types where Invoice holds a Line and Line holds a Money | WHEN the program is checked | THEN the status is "completed" and the diagnostics list is empty
  - SC5 | P3 | GIVEN the refused record Node that holds 1 field of its own type | WHEN the reason is read | THEN it contains "later profile" and "acyclic" and 0 unbound_type diagnostics are reported
  - SC6 | P5 | GIVEN the manifest the tool publishes for the operation "discover" | WHEN it is asked for | THEN its diagnostic_categories list contains "recursive_type"
  - SC7 | P1 | GIVEN the recursive union Stack read by 1 function whose body matches on it | WHEN the program is checked | THEN the command exits 0 with 1 JSON refusal and prints no traceback
- **conflicts**:
  - S1 | NONE | ran the suite command named here on the worktree before any edit; it is green and no test reads a recursive type
  - S2 | NONE | read SPEC.md lines 51-54 and 132-136; they require the rule this feature adds and nothing contradicts it
  - S3 | NONE | scanned every deftype in tests, examples and evidence for a field whose declared type is a user type; only Outcome holds Clock, which is acyclic
  - S4 | NONE | the same scan found no existing test that requires a recursive type to be accepted, so no test conflicts
  - S5 | NONE | the .relay directory was not read and no test in tests reads it
  - S6 | NONE | all edits are inside the worktree on branch feat/f4 and nothing outside it is written
  - S7 | NONE | the commit message convention of the last commits already ends with that attribution line
  - S8 | NONE | the attribution line is copied verbatim from the request into the commit message
  - S9 | NONE | no push and no merge is performed by any step of this delivery
  - S10 | NONE | ran the full suite before the change; the whole run is green and is the baseline for the green step
  - S11 | NONE | read service.py; the categories tuple is a single constant and adding one name touches no verify or obligation code
  - S12 | NONE | read the Cycle value and the duplicate diagnostics in checker.py and syntax.py; the same value-object and category structure carries over to types
  - S13 | NONE | every nwstep argument of this delivery is written in a quoted script file, so no redirection is created
  - S14 | NONE | ran a self-holding record and a recursive union through the checker; both are accepted today, so the refusal contradicts no promise
  - S15 | NONE | SPEC.md lines 135-136 place recursive data in a later profile, which is what the refusal will say
  - S16 | NONE | a heading; nothing in the repository can contradict it
  - S17 | NONE | a list number; nothing in the repository can contradict it
  - S18 | NONE | ran the self-holding record through the check operation; it is accepted today and no test pins that acceptance
  - S19 | NONE | the cycle member list already exists on the response of the F2 refusal, so naming the cycle needs no new response shape
  - S20 | NONE | a list number; nothing in the repository can contradict it
  - S21 | NONE | ran the mutually holding pair through the check operation; it is accepted today and no test pins that acceptance
  - S22 | NONE | a list number; nothing in the repository can contradict it
  - S23 | NONE | ran the recursive union through the check operation; it is accepted today and no test pins that acceptance
  - S24 | NONE | a list number; nothing in the repository can contradict it
  - S25 | NONE | ran a 3-type acyclic chain through the check operation; it is accepted today and must stay accepted
  - S26 | NONE | the shipped example hour-clock.prova has Outcome holding Clock and must keep checking; it is acyclic and stays accepted
  - S27 | NONE | a list number; nothing in the repository can contradict it
  - S28 | NONE | a self-held type is declared, so the unbound_type check never fires on it today; no misdiagnosis exists to preserve
  - S29 | NONE | the unbound_type category keeps its meaning of a type the program never declares, which no new refusal changes
  - S30 | NONE | read both SPEC.md ranges; they are consistent with each other and with the acceptance criteria
  - S31 | NONE | F3 is already committed on this branch and no other delivery writes in this worktree
  - S32 | NONE | the work touches one checker rule, one category name and its tests, which matches size S
  - S33 | NONE | the change needs checker.py, 1 name in service.py and new test files, and syntax.py already carries the field declarations
  - S34 | NONE | probe T2 in docs/spec-trace/probe.py expects the rejection and disagrees today; no test records its current outcome
- **decisions**:
  - DEC1: the refusal gets its own category recursive_type instead of reusing cyclic_dependency, because the subject (declared data types, not functions), the repair (wait for a later profile, not remove a call) and the published F2 law (cyclic_dependency means the call graph) differ, and a consumer filters by category; service.py grows by 1 name, the smallest edit that keeps the two apart.
  - DEC2: when a type cycle is found the function checks do not run, and the refusal says so. Measured on the pre-feature tree: a recursive union read by a match ends in RecursionError, because match coverage and value shape checks follow the fields of a type and are defined only on acyclic types.
  - DEC3: the refusal carries no line and column, mirroring the F2 cycle diagnostic, because a cycle spans several declarations; the machine-readable cycle member list carries the names instead.
  - DEC4: no formal model (Quint) is written: the rule is a pure function of the program text with no state, protocol, concurrency or crash-recovery question in it.
  - DEC5: the owner is absent for this run, so DEC1 to DEC4 are my own decisions, recorded here and in the brief for review.
- **mapping**:
  - P1 => test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
  - P2 => test_two_records_that_each_hold_the_other_are_refused_naming_both
  - P3 => test_the_refusal_sends_the_reader_to_a_later_profile
  - P4 => test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself
  - P5 => test_the_manifest_publishes_the_recursive_data_category
- **covers_scenarios**:
  - SC1 => test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
  - SC2 => test_two_records_that_each_hold_the_other_are_refused_naming_both
  - SC3 => test_a_union_whose_variant_payload_closes_a_cycle_is_refused
  - SC4 => test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself
  - SC5 => test_the_refusal_sends_the_reader_to_a_later_profile
  - SC6 => test_the_manifest_publishes_the_recursive_data_category
  - SC7 => test_a_function_that_matches_on_recursive_data_is_refused_not_crashed
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base held
  - SC5 => base differs
  - SC6 => base differs
  - SC7 => base differs
- **interfaces**:
  - I1: the prova command check operation, reading one JSON request on stdin and answering one JSON response on stdout
  - I2: the prova command discover operation, which publishes the diagnostic categories a caller may receive
  - I3: the checker TypeCycle value, the narrowest surface carrying the rule that a reported cycle names at least one type
- **matrix**:
  - I1.empty => a source with 0 declarations => status "completed" with 0 diagnostics
  - I1.unknown => a record field whose declared type Ghost is never declared => 1 unbound_type diagnostic and 0 recursive_type diagnostics
  - I1.malformed => an unbalanced (deftype Node (record => 1 syntax diagnostic and status "invalid_program"
  - I1.dependency-gone => n/a: the check reads only the source text of its own request and has no external dependency to lose
  - I1.repeated => the same recursive program checked in 2 separate runs => both runs answer identically, no state is kept
  - I1.concurrent => n/a: one process answers one request and shares no state between requests
  - I1.crash => a recursive union read by a function that matches on it => exit code 0, 1 JSON refusal, no traceback on standard error
  - I2.empty => discover carries no source at all => the manifest lists recursive_type among its categories
  - I2.unknown => n/a: discover reads no name from the caller that could be unknown to it
  - I2.malformed => n/a: discover carries no source field that could be malformed
  - I2.dependency-gone => n/a: the manifest is built from constants inside the process
  - I2.repeated => 2 discover requests in 2 runs => both answer the identical manifest
  - I2.concurrent => n/a: discover reads no shared state, so 2 callers cannot interfere
  - I2.crash => n/a: discover walks no graph and cannot exhaust the stack
  - I3.empty => TypeCycle built with 0 members => ValueError naming what was wrong and what to build it from
  - I3.unknown => n/a: the value holds names the search produced and resolves nothing itself
  - I3.malformed => n/a: its only field is the tuple of names the dependency search produced
  - I3.dependency-gone => n/a: a frozen value object with no collaborator to lose
  - I3.repeated => 2 values built from the same 2 members => equal values, since it is a frozen dataclass
  - I3.concurrent => n/a: a frozen value cannot change, so 2 readers see the same members
  - I3.crash => n/a: the constructor does no recursion, no IO and no graph walk
- **laws**:
  - LAW1 | a program is refused with a recursive_type diagnostic exactly when its type-dependency graph has a cycle, and the refusal names exactly the types that lie on one | generator=test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself | observation=the categories and cycle member lists of the check response, against a transitive closure computed from the generator own edge list | mutant=name the type whose field opened the walk instead of the types on the cycle, or accept a cycle of length 3
- **messages**:
  - MSG1 | (deftype Node (record (value Int) (next Node))) | the type Node leads back to itself through the declared types of its fields | core-0 requires the type-dependency graph to be acyclic, so recursive data belongs to a later profile | remove or retype the field that closes the cycle, or keep the type for a profile that supports recursive data | test=test_the_refusal_sends_the_reader_to_a_later_profile
  - MSG2 | a TypeCycle built with no member | a cycle must name at least one type | a refusal with no member would not say which declarations to repair | build it from the types the dependency search found depending on each other | test=test_a_type_cycle_that_names_no_type_is_refused_with_a_reason
- **red**: `uv run pytest -q tests/acceptance/test_f4_b1_a_record_holding_itself_is_refused.py tests/acceptance/test_f4_b2_two_records_holding_each_other_are_refused.py tests/acceptance/test_f4_b3_a_union_variant_closing_a_cycle_is_refused.py tests/acceptance/test_f4_b5_the_refusal_says_recursive_data_is_outside_this_profile.py tests/acceptance/test_f4_b6_a_function_reading_recursive_data_is_refused_without_crashing.py tests/acceptance/test_f4_b7_the_manifest_publishes_the_new_category.py tests/properties/test_f4_type_dependency_cycles.py` exited 1 in 1.732s
  - failing on the pre-feature tree (8): tests/acceptance/test_f4_b1_a_record_holding_itself_is_refused.py::test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle, tests/acceptance/test_f4_b2_two_records_holding_each_other_are_refused.py::test_two_records_that_each_hold_the_other_are_refused_naming_both, tests/acceptance/test_f4_b3_a_union_variant_closing_a_cycle_is_refused.py::test_a_union_whose_variant_payload_closes_a_cycle_is_refused, tests/acceptance/test_f4_b5_the_refusal_says_recursive_data_is_outside_this_profile.py::test_the_refusal_sends_the_reader_to_a_later_profile[a, tests/acceptance/test_f4_b5_the_refusal_says_recursive_data_is_outside_this_profile.py::test_the_refusal_sends_the_reader_to_a_later_profile[two, tests/acceptance/test_f4_b6_a_function_reading_recursive_data_is_refused_without_crashing.py::test_a_function_that_matches_on_recursive_data_is_refused_not_crashed, tests/acceptance/test_f4_b7_the_manifest_publishes_the_new_category.py::test_the_manifest_publishes_the_recursive_data_category, tests/properties/test_f4_type_dependency_cycles.py::test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself
  - tests (read from the run): 9 failed, 6 passed in 1.02s
  ```text
              )
              return

  >       assert response.get("status") == "invalid_program", (
              f"a program in which {sorted(recursive)} lead back to themselves was "
              f"accepted: {response}. Source:\n{source}\nRefuse every program whose "
              "type-dependency graph has a cycle."
          )
  E       AssertionError: a program in which ['Type0'] lead back to themselves was accepted: {'operation': 'check', 'status': 'completed', 'claim': {'kind': 'static_check', 'scope': 'this input'}, 'source_digest': '9b1c9524c1d2beb87e75bc9ea25f97c17e7ffa08efb4e252381f3efec746fb8e', 'diagnostics': []}. Source:
  E         (deftype Type0 (record (count Int) (field0 Type0)))
  E
  E         Refuse every program whose type-dependency graph has a cycle.
  E       assert 'completed' == 'invalid_program'
  E
  E         - invalid_program
  E         + completed
  E       Failing test case: test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself(
  E           program=(
  E               1,
  E               [[True]],
  E               [False],  # or any other generated value
  E           ),
  E       )
  E       Explanation:
  E           These lines were always and only run by failing test cases:
  E               /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f4/red-tree/tests/properties/test_f4_type_dependency_cycles.py:84
  E               /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f4/red-tree/tests/properties/test_f4_type_dependency_cycles.py:126

  tests/properties/test_f4_type_dependency_cycles.py:126: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f4_b1_a_record_holding_itself_is_refused.py::test_a_record_with_a_field_of_its_own_type_is_refused_naming_the_cycle
  FAILED tests/acceptance/test_f4_b2_two_records_holding_each_other_are_refused.py::test_two_records_that_each_hold_the_other_are_refused_naming_both
  FAILED tests/acceptance/test_f4_b3_a_union_variant_closing_a_cycle_is_refused.py::test_a_union_whose_variant_payload_closes_a_cycle_is_refused
  FAILED tests/acceptance/test_f4_b5_the_refusal_says_recursive_data_is_outside_this_profile.py::test_the_refusal_sends_the_reader_to_a_later_profile[a record holding itself-(deftype Node (record (value Int) (next Node)))\n]
  FAILED tests/acceptance/test_f4_b5_the_refusal_says_recursive_data_is_outside_this_profile.py::test_the_refusal_sends_the_reader_to_a_later_profile[a union with a recursive variant-(deftype Stack (union (Empty) (Pushed (top Int) (rest Stack))))\n]
  FAILED tests/acceptance/test_f4_b5_the_refusal_says_recursive_data_is_outside_this_profile.py::test_the_refusal_sends_the_reader_to_a_later_profile[two records holding each other-(deftype Invoice (record (payment Payment) (number Int)))\n\n(deftype Payment (record (invoice Invoice) (cents Int)))\n]
  FAILED tests/acceptance/test_f4_b6_a_function_reading_recursive_data_is_refused_without_crashing.py::test_a_function_that_matches_on_recursive_data_is_refused_not_crashed
  FAILED tests/acceptance/test_f4_b7_the_manifest_publishes_the_new_category.py::test_the_manifest_publishes_the_recursive_data_category
  FAILED tests/properties/test_f4_type_dependency_cycles.py::test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself
  9 failed, 6 passed in 1.02s
  ```

## 4. craft: Craft the change (revision 2)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 85.02s
  - tests (read from the run): 857 passed in 84.88s
  - slowest: 5.37s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 3.49s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.11s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 2.86s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.20s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.55s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.28s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.23s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.18s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 1.15s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  8%]
  ........................................................................ [ 16%]
  ........................................................................ [ 25%]
  ........................................................................ [ 33%]
  ........................................................................ [ 42%]
  ........................................................................ [ 50%]
  ........................................................................ [ 58%]
  ........................................................................ [ 67%]
  ........................................................................ [ 75%]
  ........................................................................ [ 84%]
  ........................................................................ [ 92%]
  .................................................................        [100%]
  ============================= slowest 10 durations =============================
  5.37s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  3.49s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.11s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  2.86s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.20s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.55s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.28s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.23s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.18s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1.15s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  857 passed in 84.88s (0:01:24)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.055s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this environment, so jev_decide.py exits 3; the category and early-refusal choices were decided locally and recorded as DEC1 and DEC2

## 5. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the change follows DEC1 (own category recursive_type), DEC2 (functions not checked when a cycle is found, src/prova/checker.py:203) and DEC3 (members instead of a location)
  - D2: pass - the cycle search has one owner, _cycles_among at src/prova/checker.py:314, used by the function rule and the type rule; the fields of a declared type have one reader, _declared_fields at src/prova/checker.py:421
  - D3: pass - the checker keeps the rule, service.py only publishes the category name at src/prova/service.py:28; no transport or filesystem code entered the checker
  - D4: pass - src/prova/checker.py:105 TypeCycle inherits the constructor that refuses an empty member tuple, so a refusal that names no type cannot be built, and the category is a named constant at src/prova/checker.py:37
  - D5: pass - src/prova/checker.py:110 the kind of a cycle is one class attribute and each subclass carries only its own sentence; DeclarationCycle, Cycle and TypeCycle are each under 25 lines
  - D6: pass - the shared behaviour sits in a small value hierarchy rather than a flag; no pattern was introduced for its own sake
  - D7: pass - the language of the domain is used throughout: declared type, field, variant payload, cycle, profile
  - D8: pass - the checker reads only the parsed program; no IO, no process and no clock was added
  - D9: pass - tests/acceptance/test_f4_b6_a_function_reading_recursive_data_is_refused_without_crashing.py:27 drives the real prova command over JSON on stdin and reads only the response and the exit code; no acceptance test imports src/prova
  - D10: pass - every test name states the behaviour in the words of a reader, for example test_a_function_that_matches_on_recursive_data_is_refused_not_crashed
  - D11: pass - the shapes and the reading helpers live in tests/acceptance/_f4_recursive_type_fixtures.py, and each refused program has an accepted twin beside it
  - D12: pass - tests/properties/test_f4_type_dependency_cycles.py:105 generates every graph over 3 types as records or unions and decides the expected verdict with its own transitive closure at line 71, a different algorithm from the tool
  - D13: pass - the 18 new tests run in 0.60s together; the whole suite is 857 tests in 83.70s, and the slowest tests of the run are recorded by the green command
  - D14: pass - the 3 refused shapes share one assertion helper and the property covers the general law, so no test repeats another
  - D15: pass - tests/acceptance/_f4_recursive_type_fixtures.py:186 says what was wrong, which types were expected and what to repair; the product refusal at src/prova/checker.py:105 names the types, the rule, the later profile and the two repairs
  - D16: n/a: the rule is a pure function of the program text; there is no state, protocol, concurrency or crash recovery for a formal model to carry (DEC4)
  - D17: pass - the module docstring of src/prova/checker.py now states the type rule and its early refusal, and the brief records DEC1 to DEC5 with the measured RecursionError that justifies DEC2
- **independent_review**:
  - REV1 | reviewer=nw-software-crafter-reviewer | findings=A separate read-only reviewer agent, 2026-11-14, APPROVE with no findings on identity ac6f43a. Own probes, about 35 cases: all 5 acceptance criteria pass (self-referencing record, two-record cycle, union-variant cycle, 3-type chain accepted, diamond accepted, tail cycle naming only the nodes on it, a 2000-type cycle and a 2000-type chain with no RecursionError). No existing test modified: only src/prova/checker.py and src/prova/service.py changed. SPEC.md untouched. Full suite 857 passed on its own run. recursive_type is published by discover. On main a recursive union read by a match raised RecursionError; it is now a structured refusal with exit 0. Composition with F2 and F3 shows no crash and no double reporting. Reviewer limits: Jev unavailable, no mutation run, no CI run, and evaluator.py, obligations.py and the rest of syntax.py were not audited. | resolution=Verdict accepted, no code changed, so the reviewed identity ac6f43a still stands. The 8 reviewer notes are accepted and deferred, none of them a defect of this behaviour: (1) the _is_a_cycle docstring at checker.py:386-388 still says functions although the search now serves type cycles; (2) the KIND default on DeclarationCycle at checker.py:67 is unreachable; (3) Diagnostic.cycle is typed DeclarationCycle or None while the base class declares no diagnostic method, latent and read by nothing; (4) the two cycle kinds format their names differently, unquoted for functions and quoted for types, and the F2 tests pin the unquoted form; (5) suppressing cyclic_dependency while a type cycle stands is sound and is disclosed as DEC2; (6) a redeclared builtin that also holds itself gives 2 refusals, duplicate_declaration and recursive_type; (7) the property generator is capped at 3 types and larger shapes are covered by hand and by the reviewer probes; (8) pre-existing and out of scope, a malformed sig crashes the parser with an unhandled IndexError at src/prova/syntax.py:411 on main too, which roadmap feature F6 owns. Notes 1 to 4 are editorial or latent and belong to the next change that touches those lines; 5 to 7 need no action; 8 is reported to its owner.

## 6. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
  - Data that leads back to itself is now refused.
- **not_verified**:
  - Jev was unavailable in this environment (TYPESAFE_API_KEY absent, client exit 3), so the category choice and the early-refusal choice were decided locally and recorded as DEC1 and DEC2 instead of being put to the service.
  - No mutation run and no CI run were made for this change; the suite was run locally on macOS with the Python the repository pins, not in the CI environment.
  - The recorded RED ran on the workspace pre-feature tree, which was taken before main moved; it therefore does not cover the F16 code that arrived with the rebase. Only the full suite run after the rebase covers that composition.
  - The 8 reviewer notes were not acted on, to keep the reviewed identity: the _is_a_cycle docstring still says functions, the KIND default on the base class is unreachable, Diagnostic.cycle is typed to a base class that declares no diagnostic method, and the two cycle kinds quote their names differently.
  - A malformed sig crashes the parser with an unhandled IndexError at src/prova/syntax.py:411; it is pre-existing on main, out of scope here, and belongs to roadmap feature F6.
  - The property generator is capped at 3 types; larger shapes (a 2000-type cycle and a 2000-type chain) were only exercised by the reviewer probes, not by a committed test.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit ac6f43a46e26768a44a08aea5f5f4477d4213c61
  - no checks declared

## Not backed by the diff

- The checker reads the declared field types of every record and every union variant as a dependency graph, reuses the cycle search the function rule already owns, and answers such a program in the new recursive_type category: the refusal names every type on the cycle, in its sentence and in the cycle member list of the response, says that core-0 requires the type-dependency graph to be acyclic and that recursive data belongs to a later profile, and says that the functions were not checked.: a guarantee names no test function of the change
- That last part is a decision with a measured reason (DEC2): on the pre-feature tree a recursive union read by a match ended the command in a RecursionError, because every check that follows the fields of a type ends only on acyclic types.: a guarantee names no test function of the change
- A field naming a type the program never declares stays an unknown type, and a chain of types that never leads back stays accepted.: a guarantee names no test function of the change
- The refusal got its own category rather than reusing cyclic_dependency (DEC1), so service.py grew by one published name and nothing else; a reader who filters by category keeps the call-graph rule and the data rule apart.: a guarantee names no test function of the change
- A prefactoring commit went first: the cycle search and the reading of a declared type fields each have one owner now, with no test edited.: a guarantee names no test function of the change
- A separate read-only reviewer agent approved the change on its own probes and left 8 notes, all accepted and deferred, none a defect of this behaviour; they are recorded with the review.: a guarantee names no test function of the change
