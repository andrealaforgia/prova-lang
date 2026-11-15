# Self-review: the seventeen dimensions

Answered by the executor against the committed change. The independent
review that the step also needs is written by a reviewer other than the
executor, so this record is not closed here.

| | Dimension | Answer |
|---|---|---|
| D1 | architecture matches the decisions | pass. The report is carried by `check` alone and published in the manifest, as DEC1 says; `src/prova/service.py:58` holds the list of operations that carry it, beside the dispatcher that owns operation names. |
| D2 | one source of truth | fixed. The three words were first written twice, as a tuple of names and three singleton values; they are now one table, `CONTRACT_STRENGTH_MEANINGS`, which the names, the strengths and the published shape are all read from. |
| D3 | layer boundaries | pass. The rule lives in the checker, the dispatcher only asks for it; the checker learns no operation name, it is passed one. |
| D4 | wrong states unrepresentable | pass. `src/prova/checker.py:1727` refuses any word that is not published, and `src/prova/checker.py:1840` refuses a report naming one function twice. Both have a test and a positive control. |
| D5 | small cohesive values | pass. `src/prova/checker.py:1778` is three fields and four short methods; each of the three values answers about itself and nothing reaches into another. |
| D6 | patterns used well | pass. A smart constructor and a closed vocabulary; no pattern added for its own sake. |
| D7 | domain language | pass. Omitted, trivial, stated, precondition, postcondition: the words of SPEC.md, not of the implementation. |
| D8 | infrastructure out of the domain | pass. The rule reads a parsed program and returns a value; it opens no file, spawns nothing and keeps nothing. |
| D9 | tests through the public interface | pass. Every acceptance and property test drives the real `prova` command over JSON, for example `tests/acceptance/test_f13_b1_a_function_without_a_precondition_is_recorded_as_omitted.py:28`. The two refusals can only be reached by building a report by hand, so they have unit tests of the module's own contract. |
| D10 | test naming | pass. Each name is a sentence about what the Owner sees; none holds a production symbol. |
| D11 | test helpers | pass. One fixture module holds the programs and the one way the tests talk to the tool; each program is written out so every expected strength is read from the source by hand. |
| D12 | property tests | pass. Four laws, `tests/properties/test_f13_contract_report_laws.py:112` and the three that follow it; the plan is the oracle, and each case is built from a closed set of block texts, which holds the literal `false` as well as the literal `true`. |
| D13 | test speed | pass with a stated cost. Nine runs of the new files: 22 passed each time, median 3.02 s. A property case costs about 38 ms because the law is observed through the real command, as every property test here does. |
| D14 | test duplication | pass. The finite examples state the four criteria and the shipped clock; the properties state the laws over generated programs; no pair repeats a stimulus and an assertion. |
| D15 | readability and failure messages | pass. Every refusal says what failed, why it matters and how to repair it (`src/prova/checker.py:1729`), and every assertion message names the expected and the actual reading. |
| D16 | formal model | n/a. The change adds no state, no protocol and no concurrency: one parsed program in, one field of one answer out. |
| D17 | documents honest | pass. The craft record states what the tests prove and what they do not, the measured costs, and the Jev service being unavailable. |

## What was fixed during this review

- The vocabulary was declared twice; it is now one table (D2).
- A published sentence used the word "holds", which an existing manifest
  test refuses. The sentence was reworded; the test was not touched.

## What a later independent review found, and what was done

Four defects, all fixed in the same branch and each one now watched by a
test that fails when the defect returns:

1. the note was answered but never published;
2. a literal block was read for being a literal, not for its value, so
   `(ensures false)` read as trivial;
3. two of the three notes were never observed;
4. the published meaning of `stated` over-claimed what a stated block
   says.

Each of the first three was checked by putting the wrong behaviour back
into the code and watching the named tests fail: the manifest test for
the first, the `false` acceptance test and two property laws for the
second, and two tests of the vacuous program for the third.
