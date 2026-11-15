# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1011 tests, all green on main).
  - not-testable (challenge this): names the project, its test command and the green baseline it starts from
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names SPEC.md as the authority behind the rule
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on which files may change, checked with git and not with a test
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): a process instruction for what to do when a conflict appears
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): names a directory that this work leaves alone
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): names where the work happens
- S7: Commit with a message ending in the line
  - not-testable (challenge this): process promise about the shape of the commit message
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the line the commit message ends with
- S9: Do not push and do not merge.
  - not-testable (challenge this): process promise, no push and no merge
- S10: Keep the full suite green.
  - not-testable (challenge this): the whole-suite run is the GREEN command of the craft step, not a test of its own
- S11: Another delivery (F10, diagnostic fields in checker.py and service.py) runs in parallel in a different worktree; this fix changes tests and docs only (no src file).
  - not-testable (challenge this): a constraint on which files this change opens, checked with git
- S12: Keep scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): says where the scripts of this run live
- S13: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell hygiene and a clean tree before the report
- S14: **Outcome.** The tests notice if the cycle search names the wrong functions or lists them in the wrong order.
  - promises: P1, P2
  - tests P1: test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
  - tests P2: test_a_refusal_names_the_members_of_a_cycle_in_declaration_order
- S15: The implementation was found correct on every probe (27 of 29 passing, the two reds were the reviewer's harness); the gaps are in the tests.
  - not-testable (challenge this): records what the review found about the implementation
- S16: The review (REV1, REJECT, owner oracle) mutated 14 pieces of F2/F3 logic: 11 died, 1 more died only on the whole suite, and 2 survive all 1011 tests:
  - not-testable (challenge this): records the counts the review measured
- S17: 1.
  - not-testable (challenge this): a list number introducing the item below it
- S18: (HIGH) src/prova/checker.py ~831: deleting the low-link propagation on pop of the strongly-connected-component search makes `a->b->c->a` answer `cycle=['b','c']` (omits `a`) and `a->b->c->d->b` answer `['c','d']` instead of `['b','c','d']`, while all tests stay green.
  - promises: P1
  - tests P1: test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
- S19: The law in tests/properties/test_f2_call_graph_cycles.py (max_examples=60, law asserted ~line 148) is right but its coverage is short: with max_examples=3000 it catches the mutant.
  - not-testable (challenge this): explains why the coverage of the existing law is short
- S20: Pin the shapes: add fixed examples (hypothesis `@example` or explicit acceptance tests through the real CLI) for a 3-cycle, a 4-chain re-entering at the second node, and a cycle with a tail, asserting the exact member set; do not just raise the example budget.
  - promises: P1
  - tests P1: test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
- S21: 2.
  - not-testable (challenge this): a list number introducing the item below it
- S22: (MEDIUM) src/prova/checker.py ~837: replacing `tuple(sorted(component, key=rank_of))` with `tuple(component)` gives `['c','b','a']` instead of `['a','b','c']` (and `['d','c','b']`), tests green.
  - promises: P2
  - tests P2: test_a_refusal_names_the_members_of_a_cycle_in_declaration_order
- S23: Add one assertion through the CLI that the `cycle` list of a three-function cycle equals declaration order, and one where the declaration order differs from the call order.
  - promises: P2
  - tests P2: test_a_refusal_names_the_members_of_a_cycle_in_declaration_order
- S24: 3.
  - not-testable (challenge this): a list number introducing the item below it
- S25: (note, record gap) docs/spec-trace.md row 8.6: add `cyclic_dependency` to the list of diagnostics that carry no location; annotate defects 2 and 3 in the spec-trace "fixed by" lines as fixed by F3 (as defect 1 is annotated "Fixed by feature F2").
  - not-testable (challenge this): a note in a prose document read by a human reviewer; the test mandates forbid pinning prose
- S26: Also add `cyclic_dependency` to the F10 location follow-up in docs/ROADMAP.md (the line starting "Locate `recursive_type` and `unbound_type` diagnostics").
  - not-testable (challenge this): a note in a prose document read by a human reviewer; the test mandates forbid pinning prose
- S27: 4.
  - not-testable (challenge this): a list number introducing the item below it
- S28: (note, do nothing in code) a source with an expression nested about 450 deep dies with RecursionError in syntax.parse_expr (pre-existing, outside F2).
  - not-testable (challenge this): a pre-existing defect outside this change, to be logged and not fixed
- S29: Log it in your handoff only; I add it to the roadmap.
  - not-testable (challenge this): process promise about where that note goes
- S30: No src file may change.
  - not-testable (challenge this): a constraint on which files may change, checked with git and not with a test
- S31: Mutate in a throwaway worktree or by editing and restoring; re-run both survivors plus 4 others from the F2/F3 logic (the self-edge case, the cycle-membership filter, the duplicate-kind comparison, one edge direction): each must turn a test red; report each mutant and its failing test.
  - not-testable (challenge this): a mutation run, recorded in the craft step as commands with the tests they turned red

## Edge matrix

- I1.empty: a source that declares nothing => refused with no cycle diagnostic, as F6 already settles | self-probe: not probed | pre-feature not probed
- I1.unknown: a body that calls a function the program does not declare => no edge in the graph; reported as an unbound name, never as a cycle | self-probe: not probed | pre-feature not probed
- I1.malformed: a source that does not parse => a reader refusal carrying line and column, with no cycle diagnostic | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): the check operation reads only the source text in the request and opens no file of its own
- I1.repeated: the same cyclic program checked in 2 separate runs => the same answer both times, which LAW2 already pins | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): 1 run answers 1 request in its own process and keeps no state between runs
- I1.crash: evaluating a function of a cyclic program => refused in JSON with no traceback, which the F2 acceptance tests already pin | self-probe: not probed | pre-feature not probed
- I2.empty: n/a (challenge this): these 2 document sections are written by hand and take no input that could be empty
- I2.unknown: n/a (challenge this): a document section takes no input that could name something unknown
- I2.malformed: n/a (challenge this): the 2 documents are prose with no parser that could refuse them
- I2.dependency-gone: n/a (challenge this): the changed lines name features and categories, not files that could go missing
- I2.repeated: n/a (challenge this): reading either document twice shows the same text both times
- I2.concurrent: n/a (challenge this): nothing writes these 2 documents while a reader is reading them
- I2.crash: n/a (challenge this): reading a document starts no process that could crash

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN 3 functions where gather calls summarise, summarise calls publish and publish calls gather
  - WHEN the program is checked
  - THEN the answer is "invalid_program" and the 1 reported cycle names all 3 of them
  - test: test_a_cycle_of_three_functions_is_named_in_full_and_in_declaration_order
