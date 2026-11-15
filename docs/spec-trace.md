# SPEC.md clause trace

Measured at commit `533271a` (`main`). SPEC.md is restart draft 0.2.

**What this is.** Each row is one requirement I extracted from SPEC.md, with the
lines it comes from and what the implementation does about it. The clause list is my
own reading of the specification, not an official inventory. A different reader could
split or merge rows, so the totals are a guide and not a precise measurement.

**How status was decided.**
- *Probe*: an ID such as `T3` refers to a probe in
  [`docs/spec-trace/probe.py`](spec-trace/probe.py). It sends a small program to the
  service in-process and compares the answer with what SPEC.md requires.
  Run `uv run python docs/spec-trace/probe.py` to reproduce the table.
- *Existing tests*: a test file in `tests/` that covers the clause.
- *Code*: the source shows the feature is absent. This is the weakest kind of evidence.

**The table below is a snapshot, and it is older than the code.** It was measured at
`533271a`; F5, F6 and F9 have landed since, so several rows no longer describe what the
probes report. Re-running `uv run python docs/spec-trace/probe.py` today reports 45 of 53
scored probes agreeing with SPEC.md. Rows 1.11 and 1.12 are the two F9 changed: probes
G3, G4 and L5 now agree, because an out-of-profile source is answered with its own
`unsupported` status and an `unsupported_construct` diagnostic that names the construct.
The rows themselves are left as the dated measurement they are; re-measuring the whole
table is its own piece of work.

**Statuses.**
- `Done`: behaviour matches the clause on the cases probed.
- `Partial`: some of the clause works.
- `Missing`: the clause belongs to `core-0` or `check`, which exist today, but the
  behaviour is wrong or absent.
- `Not started`: the clause belongs to a profile or operation not built yet
  (`verify-0`, `machine-0`, `build`, `format`).
- `Deferred`: SPEC.md itself says a later profile.

## 1. Lexical rules and grammar (lines 56-128)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 1.1 | UTF-8 s-expressions, `;` comments ignored | Done | probe L1 |
| 1.2 | Formatter preserves comment text and order | Not started | `format` is unavailable |
| 1.3 | Value names match `[a-z][a-z0-9-]*[?!]?`; type names `[A-Z]...` | Missing | probe L4: `Foo` accepted as a function name |
| 1.4 | Keywords and builtins are reserved | Missing | probe L3: a function named `let` is accepted |
| 1.5 | Integers: `+002` equals `2`, `-0` is zero, arbitrary precision | Done | probe L2b, E6; `tests/acceptance/test_s6_*` |
| 1.6 | Canonical rendering is deterministic and idempotent | Not started | `format` is unavailable |
| 1.7 | Core grammar: records, unions, `defn`, `let`, `if`, `match`, selectors, operators | Done | probes G1, G2, T15; reservation example |
| 1.8 | Reserved special forms take precedence over generic calls | Done | existing checker tests |
| 1.9 | Forward references allowed | Done | probe G6 |
| 1.10 | Declarations cannot nest in expressions | Done | probe G7 (rejected, though as `unbound_name`) |
| 1.11 | Excluded features (trailing expression, `defspec`, `fn`, division, ...) refused as *unsupported* | Partial | probe G3 rejects; G4 shows the category is `syntax` with no "unsupported" label |
| 1.12 | Decimal and text literals refused | Partial | probe L5 rejects them as `unbound_name`, not as out-of-profile |

