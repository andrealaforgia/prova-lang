# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1136 tests, all green on main).
  - not-testable (challenge this): names the project, its command and its green suite, which is context and no behaviour
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names the authority document to read, which is context and no behaviour
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a process promise about what this delivery may edit
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): a process promise about reporting a conflict to the owner
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): a process promise about a directory to leave alone
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a process promise about where the work happens
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a process promise about the commit message trailer
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the trailer line a commit message ends with
- S9: Do not push and do not merge.
  - not-testable (challenge this): a process promise about not pushing and not merging
- S10: Keep the full suite green.
  - not-testable (challenge this): a process promise kept by running the suite, with no scenario of its own
- S11: Another delivery (F11, the manifest in service.py) runs in parallel in a different worktree.
  - not-testable (challenge this): names a delivery running beside this one, which is context
- S12: F1 to F10, F13, F16, F2fix and R1 (robustness: request reader, nesting and evaluation limits, `malformed_request`, `resource_exhausted`) are on main; read how `service.py`, the table of diagnostic kinds in `checker.py` and the manifest are built now and follow that structure.
  - not-testable (challenge this): names what is on main already and which structure to follow
- S13: Keep your service.py edits small and local to ease the rebase.
  - not-testable (challenge this): a process promise about keeping one file edited narrowly
- S14: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): a process promise about where scripts are kept
- S15: Known tool rules: oracle laws must name @given property tests; design invariant witnesses must be a `class` or `def`; an independent_review resolution needs at least 20 characters; prefactor commits must come first in history; process promises go in not-testable sentences; the tool must never end in a traceback and every new request field read goes through the request reader.
  - not-testable (challenge this): rules of the recording tool, not of the product
- S16: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell quoting and a clean working tree, both process promises
- S17: **Outcome.** An agent can read the tree the compiler actually built, instead of
  - promises: P1
  - tests P1: test_a_valid_program_is_answered_with_the_tree_of_its_declarations
- S18: guessing from source text.
  - promises: P1
  - tests P1: test_a_valid_program_is_answered_with_the_tree_of_its_declarations
- S19: **Acceptance criteria**
  - not-testable (challenge this): a heading that introduces the criteria under it
- S20: 1.
  - not-testable (challenge this): the number of the first criterion, carrying no promise
- S21: Given a valid program, when `parse` runs, then the answer is a tree matching the
  - promises: P1, P7
  - tests P1: test_a_valid_program_is_answered_with_the_tree_of_its_declarations
  - tests P7: test_the_answer_says_which_source_it_is_about_and_claims_only_a_tree
- S22: published schema, with a position on every node.
  - promises: P1
  - tests P1: test_a_valid_program_is_answered_with_the_tree_of_its_declarations
- S23: 2.
  - not-testable (challenge this): the number of the second criterion, carrying no promise
- S24: Given a program with a comment, then the comment appears attached to the node
  - promises: P2
  - tests P2: test_each_comment_is_answered_on_the_declaration_written_under_it
- S25: that follows it, or to the document end.
  - promises: P2
  - tests P2: test_each_comment_is_answered_on_the_declaration_written_under_it
- S26: 3.
  - not-testable (challenge this): the number of the third criterion, carrying no promise
- S27: Given an invalid program, then `parse` refuses with the same diagnostic
  - promises: P3
  - tests P3: test_a_refused_program_is_refused_the_way_a_check_refuses_it
- S28: categories `check` would use and publishes no tree.
  - promises: P3
  - tests P3: test_a_refused_program_is_refused_the_way_a_check_refuses_it
- S29: 4.
  - not-testable (challenge this): the number of the fourth criterion, carrying no promise
- S30: Given the tree for the reservation example, then every declaration, contract
  - promises: P4
  - tests P4: test_every_example_the_source_writes_stands_in_the_tree_with_its_values
- S31: clause and example in the source appears in it.
  - promises: P4
  - tests P4: test_every_example_the_source_writes_stands_in_the_tree_with_its_values
- S32: 5.
  - not-testable (challenge this): the number of the fifth criterion, carrying no promise
- S33: Given `discover`, then `parse` is advertised available with that schema.
  - promises: P5
  - tests P5: test_reading_a_program_is_advertised_as_available
- S34: **SPEC.md** lines 81-84 (the tree schema must be fixed in fixtures), 463-470.
  - promises: P6
  - tests P6: test_the_published_source_is_answered_with_the_published_tree
- S35: **Dependencies** none; the schema choice is D7 if the Owner wants to approve it.
  - not-testable (challenge this): names the dependencies and the owner decision that covers the schema
- S36: **Size** M.
  - not-testable (challenge this): declares the size of the delivery, which is planning
- S37: **Touches** `src/prova/service.py`, `src/prova/syntax.py`,
  - not-testable (challenge this): names the files the work is expected to touch
- S38: `conformance/` fixtures, tests.
  - not-testable (challenge this): names the files the work is expected to touch
- S39: **Why it is a real expectation** `parse` is refused today
  - promises: P5
  - tests P5: test_reading_a_program_is_advertised_as_available
- S40: (`src/prova/service.py:15`, probe S2).
  - not-testable (challenge this): cites the line and the probe that observed the refusal today
- S41: Owner decision D7 (the product owner recommendation stands), as written in the roadmap:
  - not-testable (challenge this): introduces the owner decision quoted under it
- S42: **Context.** SPEC.md lines 81-84 require the canonical layout and the syntax-tree
  - promises: P6
  - tests P6: test_the_published_source_is_answered_with_the_published_tree
- S43: interchange schema fixed in conformance fixtures before `format` ships, and say
  - promises: P6
  - tests P6: test_the_published_source_is_answered_with_the_published_tree
- S44: formatting policy must not change language validity.
  - not-testable (challenge this): about formatting policy, which this delivery does not ship
- S45: **My recommendation: delegate both to me.** I will choose a layout, publish the
  - not-testable (challenge this): the owner recommendation to delegate the two choices
- S46: fixtures in the same change, and record the reasoning.
  - promises: P6
  - tests P6: test_the_published_source_is_answered_with_the_published_tree
- S47: These are presentation
  - not-testable (challenge this): says the delegated choices have no effect on meaning
- S48: choices with no semantic effect.
  - not-testable (challenge this): says the delegated choices have no effect on meaning
- S49: | Option | Consequence |
  - not-testable (challenge this): the header row of the decision table, carrying no promise
- S50: |---|---|
  - not-testable (challenge this): the rule row of the decision table, carrying no promise
- S51: | Delegate (recommended) | F15 and F12 proceed.
  - not-testable (challenge this): a consequence of delegating the decision, about planning
