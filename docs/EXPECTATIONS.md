# Expectations and questions for the restart

Status: validation plan for specification restart draft 0.2. No delivery roadmap
has been approved and no compiler check has executed. Document sanity checks are
not compiler evidence. No property question below has an accepted Relay answer.
The IDs here are document references, not Relay event or story IDs.

## Owner direction

The owner described Prova as "designed for LLMs, not humans" and asked to start
the compiler from scratch using the second Relay protocol, based on
"expectations/evidence and questions to be validated". The old implementation and
old sign-offs are not acceptance evidence for the replacement.

The owner then specified "A language better suited for LLMs, functional, aligned to
the principles of TLA+ and formal verification" and requested that the specification
be updated against the cited references. Draft 0.2 defines the corresponding semantic
direction. Remaining implementation choices must not silently change that meaning.

## Proposed first observable outcome

An agent implements the reservation transition in the specification: capacity two,
reserve below capacity, release above zero, and otherwise reject without changing
state. Both resulting state and acceptance status are requirements. The six-row
transition table is the independent behavioural oracle; rejecting every request
must fail even though it preserves the state invariant.

The first language target is `core-0`, followed by `verify-0` and `machine-0` evidence.
Compile once, run fresh inputs, check unexecuted branches and call preconditions,
and preserve the independently stated domain contract during repair. Unknown proof
results and operational failures remain distinguishable. This is the recommended
conformance target; the delivery roadmap must still choose the first increment.

Pricing, exact decimals, Huffman and Tetris are later tasks. The current small core
does not claim their features. Do not rewrite an approved domain expectation to
accommodate a compiler limitation; change scope explicitly when needed.

| Proposed expectation | Question the evidence must answer | Evidence needed before claiming support |
|---|---|---|
| E1: Correct programs execute with the stated meaning. | Does one compiled reservation artefact return the exact state and acceptance flag for all six valid state/event cases and fresh sequences? | Execute the real artefact against the independent transition table; cover malformed inputs and invalid entry states separately. |
| E2: Checking covers the whole supported program. | Can an error hide in a branch not visited by any example or inside an operator, constructor or function argument? | Invalid fixtures fail at the appropriate semantic stage; minimally corrected controls pass. Add module-boundary cases when a module profile exists. |
| E3: Contracts constrain implementations and callers. | Do wrong bodies and unsatisfied call preconditions fail even when examples pass? | Same contract/examples with correct and incorrect bodies; a caller that loses a required precondition; a valid counterpart. |
| E4: Verification has honest limits. | Are unsupported reasoning, timeout, missing dependencies and actual disproof distinguishable? | A typed core obligation requiring unsupported nonlinear reasoning, controlled timeout/tool failure, complete obligation inventory and a separate false obligation that still cannot become success. Standard build publishes no executable when required verification is incomplete. |
| E5: Diagnostics support repairs. | Can a client identify the failed operation, site and obligation without parsing prose? | Schema checks through the real public interface; an actual repair followed by rechecking; stable categories across wording changes. |
| E6: Tool operations respect authority and resources. | Can malformed input, output paths or cancellation escape the declared limits? | Bounded failure cases, output-preservation checks and adversarial path tests when writing is supported. |
| E7: The evidence belongs to the delivered candidate. | Were all required checks executed against the exact source and expectation version being accepted? | Relay toolgate receipts and answers tied to one candidate SHA and obligation digest; no skipped, absent or altered protected checks. |
| E8: Core semantics compose. | Do scope, pattern matching, evaluation order, arbitrary integers and contracts obey the same rules everywhere? | Paired conformance programs for each implemented grammar/typing rule; short-circuit contract calls; duplicate names, wrong constructor fields, recursive cycles and non-exhaustive matches; integer inputs beyond floating-point precision. |
| E9: The machine invariant is justified. | Do initialisation, admissibility, call preconditions and every transition establish the stated invariant? | Distinct initial and induction-step obligations, all six finite transition cases, a missing-guard mutation, and an induction witness explicitly distinguished from a reachable trace. |
| E10: Repair preserves the intended problem. | Can an agent obtain acceptance by weakening guarantees, strengthening preconditions or changing expected results? | Deliberate contract/example/assumption mutations trigger requirement-change handling; unchanged approved expectations reject “always reject” and deleted-input-domain repairs. |
| E11: Claim scope remains honest. | Can a finite run, bounded exploration or terminating handler be misreported as an unbounded invariant or liveness proof? | Schema/aggregation checks preserve claim kinds and bounds; a safe stuttering behaviour demonstrates that progress has not been established. No liveness tool is required to document this limit. |
| E12: The language benefits LLM development. | Does Prova improve independent correctness or cost on comparable tasks? | Repeated budget-matched construction/repair trials with a typed functional baseline and a verification-language baseline; withheld checks and full token/compute/intervention accounting. |