## 2. Types, scope and checking (lines 130-168)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 2.1 | Nominal types; constructors check every argument | Done | `tests/acceptance/test_s3_*`, checker |
| 2.2 | Type-dependency graph is acyclic | Missing | probe T2: mutually recursive records accepted |
| 2.3 | Function names unique | Missing | probe T3: two `f` accepted, last one wins silently |
| 2.4 | Builtin types cannot be redeclared | Missing | probe T4 |
| 2.5 | Constructor names unique across the program | Missing | probe T5 |
| 2.6 | Fields unique within a record or variant | Missing | probe T6 |
| 2.7 | Field selector must name an actual field of the operand's type | Done | probe T7 |
| 2.8 | A binding must not shadow a parameter, function or builtin | Missing | probe T8: `(let ((n 2)) n)` accepted |
| 2.9 | A `let` initializer cannot see its own binding | Done | probe T9 |
| 2.10 | No binder may use `result`; only a postcondition reads it | Partial | probe T11 (read outside a postcondition rejected) passes; T10 (binder named `result` accepted) fails |
| 2.11 | Explicit types; both `if` branches and all match clauses checked, branches same type | Done | probes T12, T13 |
| 2.12 | Match covers its scrutinee type; `Int` needs a catch-all | Done | probes T14, T15 |
| 2.13 | A pattern variable binds once per pattern | Missing | probe T16: `(P x x)` accepted |
| 2.14 | Call and contract dependency graph is acyclic (no recursion) | Missing | probes T17-T19; a recursive program passes `check`, then `evaluate` dies with an uncaught `RecursionError` |
| 2.15 | Modules, imports, qualification | Deferred | SPEC.md line 165 |

## 3. Evaluation and operators (lines 170-196)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 3.1 | Deterministic call-by-value, left-to-right order | Done | evaluator; reservation tests |
| 3.2 | `+ - *` and comparisons on `Int`, with type checking | Done | probe E4; checker tests |
| 3.3 | `=` structural on two values of the same type | Done | probe E2 |
| 3.4 | `and` and `or` short-circuit | Done | code reading only; probe E1 shows core-0 cannot observe it |
| 3.5 | `not` has arity one; all operator arities enforced | Missing | probe E5: `(not b b)` accepted |
| 3.6 | `if` condition is `Bool`, no truthiness | Done | probe E3 |
| 3.7 | Decimal profile, integer division | Deferred | SPEC.md lines 191-196 |

## 4. Contracts and examples (lines 198-239)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 4.1 | `requires` and `ensures` are Boolean; `ensures` reads `result` | Done | probes C1, C2 |
| 4.2 | Pre- and postconditions checked on a supplied input | Done | `tests/acceptance/test_s3_*`, `test_s4_*` |
| 4.3 | Reports identify omitted and trivial contracts | Missing | probe C8 |
| 4.4 | Calls inside contracts meet callee preconditions | Not started | needs `verify-0` obligations (probe C7) |
| 4.5 | A function's precondition is well-defined for every typed input | Not started | `verify-0` |
| 4.6 | Every function has an example calling *that* function | Missing | probe C3: an example calling another function is accepted |
| 4.7 | Example arguments and results typed; input satisfies the precondition | Done | probes C4, C5 (reported failed by `examples`) |
| 4.8 | Declared examples run and pass or fail individually | Done | `tests/acceptance/test_s2_*`, probe C6 |
| 4.9 | Missing `examples` clause is a structured rejection, not a crash | Done | commit `f59c93e`; `tests/properties/test_i1_s5_p7.py` |

## 5. `verify-0` (lines 241-318)

`verify` answers with the inventory of obligations a program owes and attempts none
of them: every entry reads `not_attempted`. Nothing else in this section exists --
no encoding, no solver, no other result value and no aggregate result.

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 5.1 | Precondition obligation for every potentially evaluated call | Partial | listed, never attempted: one entry per call under the condition that reaches it; `tests/acceptance/test_verify_lists_the_obligations_owed.py` |
| 5.2 | Body-to-postcondition, example-validity, definedness and termination records | Partial | all four listed per function and per declared example, never attempted; `tests/properties/test_obligation_inventory_laws.py` |
| 5.3 | Encoding of Booleans, linear integer arithmetic and non-recursive data | Not started | no solver chosen (Q3) |
| 5.4 | Out-of-fragment obligations return `unknown` with a reason | Not started | code |
| 5.5 | Documented translation and soundness argument | Not started | code |
| 5.6 | Result dimensions: `proved`, `disproved`, `unknown`, `not_attempted`; execution status; claim kind; scope | Partial | `not_attempted` is the result every obligation carries and `claim.kind` now also reads `obligation_inventory`; the other result values and the execution-status dimension do not exist |
| 5.7 | Provenance: digests, claim version, compiler/solver versions | Partial | only `source_digest` (probe S8) |
| 5.8 | Aggregate `verified` needs a complete obligation inventory | Partial | the inventory exists and covers every function, example and call of a `core-0` program; no aggregate result of any kind is produced |
| 5.9 | Disproof needs a validated source-level witness | Not started | code |
| 5.10 | `build` fails closed while verification is incomplete | Done | probe S3, `tests/acceptance/test_s1_*` (fails closed because it is unavailable) |
| 5.11 | Requirement integrity: claim identities and revisions, weakening disclosed | Not started | process only, no tooling |