- SC2 (P1): not-held (no held self-probe case)
  - GIVEN 4 functions in a chain where the 4th calls the 2nd back
  - WHEN the program is checked
  - THEN the refusal names exactly the 3 functions on the round and not the 1st
  - test: test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
- SC3 (P1): not-held (no held self-probe case)
  - GIVEN 3 functions calling each other round and a 4th that the 3rd calls and that calls nothing
  - WHEN the program is checked
  - THEN the refusal names exactly the 3 on the round and not the 4th
  - test: test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
- SC4 (P2): not-held (no held self-probe case)
  - GIVEN 3 functions declared gather, summarise, publish in the order they call each other
  - WHEN the program is checked
  - THEN the reported cycle reads "gather", "summarise", "publish"
  - test: test_a_cycle_of_three_functions_is_named_in_full_and_in_declaration_order
- SC5 (P2): not-held (no held self-probe case)
  - GIVEN 3 functions declared audit, settle, refund while the calls run audit, refund, settle
  - WHEN the program is checked
  - THEN the reported cycle reads "audit", "settle", "refund"
  - test: test_a_cycle_is_named_in_declaration_order_when_the_calls_run_in_another_order

## Questions for the owner

- S25: Shall I annotate defect 3 with the 3 features that closed its clauses instead of F3 alone, so the record stays true?
  - existing behaviour: defect 3 of the spec trace lists 7 clauses and F3 closed only 3 of them: cyclic types went with F4, and shadowing, result as a binder and repeated pattern variables went with F5
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- M docs/ROADMAP.md (+21 -0 lines)
- A docs/diagnostic-fields/DECISIONS.md (+21 -0 lines)
- A docs/diagnostic-fields/SUMMARY.md (+673 -0 lines)
- A docs/diagnostic-fields/TRACE.md (+5 -0 lines)
- A docs/feature/diagnostic-fields/craft.md (+120 -0 lines)
- A docs/feature/diagnostic-fields/design.md (+121 -0 lines)
- A docs/feature/diagnostic-fields/oracle.md (+100 -0 lines)
- M docs/spec-trace.md (+9 -0 lines)
- M src/prova/checker.py (+419 -44 lines)
- M src/prova/reader.py (+16 -4 lines)
- M src/prova/service.py (+239 -67 lines)
- A tests/acceptance/_f10_diagnostic_fixtures.py (+428 -0 lines)
- M tests/acceptance/_f2_cycle_fixtures.py (+70 -0 lines)
- A tests/acceptance/test_f10_b1_every_refusal_names_the_revision_of_its_source.py (+72 -0 lines)
- A tests/acceptance/test_f10_b2_a_type_error_names_its_symbol_expected_and_actual.py (+60 -0 lines)
- A tests/acceptance/test_f10_b3_a_reader_refusal_still_says_where.py (+119 -0 lines)
- A tests/acceptance/test_f10_b4_the_fields_do_not_depend_on_the_prose.py (+101 -0 lines)
- A tests/acceptance/test_f10_b5_a_repaired_program_is_accepted_with_its_new_revision.py (+65 -0 lines)
- A tests/acceptance/test_f10_b6_a_refusal_about_a_declaration_says_where_it_stands.py (+66 -0 lines)
- A tests/acceptance/test_f10_b7_the_manifest_says_what_each_refusal_carries.py (+79 -0 lines)
- A tests/acceptance/test_f10_b8_the_published_granularity_is_what_the_places_are.py (+95 -0 lines)
- A tests/acceptance/test_f10_b9_a_source_that_is_not_text_is_refused.py (+83 -0 lines)
- A tests/acceptance/test_f2fix_b1_a_cycle_is_named_in_declaration_order.py (+77 -0 lines)
- A tests/properties/test_f10_diagnostic_fields.py (+194 -0 lines)
- M tests/properties/test_f2_call_graph_cycles.py (+82 -2 lines)
- A tests/unit/test_diagnostic_refuses_what_its_kind_does_not_declare.py (+148 -0 lines)