- S52: You review the fixtures afterwards if you want.
  - not-testable (challenge this): an offer to review the fixtures afterwards, about planning
- S53: |
  - not-testable (challenge this): a table cell that closes a row, carrying no promise
- S54: | You approve the layout first | F15 waits for you.
  - not-testable (challenge this): a consequence of approving the layout first, about planning
- S55: F12 can still proceed with the tree schema alone.
  - not-testable (challenge this): says this delivery proceeds either way, about planning
- S56: |
  - not-testable (challenge this): a table cell that closes a row, carrying no promise
- S57: **Blocks** F15 only if you want to approve it.
  - not-testable (challenge this): says which other feature the decision blocks
- S58: F12 does not wait either way.
  - not-testable (challenge this): says this delivery waits for nothing, about planning
- S59: ---
  - not-testable (challenge this): a horizontal rule that ends the quoted decision

## Edge matrix

- I1.empty: the source field holds "" and declares nothing => invalid_program with the refusal a check gives it, and no tree | self-probe: not probed | pre-feature not probed
- I1.unknown: a body naming "missing", which nothing declares => invalid_program with unbound_name, and no tree | self-probe: not probed | pre-feature not probed
- I1.malformed: a source that stops inside a form => invalid_program with syntax, placed where the reader stopped, and no tree | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): reading a text reads nothing outside the request, so no dependency of it can be gone
- I1.repeated: the same source read twice in one session => the same tree and the same revision both times, and nothing written | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): the command answers one request per process and keeps nothing between two of them
- I1.crash: n/a (challenge this): reading writes no file at all, so an interrupted read can leave nothing half written
- I2.empty: discover asked with an empty source field => the manifest unchanged, because discover reads no source | self-probe: not probed | pre-feature not probed
- I2.unknown: n/a (challenge this): discover reads no field but the name of the operation, so it has nothing unknown to meet
- I2.malformed: a discover request whose source field holds 7 => the manifest unchanged, because discover reads no source | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): the manifest is built from the tables of the tool itself and reads nothing outside
- I2.repeated: discover asked twice in one session => the identical manifest both times | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): one answer per process, with nothing shared between two of them
- I2.crash: n/a (challenge this): answering the manifest writes nothing that an interruption could leave half written
- I3.empty: no pair published under conformance/parse => the suite fails on the list of published names, so the schema cannot go unfixed | self-probe: not probed | pre-feature not probed
- I3.unknown: a source published with no tree file beside it => reading the pair fails by name on the missing file | self-probe: not probed | pre-feature not probed
- I3.malformed: n/a (challenge this): a published tree that is not JSON cannot be read at all, and the suite stops on that file by name
- I3.dependency-gone: n/a (challenge this): a published pair depends on nothing but the source published beside it
- I3.repeated: the same pair read twice in one run => the same tree both times, because reading writes nothing | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): the fixtures are read and never written, so two readers cannot disagree about them
- I3.crash: n/a (challenge this): nothing writes a fixture while the tool runs, so an interruption leaves them as they are

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the 5-line source declaring the record "Counter" and the function "held-of"
  - WHEN the parse operation is asked for that source
  - THEN the answer is "completed" and its tree holds 2 declarations in source order
  - test: test_a_valid_program_is_answered_with_the_tree_of_its_declarations
- SC2 (P1): not-held (no held self-probe case)
  - GIVEN the tree answered for that 5-line source
  - WHEN every node of the tree is read
  - THEN each of them carries a line and a column where a character other than " " stands
  - test: test_every_node_stands_at_a_place_the_source_really_has
- SC3 (P2): not-held (no held self-probe case)
  - GIVEN a source whose 1st line is "; what a counter holds" above a declaration
  - WHEN the tree is asked for
  - THEN that declaration carries exactly 1 comment and no other node carries it
  - test: test_each_comment_is_answered_on_the_declaration_written_under_it
- SC4 (P2): not-held (no held self-probe case)
  - GIVEN a source whose last line is "; nothing follows this comment"
  - WHEN the tree is asked for
  - THEN the end of the document carries exactly 1 comment, spelled as written
  - test: test_a_comment_nothing_follows_is_answered_at_the_end_of_the_document
- SC5 (P3): not-held (no held self-probe case)
  - GIVEN the source "" and 5 other sources each breaking 1 rule
  - WHEN parse and check are both asked for each of them
  - THEN both answer the same status and the same categories, and parse publishes 0 trees
  - test: test_a_refused_program_is_refused_the_way_a_check_refuses_it
- SC6 (P4): not-held (no held self-probe case)
  - GIVEN the reservation example of SPEC.md with its 3 types and 3 functions
  - WHEN its tree is asked for
  - THEN the tree holds 6 declarations, 1 precondition, 4 postconditions and 7 examples
  - test: test_every_contract_clause_the_source_writes_stands_in_the_tree
- SC7 (P4): not-held (no held self-probe case)
  - GIVEN the example "(example (step (Reservation 0) (Reserve)) => (Outcome (Reservation 1) true))"
  - WHEN the example node of the tree is written back out
  - THEN the text it writes is found in the source it was read from, matching 1 line of it
  - test: test_every_example_the_source_writes_stands_in_the_tree_with_its_values
- SC8 (P5): not-held (no held self-probe case)
  - GIVEN a client that asks discover as its 1st request, before anything else
  - WHEN the manifest is read
  - THEN parse is advertised "available" and the published schema names every 1 of the kinds the tree of the example holds
  - test: test_the_published_schema_names_every_kind_the_tool_answers
- SC9 (P6): not-held (no held self-probe case)
  - GIVEN the published pair "record-and-function.prova" and the tree file beside it
  - WHEN that source is read
  - THEN the answered tree equals the 1 published beside it, with no part added or missing
  - test: test_the_published_source_is_answered_with_the_published_tree
- SC10 (P7): not-held (no held self-probe case)
  - GIVEN a request whose "source" field holds 7 and not a text
  - WHEN parse is asked
  - THEN the answer is "invalid_input" carrying the 1 category "malformed_request" and no tree
  - test: test_a_source_that_is_not_a_text_is_refused_by_name
- SC11 (P7): not-held (no held self-probe case)
  - GIVEN the 5-line source that declares "Counter" and "held-of"
  - WHEN parse is asked for it
  - THEN the answer carries a 64-character source revision and the claim "syntax_tree"
  - test: test_the_answer_says_which_source_it_is_about_and_claims_only_a_tree

## Questions for the owner

