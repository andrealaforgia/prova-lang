# Prova language specification

Version: **restart draft 0.2**, 27 September 2026. This revision incorporates the
owner's direction: a functional language intended for LLM development, with explicit
formal verification and a precise relationship to TLA+ principles. It supersedes
the retained-requirements brief at `65429a3`. No implementation or proof result is
claimed. A delivery roadmap and toolchain selection remain separate decisions.

Requirements using **must** are normative for the profile concerned. Mathematical
notation is explanatory and is not additional Prova syntax. Later profiles do not
oblige the first compiler to implement them. A compiler must report its language
and verification profiles accurately; partial implementations must not claim full
conformance.

The old v0.9.1 draft remains historical material in the external archive and local
Git history at `093fb86443c057c1d3abb4f1c033d1a6bf601d38:SPEC.md`. Its policies do not
add requirements to this revision. The [design review](docs/spec-review-2026-09-27.md)
explains the changes; [expectations](docs/EXPECTATIONS.md) identify evidence needed.

## Purpose and limits of the claim

Prova produces executable software. It aims to make generated programs easier to
inspect, verify and repair within a measured token and compute budget. Better LLM
outcomes are a hypothesis to test, not a consequence of s-expressions or annotations.

A program carries claims about its behaviour and identifiable evidence for them.
Syntax validity, type correctness, effects, examples, contracts, termination, state
invariants and temporal properties are distinct. Evidence for one must not be
reported as evidence for another. Correctness is relative to a stated claim and
assumptions; the compiler cannot establish that a claim captures human intent.

Prova remains a code-level target. Abstract system models may live above it and
specify behaviours it must implement. This permits TLA+-style modelling without
adding a natural-language layer or making the implementation its own independent
specification.

The functional core uses immutable values and pure functions. State changes return
new values. External effects have an explicit boundary. The language favours
compositional reasoning, discoverable interfaces and small repair contexts over
restrictions whose benefit has not been measured.

## Profiles and initial scope

| Profile | Required meaning | Initial delivery boundary |
|---|---|---|
| `core-0` | The syntax, values and total first-order pure functions below | First executable language target; no IO or recursion |
| `verify-0` | Complete obligation accounting and reasoning over the stated core fragment | Required before an artefact claims verified core conformance |
| `machine-0` | Explicit state/event transitions and inductive safety invariants using core functions | First system-level target; no temporal proof engine required |
| Later profiles | Recursive/generic data, richer arithmetic, effects, model checking, liveness and refinement automation | Added explicitly with semantics and conformance evidence |

Delivery may implement these incrementally, identifying incomplete operations.
Recognising syntax is not implementing its semantics. Unsupported features must be
identified as unsupported, not misdiagnosed as type errors. These profiles are
deliberately smaller than the historical language.

## Source and values

### Lexical rules and canonical form

Source is UTF-8 s-expressions. Whitespace separates tokens; parentheses delimit
forms. `;` starts a comment through the end of the line. Comments affect neither
typing nor execution. A formatter must preserve their text and order, attaching
them to the following syntax node or to the document end when none follows.

Value/function names match `[a-z][a-z0-9-]*[?!]?`. Type/constructor names match
`[A-Z][A-Za-z0-9]*`. Keywords and builtin operator names are reserved. `result` is
reserved for postconditions. `_` is a pattern wildcard, never a bound value.
Field selectors have the form `.field-name`. There is no identifier abbreviation
stop-list in this profile.

`->`, `!` and `=>` are reserved marker tokens used only at their grammar positions.
Core word keywords are `deftype`, `record`, `union`, `defn`, `sig`, `pure`, `requires`,
`ensures`, `examples`, `example`, `let`, `if`, `match`, `true`, `false` and `result`.
The builtin type names and operators below are also reserved.

Core literals are `true`, `false`, `()` and integers matching `[+-]?[0-9]+`.
Integers denote mathematical values: `+002`, `2` and `0002` denote the same integer;
`-0` denotes zero. Canonical integers have no leading plus or redundant zeros.
Decimal and text literals are outside `core-0`.

Every accepted tree has a deterministic canonical rendering. Formatting must be
idempotent and preserve meaning and comments. Non-canonical spelling is accepted.
Canonical layout and the syntax-tree interchange schema must be fixed in conformance
fixtures before shipping `format`; formatting policy must not alter language validity.

### Core grammar