## 6. Effects and termination (lines 320-344)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 6.1 | All `core-0` functions pure | Done | grammar has no effectful signature |
| 6.2 | Termination follows from acyclicity | Partial | depends on 2.14, which is Missing |
| 6.3 | Recursion, `decreases`, capabilities, effects | Deferred | SPEC.md lines 327-344 |

## 7. `machine-0` (lines 346-459)

Nothing in this section exists. The pure `step` of the reservation example runs and is
checked as an ordinary function, but no machine layer exists around it.

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 7.1 | Machine descriptor and its versioned transport schema | Not started | open decision Q10 |
| 7.2 | Roles `init`, `step`, `state-of`, `admissible`, `invariant` resolved to checked functions | Not started | code |
| 7.3 | `Init`, `Transition` and `Next` semantics | Not started | code |
| 7.4 | Three inductive-invariant obligations (init, enabled, preserved) | Not started | code |
| 7.5 | Sequential runtime; boundary rejection distinct from business rejection | Not started | code |
| 7.6 | Stuttering, progress, refinement, model exploration, TLA+ export | Deferred | SPEC.md lines 420-459 |

## 8. Tooling and runtime (lines 461-513)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 8.1 | Versioned JSON service | Done | `src/prova/__main__.py`, `service.py` |
| 8.2 | Manifest lists profiles, operations, categories and limits | Partial | `discover` returns these; no signatures, effects or per-operation schemas |
| 8.3 | Operation categories: discovery, parsing, formatting, checking, verification, examples, building | Partial | 3 of 7 exist (`discover`, `check`, `examples`), plus `evaluate` which SPEC.md does not name |
| 8.4 | Unimplemented operations advertised unavailable and refused | Done | probes S1-S3 |
| 8.5 | Diagnostics carry a stable category | Done | `DIAGNOSTIC_CATEGORIES` |
| 8.6 | Diagnostics carry location | Partial | probe S5; reader and syntax refusals carry line and column; `cyclic_dependency`, `recursive_type` and `unbound_type` carry none |
| 8.7 | Diagnostics carry source revision, symbol or obligation identity, expected and actual | Missing | probes S4, S6 |
| 8.8 | Invalid programs, unsupported reasoning and tool failures are distinct | Partial | `invalid_program` and `tool_failure` exist; "unsupported" is not a separate status |
| 8.9 | Results bind to a source revision | Partial | `source_digest` only |
| 8.10 | Build once, run fresh inputs; entry inputs decoded and precondition-checked | Partial | `evaluate` validates inputs but there is no build |
| 8.11 | Arbitrary-precision integers preserved through transport | Done | `tests/acceptance/test_s6_*` |
| 8.12 | Resource budgets (input, time, memory, output) with controlled failure | Not started | probe S7: `enforced: false` |
| 8.13 | Outputs confined to authorised destinations; failed builds preserve outputs | Partial | refused build writes nothing (`test_s1_b4_*`); no real build to confine |

## 9. Conformance example (lines 515-587)

| # | Requirement | Status | Evidence |
|---|---|---|---|
| 9.1 | Reservation source parses, checks and runs | Done | `tests/acceptance/test_s1_*` |
| 9.2 | All six table rows reproduced on fresh inputs | Done | `test_s1_b1_step_six_row_table.py` |
| 9.3 | Invalid entry states and malformed values rejected distinctly | Done | `test_s3_*` |
| 9.4 | Missing upper guard, flipped flag and always-reject bodies detected | Done at run time only | `test_s4_*`; detection by static proof needs `verify-0` |
| 9.5 | Detection "using the real compiler and executable" | Not started | there is no executable |

## 10. Empirical evaluation (lines 589-600)

