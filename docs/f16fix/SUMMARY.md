# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1007 tests, all green on main).
  - not-testable (challenge this): states the project, its test command and its baseline; no behaviour of the product follows from it
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names the authority document, states no behaviour that can be observed
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a rule about how I work; the diff shows whether I kept it, no test can
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): tells me what to do when a conflict appears; the conflict it covers is recorded on S30
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): tells me which directory to ignore, nothing observable follows from it
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a rule about where I work; the branch shows whether I kept it, no test can
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a rule about the commit message, which no test of the product observes
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the literal line a commit message must end with, observed in the log, not by a test
- S9: Do not push and do not merge.
  - not-testable (challenge this): a rule about push and merge, observed in the branch, not by a test
- S10: Keep the full suite green.
  - not-testable (challenge this): the whole suite is the observation; it is recorded as the step's own command, not as one test
- S11: Another delivery (F10, diagnostic fields: checker.py and service.py) runs in parallel in a different worktree; keep your change to src/prova/obligations.py, the tests and docs.
  - not-testable (challenge this): a rule about which files I may touch, observed in the diff, not by a test
- S12: Keep scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): a rule about where my scripts live, observed in the workspace, not by a test
- S13: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): a rule about how I call the tool and end the run, observed in the record, not by a test
- S14: **Outcome.** The `verify` inventory (src/prova/obligations.py) keeps what it already does correctly, the tests notice if any call position loses its obligation, and the path condition of an obligation in an `ensures` or a function body includes the function's own `requires`, as SPEC.md lines 210-220 say (`Pre_f(x) implies ...`).
  - promises: P1, P4
  - tests P1: test_a_call_in_every_position_a_body_can_hold_owes_its_entry
  - tests P4: test_every_function_example_and_call_owes_its_entry
- S15: The review (REV1, REJECT) measured 22 hand-made mutants against the 981-test suite: 9 survive.
  - not-testable (challenge this): reports what a review measured before this delivery; the re-measurement is the step's own command
- S16: Findings:
  - not-testable (challenge this): a heading that introduces the list of findings
- S17: 1.
  - not-testable (challenge this): the list number that introduces finding 1
- S18: (oracle gap, blocker) tests/properties/test_obligation_inventory_laws.py lines 42-48 and 104-110: BODY_SHAPES only puts the generated call in `body`, `body/then`, `body/case[0]`.
  - promises: P1
  - tests P1: test_a_call_in_every_position_a_body_can_hold_owes_its_entry
- S19: Deleting the else-arm (`_parts_of`, obligations.py ~360), the `bound +` in Let (~354), the FieldAccess descent (~348), the match scrutinee (~369-371) or the If condition (~358) silently loses real obligations and the suite stays green.
  - promises: P1
  - tests P1: test_a_call_in_every_position_a_body_can_hold_owes_its_entry
- S20: Extend the shapes with calls in an else arm, a let binding, an if condition, a match scrutinee and a field-access target, and assert the exact id set, not counts.
  - promises: P1
  - tests P1: test_a_call_in_every_position_a_body_can_hold_owes_its_entry
- S21: 2.
  - not-testable (challenge this): the list number that introduces finding 2
- S22: (oracle gap) only the path conditions "true" and "false" are ever asserted; dropping the earlier-clause negation (~377), `_can_fail` always True (~384) and `PathCondition.text` returning only clauses[0] (~69) survive.
  - promises: P2
  - tests P2: test_a_call_behind_several_conditions_is_owed_under_all_of_them
- S23: Add a program with at least 3 match clauses and an `if` nested in a `let`, asserting the full `(and ...)` text of the conditions.
  - promises: P2
  - tests P2: test_a_call_behind_several_conditions_is_owed_under_all_of_them
- S24: 3.
  - not-testable (challenge this): the list number that introduces finding 3
- S25: (oracle gap) `direct_calls` (~277) is never asserted; hardcoding 0 survives.
  - promises: P3
  - tests P3: test_the_ending_entry_says_how_many_calls_the_function_makes
- S26: Assert it on a function with a known call count.
  - promises: P3
  - tests P3: test_the_ending_entry_says_how_many_calls_the_function_makes
- S27: 4.
  - not-testable (challenge this): the list number that introduces finding 4
- S28: (defect) obligations.py ~288-290: call sites in an `ensures` and in a function body report path_condition "true" even though SPEC.md 210-220 says postcondition and body obligations hold under the function's `requires`.
  - not-testable (challenge this): describes the behaviour the rule on S30 would change; that rule is recorded there as a conflict and is not applied