`*`, `+` and `?` below mean repetition, nonempty repetition and optional occurrence.
`name`, `TypeName`, `Constructor` and `field-name` obey the lexical rules above.

```text
program       ::= declaration+
declaration   ::= type-decl | function-decl
type-decl     ::= (deftype TypeName (record field+))
                | (deftype TypeName (union variant+))
field         ::= (name type)
variant       ::= (Constructor field*)
type          ::= Unit | Bool | Int | TypeName
function-decl ::= (defn name signature requires? ensures? examples expr)
signature     ::= (sig (parameter*) -> type ! pure)
parameter     ::= (name type)
requires      ::= (requires expr+)
ensures       ::= (ensures expr+)
examples      ::= (examples example+)
example       ::= (example (name value*) => value)
value         ::= integer | true | false | () | (Constructor value*)
expr          ::= integer | true | false | () | name
                | (name expr*) | (Constructor expr*) | (operator expr*)
                | (.field-name expr)
                | (let (binding+) expr)
                | (if expr expr expr)
                | (match expr clause+)
binding       ::= (name expr)
clause        ::= (pattern expr)
pattern       ::= integer | true | false | () | _ | name
                | (Constructor pattern*)
operator      ::= + | - | * | < | <= | > | >= | = | and | or | not
```

Parentheses are literal syntax. Reserved special forms take precedence over the
generic call production. A record introduces a constructor with its type's name.
Union variants introduce their named constructors. Forward references are allowed
after whole-program declaration collection. Declarations cannot nest in expressions.

There is no trailing top-level expression, `defspec`, `fn`, `trust`, `module`,
division, general collection or effectful signature in `core-0`. Historical
counterexamples may need explicit adaptation to this profile; parser rejection
does not establish their intended semantic property.

### Types, scope and composition

Types are nominal. `Unit` has the sole value `()`. `Bool` has two values. `Int` is
arbitrary precision and must not silently overflow. Record fields and union payloads
have declared types; constructors check every argument. The type-dependency graph
must be acyclic in `core-0`, so recursive data requires a later profile. No null,
implicit conversion, mutation, exception or general function value exists here.

Top-level function and type names are unique within their namespaces; builtin types
cannot be redeclared. Types and constructors have separate namespaces,
but constructor names must be unique across the program. Fields are unique within
each record or variant. Field selection is defined only for records and resolves
from the operand's nominal type; equal field spellings in different records are
permitted. A selector must name an actual field of that type.

Parameters, sequential `let` bindings and pattern variables introduce lexical value
bindings. A binding must not shadow a visible value binding, function or builtin.
Pattern variables are scoped to their clause; the same spelling in disjoint clauses
is allowed. A `let` initializer sees preceding bindings, not the binding being
introduced. No binder may use `result`; only a postcondition may read it.

All signature parameter and return types are explicit. Local expression types are
derived without casts. Both `if` branches and every match clause are statically
checked, even when unreachable for the examples. Branch results must have the same
type. User calls and builtin arguments receive the same recursive checking.

Every match must cover all values of its scrutinee type without relying on a function
precondition. Clauses are tried in source order; first matching clause wins. An `Int`
match therefore needs a catch-all pattern. An algebraic type may be covered by its
constructors and recursively exhaustive payload patterns. A pattern variable binds
once per pattern; literal and constructor patterns must have the scrutinee's type.
Provably redundant clauses may be diagnosed without changing first-match meaning.

The combined dependency graph of function bodies and contracts must be acyclic.
Examples' calls to their own function are excluded from that graph. This prohibits
recursion through contracts as well as direct or mutual recursion. Later modules
must use explicit imports/qualification; adding an unimported symbol must not
change resolution. Parametric types, reusable higher-order abstractions and recursive
data are extension candidates, not permanent builtin-only privileges.

### Evaluation and operators

Evaluation is deterministic and call-by-value. Constructor fields, ordinary call
arguments and strict operator operands evaluate left to right. `let` initializers
evaluate sequentially. `if` evaluates its condition and only the selected branch.
`match` evaluates its scrutinee once and only the selected clause body. `and` and
`or` short-circuit left to right. All operands must still type-check.