- S33: May I update that one expectation to "parse": "available" as part of this delivery, or do you want F12 to stop before criterion 5?
  - existing behaviour: tests/unit/test_service_discover.py asserts the whole operations table by equality and pins "parse" to "unavailable", so advertising parse as available makes that existing expectation fail
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- A conformance/parse/comments.prova (+3 -0 lines)
- A conformance/parse/comments.tree.json (+28 -0 lines)
- A conformance/parse/let-and-match.prova (+6 -0 lines)
- A conformance/parse/let-and-match.tree.json (+77 -0 lines)
- A conformance/parse/record-and-function.prova (+5 -0 lines)
- A conformance/parse/record-and-function.tree.json (+45 -0 lines)
- M docs/ROADMAP.md (+6 -0 lines)
- A docs/f11-manifest/DECISIONS.md (+17 -0 lines)
- A docs/f11-manifest/SUMMARY.md (+562 -0 lines)
- A docs/f11-manifest/TRACE.md (+5 -0 lines)
- A docs/feature/f11/craft.md (+116 -0 lines)
- A docs/feature/f11/design.md (+101 -0 lines)
- A docs/feature/f11/handoff.md (+44 -0 lines)
- A docs/feature/f11/oracle.md (+69 -0 lines)
- A docs/feature/f11/selfreview.md (+43 -0 lines)
- A docs/feature/published-tree/craft.md (+71 -0 lines)
- A docs/feature/published-tree/design.md (+69 -0 lines)
- A docs/feature/published-tree/oracle.md (+62 -0 lines)
- M src/prova/checker.py (+199 -92 lines)
- M src/prova/evaluator.py (+5 -3 lines)
- A src/prova/manifest.py (+486 -0 lines)
- M src/prova/obligations.py (+4 -3 lines)
- M src/prova/reader.py (+53 -6 lines)
- M src/prova/service.py (+66 -14 lines)
- M src/prova/syntax.py (+123 -25 lines)
- A src/prova/tree.py (+486 -0 lines)
- A tests/acceptance/_f11_manifest_fixtures.py (+163 -0 lines)
- A tests/acceptance/_f12_tree_fixtures.py (+137 -0 lines)
- A tests/acceptance/test_f11_b1_the_manifest_names_every_operation_category.py (+80 -0 lines)
- A tests/acceptance/test_f11_b2_each_available_operation_publishes_its_request_and_its_answer.py (+171 -0 lines)
- A tests/acceptance/test_f11_b3_the_manifest_publishes_every_type_and_operator_core_0_has.py (+105 -0 lines)
- A tests/acceptance/test_f11_b4_a_request_that_breaks_the_published_shape_is_refused.py (+87 -0 lines)
- A tests/acceptance/test_f11_b5_an_operation_the_profile_does_not_name_says_so.py (+73 -0 lines)
- A tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py (+130 -0 lines)
- A tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py (+128 -0 lines)
- A tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py (+91 -0 lines)
- A tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py (+103 -0 lines)
- A tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py (+96 -0 lines)
- A tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py (+61 -0 lines)
- A tests/properties/test_f11_manifest_laws.py (+266 -0 lines)
- A tests/properties/test_f12_published_tree_laws.py (+246 -0 lines)
- A tests/unit/test_a_part_of_a_program_cannot_stand_nowhere.py (+54 -0 lines)
- A tests/unit/test_manifest_catalogue.py (+56 -0 lines)
- M tests/unit/test_obligation_inventory_refuses_what_it_cannot_list.py (+4 -2 lines)
- M tests/unit/test_service_discover.py (+1 -1 lines)

## Commits (git log, BASE to HEAD)

- 28befa3 Roadmap: record the unencodable-source crash raised by the F11 review
- 58ef921 Let an operator say which types it takes and answers
- fb177e3 Say what an agent may call, and what it may write
- 7070f08 Write down what the manifest now says and what it cost
- 8b67d72 Draw the same cases twice, and refuse a category claimed twice
- b4bbc45 Record the repaired work and the run that measured it
- c3b995e Close the record: the review, the self-review and the handoff
- 5a60586 Let every part of a read program say where it stands
- e5d9c2d Refuse a part of a read program that cannot say where it stands
- 2fc9a5f Say what reading a program must answer, before it answers it
- 678936f Expect the manifest to advertise reading a program
- 2893245 Write down where the published tree comes from
- 5661c47 Answer a read program with the tree the tool built
- da59b66 Hand out the comments at the end of a document once
- 6ff4a1a Observe the promises a reader found nothing watching
- 36657c2 Say what the review found and what was done about it
- e14cfed Say where a program built by hand stands
- 7903daa Refuse a signature, an example or a function with no place
- 8d869be Publish what reading a program takes and what it answers
- 5851fe7 Hold reading a program to the laws every operation obeys
- c28a3db Say how reading a program stands in the manifest now
- ab28b70 Fix where a let, a match and its patterns stand
- ed403e3 Observe that a part of a program cannot stand nowhere
- 4e4bf34 Close the gap a repair left in the published table

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f12/request.md
- **promises**:
  - P1: Reading a valid program answers the tree the tool built, with a position on every node.
  - P2: A comment is answered on the node that follows it, or at the end of the document.
  - P3: A program that breaks a rule is refused with the status and the categories a check of it gives, and no tree is published.
  - P4: The tree of the reservation example holds every declaration, every contract clause and every example the source writes.
  - P5: The manifest advertises reading a program as available and publishes the schema its tree is written in.
  - P6: The schema is fixed in conformance fixtures, each source published beside the tree it is answered with.
  - P7: Reading a program answers as the operations beside it do: one claim, the revision of the source, and the request reader refusing a source that is not a text.