- S29: Example: a4 with `requires (> (a3 n) 0)` calling a1 (which has `requires (> n 0)`) reports `call_precondition:a4:ensures[0]/arg[1]` and `call_precondition:a4:body` with "true"; a4's own precondition is dropped.
  - not-testable (challenge this): an example of that same behaviour; it is not changed, so no test of this delivery states it
- S30: Seed the path condition with the function's `requires` clauses for ensures-sites and body-sites ONLY; requires-sites correctly stay at an empty condition (SPEC.md 210-211).
  - not-testable (challenge this): not applied: it is the conflict recorded for this sentence, and no test may state a rule the delivery does not carry
- S31: Add the oracle case.
  - not-testable (challenge this): the oracle case it asks for would state the rule on S30, which is the conflict
- S32: This changes the path_condition text of existing obligations for functions that have a `requires`: if an existing test pins the old text, STOP and report (do not edit it silently).
  - not-testable (challenge this): the instruction I follow for S30, observed in the record, not by a test
- S33: 5.
  - not-testable (challenge this): the list number that introduces note 5
- S34: (note, not for you) path conditions mention let-bound names whose definition is in no entry; that is an input for F18.
  - not-testable (challenge this): a note the request addresses to another delivery, F18, not to this one
- S35: Do nothing.
  - not-testable (challenge this): an instruction to do nothing, so there is nothing to observe
- S36: Verification the reviewer will repeat: re-run the nine surviving mutants; each must now turn a test red.
  - not-testable (challenge this): the nine deletions are a measurement of the tests, recorded as the step's own command, not a behaviour of the product
- S37: Do the same yourself, in a throwaway worktree or by editing and restoring, and report each mutant and its failing test.
  - not-testable (challenge this): the same measurement, done by editing and restoring the file; it is recorded, not tested

## Edge matrix

- I1.empty: a source that declares nothing at all => refused as invalid_program with a syntax diagnostic and no inventory | self-probe: not probed | pre-feature not probed
- I1.unknown: a program that calls a function it never declares => refused with the whole-program check's own unbound_name diagnostic and no inventory | self-probe: not probed | pre-feature not probed
- I1.malformed: the source "(defn broken" => refused as invalid_program with a syntax diagnostic and no inventory | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the inventory reads no file, opens no socket and spawns nothing, so it has no dependency that can be gone
- I1.repeated: the same source asked about twice in a row => the same obligations with the same identities in the same order | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): one run reads one source on stdin and writes one answer; no state is shared between runs
- I1.crash: n/a (challenge this): the operation writes no file, so an interrupted run leaves nothing half-made to recover

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN a program with 1 function for each of the 9 positions a body can put a call in
  - WHEN the Owner asks what must be shown
  - THEN each of the 9 calls owes an entry at its own site and the program owes nothing else
  - test: test_a_call_in_every_position_a_body_can_hold_owes_its_entry
- SC2 (P1): not-held (no held self-probe case)
  - GIVEN a program whose only call sits in the else arm of an "if"
  - WHEN the Owner asks what must be shown
  - THEN the entry at "body/else" is owed under "(not (> n 0))"
  - test: test_every_function_example_and_call_owes_its_entry
- SC3 (P2): not-held (no held self-probe case)
  - GIVEN a program with 3 match clauses and an "if" inside a "let" inside the 2nd
  - WHEN the Owner asks what must be shown
  - THEN the call in the then arm is owed under "(and (not (matches n 0)) (matches n 1) (> n 5))"
  - test: test_a_call_behind_several_conditions_is_owed_under_all_of_them
- SC4 (P2): not-held (no held self-probe case)
  - GIVEN that same program, whose 3rd clause is the pattern "_"
  - WHEN the Owner reads the entry for that clause
  - THEN its condition is "(and (not (matches n 0)) (not (matches n 1)))" and the clause adds none of its own
  - test: test_a_call_behind_several_conditions_is_owed_under_all_of_them
- SC5 (P3): not-held (no held self-probe case)
  - GIVEN that same program, in which "pick" makes 4 calls and "tiny" makes 0
  - WHEN the Owner reads the 2 ending entries
  - THEN they report 4 and 0
  - test: test_the_ending_entry_says_how_many_calls_the_function_makes
