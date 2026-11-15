# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1277 tests, all green on main).
  - not-testable (challenge this): names the project, its runner and its suite; it states no outcome of the tool
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names the authority document to read, not an outcome of the tool
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a process constraint on what this delivery may edit
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): a process instruction on how to report a conflict to the owner
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): a process instruction naming a directory to leave alone
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): a process constraint on where the work happens
- S7: Commit with a message ending in the line
  - not-testable (challenge this): a process constraint on the commit message
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the line the commit message has to end with, a process constraint
- S9: Do not push and do not merge.
  - not-testable (challenge this): a process constraint forbidding a push and a merge
- S10: Keep the full suite green.
  - not-testable (challenge this): a process promise about the whole suite staying green
- S11: Another delivery (R2, two robustness fixes in reader.py and the request reader, tests) runs in parallel in a different worktree; keep your service.py edits small and local.
  - not-testable (challenge this): a process constraint about a delivery running in parallel
- S12: F1 to F16 (except F13 is merged too) and R1 are on main: read how answers are built now: `claim` and `source_digest` already appear on completed answers (parse and format publish a claim kind and scope), diagnostics carry `source_revision`, the manifest (manifest.py) publishes the shape of every answer and F14 budgets, and tests such as the F11 laws compare published fields with emitted fields.
  - not-testable (challenge this): says where to read how answers are built today
- S13: Extend those, do not duplicate them.
  - not-testable (challenge this): a design instruction to extend what exists rather than repeat it
- S14: A tool failure is never a semantic result (SPEC.md lines 270-284).
  - promises: P5
  - tests P5: test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool
- S15: Keep your scripts in your own directory under the nwstep workspace, never in a shared scratchpad.
  - not-testable (challenge this): a process constraint on where the scripts of this run live
- S16: Known tool rules: oracle laws must name @given property tests; design invariant witnesses must be a `class` or `def`, and keep the design record in step with the code; an independent_review resolution needs at least 20 characters; prefactor commits must come first in history; process promises go in not-testable sentences; the oracle RED command must name only your new test files.
  - not-testable (challenge this): the process rules of the recording tool
- S17: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): process hygiene for the shell and for the final report
- S18: **Outcome.** Any answer the tool gives carries its claim kind, its scope and the
  - promises: P1
  - tests P1: test_every_completed_answer_names_the_dependencies_it_stands_on
- S19: versions behind it, so evidence of one kind is never read as evidence of another.
  - promises: P1, P2
  - tests P1: test_every_completed_answer_names_the_dependencies_it_stands_on
  - tests P2: test_every_completed_answer_names_all_four_versions
- S20: **Acceptance criteria**
  - not-testable (challenge this): a heading that introduces the criteria below it
- S21: 1.
  - not-testable (challenge this): the number of the first criterion, carrying no outcome
- S22: Given any completed operation, when it answers, then the answer states the claim
  - promises: P1
  - tests P1: test_every_completed_answer_names_the_dependencies_it_stands_on
- S23: kind, the scope and the source and dependency digests.
  - promises: P1
  - tests P1: test_every_completed_answer_names_the_dependencies_it_stands_on
- S24: 2.
  - not-testable (challenge this): the number of the second criterion, carrying no outcome
- S25: Given any completed operation, then it states the compiler, encoding, solver and
  - promises: P2
  - tests P2: test_every_completed_answer_names_all_four_versions
- S26: runtime versions it used, or says which are not applicable.
  - promises: P2
  - tests P2: test_every_completed_answer_names_all_four_versions
- S27: 3.
  - not-testable (challenge this): the number of the third criterion, carrying no outcome
- S28: Given an examples run, then the claim kind is examples and the scope is the
  - promises: P3
  - tests P3: test_an_examples_run_calls_itself_an_examples_run
- S29: declared examples only.
  - promises: P3
  - tests P3: test_an_examples_run_calls_itself_an_examples_run
- S30: 4.
  - not-testable (challenge this): the number of the fourth criterion, carrying no outcome
- S31: Given a verify answer, then each obligation's logical result and its execution
  - promises: P4
  - tests P4: test_each_obligation_carries_both_a_logical_result_and_an_execution_status
- S32: status are separate fields.
  - promises: P4
  - tests P4: test_each_obligation_carries_both_a_logical_result_and_an_execution_status
- S33: 5.
  - not-testable (challenge this): the number of the fifth criterion, carrying no outcome
- S34: Given a tool failure, then the answer is a tool failure, not a semantic result.
  - promises: P5
  - tests P5: test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool
- S35: 6.
  - not-testable (challenge this): the number of the sixth criterion, carrying no outcome
- S36: Given a result from an earlier revision, when the source has changed, then the
  - promises: P6
  - tests P6: test_the_manifest_tells_a_client_what_makes_a_kept_answer_stale
- S37: answer does not present that result as current.
  - promises: P6
  - tests P6: test_the_manifest_tells_a_client_what_makes_a_kept_answer_stale
- S38: **SPEC.md** lines 270-284, 476-482.
  - not-testable (challenge this): a pointer to the lines of the authority behind the criteria
- S39: **Dependencies** none, but it is cheapest
  - not-testable (challenge this): a statement about dependencies and about what is cheapest
- S40: together with F16.
  - not-testable (challenge this): the rest of that statement about cost, naming no outcome
- S41: **Size** M.
  - not-testable (challenge this): the size the request estimates for this work
- S42: **Touches** `src/prova/service.py`, tests.
  - not-testable (challenge this): the files the request expects this change to touch
- S43: **Why it is a real expectation** probe S8 shows only `source_digest` is present.
  - not-testable (challenge this): the reason the request calls this a real expectation