- **sentence_map**:
  - S1 => not-testable: names the project, its command and its green suite, which is context and no behaviour
  - S2 => not-testable: names the authority document to read, which is context and no behaviour
  - S3 => not-testable: a process promise about what this delivery may edit
  - S4 => not-testable: a process promise about reporting a conflict to the owner
  - S5 => not-testable: a process promise about a directory to leave alone
  - S6 => not-testable: a process promise about where the work happens
  - S7 => not-testable: a process promise about the commit message trailer
  - S8 => not-testable: the trailer line a commit message ends with
  - S9 => not-testable: a process promise about not pushing and not merging
  - S10 => not-testable: a process promise kept by running the suite, with no scenario of its own
  - S11 => not-testable: names a delivery running beside this one, which is context
  - S12 => not-testable: names what is on main already and which structure to follow
  - S13 => not-testable: a process promise about keeping one file edited narrowly
  - S14 => not-testable: a process promise about where scripts are kept
  - S15 => not-testable: rules of the recording tool, not of the product
  - S16 => not-testable: shell quoting and a clean working tree, both process promises
  - S17 => P1
  - S18 => P1
  - S19 => not-testable: a heading that introduces the criteria under it
  - S20 => not-testable: the number of the first criterion, carrying no promise
  - S21 => P1,P7
  - S22 => P1
  - S23 => not-testable: the number of the second criterion, carrying no promise
  - S24 => P2
  - S25 => P2
  - S26 => not-testable: the number of the third criterion, carrying no promise
  - S27 => P3
  - S28 => P3
  - S29 => not-testable: the number of the fourth criterion, carrying no promise
  - S30 => P4
  - S31 => P4
  - S32 => not-testable: the number of the fifth criterion, carrying no promise
  - S33 => P5
  - S34 => P6
  - S35 => not-testable: names the dependencies and the owner decision that covers the schema
  - S36 => not-testable: declares the size of the delivery, which is planning
  - S37 => not-testable: names the files the work is expected to touch
  - S38 => not-testable: names the files the work is expected to touch
  - S39 => P5
  - S40 => not-testable: cites the line and the probe that observed the refusal today
  - S41 => not-testable: introduces the owner decision quoted under it
  - S42 => P6
  - S43 => P6
  - S44 => not-testable: about formatting policy, which this delivery does not ship
  - S45 => not-testable: the owner recommendation to delegate the two choices
  - S46 => P6
  - S47 => not-testable: says the delegated choices have no effect on meaning
  - S48 => not-testable: says the delegated choices have no effect on meaning
  - S49 => not-testable: the header row of the decision table, carrying no promise
  - S50 => not-testable: the rule row of the decision table, carrying no promise
  - S51 => not-testable: a consequence of delegating the decision, about planning
  - S52 => not-testable: an offer to review the fixtures afterwards, about planning
  - S53 => not-testable: a table cell that closes a row, carrying no promise
  - S54 => not-testable: a consequence of approving the layout first, about planning
  - S55 => not-testable: says this delivery proceeds either way, about planning
  - S56 => not-testable: a table cell that closes a row, carrying no promise
  - S57 => not-testable: says which other feature the decision blocks
  - S58 => not-testable: says this delivery waits for nothing, about planning
  - S59 => not-testable: a horizontal rule that ends the quoted decision
- **scenarios**:
  - SC1 | P1 | GIVEN the 5-line source declaring the record "Counter" and the function "held-of" | WHEN the parse operation is asked for that source | THEN the answer is "completed" and its tree holds 2 declarations in source order
  - SC2 | P1 | GIVEN the tree answered for that 5-line source | WHEN every node of the tree is read | THEN each of them carries a line and a column where a character other than " " stands
  - SC3 | P2 | GIVEN a source whose 1st line is "; what a counter holds" above a declaration | WHEN the tree is asked for | THEN that declaration carries exactly 1 comment and no other node carries it
  - SC4 | P2 | GIVEN a source whose last line is "; nothing follows this comment" | WHEN the tree is asked for | THEN the end of the document carries exactly 1 comment, spelled as written
  - SC5 | P3 | GIVEN the source "" and 5 other sources each breaking 1 rule | WHEN parse and check are both asked for each of them | THEN both answer the same status and the same categories, and parse publishes 0 trees
  - SC6 | P4 | GIVEN the reservation example of SPEC.md with its 3 types and 3 functions | WHEN its tree is asked for | THEN the tree holds 6 declarations, 1 precondition, 4 postconditions and 7 examples
  - SC7 | P4 | GIVEN the example "(example (step (Reservation 0) (Reserve)) => (Outcome (Reservation 1) true))" | WHEN the example node of the tree is written back out | THEN the text it writes is found in the source it was read from, matching 1 line of it
  - SC8 | P5 | GIVEN a client that asks discover as its 1st request, before anything else | WHEN the manifest is read | THEN parse is advertised "available" and the published schema names every 1 of the kinds the tree of the example holds
  - SC9 | P6 | GIVEN the published pair "record-and-function.prova" and the tree file beside it | WHEN that source is read | THEN the answered tree equals the 1 published beside it, with no part added or missing
  - SC10 | P7 | GIVEN a request whose "source" field holds 7 and not a text | WHEN parse is asked | THEN the answer is "invalid_input" carrying the 1 category "malformed_request" and no tree
  - SC11 | P7 | GIVEN the 5-line source that declares "Counter" and "held-of" | WHEN parse is asked for it | THEN the answer carries a 64-character source revision and the claim "syntax_tree"
