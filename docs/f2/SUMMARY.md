# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`).
  - not-testable (challenge this): names the project, its runtime and its test command, a setting not an outcome
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority for this work, a setting not an outcome
- S3: Do not change SPEC.md, the reservation example's semantics, or any existing test's expected result.
  - promises: P6
  - tests P6: test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself
- S4: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): tells the worker which directory to ignore, no observable outcome
- S5: Work in this git worktree only, on its branch.
  - not-testable (challenge this): names the worktree and branch to work in, a process constraint
- S6: Commit with a message ending in the line
  - not-testable (challenge this): requires a commit message ending, a process constraint
- S7: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the attribution line a commit must end with, a process constraint
- S8: Do not push and do not merge.
  - not-testable (challenge this): forbids pushing and merging, a process constraint
- S9: Keep the full suite green.
  - promises: P6
  - tests P6: test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself
- S10: Another delivery runs in parallel in a different worktree; stay inside your feature.
  - not-testable (challenge this): a parallel delivery in another worktree, a process constraint
- S11: **Outcome.** A program whose calls form a cycle is refused when it is checked,
  - promises: P1, P2, P3
  - tests P1: test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
  - tests P2: test_two_functions_that_call_each_other_are_refused_and_both_are_named
  - tests P3: test_a_cycle_that_runs_only_through_a_contract_clause_is_refused
- S12: with the cycle named.
  - promises: P1, P2
  - tests P1: test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
  - tests P2: test_two_functions_that_call_each_other_are_refused_and_both_are_named
- S13: The tool never dies with a Python traceback.
  - promises: P4
  - tests P4: test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json
- S14: **Acceptance criteria**
  - not-testable (challenge this): a heading that introduces the criteria, with no outcome of its own
- S15: 1.
  - not-testable (challenge this): a list marker numbering the first criterion, with no content
- S16: Given a function whose body calls itself, when the program is checked, then the
  - promises: P1
  - tests P1: test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
- S17: program is invalid and the diagnostic names the function in the cycle.
  - promises: P1
  - tests P1: test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
- S18: 2.
  - not-testable (challenge this): a list marker numbering the second criterion, with no content
- S19: Given two functions that call each other, when the program is checked, then the
  - promises: P2
  - tests P2: test_two_functions_that_call_each_other_are_refused_and_both_are_named
- S20: program is invalid and the diagnostic names both.
  - promises: P2
  - tests P2: test_two_functions_that_call_each_other_are_refused_and_both_are_named
- S21: 3.
  - not-testable (challenge this): a list marker numbering the third criterion, with no content
- S22: Given a cycle that runs only through a contract clause, when the program is
  - promises: P3
  - tests P3: test_a_cycle_that_runs_only_through_a_contract_clause_is_refused
- S23: checked, then the program is invalid.
  - promises: P3
  - tests P3: test_a_cycle_that_runs_only_through_a_contract_clause_is_refused
- S24: 4.
  - not-testable (challenge this): a list marker numbering the fourth criterion, with no content
- S25: Given any of those programs, when a function is evaluated, then the answer is a
  - promises: P4
  - tests P4: test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json
- S26: structured refusal in valid JSON and the process exits normally.
  - promises: P4
  - tests P4: test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json
- S27: 5.
  - not-testable (challenge this): a list marker numbering the fifth criterion, with no content
- S28: Given a function whose examples call that function, when the program is checked,
  - promises: P5
  - tests P5: test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself
- S29: then it is accepted (those self-calls are not a cycle).
  - promises: P5
  - tests P5: test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself
- S30: 6.
  - not-testable (challenge this): a list marker numbering the sixth criterion, with no content
- S31: Given the hour clock and the reservation example, when they are checked, then
  - promises: P6
  - tests P6: test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself
- S32: both still pass.
  - promises: P6
  - tests P6: test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself
- S33: **SPEC.md** lines 163-168 (acyclic body and contract graph), 186-189 (termination
  - not-testable (challenge this): cites the authority lines that state the acyclic rule, a citation not an outcome
- S34: follows from acyclicity), 322-325.
  - not-testable (challenge this): cites the authority lines on termination and effects, a citation not an outcome
- S35: **Dependencies** none.
  - not-testable (challenge this): states that this feature waits for no other work
- S36: **Size** M: needs a whole-program call graph over bodies and
  - not-testable (challenge this): a size estimate and the internal structure it needs, which no caller observes
- S37: contracts with the examples edge excluded.
  - promises: P5
  - tests P5: test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself
- S38: **Touches** `src/prova/checker.py`, one new diagnostic category in
  - not-testable (challenge this): names the files expected to change, an internal fact no caller observes
- S39: `src/prova/service.py:17-33`, tests.
  - not-testable (challenge this): names the files expected to change, an internal fact no caller observes
- S40: **Why it is a real expectation** probes T17, T18, T19 all disagree today;
  - not-testable (challenge this): cites existing probes as the reason this is a real expectation
- S41: `docs/spec-trace.md` defect 1 records the uncaught `RecursionError`.
  - not-testable (challenge this): cites the recorded defect as the reason, a reason not an outcome

## Edge matrix

