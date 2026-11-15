# F6 — Names and markers must be spelled as the language defines them

## Oracle: what the tests promise, before any code exists

### The promises

| # | Promise |
|---|---|
| P1 | A function declared with a word the language reserves is refused, and the refusal names that word. |
| P2 | A function or parameter name that starts with a capital is refused, and a type or constructor name that starts lower-case is refused. |
| P3 | A signature whose arrow or effect marker is anything other than `->` and `! pure` is refused — including the signature that leaves them out, which answers with that refusal instead of crashing. |
| P4 | A declared example whose arrow is not `=>` is refused. |
| P5 | A source that declares nothing at all is refused. |
| P6 | A function whose `(examples)` clause holds no example is refused. |
| P7 | Every refusal of a misspelled name or marker is placed at the line the misspelling stands on. |
| P8 | Every source, however truncated or mangled, gets one answer from every operation that reads source: a refusal with a place, never a traceback. |
| P9 | The source that declares nothing gets the identical refusal from `check`, `examples`, `verify` and `evaluate`. |
| P10 | A constructor may not be named for one of the builtin type names core-0 reserves. |

P8, P9 and P10 were added after the independent review: the reader still
raised `IndexError` and `AttributeError` on 17 further malformed shapes (every
grammar position core-0 fixes, left empty or filled with the wrong kind of
form), the equality of the empty-source refusal across the four operations was
asserted nowhere, and a constructor named `Int` was accepted. P8 and P9 are
proved by the enumerated family in
`tests/properties/test_f6_every_malformed_source_still_answers.py`; P10 by the
refusal and its accepted twin in `test_f6_b2_...`.

Criterion 7 of the request — the hour clock, the reservation example and
`conformance/add-one.prova` still check — is a preservation sentence, not a
change. It is pinned by `tests/acceptance/test_f6_b6_the_shipped_programs_still_check.py`,
which passes before and after the change. It carries no promise in the oracle
record, because the record only accepts a promise whose test can be seen failing
first.

### What the tests are

All acceptance tests drive the installed `prova` command over its real JSON
stdin/stdout surface; they import nothing from `src/prova`. The property tests
drive the same public operation in process.

| File | What it observes |
|---|---|
| `tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py` | each of the 26 words whose spelling this rule refuses as a function name, plus an unreserved control |
| `tests/acceptance/test_f6_b2_names_that_start_with_the_wrong_case_are_refused.py` | `Add-one`, the parameter `N`, the type `point`, the variant `red`, plus the same programs with the defined first letters |
| `tests/acceptance/test_f6_b3_a_mangled_signature_marker_is_refused.py` | the arrowless signature answering instead of crashing, the three mangled markers, the placement on line 2 |
| `tests/acceptance/test_f6_b4_an_example_with_the_wrong_arrow_is_refused.py` | the example arrow, and the placement on line 3 |
| `tests/acceptance/test_f6_b5_a_source_declaring_nothing_is_refused.py` | the empty source, a comment-only source, an empty `(examples)` clause |
| `tests/acceptance/test_f6_b6_the_shipped_programs_still_check.py` | the three shipped programs still accepted (preservation) |
| `tests/properties/test_f6_name_and_marker_spelling.py` | the three design laws, generated |

Seen RED first: the recorded RED command ran on the pre-feature tree with these
test files copied over it; 20 tests failed there and every mapped test is among
them.

### Decisions taken while writing the oracle

- **One category, no new word.** All seven rules are reported in the published
  `syntax` category. SPEC.md places every one of them in its lexical rules and
  core grammar, and `syntax` already means *source the tool cannot read as a
  program*. A new category would split one meaning in two and oblige every
  caller to learn a second word for the same defect.
- **A refusal now says where.** A `syntax` diagnostic will carry the location
  the error already holds. This adds a field to a response and removes nothing.
- **Scope of the name rules.** They apply to declared function names, parameter
  names, type names and constructor names. Field names are a value-name
  position too, but no criterion names them.
- **`result` is not swept (owner decision, after the parallel delivery landed).**
  SPEC.md reserves `result` for the value a postcondition speaks about: a rule
  about what a name *binds*, not about how a name is *spelled*. The
  whole-program check owns it and publishes its own refusal for it, so the
  spelling rule lets the word through and the sweep covers the other 26 words.
  Sweeping it here asked the spelling rule for an answer another rule owns, and
  made a parameter named `result` come back in the wrong category.
- **Uses of a name are untouched.** A lower-case type *reference* keeps its
  present answer, the checker's unknown-type refusal.
- **Conflict found and decided (request sentence S34).** One unit test sends the
  empty source to every advertised operation and reads the status back. The
  empty-program rule makes that answer `invalid_program` for the four operations
  that read source. The test only requires that an available operation does not
  answer `unavailable`, and an invalid program is not unavailable, so it keeps
  passing. The rule therefore applies wherever a program is read, not only to
  `check`.
- **Jev.** The two open semantic questions (which category carries the new
  refusals; which component owns the empty-program rule) were put to the Jev
  service first. It answered `typesafe: unavailable` — `TYPESAFE_API_KEY` is
  absent from this environment — so both were decided locally, as recorded
  above.

### Still open

- The design step chooses the owners inside `src/prova/syntax.py` and the one
  place in `src/prova/service.py` that carries the location through.
- Whether a formal model (Quint) pays is decided at the design step.
