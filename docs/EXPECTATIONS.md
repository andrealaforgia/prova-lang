# Expectations and questions for the restart

Status: proposed input to Relay analysis. No roadmap has been approved, no tests
have been executed for the restart, and no question below has a supported answer.
The IDs here are document references, not Relay event or story IDs.

## Owner direction

The owner described Prova as "designed for LLMs, not humans" and asked to start
the compiler from scratch using the second Relay protocol, based on
"expectations/evidence and questions to be validated". The old implementation and
old sign-offs are not acceptance evidence for the replacement.

## Proposed first observable outcome

An agent can define a small pure function with a meaningful contract and examples,
obtain precise machine-readable checking results, compile it once, and run the
result with fresh inputs. The compiler checks unexecuted branches and function-call
preconditions. It rejects an invalid program and reports unknown for reasoning
outside its declared support. It never calls an example result a universal proof.

A bounded pricing calculation in integer minor units is a candidate small domain
task. Exact decimal pricing is an alternative with a larger initial proof and
runtime surface. Neither choice has been approved. The domain requirement must
come first; do not silently change an approved decimal requirement to integers to
make the checker pass.

| Proposed expectation | Question the evidence must answer | Evidence needed before claiming support |
|---|---|---|
| E1: Correct programs execute with the stated meaning. | Does the compiled artefact return independently calculated results for fresh runtime inputs? | Build once and execute multiple inputs, including withheld boundary cases, against a separate oracle. |
| E2: Checking covers the whole supported program. | Can an error hide in a branch not visited by any example, inside a builtin, or inside a module? | Invalid fixtures fail at the appropriate semantic stage; minimally corrected controls pass once the relevant feature exists. |
| E3: Contracts constrain implementations and callers. | Do wrong bodies and unsatisfied call preconditions fail even when examples pass? | Same contract/examples with correct and incorrect bodies; a caller that loses a required precondition; a valid counterpart. |
| E4: Verification has honest limits. | Are unsupported operations and timeouts distinguishable from proof and disproof? | Controlled unknown/timeout cases, complete obligation accounting and a separate false obligation that still cannot become success. |
| E5: Diagnostics support repairs. | Can a client identify the failed operation, site and obligation without parsing prose? | Schema checks through the real public interface; an actual repair followed by rechecking; stable categories across wording changes. |
| E6: Tool operations respect authority and resources. | Can malformed input, output paths or cancellation escape the declared limits? | Bounded failure cases, output-preservation checks and adversarial path tests when writing is supported. |
| E7: The evidence belongs to the delivered candidate. | Were all required checks executed against the exact source and expectation version being accepted? | Relay toolgate receipts and answers tied to one candidate SHA and obligation digest; no skipped, absent or altered protected checks. |

These are candidate acceptance themes, not a demand to build seven features at
once. Scope each to the supported slice. An unsupported feature may be explicitly
rejected, but that rejection does not count as evidence that its deeper semantics
are correct. Every negative check needs a positive control at the relevant stage.

## Decisions to resolve before dependent implementation

| ID | Open question | Recommended starting point, not an owner decision |
|---|---|---|
| Q1 | What exact user task and numerical domain define the first end-to-end slice? | One independently specified pure calculation; choose integer or decimal semantics explicitly. |
| Q2 | What is the complete grammar, operator table and scope model for that slice? | Keep the existing s-expression shape, a small type set, conditionals and first-order functions. Specify division and omitted contracts before using them. |
| Q3 | Which obligations can the initial verifier decide, and what exact limits produce unknown? | A small documented fragment, zero trust, explicit budgets and complete obligation reporting. |
| Q4 | How does a compiled program receive new inputs and return results? | A narrow documented runtime interface; compile once, execute many inputs. |
| Q5 | Which implementation language, backend and solver form the initial trusted toolchain? | Evaluate Go as a bootstrap option; choose from the slice rather than inheriting the old architecture. Pin selected dependencies. |
| Q6 | Who supplies and protects the domain expectations and independent oracle? | Capture owner-approved requirements before implementation and review checks for shared mistaken assumptions. |
| Q7 | What input, execution and output-authority limits apply? | Specify enforceable limits before exposing file writes or unbounded input; do not inherit previous waivers. |
| Q8 | What experiment would justify expanding Prova? | Compare independent task correctness, token/compute cost, repair attempts and human interventions against a familiar typed language under equivalent conditions. |
| Q9 | What fresh Relay identity and evidence execution environment will be used? | A new protocol-2 engagement; a pinned isolated runner provisioned and checked before dispatch. |

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