| Operator | Arity and types | Meaning |
|---|---|---|
| `+`, `-`, `*` | Two `Int` arguments, result `Int` | Mathematical sum, difference, product |
| `<`, `<=`, `>`, `>=` | Two `Int` arguments, result `Bool` | Mathematical order |
| `=` | Two values of the same core type, result `Bool` | Structural equality, including all constructor fields |
| `and`, `or` | Two `Bool` arguments, result `Bool` | Short-circuit conjunction/disjunction |
| `not` | One `Bool` argument, result `Bool` | Negation |

An `if` condition is `Bool`; there is no truthiness. Operators are not values and
have no partial application or variable arity. Mathematical evaluation of a valid
core program terminates because calls and data are acyclic and primitives terminate.
Actual execution may still exhaust finite resources.

A future numeric profile must preserve exact `Decimal` values, equality independent
of stored scale, explicit rounding and no silent conversion. Exact decimal division
requires nonzero divisors and finite representability. Integer division/remainder
sign rules must be fixed before adding those operators. Modelling decimals as reals
requires a sound abstraction of each operation and its definedness; subset inclusion
alone is not that justification.

## Contracts, examples and verification

### Meaning of a claim

`requires` expressions are Boolean and may read parameters. `ensures` expressions
are Boolean and may additionally read `result` at the declared return type. Multiple
expressions in either block form a left-to-right short-circuit conjunction. Omitted
blocks mean `true`; reports must identify omitted and explicitly trivial contracts.
Acceptance of a trivial claim must not be described as meaningful domain correctness.

Contracts are pure core expressions subject to the same type and dependency rules
as bodies. Calls in contracts must meet their callees' preconditions wherever
evaluated. A function's precondition must itself be well-defined for every typed
input; it cannot assume itself true to justify a partial helper call. Postconditions
are checked under the precondition and actual body-result relation.

For body `body_f`, parameters `x`, precondition `Pre_f` and postcondition `Post_f`,
the total-correctness claim is:

```text
for every typed x:
  Pre_f(x) implies evaluation(body_f, x) terminates with a value v
                   and Post_f(x, v)
```

This quantification describes the judgment, not quantifier syntax added to the
language. Termination, definedness and postcondition obligations must be accounted
for separately even when termination follows structurally. No claim guarantees a
bound on machine memory, execution time or external response.

### Examples

Every function needs an example directly calling that same function. Arguments and
expected outputs must be closed values of the declared types, including constructors.
Each input must satisfy the precondition; the actual result must equal the expected
value and satisfy the postcondition. An unrelated expression cannot stand in for
an example of the function.

Examples demonstrate concrete behaviour and a nonempty valid input domain. They
are not universal proof, adequate coverage or evidence of test-first development.
An example failure is not a universal proof counterexample unless it also witnesses
the independently stated universal claim.

### Verification obligations and the initial fragment

Every declaration, branch and call is resolved and typed before proof. Every
potentially evaluated call emits a precondition obligation under its path condition.
Each function emits obligations connecting its body to its postcondition. Example
validity, contract definedness and structural termination have separate records.
An unreachable path can make an obligation vacuous; it does not excuse invalid
syntax, names, types or arity in that path.

The initial automated fragment is quantifier-free Boolean reasoning, linear integer
arithmetic and the non-recursive algebraic data of `core-0`, after semantics-preserving
expansion of acyclic calls. Conditionals and matches retain their path conditions.
Multiplication is linear only when one operand is a known integer constant after
sound normalisation. General `Int` multiplication is executable core syntax but
outside required `verify-0` automation. An obligation remaining outside the fragment
returns unknown with that reason; it must not be translated unsoundly.

Inlining is a valid initial strategy, not a mandate to expand without resource
bounds. The encoder must specify every emitted logical primitive's meaning. Replacing
calls with assumed postconditions is permitted only with independently established
callee obligations and a justified modular proof rule. No cyclic proof assumptions
or uninterpreted predicates standing in for required semantics are allowed.

The implementation must document its translation and justify that a discharged
obligation establishes the corresponding source claim. Parser, type checker, encoder,
solver, runtime and backend remain trusted components until stronger evidence exists.
`trust` and unchecked source axioms are absent from these profiles. This does not
mean that the trusted computing base is empty.

### Results and evidence scope

| Dimension | Required distinction |
|---|---|
| Logical obligation result | `proved`, `disproved`, `unknown`, or `not_attempted` |
| Execution status | Completed, unsupported, timed out, cancelled, resource exhausted, invalid input or tool failure |
| Claim kind | Types, termination, examples, function correctness, invariant induction, bounded exploration, finite-model exploration, safety refinement or liveness |
| Scope | Types, domain/preconditions, assumptions, model parameters and any trace/state bounds |
| Provenance | Source/dependency digests, claim/expectation version, compiler/encoding/solver/runtime versions and configuration |