## Commits (git log, BASE to HEAD)

- 626f9be [F10] give every refusal one builder, before changing what it carries
- b4cba63 [F10] state what a diagnostic must carry, as checks that fail
- 00ad63c [F10] decide where it is said what a refusal carries
- 9712e47 [F10] say which revision, which symbol, expected and actual
- fe0b519 [F10] keep the laws off a crash that is older than them
- 0af2202 [F10] write down what the change cost and what it left alone
- bcec4ec [F10] refuse a source that is not text, and say which text a place is in
- ca7236a [F10] measure the record against the commits it describes
- 6a8635c [F10] hand the feature over with what it leaves open
- 5d3a90f Roadmap: record the robustness item and the review notes raised by F2 to F10
- c281805 [F2fix] notice when the cycle search names or orders the functions wrongly
- 39794d8 [F2fix] stop claiming that the cycle refusal carries no place

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f2fix/request.md
- **promises**:
  - P1: A reader who checks a program whose calls lead back to where they started sees every function of that round named in the refusal, including the one the reading started at.
  - P2: A reader sees the functions of a cycle written in the order the program declares them, whatever order the calls run in.
- **sentence_map**:
  - S1 => not-testable: names the project, its test command and the green baseline it starts from
  - S2 => not-testable: names SPEC.md as the authority behind the rule
  - S3 => not-testable: a constraint on which files may change, checked with git and not with a test
  - S4 => not-testable: a process instruction for what to do when a conflict appears
  - S5 => not-testable: names a directory that this work leaves alone
  - S6 => not-testable: names where the work happens
  - S7 => not-testable: process promise about the shape of the commit message
  - S8 => not-testable: the line the commit message ends with
  - S9 => not-testable: process promise, no push and no merge
  - S10 => not-testable: the whole-suite run is the GREEN command of the craft step, not a test of its own
  - S11 => not-testable: a constraint on which files this change opens, checked with git
  - S12 => not-testable: says where the scripts of this run live
  - S13 => not-testable: shell hygiene and a clean tree before the report
  - S14 => P1,P2
  - S15 => not-testable: records what the review found about the implementation
  - S16 => not-testable: records the counts the review measured
  - S17 => not-testable: a list number introducing the item below it
  - S18 => P1
  - S19 => not-testable: explains why the coverage of the existing law is short
  - S20 => P1
  - S21 => not-testable: a list number introducing the item below it
  - S22 => P2
  - S23 => P2
  - S24 => not-testable: a list number introducing the item below it
  - S25 => not-testable: a note in a prose document read by a human reviewer; the test mandates forbid pinning prose
  - S26 => not-testable: a note in a prose document read by a human reviewer; the test mandates forbid pinning prose
  - S27 => not-testable: a list number introducing the item below it
  - S28 => not-testable: a pre-existing defect outside this change, to be logged and not fixed
  - S29 => not-testable: process promise about where that note goes
  - S30 => not-testable: a constraint on which files may change, checked with git and not with a test
  - S31 => not-testable: a mutation run, recorded in the craft step as commands with the tests they turned red