- SC6 (P4): not-held (no held self-probe case)
  - GIVEN any program the plan describes, of 1 to 3 functions
  - WHEN the Owner asks what must be shown
  - THEN the answer lists exactly the obligations the plan says are owed and 0 others, each under the condition the plan gives it
  - test: test_every_function_example_and_call_owes_its_entry

## Questions for the owner

- S30: May the 3 tests that assert the old path condition be rewritten to the new one, or should the inventory keep reporting an ensures-site and a body-site as reached unconditionally?
  - existing behaviour: the rule changes the path condition of every ensures-site and body-site of a function that declares a requires; 3 existing tests state the old text as their expected result and fail when it is applied: tests/acceptance/test_verify_lists_the_obligations_owed.py::test_each_call_owes_its_precondition_under_the_condition_that_reaches_it, tests/properties/test_obligation_inventory_laws.py::test_every_function_example_and_call_owes_its_entry and ::test_putting_a_call_out_of_reach_keeps_what_it_owes
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- M tests/acceptance/test_verify_lists_the_obligations_owed.py (+90 -0 lines)
- M tests/properties/test_obligation_inventory_laws.py (+116 -2 lines)

## Commits (git log, BASE to HEAD)

- bd12621 [F16fix] notice when a call position loses its obligation

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f16fix/request.md
- **promises**:
  - P1: a call owes its own entry wherever in a body it sits, and a position that stops being walked is noticed
  - P2: a path condition names every condition on the way to the call, joined in the order the program writes them, and a pattern that always matches adds none
  - P3: the entry that says a function ends counts the calls that same function makes
  - P4: everything the inventory already answered correctly is still answered exactly the same way
- **sentence_map**:
  - S1 => not-testable: states the project, its test command and its baseline; no behaviour of the product follows from it
  - S2 => not-testable: names the authority document, states no behaviour that can be observed
  - S3 => not-testable: a rule about how I work; the diff shows whether I kept it, no test can
  - S4 => not-testable: tells me what to do when a conflict appears; the conflict it covers is recorded on S30
  - S5 => not-testable: tells me which directory to ignore, nothing observable follows from it
  - S6 => not-testable: a rule about where I work; the branch shows whether I kept it, no test can
  - S7 => not-testable: a rule about the commit message, which no test of the product observes
  - S8 => not-testable: the literal line a commit message must end with, observed in the log, not by a test
  - S9 => not-testable: a rule about push and merge, observed in the branch, not by a test
  - S10 => not-testable: the whole suite is the observation; it is recorded as the step's own command, not as one test
  - S11 => not-testable: a rule about which files I may touch, observed in the diff, not by a test
  - S12 => not-testable: a rule about where my scripts live, observed in the workspace, not by a test
  - S13 => not-testable: a rule about how I call the tool and end the run, observed in the record, not by a test
  - S14 => P1,P4
  - S15 => not-testable: reports what a review measured before this delivery; the re-measurement is the step's own command
  - S16 => not-testable: a heading that introduces the list of findings
  - S17 => not-testable: the list number that introduces finding 1
  - S18 => P1
  - S19 => P1
  - S20 => P1
  - S21 => not-testable: the list number that introduces finding 2
  - S22 => P2
  - S23 => P2
  - S24 => not-testable: the list number that introduces finding 3
  - S25 => P3
  - S26 => P3
  - S27 => not-testable: the list number that introduces finding 4
  - S28 => not-testable: describes the behaviour the rule on S30 would change; that rule is recorded there as a conflict and is not applied
  - S29 => not-testable: an example of that same behaviour; it is not changed, so no test of this delivery states it
  - S30 => not-testable: not applied: it is the conflict recorded for this sentence, and no test may state a rule the delivery does not carry
  - S31 => not-testable: the oracle case it asks for would state the rule on S30, which is the conflict
  - S32 => not-testable: the instruction I follow for S30, observed in the record, not by a test
  - S33 => not-testable: the list number that introduces note 5
  - S34 => not-testable: a note the request addresses to another delivery, F18, not to this one
  - S35 => not-testable: an instruction to do nothing, so there is nothing to observe
  - S36 => not-testable: the nine deletions are a measurement of the tests, recorded as the step's own command, not a behaviour of the product
  - S37 => not-testable: the same measurement, done by editing and restoring the file; it is recorded, not tested
