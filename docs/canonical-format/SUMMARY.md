# nwstep summary

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## Request coverage

- S1: Project: Prova compiler (Python 3.12, `uv run pytest -q tests`, 1198 tests, all green on main).
  - not-testable (challenge this): states the project, its test command and its green baseline, not a behaviour of the tool
- S2: Authority: SPEC.md.
  - not-testable (challenge this): names the document that holds the authority, not an outcome anyone can observe
- S3: Do not change SPEC.md or any existing test's expected result.
  - not-testable (challenge this): a constraint on how this change is made, not a behaviour the tool shows
- S4: If an existing test conflicts with the new rule, STOP and report the conflict (context, recommendation, options with consequences, one direct question); do not edit it.
  - not-testable (challenge this): tells me what to do when I find a contradiction, which is process and not behaviour
- S5: Ignore the .relay/ directory and anything Relay planned.
  - not-testable (challenge this): names a directory to leave alone while working, not a behaviour of the tool
- S6: Work in this git worktree only, on its branch.
  - not-testable (challenge this): says where the work happens, which no answer of the tool can show
- S7: Commit with a message ending in the line
  - not-testable (challenge this): constrains the commit message of this change, not what the tool answers
- S8: `Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>`.
  - not-testable (challenge this): the exact line the commit message ends with, which is process and not behaviour
- S9: Do not push and do not merge.
  - not-testable (challenge this): forbids pushing and merging, which no behaviour of the tool shows
- S10: Keep the full suite green.
  - not-testable (challenge this): a condition on the delivery, observed by running the suite rather than promised by the tool
- S11: Another delivery (F14, declared budgets: __main__.py, service.py, limits) runs in parallel in a different worktree; keep your service.py edits small and local.
  - not-testable (challenge this): says how large the edit to one file may be, which is process and not behaviour
- S12: F12 is on main: `parse` returns the tree the compiler builds (src/prova/tree.py, comments kept by src/prova/reader.py, a place on every node, conformance/parse fixtures); build the formatter on that tree and those comments, do not re-read the text a second way.
  - promises: P1, P2
  - tests P1: test_the_canonical_text_is_what_formatting_it_again_answers
  - tests P2: test_every_comment_is_written_once_and_in_the_order_it_was_written