- I1.empty: source is the empty string => completed with no diagnostics: a program with no function has no call and no cycle | self-probe: not probed | pre-feature not probed
- I1.unknown: a body calls a function no declaration names => invalid_program with the existing unbound_name diagnostic and no cycle reported | self-probe: not probed | pre-feature not probed
- I1.malformed: an unclosed form such as (defn f => invalid_program with the existing syntax diagnostic; the cycle rule never runs | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): check reads only the source carried in the request and opens no file, service or other dependency
- I1.repeated: the same cyclic program checked in two separate runs => identical responses, with the same cycle written the same way | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): each request is one short-lived process that shares no mutable state and writes no output other runs could read
- I1.crash: n/a (challenge this): check writes nothing, so an interrupted run leaves no partial state behind to recover
- I2.empty: source is the empty string and a function is named => invalid_input with unknown_function, as it answers today | self-probe: not probed | pre-feature not probed
- I2.unknown: a function name the cyclic program does not declare => invalid_program naming the cycle, because the program is checked before the function is looked up, as it is today | self-probe: not probed | pre-feature not probed
- I2.malformed: an argument text that is not a value, such as ((( => invalid_input with malformed_value, as it answers today | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): evaluate reads only the source and arguments carried in the request
- I2.repeated: the same cyclic program evaluated twice => identical refusals and exit code 0 both times | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): one short-lived process per request, with no shared state between them
- I2.crash: the uncaught RecursionError that ends the process with exit 1 today => exit 0 with a JSON refusal: this edge is the defect the feature removes | self-probe: not probed | pre-feature not probed
- I3.empty: source is the empty string => completed with 0 example results | self-probe: not probed | pre-feature not probed
- I3.unknown: a cyclic program whose example names an undeclared function => invalid_program, because the program is checked before any example runs | self-probe: not probed | pre-feature not probed
- I3.malformed: an unclosed form => invalid_program with the existing syntax diagnostic | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): the examples operation reads only the source carried in the request
- I3.repeated: the declared examples of the same cyclic program run twice => identical refusals and exit code 0 both times | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): one short-lived process per request, with no shared state between them
- I3.crash: the uncaught RecursionError raised while running a declared example of a cyclic program => exit 0 with a JSON refusal | self-probe: not probed | pre-feature not probed
- I4.empty: a discover request with no source field => the manifest, now listing 1 more diagnostic category than before | self-probe: not probed | pre-feature not probed
- I4.unknown: an operation name the tool does not recognise => unavailable with unknown_operation, unchanged by this work | self-probe: not probed | pre-feature not probed
- I4.malformed: a request that is not JSON => the existing tool_failure answer, unchanged by this work | self-probe: not probed | pre-feature not probed
- I4.dependency-gone: n/a (challenge this): discover reads only its own manifest and opens no dependency
- I4.repeated: discover asked twice => identical manifests, including the order of the category list | self-probe: not probed | pre-feature not probed
- I4.concurrent: n/a (challenge this): one short-lived process per request, with no shared state between them
- I4.crash: n/a (challenge this): discover evaluates nothing and writes nothing, so it has no crash window of its own

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the program (defn countdown (sig ((n Int)) -> Int ! pure) (examples (example (countdown 1) => 0)) (countdown (- n 1)))
  - WHEN the program is checked
  - THEN the status is invalid_program and the 1 reported cycle names countdown
  - test: test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN even-steps whose body calls odd-steps and odd-steps whose body calls even-steps, each with 1 declared example
  - WHEN the program is checked
  - THEN the status is invalid_program and the 1 reported cycle names both even-steps and odd-steps
  - test: test_two_functions_that_call_each_other_are_refused_and_both_are_named
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN (defn balance ... (ensures (= (balance result) result)) ... n) whose body is just the parameter n and whose 1 ensures clause calls balance
  - WHEN the program is checked
  - THEN the status is invalid_program and the 1 reported cycle names balance
  - test: test_a_cycle_that_runs_only_through_a_contract_clause_is_refused
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN that same self-calling countdown program, which today ends the process with exit 1 and an uncaught RecursionError
  - WHEN countdown is evaluated with the argument 3
  - THEN the exit code is 0, stdout is valid JSON with status invalid_program, and stderr carries no traceback
  - test: test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json
- SC5 (P4): not-held (no held self-probe case)
  - GIVEN that same self-calling countdown program with its 1 declared example
  - WHEN its declared examples are run
  - THEN the exit code is 0, stdout is valid JSON with status invalid_program, and stderr carries no traceback
  - test: test_running_the_declared_examples_of_a_cyclic_program_is_refused_in_json
- SC6 (P5): not-held (no held self-probe case)
  - GIVEN (defn doubled ... (examples (example (doubled 3) => 6) (example (doubled 0) => 0)) (+ n n)), whose 2 examples both name doubled
  - WHEN the program is checked
  - THEN the status is completed with 0 diagnostics, while the same function with (doubled n) added to its body is invalid_program
  - test: test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself
- SC7 (P6): not-held (no held self-probe case)
  - GIVEN examples/hour-clock.prova and the reservation example of SPEC.md, each with 3 functions calling valid-state
  - WHEN each is checked
  - THEN the status is completed with 0 diagnostics, while a copy whose guard is replaced by (valid-state current) is invalid_program
  - test: test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself
- SC8 (P1): not-held (no held self-probe case)
  - GIVEN a generated program of 1 to 3 functions with a body edge and a contract edge drawn for each ordered pair
  - WHEN each program is checked
  - THEN it is refused exactly when a function can reach itself, the refusal names exactly those functions, and 2 separate runs give 1 identical answer
  - test: test_a_program_is_refused_exactly_when_its_calls_form_a_cycle

## Questions for the owner

- S11: Which diagnostic category should a refused cyclic program carry, since the choice is visible to every caller of this tool?
  - existing behaviour: checked all three shapes against the current build: a self-calling function, a mutually calling pair and a contract-only cycle each answer status completed from check today, so the system accepts exactly what this sentence asks it to refuse
  - status: decided at oracle
- S12: Should the refusal name the cycle in a machine-readable field beside the reason text, or in the reason text alone?
  - existing behaviour: nothing in the response names a cycle today, and the existing diagnostic entries carry only category, reason and location, so there is no field a caller can read the members of a cycle from
  - status: decided at oracle
- S13: A refused program will now answer with a diagnostic and exit 0, where today the caller sees exit 1: is exit 0 with a refusal in the response the answer you want for a program the tool refuses to run?
  - existing behaviour: evaluating the self-calling program ends the process with exit 1, an empty stdout and an uncaught RecursionError on stderr, which contradicts the promise that the tool never dies with a traceback
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- A docs/feature/f2/craft.md (+77 -0 lines)
- A docs/feature/f2/design.md (+111 -0 lines)
- A docs/feature/f2/oracle.md (+88 -0 lines)
- M docs/spec-trace.md (+7 -0 lines)
- M src/prova/checker.py (+171 -2 lines)
- M src/prova/service.py (+3 -0 lines)
- A tests/acceptance/_f2_cycle_fixtures.py (+242 -0 lines)
- A tests/acceptance/test_f2_b1_self_calling_function_is_refused.py (+63 -0 lines)
- A tests/acceptance/test_f2_b2_mutually_calling_functions_are_refused.py (+67 -0 lines)
- A tests/acceptance/test_f2_b3_contract_cycle_is_refused.py (+60 -0 lines)
- A tests/acceptance/test_f2_b4_evaluating_a_cyclic_program_refuses_without_crashing.py (+96 -0 lines)
- A tests/acceptance/test_f2_b5_examples_naming_their_own_function_are_accepted.py (+48 -0 lines)
- A tests/acceptance/test_f2_char1_shipped_programs_still_check.py (+70 -0 lines)
- A tests/properties/test_f2_call_graph_cycles.py (+178 -0 lines)
- A tests/unit/test_checker_cycle_value.py (+48 -0 lines)

## Commits (git log, BASE to HEAD)

- 25eea8c [F2] oracle: a program whose calls form a cycle must be refused, not crash
- 8db12de [F2] record what the oracle step decided, in plain language
- 61ca48e [F2] record the design: one more whole-program pass in the checker
- 851dfd2 [F2] refuse a program whose calls form a cycle, naming the functions
- f2ff7f9 [F2] record the craft step and note the fixed conformance defect

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f2/request.md
- **promises**:
  - P1: A function whose body calls itself is refused when the program is checked, and the refusal names that function.
  - P2: Two functions that call each other are refused when the program is checked, and the refusal names both of them.
  - P3: A program whose only cycle runs through a contract clause is refused when the program is checked.
  - P4: Asking a cyclic program for an answer gives a structured refusal in valid JSON and the process exits normally; the tool never dies with a Python traceback.
  - P5: A function whose declared examples name that same function is accepted, because an example call to its own function is not a cycle.
  - P6: The hour clock and the reservation example still pass when they are checked, and no result an existing test expects changes.