- **scenarios**:
  - SC1 | P1 | GIVEN a program with 1 function for each of the 9 positions a body can put a call in | WHEN the Owner asks what must be shown | THEN each of the 9 calls owes an entry at its own site and the program owes nothing else
  - SC2 | P1 | GIVEN a program whose only call sits in the else arm of an "if" | WHEN the Owner asks what must be shown | THEN the entry at "body/else" is owed under "(not (> n 0))"
  - SC3 | P2 | GIVEN a program with 3 match clauses and an "if" inside a "let" inside the 2nd | WHEN the Owner asks what must be shown | THEN the call in the then arm is owed under "(and (not (matches n 0)) (matches n 1) (> n 5))"
  - SC4 | P2 | GIVEN that same program, whose 3rd clause is the pattern "_" | WHEN the Owner reads the entry for that clause | THEN its condition is "(and (not (matches n 0)) (not (matches n 1)))" and the clause adds none of its own
  - SC5 | P3 | GIVEN that same program, in which "pick" makes 4 calls and "tiny" makes 0 | WHEN the Owner reads the 2 ending entries | THEN they report 4 and 0
  - SC6 | P4 | GIVEN any program the plan describes, of 1 to 3 functions | WHEN the Owner asks what must be shown | THEN the answer lists exactly the obligations the plan says are owed and 0 others, each under the condition the plan gives it
- **conflicts**:
  - S1 | NONE | ran the whole suite on the branch before the change: 1007 tests, 0 failures, so the baseline the sentence states is the one I measured
  - S2 | NONE | read SPEC.md lines 200 to 230 and changed none of it
  - S3 | NONE | no existing test's expected result is changed by this delivery; the one rule that would change three of them is recorded as the conflict on S30
  - S4 | NONE | this sentence is the instruction I follow for S30; nothing in the repository contradicts it
  - S5 | NONE | read nothing under .relay/ and wrote nothing there
  - S6 | NONE | every commit is on feat/f16fix in this worktree; no other tree was touched
  - S7 | NONE | the commit message ends with the line the request gives
  - S8 | NONE | the commit message ends with exactly that line
  - S9 | NONE | no push and no merge was run; the branch is 1 commit ahead of its base, locally
  - S10 | NONE | the whole suite is green after the change: 1010 passed, 0 failed
  - S11 | NONE | src/prova/checker.py and src/prova/service.py are untouched; this delivery changes tests and documents only, and not even src/prova/obligations.py
  - S12 | NONE | the scripts live under the nwstep workspace in mine/ and none of them is committed
  - S13 | NONE | nwstep arguments are built in Python, so no shell reads an arrow; git status --short is run before the final message
  - S14 | NONE | its first two clauses are what this delivery proves; its third clause is the rule recorded as the conflict on S30, and it is not applied
  - S15 | NONE | re-ran all 9 deletions the review names and reproduced that the old tests let them live
  - S16 | NONE | a heading, nothing in the repository can contradict it
  - S17 | NONE | a list number, nothing in the repository can contradict it
  - S18 | NONE | read the file at those lines: BODY_SHAPES placed a call in 3 positions only, as the sentence says
  - S19 | NONE | applied each of those 5 deletions to the tree and confirmed the suite stayed green before the change
  - S20 | NONE | the walk over a body already visits all 5 positions, so the shapes can be extended without touching production code
  - S21 | NONE | a list number, nothing in the repository can contradict it
  - S22 | NONE | applied those 3 deletions and confirmed they survived the suite as it was
  - S23 | NONE | the reader of a path condition already joins several clauses, so such a program can be asserted as the sentence asks
  - S24 | NONE | a list number, nothing in the repository can contradict it
  - S25 | NONE | searched the tests for direct_calls and found no assertion on it before this change
  - S26 | NONE | the ending entry already reports the count, so a program with a known call count can assert it
  - S27 | NONE | a list number, nothing in the repository can contradict it
  - S28 | NONE | read obligations.py lines 282 to 291 and confirmed that ensures-sites and the body-site start from an empty condition, exactly as the sentence says
  - S29 | NONE | built that program and read the answer: both entries report true, as the sentence says
  - S30 | CONFLICT | the rule changes the path condition of every ensures-site and body-site of a function that declares a requires; 3 existing tests state the old text as their expected result and fail when it is applied: tests/acceptance/test_verify_lists_the_obligations_owed.py::test_each_call_owes_its_precondition_under_the_condition_that_reaches_it, tests/properties/test_obligation_inventory_laws.py::test_every_function_example_and_call_owes_its_entry and ::test_putting_a_call_out_of_reach_keeps_what_it_owes | May the 3 tests that assert the old path condition be rewritten to the new one, or should the inventory keep reporting an ensures-site and a body-site as reached unconditionally?
  - S31 | NONE | the oracle case for the rule is not added, because the rule it would state is the conflict on S30
  - S32 | NONE | this is the instruction I follow: 3 existing tests pin the old text, so the conflict is reported and no test is edited
  - S33 | NONE | a list number, nothing in the repository can contradict it
  - S34 | NONE | did nothing about let-bound names, as the sentence asks
  - S35 | NONE | did nothing, as the sentence asks
  - S36 | NONE | re-ran all 9 deletions against the delivered tests: each one turns at least one test red
  - S37 | NONE | re-ran them by editing and restoring the file in this worktree; the file is byte-identical to its committed form afterwards