Only a completed justified result may be `proved`. An interrupted or timed-out proof
is unknown with its execution reason retained. A checker that never ran has
`not_attempted`, not success. Logical truth and proof-search robustness remain separate.
Tool failures and conflicting solver results block acceptance; they do not become
semantic counterexamples. No evidence kind silently upgrades another kind.

An aggregate verified result requires a complete inventory of required obligations,
all discharged, plus passing examples and static checks for the selected profile.
The inventory identifies structurally discharged checks as well as solver checks.
No unsupported function or missing dependency may erase unrelated obligations.
Incomplete verification must never produce an artefact labelled verified.
The standard `build` operation fails closed while required verification is incomplete
or unavailable and publishes no executable artefact. Internal evaluation during
compiler development is not a release build or evidence of verified-build conformance.

Disproof requires a validated source-level witness satisfying the claim's assumptions
and violating its conclusion. Function witnesses must replay against the reference
semantics within a declared replay budget; failed validation yields unknown, not an
invented disproof. An induction-step witness and a reachable execution trace are
different evidence types; only a validated initial state and transition sequence
may be called a reachable counterexample.

The initial implementation may trust a selected solver's validity result, disclosing
that trust. Independent proof certificates or a small checking kernel can strengthen
later assurance, but must not be claimed because two solvers or seeds agree. Future
proof caches must include the complete semantic dependency closure and configuration.

### Requirement integrity during repair

Approved public claims and acceptance examples have identities and revisions separate
from bodies. An edit must disclose changes to input domains, guarantees, examples,
effects, trust and environmental assumptions. Weakening a guarantee, strengthening
a precondition or deleting an example cannot count as an implementation repair under
the unchanged claim version.

Where implication or equivalence can be established, tools may report it. Otherwise
the semantic relationship is undetermined and requires requirement review. Independently
approved expectations, adversarial tests and mutation checks assess whether the claim
is useful; a proof cannot settle that.

## Effects and termination

Pure functions are deterministic and cannot read time, randomness, environment,
filesystem, network or hidden mutable state. In `core-0` all functions are pure.
Mathematical termination follows from core restrictions, not a runtime step cap.
Exceeding a budget is resource exhaustion, not proof of divergence.

A later recursion profile must define a well-founded termination rule covering all
recursive cycles, including mutual recursion and specification calls. A measure must
belong to its declared well-founded domain and strictly decrease at the required
edges; a scalar natural-number measure must also be nonnegative. Writing `decreases`
does not establish termination. General correctness and termination are not promised
decidable for arbitrary later extensions.

A later effects profile must declare authority in interfaces and check actual uses.
Capabilities come from an authorised runtime or checked attenuation, never ordinary
value construction. Scope rules must distinguish enclosing capabilities from explicit
parameters. Capture and aliasing rules must be specified before those features are
supported. Stubs must accept the same data shapes as their real interfaces.

Permission does not prove successful IO, atomicity, retry safety, secrecy or liveness.
External values need validation before entering refined types or satisfying
preconditions. Adapter guarantees, environmental errors and contract faults must be
distinguishable. Completed effects cannot be treated as undone because a later
operation failed.

## State machines and temporal properties

### Machine boundary

`machine-0` uses named core functions and types, not new temporal expression syntax.
A machine descriptor identifies state/event/outcome types, initialiser, transition,
outcome-to-state projection, admissibility predicate, invariant and runtime assumptions.
Its exact versioned transport schema must be fixed before machine operations ship.

The roles are `init : Unit -> State`, `step : (State, Event) -> Outcome`,
`state-of : Outcome -> State`, `admissible : (State, Event) -> Bool`, and
`invariant : State -> Bool`. A nullary source function supplies `init`'s Unit input.
These describe roles, not higher-order core values. The descriptor resolves checked
function names. Initialiser, projection, invariant and admissibility functions must
have preconditions valid for every input of their respective declared types. The
step may require an invariant state. Calls inside all helpers still need their own
preconditions established; predicates cannot hide undefined behaviour behind assumptions.