- **sentence_map**:
  - S1 => not-testable: names the project, its runtime and its test command, a setting not an outcome
  - S2 => not-testable: names SPEC.md as the authority for this work, a setting not an outcome
  - S3 => P6
  - S4 => not-testable: tells the worker which directory to ignore, no observable outcome
  - S5 => not-testable: names the worktree and branch to work in, a process constraint
  - S6 => not-testable: requires a commit message ending, a process constraint
  - S7 => not-testable: the attribution line a commit must end with, a process constraint
  - S8 => not-testable: forbids pushing and merging, a process constraint
  - S9 => P6
  - S10 => not-testable: a parallel delivery in another worktree, a process constraint
  - S11 => P1,P2,P3
  - S12 => P1,P2
  - S13 => P4
  - S14 => not-testable: a heading that introduces the criteria, with no outcome of its own
  - S15 => not-testable: a list marker numbering the first criterion, with no content
  - S16 => P1
  - S17 => P1
  - S18 => not-testable: a list marker numbering the second criterion, with no content
  - S19 => P2
  - S20 => P2
  - S21 => not-testable: a list marker numbering the third criterion, with no content
  - S22 => P3
  - S23 => P3
  - S24 => not-testable: a list marker numbering the fourth criterion, with no content
  - S25 => P4
  - S26 => P4
  - S27 => not-testable: a list marker numbering the fifth criterion, with no content
  - S28 => P5
  - S29 => P5
  - S30 => not-testable: a list marker numbering the sixth criterion, with no content
  - S31 => P6
  - S32 => P6
  - S33 => not-testable: cites the authority lines that state the acyclic rule, a citation not an outcome
  - S34 => not-testable: cites the authority lines on termination and effects, a citation not an outcome
  - S35 => not-testable: states that this feature waits for no other work
  - S36 => not-testable: a size estimate and the internal structure it needs, which no caller observes
  - S37 => P5
  - S38 => not-testable: names the files expected to change, an internal fact no caller observes
  - S39 => not-testable: names the files expected to change, an internal fact no caller observes
  - S40 => not-testable: cites existing probes as the reason this is a real expectation
  - S41 => not-testable: cites the recorded defect as the reason, a reason not an outcome
- **scenarios**:
  - SC1 | P1 | GIVEN the program (defn countdown (sig ((n Int)) -> Int ! pure) (examples (example (countdown 1) => 0)) (countdown (- n 1))) | WHEN the program is checked | THEN the status is invalid_program and the 1 reported cycle names countdown
  - SC2 | P2 | GIVEN even-steps whose body calls odd-steps and odd-steps whose body calls even-steps, each with 1 declared example | WHEN the program is checked | THEN the status is invalid_program and the 1 reported cycle names both even-steps and odd-steps
  - SC3 | P3 | GIVEN (defn balance ... (ensures (= (balance result) result)) ... n) whose body is just the parameter n and whose 1 ensures clause calls balance | WHEN the program is checked | THEN the status is invalid_program and the 1 reported cycle names balance
  - SC4 | P4 | GIVEN that same self-calling countdown program, which today ends the process with exit 1 and an uncaught RecursionError | WHEN countdown is evaluated with the argument 3 | THEN the exit code is 0, stdout is valid JSON with status invalid_program, and stderr carries no traceback
  - SC5 | P4 | GIVEN that same self-calling countdown program with its 1 declared example | WHEN its declared examples are run | THEN the exit code is 0, stdout is valid JSON with status invalid_program, and stderr carries no traceback
  - SC6 | P5 | GIVEN (defn doubled ... (examples (example (doubled 3) => 6) (example (doubled 0) => 0)) (+ n n)), whose 2 examples both name doubled | WHEN the program is checked | THEN the status is completed with 0 diagnostics, while the same function with (doubled n) added to its body is invalid_program
  - SC7 | P6 | GIVEN examples/hour-clock.prova and the reservation example of SPEC.md, each with 3 functions calling valid-state | WHEN each is checked | THEN the status is completed with 0 diagnostics, while a copy whose guard is replaced by (valid-state current) is invalid_program
  - SC8 | P1 | GIVEN a generated program of 1 to 3 functions with a body edge and a contract edge drawn for each ordered pair | WHEN each program is checked | THEN it is refused exactly when a function can reach itself, the refusal names exactly those functions, and 2 separate runs give 1 identical answer
