# Prova restart: retained semantic requirements

Status: restart baseline, extracted from the previous v0.9.1 draft and review
findings on 2026-09-27. This is not a complete grammar, an approved implementation
plan or a claim that any feature exists. The first supported subset must be made
precise through the questions in [EXPECTATIONS.md](docs/EXPECTATIONS.md).

The old specification is available in Git at
`093fb86443c057c1d3abb4f1c033d1a6bf601d38:SPEC.md` and in the external archive.
Its detailed policies are historical context, not additional restart obligations.
Do not import its whole feature set or claim v0.9.1 conformance by default.

## Purpose and limits of the claim

Prova occupies the position of a programming language. It has no natural-language
surface or domain-description layer. Such tools may generate Prova independently.

The compiler must distinguish well-formed syntax, valid names and types, permitted
effects, contract satisfaction, example results and executable behaviour. Evidence
for one does not establish the others. In particular, proving a contract does not
prove that it expresses the owner's intent. Independent requirements and acceptance
evidence remain necessary.

## Source and values

Retain UTF-8 s-expressions as the starting syntax and a single canonical format.
Accept well-formed non-canonical source; formatting alone is not a compilation error.
Numeric spellings denote values, not observable lexical histories. Formatting must
preserve meaning and be idempotent. Exact grammar, comment preservation and the
machine-readable tree schema must be fixed before implementing their supported subset.

Values are immutable. Types and function signatures are explicit; implicit
conversions and truthiness are absent. An `if` condition is `Bool`. Operators and
named calls have checked arity and argument/result types. Both branches of an `if`
are checked even when supplied examples visit only one branch. The same checking
rules apply inside builtin calls and user-defined calls.

Evaluation is strict and left to right, subject to explicitly specified special
forms. A `let` evaluates bindings sequentially, so later bindings can use earlier
ones. Names resolve lexically. Preserve the previous prohibition on shadowing visible
bindings and prelude names; diagnostics should identify both conflicting sites.
The exact binder namespaces and scope of declarations must be specified before use.

The intended value model includes `Unit`, `Bool`, arbitrary-precision `Int`, exact
`Decimal`, `Text`, `Bytes`, immutable collections, records and tagged unions.
Expected failures use `Option` and `Result`. This is a direction for expansion, not
a requirement to implement all of these in the first slice. Refinements add
predicates over existing types when supported.

`Int` must not silently overflow. For `Decimal`, equality is numeric: trailing zeros
and stored scale are unobservable. Arithmetic is exact and never silently rounds;
rounding and rendering precision are explicit operations. Exact division requires a
nonzero divisor and a finitely representable result. A solver model over reals must
not introduce impossible decimal values as alleged source-language counterexamples.
Integer division, modulo, negative operands and literal typing still need a complete
operator table for the new supported subset.

## Contracts, examples and verification

Retain function preconditions, postconditions and executable examples. `result` in
a postcondition denotes the actual returned value. A typical historical declaration
shape is shown below; the fixture corpus uses this syntax, but it is not a complete
grammar definition.

```lisp
(defn nonnegative
  (sig ((amount Int)) -> Int ! pure)
  (requires (>= amount 0))
  (ensures (= result amount))
  (examples (example (nonnegative 2) => 2))
  amount)
```

Examples are mandatory for ordinary function declarations in the retained design.
Their expected outputs and contracts must hold. Finite examples do not prove a
universal postcondition, and their presence does not establish test-first development.
Omitted contracts historically meant `requires true` and `ensures true`; if retained,
that must remain visibly a trivial claim, never a correctness endorsement.

Verification must connect each obligation to the implementation, its environment
and its assumptions. Preconditions are obligations at call sites. Postconditions
cover all possible returns under the precondition. Nested/module declarations do
not escape checking. Unsupported reasoning in one declaration must not silently
remove another declaration's obligations.

Report proved, disproved and unknown separately. An unsupported fragment, exhausted
budget or failed verification dependency cannot yield a proved result. A verified
build cannot succeed with outstanding required obligations. Never silently omit
obligations, replace universal reasoning with examples, or treat an empty obligation
list as proof that all required obligations were checked.

Counterexamples must satisfy the source-language types and preconditions and
demonstrate the claimed violation. Record enough information to replay them. If
the compiler cannot establish that a solver witness is valid, report the limitation
honestly rather than inventing a disproof.

Trust defaults to zero. The initial subset should have no trust escape hatch.
Any later assumption mechanism needs explicit scope, reporting and acceptance
criteria. A proof-fragility policy, multiple solvers, seed variation and proof caching
are separate design decisions; none is a prerequisite imposed by this restart.

## Effects and termination

A pure function is deterministic and has no external effects. Effectful signatures
declare capability authority and the compiler checks actual use against it.
Capabilities cannot be forged by program code. Runtime-provided capabilities and
approved attenuation define the authority boundary.

Preserve the distinction between capabilities in enclosing module scope and those
passed as function parameters. An effect row must not be limited accidentally to
parameter names. Any closure support must define and enforce capability capture.
Deterministic stubs for effectful examples must support the operation's actual data
types, including constructor-valued results, when that feature is introduced.

Termination claims must be justified by the supported language, such as an acyclic
call graph initially or checked decreasing measures later. Mathematical termination
does not bound practical memory, elapsed time, external IO or the lifetime of an
event loop. Do not promise machine availability from a termination proof.

## Tooling and runtime agreement

Provide a versioned JSON interface with stable diagnostic categories, source
locations or structural paths, and explicit operation outcomes. Keep language
version, supported fragment, available functions and signatures discoverable by an
agent. Documentation must distinguish supported operations from proposed ones.

Define one semantics that static checking, verification, example execution and
generated execution all respect. Check that agreement with independent tests and
reference calculations, not only helpers shared by both implementation paths.
Executing examples or emitting their precomputed output does not demonstrate a
compiler that handles fresh runtime inputs.

The compiler must bound its own resource use and diagnose exhaustion without
crashing. Permitted input limits and cancellation behaviour need explicit contracts.
Build outputs must stay within authorised destinations, including in the presence
of path traversal, symlinks and concurrent filesystem changes. A check made only
after a write cannot enforce that boundary. Existing output preservation must be
specified and tested. These protections apply when output writing is introduced;
no previous security waiver carries forward.

## Deferred scope

Self-hosting, general higher-order functions, concurrency, structural project editing,
advanced proof guidance, proof caching, trust budgets and broad standard libraries
need demonstrated use cases before entering scope. Go remains a possible bootstrap
implementation and target, not a semantic property of Prova.

Pricing is a candidate first domain task. Huffman coding and deterministic Tetris
state transitions are later stress tests, not first-iteration commitments. Retain
their domain requirements if selected, not the old launchers' rebuild-per-input
workaround. Compression needs independent optimality/size checks as well as
round trips; a game needs independently checked rules as well as replay consistency.