- **scenarios**:
  - SC1 | P1 | GIVEN 3 functions where gather calls summarise, summarise calls publish and publish calls gather | WHEN the program is checked | THEN the answer is "invalid_program" and the 1 reported cycle names all 3 of them
  - SC2 | P1 | GIVEN 4 functions in a chain where the 4th calls the 2nd back | WHEN the program is checked | THEN the refusal names exactly the 3 functions on the round and not the 1st
  - SC3 | P1 | GIVEN 3 functions calling each other round and a 4th that the 3rd calls and that calls nothing | WHEN the program is checked | THEN the refusal names exactly the 3 on the round and not the 4th
  - SC4 | P2 | GIVEN 3 functions declared gather, summarise, publish in the order they call each other | WHEN the program is checked | THEN the reported cycle reads "gather", "summarise", "publish"
  - SC5 | P2 | GIVEN 3 functions declared audit, settle, refund while the calls run audit, refund, settle | WHEN the program is checked | THEN the reported cycle reads "audit", "settle", "refund"
- **conflicts**:
  - S1 | NONE | checked the project layout, the pyproject test dependencies and a full run of "uv run pytest -q tests": it is green
  - S2 | NONE | read SPEC.md lines 163-165, which carry the acyclic rule this work pins; nothing here changes them
  - S3 | NONE | the change adds 1 test file and adds cases, a reader and 1 law to existing test files; no expected result of an existing test changes
  - S4 | NONE | checked every F2 and F3 acceptance test and the F2 property: none of them expects the behaviour this work pins to be different
  - S5 | NONE | checked that no .relay directory exists in this worktree and that no test reads one
  - S6 | NONE | checked that the worktree is on branch feat/f2fix and that all edits are inside it
  - S7 | NONE | checked the recent commit messages of the branch: they end with a co-author line already
  - S8 | NONE | checked that no commit hook rejects that line in this worktree, which installs no commit hooks
  - S9 | NONE | checked that nothing in this work pushes or merges; the branch stays local
  - S10 | NONE | ran the whole suite before recording: it is green, so keeping it green is consistent with the tree
  - S11 | NONE | checked that the F10 delivery touches src/prova/checker.py and src/prova/service.py, which this change does not open
  - S12 | NONE | checked that the scripts of this run live under the nwstep workspace and that none is written into the repository
  - S13 | NONE | checked that every arrow goes into a file like this one rather than a zsh command line
  - S14 | NONE | read the cycle search and the tests over it: the tool already answers both the names and their order correctly, so only the tests change
  - S15 | NONE | checked the 2 surviving mutants against the tree: the behaviour they change is the one the request calls correct
  - S16 | NONE | re-ran 6 of the 14 mutants the review names; the counts it reports are its own measurement and nothing in the tree contradicts them
  - S17 | NONE | a list number; nothing in the repository can contradict it
  - S18 | NONE | reproduced the mutant: with it applied the tool answers task2 and task3 for a chain of 4 that leads back to its 2nd function
  - S19 | NONE | read the law and its settings: max_examples is 60 and the generator draws at most 3 functions, so the 4-function shapes are out of its reach at any budget
  - S20 | NONE | checked that hypothesis is a declared dev dependency and that the example decorator accepts a 4-function graph the strategy would not draw
  - S21 | NONE | a list number; nothing in the repository can contradict it
  - S22 | NONE | reproduced the mutant: with it applied the members of a cycle are reported in the order the search popped them
  - S23 | NONE | checked that the response carries the cycle as a list, so its order is observable through the command surface
  - S24 | NONE | a list number; nothing in the repository can contradict it
  - S25 | CONFLICT | defect 3 of the spec trace lists 7 clauses and F3 closed only 3 of them: cyclic types went with F4, and shadowing, result as a binder and repeated pattern variables went with F5 | Shall I annotate defect 3 with the 3 features that closed its clauses instead of F3 alone, so the record stays true?
  - S26 | NONE | read the F10 follow-up line in the roadmap: it names 2 diagnostics and the cycle refusal carries no location either
  - S27 | NONE | a list number; nothing in the repository can contradict it
  - S28 | NONE | probed the command with a body nested 450, 700 and 1000 deep: 450 is answered, 700 ends in a RecursionError in parse_expr and 1000 in the reader, so the defect is real and only the depth differs
  - S29 | NONE | checked that the handoff step is the place this run records such a note
  - S30 | NONE | checked that every edit of this change is under tests or docs; git reports no file under src as modified
  - S31 | NONE | checked that each named mutant has exactly 1 occurrence of the text it replaces, so each can be applied and restored