## Edge matrix

- I1.empty: a check request whose source field is the empty text => the answer refuses the empty text and carries no claim, no digest and no provenance | self-probe: not probed | pre-feature not probed
- I1.unknown: an operation named fly, which this tool does not have => status unavailable with no claim and no provenance | self-probe: not probed | pre-feature not probed
- I1.malformed: a check request whose source field holds the number 7 => status invalid_input naming the field source, with no provenance | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): a request is answered from its own text alone; this tool reads no file and calls no service while it answers
- I1.repeated: the same check request sent twice => both answers carry the same revision, the same dependency digest and the same 4 versions | self-probe: not probed | pre-feature not probed
- I1.concurrent: 2 requests answered by 2 processes at once => each answer carries the revision of its own text only, since neither process shares anything | self-probe: not probed | pre-feature not probed
- I1.crash: n/a (challenge this): the command writes no file and keeps no state, so a run stopped halfway leaves nothing to repair or to read
- I2.empty: discover sent with no other field => the manifest is answered whole, with the dependency digest and the 4 versions in it | self-probe: not probed | pre-feature not probed
- I2.unknown: a client looks up the operation build, which this tool does not answer => it is listed unavailable and carries no answer shape to read | self-probe: not probed | pre-feature not probed
- I2.malformed: discover sent with a source field holding the number 7 => the manifest is answered as usual, because discover reads no field of the request | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): the manifest is read from this tool own tables, with no file and no service behind it
- I2.repeated: discover asked twice => the same dependency digest and the same 4 versions both times | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): discover reads nothing another run can change, so 2 runs cannot meet over anything
- I2.crash: n/a (challenge this): discover writes nothing, so a run stopped halfway leaves nothing behind
- I3.empty: the entry point called with an empty JSON object => status unavailable, because no operation is named, with no provenance | self-probe: not probed | pre-feature not probed
- I3.unknown: the entry point called with the operation fly => status unavailable with the refusal that names it, and no provenance | self-probe: not probed | pre-feature not probed
- I3.malformed: the entry point called with a request object that raises while 1 field is read => status tool_failure with no claim, no result, no digest and no provenance | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): nothing outside the process is read while an answer is built, so nothing can be gone
- I3.repeated: the same request answered twice in 1 process => the 2 texts are identical, including both digests | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): the entry point keeps nothing between 2 calls, so 2 calls cannot meet over anything
- I3.crash: n/a (challenge this): nothing is written, so a call stopped halfway leaves nothing behind

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN a program of 2 functions sent to "check"
  - WHEN the tool answers it
  - THEN the answer carries a claim kind, a scope, the SHA-256 of the 2-function text and a 64-character dependency digest equal to the one "discover" publishes
  - test: test_every_completed_answer_names_the_dependencies_it_stands_on
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN that same program sent to each of the 6 operations this tool completes
  - WHEN each answers
  - THEN each answer names exactly 4 versions and says of the solver and the encoding "not applicable" with a reason of its own
  - test: test_every_completed_answer_names_all_four_versions
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN a program declaring 2 examples
  - WHEN its examples are run
  - THEN the claim kind is "examples", the scope names the declared examples, and the answer carries exactly those 2 entries
  - test: test_an_examples_run_calls_itself_an_examples_run
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN that same 2-function program sent to "verify"
  - WHEN the inventory is answered
  - THEN every entry carries 2 separate fields, a logical result "not_attempted" and an execution status "unsupported"
  - test: test_each_obligation_carries_both_a_logical_result_and_an_execution_status
- SC5 (P5): not-held (no held self-probe case)
  - GIVEN a request object that raises while the tool reads 1 field of it
  - WHEN the tool is asked to answer it
  - THEN the answer carries status "tool_failure" with no claim, no result, no source digest and no provenance
  - test: test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool
- SC6 (P6): not-held (no held self-probe case)
  - GIVEN an answer kept about a 2-function program and the same program with 1 function added
  - WHEN both are checked
  - THEN the 2 answers name 2 different revisions, the same dependency digest, and the manifest names both fields as the ones a client compares
  - test: test_the_manifest_tells_a_client_what_makes_a_kept_answer_stale

## Questions for the owner

- S22: Should the provenance block be carried by the 6 operations the profile names and left off evaluate, this tool own extension, or should the pinned transcript test be widened to admit it?
  - existing behaviour: the accepted test tests/properties/test_i1_s4_p6_transcript.py pins the completed evaluate answer to exactly the 6 top-level fields operation, status, claim, source_digest, diagnostics and result, and pins its claim to exactly 2 keys, so no new field can reach the evaluate answer without editing that test
  - status: decided at oracle
