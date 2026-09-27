# Codebase brief

Measured on 27 September 2026 at commit `ee5e1556b3a5e06945a02a61ef3a4cad51744b12`
(`git ls-files` on that commit). Everything below describes that commit only.

## What exists

There is no code. The commit tracks 21 files: six Markdown documents, fourteen
historical `.prova` fixtures and `.gitignore`. A search for any tracked file that
is not Markdown, `.prova` or `.gitignore` returned zero; the same listing without
that filter returned all 21, so the search did run.

There is no compiler, no build system, no test runner, no dependency manifest and
no CI configuration. Line coverage, hotspots by churn and legacy seams do not
apply, because there is nothing to execute or change. For that reason the legacy
code analysis and system walkthrough were not run: both inspect source code, and
none exists.

| Path | Role | Size |
|---|---|---|
| `SPEC.md` | Restart draft 0.2: `core-0`, `verify-0`, `machine-0` semantics, agent interface, reservation conformance example | 644 lines |
| `docs/EXPECTATIONS.md` | Proposed expectations E1 to E12, open decisions Q1 to Q10, evidence discipline | 107 lines |
| `docs/RELAY.md` | Handoff for protocol 2: authority, delivery shape, evidence-runner validation | 87 lines |
| `docs/spec-review-2026-09-27.md` | Design review of the earlier baseline that motivated draft 0.2 | 401 lines |
| `evidence/README.md` | Meaning and provenance of the fourteen fixtures | 51 lines |
| `evidence/cases/*.prova` | Fourteen single-line historical counterexamples and positive controls | 95 to 282 bytes each |
| `README.md` | Entry point and restart statement | 44 lines |

## Architecture

None has been chosen. `SPEC.md` ("Implementation decisions still required") and
`docs/EXPECTATIONS.md` (Q2 to Q5, Q7, Q9, Q10) list the undecided parts: bootstrap
language, backend and solver, syntax-tree and JSON operation schemas, runtime
framing and value encoding, resource limits, evidence runner and machine
descriptor. The only architectural commitments are semantic: a versioned JSON
service with discovery, parse, format, check, verify, examples and build
operations; build once and run fresh inputs; arbitrary-precision integers carried
without floating point; unsupported features refused as unsupported.

## Real test coverage

Zero. No check of any kind is tracked. `docs/EXPECTATIONS.md` records two
authoring-time checks of the reservation example (a temporary evaluator and a
hand-written QF_LIA model run through Z3). Neither is in the repository, neither
exercises a Prova compiler, and the document itself states they are not receipts.
`evidence/README.md` states that no fixture has been run.

## Danger zones

`evidence/cases/` does not fit `core-0` as written. All fourteen fixtures end with
a trailing top-level call, which `core-0` excludes. Beyond that, three use
`Decimal` and division (`constant-division`, `exact-division`,
`inexact-division`), three use the `length-text` builtin (`builtin-hides-name`,
`builtin-hides-type`, `valid-builtin`), and `missing-call-precondition` uses
`defspec`. None of those features is in `core-0`. `evidence/README.md` requires
each fixture to be adapted explicitly with its semantic question preserved, and
warns that an unsupported-feature rejection does not validate the deeper property.
Running the fixtures unchanged will produce rejections that look like success and
prove nothing.

`SPEC.md` is the only oracle. Its six-row reservation transition table is the
independent behavioural oracle for E1 and E9. Any edit to the table, the `step`
contract or the examples changes the requirement, not the implementation, and
must travel as a visible requirement revision (E10, Q6).

`docs/EXPECTATIONS.md` looks like approved acceptance criteria but is not. It
labels its IDs as document references, its recommendations as "not an owner
decision", and every property as unanswered. Copying its prose into story
obligations would repeat the failure `docs/RELAY.md` warns against.

Honest limits are the easiest thing to get wrong. E4 and E11 require unknown,
timeout, tool failure and disproof to stay distinct, and a finite run never to be
reported as an unbounded invariant. With no solver chosen, nothing yet guards this.

The engagement identity is unconfirmed. `docs/RELAY.md` asks for a fresh identity,
checked unused, and says starting the previous swarm resumes old work. The local
Relay configuration names this swarm `prova-lang-v1`. Nothing in the repository
records whether that identity was previously used. This needs confirming, not
assuming.

## Hotspots

The repository has two commits, both from 27 September 2026, so churn says nothing
yet. Future change will concentrate in `SPEC.md` (the grammar and reservation
example) and `docs/EXPECTATIONS.md`, which every first-iteration story will cite.

## What this means for planning

The first iteration starts from nothing, so every story has to create its own
runnable surface. The first story's owner-visible check is necessarily the first
execution of any Prova tool. Q1 (first increment), Q4 (runtime framing) and Q5
(toolchain) block the first story. Q3 (solver) blocks `verify-0` stories only, and
Q10 blocks `machine-0` only.