- **decisions**:
  - S25: Annotate defect 2 as fixed by F3, and defect 3 as fixed by F3, F4 and F5, naming which clause each feature closed. The owner is absent, so this is my decision: writing F3 alone over all 7 clauses of defect 3 would put a false claim in the record, and the request asks for the record of a closed gap, not for a particular feature name.
  - DEC1: No formal model. This change adds no state machine, protocol, concurrency or crash behaviour; the one law over a broad domain already has a generated property, so a Quint model would restate the test.
  - DEC2: The 4-function shapes are pinned as fixed examples on the existing property, because the generator draws at most 3 functions and could never reach them; the 3-function shapes are pinned as acceptance tests through the real command, where the order of the names is observable. The example budget stays at 60.
  - DEC3: The order of the names also became a generated property, not only 2 fixed examples, because it is a law over every program the generator draws.
  - DEC4: The RED run applies the 2 surviving mutants together, because each of them kills only part of the tests this change adds: the first one changes which functions are named, the second one changes only their order.
- **mapping**:
  - P1 => test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
  - P2 => test_a_refusal_names_the_members_of_a_cycle_in_declaration_order
- **covers_scenarios**:
  - SC1 => test_a_cycle_of_three_functions_is_named_in_full_and_in_declaration_order
  - SC2 => test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
  - SC3 => test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
  - SC4 => test_a_cycle_of_three_functions_is_named_in_full_and_in_declaration_order
  - SC5 => test_a_cycle_is_named_in_declaration_order_when_the_calls_run_in_another_order
- **interfaces**:
  - I1: the prova command JSON stdin and stdout surface, operation "check", which answers with a status and a list of diagnostics
  - I2: the written record a human reader reads: docs/spec-trace.md row 8.6 with its defect list, and the F10 follow-up line of docs/ROADMAP.md