Out of scope for the compiler as such. No task set, baseline language or experiment
exists (Q8). Not counted below.

## Summary

81 requirements were extracted. Deferred rows are excluded from the percentages.
Row 9.4 is counted as Done although it only holds at run time.

| Area | Done | Partial | Missing | Not started | Deferred | Rows |
|---|---|---|---|---|---|---|
| `core-0`: syntax, types, evaluation, contracts, purity (sections 1-4, 6) | 22 | 4 | 13 | 4 | 3 | 46 |
| `verify-0` (section 5) | 1 | 5 | 0 | 5 | 0 | 11 |
| `machine-0` (section 7) | 0 | 0 | 0 | 5 | 1 | 6 |
| Tooling and runtime (section 8) | 4 | 7 | 1 | 1 | 0 | 13 |
| Reservation conformance example (section 9) | 4 | 0 | 0 | 1 | 0 | 5 |
| **All** | **31** | **16** | **14** | **16** | **4** | **81** |

How to read this.
- **`core-0`:** 22 of 43 live rows are Done (51%), and 26 of 43 (60%) are Done or Partial.
  The 13 Missing rows are mostly small `check` rules (see the defect list below).
- **`verify-0`:** no obligation has ever been attempted, so nothing here is Done beyond
  the fail-closed `build` refusal. What exists is the inventory: the tool now says what
  would have to be shown, which is the list the encoder and solver rows will work from.
- **`machine-0`:** 0%. The roles and obligations around `step` do not exist.
- **Equal weighting misleads.** One `verify-0` row, such as the solver encoding, is far
  more work than one `check` rule. The row counts do not measure effort.
- **Overall:** 31 of 77 live rows are Done (40%). My earlier "10-15%" was too low if
  counted by rows and too high if counted by effort. Neither figure is the right one.
  A better claim is: the `core-0` front end is about half conformant, the verifier knows
  what it owes but attempts none of it, and the state-machine layer has not started.

## Defects found by this trace

These are gaps against SPEC.md on clauses the current build claims to cover.
They are the cheapest next work, because `core-0` and `check` already exist.

1. **Recursion is accepted and crashes the tool** (2.14). A function that calls
   itself passes `check`. `evaluate` then raises an uncaught `RecursionError`.
   SPEC.md requires rejecting it at check time.
   *Fixed by feature F2.* `check` now refuses a program whose bodies and
   contracts depend on themselves, with the category `cyclic_dependency` naming
   the functions of the cycle, and no operation reaches the evaluator with such
   a program. Probes T17, T18 and T19 agree after the change and disagreed
   before it (`uv run python docs/spec-trace/probe.py`: 34 of 53 scored probes
   agree, against 31 of 53 at commit `f2bbb73`). The table above is left as it
   was measured at `533271a` and is not re-scored here.
2. **Duplicate function names are accepted silently** (2.3). The second definition
   replaces the first and the program evaluates with it.
   *Fixed by feature F3.* `check` now refuses a program that declares one name
   twice, with the category `duplicate_declaration` naming the repeated name and
   the places it is declared at.
3. **Seven more `check` gaps share a fix location.** Cyclic types (2.2),
   builtin redeclaration (2.4), duplicate constructors (2.5), duplicate fields (2.6),
   shadowing (2.8), `result` as a binder (2.10) and repeated pattern variables (2.13)
   are all accepted.
   *Fixed by features F3, F4 and F5*, not by one of them: F3 refuses builtin
   redeclaration (2.4), duplicate constructors (2.5) and duplicate fields (2.6);
   F4 refuses cyclic types (2.2) as recursive data outside this profile; F5
   refuses shadowing (2.8), `result` as a binder (2.10) and repeated pattern
   variables (2.13). The row counts in the table above were measured before
   these features and are not re-scored here.
4. **Reserved words and name shape are not enforced** (1.3, 1.4).
5. **Operator arity is not fully enforced** (3.5). `(not b b)` passes.
6. **An example can call a different function** (4.6).
7. **Diagnostics lack the fields SPEC.md names** (8.7).

Not verified: I checked each defect with one small program. A fuller test for each
would also try nearby shapes.