- **conflicts**:
  - S1 | NONE | ran uv run pytest -q tests on the pre-feature tree: 772 passed in 67.90s, so the stated command and runtime are the ones this repository uses
  - S2 | NONE | read SPEC.md lines 163-168, 186-189 and 322-325; they state the acyclic rule this request asks for, and contradict nothing in it
  - S3 | NONE | the new tests read SPEC.md and build cyclic copies in memory only; no test edits SPEC.md, the example or any existing expected result
  - S4 | NONE | the .relay directory holds planning notes only; no source, test or example under it is read by the suite
  - S5 | NONE | git status shows this worktree on branch feat/f2 with no other checkout in the way of the work
  - S6 | NONE | the repository has no commit-msg hook and no .pre-commit-config.yaml, so no installed check disagrees with the required ending
  - S7 | NONE | existing commits carry a Co-Authored-By trailer of the same shape, so the required line fits the history
  - S8 | NONE | no automation in this repository pushes or merges, so nothing contradicts leaving the branch local
  - S9 | NONE | the whole suite passes before the change, so green is a state this change must preserve rather than restore
  - S10 | NONE | the touched files named by this request are checker.py, service.py and new test files only, so another worktree is not shared
  - S11 | CONFLICT | checked all three shapes against the current build: a self-calling function, a mutually calling pair and a contract-only cycle each answer status completed from check today, so the system accepts exactly what this sentence asks it to refuse | Which diagnostic category should a refused cyclic program carry, since the choice is visible to every caller of this tool?
  - S12 | CONFLICT | nothing in the response names a cycle today, and the existing diagnostic entries carry only category, reason and location, so there is no field a caller can read the members of a cycle from | Should the refusal name the cycle in a machine-readable field beside the reason text, or in the reason text alone?
  - S13 | CONFLICT | evaluating the self-calling program ends the process with exit 1, an empty stdout and an uncaught RecursionError on stderr, which contradicts the promise that the tool never dies with a traceback | A refused program will now answer with a diagnostic and exit 0, where today the caller sees exit 1: is exit 0 with a refusal in the response the answer you want for a program the tool refuses to run?
  - S14 | NONE | a heading introduces the list that follows and states no behaviour the current build could contradict
  - S15 | NONE | a bare list marker states no behaviour the current build could contradict
  - S16 | NONE | the shape is already covered by the conflict recorded for S11; the body self-call is accepted today and nothing else about it disagrees
  - S17 | NONE | no existing test or example expects a self-calling function to be accepted, so refusing it breaks no recorded expectation
  - S18 | NONE | a bare list marker states no behaviour the current build could contradict
  - S19 | NONE | the mutually calling pair is covered by the conflict recorded for S11; nothing else in the build disagrees with refusing it
  - S20 | NONE | no existing test expects a mutually calling pair to be accepted, so refusing it breaks no recorded expectation
  - S21 | NONE | a bare list marker states no behaviour the current build could contradict
  - S22 | NONE | checked the contract clause path: check already type-checks requires and ensures, so a contract call is already visible where the graph will be built
  - S23 | NONE | the hour clock and the reservation example call other functions from contracts but never back, so refusing contract cycles leaves them accepted
  - S24 | NONE | a bare list marker states no behaviour the current build could contradict
  - S25 | NONE | evaluate already runs the whole check before it looks up the function, so a refused program reaches the caller as invalid_program without further work
  - S26 | NONE | the command already prints one JSON response and exits 0 for every answered request, so exiting normally needs no change of that path
  - S27 | NONE | a bare list marker states no behaviour the current build could contradict
  - S28 | NONE | declared examples are parsed as values, not expressions, so an example never contributes a call edge that a graph over bodies and contracts could see
  - S29 | NONE | every function in the repository declares an example naming itself, so accepting those is the behaviour the build already has and must keep
  - S30 | NONE | a bare list marker states no behaviour the current build could contradict
  - S31 | NONE | checked both programs: the hour clock and the reservation example are accepted today and their calls are acyclic, so the new rule leaves them accepted
  - S32 | NONE | both programs are covered by existing passing tests, which this change leaves untouched
  - S33 | NONE | read those authority lines; they state the rule the request asks for and no other rule the build already implements differently
  - S34 | NONE | read lines 322-325; they rule out a runtime step cap, which agrees with refusing at check time instead of counting steps at run time
  - S35 | NONE | nothing in the current build is half-finished in this area; there is no partial cycle check to wait for
  - S36 | NONE | the checker already walks every body and contract expression, so building the graph needs no structure the build lacks
  - S37 | NONE | the examples clause holds values only, so excluding it from the graph agrees with how the build already parses examples
  - S38 | NONE | read checker.py: check_program is the one place a whole-program rule can be added, which agrees with the named file
  - S39 | NONE | read service.py lines 17-33: DIAGNOSTIC_CATEGORIES is the published vocabulary and the discover test asserts a subset, so adding one category breaks no existing expectation
  - S40 | NONE | ran the three probes by hand against the current build: all three programs answer completed from check, which matches the claim that they disagree
  - S41 | NONE | read docs/spec-trace.md defect 1 and reproduced the uncaught RecursionError, so the recorded defect is the behaviour observed today
- **decisions**:
  - S11: The refusal carries a new diagnostic category cyclic_dependency, named after the rule of the authority (the combined dependency graph of bodies and contracts must be acyclic) rather than after recursion, so that a mutual or contract-only cycle is not mis-described as a recursive definition. Recorded as the executor decision and put to the person at the pause after this step.
  - S12: One diagnostic per cycle, naming every function of that cycle in a cycle field beside the human reason, which also names them. A machine-readable field lets a caller read the members without parsing prose, and one entry per cycle is what makes the two-function criterion observable as one finding naming both.
  - S13: Exit 0 with the refusal carried in the response, because the request asks that the process exit normally and every answered request already exits 0, including a program refused as invalid_program; no caller in this repository branches on a non-zero exit. Put to the person at the pause after this step. The refusal at check time also removes the only path that reached the uncaught RecursionError: refusing the program when it is checked removes the only path that reached the uncaught RecursionError, since evaluate and examples both check the program before they evaluate anything.
  - DEC1: Paradigm and layout follow the sibling code, because the authority text names none: module-level functions and frozen dataclasses, the check added inside check_program, acceptance tests driving the installed command over JSON and property tests calling the service in process.
  - DEC2: No formal model (Quint). The rule is a pure graph property of one immutable parsed program, with no state machine, protocol, concurrency or crash window to explore; a generated property over call graphs observes the same law directly and runs in the suite.
  - DEC3: The two promises that state behaviour the build already has (P5, P6) are each tested together with the one program they must stay distinguishable from, so the test fails if the new rule is absent, if it over-rejects, or if the check silently stops running on those programs.
- **mapping**:
  - P1 => test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
  - P2 => test_two_functions_that_call_each_other_are_refused_and_both_are_named
  - P3 => test_a_cycle_that_runs_only_through_a_contract_clause_is_refused
  - P4 => test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json
  - P5 => test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself
  - P6 => test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself
- **covers_scenarios**:
  - SC1 => test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
  - SC2 => test_two_functions_that_call_each_other_are_refused_and_both_are_named
  - SC3 => test_a_cycle_that_runs_only_through_a_contract_clause_is_refused
  - SC4 => test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json
  - SC5 => test_running_the_declared_examples_of_a_cyclic_program_is_refused_in_json
  - SC6 => test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself
  - SC7 => test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself
  - SC8 => test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC6 => base differs
  - SC7 => base differs
  - SC8 => base differs
- **interfaces**:
  - I1: the check operation of the prova command, one JSON request on stdin and one JSON response on stdout
  - I2: the evaluate operation of the prova command, same JSON surface
  - I3: the examples operation of the prova command, same JSON surface
  - I4: the discover operation of the prova command, which publishes the diagnostic categories this tool can emit