- **decisions**:
  - S30: not applied. Applying it fails 3 existing tests (measured, whole suite: 3 failed, 1007 passed), and the request forbids editing an existing test's expected result and tells me to stop and report. Findings 1 to 3 are delivered; finding 4 goes back to the owner with the measurement.
  - DEC1: no formal model, no Quint. The inventory keeps no state, runs no protocol, spawns nothing and writes no file; it is a pure function from one syntax tree to one list.
  - DEC2: no production code is changed. Findings 1 to 3 are gaps in the oracle, not defects: the walk over a body already visits every position, so this delivery is tests and documents only.
  - DEC3: the nine deletions are applied and restored by a script kept under the nwstep workspace and never committed; after each run src/prova/obligations.py is byte-identical to its committed form.
  - DEC4: typesafe unavailable: TYPESAFE_API_KEY is absent from this environment and the client exits 3, so the conflict decision was taken locally from a measured whole-suite run.
- **mapping**:
  - P1 => test_a_call_in_every_position_a_body_can_hold_owes_its_entry
  - P2 => test_a_call_behind_several_conditions_is_owed_under_all_of_them
  - P3 => test_the_ending_entry_says_how_many_calls_the_function_makes
  - P4 => test_every_function_example_and_call_owes_its_entry
- **covers_scenarios**:
  - SC1 => test_a_call_in_every_position_a_body_can_hold_owes_its_entry
  - SC2 => test_every_function_example_and_call_owes_its_entry
  - SC3 => test_a_call_behind_several_conditions_is_owed_under_all_of_them
  - SC4 => test_a_call_behind_several_conditions_is_owed_under_all_of_them
  - SC5 => test_the_ending_entry_says_how_many_calls_the_function_makes
  - SC6 => test_every_function_example_and_call_owes_its_entry
- **predictions**:
  - SC1 => base held
  - SC2 => base held
  - SC3 => base held
  - SC4 => base held
  - SC5 => base held
  - SC6 => base held
- **interfaces**:
  - I1: the prova command's JSON stdin and stdout surface, operation verify, which answers with the inventory of obligations a source owes
- **matrix**:
  - I1.empty => a source that declares nothing at all => refused as invalid_program with a syntax diagnostic and no inventory
  - I1.unknown => a program that calls a function it never declares => refused with the whole-program check's own unbound_name diagnostic and no inventory
  - I1.malformed => the source "(defn broken" => refused as invalid_program with a syntax diagnostic and no inventory
  - I1.dependency-gone => n/a: the inventory reads no file, opens no socket and spawns nothing, so it has no dependency that can be gone
  - I1.repeated => the same source asked about twice in a row => the same obligations with the same identities in the same order
  - I1.concurrent => n/a: one run reads one source on stdin and writes one answer; no state is shared between runs
  - I1.crash => n/a: the operation writes no file, so an interrupted run leaves nothing half-made to recover
- **laws**:
  - LAW1 | every call a body makes owes its own precondition entry, wherever in the body it sits | generator=test_a_call_in_every_position_a_body_can_hold_owes_its_entry | observation=the exact set of obligation identities the answer lists | mutant=stop walking the else arm, the let bindings, the field-access target, the match scrutinee or the if condition
  - LAW2 | a path condition names every condition on the way to the call, joined in the order the program writes them, and a pattern that always matches adds none | generator=test_a_call_behind_several_conditions_is_owed_under_all_of_them | observation=the path_condition text of each call entry | mutant=drop the negation of the earlier clauses, treat every pattern as one that can fail, or print only the first clause
  - LAW3 | the entry that says a function ends counts the calls that same function makes | generator=test_the_ending_entry_says_how_many_calls_the_function_makes | observation=direct_calls reported per function | mutant=report a fixed 0