- **conflicts**:
  - S1 | NONE | checked the suite and the command named: 1136 tests run green on this worktree before any edit
  - S2 | NONE | checked SPEC.md lines 81-84 and 463-470: they require the schema in fixtures, which this work adds
  - S3 | NONE | no expected result of an existing test is edited by this delivery, which the suite run shows
  - S4 | NONE | the one conflict found is reported under S33 rather than repaired by editing a test
  - S5 | NONE | the .relay directory is read by nothing in this change and holds no test of the suite
  - S6 | NONE | every edit of this delivery is inside the worktree named, on the branch it carries
  - S7 | NONE | the trailer is a rule about commits, and no existing behaviour of the product touches it
  - S8 | NONE | the trailer line is a rule about commits and contradicts nothing the product does
  - S9 | NONE | nothing in this delivery pushes or merges, and no test of the suite does either
  - S10 | NONE | the suite is green before this change, and the one test that cannot stay green is reported under S33
  - S11 | NONE | the other delivery owns the manifest, so the edit here adds entries and moves no existing one
  - S12 | NONE | read service.py, the kinds table in checker.py and the manifest, and followed how each is built
  - S13 | NONE | the edit of service.py adds one operation beside its siblings and rewrites none of them
  - S14 | NONE | the scripts of this run live under the workspace directory of this delivery only
  - S15 | NONE | the laws name @given tests, the witnesses are definitions, and the prefactor commit comes first
  - S16 | NONE | a shell rule about quoting and a clean tree, which no behaviour of the product touches
  - S17 | NONE | checked that no operation answers a tree today, so nothing already answers this outcome
  - S18 | NONE | checked that an agent has no published tree today and must read the source text itself
  - S19 | NONE | a heading above the criteria, which contradicts no behaviour the tool has
  - S20 | NONE | the number of a criterion, which contradicts no behaviour the tool has
  - S21 | NONE | checked service.py line 21: parse is refused as unavailable, which is absence, not a contradiction
  - S22 | NONE | checked the typed tree: it carries places on expressions, and the missing ones are added here
  - S23 | NONE | the number of a criterion, which contradicts no behaviour the tool has
  - S24 | NONE | checked reader.py: comments are dropped while reading, which is absence, not a contradiction
  - S25 | NONE | checked that no answer of the tool mentions a comment today, so nothing disagrees with this
  - S26 | NONE | the number of a criterion, which contradicts no behaviour the tool has
  - S27 | NONE | checked that every operation reading source already refuses through one shared rule
  - S28 | NONE | checked that a refusal of that shared rule carries no result field for any operation
  - S29 | NONE | the number of a criterion, which contradicts no behaviour the tool has
  - S30 | NONE | checked the example in SPEC.md and the tests that protect it: this work reads it and changes nothing
  - S31 | NONE | checked the typed tree holds every declaration, clause and example of that source already
  - S32 | NONE | the number of a criterion, which contradicts no behaviour the tool has
  - S33 | CONFLICT | tests/unit/test_service_discover.py asserts the whole operations table by equality and pins "parse" to "unavailable", so advertising parse as available makes that existing expectation fail | May I update that one expectation to "parse": "available" as part of this delivery, or do you want F12 to stop before criterion 5?
  - S34 | NONE | checked conformance/: it holds one source and no published tree, so nothing published disagrees
  - S35 | NONE | a statement about dependencies and the owner decision, contradicting no behaviour
  - S36 | NONE | a statement of size, which contradicts no behaviour the tool has today
  - S37 | NONE | checked both files named: each is touched as the sentence expects, and neither forbids it
  - S38 | NONE | checked conformance/ and tests/: both take new files without disturbing what is there
  - S39 | NONE | checked service.py line 21 and the probe named: parse is refused today, as the sentence says
  - S40 | NONE | a citation of a line and a probe, which contradicts no behaviour the tool has
  - S41 | NONE | introduces the quoted owner decision and contradicts no behaviour the tool has
  - S42 | NONE | checked SPEC.md lines 81-84: the requirement is unmet today, which is absence, not a conflict
  - S43 | NONE | checked that no fixture fixes a schema today, so publishing the first pair disagrees with nothing
  - S44 | NONE | formatting ships later, and this delivery changes no rule about what a valid program is
  - S45 | NONE | the recommendation delegates the choice, and no behaviour of the tool contradicts it
  - S46 | NONE | the fixtures are published in this same change, which nothing in the repository prevents
  - S47 | NONE | checked that the tree answered changes no rule of core-0 and no answer of another operation
  - S48 | NONE | checked that publishing a tree leaves every existing status and category as it was
  - S49 | NONE | a table header of the quoted decision, contradicting no behaviour the tool has
  - S50 | NONE | a table rule of the quoted decision, contradicting no behaviour the tool has
  - S51 | NONE | a consequence of delegating, about planning rather than about the tool behaviour
  - S52 | NONE | an offer to review fixtures later, which contradicts no behaviour the tool has
  - S53 | NONE | a table cell closing a row, contradicting no behaviour the tool has
  - S54 | NONE | a consequence for another feature, about planning rather than about this tool
  - S55 | NONE | says this delivery proceeds, which contradicts no behaviour the tool has
  - S56 | NONE | a table cell closing a row, contradicting no behaviour the tool has
  - S57 | NONE | names what the decision blocks elsewhere, contradicting no behaviour here
  - S58 | NONE | says this delivery waits for nothing, contradicting no behaviour the tool has
  - S59 | NONE | a horizontal rule that ends the quotation and carries no behaviour at all
- **decisions**:
  - S33: put to the owner before any code lands; my recommendation is that the single expectation pinning parse as unavailable in tests/unit/test_service_discover.py be updated to "available" as part of this delivery, because criterion 5 of the request outranks a compatibility expectation that only records what was unbuilt; recorded as asked, not as settled.
  - DEC1: the published tree is the typed tree the tool already builds, written as JSON nodes that each carry a "kind" and a "position"; a declaration, a signature, a parameter, a field, an example, every expression, every pattern and every comment is a node, and the kinds are published by the manifest.
  - DEC2: a comment is published with the characters it was written with, from its ";" to the end of its line, so that a later formatter can write it back unchanged rather than guess the spacing a reader chose.
  - DEC3: a comment attaches to the first node, in the order the tree is walked outermost first, whose place is after the comment; a comment that no node follows is published at the end of the document, on the program node.
  - DEC4: reading a program is an operation that reads source, so it reads the "source" field through the one request reader, refuses a value that is not a text by name, and carries the claim and the source revision its siblings carry.
  - DEC5: no formal model (Quint) pays here: reading a program holds no state between requests, has no protocol of several steps, runs nothing concurrently and writes nothing, so there is no state space a model would explore.
  - DEC6: a field keeps the (name, type) pair the typed tree has today, because an existing test pins that shape by equality; the place of a field node is read from the table of declared names the program already owns, so nothing is counted twice.
  - DEC7: typesafe: unavailable: TYPESAFE_API_KEY is absent from this environment, so the two open questions (which parts are nodes, and how a comment attaches) were settled locally and recorded as DEC1, DEC3 and DEC6.
- **mapping**:
  - P1 => test_a_valid_program_is_answered_with_the_tree_of_its_declarations
  - P2 => test_each_comment_is_answered_on_the_declaration_written_under_it
  - P3 => test_a_refused_program_is_refused_the_way_a_check_refuses_it
  - P4 => test_every_example_the_source_writes_stands_in_the_tree_with_its_values
  - P5 => test_reading_a_program_is_advertised_as_available
  - P6 => test_the_published_source_is_answered_with_the_published_tree
  - P7 => test_the_answer_says_which_source_it_is_about_and_claims_only_a_tree
- **covers_scenarios**:
  - SC1 => test_a_valid_program_is_answered_with_the_tree_of_its_declarations
  - SC2 => test_every_node_stands_at_a_place_the_source_really_has
  - SC3 => test_each_comment_is_answered_on_the_declaration_written_under_it
  - SC4 => test_a_comment_nothing_follows_is_answered_at_the_end_of_the_document
  - SC5 => test_a_refused_program_is_refused_the_way_a_check_refuses_it
  - SC6 => test_every_contract_clause_the_source_writes_stands_in_the_tree
  - SC7 => test_every_example_the_source_writes_stands_in_the_tree_with_its_values
  - SC8 => test_the_published_schema_names_every_kind_the_tool_answers
  - SC9 => test_the_published_source_is_answered_with_the_published_tree
  - SC10 => test_a_source_that_is_not_a_text_is_refused_by_name
  - SC11 => test_the_answer_says_which_source_it_is_about_and_claims_only_a_tree
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
- **interfaces**:
  - I1: the parse operation of the JSON service, asked through the command over standard input or through the public handle
  - I2: the discover operation, which publishes the operations the tool answers and the schema of the tree
  - I3: the conformance fixtures under conformance/parse, each source published beside the tree it is answered with