- S25: Should the 4 versions be named by the 6 operations the profile names and left off evaluate for the same reason?
  - existing behaviour: the same pinned transcript test forbids a new field on the completed evaluate answer, so the 4 versions cannot be named there either
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- M docs/ROADMAP.md (+8 -0 lines)
- A docs/feature/provenance/craft.md (+91 -0 lines)
- A docs/feature/provenance/design.md (+68 -0 lines)
- A docs/feature/provenance/oracle.md (+85 -0 lines)
- A docs/r2-two-crashes/DECISIONS.md (+15 -0 lines)
- A docs/r2-two-crashes/SUMMARY.md (+498 -0 lines)
- A docs/r2-two-crashes/TRACE.md (+5 -0 lines)
- M src/prova/__main__.py (+29 -0 lines)
- M src/prova/checker.py (+3 -0 lines)
- M src/prova/manifest.py (+37 -14 lines)
- M src/prova/obligations.py (+14 -6 lines)
- A src/prova/provenance.py (+216 -0 lines)
- M src/prova/reader.py (+74 -0 lines)
- M src/prova/service.py (+237 -47 lines)
- A tests/acceptance/_f17_provenance_fixtures.py (+119 -0 lines)
- M tests/acceptance/_r1_robustness_fixtures.py (+13 -2 lines)
- A tests/acceptance/test_f17_b1_every_answer_says_what_it_stands_on.py (+99 -0 lines)
- A tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py (+122 -0 lines)
- A tests/acceptance/test_f17_b3_an_examples_run_reaches_only_the_declared_examples.py (+81 -0 lines)
- A tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py (+116 -0 lines)
- A tests/acceptance/test_f17_b5_an_answer_about_an_older_source_says_so.py (+92 -0 lines)
- A tests/acceptance/test_r2_b1_a_text_that_cannot_be_written_as_utf8_is_refused.py (+195 -0 lines)
- A tests/acceptance/test_r2_b2_an_integer_literal_past_the_digit_limit_is_refused.py (+229 -0 lines)
- A tests/acceptance/test_r2_b3_a_number_in_the_request_too_long_to_read_is_refused.py (+111 -0 lines)
- M tests/properties/_r1_mangled_requests.py (+11 -1 lines)
- M tests/properties/test_f11_manifest_laws.py (+76 -0 lines)
- A tests/properties/test_f17_provenance_laws.py (+189 -0 lines)
- A tests/properties/test_r2_p1_a_surrogate_or_a_long_run_of_digits_is_answered.py (+396 -0 lines)
- A tests/unit/test_f17_b6_a_failure_of_the_tool_is_not_an_answer_about_a_program.py (+120 -0 lines)
- A tests/unit/test_reader_counts_the_digits_of_an_atom.py (+36 -0 lines)

## Commits (git log, BASE to HEAD)

- 2ffc5f1 Refuse half a character and an over-long run of digits
- 96195ed Record what was decided, what was proved and what was not
- 7109998 Hand the formatter the characters of a submitted text
- 53690f7 Count the digits of a text that has none as none
- b9d7026 Answer a request whose own number is too long to read
- ffbee38 Ask every operation and every named text for the same two facts
- 192f137 Bring the record up to date with what the review changed
- e5b86d7 Roadmap: record the three crashes found by the R2 review
- f2a76f7 Write the digest of a text in one place
- bc577e0 Say what every answer stands on, and keep a failure of the tool apart
- b2593c9 Write down what the new checks cost to run
- dc328d4 Stop promising a field a budget can take away
- 1a79b6c Say the same thing about an obligation in both places
- 9212ab5 Run the laws over every cell of their grid
- ad39ced Measure the suite again, on the tree that will be read

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f17/request.md
- **promises**:
  - P1: Any answer this tool completes says what kind of statement it makes, how far that statement reaches, which revision of the source it is about and which dependencies it stands on.
  - P2: Any answer this tool completes names the compiler, the encoding, the solver and the runtime it used, and says of each one it did not use that it does not apply and why.
  - P3: An examples run calls itself an examples run and reaches the examples the program declares, and no further.
  - P4: A verify answer keeps what each obligation would have to show apart from what happened when something tried to show it.
  - P5: A failure of this tool itself is answered as a failure of the tool and reports nothing about a program.
  - P6: An answer kept from before an edit does not read as an answer about the text the client holds now.
- **sentence_map**:
  - S1 => not-testable: names the project, its runner and its suite; it states no outcome of the tool
  - S2 => not-testable: names the authority document to read, not an outcome of the tool
  - S3 => not-testable: a process constraint on what this delivery may edit
  - S4 => not-testable: a process instruction on how to report a conflict to the owner
  - S5 => not-testable: a process instruction naming a directory to leave alone
  - S6 => not-testable: a process constraint on where the work happens
  - S7 => not-testable: a process constraint on the commit message
  - S8 => not-testable: the line the commit message has to end with, a process constraint
  - S9 => not-testable: a process constraint forbidding a push and a merge
  - S10 => not-testable: a process promise about the whole suite staying green
  - S11 => not-testable: a process constraint about a delivery running in parallel
  - S12 => not-testable: says where to read how answers are built today
  - S13 => not-testable: a design instruction to extend what exists rather than repeat it
  - S14 => P5
  - S15 => not-testable: a process constraint on where the scripts of this run live
  - S16 => not-testable: the process rules of the recording tool
  - S17 => not-testable: process hygiene for the shell and for the final report
  - S18 => P1
  - S19 => P1,P2
  - S20 => not-testable: a heading that introduces the criteria below it
  - S21 => not-testable: the number of the first criterion, carrying no outcome
  - S22 => P1
  - S23 => P1
  - S24 => not-testable: the number of the second criterion, carrying no outcome
  - S25 => P2
  - S26 => P2
  - S27 => not-testable: the number of the third criterion, carrying no outcome
  - S28 => P3
  - S29 => P3
  - S30 => not-testable: the number of the fourth criterion, carrying no outcome
  - S31 => P4
  - S32 => P4
  - S33 => not-testable: the number of the fifth criterion, carrying no outcome
  - S34 => P5
  - S35 => not-testable: the number of the sixth criterion, carrying no outcome
  - S36 => P6
  - S37 => P6
  - S38 => not-testable: a pointer to the lines of the authority behind the criteria
  - S39 => not-testable: a statement about dependencies and about what is cheapest
  - S40 => not-testable: the rest of that statement about cost, naming no outcome
  - S41 => not-testable: the size the request estimates for this work
  - S42 => not-testable: the files the request expects this change to touch
  - S43 => not-testable: the reason the request calls this a real expectation