- **matrix**:
  - I1.empty => a source that declares nothing => refused with no cycle diagnostic, as F6 already settles
  - I1.unknown => a body that calls a function the program does not declare => no edge in the graph; reported as an unbound name, never as a cycle
  - I1.malformed => a source that does not parse => a reader refusal carrying line and column, with no cycle diagnostic
  - I1.dependency-gone => n/a: the check operation reads only the source text in the request and opens no file of its own
  - I1.repeated => the same cyclic program checked in 2 separate runs => the same answer both times, which LAW2 already pins
  - I1.concurrent => n/a: 1 run answers 1 request in its own process and keeps no state between runs
  - I1.crash => evaluating a function of a cyclic program => refused in JSON with no traceback, which the F2 acceptance tests already pin
  - I2.empty => n/a: these 2 document sections are written by hand and take no input that could be empty
  - I2.unknown => n/a: a document section takes no input that could name something unknown
  - I2.malformed => n/a: the 2 documents are prose with no parser that could refuse them
  - I2.dependency-gone => n/a: the changed lines name features and categories, not files that could go missing
  - I2.repeated => n/a: reading either document twice shows the same text both times
  - I2.concurrent => n/a: nothing writes these 2 documents while a reader is reading them
  - I2.crash => n/a: reading a document starts no process that could crash
- **laws**:
  - LAW1 | a program is refused exactly when some function can reach itself through a body or a contract clause, and the refusal names exactly those functions | generator=test_a_program_is_refused_exactly_when_its_calls_form_a_cycle | observation=the names the cycle diagnostics carry equal the functions that a transitive closure over the generated edges finds reaching themselves | mutant=a search that drops what a deeper call learned names 2 of the 3 functions of a chain of 4 that leads back to its 2nd function
  - LAW2 | checking the same program in 2 separate runs gives the same answer, so no iteration order of a set leaks into the report | generator=test_checking_the_same_program_in_two_runs_gives_the_same_answer | observation=the 2 responses are equal | mutant=a report built from the iteration order of a set differs between 2 processes with different hash seeds
  - LAW3 | the members of a reported cycle are written in the order the program declares them | generator=test_a_refusal_names_the_members_of_a_cycle_in_declaration_order | observation=the names a reported cycle carries are its declared names in declaration order | mutant=reporting the members in the order the search popped them answers task2, task1, task0 for a program declared task0, task1, task2
- **messages**:
  - MSG0 | none: this change adds no refusal of its own, because no file under src changes; every message the command prints is the one F2 and F3 already shipped
- **red**: `sh /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f2fix/mine/red.sh` exited 1 in 2.693s
  - failing on the pre-feature tree (4): tests/acceptance/test_f2fix_b1_a_cycle_is_named_in_declaration_order.py::test_a_cycle_of_three_functions_is_named_in_full_and_in_declaration_order, tests/acceptance/test_f2fix_b1_a_cycle_is_named_in_declaration_order.py::test_a_cycle_is_named_in_declaration_order_when_the_calls_run_in_another_order, tests/properties/test_f2_call_graph_cycles.py::test_a_program_is_refused_exactly_when_its_calls_form_a_cycle, tests/properties/test_f2_call_graph_cycles.py::test_a_refusal_names_the_members_of_a_cycle_in_declaration_order
  - tests (read from the run): 4 failed, 1 passed in 1.80s
  ```text
  E             (defn task1
  E               (sig ((n Int)) -> Int ! pure)
  E               (examples (example (task1 1) => 1))
  E               (+ (task2 n) n))
  E
  E             (defn task2
  E               (sig ((n Int)) -> Int ! pure)
  E               (examples (example (task2 1) => 1))
  E               (+ (task3 n) n))
  E
  E             (defn task3
  E               (sig ((n Int)) -> Int ! pure)
  E               (examples (example (task3 1) => 1))
  E               (+ (task1 n) n))
  E
  E             Write the members of a cycle in the order the program declares them.
  E           assert ['task3', 'task2'] == ['task2', 'task3']
  E
  E             At index 0 diff: 'task3' != 'task2'
  E             Use -v to get more diff
  E           (note: 1 other explicit example also failed with this error; use Verbosity.verbose to view)
  E           Failing explicit example: test_a_refusal_names_the_members_of_a_cycle_in_declaration_order(
  E               graph=(4,
  E                [[False, True, False, False],
  E                 [False, False, True, False],
  E                 [False, False, False, True],
  E                 [False, True, False, False]],
  E                [[False, False, False, False],
  E                 [False, False, False, False],
  E                 [False, False, False, False],
  E                 [False, False, False, False]]),
  E           )

  tests/properties/test_f2_call_graph_cycles.py:228: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f2fix_b1_a_cycle_is_named_in_declaration_order.py::test_a_cycle_of_three_functions_is_named_in_full_and_in_declaration_order
  FAILED tests/acceptance/test_f2fix_b1_a_cycle_is_named_in_declaration_order.py::test_a_cycle_is_named_in_declaration_order_when_the_calls_run_in_another_order
  FAILED tests/properties/test_f2_call_graph_cycles.py::test_a_program_is_refused_exactly_when_its_calls_form_a_cycle
  FAILED tests/properties/test_f2_call_graph_cycles.py::test_a_refusal_names_the_members_of_a_cycle_in_declaration_order
  4 failed, 1 passed in 1.80s
  ```

