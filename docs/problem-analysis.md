# Problem analysis: scoping the first Prova iteration (second question cycle)

Scope note: analyses WHAT the first iteration is and WHY; does not choose
technologies, write executable checks, or configure Relay.

## 1. Updated problem statement

The Owner has answered the open questions from the previous analysis. Their
answers, verbatim:

> Q1 (increment scope): "As recommended (A), clarified: the first iteration
> delivers a checked evaluator, not a completed compiler, described as
> checking and direct evaluation. It must validate the six expected outcomes,
> function preconditions and postconditions, and reject invalid inputs. It
> must not claim universal proof or completed compilation. Function-contract
> verification and verified executable generation go in the next planned
> increment; machine-level proofs can follow separately."

> Q2 (unverified build): "As recommended: no unproven build; building waits
> for proof. The first iteration shows results only through checking and
> direct evaluation, with no build claim."

> Q3 (protected example): "Approve as written, clarified: protect the
> example's semantics, contracts and expected outcomes; changes to those
> require Owner approval. Formatting-only changes do not require a new
> product decision, though evidence must still match the exact candidate
> revision."

> Q4 (engagement identity): "Keep prova-lang-v1 if its ledger contains only
> this fresh engagement."

> Q5 (fixture adaptation): "Defer historical sample adaptation until the
> relevant features enter scope."

The problem is now: deliver, as the first iteration, a checked evaluator for
the reservation source — whole-program checking plus direct evaluation of
fresh inputs and declared examples — that demonstrates the six expected
outcomes, checks preconditions and postconditions, and rejects invalid
inputs, while making no claim of universal proof, completed compilation, or
a built artefact. Verification (`verify-0`) and build are explicitly the
next iteration's problem, not this one's. The reservation example's
semantics, contracts and expected outcomes are protected: any implementation
that disagrees with them is wrong until the Owner approves a stated
revision. The engagement identity question resolves to a factual check, not
a naming decision. Historical fixtures stay out of scope entirely for now.

## 2. What the first iteration is and is not

**Is:** a checked evaluator exercised through two behaviours only —
*checking* (static, whole-program: types, scope, contract well-formedness)
and *direct evaluation* (dynamic: running declared examples, and running
fresh inputs against `step`, `initial` and `valid-state`, evaluating each
function's precondition before its body and its postcondition against the
concrete result actually produced). Both behaviours run through the real
public interface, on the reservation source verbatim.

**Is not:** no `build` operation attempted or claimed, in either an
unverified or a gated-standard sense — Q2 removes the ambiguity the previous
analysis raised under "Option A" by simply declining to exercise `build` at
all this iteration. No `verify-0` obligation discharge, no solver, no
`machine-0` descriptor or induction obligations, no machine-level proof. No
historical fixture adaptation (Q5). No claim of "verified", "proved" or
"built" anywhere in output, ever, for this iteration's results.

**The SPEC tension, resolved:** SPEC's internal-evaluation line ("Internal
evaluation during compiler development is not a release build or evidence
of verified-build conformance", line ~292) gives explicit textual licence
for what Q1/Q2 describe. The remaining friction: SPEC's initial
operation-category list (discovery, parsing, formatting, checking,
verification, examples, building — line ~467) has no category for running a
*fresh* input against a checked function. "Examples" already covers
dynamically running the *declared* examples (line ~230: closed-value calls
checked for result equality and postcondition satisfaction), so "every
function's examples run and pass" needs no new capability. What is new is
generalising that same dynamic-contract-check mechanism to inputs the
author did not write down (the two uncovered table rows, the
precondition-violating states, the three deliberately wrong bodies).

Exposing that generalisation through the real interface — with `build` and
`verify` advertised as unavailable and refused explicitly, as line ~469–470
licenses for any unimplemented operation — is consistent with SPEC in
substance but not literally covered by its enumerated category list. It
should therefore be recorded as a proposed, narrow semantic change (an
addition to the operation-category vocabulary) at the point it is
implemented, not silently folded into "checking" or "examples" as if
already named. This is a documentation action already authorised in
substance by Q1 and Q2 — it needs no further Owner decision, and it touches
no protected content under Q3.

A labelling point follows: a passed per-input postcondition check (a result
satisfying `Post_f` for the one concrete input exercised) is not the
universal total-correctness judgment in SPEC's contracts section (line
~215–221). Reports must say what was checked — this call, this input —
never borrow vocabulary ("proved", "holds", "verified") reserved for the
discharged universal obligation.

## 3. Observable outcomes and candidate thin vertical slices

Plain behavioural terms for what the Owner will check:

- Whole-program checking accepts the reservation source; a structurally or
  semantically invalid variant is rejected, including an error placed in
  either of `step`'s two branches, where none of the four declared
  examples reaches it.
- Every function's declared examples (`valid-state`: 2, `initial`: 1,
  `step`: 4) run through direct evaluation and pass.
- Direct evaluation of `step` reproduces all six transition-table rows'
  state and `accepted` flag, including the two rows no example covers —
  `(1, Reserve) → (2, true)` and `(2, Release) → (1, true)`.
- Entry precondition violations — `(Reservation 3)`, `(Reservation -1)` —
  and malformed or ill-typed inputs are rejected with no successful result,
  at the precondition boundary, not silently executed.
- Postcondition violations in a deliberately wrong body are detected during
  evaluation: a missing upper guard, a flipped `accepted` flag, and a body
  that rejects every event ("reject everything", SPEC's own named failure
  case) each must be caught, not passed.
- Arbitrary-precision integers are not routed through binary floating
  point — a value outside floating-point-safe range comes back exactly.