- S13: F11 published operations in src/prova/manifest.py (format is `unavailable` there; make it available with request and response schemas, kept consistent with F11's laws; the one existing expectation that pins format as unavailable may change minimally, each such edit in its own commit and listed in your report).
  - promises: P6
  - tests P6: test_formatting_is_advertised_as_one_an_agent_may_ask_for
- S14: Process hygiene for zsh: quote `=>` and any `>` inside nwstep arguments, and pass submissions as files; run `git status --short` before your final message and leave it clean.
  - not-testable (challenge this): shell quoting and a clean working tree, which are process and not behaviour
- S15: **Outcome.** The Owner can run `format` on any accepted source and get the same
  - promises: P1
  - tests P1: test_the_canonical_text_is_what_formatting_it_again_answers
- S16: canonical text every time, with comments intact.
  - promises: P1, P2
  - tests P1: test_the_canonical_text_is_what_formatting_it_again_answers
  - tests P2: test_every_comment_is_written_once_and_in_the_order_it_was_written
- S17: **Acceptance criteria**
  - not-testable (challenge this): a heading introducing the criteria written under it
- S18: 1.
  - not-testable (challenge this): the number of the first criterion, which carries no behaviour of its own
- S19: Given any accepted program, when `format` runs, then it returns canonical text;
  - promises: P1
  - tests P1: test_the_canonical_text_is_what_formatting_it_again_answers
- S20: when `format` runs on that output, then the bytes are identical.
  - promises: P1
  - tests P1: test_the_canonical_text_is_what_formatting_it_again_answers
- S21: 2.
  - not-testable (challenge this): the number of the second criterion, which carries no behaviour of its own
- S22: Given a program with comments, then every comment appears once, in order,
  - promises: P2
  - tests P2: test_every_comment_is_written_once_and_in_the_order_it_was_written
- S23: attached to the following declaration, or at the end.
  - promises: P2
  - tests P2: test_every_comment_is_written_once_and_in_the_order_it_was_written
- S24: 3.
  - not-testable (challenge this): the number of the third criterion, which carries no behaviour of its own
- S25: Given non-canonical integer spellings such as `+002`, then the output is
  - promises: P3
  - tests P3: test_a_leading_plus_and_a_leading_zero_are_written_away
- S26: canonical and the program's meaning is unchanged.
  - promises: P3
  - tests P3: test_a_leading_plus_and_a_leading_zero_are_written_away
- S27: 4.
  - not-testable (challenge this): the number of the fourth criterion, which carries no behaviour of its own
- S28: Given formatted output, when it is checked and its examples run, then the
  - promises: P4
  - tests P4: test_the_canonical_text_is_still_an_accepted_program
- S29: results equal those of the original source.
  - promises: P4
  - tests P4: test_the_canonical_text_is_still_an_accepted_program
- S30: 5.
  - not-testable (challenge this): the number of the fifth criterion, which carries no behaviour of its own
- S31: Given an invalid program, then `format` refuses and returns no text.
  - promises: P5
  - tests P5: test_a_refusal_says_what_a_check_of_the_same_source_says
- S32: **SPEC.md** lines 60-63, 81-84.
  - not-testable (challenge this): points at the lines of the authority to read, not at an outcome to observe
- S33: **Dependencies** D7.
  - not-testable (challenge this): names the owner decision this work waits on, which is scheduling and not behaviour
- S34: **Size** L: a layout policy
  - not-testable (challenge this): an estimate of how large the work is, which nothing the tool answers can show
- S35: plus the fixtures SPEC.md requires before shipping it.
  - promises: P7
  - tests P7: test_the_published_source_is_answered_with_the_published_text
- S36: **Touches** new formatter area, `src/prova/service.py`, `conformance/` fixtures,
  - not-testable (challenge this): lists the places expected to change, which is a guess about the diff and not behaviour
- S37: tests.
  - not-testable (challenge this): continues the list of places expected to change
- S38: **Why it is a real expectation** `format` is refused today
  - promises: P6
  - tests P6: test_formatting_is_advertised_as_one_an_agent_may_ask_for
- S39: (`src/prova/service.py:15`).
  - not-testable (challenge this): a file and a line that locate today's refusal, not an outcome to observe
- S40: Owner decision D7 (the product owner recommendation stands), exactly as written in the roadmap:
  - not-testable (challenge this): introduces the owner decision quoted under it
- S41: **Context.** SPEC.md lines 81-84 require the canonical layout and the syntax-tree
  - promises: P7
  - tests P7: test_the_published_source_is_answered_with_the_published_text
- S42: interchange schema fixed in conformance fixtures before `format` ships, and say
  - promises: P7
  - tests P7: test_the_published_source_is_answered_with_the_published_text
- S43: formatting policy must not change language validity.
  - promises: P4
  - tests P4: test_the_canonical_text_is_still_an_accepted_program
- S44: **My recommendation: delegate both to me.** I will choose a layout, publish the
  - promises: P7
  - tests P7: test_the_published_source_is_answered_with_the_published_text
- S45: fixtures in the same change, and record the reasoning.
  - not-testable (challenge this): a promise to write the reasoning down in the documents, which no answer of the tool shows
- S46: These are presentation
  - not-testable (challenge this): part of the owner's reason for delegating the choice
- S47: choices with no semantic effect.
  - promises: P4
  - tests P4: test_the_canonical_text_is_still_an_accepted_program
- S48: | Option | Consequence |
  - not-testable (challenge this): the header row of the table of options in the quoted decision
- S49: |---|---|
  - not-testable (challenge this): the rule line under that table header
- S50: | Delegate (recommended) | F15 and F12 proceed.
  - not-testable (challenge this): the consequence of the option the owner took, which is scheduling and not behaviour
- S51: You review the fixtures afterwards if you want.
  - not-testable (challenge this): an offer to review the fixtures later, which is not an outcome of the tool
- S52: |
  - not-testable (challenge this): the closing cell of a row of the table of options
- S53: | You approve the layout first | F15 waits for you.
  - not-testable (challenge this): the consequence of the option the owner did not take
- S54: F12 can still proceed with the tree schema alone.
  - not-testable (challenge this): about another delivery's scheduling, not about what this tool answers
- S55: |
  - not-testable (challenge this): the closing cell of a row of the table of options
- S56: **Blocks** F15 only if you want to approve it.
  - not-testable (challenge this): says whether this work waits for approval, which is scheduling and not behaviour
- S57: F12 does not wait either way.
  - not-testable (challenge this): about another delivery's scheduling, not about what this tool answers
- S58: ---
  - not-testable (challenge this): a horizontal rule closing the quoted owner decision
- S59: The layout policy must be written down as fixtures before the formatter ships (SPEC.md lines 81-84): commit hand-written pairs (non-canonical source, canonical text) under conformance/format/ in the oracle step, computed by hand and not by running the tool.
  - promises: P7
  - tests P7: test_the_published_source_is_answered_with_the_published_text

## Edge matrix

- I1.empty: a request whose source field holds the empty text => status invalid_program, 1 syntax diagnostic saying the source holds no declaration and how to add one, and no result field | self-probe: not probed | pre-feature not probed
- I1.unknown: a program naming a type no declaration introduces => status invalid_program, a diagnostic naming the unknown type and where it stands, and no result field | self-probe: not probed | pre-feature not probed
- I1.malformed: a request whose source field holds the number 7 and not text => status invalid_input, 1 malformed_request diagnostic naming the source field, and no result field | self-probe: not probed | pre-feature not probed
- I1.dependency-gone: n/a (challenge this): formatting reads only the characters the request carries; it opens no file, reads no clock and calls nothing outside the process, so there is no dependency that can be gone
- I1.repeated: the same source sent to format twice in one process => the 2 answers are equal, and nothing anywhere is written or changed by either | self-probe: not probed | pre-feature not probed
- I1.concurrent: n/a (challenge this): formatting keeps no state between requests and writes nothing, so 2 requests running at once cannot observe or disturb one another
- I1.crash: n/a (challenge this): formatting writes no file and holds no lock, so a stop partway leaves no half-written output and nothing to recover
- I2.empty: a discover request carrying no field but the operation => the manifest still names format as available with its 2 published shapes | self-probe: not probed | pre-feature not probed
- I2.unknown: n/a (challenge this): discover reads no field of the request beyond the operation name, so there is no unknown value a client could send it
- I2.malformed: a request that is the number 7 and not an object with fields => status invalid_input, 1 malformed_request diagnostic, and no manifest | self-probe: not probed | pre-feature not probed
- I2.dependency-gone: n/a (challenge this): the manifest is built from this tool's own tables in manifest.py and checker.py, so there is no outside source it could lose
- I2.repeated: discover asked twice in one process => the 2 manifests are equal, since the answer is built from constants and nothing is kept | self-probe: not probed | pre-feature not probed
- I2.concurrent: n/a (challenge this): discover reads tables and writes nothing, so 2 readers at once cannot disturb each other
- I2.crash: n/a (challenge this): discover writes nothing anywhere, so a stop partway can leave nothing behind
- I3.empty: the directory conformance/format holding no pair at all => the suite fails, naming the 3 pairs it reads and saying that a layout nothing publishes is not fixed | self-probe: not probed | pre-feature not probed
- I3.unknown: a source published with no canonical text beside it => the suite fails, naming the file that has no partner, because half a pair fixes nothing | self-probe: not probed | pre-feature not probed
- I3.malformed: a published source the tool refuses as a program => the suite fails saying a fixture that fixes the layout must be a program the tool accepts | self-probe: not probed | pre-feature not probed
- I3.dependency-gone: n/a (challenge this): both halves of every pair are files of this repository, read from the checkout the suite runs in
- I3.repeated: the same pair read twice in one run => the same 2 texts, because the suite only reads the published files and writes neither | self-probe: not probed | pre-feature not probed
- I3.concurrent: n/a (challenge this): the suite only reads the published files, so 2 readers at once see the same characters
- I3.crash: n/a (challenge this): nothing writes the published pairs while the suite runs, so a stop partway cannot damage them

## Definition of done

- SC1 (P1): not-held (no held self-probe case)
  - GIVEN the 1-line source "(defn add-one   (sig ((n Int)) -> Int ! pure)   (ensures (= result (+ n 1)))   (examples (example (add-one 41) => 42))   (+ n 1))"
  - WHEN format runs on it, and then on the text it answered
  - THEN the 2 answers carry identical characters, written over 5 lines or more, ending with exactly 1 line terminator
  - test: test_the_canonical_text_is_what_formatting_it_again_answers
- SC2 (P2): not-held (no held self-probe case)
  - GIVEN a source whose 3 comments stand above the 1st declaration, above the 2nd, and inside the body of the last one
  - WHEN format runs
  - THEN each of the 3 comments stands exactly 1 time, in that order, and "; nothing follows this one" is the last line carrying anything
  - test: test_every_comment_is_written_once_and_in_the_order_it_was_written
- SC3 (P3): not-held (no held self-probe case)
  - GIVEN a program spelling its whole numbers "+0007", "0012", "+005" and "-0"
  - WHEN format runs, and the declared examples of both texts run
  - THEN the answered text holds none of those 4 spellings, holds 7, 12, 5 and 0, and the 1 example entry is equal to the one the source answered
  - test: test_a_leading_plus_and_a_leading_zero_are_written_away
- SC4 (P4): not-held (no held self-probe case)
  - GIVEN the reservation program SPEC.md publishes, which declares 7 examples
  - WHEN check, parse and examples run over its canonical text and over the source
  - THEN both texts are answered "completed", the 2 trees agree apart from where the nodes stand, and the 7 example entries are equal
  - test: test_the_canonical_text_answers_the_same_examples
- SC5 (P5): not-held (no held self-probe case)
  - GIVEN the source "(defn add-one", which stops after 1 unclosed parenthesis, and 3 more sources the tool refuses for 3 other reasons
  - WHEN format runs over each of the 4 and check runs over the same 4
  - THEN format answers each with the status check answers and the same 1 diagnostic, and carries no result field at all
  - test: test_a_refusal_says_what_a_check_of_the_same_source_says
- SC6 (P6): not-held (no held self-probe case)
  - GIVEN the tool as it ships, asked for its manifest with 0 other fields
  - WHEN discover runs
  - THEN the operations list says format is "available", the formatting category names format with that same word, and the published shapes name "source" and "result"
  - test: test_formatting_is_advertised_as_one_an_agent_may_ask_for
- SC7 (P7): not-held (no held self-probe case)
  - GIVEN the pair published as "shapes.prova" and "shapes.canonical.prova", 2 files written by hand from the layout policy
  - WHEN format runs on the 1st of the 2 files
  - THEN the answered text equals the 2nd file character for character, and formatting that 2nd text answers it again unchanged
  - test: test_the_published_source_is_answered_with_the_published_text

## Questions for the owner

- S13: The request asks to make format available and allows the one pinned expectation to change minimally: may I change that single line from "unavailable" to "available", in a commit of its own, and list it in my report?
  - existing behaviour: tests/unit/test_service_discover.py line 34 asserts the published operations list carries "format": "unavailable", and src/prova/manifest.py declares format as NotAnsweredYet, which refuses to publish any request or answer shape for it
  - status: decided at oracle
- S29: Does "the results equal those of the original source" mean the status, the diagnostics and the result payload, each answer still carrying the revision of its own text?
  - existing behaviour: every completed answer of this tool carries source_digest, the SHA-256 of the exact submitted characters built by service.SourceRevision, so the answer about the source and the answer about its canonical text can never be equal as whole objects
  - status: decided at oracle

## Observed side effects (git, BASE to HEAD)

- A conformance/format/clauses.canonical.prova (+10 -0 lines)
- A conformance/format/clauses.prova (+5 -0 lines)
- A conformance/format/comments.canonical.prova (+11 -0 lines)
- A conformance/format/comments.prova (+7 -0 lines)
- A conformance/format/integers.canonical.prova (+6 -0 lines)
- A conformance/format/integers.prova (+4 -0 lines)
- A conformance/format/nested.canonical.prova (+32 -0 lines)
- A conformance/format/nested.prova (+9 -0 lines)
- A conformance/format/shapes.canonical.prova (+15 -0 lines)
- A conformance/format/shapes.prova (+5 -0 lines)
- A docs/feature/format/design.md (+124 -0 lines)
- A docs/feature/format/oracle.md (+108 -0 lines)
- A src/prova/formatter.py (+442 -0 lines)
- M src/prova/manifest.py (+30 -1 lines)
- M src/prova/service.py (+53 -4 lines)
- M src/prova/syntax.py (+14 -0 lines)
- M src/prova/tree.py (+3 -9 lines)
- A tests/acceptance/_f15_format_fixtures.py (+123 -0 lines)
- A tests/acceptance/test_f15_b1_formatting_twice_answers_the_same_text.py (+69 -0 lines)
- A tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py (+98 -0 lines)
- A tests/acceptance/test_f15_b3_an_integer_is_written_one_way_only.py (+76 -0 lines)
- A tests/acceptance/test_f15_b4_the_canonical_text_means_what_the_source_meant.py (+94 -0 lines)
- A tests/acceptance/test_f15_b5_a_source_that_is_not_a_program_gets_no_text.py (+83 -0 lines)
- A tests/acceptance/test_f15_b6_the_manifest_offers_formatting.py (+83 -0 lines)
- A tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py (+94 -0 lines)
- A tests/properties/_f15_written_programs.py (+313 -0 lines)
- A tests/properties/test_f15_laws.py (+140 -0 lines)
- M tests/unit/test_service_discover.py (+1 -1 lines)

## Commits (git log, BASE to HEAD)

- 140aa21 Let a program say in which order it was written
- 888b318 Say how a program is written out, before anything writes one
- 7a0c4c3 Decide who answers what a program looks like written out
- f07631d Write a program out the one way it is written
- 7a0271f Say that writing a program out is something the tool does
- a2e62e6 Catch a number whose sign is dropped
- dd044b8 Stop a part that needs several lines being squeezed onto one

## 1. oracle: Frame the work and write the oracle (revision 1)

- **request**:
  - /Users/andrealaforgia/.cache/nwave/nwstep-runs/prova-f15/request.md
- **promises**:
  - P1: Asking the tool to format a program it accepts answers canonical text, and asking it to format that text answers exactly the same characters.
  - P2: Every comment the reader wrote stands once in the canonical text, in the order it was written, above the declaration that follows it, or after the last declaration when none follows.
  - P3: A whole number written with a leading plus or a leading zero comes back written the one canonical way, and the program answers what it answered before.
  - P4: The canonical text is a program the tool accepts, declares the same program as the source and answers the same examples.
  - P5: A source the tool does not accept is refused, and the refusal carries no text at all.
  - P6: An agent reading the manifest finds formatting offered with the shape of what it sends and the shape of what it gets back, and the word it carries is the word the operation answers with.
  - P7: The canonical layout is fixed by pairs published under conformance/format, each a source beside the one text the tool answers for it.
- **sentence_map**:
  - S1 => not-testable: states the project, its test command and its green baseline, not a behaviour of the tool
  - S2 => not-testable: names the document that holds the authority, not an outcome anyone can observe
  - S3 => not-testable: a constraint on how this change is made, not a behaviour the tool shows
  - S4 => not-testable: tells me what to do when I find a contradiction, which is process and not behaviour
  - S5 => not-testable: names a directory to leave alone while working, not a behaviour of the tool
  - S6 => not-testable: says where the work happens, which no answer of the tool can show
  - S7 => not-testable: constrains the commit message of this change, not what the tool answers
  - S8 => not-testable: the exact line the commit message ends with, which is process and not behaviour
  - S9 => not-testable: forbids pushing and merging, which no behaviour of the tool shows
  - S10 => not-testable: a condition on the delivery, observed by running the suite rather than promised by the tool
  - S11 => not-testable: says how large the edit to one file may be, which is process and not behaviour
  - S12 => P1,P2
  - S13 => P6
  - S14 => not-testable: shell quoting and a clean working tree, which are process and not behaviour
  - S15 => P1
  - S16 => P1,P2
  - S17 => not-testable: a heading introducing the criteria written under it
  - S18 => not-testable: the number of the first criterion, which carries no behaviour of its own
  - S19 => P1
  - S20 => P1
  - S21 => not-testable: the number of the second criterion, which carries no behaviour of its own
  - S22 => P2
  - S23 => P2
  - S24 => not-testable: the number of the third criterion, which carries no behaviour of its own
  - S25 => P3
  - S26 => P3
  - S27 => not-testable: the number of the fourth criterion, which carries no behaviour of its own
  - S28 => P4
  - S29 => P4
  - S30 => not-testable: the number of the fifth criterion, which carries no behaviour of its own
  - S31 => P5
  - S32 => not-testable: points at the lines of the authority to read, not at an outcome to observe
  - S33 => not-testable: names the owner decision this work waits on, which is scheduling and not behaviour
  - S34 => not-testable: an estimate of how large the work is, which nothing the tool answers can show
  - S35 => P7
  - S36 => not-testable: lists the places expected to change, which is a guess about the diff and not behaviour
  - S37 => not-testable: continues the list of places expected to change
  - S38 => P6
  - S39 => not-testable: a file and a line that locate today's refusal, not an outcome to observe
  - S40 => not-testable: introduces the owner decision quoted under it
  - S41 => P7
  - S42 => P7
  - S43 => P4
  - S44 => P7
  - S45 => not-testable: a promise to write the reasoning down in the documents, which no answer of the tool shows
  - S46 => not-testable: part of the owner's reason for delegating the choice
  - S47 => P4
  - S48 => not-testable: the header row of the table of options in the quoted decision
  - S49 => not-testable: the rule line under that table header
  - S50 => not-testable: the consequence of the option the owner took, which is scheduling and not behaviour
  - S51 => not-testable: an offer to review the fixtures later, which is not an outcome of the tool
  - S52 => not-testable: the closing cell of a row of the table of options
  - S53 => not-testable: the consequence of the option the owner did not take
  - S54 => not-testable: about another delivery's scheduling, not about what this tool answers
  - S55 => not-testable: the closing cell of a row of the table of options
  - S56 => not-testable: says whether this work waits for approval, which is scheduling and not behaviour
  - S57 => not-testable: about another delivery's scheduling, not about what this tool answers
  - S58 => not-testable: a horizontal rule closing the quoted owner decision
  - S59 => P7
- **scenarios**:
  - SC1 | P1 | GIVEN the 1-line source "(defn add-one   (sig ((n Int)) -> Int ! pure)   (ensures (= result (+ n 1)))   (examples (example (add-one 41) => 42))   (+ n 1))" | WHEN format runs on it, and then on the text it answered | THEN the 2 answers carry identical characters, written over 5 lines or more, ending with exactly 1 line terminator
  - SC2 | P2 | GIVEN a source whose 3 comments stand above the 1st declaration, above the 2nd, and inside the body of the last one | WHEN format runs | THEN each of the 3 comments stands exactly 1 time, in that order, and "; nothing follows this one" is the last line carrying anything
  - SC3 | P3 | GIVEN a program spelling its whole numbers "+0007", "0012", "+005" and "-0" | WHEN format runs, and the declared examples of both texts run | THEN the answered text holds none of those 4 spellings, holds 7, 12, 5 and 0, and the 1 example entry is equal to the one the source answered
  - SC4 | P4 | GIVEN the reservation program SPEC.md publishes, which declares 7 examples | WHEN check, parse and examples run over its canonical text and over the source | THEN both texts are answered "completed", the 2 trees agree apart from where the nodes stand, and the 7 example entries are equal
  - SC5 | P5 | GIVEN the source "(defn add-one", which stops after 1 unclosed parenthesis, and 3 more sources the tool refuses for 3 other reasons | WHEN format runs over each of the 4 and check runs over the same 4 | THEN format answers each with the status check answers and the same 1 diagnostic, and carries no result field at all
  - SC6 | P6 | GIVEN the tool as it ships, asked for its manifest with 0 other fields | WHEN discover runs | THEN the operations list says format is "available", the formatting category names format with that same word, and the published shapes name "source" and "result"
  - SC7 | P7 | GIVEN the pair published as "shapes.prova" and "shapes.canonical.prova", 2 files written by hand from the layout policy | WHEN format runs on the 1st of the 2 files | THEN the answered text equals the 2nd file character for character, and formatting that 2nd text answers it again unchanged
- **conflicts**:
  - S1 | NONE | ran uv run pytest -q tests on this worktree before writing anything: 1198 tests pass, so the stated baseline holds
  - S2 | NONE | read SPEC.md lines 60-63 and 81-84, which state the formatting rules this work implements
  - S3 | NONE | searched tests/ for every assertion about format: only tests/unit/test_service_discover.py pins it, and S13 grants that one exception by name
  - S4 | NONE | the two contradictions I found are recorded against S13 and S29 with their questions, and no existing test was edited while asking
  - S5 | NONE | the .relay directory holds no code this change reads, and no test in tests/ opens it
  - S6 | NONE | the work runs in the worktree /Users/andrealaforgia/dev/prova-wt-f15 on branch feat/f15, which nothing in the repository contradicts
  - S7 | NONE | nothing in the repository constrains the commit message, and this worktree declares no commit hooks at all
  - S8 | NONE | the co-author line is text inside a commit message; no test, hook or script in this repository reads one
  - S9 | NONE | no test, hook or script in this repository pushes or merges, so nothing already does what the sentence forbids
  - S10 | NONE | the baseline run of the whole suite passes, so keeping it green contradicts nothing the repository already does
  - S11 | NONE | read src/prova/service.py: its two dispatch tables and one runner per operation are all a new operation needs, so the edit stays inside them
  - S12 | NONE | read src/prova/tree.py and src/prova/reader.py: the typed tree and reader.Comment already carry every part, place and comment a formatter needs
  - S13 | CONFLICT | tests/unit/test_service_discover.py line 34 asserts the published operations list carries "format": "unavailable", and src/prova/manifest.py declares format as NotAnsweredYet, which refuses to publish any request or answer shape for it | The request asks to make format available and allows the one pinned expectation to change minimally: may I change that single line from "unavailable" to "available", in a commit of its own, and list it in my report?
  - S14 | NONE | zsh quoting and a clean working tree are about running this work; no behaviour of the tool depends on either
  - S15 | NONE | src/prova/service.py refuses format today, so there is no canonical text already answered for this outcome to contradict
  - S16 | NONE | src/prova/reader.py already keeps every comment with its characters and its place, so keeping them intact contradicts nothing it does
  - S17 | NONE | a heading over the criteria written under it; the repository states nothing about it
  - S18 | NONE | the number of the first criterion; nothing in the repository states anything about it
  - S19 | NONE | no operation of this tool writes a program out today, so no answer can disagree about what canonical text is
  - S20 | NONE | nothing in the repository answers text for a program, so no existing answer can disagree about its bytes
  - S21 | NONE | the number of the second criterion; nothing in the repository states anything about it
  - S22 | NONE | reader.Comment keeps each comment's characters and place, and conformance/parse/comments.prova shows them answered once and in order
  - S23 | NONE | tree.AttachedComments already hands a comment to the node that follows it and the rest to the document end, which is the rule this sentence states
  - S24 | NONE | the number of the third criterion; nothing in the repository states anything about it
  - S25 | NONE | reader.INT_RE accepts "+002" and syntax.IntLit keeps the whole number and not its spelling, so a canonical spelling is already reachable
  - S26 | NONE | the typed tree holds the number itself, so writing it the canonical way cannot reach anything that decides what the program means
  - S27 | NONE | the number of the fourth criterion; nothing in the repository states anything about it
  - S28 | NONE | the check and examples operations already answer about any submitted text, so both can be asked about a canonical text as well
  - S29 | CONFLICT | every completed answer of this tool carries source_digest, the SHA-256 of the exact submitted characters built by service.SourceRevision, so the answer about the source and the answer about its canonical text can never be equal as whole objects | Does "the results equal those of the original source" mean the status, the diagnostics and the result payload, each answer still carrying the revision of its own text?
  - S30 | NONE | the number of the fifth criterion; nothing in the repository states anything about it
  - S31 | NONE | service._checked_program already refuses a source it cannot read, and its Refusal class holds no result field at all, so a refusal already carries no text
  - S32 | NONE | read SPEC.md lines 60-63 and 81-84: they state the rules this work implements and contradict none of them
  - S33 | NONE | D7 is quoted in this request and nothing in the repository records a different decision about the layout
  - S34 | NONE | an estimate of how large the work is; nothing the repository holds states anything about it
  - S35 | NONE | conformance/ holds the parse pairs F12 published and no format pairs at all, so there is nothing to contradict
  - S36 | NONE | src/prova/service.py and conformance/ exist and hold no formatter and no format pairs, so the named places are free
  - S37 | NONE | searched tests/ and found no test of formatting, so nothing there contradicts adding them
  - S38 | NONE | read src/prova/service.py: format stands in UNAVAILABLE_OPERATIONS and is refused there, exactly as the sentence says
  - S39 | NONE | the refusal the sentence points at is in src/prova/service.py, now at line 28 rather than at line 15, and says the same thing
  - S40 | NONE | introduces the owner decision quoted under it; the repository states nothing about it
  - S41 | NONE | read SPEC.md lines 81-84: they ask for the canonical layout and the tree schema to be fixed in conformance fixtures before format ships
  - S42 | NONE | conformance/parse holds the tree pairs F12 published, so the schema half is already fixed and only the layout half is missing
  - S43 | NONE | nothing in the repository makes a layout decision at all, so no layout can be altering language validity today
  - S44 | NONE | the owner delegates the layout; nothing in the repository records an approved layout that a choice could contradict
  - S45 | NONE | the reasoning is written into the documents this delivery generates, which no test and no answer of the tool reads
  - S46 | NONE | part of the owner's reason for delegating the choice; nothing in the repository states anything about it
  - S47 | NONE | the typed tree the checker reads carries no layout at all, so a layout choice cannot reach what a program means
  - S48 | NONE | the header row of the table of options in the quoted decision; the repository states nothing about it
  - S49 | NONE | the rule line under that table header; the repository states nothing about it
  - S50 | NONE | the consequence of the option the owner took; it is scheduling and the repository states nothing about it
  - S51 | NONE | an offer to review the fixtures later; no test reads whether a fixture was approved
  - S52 | NONE | the closing cell of a row of the table of options; the repository states nothing about it
  - S53 | NONE | the consequence of the option the owner did not take; the repository states nothing about it
  - S54 | NONE | about another delivery's scheduling; F12 is already on main with its tree schema published
  - S55 | NONE | the closing cell of a row of the table of options; the repository states nothing about it
  - S56 | NONE | says whether this work waits for approval; the repository states nothing about scheduling
  - S57 | NONE | about another delivery's scheduling; F12 is already delivered on main
  - S58 | NONE | a horizontal rule closing the quoted owner decision; the repository states nothing about it
  - S59 | NONE | conformance/ has no format directory at all, so publishing the hand-written pairs there contradicts nothing
- **decisions**:
  - S13: Record the contradiction and put the question to the owner at the oracle pause. The request itself grants this single exception, so change only the word on line 34 of tests/unit/test_service_discover.py from "unavailable" to "available", in a commit of its own, and list that commit in the report. No other test's expected result is touched.
  - S29: Read "the results equal those of the original source" as the operation, the status, the diagnostics and the result payload, with each answer still carrying the revision of its own text. SPEC.md lines 480-482 make the revision the one thing that says which text an answer is about, so making the two revisions equal would be the real defect and would let evidence about one text certify another.
  - DEC1: The canonical layout is this. Every declaration starts at column 1, exactly 1 empty line stands between two declarations, and the text ends with exactly 1 line terminator. A deftype is written on 1 line. A defn is broken, with its name on the opening line and its signature, its requires, its ensures, its examples and its body each starting on its own line 2 columns further in. An examples clause is broken with 1 example per line. Every other form is written on 1 line unless it holds a let, an if or a match anywhere inside it; such a form writes its head and, when that part is itself written on 1 line, its first part on the opening line, and every remaining part on its own line 2 columns further in.
  - DEC2: Comments. Each comment stands on its own line at column 1 above the declaration that follows it, with no empty line between the comment and that declaration, in the order the reader wrote them. A comment no declaration follows stands after the last declaration, separated from it by 1 empty line. A comment written inside a declaration therefore rises to stand above the next declaration, which is what SPEC.md line 63 asks and what makes the layout idempotent: formatting again finds that comment in the place the rule already sends it.
  - DEC3: A whole number is written canonically, with no leading plus and no leading zero, and -0 is written 0 (SPEC.md lines 76-78). The typed tree carries the number and never its spelling, so this needs no choice beyond writing the number out.
  - DEC4: An empty requires or empty ensures clause is written away. Core-0 reads either as the empty conjunction, which is true, and SPEC.md line 204 says an omitted block means true, so the two spell one thing; the typed tree cannot tell them apart in any case.
  - DEC5: No formal model. Formatting is a pure function of one submitted text: it keeps no state, speaks no protocol, takes no lock and writes no file, so a Quint model would restate the idempotence law that the generated property test already searches for counterexamples to.
  - DEC6: The answer carries the canonical text under result.text, beside the claim, the source revision and the diagnostics list that every completed answer about a source already carries, so formatting reads like every sibling operation and an agent needs no new rule to read it.
  - DEC7: The formatter is built on the typed tree syntax.py already produces and on the comments reader.py already keeps. It reads no character of the submitted text itself, so there is no second reading of the source that could disagree with the first.
  - DEC8: Formatting writes no refusal of its own. It refuses through service._checked_program, the one rule every operation that reads a source already shares, so a source refused by check is refused by format in the same status and the same words.
- **mapping**:
  - P1 => test_the_canonical_text_is_what_formatting_it_again_answers
  - P2 => test_every_comment_is_written_once_and_in_the_order_it_was_written
  - P3 => test_a_leading_plus_and_a_leading_zero_are_written_away
  - P4 => test_the_canonical_text_is_still_an_accepted_program
  - P5 => test_a_refusal_says_what_a_check_of_the_same_source_says
  - P6 => test_formatting_is_advertised_as_one_an_agent_may_ask_for
  - P7 => test_the_published_source_is_answered_with_the_published_text
- **covers_scenarios**:
  - SC1 => test_the_canonical_text_is_what_formatting_it_again_answers
  - SC2 => test_every_comment_is_written_once_and_in_the_order_it_was_written
  - SC3 => test_a_leading_plus_and_a_leading_zero_are_written_away
  - SC4 => test_the_canonical_text_answers_the_same_examples
  - SC5 => test_a_refusal_says_what_a_check_of_the_same_source_says
  - SC6 => test_formatting_is_advertised_as_one_an_agent_may_ask_for
  - SC7 => test_the_published_source_is_answered_with_the_published_text
- **predictions**:
  - SC1 => base differs
  - SC2 => base differs
  - SC3 => base differs
  - SC4 => base differs
  - SC5 => base differs
  - SC6 => base differs
  - SC7 => base differs
- **interfaces**:
  - I1: the format operation of the JSON service, asked through the prova command on standard input and through service.handle
  - I2: the discover operation's manifest, where an agent reads whether formatting can be asked for, what it takes and what it answers
  - I3: the pairs published under conformance/format, which fix the canonical layout a reader writes against
- **matrix**:
  - I1.empty => a request whose source field holds the empty text => status invalid_program, 1 syntax diagnostic saying the source holds no declaration and how to add one, and no result field
  - I1.unknown => a program naming a type no declaration introduces => status invalid_program, a diagnostic naming the unknown type and where it stands, and no result field
  - I1.malformed => a request whose source field holds the number 7 and not text => status invalid_input, 1 malformed_request diagnostic naming the source field, and no result field
  - I1.dependency-gone => n/a: formatting reads only the characters the request carries; it opens no file, reads no clock and calls nothing outside the process, so there is no dependency that can be gone
  - I1.repeated => the same source sent to format twice in one process => the 2 answers are equal, and nothing anywhere is written or changed by either
  - I1.concurrent => n/a: formatting keeps no state between requests and writes nothing, so 2 requests running at once cannot observe or disturb one another
  - I1.crash => n/a: formatting writes no file and holds no lock, so a stop partway leaves no half-written output and nothing to recover
  - I2.empty => a discover request carrying no field but the operation => the manifest still names format as available with its 2 published shapes
  - I2.unknown => n/a: discover reads no field of the request beyond the operation name, so there is no unknown value a client could send it
  - I2.malformed => a request that is the number 7 and not an object with fields => status invalid_input, 1 malformed_request diagnostic, and no manifest
  - I2.dependency-gone => n/a: the manifest is built from this tool's own tables in manifest.py and checker.py, so there is no outside source it could lose
  - I2.repeated => discover asked twice in one process => the 2 manifests are equal, since the answer is built from constants and nothing is kept
  - I2.concurrent => n/a: discover reads tables and writes nothing, so 2 readers at once cannot disturb each other
  - I2.crash => n/a: discover writes nothing anywhere, so a stop partway can leave nothing behind
  - I3.empty => the directory conformance/format holding no pair at all => the suite fails, naming the 3 pairs it reads and saying that a layout nothing publishes is not fixed
  - I3.unknown => a source published with no canonical text beside it => the suite fails, naming the file that has no partner, because half a pair fixes nothing
  - I3.malformed => a published source the tool refuses as a program => the suite fails saying a fixture that fixes the layout must be a program the tool accepts
  - I3.dependency-gone => n/a: both halves of every pair are files of this repository, read from the checkout the suite runs in
  - I3.repeated => the same pair read twice in one run => the same 2 texts, because the suite only reads the published files and writes neither
  - I3.concurrent => n/a: the suite only reads the published files, so 2 readers at once see the same characters
  - I3.crash => n/a: nothing writes the published pairs while the suite runs, so a stop partway cannot damage them
- **laws**:
  - LAW1 | Writing an accepted program out twice answers the same characters as writing it out once | generator=test_writing_any_program_out_twice_answers_the_same_text | observation=the text the tool answers for the source and the text it answers for that text are compared character for character | mutant=a layout that keeps a run of spaces from the submitted text, so a program written on one line and its canonical text disagree on the second pass
  - LAW2 | The canonical text declares the same program as the source, apart from where its parts stand | generator=test_writing_any_program_out_keeps_the_program_it_declares | observation=the trees the parse operation answers for both texts are compared with the places and the comment attachments taken out | mutant=writing a whole number with its sign dropped, which changes the number the tree carries
  - LAW3 | Every comment of the source stands once in the canonical text, in the order it was written | generator=test_writing_any_program_out_keeps_every_comment_once_and_in_order | observation=the comments of the answered tree of the canonical text are compared with the list of comments the generator wrote into the source | mutant=dropping a comment that no declaration follows, so the last comment of a source disappears
  - LAW4 | The canonical text is accepted, and its declared examples answer what the source's examples answered | generator=test_writing_any_program_out_keeps_what_its_examples_answer | observation=the check status and the whole examples payload of both texts are compared entry by entry | mutant=writing the clauses of a match in the wrong order, so a program answers a different value for the same input
- **messages**:
  - MSG1 | a source that stops after an unclosed parenthesis, sent to format | the text is not a core-0 program: the reader met the end of the input with a form still open | a text the reader cannot read holds no tree to write out, so there is no canonical spelling of it | close the form at the line and column the refusal names, then ask for the text again | test=test_a_refusal_says_what_a_check_of_the_same_source_says
  - MSG2 | a source holding no declaration at all, sent to format | the source holds no declaration, and core-0 writes a program with a plus | an empty text names no program, so there is nothing to write out | add at least one (deftype ...) or (defn ...) form to the source | test=test_a_refusal_says_what_a_check_of_the_same_source_says
  - MSG3 | a program adding a whole number to true, sent to format | a rule of core-0 is broken, with the type expected and the type written both named at the place they stand | a program that breaks a rule of core-0 is not an accepted program, and only an accepted program has a canonical spelling | repair the operand at the place the refusal names, then ask for the text again | test=test_a_refusal_says_what_a_check_of_the_same_source_says
  - MSG4 | a program written with the division sign, sent to format | the construct is outside the core-0 profile, named as the construct it is rather than as a type error | core-0 declares no division operator, so no spelling of the form has a meaning here | write the calculation with an operator core-0 has, + - or *, then ask again | test=test_a_refusal_says_what_a_check_of_the_same_source_says
- **red**: `uv run pytest -q tests/acceptance/test_f15_b1_formatting_twice_answers_the_same_text.py tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py tests/acceptance/test_f15_b3_an_integer_is_written_one_way_only.py tests/acceptance/test_f15_b4_the_canonical_text_means_what_the_source_meant.py tests/acceptance/test_f15_b5_a_source_that_is_not_a_program_gets_no_text.py tests/acceptance/test_f15_b6_the_manifest_offers_formatting.py tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py tests/properties/test_f15_laws.py` exited 1 in 2.539s
  - failing on the pre-feature tree (24): tests/acceptance/test_f15_b1_formatting_twice_answers_the_same_text.py::test_the_canonical_text_is_what_formatting_it_again_answers, tests/acceptance/test_f15_b1_formatting_twice_answers_the_same_text.py::test_a_program_written_on_one_line_comes_back_written_on_several, tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py::test_every_comment_is_written_once_and_in_the_order_it_was_written, tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py::test_a_comment_stands_over_the_declaration_it_was_written_over, tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py::test_a_comment_that_no_declaration_follows_stands_at_the_end, tests/acceptance/test_f15_b3_an_integer_is_written_one_way_only.py::test_a_leading_plus_and_a_leading_zero_are_written_away, tests/acceptance/test_f15_b3_an_integer_is_written_one_way_only.py::test_the_program_answers_what_it_answered_before, tests/acceptance/test_f15_b4_the_canonical_text_means_what_the_source_meant.py::test_the_canonical_text_is_still_an_accepted_program, tests/acceptance/test_f15_b4_the_canonical_text_means_what_the_source_meant.py::test_the_canonical_text_declares_the_same_program, tests/acceptance/test_f15_b4_the_canonical_text_means_what_the_source_meant.py::test_the_canonical_text_answers_the_same_examples, tests/acceptance/test_f15_b5_a_source_that_is_not_a_program_gets_no_text.py::test_a_refusal_says_what_a_check_of_the_same_source_says[a, tests/acceptance/test_f15_b6_the_manifest_offers_formatting.py::test_formatting_is_advertised_as_one_an_agent_may_ask_for, tests/acceptance/test_f15_b6_the_manifest_offers_formatting.py::test_the_manifest_says_what_to_send_and_what_comes_back, tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_every_published_pair_is_one_this_suite_reads, tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_source_is_answered_with_the_published_text[comments], tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_source_is_answered_with_the_published_text[integers], tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_source_is_answered_with_the_published_text[shapes], tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_text_is_answered_with_itself[comments], tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_text_is_answered_with_itself[integers], tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_text_is_answered_with_itself[shapes], tests/properties/test_f15_laws.py::test_writing_any_program_out_twice_answers_the_same_text, tests/properties/test_f15_laws.py::test_writing_any_program_out_keeps_the_program_it_declares, tests/properties/test_f15_laws.py::test_writing_any_program_out_keeps_every_comment_once_and_in_order, tests/properties/test_f15_laws.py::test_writing_any_program_out_keeps_what_its_examples_answer
  - tests (read from the run): 27 failed, 5 passed in 2.09s
  ```text
  E         The generator writes only programs the tool accepts, so a refusal here is either a defect of the tool or of the generator; read the diagnostic to tell which
  E       assert 'unavailable' == 'completed'
  E
  E         - completed
  E         + unavailable
  E       Failing test case: test_writing_any_program_out_keeps_what_its_examples_answer(
  E           program=WrittenProgram(text='(defn fn0 (sig ((n Int)) -> Int ! pure) (ensures (= result (+ n 0))) (examples (example (fn0 0) => 0)) (+ n 0))\n',
  E            comments=()),  # or any other generated value
  E       )

  tests/properties/test_f15_laws.py:42: AssertionError
  =========================== short test summary info ============================
  FAILED tests/acceptance/test_f15_b1_formatting_twice_answers_the_same_text.py::test_the_canonical_text_is_what_formatting_it_again_answers
  FAILED tests/acceptance/test_f15_b1_formatting_twice_answers_the_same_text.py::test_a_program_written_on_one_line_comes_back_written_on_several
  FAILED tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py::test_every_comment_is_written_once_and_in_the_order_it_was_written
  FAILED tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py::test_a_comment_stands_over_the_declaration_it_was_written_over
  FAILED tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py::test_a_comment_that_no_declaration_follows_stands_at_the_end
  FAILED tests/acceptance/test_f15_b3_an_integer_is_written_one_way_only.py::test_a_leading_plus_and_a_leading_zero_are_written_away
  FAILED tests/acceptance/test_f15_b3_an_integer_is_written_one_way_only.py::test_the_program_answers_what_it_answered_before
  FAILED tests/acceptance/test_f15_b4_the_canonical_text_means_what_the_source_meant.py::test_the_canonical_text_is_still_an_accepted_program
  FAILED tests/acceptance/test_f15_b4_the_canonical_text_means_what_the_source_meant.py::test_the_canonical_text_declares_the_same_program
  FAILED tests/acceptance/test_f15_b4_the_canonical_text_means_what_the_source_meant.py::test_the_canonical_text_answers_the_same_examples
  FAILED tests/acceptance/test_f15_b5_a_source_that_is_not_a_program_gets_no_text.py::test_a_refusal_says_what_a_check_of_the_same_source_says[a program adding a number to true]
  FAILED tests/acceptance/test_f15_b5_a_source_that_is_not_a_program_gets_no_text.py::test_a_refusal_says_what_a_check_of_the_same_source_says[a program dividing, which core-0 has no operator for]
  FAILED tests/acceptance/test_f15_b5_a_source_that_is_not_a_program_gets_no_text.py::test_a_refusal_says_what_a_check_of_the_same_source_says[a text holding no declaration at all]
  FAILED tests/acceptance/test_f15_b5_a_source_that_is_not_a_program_gets_no_text.py::test_a_refusal_says_what_a_check_of_the_same_source_says[a text that stops after 1 unclosed parenthesis]
  FAILED tests/acceptance/test_f15_b6_the_manifest_offers_formatting.py::test_formatting_is_advertised_as_one_an_agent_may_ask_for
  FAILED tests/acceptance/test_f15_b6_the_manifest_offers_formatting.py::test_the_manifest_says_what_to_send_and_what_comes_back
  FAILED tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_every_published_pair_is_one_this_suite_reads
  FAILED tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_source_is_answered_with_the_published_text[comments]
  FAILED tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_source_is_answered_with_the_published_text[integers]
  FAILED tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_source_is_answered_with_the_published_text[shapes]
  FAILED tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_text_is_answered_with_itself[comments]
  FAILED tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_text_is_answered_with_itself[integers]
  FAILED tests/acceptance/test_f15_b7_the_published_pairs_are_what_formatting_answers.py::test_the_published_text_is_answered_with_itself[shapes]
  FAILED tests/properties/test_f15_laws.py::test_writing_any_program_out_twice_answers_the_same_text
  FAILED tests/properties/test_f15_laws.py::test_writing_any_program_out_keeps_the_program_it_declares
  FAILED tests/properties/test_f15_laws.py::test_writing_any_program_out_keeps_every_comment_once_and_in_order
  FAILED tests/properties/test_f15_laws.py::test_writing_any_program_out_keeps_what_its_examples_answer
  27 failed, 5 passed in 2.09s
  ```

## 4. design: Find the owners and design the change (revision 2)

- **owners**:
  - how the characters of a source become forms, and the comments kept with their characters and places => src/prova/reader.py
  - what a program declares, as the typed tree the checker walks => src/prova/syntax.py
  - the order a source writes its declarations => src/prova/syntax.py, as Program.in_source_order, moved there by the prefactor from tree.py
  - how a closed value, a whole number, a boolean and the unit value are written the way a program writes them => src/prova/values.py, render, reused unchanged
  - which comment stands before which thing => src/prova/tree.py, AttachedComments, reused: the formatter asks it at each declaration instead of deciding again
  - the one rule by which a submitted source becomes a checked program or a refusal => src/prova/service.py, _checked_program, reused unchanged
  - which operations exist and which of them this tool answers => src/prova/service.py
  - what an agent reads about an operation it may call => src/prova/manifest.py
  - the canonical text of a program: which form stands on one line, how deep each line stands, where the empty lines and the final line terminator go => new: src/prova/formatter.py, because no module writes a program out today and tree.py writes the JSON tree an agent reads, which knows nothing of lines on a page
  - the layout a reader writes against => new: conformance/format, the three published pairs; no production code reads them
- **reuse_decision**: Reused without change: reader.py for the forms and the comments, syntax.py for the typed tree, values.render for every literal and every example value, tree.AttachedComments for which comment stands before which thing, and service._checked_program for the one refusal every operation that reads a source shares. Extended in place: service.py moves format out of the refused operations into the two tables that already list what it answers, and gains one runner beside its siblings; manifest.py gives format its two published shapes instead of NotAnsweredYet. Created new: src/prova/formatter.py, because nothing in this tool writes a program out. tree.py was the only candidate and does not fit: it answers the JSON tree an agent reads, where a part carries its place as two numbers and never as a column on a page, so putting the layout there would make one module answer two different questions about the same tree. Moved: the order a source writes its declarations, from a private function of tree.py onto syntax.Program, so that the formatter and the tree reader ask the program rather than each reading its two lookup tables. An independent review then found that the first version of Form let any part open a form and flattened it onto the opening line, so a binding whose value was an if was written on one line while an identical second binding was written over several: one expression, two layouts by position. Word and NoWord were added so that a form's opening is typed as something that cannot break, which makes the rule structural rather than remembered.
- **paradigm**: oo
- **boundaries**:
  - the JSON request and the JSON answer => src/prova/service.py owns it; formatter.py never sees a request, a status, a claim or a diagnostic, and returns characters
  - the typed tree => src/prova/syntax.py owns it; formatter.py reads it and changes nothing in it
  - the characters of a submitted source => src/prova/reader.py owns reading them; formatter.py writes characters and reads none, so there is no second reading that could disagree with the first
  - what an agent is told about an operation => src/prova/manifest.py owns it; service.py prints the parts manifest.py hands it and writes no shape of its own
  - the layout fixed for a reader => conformance/format owns it; the test suite reads the pairs and no production code does
- **domain_types**:
  - Form, new in src/prova/formatter.py: one parenthesised form of the canonical text, holding the word that opens it and the parts written inside it. It answers how it is written and over how many lines, so no caller composes a line itself.
  - Layout, new in src/prova/formatter.py, with WhenItHoldsABrokenPart, Always and OnePartPerLine: the three ways a form spreads over lines, as objects a form holds rather than as flags read at each use. A let, an if, a match and a defn are Always; an examples clause is OnePartPerLine; every other form takes the first.
  - Indent, new in src/prova/formatter.py: how far from the left margin a line stands, and the one answer to what two columns further in means.
  - CanonicalText, new in src/prova/formatter.py: the paragraphs one program is written as. It owns the single empty line between two declarations and the single line terminator the text ends with.
  - syntax.Program, changed: gains in_source_order(), the one answer to the order a source writes its declarations, moved from tree.py where a reader of its two lookup tables decided it from outside.
  - manifest.Operation for format, changed: its traffic becomes the published request and answer shapes instead of NotAnsweredYet, which is what makes the Catalogue publish them at all.
  - Word, new in src/prova/formatter.py: a part of the canonical text written on one line whatever the program holds -- a name, a whole number, a marker token, an operator, or a whole pattern, which core-0 builds out of literals, names and constructors and never out of a let, an if or a match. It is the only thing a form may open with.
  - NoWord, new in src/prova/formatter.py: what a parenthesised list opens with where core-0 gives it no word of its own, the bindings of a let and the parameters of a signature. A Null Object rather than an absent word, so no reader of a form asks whether there is a word before deciding what to write.
- **invariants**:
  - INV1 | The canonical text is a function of the typed tree and the comments alone: no character of the submitted source reaches it, so two sources that declare one program are written out identically | witness=src/prova/formatter.py:canonical_text | bypass=none
  - INV2 | Every parenthesised form of the canonical text is written by one object, so whether a form stands on one line is decided in one place and never at a call site | witness=src/prova/formatter.py:Form | bypass=none
  - INV3 | How deep a line stands is answered by one object, so two columns further in means the same thing everywhere | witness=src/prova/formatter.py:Indent | bypass=none
  - INV4 | A comment is handed to the thing that follows it by the object that already decides that for the published tree, never by a second rule of the formatter | witness=src/prova/tree.py:AttachedComments | bypass=none
  - INV5 | The order a source writes its declarations is answered by the program itself, so the formatter and the tree reader cannot disagree about it | witness=src/prova/syntax.py:Program | bypass=none
  - INV6 | An operation this tool advertises as available publishes the shape of its request and of its answer, and one it refuses publishes none; neither can be announced without the other | witness=src/prova/manifest.py:Catalogue | bypass=none
  - INV7 | A form opens with something that is written on one line by construction, so the opening line of a form written over several lines can always be built and no part that must break is ever flattened to fit it | witness=src/prova/formatter.py:Word | bypass=none
- **prefactoring**: yes
- **prefactoring_reason**: tree.py decides the order a source writes its declarations by reading Program's two lookup tables from outside, in a private function tree._in_source_order. The formatter needs that same order, and a second copy of it would be a second decider of one fact. One commit before the feature moves the decision onto syntax.Program as in_source_order() and leaves tree.py calling it: the same declarations, sorted by the same places, in the same tuple, so every existing test of the published tree passes unchanged and no test is edited.

## 6. craft: Craft the change (revision 2)

- **refactor_commits**:
  - 140aa21fc6d75197cfe5eee2833d66dfb82585ad
- **refactor_check**: the check ran on the parent and on each refactor commit
  - 140aa21fc6d7 (Let a program say in which order it was written): before exit 0, after exit 0
- **green**: `uv run pytest -q tests --durations=10` exited 0 in 146.816s
  - tests (read from the run): 1234 passed in 146.67s
  - slowest: 7.40s call tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  - slowest: 4.81s call tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  - slowest: 4.27s call tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  - slowest: 3.67s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  - slowest: 3.40s call tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  - slowest: 3.01s call tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  - slowest: 2.17s call tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  - slowest: 1.80s call tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  - slowest: 1.71s call tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  - slowest: 1.54s call tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  ```text
  ........................................................................ [  5%]
  ........................................................................ [ 11%]
  ........................................................................ [ 17%]
  ........................................................................ [ 23%]
  ........................................................................ [ 29%]
  ........................................................................ [ 35%]
  ........................................................................ [ 40%]
  ........................................................................ [ 46%]
  ........................................................................ [ 52%]
  ........................................................................ [ 58%]
  ........................................................................ [ 64%]
  ........................................................................ [ 70%]
  ........................................................................ [ 75%]
  ........................................................................ [ 81%]
  ........................................................................ [ 87%]
  ........................................................................ [ 93%]
  ........................................................................ [ 99%]
  ..........                                                               [100%]
  ============================= slowest 10 durations =============================
  7.40s call     tests/properties/test_i1_s3_p4.py::test_p4_ill_typed_current_is_rejected_distinctly
  4.81s call     tests/properties/test_i1_s3_p3.py::test_p3_malformed_current_text_is_rejected_distinctly
  4.27s call     tests/properties/test_i1_s3_p3_field_count_and_constructor.py::test_p3_field_count_and_unknown_constructor_rejected_as_input_failure
  3.67s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_interleaved_sequences_keep_per_request_verdicts
  3.40s call     tests/properties/test_r1_p1_every_mangled_request_is_answered_with_one_json_response.py::test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly
  3.01s call     tests/properties/test_s1_b2_no_forbidden_claim_property.py::test_no_evaluate_run_ever_emits_a_forbidden_claim
  2.17s call     tests/properties/test_i1_s3_p5_interleaved.py::test_p5_valid_request_follows_every_rejection_family
  1.80s call     tests/properties/test_i1_s3_p4.py::test_p4_finite_families_exhaustively_crossed_with_both_events
  1.71s call     tests/properties/test_i1_s6_p5.py::test_p5_mixed_sequence_each_response_matches_its_own_request
  1.54s call     tests/properties/test_f1_hour_clock_dial_property.py::test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it
  1234 passed in 146.67s (0:02:26)
  ```
- **scorecard**: `uv run python -m compileall -q src tests` exited 0 in 0.054s
- **typesafe**: unavailable: TYPESAFE_API_KEY is absent from this environment. The client was run from a shell command at the first eligible question, the choice between attaching a comment to the following declaration and to the following syntax node, and reported the key missing; that choice was then put to the owner and answered by the owner, and the remaining choices were settled locally and recorded as decisions in the oracle and design records.

## 7. selfreview: Self-review (revision 2)

- **answers**:
  - D1: pass - the committed change is the design record: one new owner (src/prova/formatter.py) for the canonical text, service.py moving format into the two tables it already keeps plus one runner, manifest.py giving it the two published shapes, and the prefactor moving the declaration order onto the program. The owner's option C is in the code: the manifest result description states the format/parse difference plainly.
  - D2: pass - no fact is decided twice. values.render stays the one answer to how a program writes a whole number, a boolean and the unit value, so the formatter adds no spelling rule; tree.AttachedComments stays the one answer to which comment stands before which thing; the prefactor removed the second place that worked out the order a source writes its declarations rather than adding a third.
  - D3: pass - dependencies point one way. formatter.py imports syntax, reader.Comment, tree and values and never service; service.py imports formatter and never the layout; formatter.py sees no request, status, claim or diagnostic and returns characters, so the JSON boundary stays in service.py.
  - D4: fixed:src/prova/formatter.py:87 - the depth of a line was an int passed around, which any caller could have added 3 to; Indent owns it and answers deeper() once, and the probe that changed it to three columns was noticed. A form also used to open with any part at all and flattened it, which an independent review caught: a form now opens with a Word or a NoWord, neither of which can need a second line. This repository runs no type checker, so that is centralised construction plus a loud failure (a Form answers no opens and raises AttributeError), not a static guarantee; it is stated that way in the code and the design.
  - D5: pass - src/prova/formatter.py:104 - Form holds three instance variables, its opening, its parts and its layout; Calisthenics rule 8 asks for two, and the third is the opening, which is what the review's defect required to be a thing of its own rather than the first element of the parts. It tells rather than asks: it answers written() and flat() and exposes no field for a caller to branch on. The three layout classes and NoWord replace flags and an absent-value check, so there is no else in the deciding code. Second deliberate break: those classes carry no state, which rule 10 warns about; they are a Strategy and a Null Object.
  - D6: pass - two patterns and no more: Strategy for how a form spreads over lines, and the table of one lambda per node kind that tree.py already uses for the same tree, so a reader moving between the two files meets the same shape. No framework, no base class for a single caller.
  - D7: n/a:this is a compiler, not a domain with aggregates, repositories or domain events. The nearest thing to an aggregate is syntax.Program, and the change gives it a method about its own declarations rather than letting a reader work it out from its two tables.
  - D8: pass - no infrastructure entered the domain. formatter.py opens no file, reads no clock, calls no process and keeps no state; the only file reading in the change is the test suite reading the published pairs under conformance/format, and no production code reads them.
  - D9: pass - tests/acceptance/_f15_format_fixtures.py:24 - every check reaches the tool through service.handle with a JSON request, the same surface the prova command drives, and asserts on the answered JSON. No test imports formatter, Form or Indent, so renaming any of them leaves every check green.
  - D10: pass - each test name is a sentence about what the Owner gets: the canonical text is what formatting it again answers; every comment is written once and in the order it was written; a source the tool refuses is answered without any text. No test name carries a production symbol, a layer or a process id.
  - D11: pass - one helper module per test directory, as this repository already does: _f15_format_fixtures.py for the acceptance checks and _f15_written_programs.py for the generated ones. Neither owns a whole scenario; each test writes its own Given, When and Then.
  - D12: fixed:tests/properties/test_f15_laws.py:56 - four laws over generated programs, one law each. Fixed twice. After my own probe: breaking the writer so that it wrote a number's size and dropped its sign was noticed by nothing, because no generated expression held a number below zero; the generator now draws from -9 to 9. After the independent review: no generated program put a form that must break where a form opens, so the three shapes bound-branch, picked and summed were added, and the laws now draw the same 40 programs every run (derandomize=True), shown by two separate processes drawing an identical list.
  - D13: pass - the 32 new checks run in 0.39s together; the slowest single one is 0.06s, a property of 40 cases, and the other 28 are under 5ms. Run nine times in a row they passed nine times, wall-clock median 0.507s and slowest 0.521s, so none is flaky. The whole suite is 1230 passed in 147.16s, against 1198 in 148.10s before.
  - D14: pass - no two checks make the same observation. The idempotence of a worked example and the idempotence of every generated program are a different reach, not a repeat; the published pairs are the only check of the exact characters; the refusal pair is split into the promise the tool already kept, that a refusal carries no text, and the one it did not, that the refusal says what a check says.
  - D15: pass - tests/acceptance/test_f15_b2_every_comment_is_kept_once_and_in_order.py:56 - every failure message says what failed with the values, why it matters and what to do: a lost comment drops what a reader said and a repeated one invents it, so hand each comment to exactly one place. The refusals the operation itself gives are the shared ones, which already name the rule, the place and the repair.
  - D16: pass - recorded as 'No model for the canonical text of a program is canonical already: there is no shared state, no protocol with more than one step, no concurrency window and no crash window.' Writing a program out reads one text, keeps nothing and writes no file. quint is not installed here either, which is a capability limit and not a check that passed; the law is searched for counterexamples by generated property tests against the real tool.
  - D17: pass - the documents say what was proved and what was not. The oracle says no formatter existed when it was written and now says which pairs were published later and why; the design says what enforces the typed opening in a repository with no type checker, with the AttributeError it raises; the handoff carries the pre-existing long-integer crash that is not this work's, the two operations' different comment placing, and that the two new pairs were committed in the same commit as the fix they check.
- **independent_review**:
  - REV1 | reviewer=independent-review-f15 | findings=6 (verdict REJECT at a2e62e6) | resolution=D1 G1 N1 N2 fixed in dd044b8, D2 logged in the roadmap as robustness item R2, N3 stated as by design
  - REV2 | reviewer=independent-review-f15 | findings=4 (verdict APPROVE at dd044b8, none blocking) | resolution=N4 wording corrected, N5 stated in the handoff, D2 and N3 carried as stated limits

## 8. handoff: Hand off (revision 1)

- **summary** (sentences the diff backs):
  - Writing a core-0 program out is now something the tool does.
  - An independent review rejected a first version for flattening a part that needed several lines onto an opening line, and that is repaired by giving a form an opening that cannot need a second line.
  - Two things the next reader should know: a comment written inside a declaration rises out of it, so this operation and the one that reads a program as a tree place comments differently, which the manifest says; and the two pairs added for the repair were committed with the repair rather than before it.
- **not_verified**:
  - The canonical layout is a choice, not a finding. The owner delegated it and has accepted the shape the published pairs show, including the opening parenthesis that stands alone where the first part of a list must be written over several lines. Nothing here shows it reads well to anyone else; the five pairs under conformance/format are what to look at.
  - A comment written inside a declaration rises to stand over the next declaration, or to the end. That is what acceptance criterion 2 asks for. SPEC.md line 63 says the following syntax node, which is what the parse operation does instead, so the two operations place a comment differently. The difference is published in the manifest text an agent reads and is carried as its own follow-up expectation; it is not a defect of this work and it is not fixed here.
  - The typed opening of a form is not statically guaranteed. This repository runs no type checker, so what keeps a part that must break out of an opening line is that every form is built inside formatter.py and that a form handed to another form as its opening raises AttributeError rather than quietly flattening. A caller outside that module could still build one by hand.
  - A whole number of more than about 4300 digits makes the tool fail with a ValueError from reader.py rather than refuse the source. It does so on the base commit too, for the check operation, with no formatter involved, so it is not this work's defect; it is logged separately as a robustness item. Formatting such a source fails the same way.
  - The two pairs nested and clauses were committed in the same commit as the fix they check, not before it. They were worked out by hand from the published rules and not by running the tool, and the fix was separately shown to be needed by re-injecting the defect and watching a check go red; but nobody saw those two pairs fail before the code that satisfies them existed.
  - No formal model was written and none was possible to run here: quint is not installed on this machine. The idempotence and meaning-preserving laws are searched for counterexamples by generated property tests over 40 programs each, which is evidence and not proof.
  - The generated programs cover the declaration shapes the generator writes, not every program core-0 can express: there is no nesting beyond the shapes listed, no deeply nested data, and no program near the reading limit.
  - Nothing was measured about how the tool behaves under two requests at once, under interruption, or against a file on disk, because formatting keeps no state, holds no lock and writes no file.
- **pre-review receipt** (run by the tool when this record was written):
  - candidate: commit dd044b80b7f70c7a3e32b2caa4038bc9d2d0d8a4 with uncommitted changes
  - no checks declared

## Not backed by the diff

- Ask for the canonical text of any program it accepts and the same characters come back every time, with the reader's comments kept once each and in the order they were written, and whole numbers written the one canonical way; a source that is not a program is refused exactly as a check refuses it and carries no text at all.: a guarantee names no test function of the change
- The layout is published as eight rules and as five hand-computed pairs under conformance/format, each a source a reader might write beside the one text answered for it, worked out by hand and not by running the tool.: a guarantee names no test function of the change
- It is decided by the shape of the program and never by how wide a line has grown, which is what makes asking twice give the same answer.: a guarantee names no test function of the change
- A new module owns the text and nothing else: it is handed the tree the tool already builds and the comments the reader already kept, sees no request and no status, and reads no character of the submitted source.: a guarantee names no test function of the change
- One commit before the feature moved the order a source writes its declarations onto the program itself, so no second place works it out.: a guarantee names no test function of the change
- Checked by driving the tool's own JSON surface: worked examples for each promise, four laws over generated programs that draw the same cases every run, and the five published pairs compared character for character.: a guarantee names no test function of the change
- Eight deliberately re-injected defects were each caught by a check.: a guarantee names no test function of the change