- **scenarios**:
  - SC1 | P1 | GIVEN a program of 2 functions sent to "check" | WHEN the tool answers it | THEN the answer carries a claim kind, a scope, the SHA-256 of the 2-function text and a 64-character dependency digest equal to the one "discover" publishes
  - SC2 | P2 | GIVEN that same program sent to each of the 6 operations this tool completes | WHEN each answers | THEN each answer names exactly 4 versions and says of the solver and the encoding "not applicable" with a reason of its own
  - SC3 | P3 | GIVEN a program declaring 2 examples | WHEN its examples are run | THEN the claim kind is "examples", the scope names the declared examples, and the answer carries exactly those 2 entries
  - SC4 | P4 | GIVEN that same 2-function program sent to "verify" | WHEN the inventory is answered | THEN every entry carries 2 separate fields, a logical result "not_attempted" and an execution status "unsupported"
  - SC5 | P5 | GIVEN a request object that raises while the tool reads 1 field of it | WHEN the tool is asked to answer it | THEN the answer carries status "tool_failure" with no claim, no result, no source digest and no provenance
  - SC6 | P6 | GIVEN an answer kept about a 2-function program and the same program with 1 function added | WHEN both are checked | THEN the 2 answers name 2 different revisions, the same dependency digest, and the manifest names both fields as the ones a client compares
- **conflicts**:
  - S1 | NONE | read pyproject.toml and the tests directory: a Python 3.12 project with a pytest suite, which nothing in this change alters
  - S2 | NONE | read SPEC.md lines 270-284 and 476-482: they ask for exactly the distinctions this request asks for
  - S3 | NONE | this change adds test files of its own and edits no existing test and no line of SPEC.md
  - S4 | NONE | the conflict found at S22 and S25 is reported to the owner here and no existing test is edited
  - S5 | NONE | nothing under .relay is read, imported or named by this change
  - S6 | NONE | all work happens in the worktree at prova-wt-f17 on its own branch
  - S7 | NONE | the commit message of this change ends with the line the request names
  - S8 | NONE | the co-author line is written exactly as the request spells it
  - S9 | NONE | nothing in this change pushes or merges anything
  - S10 | NONE | the whole suite is run before the change is recorded as done
  - S11 | NONE | the edits to service.py are local additions to the answers already built there
  - S12 | NONE | read service.py and manifest.py: claim, source_digest, source_revision and the published shapes are all there as described
  - S13 | NONE | the new block extends the published shapes and the one builder of an answer instead of repeating them
  - S14 | NONE | read SPEC.md lines 280-284 and the manifest: tool_failure is named there and no operation answers with it today
  - S15 | NONE | every script of this run lives under the nwstep workspace in a directory of its own
  - S16 | NONE | the laws name generated property tests, the RED command names only the new test files, and the witnesses are classes or defs
  - S17 | NONE | every submission is passed from a script file and git status is read before the final report
  - S18 | NONE | read every completed answer built in service.py: each carries a claim and a digest, so the outcome extends what is there
  - S19 | NONE | no answer names a version today, so nothing contradicts naming them
  - S20 | NONE | a heading above the criteria, contradicted by nothing in the code
  - S21 | NONE | the number of a criterion, contradicted by nothing in the code
  - S22 | CONFLICT | the accepted test tests/properties/test_i1_s4_p6_transcript.py pins the completed evaluate answer to exactly the 6 top-level fields operation, status, claim, source_digest, diagnostics and result, and pins its claim to exactly 2 keys, so no new field can reach the evaluate answer without editing that test | Should the provenance block be carried by the 6 operations the profile names and left off evaluate, this tool own extension, or should the pinned transcript test be widened to admit it?
  - S23 | NONE | the content asked for, a claim kind, a scope and 2 digests, is contradicted by no existing answer; only the operation evaluate is in question, recorded at S22
  - S24 | NONE | the number of a criterion, contradicted by nothing in the code
  - S25 | CONFLICT | the same pinned transcript test forbids a new field on the completed evaluate answer, so the 4 versions cannot be named there either | Should the 4 versions be named by the 6 operations the profile names and left off evaluate for the same reason?
  - S26 | NONE | no test names any version today, so saying which do not apply contradicts nothing
  - S27 | NONE | the number of a criterion, contradicted by nothing in the code
  - S28 | NONE | the examples answer already claims the kind examples with the scope declared examples, so the sentence agrees with what is there
  - S29 | NONE | the run answers one entry per declared example today, which is the scope the sentence asks for
  - S30 | NONE | the number of a criterion, contradicted by nothing in the code
  - S31 | NONE | an obligation entry carries one result field today and no test pins the set of fields of an entry
  - S32 | NONE | the vocabularies of SPEC.md lines 270-284 share no word, so 2 fields can be told apart
  - S33 | NONE | the number of a criterion, contradicted by nothing in the code
  - S34 | NONE | two accepted tests require tool_failure to stay out of the published statuses of an answered request, which this change keeps; nothing requires the service never to report a failure of itself
  - S35 | NONE | the number of a criterion, contradicted by nothing in the code
  - S36 | NONE | the tool keeps no answer and no state between requests, so an older result can only be one a client kept
  - S37 | NONE | an answer already names the revision it is about, and nothing presents it as current beyond that
  - S38 | NONE | read both ranges of SPEC.md: they carry the dimensions this request asks the answer to state
  - S39 | NONE | a statement about dependencies, contradicted by nothing in the code
  - S40 | NONE | the rest of that statement, contradicted by nothing in the code
  - S41 | NONE | the size estimate, contradicted by nothing in the code
  - S42 | NONE | service.py is where every answer is built, so it is where the block is added
  - S43 | NONE | read the answers the tool gives: only source_digest is there, as the sentence says