Outcome includes the new state and observable acceptance/rejection result. Every
observable relevant to a claim must appear in its model. A later pure extension
may return command descriptions for an authorised host, conceptually
`State × Event -> State × List Command`; this does not add `List` to `core-0`.
Issuing a command is not evidence that its effect occurred. Results and failures
return as explicit events with checked data.

### Initial states, transitions and invariants

For the first deterministic initialiser, `Init(s)` means `s = init()`. Define:

```text
Transition(s, e, outcome, s') iff
  admissible(s, e) and Pre_step(s, e)
  and outcome = step(s, e) and s' = state-of(outcome)

Next(s, s') iff there exist typed e and outcome such that
                 Transition(s, e, outcome, s')
```

The existential is model notation, not a new expression construct. Proof obligations
range symbolically over typed events; an unbounded event type must not be enumerated
as though finite. Host delivery may choose among events, so deterministic handlers
do not make the whole system deterministic.

`Next` is the state projection used for invariant reasoning. The observable model
also retains the event and outcome of `Transition`; output or refinement claims
must not use the projection to discard observable differences. The separate
precondition obligation below prevents a stronger step precondition from silently
removing required transitions.

For candidate inductive invariant `Inv`, establish:

```text
Init(s) => Inv(s)
Inv(s) and admissible(s, e) => Pre_step(s, e)
Inv(s) and admissible(s, e) => Inv(state-of(step(s, e)))
```

Account for initialiser/projection/predicate preconditions and definedness. If a
stronger inductive invariant `Ind` is needed, prove initialisation and preservation
for `Ind`, then `Ind => Safety`; do not substitute the weaker safety predicate
without checking inductiveness. An inconsistent initial condition or unsatisfiable
required domain must not silently certify a useful machine.

The first runtime executes transitions sequentially with one authoritative state.
It validates event data and admissibility, then publishes returned state and outcome
together. No unmodelled writer can modify state between checking and publication.
Events outside the admissible domain receive explicit boundary rejection with unchanged
state. These differ from admissible events whose business result is rejection. Include
the boundary when making claims about all external requests.

Machine evidence is conditional on this model. Function proofs alone do not establish
host atomicity or delivery guarantees. A concurrent runtime needs a separate
serialisation/refinement argument.

### Behaviours, progress and abstraction

A safety behaviour starts in `Init` and follows `Next` transitions or stuttering
steps leaving all modelled state unchanged. No fairness is assumed by default. If
outputs/effects are relevant observables, an unchanged local state with a changed
output is not a stuttering step of that full model.

Handler termination and invariant preservation do not imply request completion,
eventual responses or system termination. A later liveness claim must state its
temporal property, action/environment model, fairness assumptions and proof method.
Weak fairness concerns continuously enabled actions; strong fairness concerns actions
enabled infinitely often. Neither supplies missing environmental guarantees such as
eventual message arrival or capacity becoming available.

A ranking function supports progress only with justified conditions on intervening
transitions and scheduling. Natural-number measures do not make general liveness
decidable. Infinite stuttering is allowed by the safety model and can refute progress
unless excluded by sufficient explicit assumptions.

Safety refinement identifies a mapping `alpha` from concrete to abstract state and
proves initial correspondence and that each concrete transition maps to an abstract
transition or stutter. Include concrete invariants and visible outputs. These
simulation obligations alone do not establish liveness refinement; progress and
possible infinite concrete stuttering need a separate argument. This simple mapping
discipline is a starting method, not every possible TLA+ refinement proof.

### Model exploration and TLA+ integration

Complete finite-model exploration establishes the checked property for that model.
Bounded exploration establishes only that no violation was found within the specified
domain and trace bound. Random simulation establishes observed runs. Inductive
reasoning can establish invariants without a trace-length bound, under its assumptions.
Metadata must preserve these distinctions and any reductions, abstractions or state
constraints affecting exploration.

TLA+/TLC or Apalache integration is an optional later adapter. Export must preserve
the chosen transition semantics and record source/mapping identity. External checker
acceptance concerns that model; executable conformance also needs the implementation/
model connection. `machine-0` claims neither full TLA+ syntax, temporal proof automation
nor automatic refinement.

## Tooling and runtime agreement

### Agent interface

The compiler is a versioned JSON service. Its manifest lists supported profiles,
operations, syntax/library signatures, contracts/effects, diagnostic schemas and
resource limits. Initial operation categories are discovery, parsing, formatting,
checking, verification, examples and building. Fix their request/response schemas
with positive and negative fixtures before release. Advertise unimplemented operations
as unavailable and refuse them explicitly.