- **matrix**:
  - I1.empty => the source field holds "" and declares nothing => invalid_program with the refusal a check gives it, and no tree
  - I1.unknown => a body naming "missing", which nothing declares => invalid_program with unbound_name, and no tree
  - I1.malformed => a source that stops inside a form => invalid_program with syntax, placed where the reader stopped, and no tree
  - I1.dependency-gone => n/a: reading a text reads nothing outside the request, so no dependency of it can be gone
  - I1.repeated => the same source read twice in one session => the same tree and the same revision both times, and nothing written
  - I1.concurrent => n/a: the command answers one request per process and keeps nothing between two of them
  - I1.crash => n/a: reading writes no file at all, so an interrupted read can leave nothing half written
  - I2.empty => discover asked with an empty source field => the manifest unchanged, because discover reads no source
  - I2.unknown => n/a: discover reads no field but the name of the operation, so it has nothing unknown to meet
  - I2.malformed => a discover request whose source field holds 7 => the manifest unchanged, because discover reads no source
  - I2.dependency-gone => n/a: the manifest is built from the tables of the tool itself and reads nothing outside
  - I2.repeated => discover asked twice in one session => the identical manifest both times
  - I2.concurrent => n/a: one answer per process, with nothing shared between two of them
  - I2.crash => n/a: answering the manifest writes nothing that an interruption could leave half written
  - I3.empty => no pair published under conformance/parse => the suite fails on the list of published names, so the schema cannot go unfixed
  - I3.unknown => a source published with no tree file beside it => reading the pair fails by name on the missing file
  - I3.malformed => n/a: a published tree that is not JSON cannot be read at all, and the suite stops on that file by name
  - I3.dependency-gone => n/a: a published pair depends on nothing but the source published beside it
  - I3.repeated => the same pair read twice in one run => the same tree both times, because reading writes nothing
  - I3.concurrent => n/a: the fixtures are read and never written, so two readers cannot disagree about them
  - I3.crash => n/a: nothing writes a fixture while the tool runs, so an interruption leaves them as they are
- **laws**:
  - LAW1 | every node of a published tree stands at a place the source really has | generator=test_every_node_stands_where_the_source_holds_a_character | observation=the line is one the source holds and the character at that column is not a space | mutant=a node built with the default place line 0 column 0, or carrying the place of its parent
  - LAW2 | every comment is answered exactly once, on the first node that stands after it, or at the end of the document when no node does | generator=test_every_comment_is_answered_once_on_the_first_node_after_it | observation=the holder is the node with the smallest place after the comment, and the document end holds the comment only when no node follows it | mutant=every comment collected at the document end whatever follows it
  - LAW3 | a tree is published exactly when a check of the same source completes, and a refusal carries the status and categories the check gives | generator=test_a_tree_is_published_exactly_when_a_check_completes | observation=status and categories equal those of check for the same text, and a result stands in the answer exactly when the status is completed | mutant=an empty tree published beside a refusal, or a category invented for reading alone
- **messages**:
  - MSG0 | none: reading a program adds no refusal of its own. Every refusal it gives is built by the rule it shares with check, and a source that is not a text is refused by the one request reader, each of which already states what, why and how.