These are acceptance themes, not a demand to build twelve features at once. E12
is an empirical research question after a working slice, not an invented unit test.
Scope each to the supported profile. An unsupported feature may be explicitly
rejected, but that rejection does not count as evidence that its deeper semantics
are correct. Every negative check needs a positive control at the relevant stage.

## Decisions to resolve before dependent implementation

| ID | Open question | Recommended starting point, not an owner decision |
|---|---|---|
| Q1 | What is the first independently deliverable increment towards the reservation target? | Use the current grammar and integer domain; approve a narrow roadmap rather than reopening settled semantics. |
| Q2 | What canonical layout, syntax-tree schema and JSON operation schemas implement the written semantics? | Fix fixtures and stable diagnostic categories before their implementation. |
| Q3 | Which solver/encoding implements `verify-0`, and what budgets apply? | Document the translation for Boolean/linear-integer/non-recursive data reasoning, source-witness validation and complete obligation inventory. |
| Q4 | What exact runtime framing and value encoding carries fresh inputs and outcomes? | Preserve arbitrary integers, nominal types and constructor fields; validate types/preconditions at entry; compile once. |
| Q5 | Which implementation language, backend and dependency versions form the trusted toolchain? | Evaluate a small bootstrap and existing verification backends where useful; do not inherit the old architecture. |
| Q6 | How are the reservation contract and independent transition table protected and versioned? | Obtain domain acceptance through the roadmap and keep body edits distinct from requirement changes. |
| Q7 | What enforceable resource and output-authority limits apply? | Define the initial adapter's limits and failure/cleanup rules; preserve outputs on failure and inherit no waivers. |
| Q8 | What task set, models, budgets and comparison languages define the first experiment? | Include one typed functional and one verification baseline, held-out checks, repairs and repeated runs. |
| Q9 | What fresh Relay identity and evidence runner will be used? | A new protocol-2 engagement with a pinned isolated environment validated before dispatch. |
| Q10 | What machine-descriptor schema and host adapter realise `machine-0`? | Resolve checked function roles, preserve state/outcome publication, state environmental assumptions and distinguish witness kinds. |

Resolve genuine product choices with the owner. Resolve ordinary technical choices
with evidence and record the reasoning. Do not make every routine choice a blocker.

## Evidence discipline

Write expectations and scoped property questions before the implementation. Test
selection failures, missing executables, unavailable dependencies and timeouts are
execution problems, not successful tests or semantic counterexamples. A failing
test is only a useful red state if it executed and failed for the intended reason.

Never change an approved expected result merely to match a regression. Correcting
a mistaken expectation requires a visible requirement revision and fresh evidence.
Boundary properties, mutations and independent oracles should challenge the claim;
generated inputs provide finite evidence, not an unbounded theorem.

Keep focused checks fast and full checks bounded. A test must not recursively start
its own discovery command. Manage only child processes owned by that run, propagate
exit status accurately, and clean up temporary artefacts on interruption. Measure
timeouts under the chosen environment before scheduling work. Repeated identical
failures need a diagnosis of their actual output, not another unchanged retry.

## Specification authoring checks

On 27 September 2026, a temporary, deliberately limited evaluator checked the
worked source's seven examples, all six table transitions and rejection of two
invalid entry states. Independent table comparisons detected a missing capacity
guard and an implementation that rejected every event. This evaluator is not a
Prova compiler, type checker or language-conformance test suite.

A separately written QF_LIA model checked with Z3 5.0.0 found no counterexample to
initial validity or invariant preservation and found witnesses for the two deliberate
fault scenarios. That result concerns the manually encoded mathematical model, not
a compiler translation or the full language. These checks help assess consistency
of this draft; they are not Relay receipts and do not answer E1–E12 for an implementation.