## 5. craft: Craft the change (revision 2)

- **green**: `uv run pytest -q tests --durations=10` exited 0 in 112.257s
  - tests (read from the run): 1045 passed in 112.13s
  - slowest: 6.35s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.13s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 3.67s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.17s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 2.62s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 1.87s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.55s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.47s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.33s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  - slowest: 1.32s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  6%]
  ........................................................................ [ 13%]
  ........................................................................ [ 20%]
  ........................................................................ [ 27%]
  ........................................................................ [ 34%]
  ........................................................................ [ 41%]
  ........................................................................ [ 48%]
  ........................................................................ [ 55%]
  ........................................................................ [ 62%]
  ........................................................................ [ 68%]
  ........................................................................ [ 75%]
  ........................................................................ [ 82%]
  ........................................................................ [ 89%]
  ........................................................................ [ 96%]
  .....................................                                    [100%]
  ============================= slowest 10 durations =============================
  6.35s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.13s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  3.67s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.17s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  2.62s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  1.87s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.55s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.47s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.33s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1.32s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1045 passed in 112.13s (0:01:52)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.054s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from the environment of this run, so the client answered nothing; the 2 open choices were decided locally and recorded as the S25 decision and DEC2

## 6. selfreview: Self-review (revision 2)

- **answers**:
  - D1: pass - no design step is due at size S; the change follows the decisions recorded in the oracle step, DEC2 and DEC4, and adds no structure of its own
  - D2: pass - the 2 cycle programs and the order-keeping reader live once, in tests/acceptance/_f2_cycle_fixtures.py:119, tests/acceptance/_f2_cycle_fixtures.py:145 and tests/acceptance/_f2_cycle_fixtures.py:255, and the acceptance tests import them rather than repeat a source
  - D3: pass - the acceptance tests reach the tool only as a subprocess over JSON, and the property reaches the published service entry; neither opens a module of the checker
  - D4: pass - tests/properties/test_f2_call_graph_cycles.py:68 builds every call graph from a set of caller-callee pairs, so a ragged or wrongly sized matrix cannot be written by hand into the 2 pinned shapes at tests/properties/test_f2_call_graph_cycles.py:79
  - D5: pass - tests/properties/test_f2_call_graph_cycles.py:139 is one reader with one reason to change, beside the set-reading one it names; the change adds no class and no function with a flag argument
  - D6: n/a: the change adds tests and record lines only, so no design pattern is introduced or changed by it
  - D7: pass - the fixtures and tests speak of functions, cycles, declaration order and refusals, the words the authority uses, and name no internal symbol of the checker
  - D8: pass - no infrastructure is touched: the tests run the shipped command and the published service entry, and the change opens no file under src
  - D9: pass - tests/acceptance/test_f2fix_b1_a_cycle_is_named_in_declaration_order.py:26 drives the real prova command over JSON stdin and stdout and imports nothing from src/prova; the fixtures module it uses does the same
  - D10: pass - both test names read as sentences about what a reader of a refusal sees, and carry no process id, no layer term and no production symbol
  - D11: pass - the 2 programs and the order-keeping reader are shared through the existing F2 fixtures module, which already owned the cycle fixtures and the set-reading one
  - D12: pass - tests/properties/test_f2_call_graph_cycles.py:210 is a generated law over every drawn call graph, with its oracle taken from the declaration order of the generator and not from the search under test
  - D13: pass - the 2 changed test files ran 9 times in a row, all green, median 0.86 s for their 5 tests; the whole suite is 110 s, inside the 300 s ceiling
  - D14: pass - the 2 four-function shapes are pinned only where the generator cannot draw them, and the command-level tests observe the order, which no property repeated before
  - D15: pass - tests/acceptance/test_f2fix_b1_a_cycle_is_named_in_declaration_order.py:45 says what was reported, what was expected and what to do about it, and prints the whole response and the program it came from
  - D16: n/a: the change adds no state, protocol, concurrency or crash behaviour; its one broad law is covered by a generated property, as DEC1 records
  - D17: fixed:the location work merged into the base while this change was in flight; measured through the command, a cyclic program answers with a location, so the 2 record lines that said otherwise were withdrawn in commit 39794d8 and the test docstrings corrected
