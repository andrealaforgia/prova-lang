# Prova specification review: LLMs, functional programming and formal verification

Review date: 27 September 2026. Baseline: `65429a34b4326cb5ee902fbfdd4fc1bdcf98ec40`.
This is an independent design assessment, with no nWave workflow or delegated
reviewers. The specification has not been changed by this review.

## Verdict

Prova is a credible direction for a small functional language with explicit
verification and a useful machine interface. It is not yet demonstrated to be
better for LLMs than existing languages. Its current specification does not yet
define the system-level semantics needed to substantiate TLA+ alignment.

Continue the experiment, but resolve a small semantic core before dispatching
compiler implementation. The restart brief I prepared is deliberately incomplete;
it should not be presented to a builder as an implementation-ready language standard.
Neither its brevity nor a green Relay receipt can substitute for those decisions.

| Goal | Current assessment | Evidence still needed |
|---|---|---|
| More effective LLM development | Plausible, unvalidated | Independently scored generation and repair tasks under equal budgets, including existing-language baselines |
| Functional programming | Good starting direction | Precise pure-function, data, pattern-matching, composition and effect semantics |
| Formal verification | Appropriate intentions, incomplete contract | Defined proof obligations, supported logic, termination policy, assumptions and trusted implementation boundary |
| Alignment with TLA+ | Compatible foundations, missing system model | Initial states, transition relation, invariants, environment model, trace semantics and eventual refinement connection |
| Ready for a compiler implementation plan | Not yet for a whole compiler | An approved, executable specification of one small end-to-end subset |

## Scope and evidence

I read the current `SPEC.md`, README, expectation questions, Relay handoff and all
14 retained source fixtures. I compared them with the archived v0.9.1 specification,
the temporal-layer design note and the earlier LLM design assessment at the historical
revision `093fb86443c057c1d3abb4f1c033d1a6bf601d38`. Historical requirements are not
silently reinstated here. Findings below distinguish current omissions from older
ideas that should not be brought back unchanged.

External comparisons use primary language/tool documentation and research papers,
linked beside the relevant claims. No Prova compiler exists in this working tree,
and no compiler test or TLA+ tool was run. A six-transition Python sanity check of
the small reservation example below passed; it is finite illustrative evidence only.
There is no new empirical evidence that Prova improves LLM performance.

## 1. Define what a successful verification actually establishes