Diagnostics contain a stable category, expected/actual information where relevant,
source revision, location or structural path, symbol/obligation identity and precise
reason. Invalid programs, unsupported reasoning and tool failures are distinct.
Agents must discover signatures and bindings without guessing undocumented APIs.
Long explanations supplement structured data.

Results and edits bind to source/dependency revisions. Stale evidence cannot certify
a changed artefact. A future edit operation must reject stale targets and rename
resolved bindings. Draft holes or incomplete trees may receive partial checking in
a later tooling profile, but cannot become verified programs. Decoder constraints
are not assumed to establish semantic correctness.

### Compilation and entry boundary

Parsing, static checking, logical encoding, examples and generated execution must
implement the same semantics. Verification binds to the typed program and backend
configuration used for output. Differential checks and independent calculations are
required evidence, not a claim that the compiler itself is proved.

Build once and execute fresh inputs. Constant-folding is permitted; replacing a
runtime program with precomputed example output is not conformance. The first adapter
invokes named entry functions selected in build metadata. External inputs must decode
to declared types and satisfy entry preconditions before calling compiled code;
rejection has no successful return value. Internal contract failure in a supposedly
verified execution is an assurance failure, not an ordinary domain error or success.

Transport must preserve arbitrary-precision integers and distinguish nominal types,
constructors and fields. Framing, error schema, cancellation and executable target
are required decisions before that adapter's implementation. Passing JSON numbers
through binary floating point would violate integer semantics.

### Resources and build authority

Operations have declared input, time, memory and output budgets, with controlled
diagnostic failure on exhaustion. Totality does not guarantee sufficient resources.
Limits are observable and included in evidence; they must not silently become
semantic bounds on the program's mathematical domain.

Outputs stay within authorised destinations even under path traversal, symlinks and
concurrent filesystem changes. Enforcement governs writing, not only inspection
afterwards. Existing outputs survive failed builds unless replacement was authorised
under documented transactional rules. Build authority is separate from program effects.

## Core conformance example

This source uses only `core-0`. It is a normative semantic example, not a claim that
a compiler has parsed or proved it. A two-unit reservation component accepts reserve
below capacity, accepts release above zero, and otherwise rejects without changing
state. Acceptance is observable: “reject everything” is incorrect even if safe.

```lisp
(deftype Reservation (record (reserved Int)))
(deftype Event (union (Reserve) (Release)))
(deftype Outcome (record (state Reservation) (accepted Bool)))

(defn valid-state
  (sig ((current Reservation)) -> Bool ! pure)
  (examples
    (example (valid-state (Reservation 0)) => true)
    (example (valid-state (Reservation 3)) => false))
  (and (>= (.reserved current) 0) (<= (.reserved current) 2)))

(defn initial
  (sig () -> Reservation ! pure)
  (ensures (= result (Reservation 0)))
  (examples (example (initial) => (Reservation 0)))
  (Reservation 0))

(defn step
  (sig ((current Reservation) (event Event)) -> Outcome ! pure)
  (requires (valid-state current))
  (ensures
    (valid-state (.state result))
    (= (.accepted result)
       (match event
         ((Reserve) (< (.reserved current) 2))
         ((Release) (> (.reserved current) 0))))
    (= (.reserved (.state result))
       (+ (.reserved current)
          (if (.accepted result)
              (match event ((Reserve) 1) ((Release) -1))
              0))))
  (examples
    (example (step (Reservation 0) (Reserve)) => (Outcome (Reservation 1) true))
    (example (step (Reservation 2) (Reserve)) => (Outcome (Reservation 2) false))
    (example (step (Reservation 1) (Release)) => (Outcome (Reservation 0) true))
    (example (step (Reservation 0) (Release)) => (Outcome (Reservation 0) false)))
  (match event
    ((Reserve)
      (if (< (.reserved current) 2)
          (Outcome (Reservation (+ (.reserved current) 1)) true)
          (Outcome current false)))
    ((Release)
      (if (> (.reserved current) 0)
          (Outcome (Reservation (- (.reserved current) 1)) true)
          (Outcome current false)))))
```

For a `machine-0` descriptor, additionally supply checked projection and admissibility
helpers. Here projection selects `.state` and all typed events are admissible in
an invariant state; the step precondition still needs proof.

