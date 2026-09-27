# Problem analysis: starting the Prova restart under Relay protocol 2

Scope note: analyses WHAT must be decided and WHY; frames options with
trade-offs where a genuine product choice exists. Does not choose
technologies, write executable checks, or configure Relay.

## 1. Problem restatement and success criteria

The Owner's instruction, verbatim:

> "Read SPEC.md, docs/EXPECTATIONS.md and docs/RELAY.md. Start a fresh Relay
> protocol-2 engagement. Do not import previous iterations, queues, approvals
> or completion credit. Propose the smallest end-to-end increment towards the
> reservation example. Record explicit expectations and property questions
> before implementation, then have the executable checks independently
> reviewed. Resolve the remaining implementation decisions: bootstrap
> language, backend, solver, interface schemas, runtime transport and
> resource budgets. Use the semantics already defined in SPEC.md. Record any
> proposed semantic change explicitly rather than changing requirements to
> accommodate the implementation. Validate the actual worker environment and
> evidence runner before dispatching implementation work. Confirm that
> Claude, Relay commands and the selected tools can be launched. Check
> passing, failing, missing-selector and timeout cases. Keep deferred
> features outside the initial scope. Completion requires execution evidence
> for the exact candidate commit and supported answers to the original
> property questions. Never weaken a contract or change an expected result
> merely to make a check pass. Present the narrow roadmap and necessary owner
> decisions, then proceed through the protocol once approved."

Success criteria, all required simultaneously: a fresh confirmed-unused Relay
identity carrying no prior state; a narrow, independently reviewed increment
whose executable checks predate implementation; every implementation
decision resolved and recorded, with any semantic deviation from SPEC.md
logged explicitly rather than absorbed; a demonstrated (not assumed)
worker/evidence-runner environment covering pass, fail, missing-selector and
timeout; completion evidenced by toolgate execution against the exact
candidate commit with every property question answered `supported`,
`contradicted` or `insufficient_evidence`; no weakened contract or altered
expected result to force a pass; and a presented roadmap/decision set with
protocol progress gated on Owner approval.

## 2. Settled vs undecided

**Settled by SPEC.md (do not reopen):** profiles — `core-0` (total,
first-order, pure, no IO/recursion) as first target, `verify-0` (complete
obligation accounting) required before any "verified" claim, `machine-0`
(state/event transitions with inductive invariants) as first system-level
target, later profiles explicitly out (lines 42–55, 602–613); grammar and
lexical rules (56–129); contract semantics — total-correctness reading,
short-circuit conjunction, mandatory per-function examples, example ≠ proof
(198–240); the verification result vocabulary `proved`/`disproved`/`unknown`/
`not_attempted` with no kind upgrading another (270–306); `machine-0` roles
(`init`/`step`/`state-of`/`admissible`/`invariant`) and its three induction
obligations (346–419); the reservation example itself — types, the three
functions, their contracts/examples, and the six-row transition table as
independent oracle (515–587); runtime discipline — build once, run fresh
inputs, arbitrary-precision integers, entry preconditions checked first,
standard `build` fails closed on incomplete verification (484–513).

**Genuinely undecided** (SPEC.md line 633 onward, mapping to EXPECTATIONS.md
Q1–Q10): bootstrap language; backend and solver with trust boundary;
canonical layout and JSON schemas; runtime framing and value representation;
measured resource budgets and output handling; Relay engagement identity and
evidence-runner validation; `machine-0` descriptor transport schema.
Addressed per-item in section 4.

## 3. Smallest end-to-end increment towards the reservation example

An "end-to-end increment" is something runnable through the real public
compiler interface, not a unit test of internal code.