- **matrix**:
  - I1.empty => source is the empty string => completed with no diagnostics: a program with no function has no call and no cycle
  - I1.unknown => a body calls a function no declaration names => invalid_program with the existing unbound_name diagnostic and no cycle reported
  - I1.malformed => an unclosed form such as (defn f => invalid_program with the existing syntax diagnostic; the cycle rule never runs
  - I1.dependency-gone => n/a: check reads only the source carried in the request and opens no file, service or other dependency
  - I1.repeated => the same cyclic program checked in two separate runs => identical responses, with the same cycle written the same way
  - I1.concurrent => n/a: each request is one short-lived process that shares no mutable state and writes no output other runs could read
  - I1.crash => n/a: check writes nothing, so an interrupted run leaves no partial state behind to recover
  - I2.empty => source is the empty string and a function is named => invalid_input with unknown_function, as it answers today
  - I2.unknown => a function name the cyclic program does not declare => invalid_program naming the cycle, because the program is checked before the function is looked up, as it is today
  - I2.malformed => an argument text that is not a value, such as ((( => invalid_input with malformed_value, as it answers today
  - I2.dependency-gone => n/a: evaluate reads only the source and arguments carried in the request
  - I2.repeated => the same cyclic program evaluated twice => identical refusals and exit code 0 both times
  - I2.concurrent => n/a: one short-lived process per request, with no shared state between them
  - I2.crash => the uncaught RecursionError that ends the process with exit 1 today => exit 0 with a JSON refusal: this edge is the defect the feature removes
  - I3.empty => source is the empty string => completed with 0 example results
  - I3.unknown => a cyclic program whose example names an undeclared function => invalid_program, because the program is checked before any example runs
  - I3.malformed => an unclosed form => invalid_program with the existing syntax diagnostic
  - I3.dependency-gone => n/a: the examples operation reads only the source carried in the request
  - I3.repeated => the declared examples of the same cyclic program run twice => identical refusals and exit code 0 both times
  - I3.concurrent => n/a: one short-lived process per request, with no shared state between them
  - I3.crash => the uncaught RecursionError raised while running a declared example of a cyclic program => exit 0 with a JSON refusal
  - I4.empty => a discover request with no source field => the manifest, now listing 1 more diagnostic category than before
  - I4.unknown => an operation name the tool does not recognise => unavailable with unknown_operation, unchanged by this work
  - I4.malformed => a request that is not JSON => the existing tool_failure answer, unchanged by this work
  - I4.dependency-gone => n/a: discover reads only its own manifest and opens no dependency
  - I4.repeated => discover asked twice => identical manifests, including the order of the category list
  - I4.concurrent => n/a: one short-lived process per request, with no shared state between them
  - I4.crash => n/a: discover evaluates nothing and writes nothing, so it has no crash window of its own
- **laws**:
  - LAW1 | A program is refused exactly when the graph of its body and contract calls has a cycle, the refusal names exactly the functions that lie on one, and a declared example call to its own function is never an edge | generator=test_a_program_is_refused_exactly_when_its_calls_form_a_cycle | observation=for every generated call graph, status invalid_program with cyclic_dependency naming exactly the functions that can reach themselves, else status completed with no diagnostics | mutant=count an example call as an edge and every generated program becomes cyclic, so the accepted half fails
  - LAW2 | The answer depends on the program alone: two separate runs of the command on the same source answer identically, so no set iteration order decides which cycle is reported first or how its members are written | generator=test_checking_the_same_program_in_two_runs_gives_the_same_answer | observation=the responses of two processes, which have two hash seeds, compare equal | mutant=write the cycle members in set iteration order and the two runs disagree
- **messages**:
  - MSG1 | a function whose body calls itself | the calls of the program form a cycle through countdown | core-0 requires the combined dependency graph of function bodies and contracts to be acyclic, so the tool cannot promise the call ends | remove the call to countdown from the body or contract of countdown; a call in an example to its own function is not part of the graph | test=test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
  - MSG2 | two functions that call each other | the calls of the program form a cycle through even-steps and odd-steps | the same acyclic rule covers mutual recursion, not only direct recursion | remove one of the two calls so that the pair no longer depends on itself | test=test_two_functions_that_call_each_other_are_refused_and_both_are_named
  - MSG3 | a function whose ensures clause calls itself | the calls of the program form a cycle through balance | the graph covers contract clauses as well as bodies, so a contract call closes a cycle exactly as a body call does | remove the call to balance from its ensures clause, or call a different function from it | test=test_a_cycle_that_runs_only_through_a_contract_clause_is_refused
- **red**: `uv run pytest -q tests/acceptance/test_f2_b1_self_calling_function_is_refused.py tests/acceptance/test_f2_b2_mutually_calling_functions_are_refused.py tests/acceptance/test_f2_b3_contract_cycle_is_refused.py tests/acceptance/test_f2_b4_evaluating_a_cyclic_program_refuses_without_crashing.py tests/acceptance/test_f2_b5_examples_naming_their_own_function_are_accepted.py tests/acceptance/test_f2_char1_shipped_programs_still_check.py tests/properties/test_f2_call_graph_cycles.py` exited 1 in 2.512s
  - failing on the pre-feature tree (9): tests/acceptance/test_f2_b1_self_calling_function_is_refused.py::test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it, tests/acceptance/test_f2_b2_mutually_calling_functions_are_refused.py::test_two_functions_that_call_each_other_are_refused_and_both_are_named, tests/acceptance/test_f2_b3_contract_cycle_is_refused.py::test_a_cycle_that_runs_only_through_a_contract_clause_is_refused, tests/acceptance/test_f2_b4_evaluating_a_cyclic_program_refuses_without_crashing.py::test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json, tests/acceptance/test_f2_b4_evaluating_a_cyclic_program_refuses_without_crashing.py::test_running_the_declared_examples_of_a_cyclic_program_is_refused_in_json, tests/acceptance/test_f2_b5_examples_naming_their_own_function_are_accepted.py::test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself, tests/acceptance/test_f2_char1_shipped_programs_still_check.py::test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself, tests/acceptance/test_f2_char1_shipped_programs_still_check.py::test_the_reservation_example_still_passes_unlike_a_copy_whose_guard_calls_itself, tests/properties/test_f2_call_graph_cycles.py::test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
  - tests (read from the run): 9 failed, 5 passed in 1.84s
  ```text
              )
              return

  >       assert response.get("status") == "invalid_program", (
              f"a program in which {sorted(on_a_cycle)} can reach themselves was "
              f"accepted: {response}. Source:\n{source}\nRefuse every program whose "
              "dependency graph has a cycle."
          )
  E       AssertionError: a program in which ['task0'] can reach themselves was accepted: {'operation': 'check', 'status': 'completed', 'claim': {'kind': 'static_check', 'scope': 'this input'}, 'source_digest': '94be04c44c0659c30fafef5f900be78c7e84ae5499383dcb5cdbc4f4c42dd8df', 'diagnostics': []}. Source:
  E         (defn task0
  E           (sig ((n Int)) -> Int ! pure)
  E           (ensures (= result (task0 n)))
  E           (examples (example (task0 1) => 1))
  E           n)
  E
  E         Refuse every program whose dependency graph has a cycle.
  E       assert 'completed' == 'invalid_program'
  E
  E         - invalid_program
  E         + completed
  E       Failing test case: test_a_program_is_refused_exactly_when_its_calls_form_a_cycle(
  E           graph=(
  E               1,
  E               [[False]],  # or any other generated value
  E               [[True]],
  E           ),
  E       )

  tests/properties/test_f2_call_graph_cycles.py:137: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f2_b1_self_calling_function_is_refused.py::test_a_function_that_calls_itself_is_refused_and_the_refusal_names_it
  FAILED tests/acceptance/test_f2_b2_mutually_calling_functions_are_refused.py::test_two_functions_that_call_each_other_are_refused_and_both_are_named
  FAILED tests/acceptance/test_f2_b3_contract_cycle_is_refused.py::test_a_cycle_that_runs_only_through_a_contract_clause_is_refused
  FAILED tests/acceptance/test_f2_b4_evaluating_a_cyclic_program_refuses_without_crashing.py::test_evaluating_a_function_of_a_cyclic_program_is_refused_in_json
  FAILED tests/acceptance/test_f2_b4_evaluating_a_cyclic_program_refuses_without_crashing.py::test_running_the_declared_examples_of_a_cyclic_program_is_refused_in_json
  FAILED tests/acceptance/test_f2_b5_examples_naming_their_own_function_are_accepted.py::test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself
  FAILED tests/acceptance/test_f2_char1_shipped_programs_still_check.py::test_the_hour_clock_still_passes_unlike_a_copy_whose_guard_calls_itself
  FAILED tests/acceptance/test_f2_char1_shipped_programs_still_check.py::test_the_reservation_example_still_passes_unlike_a_copy_whose_guard_calls_itself
  FAILED tests/properties/test_f2_call_graph_cycles.py::test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
  9 failed, 5 passed in 1.84s
  ```

## 2. design: Find the owners and design the change (revision 1)

- **owners**:
  - which whole programs are invalid, and with which diagnostics => src/prova/checker.py check_program, which already owns every whole-program rule (unknown types, type agreement, match exhaustiveness)
  - what a function depends on: the calls in its body and in its contract clauses => new: src/prova/checker.py _callees_of; no unit collects callees today, _infer passes a call by to type it and keeps nothing
  - finding the sets of functions that depend on each other => new: src/prova/checker.py _cycles_in; no graph search exists in this repository
  - what one reported cycle is, and how its members are named and ordered => new: src/prova/checker.py Cycle, a value object beside Diagnostic in the module that owns the rule
  - the shape of a diagnostic (category, reason, location, and now the cycle it names) => src/prova/checker.py Diagnostic, extended with one optional field in the same way location is already optional
  - the published vocabulary of diagnostic categories => src/prova/service.py DIAGNOSTIC_CATEGORIES, which the discover operation answers with
  - turning a diagnostic into a JSON entry => src/prova/service.py _diagnostic_dict, which already decides which optional fields appear
  - the order in which an operation checks a program before it evaluates anything => src/prova/service.py _run_check, _run_examples and _run_evaluate, all unchanged: each already checks first
  - what a function declares: signature, requires, ensures, examples, body => src/prova/syntax.py Function, read by the new rule and not changed
  - printing one JSON response and exiting 0 => src/prova/__main__.py, unchanged: it already exits 0 for every answered request
- **reuse_decision**: Reused: check_program keeps its place as the single owner of whole-program rules, so the new rule is one more pass inside it rather than a second checker a caller must remember to run; Diagnostic gains one optional field, exactly as location is already optional, so the wire adapter keeps one way to render a diagnostic; _diagnostic_dict stays the only place that turns a diagnostic into JSON; the three operations keep their existing order, in which the program is checked before anything is evaluated, which is why criterion 4 needs no change to the evaluator at all. Created new: Cycle, _callees_of, _calls_in and _cycles_in. No existing owner fits, because nothing in this repository collects the callees of a function or searches a graph: _infer visits a call to type it and keeps no record of it. Rejected alternative: collecting edges inside _infer while it already walks every expression. It would guarantee the two agree on what a call is, but it threads an accumulator through twenty recursive call sites of a function whose single responsibility is typing, and it would mix a whole-program rule into a per-expression one. The cost of the choice taken is a second walk of the same expression trees, paid for by walking the node structure itself rather than a list of node kinds, so a kind added later cannot escape either walk.
- **paradigm**: fp
- **boundaries**:
  - the JSON response boundary, owned by src/prova/service.py: the new category and the new cycle field become public there; the checker owns the rule and never decides the wire shape
  - the parsed-program boundary, owned by src/prova/syntax.py: the checker reads the already parsed Program and never re-reads or re-parses source text
  - the process boundary, owned by src/prova/__main__.py: one JSON response on stdout and exit 0, unchanged by this work, which is what makes a refused program exit normally
  - the dependency direction stays inward: service depends on checker, checker depends on syntax, and nothing in the checker knows about JSON, stdin or exit codes
- **domain_types**:
  - Cycle (new, src/prova/checker.py): an immutable value object holding the functions of one cycle in the declaration order of the program. Its constructor refuses an empty member list, so a reported cycle that names no function cannot be built. It owns the sentence that describes itself and the names it publishes.
  - Diagnostic (changed, src/prova/checker.py): gains one optional field cycle, defaulting to none, in the same shape as the existing optional location. Every existing construction site is unchanged.
  - the dependency graph itself stays an ordinary mapping from function name to the names it calls, built and consumed inside _cycles_in. It is not a published type because no caller outside that function reads it, and a type there would repeat what Cycle already carries.
- **invariants**:
  - INV1 | Every reported cycle names at least one function: a cycle with no member cannot be constructed | witness=src/prova/checker.py:Cycle | bypass=none
  - INV2 | Every call written in a body or in a contract clause is an edge of the graph, including calls inside expression kinds added to the grammar later, because the walk is over the node structure itself and not over a list of node kinds | witness=src/prova/checker.py:_calls_in | bypass=a call reached through a node that is neither a dataclass nor a tuple nor a list would be missed; the grammar in syntax.py has no such node today
  - INV3 | A declared example never contributes an edge: only the body and the contract clauses of a function are walked, and an examples clause holds values rather than expressions | witness=src/prova/checker.py:_callees_of | bypass=none
  - INV4 | The cycle search itself never recurses on the size of the program: it is iterative, so a program with more functions than the Python recursion limit is refused rather than ending the process the way the defect this feature removes does | witness=src/prova/checker.py:_cycles_in | bypass=expression depth is still walked recursively, in _infer and in _calls_in; that limit is older than this change and is not touched by it
  - INV5 | The report depends on the program alone: the members of a cycle are listed in declaration order and the cycles in the declaration order of their first member, never in the iteration order of a set | witness=src/prova/checker.py:_cycles_in | bypass=none
  - INV6 | A call to a function the program does not declare is not an edge: it is already reported as an unbound name, and the graph holds declared functions only | witness=src/prova/checker.py:_callees_of | bypass=none
- **prefactoring**: no
- **prefactoring_reason**: The code this change touches already separates the owner of the rule (checker) from the adapter that publishes it (service), and check_program is already a sequence of independent passes over the same parsed program, so the new pass is added beside the others without restructuring any of them. No existing function changes behaviour, changes shape or needs a seam opened for this work. One pre-existing matter is noted and deliberately not repaired here: a diagnostic category is a plain string in a closed published vocabulary, which a type could own; changing that would touch every diagnostic and every test that reads one, far outside this request, so it is reported rather than fixed.

## 3. craft: Craft the change (revision 1)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 65.813s
  - tests (read from the run): 788 passed in 65.71s
  - slowest: 4.54s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 3.00s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 2.65s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 2.26s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 1.88s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.32s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.10s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.04s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 0.99s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 0.90s call tests/properties/test_i1_s4_p7_pinned_snapshots.py::test_p7_protected_snapshots_agree_before_after_construction_and_after_execution
  ```text
  ........................................................................ [  9%]
  ........................................................................ [ 18%]
  ........................................................................ [ 27%]
  ........................................................................ [ 36%]
  ........................................................................ [ 45%]
  ........................................................................ [ 54%]
  ........................................................................ [ 63%]
  ........................................................................ [ 73%]
  ........................................................................ [ 82%]
  ........................................................................ [ 91%]
  ....................................................................     [100%]
  ============================= slowest 10 durations =============================
  4.54s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  3.00s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  2.65s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  2.26s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  1.88s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.32s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.10s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.04s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  0.99s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  0.90s call     tests/properties/test_i1_s4_p7_pinned_snapshots.py::test_p7_protected_snapshots_agree_before_after_construction_and_after_execution
  788 passed in 65.71s (0:01:05)
  ```
- **scorecard**: `uv run pytest -q tests --collect-only -W error` exited 0 in 0.302s
  ```text
  tests/unit/test_checker_match_pattern_types.py::test_pattern_constructor_of_unrelated_type_to_scrutinee_is_rejected
  tests/unit/test_checker_match_pattern_types.py::test_pattern_constructor_matching_scrutinee_type_is_accepted
  tests/unit/test_checker_match_pattern_types.py::test_pattern_with_too_many_subpatterns_is_rejected
  tests/unit/test_checker_match_pattern_types.py::test_pattern_with_too_few_subpatterns_is_rejected
  tests/unit/test_checker_match_pattern_types.py::test_pattern_with_exactly_the_declared_subpatterns_is_accepted
  tests/unit/test_checker_match_pattern_types.py::test_int_match_without_catch_all_is_rejected_as_non_exhaustive
  tests/unit/test_checker_match_pattern_types.py::test_int_match_with_variable_catch_all_is_accepted
  tests/unit/test_checker_match_pattern_types.py::test_int_match_with_wildcard_catch_all_is_accepted
  tests/unit/test_checker_match_pattern_types.py::test_bool_match_covering_true_and_false_is_accepted
  tests/unit/test_checker_match_pattern_types.py::test_bool_match_missing_false_is_rejected_as_non_exhaustive
  tests/unit/test_checker_match_pattern_types.py::test_unit_pattern_covers_a_unit_scrutinee
  tests/unit/test_checker_match_pattern_types.py::test_union_match_covering_every_variant_is_accepted
  tests/unit/test_checker_match_pattern_types.py::test_union_match_missing_a_variant_is_rejected_as_non_exhaustive
  tests/unit/test_checker_match_pattern_types.py::test_union_payload_patterns_must_be_recursively_exhaustive
  tests/unit/test_checker_match_pattern_types.py::test_non_exhaustive_match_in_a_branch_no_example_reaches_is_rejected
  tests/unit/test_checker_match_pattern_types.py::test_literal_pattern_of_a_type_other_than_the_scrutinee_is_rejected
  tests/unit/test_checker_match_pattern_types.py::test_wrong_arity_pattern_reports_only_arity_mismatch
  tests/unit/test_checker_match_pattern_types.py::test_literal_subpattern_disagreeing_with_a_constructor_field_type_is_rejected
  tests/unit/test_checker_match_pattern_types.py::test_literal_subpattern_agreeing_with_a_constructor_field_type_is_accepted
  tests/unit/test_checker_match_pattern_types.py::test_unit_literal_pattern_against_a_non_unit_scrutinee_is_rejected
  tests/unit/test_checker_match_pattern_types.py::test_multi_column_record_pattern_with_one_uncovered_column_is_rejected
  tests/unit/test_checker_match_pattern_types.py::test_multi_column_record_pattern_covering_every_combination_is_accepted
  tests/unit/test_checker_return_and_contract_types.py::test_body_type_disagreeing_with_declared_return_type_is_rejected
  tests/unit/test_checker_return_and_contract_types.py::test_requires_clause_that_is_not_bool_is_rejected
  tests/unit/test_checker_return_and_contract_types.py::test_ensures_clause_that_is_not_bool_is_rejected
  tests/unit/test_checker_return_and_contract_types.py::test_matching_body_and_bool_contracts_are_accepted
  tests/unit/test_evaluator_field_access.py::test_field_access_on_union_variant_resolves_its_own_field
  tests/unit/test_evaluator_field_access.py::test_field_access_on_record_type_resolves_via_the_type_declaration
  tests/unit/test_evaluator_field_access.py::test_field_access_on_the_second_union_variant_is_not_matched_by_the_first
  tests/unit/test_evaluator_field_access.py::test_field_access_selects_the_declared_field_by_name_not_by_position_zero
  tests/unit/test_evaluator_field_access.py::test_field_access_resolves_the_record_type_when_a_union_variant_shares_its_name
  tests/unit/test_evaluator_field_access.py::test_field_access_on_a_constructor_naming_no_declared_type_reports_a_diagnostic_instead_of_crashing
  tests/unit/test_evaluator_field_access.py::test_constructor_call_naming_no_declared_type_in_a_function_body_reports_a_diagnostic_instead_of_crashing
  tests/unit/test_service_discover.py::test_discover_reports_partial_core_0_profile
  tests/unit/test_service_discover.py::test_discover_reports_each_operation_availability
  tests/unit/test_service_discover.py::test_advertised_availability_matches_what_the_service_answers
  tests/unit/test_service_discover.py::test_discover_lists_diagnostic_categories_and_resource_limits
  tests/unit/test_service_discover.py::test_discover_makes_no_verification_proof_or_build_claim

  788 tests collected in 0.20s
  ```
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this environment and is declared in no shell profile; jev_decide.py run from a shell command exits 3 (service unavailable). The open choices of this run (category name, diagnostic shape, exit code) were decided locally and settled by the owner at the pause after the oracle step.

## 4. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the change is exactly what the design recorded: one more pass inside check_program (src/prova/checker.py:132), the four new units it named, one category and one field in service.py. No alternative was taken and nothing outside the named owners changed.
  - D2: pass - the new category string has one owner, checker.CYCLIC_DEPENDENCY, which service.py imports into its published vocabulary rather than repeating the literal; the sentence a cycle carries is built in one place, Cycle.diagnostic; the test fixture reuses the existing reservation_source extractor instead of a second copy.
  - D3: pass - the direction stays inward: checker imports syntax only, service imports checker, and nothing in checker mentions JSON, stdin or an exit code. The wire shape of the new field is decided only in service._diagnostic_dict (src/prova/service.py:111).
  - D4: pass - src/prova/checker.py:49 - a cycle that names no function cannot be built: the constructor refuses an empty member list with a reason that says what to build it from, and tests/unit/test_checker_cycle_value.py:21 observes that refusal while its sibling builds a real one. The members stay a tuple of names rather than a bare list, and the decision whether a component is a cycle is a named function, not a boolean flag passed around.
  - D5: pass - src/prova/checker.py:39 - the one class added is a small immutable value object with a single instance variable and no setter or getter-and-branch: callers tell it to describe itself or to build its diagnostic. No abbreviation, one responsibility, no stateless utility class. The declared paradigm is fp, so the rest of the change is small pure functions.
  - D6: pass - no pattern was introduced for its own sake. The search is a standard iterative depth-first strongly-connected-components walk, named for what it finds rather than for the algorithm, and it is the only place that knows the graph exists.
  - D7: pass - the words are the words of the language the tool checks: cycle, members, callees, declared function, contract clause, example. Nothing is called a manager, helper or graph node, and Cycle is the owner of what a cycle knows about itself.
  - D8: pass - no infrastructure entered the checker: it reads an already parsed program and returns diagnostics. Reading stdin, writing stdout and the exit code stay in __main__.py, which this change does not touch at all.
  - D9: pass - tests/acceptance/_f2_cycle_fixtures.py:165 - every acceptance test drives the installed prova command over its real JSON surface and imports nothing from src/prova; the property tests call the public service entry in process, as the sibling property tests in this repository already do. Only the two unit tests for the constructor touch checker directly, which the test mandate allows for a non-exported module and which this repository already does in tests/unit/test_checker_*.py.
  - D10: pass - every new test name is a sentence about what a user gets: a function that calls itself is refused and the refusal names it; two functions that call each other are refused and both are named; the hour clock still passes unlike a copy whose guard calls itself. No process id, no layer term, no production symbol.
  - D11: pass - one fixture module owns the programs, the runner and the two readers of a response; no test re-implements them. A new runner was written rather than reusing the existing run_check because that one asserts the exit code is 0 and discards standard error, which is exactly what criterion 4 has to observe.
  - D12: pass - tests/properties/test_f2_call_graph_cycles.py:115 - the law is stated over every call graph of one to three functions with a body edge and a contract edge drawn per ordered pair, bounded and derandomized. Its oracle is computed by transitive closure over the generated edges (line 81), which is not the search the tool runs, and every generated function declares an example naming itself, so the exclusion of example calls is exercised in every case.
  - D13: pass - measured, not guessed: the eight new files ran nine times in a row, 16 passed each time, median 0.98s and slowest run 1.02s; the slowest single test is 0.44s (the law that needs two processes to make a hash-order fault visible) and every other new test is at or under 0.05s. The whole suite is 788 passed in 65.29s against 772 in 67.90s before.
  - D14: pass - no two new tests assert the same pair. Each refusal test observes a different shape (self-call, mutual pair, contract-only) and each is paired with the one control that differs from it by a single call; the property adds the shapes no table covers and repeats none of the fixed examples.
  - D15: pass - tests/acceptance/test_f2_b1_self_calling_function_is_refused.py:42 - every new assertion says what failed, why it matters and what must become true, and quotes the response it saw. The diagnostic the product emits does the same: it names the functions, names the rule they break and says to remove one of the calls that closes the cycle; the remedy was run, and the control programs that apply it are accepted (src/prova/checker.py:66).
  - D16: pass - no model, and the reason names what is absent rather than calling the problem simple: no shared state, no protocol with more than one step, no concurrency and no crash window. The rule is a pure function of one immutable parsed program, and the generated property observes it directly in the ordinary suite. (quint is also not installed here, which is recorded as a fact, not as the reason.)
  - D17: fixed:two documents were made false by this change and both were corrected in the same change. The oracle document still listed three open questions the Owner had answered; it now records the answers. The conformance trace recorded this defect as present; a dated note under it records the fix with the probe counts measured before and after (31 and 34 of 53), while its table is left as measured at the commit its own header pins. Every number in the feature documents was re-measured for this record rather than copied.
- **independent_review**:
  - REV1 | reviewer=none-assigned | findings=No independent review was performed: this run has one executor, no reviewer was assigned to it, and the role may not review its own work, so no finding of an independent reader is recorded here. What an independent reader still has to judge, with the evidence already in the repository: whether the three deliberate breaks cover the rule rather than only its reporting; whether refusing a cyclic program at check time changes any promise another feature depends on; whether the new diagnostic sentence reads well to someone who did not write it. | resolution=Outstanding, and reported as outstanding rather than filled in by the executor. The handoff carries it to the reviewer and the blind examiner the delivery still owes, with the commits, the commands and their observed output, so the review can start from evidence rather than from this record.

## 5. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
- **not_verified**:
  - No independent review: this run had one executor and no reviewer was assigned, and the role may not review its own work. The self-review dimensions were answered by the executor alone, which is not a substitute.
  - The blind examination the delivery owes has not run.
  - The exclusion of declared examples from the graph is not guarded by anything a mutation could break: an examples clause holds values rather than expressions, so pointing the rule at the examples would change no answer. That half of criterion 5 is structural, and the test that covers it would also pass if the exclusion were written differently.
  - Expression depth is still walked recursively, by the existing type pass and by the new call walk. A deep enough single expression still ends the process. That limit is older than this change and was not measured, reproduced or repaired here; only the new search over the number of functions was made iterative.
  - No lint or type checker exists in this repository, so the mechanical check recorded is a collection of every test with warnings as errors. Nothing checked formatting, typing or complexity, here or on the pre-feature tree.
  - Jev was not consulted: TYPESAFE_API_KEY is absent from the environment and declared in no shell profile, and the client exits 3. Every judgment in this run is the executor's own, with the three user-visible choices settled by the Owner.
  - No formal model was written. The reason recorded is the absence of shared state, a multi-step protocol, concurrency or a crash window, not the absence of a tool; quint is also not installed here, which was not relied on as the reason.
  - The conformance trace table was not re-scored. It is pinned by its own header to an older commit; only a dated note under its defect 1 records this fix, with the probe counts before and after. The six interlocking row counts in that table still describe the commit it names.
  - Performance was not measured beyond test duration. The new pass walks every body and contract a second time and runs a search over the declared functions; no program large enough to show a cost was tried, and no speed claim is made.
  - Behaviour of this branch merged with the delivery running in the other worktree was not tried. Both were developed apart, and only this worktree was run.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit f2ff7f9f65334382061bbe698b840fed37d3bfc0
  - no checks declared

## Not backed by the diff

- A program whose functions depend on themselves is now refused when it is checked, and the refusal names the functions of each cycle, both in a sentence and in a machine-readable field.: a guarantee names no test function of the change
- Before this change such a program passed check and then ended the process with an uncaught RecursionError, exit 1 and no answer at all; now every operation answers with a diagnostic and exits 0, because check, examples and evaluate already check a program before evaluating anything.: a guarantee names no test function of the change
- The rule reads the calls written in bodies and contract clauses and never the declared examples, so a function whose examples name it stays accepted; the hour clock and the reservation example stay accepted, and each of those tests also checks a copy of the same program with one guard replaced by a self-call, so acceptance cannot pass by the rule never running.: a guarantee names no test function of the change
- Three deliberate breaks of the new code were made and each was caught by a different test, then restored.: a guarantee names no test function of the change
- The repository's own SPEC probe script agrees on the three clauses this feature targets and disagreed on all three before.: a guarantee names no test function of the change
- What the next reader must know: no independent review has been done, and the examiner still owes its pass; the two naming choices a caller sees (the category and the field) were settled by the Owner before any code was written.: a guarantee names no test function of the change