- **decisions**:
  - S22: Carry the provenance block on the 6 operations the profile names (check, verify, examples, parse, format, discover) and leave the evaluate answer exactly as it is, because the pinned transcript test is an accepted guard this delivery may not edit; the gap is reported to the owner and written in the documents.
  - S25: Name the 4 versions in that same block, so the versions reach the same 6 operations and evaluate keeps the answer it has today; the owner is asked the same question once.
  - DEC1: A failure of this tool is answered by the one place that turns an answer into the text the command prints, with status tool_failure, and tool_failure stays out of the published statuses of an answered request, which the manifest already explains.
  - DEC2: The dependency digest is the SHA-256 of the canonical JSON of the profile, the published language and the 4 versions, published by discover so a client can compare a kept answer with this tool.
  - DEC3: An obligation keeps result as its logical standing and gains execution_status, whose word unsupported comes from the execution vocabulary of SPEC.md lines 270-284, because this tool has no solver.
  - DEC4: No formal model (Quint): this change adds no state, no protocol, no concurrency and no crash behaviour; every answer stays one function of one request, so a model would restate the code.
  - DEC5: Jev was not asked: TYPESAFE_API_KEY is absent from this environment and from a login shell, so the client exits 3; every choice below was settled locally and is recorded here.
  - DEC6: A failure of the tool is observed through the public entry point the command calls, because no input of the command can make the tool fail inside itself without planting a defect; the limit is written in the documents.
  - DEC7: The published scope of an examples run stays the words it has today, and the test proves the scope is really only the declared examples by counting the entries against the examples the sent text declares.
- **mapping**:
  - P1 => test_every_completed_answer_names_the_dependencies_it_stands_on
  - P2 => test_every_completed_answer_names_all_four_versions
  - P3 => test_an_examples_run_calls_itself_an_examples_run
  - P4 => test_each_obligation_carries_both_a_logical_result_and_an_execution_status
  - P5 => test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool
  - P6 => test_the_manifest_tells_a_client_what_makes_a_kept_answer_stale
- **covers_scenarios**:
  - SC1 => test_every_completed_answer_names_the_dependencies_it_stands_on
  - SC2 => test_every_completed_answer_names_all_four_versions
  - SC3 => test_an_examples_run_calls_itself_an_examples_run
  - SC4 => test_each_obligation_carries_both_a_logical_result_and_an_execution_status
  - SC5 => test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool
  - SC6 => test_the_manifest_tells_a_client_what_makes_a_kept_answer_stale
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC6 => base differs
- **interfaces**:
  - I1: the prova command, one JSON request on standard input and one JSON answer on standard output
  - I2: the discover operation, which publishes the shape of every answer, the statuses and the limits a client reads
  - I3: the public entry point the command calls to turn one request into the one text it prints
- **matrix**:
  - I1.empty => a check request whose source field is the empty text => the answer refuses the empty text and carries no claim, no digest and no provenance
  - I1.unknown => an operation named fly, which this tool does not have => status unavailable with no claim and no provenance
  - I1.malformed => a check request whose source field holds the number 7 => status invalid_input naming the field source, with no provenance
  - I1.dependency-gone => n/a: a request is answered from its own text alone; this tool reads no file and calls no service while it answers
  - I1.repeated => the same check request sent twice => both answers carry the same revision, the same dependency digest and the same 4 versions
  - I1.concurrent => 2 requests answered by 2 processes at once => each answer carries the revision of its own text only, since neither process shares anything
  - I1.crash => n/a: the command writes no file and keeps no state, so a run stopped halfway leaves nothing to repair or to read
  - I2.empty => discover sent with no other field => the manifest is answered whole, with the dependency digest and the 4 versions in it
  - I2.unknown => a client looks up the operation build, which this tool does not answer => it is listed unavailable and carries no answer shape to read
  - I2.malformed => discover sent with a source field holding the number 7 => the manifest is answered as usual, because discover reads no field of the request
  - I2.dependency-gone => n/a: the manifest is read from this tool own tables, with no file and no service behind it
  - I2.repeated => discover asked twice => the same dependency digest and the same 4 versions both times
  - I2.concurrent => n/a: discover reads nothing another run can change, so 2 runs cannot meet over anything
  - I2.crash => n/a: discover writes nothing, so a run stopped halfway leaves nothing behind
  - I3.empty => the entry point called with an empty JSON object => status unavailable, because no operation is named, with no provenance
  - I3.unknown => the entry point called with the operation fly => status unavailable with the refusal that names it, and no provenance
  - I3.malformed => the entry point called with a request object that raises while 1 field is read => status tool_failure with no claim, no result, no digest and no provenance
  - I3.dependency-gone => n/a: nothing outside the process is read while an answer is built, so nothing can be gone
  - I3.repeated => the same request answered twice in 1 process => the 2 texts are identical, including both digests
  - I3.concurrent => n/a: the entry point keeps nothing between 2 calls, so 2 calls cannot meet over anything
  - I3.crash => n/a: nothing is written, so a call stopped halfway leaves nothing behind
- **laws**:
  - LAW1 | a completed answer stands on the dependency digest this tool publishes, and an answer that completed nothing carries no provenance at all | generator=test_every_completed_answer_says_what_it_stands_on | observation=for every operation and every kind of source, a completed answer carries the published dependency digest and a refusal carries none | mutant=the block stamped on every answer, refusals included
  - LAW2 | the revision an answer carries is the SHA-256 of exactly the characters sent, so 2 texts that differ never share one | generator=test_two_sources_never_share_one_revision | observation=the digest computed in the test from the text it sent equals the one in the answer, and no 2 texts map to one digest | mutant=a digest computed over the parsed program rather than the text sent
  - LAW3 | every one of the 4 versions a completed answer names is a version with a digit in it or a sentence saying it does not apply | generator=test_every_version_is_a_version_or_says_it_does_not_apply | observation=each of the 4 names carries a text that is one or the other, for every operation and every kind of source | mutant=an empty text or a bare null for a version that does not apply