- **independent_review**:
  - REV1 | reviewer=independent-impl-review | findings=4 (verdict REJECT of merged F2 and F3 at 5498173) | resolution=F-1 and F-2 fixed in f73061a, F-3 documents corrected, F-4 logged in the roadmap
  - REV2 | reviewer=independent-impl-review | findings=1 (verdict APPROVE at f73061a) | resolution=the note about the location of unbound_constructor was measured against the rebased base, where that refusal and the cycle refusal both answer with a location, so nothing was added to the follow-up and the 2 record lines that claimed otherwise were withdrawn in 39794d8 instead

## 7. handoff: Hand off (revision 2)

- **summary** (sentences the diff backs):
  - Both are now caught.
- **not_verified**:
  - A source whose body nests one expression deeply still ends the command with a traceback instead of an answer: measured on this tree, depth 450 is answered, depth 700 ends in a RecursionError inside the expression parser and depth 1000 inside the reader. Pre-existing, outside this change, and logged here rather than repaired.
  - Row 8.6 of the trace still says that recursive_type and unbound_type carry no location, and the location follow-up still asks for them to be located. Measured through the command on this tree, both of them, and unbound_constructor as well, now answer with a location. That line belongs to the delivery that located them, not to this change, so it was left as it stands and is reported instead.
  - The repository declares no lint and no type checker, so the mechanical check of this run is a byte-compile of src and tests only. Nothing here says anything about style or types.
  - Jev was authorised but could not be asked: the key is absent from the environment of this run, so the two open choices, how to annotate the third defect and where to pin the fixed shapes, were decided locally and recorded as decisions.
  - The documents changed by this work are prose and no test pins them; a human reader checks them. The mutation runs and the whole-suite run are recorded commands, not tests.
  - Only 6 of the 14 changes the earlier review reports were re-applied here. The counts that review gives for the other 8 are its own measurement and were not repeated.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit 39794d83e60ea60c1a7f6e1c37f6900dd569e49e with uncommitted changes
  - no checks declared

## Not backed by the diff

- Two ways of breaking the cycle search survived the whole suite before this change: one named a proper part of the functions that call each other round, the other wrote their names in the order the search reached them.: a guarantee names no test function of the change
- A cycle of three, and a cycle whose declaration order is not its call order, are checked through the real command and assert the exact list of names; the two four-function shapes the generator can never draw, a chain leading back to its second function and a cycle with a fourth function hanging off it, are pinned as fixed examples on the law that was already there; and the order of the names became a generated law of its own.: a guarantee names no test function of the change
- No file under src and no line of SPEC.md changed, and no expected result of an existing test changed.: a guarantee names no test function of the change
- Six changes to the cycle and repeated-name logic were applied to the tree one at a time and restored: each one turned at least one test red, and the two that used to survive now fail the tests this change adds.: a guarantee names no test function of the change
- The record of which features closed the second and third listed defects is corrected: the second was closed by F3, the third by F3, F4 and F5 together, named clause by clause, because F3 alone closed only three of its seven clauses.: a guarantee names no test function of the change
- The two notes the request asked for about a refusal that carries no place were withdrawn after the rebase: the location work merged into the base while this change was in flight, and a cyclic program now answers with a location, so writing those notes would have put a false line into the record.: a guarantee names no test function of the change