- Honest labelling holds throughout: no "verified", "proved" or "built"
  claim appears anywhere in this iteration's output.

**Candidate thin vertical slices**, each runnable one at a time through the
real interface, each independently demonstrable:

1. Check the reservation source whole; a hand-built malformed variant is
   rejected with a diagnostic.
2. Directly evaluate every declared example for all three functions;
   confirm all pass.
3. Directly evaluate `step` against the two table rows no example covers;
   confirm state and `accepted` match the table.
4. Directly evaluate the two precondition-violating entry states and at
   least one malformed/ill-typed input; confirm rejection, no successful
   result.
5. Directly evaluate three deliberately wrong bodies (missing guard,
   flipped flag, reject-everything); confirm each is caught, not accepted.
6. Directly evaluate a fresh input with an integer outside
   floating-point-safe range; confirm no precision loss.

Their order (1 before the rest; 6 anywhere after the interface exists) is a
sequencing choice for the roadmap, not asserted here.

## 4. Remaining implementation decisions

Routine — technical choices resolved with evidence, not Owner questions:

| Decision | Why routine | Scope this iteration |
|---|---|---|
| Bootstrap language | Host-language-agnostic semantics; an engineering evaluation | Supports checking + direct evaluation cleanly |
| Interface/JSON schema | Mechanics, fixed with positive/negative fixtures before release | Covers only discovery/parse/check/(new evaluation category) — not build/verify |
| Value encoding | Constrained by SPEC: arbitrary-precision integers, nominal types/constructors/fields preserved, no float routing | Concrete carrier only |
| Resource budgets | SPEC requires budgets measured, not guessed | Set after the evidence-runner's four cases are timed for real |
| Evidence-runner validation | Demonstrated, not assumed, per standing Relay requirement | Passing, failing, missing-selector, timeout cases |

Deferred entirely (not this iteration's problem, per Q1): solver/encoding
for `verify-0` and its trust disclosure; `machine-0` descriptor schema,
roles and induction obligations; build target/backend and release-build
packaging — there is no build to target this iteration.

## 5. Risks

- **The engagement-identity condition (Q4) is a fact to check, not a
  question.** "Keep `prova-lang-v1` if its ledger contains only this fresh
  engagement" is conditional; the ledger must be inspected before reusing
  the name, not assumed clean because it was asked about once.
- **The protected example (Q3) narrows how disagreement is resolved.** Any
  mismatch between the implementation and the example's semantics,
  contracts or expected outcomes is resolved by fixing the implementation,
  or by a visible, Owner-approved requirement revision — never by quietly
  adjusting the contract, example or table. Formatting-only edits need no
  fresh product decision, but evidence must still name the exact candidate
  revision it was produced against.
- **The operation-category gap (section 2) needs writing down.** If this
  iteration exposes fresh-input direct evaluation through the interface
  without recording it as a proposed addition, the vocabulary drifts ahead
  of the specification silently — the failure mode the Owner's standing
  instruction on semantic changes exists to prevent.
- **Dynamic contract-checking must not borrow verification vocabulary.** A
  per-input postcondition check that passes is evidence about that input
  only; "proved"/"verified" language would misstate its scope even though
  no `verify-0` work has happened.
- **No fixtures means the malformed-input and wrong-body controls must be
  hand-built fresh.** Q5 defers all fourteen historical fixtures, so the
  malformed variant (slice 1) and the three wrong-body variants (slice 5)
  are new artefacts, not adaptations — unbudgeted, they may be skipped.
- **No-build removes one contradiction but not all pressure.** Declining
  `build` entirely (Q2) resolves the fail-closed tension the previous
  analysis flagged, but increases reliance on direct evaluation being
  visibly distinct from a build in every report, under delivery pressure.

## 6. Open questions

No material ambiguities remain at the Owner-decision level: Q1–Q5 cover
increment scope, the no-build rule, the protected example, engagement
identity and fixture deferral, and each has a clear, actionable answer
above.

**Deferrable unknowns, and why each is deferrable:**

- E12's baseline languages, comparison work set and budgets — not asked
  this cycle, and explicitly out of scope because E12 is an empirical
  question after a working slice exists, not part of the first iteration.
- Solver/encoding for `verify-0` — deferred with `verify-0` itself under
  Q1; nothing in this iteration depends on it.
- `machine-0` descriptor schema — deferred with `machine-0`; roles are
  already fixed in SPEC when that work starts.
- Exact JSON schema field names, bootstrap language and backend — routine
  technical choices (section 4), resolved by evidence, not by the Owner.
- Precise resource-budget numbers — deferred by SPEC's own instruction to
  measure the real environment before setting them.

## 7. Confidence

- Users: 8/10 — unchanged; stated in SPEC, the LLM-benefit claim remains
  an explicit hypothesis outside this iteration's scope.
- Current process: 9/10 — the previous cycle's two live ambiguities
  (increment shape, build-claim status) are both now settled.
- Success for the first iteration: 9/10 — up from 6/10; the target, the
  oracle and the exact behaviours to demonstrate (section 3) are fixed,
  with no remaining scope option to choose between.
- Constraints: 8/10 — up from 7/10; declining `build` outright removes the
  fail-closed contradiction; the residual item is recording the
  operation-category addition (section 2), a documentation action.
- Risks: 8/10 — up from 7/10; fixture mismatch is no longer live (deferred
  under Q5); the residual risks are the identity ledger check, labelling
  discipline under pressure, and building the hand-made controls fixtures
  would otherwise have supplied.