- **messages**:
  - MSG1 | a request object that raises while the tool reads 1 field of it | the tool failed while it was answering, and the failure that was raised is named | the failure is of the tool itself, so nothing was read about the program and nothing is reported about it | send the request again and report the failure with the operation it names | test=test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool
- **red**: `uv run pytest -q tests/acceptance/test_f17_b1_every_answer_says_what_it_stands_on.py tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py tests/acceptance/test_f17_b3_an_examples_run_reaches_only_the_declared_examples.py tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py tests/acceptance/test_f17_b5_an_answer_about_an_older_source_says_so.py tests/unit/test_f17_b6_a_failure_of_the_tool_is_not_an_answer_about_a_program.py tests/properties/test_f17_provenance_laws.py` exited 1 in 4.349s
  - failing on the pre-feature tree (14): tests/acceptance/test_f17_b1_every_answer_says_what_it_stands_on.py::test_every_completed_answer_names_the_dependencies_it_stands_on, tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py::test_every_completed_answer_names_all_four_versions, tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py::test_the_two_this_tool_really_used_name_a_version, tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py::test_the_two_this_tool_has_none_of_say_so_with_a_reason, tests/acceptance/test_f17_b3_an_examples_run_reaches_only_the_declared_examples.py::test_an_examples_run_calls_itself_an_examples_run, tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py::test_each_obligation_carries_both_a_logical_result_and_an_execution_status, tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py::test_the_logical_result_and_the_execution_status_speak_their_own_words, tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py::test_this_tool_owes_every_obligation_and_ran_none_of_them, tests/acceptance/test_f17_b5_an_answer_about_an_older_source_says_so.py::test_the_tool_behind_both_answers_is_the_same_one, tests/acceptance/test_f17_b5_an_answer_about_an_older_source_says_so.py::test_the_manifest_tells_a_client_what_makes_a_kept_answer_stale, tests/unit/test_f17_b6_a_failure_of_the_tool_is_not_an_answer_about_a_program.py::test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool, tests/unit/test_f17_b6_a_failure_of_the_tool_is_not_an_answer_about_a_program.py::test_a_failure_of_the_tool_reports_nothing_about_a_program, tests/properties/test_f17_provenance_laws.py::test_every_completed_answer_says_what_it_stands_on, tests/properties/test_f17_provenance_laws.py::test_every_version_is_a_version_or_says_it_does_not_apply
  - tests (read from the run): 14 failed, 6 passed in 3.74s
  ```text
          answer = _ask({"operation": operation, "source": source})
          if answer["status"] != "completed":
              return
          named = (answer.get("provenance") or {}).get("versions")

  >       assert isinstance(named, dict) and sorted(named) == sorted(
              THE_VERSIONS_AN_ANSWER_NAMES
          ), (
              f"the completed {operation!r} answer names {named}: a reader "
              f"comparing two answers has to find each of "
              f"{sorted(THE_VERSIONS_AN_ANSWER_NAMES)} in both."
          )
  E       AssertionError: the completed 'check' answer names None: a reader comparing two answers has to find each of ['compiler', 'encoding', 'runtime', 'solver'] in both.
  E       assert (False)
  E        +  where False = isinstance(None, dict)
  E       Failing test case: test_every_version_is_a_version_or_says_it_does_not_apply(
  E           operation='check',  # or any other generated value
  E           source='(defn twice\n  (sig ((n Int)) -> Int ! pure)\n  (requires (> n 0))\n  (ensures (= result (* n 2)))\n  (examples (example (twice 2) => 4))\n  (* n 2))\n',
  E       )
  E       Explanation:
  E           These lines were always and only run by failing test cases:
  E               /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f17/red-tree/tests/properties/test_f17_provenance_laws.py:165

  tests/properties/test_f17_provenance_laws.py:167: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f17_b1_every_answer_says_what_it_stands_on.py::test_every_completed_answer_names_the_dependencies_it_stands_on
  FAILED tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py::test_every_completed_answer_names_all_four_versions
  FAILED tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py::test_the_two_this_tool_really_used_name_a_version
  FAILED tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py::test_the_two_this_tool_has_none_of_say_so_with_a_reason
  FAILED tests/acceptance/test_f17_b3_an_examples_run_reaches_only_the_declared_examples.py::test_an_examples_run_calls_itself_an_examples_run
  FAILED tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py::test_each_obligation_carries_both_a_logical_result_and_an_execution_status
  FAILED tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py::test_the_logical_result_and_the_execution_status_speak_their_own_words
  FAILED tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py::test_this_tool_owes_every_obligation_and_ran_none_of_them
  FAILED tests/acceptance/test_f17_b5_an_answer_about_an_older_source_says_so.py::test_the_tool_behind_both_answers_is_the_same_one
  FAILED tests/acceptance/test_f17_b5_an_answer_about_an_older_source_says_so.py::test_the_manifest_tells_a_client_what_makes_a_kept_answer_stale
  FAILED tests/unit/test_f17_b6_a_failure_of_the_tool_is_not_an_answer_about_a_program.py::test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool
  FAILED tests/unit/test_f17_b6_a_failure_of_the_tool_is_not_an_answer_about_a_program.py::test_a_failure_of_the_tool_reports_nothing_about_a_program
  FAILED tests/properties/test_f17_provenance_laws.py::test_every_completed_answer_says_what_it_stands_on
  FAILED tests/properties/test_f17_provenance_laws.py::test_every_version_is_a_version_or_says_it_does_not_apply
  14 failed, 6 passed in 3.74s
  ```