**Candidate thinnest vertical slice** — compile the reservation source
(SPEC.md's worked example, verbatim) and execute `step` once against a fresh
input:

1. **parse**: the reservation source is accepted; a structurally malformed
   variant is rejected with a diagnostic (the E8-style hand-built
   malformed-tree control expected of any behaviour adding evaluator code).
2. **check**: types, scope and contract well-formedness resolve across the
   whole source, including both branches of `step`.
3. **build once**: a single artefact is produced for `step`/`initial`,
   without requiring `verify-0` obligations discharged — unless the Owner
   decides the slice must already fail closed, in which case `build` cannot
   run meaningfully until `verify-0` exists (see options below).
4. **run fresh input**: invoke `step` on an input outside the four given
   examples (e.g. `(Reservation 2) (Release)`) and check state and
   `accepted` against the independent transition table.
5. **negative control**: an invalid entry state (e.g. `(Reservation 3)`)
   is rejected at the precondition boundary rather than silently executed.

This is the minimum needed to answer E1 (execution against the independent
oracle) and start E2/E8 (branch coverage, malformed-tree handling), without
touching verification, machine descriptors, formatting or `examples`.

**Options and trade-offs (genuine product choice):**

- **A — parse/check/build/run only, `verify-0` deferred.** Smallest and
  fastest, but SPEC.md's "no `build` without complete verification" rule
  (line 291) forces a choice: either this increment's `build` is an
  explicitly-disclosed unverified/development capability distinct from the
  gated "standard build," or no `build` is exercised and only
  `parse`/`check` plus direct interpretation produce a "run" result.
- **B — add a minimal `verify-0` slice for `step`'s postcondition.**
  Removes the ambiguity in A by producing an honestly-verified build, but
  pulls solver selection (Q3) into a hard blocker for the first increment —
  something both SPEC.md and EXPECTATIONS.md treat as avoidable.
- **C — add `machine-0` framing for `step`/`init`.** Most complete
  alignment with the recommended core-0 → verify-0 → machine-0 path, but
  adds the descriptor schema (Q10) and three induction obligations, so the
  increment is no longer smallest.

Recommendation direction (not a decision made on the Owner's behalf): Option
A, with the unverified-build distinction stated explicitly — keeps the
increment smallest, defers `verify-0`/`machine-0` to their own stories, and
avoids forcing Q3/Q10 before any evidence exists.

**Explicitly deferred:** `verify-0` obligation discharge, `machine-0`
descriptor and induction obligations, `examples` as a standalone operation,
`format`, diagnostics-schema completeness beyond the one malformed-input
control, and all fourteen historical fixtures (none fit `core-0` as written).

## 4. Implementation decisions

| Decision | Classification | Recommended default and reasoning | Blocks |
|---|---|---|---|
| Bootstrap language (Q5) | Routine — reversible, no semantic effect; pytest is required regardless | A language with a mature pytest-drivable interface and no inherited old architecture; SPEC.md's semantics are host-language-agnostic, so this is an engineering evaluation | First story |
| Backend/target (Q5) | Routine — same reasoning | Whatever pairs naturally with the bootstrap choice; no bespoke runtime work needed for `core-0`'s tiny value set | First story |
| Solver for `verify-0` (Q3) | Routine tool pick, but the translation/encoding and its trust disclosure is product-relevant since SPEC.md requires it documented and justified, and the authoring-time check already used Z3 as reference | Deferred entirely under Option A | `verify-0` stories only |
| Interface/JSON schemas (Q2) | Routine mechanics, but must be fixed with positive/negative fixtures before any operation ships — a hard prerequisite, not a style choice | Minimal schema covering only `parse`/`check`/`build`/`run`, versioned from the first commit | Every story calling the compiler |
| Runtime transport/value encoding (Q4) | Routine, tightly constrained: must preserve arbitrary-precision integers, distinguish nominal types/constructors/fields, never route integers through binary floating point (lines 498–501) | Any encoding meeting those constraints; only the concrete carrier is open | First story's run step |
| Resource budgets (Q7) | Routine, evidence-based — SPEC.md requires budgets measured, not guessed | Set from an actual measured run in the chosen environment (section 5), not a round number chosen in advance | Dispatch of any implementation work |
| Machine descriptor schema (Q10) | Routine mechanics; the roles it exposes are already fixed by SPEC.md | Deferred under Option A | `machine-0` stories only |
| Relay engagement identity (Q9) | Product/governance choice — determines what prior work is disclaimed, not a technical fact | A new name, confirmed unused against Relay's own state, before any dispatch | The entire engagement |

## 5. Environment and evidence-runner validation

RELAY.md requires demonstrating — not assuming — that the actual detached
worker environment can launch Claude, Relay commands and the selected tools,
across four observable cases:

- **Passing**: a check known to succeed reports a pass via the pytest
  selector path, with real command, source SHA and output captured.
- **Failing**: a check built to fail reports failure for the *intended*
  reason, distinguishable from a crash, missing dependency or selector
  error — EXPECTATIONS.md requires the failure reason, not just a red
  result. The E8-style malformed-tree control from section 3 is a natural
  candidate for this case.
- **Missing-selector**: a non-existent pytest node/file selector is
  requested and the runner reports selection failure explicitly, never as
  zero-tests-pass or a skip.
- **Timeout**: a check exceeding a bounded limit is cut off, its process
  tree cleaned up, and reported as a timeout, not a pass, hang or crash.

All four must be distinguishable in the runner's output, because environment
failure, compiler failure and inadequate-test failure route to three
different next actions. Budgets (Q7) should be set only after these four
cases are run and timed for real, not before.

## 6. Risks and contradictions

- **Fixtures do not fit `core-0`.** All fourteen historical fixtures end in
  a disallowed trailing top-level call; several use out-of-profile features
  (`Decimal`, division, `length-text`, `defspec`). Run unchanged, they
  produce rejections that look like successful negative tests but prove
  nothing; each selected fixture needs explicit adaptation preserving its
  semantic question.
- **Engagement identity is unconfirmed.** The local Relay swarm is
  configured as `prova-lang-v1`. RELAY.md requires a fresh, checked-unused
  identity and warns that starting the existing swarm resumes old work;
  nothing inspected confirms prior use either way — this needs active
  confirmation, not assumption.
- **The spec's worked example is also the oracle.** Any change to the
  `step` contract, examples or transition table is a requirement change
  needing visible revision (E10, Q6), not a routine implementation
  adjustment — an easy line to cross under delivery pressure.
- **Honest-limits accounting (E4/E11) has no owner yet.** With no solver
  chosen, nothing yet distinguishes `unknown`, `timeout`, `tool failure` and
  genuine `disproved`, nor guards a finite run being reported as an
  unbounded invariant/liveness result. Not a defect in Option A — a gap the
  increment does not close and should not appear to close.
- **EXPECTATIONS.md's own IDs are not approved acceptance criteria.** It
  states E1–E12/Q1–Q10 are document references, every property currently
  unanswered; copying its prose directly into story obligations repeats the
  failure RELAY.md warns against.
- **Two non-receipt checks already exist and could be mistaken for
  evidence.** A temporary evaluator and a hand-encoded QF_LIA Z3 model
  checked the reservation example's authoring correctness on 27 September
  2026; EXPECTATIONS.md states plainly neither is a Relay receipt or
  evidence for an implementation. Property answers must cite a toolgate
  receipt against the real candidate commit, not these.
- **`build`'s fail-closed rule creates a scoping tension.** Under Option A,
  any `build` exercised is either not the "standard" gated build, or the
  increment must include enough `verify-0` to earn that label — a
  contradiction only if left unstated.

## 7. Open questions

**Only the Owner can answer:**

1. Which first-increment scope (Option A, B or C, section 3)? Determines
   whether solver selection and machine-descriptor work enter the first
   story. Blocks: writing the roadmap's first story.
2. Is an unverified/development `build` a distinct, disclosed capability
   separate from the gated "standard build"? A product decision about what
   the tool may claim, not a technical detail. Blocks: how E1 evidence is
   produced under Option A without contradicting the fail-closed rule.
3. What name replaces `prova-lang-v1`, and who confirms it unused? An
   authority/governance matter, not a technical one. Blocks: engagement
   start itself.
4. Which typed-functional and verification-language baselines and task set
   ground the E12 comparison (Q8)? A research-design and credibility
   commitment, not derivable from evidence. Blocks: only the E12 story, not
   the first increment — listed because no evidence resolves it.
5. How much fixture-adaptation work belongs in the first increment versus
   later? A priority/risk-appetite judgement, not derivable from SPEC.md
   alone. Blocks: whether the first increment includes any
   fixture-derived checks beyond the one malformed-tree control.

**Deferrable unknowns (resolvable later with evidence):** exact
solver/encoding for `verify-0` (Q3, deferred under Option A, resolved by
evaluating candidates against the documented fragment when scheduled); exact
JSON schema field names/framing (Q2/Q4, resolved by drafting and testing
fixtures once section 4's constraints are honoured); precise budget numbers
(Q7, deferred by SPEC.md's own instruction to measure first); machine
descriptor transport schema (Q10, deferred until a `machine-0` story, roles
already fixed).

## 8. Confidence

- Users (LLM agent producing/repairing Prova programs; Owner reviewing
  evidence): 8/10 — stated in SPEC.md, though the LLM-benefit claim is an
  explicit hypothesis.
- Current process (protocol 2, expectations-before-implementation,
  independent review, toolgate receipts): 8/10 — detailed and consistent.
- Success for the first increment: 6/10 — the target and oracle are fixed,
  but the Option A/B/C choice (Q1) is genuinely open and changes the shape
  of "done."
- Constraints: 7/10 — normative rules are precise; residual uncertainty is
  how the fail-closed `build` rule interacts with a deliberately unverified
  first increment.
- Risks: 7/10 — fixture mismatch, identity and honest-limits gaps are well
  documented; residual uncertainty is only how they surface once real
  tooling exists.