Priority: before the first verifier implementation.
Location: [SPEC.md, contracts and verification](../SPEC.md#contracts-examples-and-verification),
especially lines 80–100 and 127–131.

The spec correctly distinguishes proof from examples and unknown from success.
However, it does not yet define the judgments behind those labels. Implementers
must otherwise invent which semantics they are proving and what a successful
`build` promises.

For a total pure function, the intended claim might be: for every well-typed input
satisfying its precondition, evaluation terminates with a value satisfying its
postcondition. If only partial correctness is established, termination must be a
separate obligation, not implied by the same label. Resource exhaustion is another
operational matter, even for mathematically terminating functions.

Specify the initial expression grammar, typing rules, evaluation rules and the
verification-condition rule for every supported construct. Define the declared
solver fragment as well as its encoding. Establish that recursive assumptions
cannot be used circularly without justified termination or an appropriate proof rule.

A candidate verified build should identify the source revision, claim, dependencies,
assumptions, discharged obligations and trusted tool versions. Distinguish a logical
unknown from a failed tool execution, cancellation or missing dependency. A process
crash is not a mathematical answer.

Decide whether “proved” initially means accepted by a trusted SMT solver or checked
through independent proof evidence. Either can be an honest engineering choice;
they are different assurance claims. Lean's separation of elaboration and kernel
checking illustrates the distinction, without removing all trust from its execution
toolchain. [Lean elaboration and kernel checking](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/).

Acceptance question: can the same contract and examples, attached to two bodies
that differ only on an unvisited branch, yield proof for the correct body and a
valid counterexample for the incorrect one? Can a test detect an omitted obligation?

## 2. Protect the problem from changes made to obtain a proof

Priority: before an autonomous repair loop.
Location: [SPEC.md, lines 18–22 and 74–78](../SPEC.md#contracts-examples-and-verification),
[EXPECTATIONS.md, evidence discipline](EXPECTATIONS.md#evidence-discipline).

The current text recognises that contract correctness is not requirement correctness.
It needs an enforceable interface boundary around that distinction. An agent can
make a failing implementation “verify” by weakening the guarantee, restricting the
input domain, deleting an example, or assuming a stronger environment.

For example, “the result is sorted” allows a function to return an empty list for
every input. A meaningful sorting contract also preserves the input multiset.
Likewise, `requires false` can make a universal implication vacuous. Requiring an
example helps only if the example must actually exercise that function on an input
satisfying the same precondition.

Record independently approved public requirements and classify changes to accepted
inputs, guarantees, examples, effects and assumptions. Do not claim automatic
semantic equivalence checking in general: when an edit's meaning cannot be shown
unchanged, report that uncertainty. Add satisfiability and vacuity checks where the
chosen fragment supports them. Include a mutation that weakens the problem, not
only mutations that break the implementation.

Relay's protected expectation versions help enforce this at delivery time. Prova
still needs to express the semantic difference between changing a body and changing
its public claim. An execution receipt establishes what ran; it does not establish
that the original question was the right one. Lean's proof-validation documentation
similarly distinguishes checking a proof from checking it against the intended
theorem statement. [Lean proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/).

## 3. Make the TLA+ relationship precise

Priority: decide the semantic direction before choosing the runtime architecture.
Location: [SPEC.md, effects and termination](../SPEC.md#effects-and-termination),
and its absence of a machine/trace model.

TLA+ models permitted behaviours as sequences of states. Its abstractions concern
initial states, allowed transitions and properties of executions. Function contracts
alone do not provide this system-level description. A code-level target can coexist
with a separate abstract model; Prova does not need a natural-language surface to
support that relationship. [Lamport's high-level account](https://lamport.azurewebsites.net/tla/high-level-view.html).

The useful distinction is between safety, which excludes bad behaviour, and liveness,
which requires progress. A system that accepts a request and then does nothing may
preserve every state invariant while failing a progress requirement. Fairness is an
assumption about which enabled actions eventually execute, not something guaranteed
by a total handler. [Lamport on safety, liveness and fairness](https://lamport.org/tla/safety-liveness.pdf).

For an initial state-transition subset, define `Init`, `Next`, a state invariant,
and the allowed environment inputs. Establish initial validity and preservation:

```text
Init(s)                         implies Inv(s)
Inv(s) and Next(s, s')           implies Inv(s')
```

An invariant that is true only of reachable states may require a stronger inductive
invariant to discharge the second obligation. A failed induction step can therefore
expose an unreachable state; do not automatically report it as a reachable execution
counterexample. Distinguish those two kinds of witness.

If the implementation has more detailed state than the abstract model, define a
mapping between them. For safety refinement, a concrete transition must map to an
allowed abstract transition or an unchanged abstract state, together with the
initial-state obligation. Preserving liveness requires additional progress and
fairness reasoning. Stuttering is part of the relationship, not an accidental
exception. [Lamport on stuttering and refinement](https://lamport.azurewebsites.net/tla/stuttering.html?back-link=advanced.html).

Do not implement a new temporal theorem prover first. Initially, state records,
event unions and pure transition functions can express a useful invariant discipline
without special temporal syntax. A later bridge to TLA+/TLC or Apalache can add model
exploration. Generating a TLA+ file is not, by itself, proof that the executable
implements the model: the translation and runtime connection need evidence too.

## 4. Correct the archived temporal note before reusing it

Priority: before adopting any temporal extension. These are historical claims,
not defects asserted to exist in the current brief.

The old `design_notes/temporal-layer.md` proposed invariants, liveness measures,
model checking and refinement. The progression is useful, but four statements need
correction.

| Historical idea | Correction |
|---|---|
| A total event handler already makes the running program a TLA+ specification. | The handler gives a possible transition function. The runtime still needs defined initialisation, enabled actions, input delivery, atomicity, state visibility and assumptions. |
| A mandatory natural-number measure makes liveness a decidable language feature. | A measure can support particular progress proofs under sufficient transition and fairness conditions. It does not make arbitrary liveness or its proof obligations decidable, and not all useful liveness arguments have that simple form. |
| “TLC-style bounded model checking” is a tier between testing and proof. | Separate complete exploration of a finite model from exploration limited to a trace length. Bounds on instances and bounds on traces establish different claims. Evidence is not a single stronger/weaker ladder. |
| Per-handler invariants catch a class of bug that function contracts cannot express. | State-transition contracts can express preservation already. Machine-level declarations improve centralisation, completeness of coverage and the link to executions. Their benefit is not a logical inability of contracts to state the same predicate. |

TLC is an explicit-state model checker supporting safety and liveness. Apalache
distinguishes bounded checking from inductiveness checking; finding no violation
within a trace bound does not establish the absence of longer violations.
[TLA+ tools](https://lamport.azurewebsites.net/tla/tools.html),
[Apalache's checking modes](https://apalache-mc.org/),
[Apalache's explanation of bounds](https://apalache-mc.org/docs/tutorials/symbmc.html).

The old spec's finite collection combinators and recursive encodings also do not
automatically establish a decidable proof fragment. Each concrete collection being
finite is different from verifying a property over all possible collection sizes.
Make claims about decidability only for a precisely characterised logic.

## 5. Functional foundations are sound; composition needs specification

Priority: define the initial subset, then grow from concrete use cases.
Location: [SPEC.md, source and values](../SPEC.md#source-and-values) and
[deferred scope](../SPEC.md#deferred-scope).

Immutability, explicit data variants, pure functions and explicit effects are good
foundations. Functional programming does not require lazy evaluation, unrestricted
higher-order functions or category-theory vocabulary. A strict first-order core can
be a sensible starting language.

But a language useful for substantial functional programs needs a coherent route to
reusable data and operations: algebraic data constructors, exhaustive pattern
matching, parametric types where needed, module interfaces and disciplined recursion.
The current spec names these directions without defining the mechanisms.

The archived language allowed selected builtin combinators to take functions while
ordinary user functions could not. That can simplify an initial verifier, but it
must not become an unquestioned permanent privilege of the standard library.
Otherwise agents duplicate algorithms or need compiler changes to express normal
abstractions. Specialisation/defunctionalisation or a restricted higher-order subset
are options to investigate later, not immediate feature commitments.

The ban on shadowing may help local reasoning, but it interacts with namespace and
import design. Adding an unrelated exported name should not unexpectedly invalidate
a local binding across a project. Specify qualification and import visibility before
multi-module work. Define collection iteration order and text operations before
claiming deterministic observable behaviour.

F* demonstrates that pure and effectful functional programming can coexist with
proof-oriented development and automated reasoning. It is a useful comparison point,
not evidence that Prova should inherit its full type system.
[F* language overview](https://fstar-lang.org/).

## 6. Effects are permission, not a model of what the world will do

Priority: before IO or reactive runtime support.
Location: [SPEC.md, lines 104–113](../SPEC.md#effects-and-termination).

Knowing that a function may write a file does not establish that it writes the
right file, writes it atomically, retries safely or handles partial failure. Knowing
that a network capability is available does not establish that the server responds.
The boundary between mathematical reasoning and operational assumptions must be
explicit.

A promising initial organisation is a pure decision function, conceptually:

```text
step : State × Event → State × List Command
```

This is design notation, not proposed Prova syntax. Commands are data describing
requested effects. An authorised host executes them and returns success or failure
as later events. Events model external choices, so a deterministic function can
still participate in a nondeterministic system model. Define invalid-event behaviour
explicitly, for example a rejected event with unchanged state and an error value.

The host must preserve the model's assumptions. A returned command is not an effect
already completed. Sequential host execution can establish the first atomicity
model; later concurrency requires a justified serialisation or refinement story.
External values must be decoded and checked before entering refined types. Exported
function preconditions need boundary validation or a stated trusted-caller assumption.

This pattern is a recommendation for a small first runtime, not a universal mandate
that every future Prova function use a command list.

## 7. Numerical exactness is valuable, but currently too underspecified

Priority: before implementing the selected numeric fragment.
Location: [SPEC.md, lines 50–56](../SPEC.md#source-and-values).

Keep exact arithmetic, no silent overflow and explicit rounding. Decide literal
typing, negative integer division/remainder, mixed-type operations and comparison
before writing either the evaluator or the encoder. The immutable-value rule also
needs consistent serialization and display semantics.

Exact finite decimals are not all real numbers. Modelling arithmetic over reals can
help establish some universal properties, but only when the encoding is a sound
abstraction of the supported operations and their definedness. Type inclusion alone
does not justify arbitrary extra axioms, division behaviour or rounding rules.

The retained division cases are useful: `3.0 / 3.0` is exact, whereas unrestricted
decimal division by 3 is not always exact. A false representability predicate, or an
unconstrained predicate the solver can assign freely, can corrupt the result.

Start with a small explicitly supported integer fragment if the chosen domain allows
it. If the owner's task actually requires decimal semantics, specify and implement
them rather than silently changing the task. Fixed-scale money can be an explicit
domain type without pretending to be the general `Decimal` type.

## 8. The LLM advantage must come from useful feedback and measured outcomes

Priority: design the evaluation before expanding the language.
Location: [SPEC.md, tooling](../SPEC.md#tooling-and-runtime-agreement),
[EXPECTATIONS.md, Q8](EXPECTATIONS.md#decisions-to-resolve-before-dependent-implementation).

Uniform syntax may simplify parsing and structural manipulation. It does not by
itself show that a pretrained model produces correct programs more often. More
mandatory annotations can provide useful redundancy or merely consume more context
and solver time. Humans and LLMs both benefit from coherent interfaces and precise
errors; “unpleasant for humans” is not an optimisation objective.

Prioritise an authoritative machine-readable library catalogue, expected types and
in-scope names, small diagnostic context, explicit failure reasons and revision-bound
results. Checking an incomplete draft or typed hole can be useful, provided no such
draft can become a verified executable. Structural editing can wait; attaching a
source revision to diagnostic locations cannot if multiple revisions are in play.

Constrained decoding can enforce a chosen output grammar, but that structural
guarantee is not general requirement correctness. The research establishes a useful
technique rather than a reason to prefer Prova's syntax automatically.
[Grammar-constrained decoding research](https://arxiv.org/abs/2305.13971).

Clover studies consistency between code, specifications and descriptions on a
hand-designed Dafny benchmark. It supports investigating feedback from verification,
not a universal correctness claim or a demonstrated advantage for Prova.
[Clover](https://arxiv.org/abs/2310.17807).

Research on F* program/proof synthesis also finds value in type-based retrieval and
checking candidate fragments. This supports the priority on discoverable interfaces
and local feedback. It does not transfer its measured results to a new language.
[SMT-assisted proof-oriented synthesis](https://arxiv.org/abs/2405.01787).

Measure independent task success, not just compilation rate. Compare the same agent
and task families against a familiar typed functional language and an established
verification language such as Dafny or F*. Supply each a usable tool interface and
equivalent total token/compute budgets. Include build and solver costs, diagnostics,
repair attempts, human intervention and failed attempts in the accounting.

Use withheld requirements-based checks and fresh tasks: initial construction,
cross-module changes, boundary errors, weakened-contract repairs and state-transition
bugs. Repeat enough runs to expose variation. Vary syntax and mandatory-example
policies separately so better tooling is not mistakenly credited to parentheses.

## 9. Separate logical assurance from proof-search reliability and runtime trust

Priority: before defining build acceptance metadata.
Location: [SPEC.md, lines 86–100 and 127–139](../SPEC.md#tooling-and-runtime-agreement).

A useful result identifies the claim and the kind of evidence, not only a green
status. Keep “tested on these inputs”, “explored this finite model”, “no violation
within this trace bound”, “invariant proved inductive”, and “function contract proved
under these assumptions” distinct. These claims are not interchangeable.

The encoder, imported contracts, solver, backend, runtime adapters and selected
libraries form part of the trusted boundary unless separately justified. A zero
source-level trust allowance does not mean a zero trusted computing base.
Interpreter/backend differential checks reduce risk but cannot prove that both do
not share the same semantic mistake. A reference semantics and independent oracles
remain important.

Proof-search cost is a usability and reproducibility dimension, separate from truth.
Multiple seeds finding the same answer do not repair an unsound encoding. The restart
correctly stops requiring the old fragility/cache machinery. If caching is later
added, its key must cover semantic dependencies and configuration, not just the
visible function text.

Dafny's tooling distinguishes verification variability and resource measurements.
It is a useful precedent for measuring difficult obligations without confusing
search cost with a counterexample.
[Dafny verification optimisation](https://dafny.org/dafny/VerificationOptimization/VerificationOptimization).

## A small example that exercises all three goals

Use a reservation component with fixed positive capacity, a count of reserved units,
and `Reserve`/`Release` events. Begin with count zero. Reserve increments below
capacity and otherwise rejects; release decrements above zero and otherwise rejects.
Rejection preserves state. Make the returned success/rejection result part of the
domain contract, so “reject everything” cannot satisfy the intended behaviour.

The functional core is the total state-transition function. The safety invariant is
`0 <= reserved <= capacity`. Initialisation establishes it and every event handler
preserves it. For capacity 2, the three possible valid counts and two event kinds
give six transitions to inspect. Removing the full-capacity guard produces a concrete
counterexample at count 2. This finite check was sanity-checked during the review;
it is not a proof for all capacities.

For a reactive extension, add a pending-request model. A system may remain forever
at a safe state while ignoring a pending request. Local function termination and
the count invariant do not rule that execution out. A progress claim needs a precise
definition of which request must be handled, under what capacity and delivery
conditions, and what scheduling assumptions apply. Fairness must not silently
promise that capacity becomes available or a network message arrives.

Compile once and run fresh event sequences. Prove the supported local obligations;
record any finite model exploration separately. Ask an agent to repair the missing
guard without changing the success conditions or shrinking the input domain. This
tests functional semantics, a TLA+-compatible invariant discipline and the actual
generate/check/repair experience in one small problem.

Pricing is still a useful arithmetic test, but this stateful domain expressed through
pure functions better exercises the additional TLA+ goal in the owner's latest request.
It is a proposed milestone, not an approved change of scope.

## Recommended decisions and order

| Order | Concrete decision or deliverable | What permits progression |
|---|---|---|
| 1 | Approve a small domain task, protected expected behaviour and state model. | Positive and negative requirements are independent of the implementation. |
| 2 | Specify exactly the syntax, types, evaluation, operators and contracts needed for that task. | Each rule has representative valid/invalid programs and an unambiguous expected result. |
| 3 | Define proof fragment, termination boundary, result schema and trusted components. | “Verified” has an exact scoped meaning; unsupported cases and tool failures are distinguishable. |
| 4 | Build one vertical slice from source to checked artefact to fresh runtime inputs. | Same-contract/different-body checks, call preconditions, runtime agreement and input-boundary checks succeed. |
| 5 | Establish transition invariants and a small independent model comparison. | Initial validity and preservation are justified; evidence states its bounds and assumptions. |
| 6 | Run the first comparative LLM experiment. | Results justify further language work rather than assuming benefit. |
| Later | Add needed abstractions, broader IO, model-checker integration and eventually liveness/refinement automation. | Each addition answers an observed limitation without weakening existing claims. |

Dafny already combines contracts, termination specifications and executable
compilation. Use it as a comparison or investigate it as a backend candidate if that
reduces the unknowns; translating to an existing verifier still requires a faithful
semantic translation. Do not inherit an implementation strategy merely because the
old compiler used it. [Dafny reference](https://dafny.org/dafny/DafnyRef/DafnyRef).

The suggested product description is: **a small functional language with explicit
state-transition semantics and machine-readable verification feedback, intended to
make LLM-generated software easier to check and repair**. It states the intended
benefit without claiming an empirical victory or system proof that has not happened.

Relay can now conduct the focused specification work. The next implementation
dispatch should follow an agreed small semantic contract, rather than interpreting
this review as an instruction to build every proposed feature.