## 2. design: Find the owners and design the change (revision 1)

- **owners**:
  - the shape of every answer a client reads => src/prova/manifest.py, which already publishes a field with its kind, its presence and what it is for
  - which operation carries which answer field => src/prova/manifest.py, THE_OPERATIONS, where each operation already names its own answer fields
  - building the answer of each operation => src/prova/service.py, the only place that knows operation names
  - the revision of a submitted source => src/prova/service.py, SourceRevision, which this change leaves as the one thing that says which text an answer is about
  - the SHA-256 of a text => new: src/prova/provenance.py, Digest; two things are hashed now, the submitted source and this tool own description, and a second place writing the same algorithm would be a second decider
  - which versions stand behind an answer => new: src/prova/provenance.py; no module reads this tool own version, the interpreter or the absence of a solver today
  - what an obligation would have to show, and what happened to the attempt => src/prova/obligations.py, Obligation, which already owns the entry a client reads
  - the vocabulary of statuses an answered request carries => src/prova/service.py, STATUSES, left as it is so a failure of the tool stays outside it
- **reuse_decision**: Reused: the manifest field vocabulary (when completed), the one builder of a refusal, SourceRevision, the obligation entry and the statuses table; every one of them is extended where it already stands. Created new: src/prova/provenance.py, because no module owns what this tool is made of -- its own version, the interpreter under it, the absence of a solver and an encoder, and the digest over its published language; putting that in service.py would make the dispatcher decide facts about the tool, and putting it in manifest.py would make the catalogue of operations read the environment. The new module also takes over the SHA-256 of a text, which service.SourceRevision keeps using, so one place writes that algorithm.
- **paradigm**: oo
- **boundaries**:
  - the JSON answer a client reads: service.py owns it, and every new field is added where that answer is built
  - the published shape of an answer: manifest.py owns it, and the new field is published there for the six operations that carry it and for no other
  - one entry of the obligation inventory: obligations.py owns it, and the second field is added to the entry it already builds
  - the process this tool runs in: provenance.py is the only place that reads the interpreter and the package metadata, and it turns both into domain values at once
- **domain_types**:
  - Digest: the SHA-256 of a text, built only by hashing one, rendered as the hexadecimal a client compares
  - Version: one of the four things behind an answer, built either as a version this tool used or as a statement that it does not apply with its reason, never as both and never empty
  - Versions: exactly the four versions SPEC.md lines 270-284 ask for, held as one collection that cannot be built from another set of names
  - Provenance: what a completed answer stands on, a dependency digest and its versions, published as the one object every completed answer carries
  - Obligation (changed): gains the execution status beside the logical result it already carries, both constants of the type rather than values a caller sets
- **invariants**:
  - INV1 | every completed answer stands on the dependency digest this tool publishes, because the answer and the manifest read it from the one builder | witness=src/prova/service.py:_stands_on | bypass=none: nothing outside service.py builds an answer
  - INV2 | a version is either one this tool used or a statement that it does not apply with its reason, never both, never empty | witness=src/prova/provenance.py:Version | bypass=Python still lets a caller build the record by hand; the two named constructors are the only paths in this tool, and each refuses an empty text
  - INV3 | a provenance names exactly the four versions SPEC.md asks for; one built from another set of names refuses | witness=src/prova/provenance.py:Versions | bypass=none inside this tool
  - INV4 | the SHA-256 of a text is written in one place, so the revision of a source and the digest of the dependencies cannot drift apart in how they are spelled | witness=src/prova/provenance.py:Digest | bypass=none
  - INV5 | an obligation carries its logical result and its execution status as two fields whose vocabularies share no word, and neither is a value a caller can set | witness=src/prova/obligations.py:Obligation | bypass=none: both are constants of the type
  - INV6 | a failure of this tool is answered with a status no answered request carries, and with no claim, no result, no revision and no provenance | witness=src/prova/service.py:answer_text | bypass=a failure raised after the answer has been printed is outside this boundary and still reaches the caller as a broken run
- **prefactoring**: yes
- **prefactoring_reason**: One commit before the feature moves the SHA-256 of a text out of service.SourceRevision into the new provenance.Digest, with SourceRevision delegating to it. Behaviour is unchanged: the same algorithm over the same characters, the same hexadecimal rendered, no test edited and no answer field added. It comes first because the feature hashes a second thing, this tool own description, and without the move the algorithm would be written twice.

## 3. craft: Craft the change (revision 1)

- **refactor_commits**:
  - 7a2b7b6
- **refactor_check**: the check ran on the parent and on each refactor commit
  - 7a2b7b6c6507 (Write the digest of a text in one place): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 207.258s
  - tests (read from the run): 1297 passed in 207.09s
  - slowest: 9.77s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 6.41s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 5.66s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 4.88s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 4.18s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 3.96s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 2.87s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 2.39s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 2.37s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 2.06s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  5%]
  ........................................................................ [ 11%]
  ........................................................................ [ 16%]
  ........................................................................ [ 22%]
  ........................................................................ [ 27%]
  ........................................................................ [ 33%]
  ........................................................................ [ 38%]
  ........................................................................ [ 44%]
  ........................................................................ [ 49%]
  ........................................................................ [ 55%]
  ........................................................................ [ 61%]
  ........................................................................ [ 66%]
  ........................................................................ [ 72%]
  ........................................................................ [ 77%]
  ........................................................................ [ 83%]
  ........................................................................ [ 88%]
  ........................................................................ [ 94%]
  ........................................................................ [ 99%]
  .                                                                        [100%]
  ============================= slowest 10 durations =============================
  9.77s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  6.41s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  5.66s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  4.88s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  4.18s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  3.96s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  2.87s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  2.39s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  2.37s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  2.06s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1297 passed in 207.09s (0:03:27)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.148s