| Before | Event | After | Accepted |
|---|---|---|---|
| 0 | Reserve | 1 | true |
| 1 | Reserve | 2 | true |
| 2 | Reserve | 2 | false |
| 0 | Release | 0 | false |
| 1 | Release | 0 | true |
| 2 | Release | 1 | true |

The table defines all transitions of this finite count/event model. Future conformance
checks must also reject malformed values and invalid entry states. A missing upper
guard must be detected despite examples visiting only non-full states; a changed
acceptance flag must fail the contract even when the invariant holds. Use the real
compiler and executable for these checks once implemented.

## Empirical evaluation

Measure independent correctness under fixed total token and compute budgets, counting
unsuccessful attempts, verification cost and human intervention. Compare equivalent
tasks/tools against a familiar typed functional language and an established verification
language. Include fresh tasks, withheld checks, requirement changes and repairs;
compilation rate alone is not the outcome.

Evaluate syntax, mandatory examples, discovery and repair feedback separately where
possible. Do not attribute a stronger checker's benefit to syntax. Record model/tool
versions and repeated-run variation. Formal evidence and empirical effectiveness
answer different questions and remain separate reports.

## Deferred scope

Recursion, recursive/generic data, general higher-order functions, Decimal, Text,
Bytes, collections and effects need their own conformance slices. Ordinary failures
in those profiles use explicit algebraic outcomes such as `Option` and `Result`.
No universal ban on useful abstraction follows from core limits.

Concurrency, liveness checking, refinement automation, model-checker adapters,
independent proof kernels, proof caches, structural editing, self-hosting and broad
libraries are not first-compiler commitments. Pricing, Huffman and Tetris are later
candidate tasks. Reservations are the first recommended conformance target, not
permission to start a whole delivery roadmap without planning.

## Reference alignment

Sources inform design choices; their guarantees do not transfer without a justified
implementation. Alignment adopts relevant principles, not every feature or tool.

| Reference | Adopted principle | Boundary |
|---|---|---|
| [TLA+ model](https://lamport.azurewebsites.net/tla/high-level-view.html) | Initial states, transitions and behaviours | Runtime/model correspondence needs evidence |
| [Stuttering and refinement](https://lamport.azurewebsites.net/tla/stuttering.html?back-link=advanced.html) | Observable abstraction and stuttering-aware correspondence | Safety simulation does not prove liveness |
| [Safety, liveness and fairness](https://lamport.org/tla/safety-liveness.pdf) | Separate safety from progress under assumptions | No default fairness or general liveness decision procedure |
| [TLC](https://lamport.azurewebsites.net/tla/tools.html) and [Apalache](https://apalache-mc.org/docs/apalache/running.html) | Distinguish model exploration and induction | Bounds and translation assumptions remain visible |
| [Dafny](https://dafny.org/dafny/DafnyRef/DafnyRef) | Contracts, call obligations and termination reasoning | No requirement to adopt its object model/backend |
| [F*](https://fstar-lang.org/) | Functional core with effects and proof-oriented abstraction | No immediate dependent-type or unrestricted higher-order requirement |
| [Lean's kernel](https://lean-lang.org/doc/reference/latest/Elaboration-and-Compilation/) and [proof validation](https://lean-lang.org/doc/reference/latest/ValidatingProofs/) | Separate producing/checking evidence and protect the intended claim | No independent kernel claimed for initial SMT checking |
| [Clover](https://arxiv.org/abs/2310.17807) and [F* synthesis](https://arxiv.org/abs/2405.01787) | Investigate checking feedback and discoverable typed context | Results are not measurements of Prova |
| [Grammar constraints](https://arxiv.org/abs/2305.13971) | Constrain generated syntax | Grammar validity is not requirement correctness |
| [Dafny verification optimisation](https://dafny.org/dafny/VerificationOptimization/VerificationOptimization) | Measure search cost/variability separately | Search reliability is not logical validity |

## Implementation decisions still required

The semantics above are current draft decisions, not questions each builder must
invent answers to. Before dependent implementation, select the bootstrap language,
backend and solver with their trust boundary; fix layout and JSON schemas with
fixtures; choose runtime framing and exact value representation; set measured budgets
and safe output handling; and map the first slice to independently reviewed Relay
expectations.

These are scoped decisions, not reasons to reopen every language choice or block
unrelated work. Changes must record their semantic effect and revise conformance
expectations, rather than quietly accommodating implementation behaviour.