- **red**: `uv run pytest -q tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py tests/properties/test_f12_published_tree_laws.py` exited 1 in 3.322s
  - failing on the pre-feature tree (21): tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py::test_a_valid_program_is_answered_with_the_tree_of_its_declarations, tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py::test_the_answer_says_which_source_it_is_about_and_claims_only_a_tree, tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py::test_every_node_stands_at_a_place_the_source_really_has, tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py::test_the_command_answers_the_same_tree_as_the_library, tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py::test_each_comment_is_answered_on_the_declaration_written_under_it, tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py::test_a_comment_nothing_follows_is_answered_at_the_end_of_the_document, tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py::test_every_comment_of_the_source_is_answered_exactly_once, tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_refused_program_is_refused_the_way_a_check_refuses_it[a, tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_source_that_is_not_a_text_is_refused_by_name, tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py::test_every_type_and_function_the_source_declares_stands_in_the_tree, tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py::test_every_contract_clause_the_source_writes_stands_in_the_tree, tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py::test_every_example_the_source_writes_stands_in_the_tree_with_its_values, tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py::test_reading_a_program_is_advertised_as_available, tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py::test_the_manifest_publishes_the_schema_the_tree_is_written_in, tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py::test_the_published_schema_names_every_kind_the_tool_answers, tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py::test_every_published_source_is_one_this_suite_reads, tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py::test_the_published_source_is_answered_with_the_published_tree[comments], tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py::test_the_published_source_is_answered_with_the_published_tree[record-and-function], tests/properties/test_f12_published_tree_laws.py::test_every_node_stands_where_the_source_holds_a_character, tests/properties/test_f12_published_tree_laws.py::test_every_comment_is_answered_once_on_the_first_node_after_it, tests/properties/test_f12_published_tree_laws.py::test_a_tree_is_published_exactly_when_a_check_completes
  - tests (read from the run): 26 failed, 6 passed in 2.76s
  ```text
  E             '(deftype T0 (record (a0 Int) (b0 Bool)))\n'
  E           assert 'unavailable' == 'completed'
  E
  E             - completed
  E             + unavailable
  E           Failing test case: test_a_tree_is_published_exactly_when_a_check_completes(
  E               # The test always failed when commented parts were varied together.
  E               source='(deftype T0 (record (a0 Int) (b0 Bool)))\n',  # or any other generated value
  E               cut=0,  # or any other generated value
  E           )

  tests/properties/test_f12_published_tree_laws.py:197: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py::test_a_valid_program_is_answered_with_the_tree_of_its_declarations
  FAILED tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py::test_the_answer_says_which_source_it_is_about_and_claims_only_a_tree
  FAILED tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py::test_every_node_stands_at_a_place_the_source_really_has
  FAILED tests/acceptance/test_f12_b1_a_valid_program_is_answered_with_its_tree.py::test_the_command_answers_the_same_tree_as_the_library
  FAILED tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py::test_each_comment_is_answered_on_the_declaration_written_under_it
  FAILED tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py::test_a_comment_nothing_follows_is_answered_at_the_end_of_the_document
  FAILED tests/acceptance/test_f12_b2_a_comment_is_attached_to_what_follows_it.py::test_every_comment_of_the_source_is_answered_exactly_once
  FAILED tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_refused_program_is_refused_the_way_a_check_refuses_it[a body naming what is not bound-(defn one\n  (sig () -> Int ! pure)\n  (examples (example (one) => 1))\n  missing)\n]
  FAILED tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_refused_program_is_refused_the_way_a_check_refuses_it[a body of the wrong type-(defn one\n  (sig () -> Int ! pure)\n  (examples (example (one) => 1))\n  true)\n]
  FAILED tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_refused_program_is_refused_the_way_a_check_refuses_it[a division the profile does not have-(defn half\n  (sig ((n Int)) -> Int ! pure)\n  (examples (example (half 2) => 1))\n  (/ n 2))\n]
  FAILED tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_refused_program_is_refused_the_way_a_check_refuses_it[a form that is never closed-(deftype Counter (record (held Int))\n]
  FAILED tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_refused_program_is_refused_the_way_a_check_refuses_it[a name that is declared twice-(deftype Counter (record (held Int)))\n(deftype Counter (record (held Int)))\n]
  FAILED tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_refused_program_is_refused_the_way_a_check_refuses_it[a source that declares nothing-]
  FAILED tests/acceptance/test_f12_b3_an_invalid_program_is_refused_without_a_tree.py::test_a_source_that_is_not_a_text_is_refused_by_name
  FAILED tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py::test_every_type_and_function_the_source_declares_stands_in_the_tree
  FAILED tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py::test_every_contract_clause_the_source_writes_stands_in_the_tree
  FAILED tests/acceptance/test_f12_b4_the_reservation_example_appears_whole_in_its_tree.py::test_every_example_the_source_writes_stands_in_the_tree_with_its_values
  FAILED tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py::test_reading_a_program_is_advertised_as_available
  FAILED tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py::test_the_manifest_publishes_the_schema_the_tree_is_written_in
  FAILED tests/acceptance/test_f12_b5_discover_advertises_parse_with_its_schema.py::test_the_published_schema_names_every_kind_the_tool_answers
  FAILED tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py::test_every_published_source_is_one_this_suite_reads
  FAILED tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py::test_the_published_source_is_answered_with_the_published_tree[comments]
  FAILED tests/acceptance/test_f12_b6_the_published_fixtures_are_what_reading_answers.py::test_the_published_source_is_answered_with_the_published_tree[record-and-function]
  FAILED tests/properties/test_f12_published_tree_laws.py::test_every_node_stands_where_the_source_holds_a_character
  FAILED tests/properties/test_f12_published_tree_laws.py::test_every_comment_is_answered_once_on_the_first_node_after_it
  FAILED tests/properties/test_f12_published_tree_laws.py::test_a_tree_is_published_exactly_when_a_check_completes
  26 failed, 6 passed in 2.76s
  ```

## 2. design: Find the owners and design the change (revision 1)

- **owners**:
  - the characters of a source, the forms they write and where each form stands => src/prova/reader.py
  - the typed tree of a core-0 program, and the place of every form it was read from => src/prova/syntax.py
  - every name a program declares, with the place it stands at => src/prova/syntax.py, class Declarations
  - which operations the tool answers, and what each answer carries => src/prova/service.py
  - the categories a refusal carries and what each one holds => src/prova/checker.py, table DIAGNOSTIC_KINDS
  - how a value is written back as the text a program writes => src/prova/values.py, function render
  - the shape of the tree a client is answered with, and the schema that names its kinds => new: src/prova/tree.py, because no module owns a published interchange format today
- **reuse_decision**: Reused: the reader for the forms and their places, the typed tree for the structure, the shared rule in service.py that refuses a source every operation refuses the same way, the table of declared names for the place of a field, values.render for the text of an example value, and the manifest for publishing. Created new: src/prova/tree.py, which owns the published node kinds, the attachment of a comment and the schema the manifest publishes. No existing owner fits: syntax.py owns the tree the checker walks and must not learn a wire format, and service.py owns operations and answers, not the shape of a tree. reader.py gains the comments it already meets and today throws away, because it is the only place that reads characters.
- **paradigm**: oo
- **boundaries**:
  - the request boundary: the source field is read by the one request reader in service.py, and reading a program adds no field of its own
  - the answer boundary: service.py builds every response dictionary; tree.py hands it one tree and names no operation and no status
  - the text boundary: reader.py turns characters into forms and comments, and nothing after it reads a character of the source again
  - the published boundary: the pairs under conformance/parse are read by the suite and written by a person, never written by the tool
- **domain_types**:
  - Place (new, tree.py): the line and column a node stands at, built only from a form the reader placed
  - PublishedNode (new, tree.py): one node of the published tree: its kind, its place, the parts it carries and the comments attached to it
  - TreeSchema (new, tree.py): the kinds of node and what each kind carries, read by the manifest from the same table the builder builds from
  - Comment (new, reader.py): the characters a reader wrote, from the ";" to the end of its line, and the place they stand at
  - SourceText (new, reader.py): the forms of one text beside the comments met while reading it
  - Parameter (changed, syntax.py): a declared parameter as a value object carrying its name, its declared type and its place, instead of a bare pair of strings
  - Binding (changed, syntax.py): one binding of a let as a value object carrying its name, its expression and its place, instead of a bare pair
- **invariants**:
  - INV1 | every published node carries the place of the form it was read from, and a node cannot be built without one | witness=src/prova/tree.py:PublishedNode | bypass=none
  - INV2 | the kinds the manifest publishes are the kinds the builder can answer, because both read one table | witness=src/prova/tree.py:TreeSchema | bypass=none
  - INV3 | every comment of the source is published exactly once: on the first node that stands after it, or at the end of the document when no node does | witness=src/prova/tree.py:AttachedComments | bypass=none
  - INV4 | a tree is published only for a source that passed every rule of core-0, so an answer that refuses a source carries no tree at all | witness=src/prova/service.py:_run_parse | bypass=none
  - INV5 | a comment keeps the characters it was written with, from its ";" to the end of its line | witness=src/prova/reader.py:Comment | bypass=none
- **prefactoring**: yes
- **prefactoring_reason**: The typed tree keeps a declared parameter and a let binding as bare pairs of strings, and its declarations, signatures, examples, match clauses and patterns carry no place at all. Publishing a tree needs a place on each of them and needs a parameter and a binding to be able to carry one, so the pairs become value objects and the places are filled first, in commits that change no answer the tool gives and edit no test. A field keeps its pair, because an existing test pins that shape by equality; its place is read from the table of declared names instead.

## 3. craft: Craft the change (revision 1)

- **refactor_commits**:
  - 385b185
- **refactor_check**: the check ran on the parent and on each refactor commit
  - 385b185a2da3 (Let every part of a read program say where it stands): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 138.239s
  - tests (read from the run): 1168 passed in 138.10s
  - slowest: 7.12s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.65s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 4.15s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.56s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 3.40s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 2.99s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 2.12s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.75s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.63s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.55s call tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  ```text
  ........................................................................ [  6%]
  ........................................................................ [ 12%]
  ........................................................................ [ 18%]
  ........................................................................ [ 24%]
  ........................................................................ [ 30%]
  ........................................................................ [ 36%]
  ........................................................................ [ 43%]
  ........................................................................ [ 49%]
  ........................................................................ [ 55%]
  ........................................................................ [ 61%]
  ........................................................................ [ 67%]
  ........................................................................ [ 73%]
  ........................................................................ [ 80%]
  ........................................................................ [ 86%]
  ........................................................................ [ 92%]
  ........................................................................ [ 98%]
  ................                                                         [100%]
  ============================= slowest 10 durations =============================
  7.12s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.65s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  4.15s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.56s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  3.40s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  2.99s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  2.12s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.75s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.63s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.55s call     tests/properties/test_i1_s1_p6.py::test_p6_refused_build_preserves_pre_existing_outputs
  1168 passed in 138.10s (0:02:18)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.126s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this process environment, so jev_decide.py exited 3 before sending anything; the open choices (which parts of the tree are nodes, how a comment attaches, where a field node reads its place) were settled locally and recorded as DEC1, DEC3 and DEC6 of the oracle step

## 4. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the change is what the design record names: tree.py owns the published tree and the schema, reader.py owns the characters and the comments, syntax.py owns the typed tree and the places, service.py owns the operation and the answer
  - D2: pass - the kinds are published and built from one table (src/prova/tree.py:141 TreeSchema), the place of a field is read from the table of declared names rather than counted again, and the words that say where a field is unique are written once in syntax.py as within_record and within_variant
  - D3: pass - tree.py reads syntax.py and reader.py and knows no operation, no status and no response shape; service.py hands it a checked program and prints what it gets back; nothing in syntax.py or reader.py knows the published format
  - D4: pass - src/prova/tree.py:36 refuses a place that stands before line 1 column 1, and a part of a read program cannot be built without its place at all (src/prova/syntax.py:472 Parameter, 755 Binding), which tests/unit/test_a_part_of_a_program_cannot_stand_nowhere.py:29 observes
  - D5: pass - src/prova/tree.py:55 AttachedComments owns the attachment rule and nothing else, Place owns a place, PublishedNode owns a node, TreeSchema owns the table; each is small, holds its own state and is asked rather than read
  - D6: pass - no pattern was imposed: a table from a node type to its published kind and parts replaces a chain of type tests, and the walk that publishes is one method on the node that owns the data
  - D7: pass - the words of the domain are the words of the grammar: a declaration, a signature, a parameter, a field, an example, a clause, a pattern, a comment; no manager, helper or builder was added
  - D8: pass - nothing in tree.py reads a file, a clock or an environment: it is handed a program and the comments of its source and answers a dictionary
  - D9: pass - every test asks the service through its public operation or the real command (tests/acceptance/_f12_tree_fixtures.py:93), and the unit test about places uses the public types of syntax.py; no test reaches a private function of tree.py
  - D10: pass - each test is named as a sentence about what the tool answers: a valid program is answered with the tree of its declarations, a comment is answered on the declaration written under it, a refused program is refused the way a check refuses it
  - D11: pass - the shared helpers are the walk over a tree, the two requests and the list of oracle programs (tests/acceptance/_f12_tree_fixtures.py:83); no helper owns a whole scenario and each test writes its own Given
  - D12: pass - three laws over generated programs: tests/properties/test_f12_published_tree_laws.py:131 every node stands where the source holds a character, 162 every comment is answered once on the first node after it, 226 a tree is published exactly when a check completes; all three derandomised
  - D13: pass - the seven test files of this change run 35 tests in 0.30s, measured nine times in a row with the same count and the same time; the slowest single test is the one that drives the real command, at 0.04s
  - D14: pass - the example tests and the laws observe different things: the examples pin one tree each, the laws observe what holds over generated programs, and no law repeats a pair an example already fixes
  - D15: pass - every refusal this change adds says what, why and how: src/prova/tree.py:36 names the place, why it is no place in a text and what to build it from; src/prova/syntax.py:574 names the kind and the name it was asked about and why that is a question about a program never read
  - D16: n/a: reading a program keeps nothing between requests, has no protocol of several steps, runs nothing concurrently and writes no file, so a formal model has no state space to explore; written in the design record as DEC5
  - D17: fixed: the oracle record said the manifest expectation was an open question after the owner had answered it, and the craft record counted a suite that the merge of the other delivery has since changed; both were rewritten against what the repository now holds, and the craft record names the three tests that already existed and were edited
- **independent_review**:
  - REV1 | reviewer=independent-review-f12 | findings=8 (verdict REJECT at 4d99522) | resolution=all eight fixed in da59b66 and 6ff4a1a, integrated with F11 afterwards
  - REV2 | reviewer=independent-review-f12 | findings=3 (verdict APPROVE at c28a3db, non-blocking) | resolution=F9 and F10 fixed after the review, F11 handled as stated in the handoff

## 5. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
- **not_verified**:
  - The sentence in the published position text that says a field and a parameter stand at the name they declare is verified by reading only: a test pinning the wording of a document is forbidden, so nothing fails if that sentence goes stale while the behaviour stays right.
  - No linter and no type checker is configured in this project, so the scorecard only compiles the package and the tests: no style, type or dead-code claim is made.
  - Jev was unreachable for the whole run, TYPESAFE_API_KEY being absent, so every open choice was settled locally and written down rather than put to the service.
  - The craft step could not be recorded again after this branch moved onto main: the workspace baseline is the commit the work started from, so the tool reads the commits of main as feature commits standing before the two refactor commits. The refusal was reported upward and nothing was decided here, so the craft record names the commit ids this branch carried before the move.
  - A tree of a program that nests close to the published reading limit was never published: the limit is refused by the reader before a tree is built, and nothing measures how large an answered tree may become.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit 4e4bf34646ebb178ea2afc1ca85552e9674d60ea
  - no checks declared

## Not backed by the diff

- Reading a program is answered now, with the tree the tool built and a place on every node of it.: a guarantee names no test function of the change
- The comments the reader used to drop are kept, each answered on the first node standing after it or at the end of the document, with the characters it was written with and no line terminator.: a guarantee names no test function of the change
- A source that breaks a rule of core-0 is refused exactly as a check refuses it and carries no tree.: a guarantee names no test function of the change
- The schema is published by the manifest from the same table the tree is built from, and fixed by three published pairs under conformance/parse, each tree written by hand from the source before the code existed.: a guarantee names no test function of the change
- Two reviews were answered: the first rejected the work over eight findings, every one of which was repaired with a check that fails on the old behaviour; the second approved it with three notes, two of which were repaired afterwards.: a guarantee names no test function of the change
- Every repair was checked by putting the wrong behaviour back and watching the test that must see it fail.: a guarantee names no test function of the change