- **typesafe**: refused: the owner forbade the remote question service for this run; every open choice was settled locally and written down with its reason in the design record and in docs/feature/provenance. The key was also absent from this environment, so the client exits 3 here.

## 4. selfreview: Self-review (revision 1)

- **answers**:
  - D1: pass - the design record names a new owner for what this tool is made of, and src/prova/provenance.py holds exactly that, with service.py asking it in one place
  - D2: fixed:the SHA-256 of a text had two writers; the prefactor commit left one, and the discover answer now reuses the published claim field instead of repeating its text in manifest.py
  - D3: pass - provenance.py takes the published language as an argument and reads the process itself; it imports no dispatcher, so the direction stays one way
  - D4: fixed:src/prova/provenance.py:110 refuses any set of names but the four, and src/prova/provenance.py:82 refuses a version with nothing said about it, so neither state can be built
  - D5: pass - src/prova/provenance.py:57 holds two fields and tells rather than exposes them: written_into puts the version in the answer, and no caller reads the pair
  - D6: n/a:no pattern was introduced; value objects and a first-class collection are the shape this repository already uses for a boundary record
  - D7: pass - the words are the ones a reader of SPEC.md uses: a digest, a version, an obligation that stands somewhere and an attempt that was not supported; no Manager and no Helper
  - D8: pass - the only reads of the process, the package metadata and the interpreter, sit in one function at the edge of provenance.py and reach no decision about a program
  - D9: pass - tests/acceptance/test_f17_b1_every_answer_says_what_it_stands_on.py:36 drives the real command over its JSON surface; the one file that calls the public entry point says in its docstring why no input of the command can reach a failure of the tool
  - D10: pass - every test name is a sentence about what a client gets, with no production symbol and no process id in it
  - D11: pass - one fixtures module holds the program, the operations and the readers; no file re-implements them, and the property file is self-contained because it drives the shipped command only
  - D12: fixed:tests/properties/test_f17_provenance_laws.py:55 is the closed grid of 30 cells, and the case count of the two laws over it is the size of the grid, so each cell is drawn rather than a part sampled
  - D13: pass - nine runs of the seven files passed all 20 checks, median 6.61 s and slowest 6.67 s; the three checks that start no process run under 5 ms; nothing sleeps
  - D14: pass - each test adds an observation none of the others makes; the few that already passed before the change state behaviour the change must not break and say so
  - D15: pass - tests/acceptance/_f17_provenance_fixtures.py:99 says what is missing, why a reader needs it and what to carry; src/prova/provenance.py:86 does the same for a version built with nothing said
  - D16: n/a:the change adds no state, no protocol, no concurrency and no crash window: every answer is one function of one request, which the design records as DEC4
  - D17: fixed:the craft document reported a count measured on an earlier tree; it is re-measured on this one, and the gap at evaluate is written in the manifest documentation as well as in the documents
- **independent_review**:
  - REV1 | reviewer=rev-f17 | findings=5 (verdict APPROVE at b2593c9, one medium defect: discover published three fields as always present that a lowered answer budget takes away) | resolution=F1 F2 F3 and F4 were fixed after the review in four commits, each with the old behaviour re-injected to see the check fail; F5 needs nothing, the two messages are older than this change

## 5. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
- **not_verified**:
  - That a failure of the tool can be reached through the input of the command: it cannot without a defect planted on purpose, so it is observed through the public entry point the command calls, and the premise is the failure the answer names.
  - Anything about the evaluate answer, which this change leaves exactly as it was.
  - That the version named for the compiler is the version of the code that answered: it is read from the metadata of the installed package, which an install can leave behind a working tree.
  - The behaviour of this change under a solver or an encoder: there is none here, and both are reported as not applicable rather than tried.
  - The craft record of this run still names the prefactor commit by the id it had before the branch was moved onto the current main, and reports the count measured then; re-recording it refuses, because from the baseline this workspace exported the history now starts with a commit of the other delivery.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit ad39cedfdc39bc730b06056a065619a73748c353
  - no checks declared

## Not backed by the diff

- Every completed answer of the six operations the profile names now says what it stands on: the digest of this tool and of the language it reads, and the compiler, the encoding, the solver and the runtime behind it, each either a version or the reason there is none.: a guarantee names no test function of the change
- An obligation says where it stands as a statement and what happened to the attempt to settle it in two fields whose words share no vocabulary.: a guarantee names no test function of the change
- A failure inside the tool is answered as a failure of the tool, with no claim, no result and no revision, under a status an answered request never carries.: a guarantee names no test function of the change
- One operation is left out on purpose: evaluate keeps the answer it had, because an accepted test pins that answer to six fields and evaluate is this tool own operation, named in none of the operation categories of the authority; the manifest says so in words under documentation.stands_on, and the reader who wants it has to widen that test first.: a guarantee names no test function of the change
- The field is spelled stands_on rather than provenance because the word carries proven inside it and several accepted tests refuse any answer whose text says something was proven.: a guarantee names no test function of the change
- Checked by seven new test files driven over the shipped command, by three laws that each send one request per cell of a closed grid, and by the whole suite; each fix made after the independent review was seen to fail once with the old behaviour put back.: a guarantee names no test function of the change
