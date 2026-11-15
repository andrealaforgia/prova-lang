# A function's examples are about that function — the self-review

Seventeen dimensions, answered against the committed change
(`[F8] read whose example a declared example is`). No debt is left: each
line is pass or a justified n/a.

| # | dimension | answer | evidence |
|---|---|---|---|
| D1 | architecture matches the design | pass | one owner in `checker.py`, one published word in `service.py:31`; no other file touched |
| D2 | one source of truth | pass | the name called, the count and the ordinal are read once, in `DeclaredExample.of` (`checker.py:570`); `check_program` (`checker.py:700`) decides nothing itself; the word is written once (`checker.py:97`) |
| D3 | layer boundaries | pass | the rule reads parsed syntax and answers a `Diagnostic`; it calls no reader, evaluator or service |
| D4 | wrong states unrepresentable | pass | `checker.py:544` gives the example its own type, built only from a function, its example and the program, so no caller can ask the question with another function's count; refusals are values, not booleans (`checker.py:589`) |
| D5 | small cohesive classes | pass | `checker.py:544`: one frozen dataclass, 6 fields, 5 short methods, no nesting; `is_about_its_own_function` (`checker.py:586`) names the question |
| D6 | design patterns | n/a | none added; the change follows the shape `Cycle` and `TypeCycle` already use |
| D7 | domain-driven design | pass | the owner speaks SPEC.md's language and each refusal quotes the rule broken (`checker.py:607`, `checker.py:630`) |
| D8 | infrastructure out of the domain | pass | no file, process, clock or network; a pure function of a parsed program |
| D9 | tests through the public interface | pass | acceptance tests drive the real `prova` command over JSON only (`_f8_example_subject_fixtures.py:246`); property tests use the published request surface and published words |
| D10 | test naming | pass | every name is a sentence about what a reader gets, e.g. `test_f8_b1_...py:32` |
| D11 | test DSL and helpers | pass | programs and the two assertion helpers live once, in the fixtures module |
| D12 | property tests | pass | `test_f8_example_subject.py:108` draws the case first from a closed set of 5, then builds a program in that case by construction, no filtering; bounds declared in the module |
| D13 | test speed | pass | 9 runs of the 8 new files: 26 passed each time, 1.22-1.24s; full suite 1007 passed in 100.11s |
| D14 | test duplication | pass | each test adds a distinct observation; no finite example repeats the property's pair |
| D15 | readability and failure messages | pass | refusals say what, why and how with the facts held (`checker.py:607`, `checker.py:630`); assertions state expected, actual and contract (`_f8_example_subject_fixtures.py:283`) |
| D16 | formal model | n/a | a pure check with no state, protocol, concurrency or crash window; recorded as DEC6 |
| D17 | documents honest | pass | `oracle.md` and `craft.md` carry the measured numbers and name what is not proved |

## The independent review

REV1 approved the change with 2 Medium findings, neither blocking. Both
are fixed:

| finding | fix | check that turns red without it |
|---|---|---|
| the branch for a name that is no function had no falsifier: treating every name called as declared kept the suite green | both halves of the refusal are now stated in the tests | treating every name as declared fails 3 tests; treating none as declared fails 2 |
| "which this program does not declare" was false of a declared constructor and of a builtin operator | the refusal says "which is not a function this program declares", and both programs are observed | the earlier wording fails 3 tests |