- **messages**:
  - MSG0 | none: this delivery adds no refusal path and no new edge form; every message the inventory can print already exists and is unchanged
- **red**: `uv run python /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f16fix/mine/mutants.py --red` exited 1 in 72.875s
  - failing on the pre-feature tree (4): tests/properties/test_obligation_inventory_laws.py::test_a_call_in_every_position_a_body_can_hold_owes_its_entry, tests/acceptance/test_verify_lists_the_obligations_owed.py::test_a_call_behind_several_conditions_is_owed_under_all_of_them, tests/acceptance/test_verify_lists_the_obligations_owed.py::test_the_ending_entry_says_how_many_calls_the_function_makes, tests/properties/test_obligation_inventory_laws.py::test_every_function_example_and_call_owes_its_entry
  - tests (read from the run): 3 failed, 16 passed in 10.93s
  ```text
          )
          counted = {entry.get("function"): entry.get("direct_calls") for entry in entries}

  >       assert counted == NESTED_DIRECT_CALLS, (
              f"WHAT: the ending entries report {counted} calls, not the "
              f"{NESTED_DIRECT_CALLS} the program writes. "
              "WHY: a function ends structurally because the calls it reaches are acyclic, "
              "so the Owner is told how many calls that claim is about; a fixed number "
              "tells them nothing about this program. "
              f"HOW: count the calls in:\n{NESTED_CONDITIONS_SOURCE}"
          )
  E       AssertionError: WHAT: the ending entries report {'tiny': 0, 'pick': 0} calls, not the {'tiny': 0, 'pick': 4} the program writes. WHY: a function ends structurally because the calls it reaches are acyclic, so the Owner is told how many calls that claim is about; a fixed number tells them nothing about this program. HOW: count the calls in:
  E         (defn tiny
  E           (sig ((n Int)) -> Int ! pure)
  E           (requires (> n 0))
  E           (examples (example (tiny 1) => 1))
  E           n)
  E
  E         (defn pick
  E           (sig ((n Int)) -> Int ! pure)
  E           (examples (example (pick 1) => 1))
  E           (match n
  E             (0 (tiny n))
  E             (1 (let ((m n)) (if (> n 5) (tiny n) (tiny m))))
  E             (_ (tiny n))))
  E
  E       assert {'tiny': 0, 'pick': 0} == {'tiny': 0, 'pick': 4}
  E
  E         Omitting 1 identical items, use -vv to show
  E         Differing items:
  E         {'pick': 0} != {'pick': 4}
  E         Use -v to get more diff

  tests/acceptance/test_verify_lists_the_obligations_owed.py:347: AssertionError
  =========================== short test summary info ============================
  FAILED tests/properties/test_obligation_inventory_laws.py::test_every_function_example_and_call_owes_its_entry
  FAILED tests/properties/test_obligation_inventory_laws.py::test_a_call_in_every_position_a_body_can_hold_owes_its_entry
  FAILED tests/acceptance/test_verify_lists_the_obligations_owed.py::test_the_ending_entry_says_how_many_calls_the_function_makes
  3 failed, 16 passed in 10.93s

  ```

## 2. craft: Craft the change (revision 1)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 111.332s
  - tests (read from the run): 1010 passed in 111.19s
  - slowest: 6.69s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.24s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.89s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.29s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.75s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.98s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.63s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.56s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.36s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  - slowest: 1.34s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  ```text
  ........................................................................ [  7%]
  ........................................................................ [ 14%]
  ........................................................................ [ 21%]
  ........................................................................ [ 28%]
  ........................................................................ [ 35%]
  ........................................................................ [ 42%]
  ........................................................................ [ 49%]
  ........................................................................ [ 57%]
  ........................................................................ [ 64%]
  ........................................................................ [ 71%]
  ........................................................................ [ 78%]
  ........................................................................ [ 85%]
  ........................................................................ [ 92%]
  ........................................................................ [ 99%]
  ..                                                                       [100%]
  ============================= slowest 10 durations =============================
  6.69s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.24s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.89s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.29s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.75s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.98s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.63s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.56s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.36s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1.34s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1010 passed in 111.19s (0:01:51)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.041s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this environment; the client exits 3, so the conflict on S30 was decided locally from a measured whole-suite run
