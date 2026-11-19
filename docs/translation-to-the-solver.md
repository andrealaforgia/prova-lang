# What this tool writes for the solver, and why it settles your claim

When `verify` answers that an obligation is `proved`, something was
written down and handed to a solver. This document says what was
written, what each part of it means, and why the solver settling it
settles the claim your source makes.

The `discover` operation publishes the version of this translation, the
list of primitives below and the path of this document, so an answer
always points at the version of this text that belongs to it.

## What the translation covers

Only this, and deliberately nothing more:

- the unbounded whole numbers of `core-0`, their sum, difference and
  order, and equality;
- multiplication **only** where one operand is written as a literal;
- the booleans, the connectives and `if`;
- the single value of `Unit`;
- the records and unions a program declares, which are never recursive
  in this profile, their constructors and their fields;
- `match`, where each pattern is a wildcard, a name, a whole number, a
  boolean, the unit value or a constructor with no fields of its own;
- calls to declared functions, expanded in place.

An obligation that needs anything else is answered `unknown` with that
reason, and **nothing is translated for it at all**. That includes a
`let` binding, a pattern carrying patterns of its own, and the product of
two numbers neither of which is a literal — which SPEC.md puts outside
the automation required at this stage. Anything a later profile adds is
unsettled here rather than guessed at.

## Every primitive, and what it means

- `integer` — a whole number exactly as the program writes it, in the
  mathematical integers: no width, no wrapping and no largest value.
- `variable` — one value of a declared type, standing for every value
  that type has: the parameters of the function the obligation is about.
- `truth` — the boolean the program writes as `true`.
- `falsity` — the boolean the program writes as `false`.
- `unit` — the single value of the type `Unit`, written `()`.
- `sum` — the mathematical sum of two whole numbers.
- `difference` — the mathematical difference of two whole numbers.
- `product` — the mathematical product of two whole numbers, written only
  where one of them is a literal, which keeps the arithmetic linear.
- `less` — whether the first whole number is below the second.
- `at_most` — whether the first is below the second or equal to it.
- `greater` — whether the first whole number is above the second.
- `at_least` — whether the first is above the second or equal to it.
- `equals` — whether two values of one type are the same value, which for
  the shapes below means the same constructor with the same field values
  throughout.
- `conjunction` — all of the given conditions are true at once.
- `disjunction` — at least one of the two conditions is true.
- `negation` — the condition is not true.
- `conditional` — the value of the second term where the first condition
  is true and of the third where it is not; what both `if` and `match`
  become.
- `shape` — one value made by a declared constructor from its field
  values: a record, or one variant of a union, never a recursive one.
- `field` — the value of one declared field of a value built by a
  constructor.
- `is_shape` — whether a value was made by the constructor the term
  names.

## Why each translation is faithful to the language

Each line below is a premise. If one of them were false, a `proved` from
this tool could be wrong, so each is stated rather than assumed.

**Whole numbers.** SPEC.md says `Int` is arbitrary precision and must not
silently overflow. The solver's integers are the mathematical integers
and the evaluator's are Python integers, which are unbounded. There is no
width on either side, so no input exists at which the two differ.

**The connectives.** `and` and `or` short-circuit left to right in
`core-0`. Short-circuit and strict evaluation agree for every expression
that is total and free of effects, and in this fragment every expression
is: the profile has no division and no other partial primitive, no
effect, and no call that fails to end. So the strict connectives mean the
same thing here. Division is the operation that would break this
argument, and it is not in the profile at all.

**Records and unions.** Each declared type becomes one freely generated
datatype: distinct constructors build distinct values, every value is
built by one of them, and two values are equal exactly when they are the
same constructor over equal fields. That is what structural equality
means in `core-0`, which is why `=` translates to equality, and it is
what makes an exhaustive `match` exhaustive on both sides.

**`match`.** The clauses become a chain of conditionals in source order,
so the first matching clause still wins. The last clause is the final
alternative with no test of its own: the checker that accepted the
program has already shown the match exhaustive over the scrutinee's
type, so nothing but a value that clause matches can reach it.

**Field selection.** Selection is defined only on records and is
resolved from the operand's nominal type by the checker, so an accessor
is only ever applied to a value of its own constructor.

**Calls.** A call becomes the callee's body with its parameters standing
for the arguments. SPEC.md names inlining a valid initial strategy. The
combined dependency graph of bodies and contracts is acyclic in
`core-0`, so the expansion ends; a bound on how far it may go is kept
anyway, and an obligation that passes it is left unsettled rather than
answered from half a translation. A callee's postcondition is **never**
assumed in place of its body: SPEC.md permits that only with
independently established callee obligations and a justified modular
proof rule, and this tool has neither.

## Why settling the formula settles your claim

The translation defines a **total** reading of a `core-0` program: every
well-typed expression denotes a value, because the profile has no partial
primitive, no effect and no call that fails to end. The evaluator agrees
with that reading wherever it returns a value at all. Where it does not
agree it does not return a different value — it refuses, and a refusal is
not a counterexample to anything. Three things make it refuse, the same
three listed under contract definedness below: a callee's precondition
that does not hold, a callee's postcondition that does not hold, and the
evaluation depth budget.

So, obligation by obligation:

- **a body against its postcondition.** The claim is: for every input of
  the declared types that meets the function's precondition, what the
  body answers satisfies the postcondition. Shown over the total
  reading, it holds of every run that returns a value. That is the
  promise the function makes.
- **a call's precondition.** The claim is: wherever the condition that
  reaches the call holds, the callee's precondition holds of the
  arguments. The condition that reaches it — the function's own
  `requires`, plus every branch and clause on the way down — is
  **assumed**. That is why a call standing behind a test that establishes
  its precondition is provable, and the same call with nothing in front
  of it is not. Where the call stands in what the function promises, the
  function's answer is in scope and stands for its body, because only a
  postcondition may read it.
- **a declared example.** The claim is: the arguments meet the
  precondition, and what the function answers over them is the value the
  example states. The arguments are closed values, so the formula has no
  variable in it.
- **a contract's definedness.** Not sent to a solver, and the narrowest
  of these claims. Read over the total meaning of `core-0` above, every
  operation the profile has is defined for every value of its declared
  types. That is all this entry claims. It does **not** claim that
  running a clause answers a value, because three things can stop a run
  of one: a call whose precondition does not hold, a call whose
  postcondition does not hold — which the evaluator checks and refuses —
  and the evaluation depth budget, which stops a run that nests deeper
  than this tool runs. The first is a call-precondition obligation of
  its own, listed and settled separately; the second is the callee's own
  body-to-postcondition obligation, also listed; the third is a budget
  this tool declares and is not a statement about your program.
- **a function's structural ending.** Not sent to a solver. The checker
  refuses any program whose combined dependency graph has a cycle, so
  every call this function can reach ends, and so does it.

Those last two carry `discharged_by: "structure"` instead of `"solver"`,
so you can see at a glance which of your obligations rest on a solver's
word and which on the two rules just stated.

When you send a machine descriptor with a `verify` request, three more
obligations join that list, and the same reading settles them. SPEC.md
lines 395-401 state them for the candidate invariant `Inv` your descriptor
names: `Init(s) => Inv(s)`, `Inv(s) and admissible(s, e) => Pre_step(s, e)`
and `Inv(s) and admissible(s, e) => Inv(state-of(step(s, e)))`. Each becomes
one claim of exactly the shape above. The first has no variable in it: the
initialiser takes nothing, so the formula is the invariant read over the one
state it answers, which is why an initial condition nothing satisfies is
caught here and by nothing else — preservation of a condition no state
satisfies is valid for an empty reason, and a machine certified on it would
be certified for having no states. The other two take the two parameters the
step declares, which become one symbolic value of the state type and one of
the event type: the formula says what it says for *every* value of that
event type, so nothing lists the events and an event type with no bound —
one carrying a whole number, say — is read exactly as one with two values,
as SPEC.md lines 384-386 require. The invariant, the admissibility
predicate, the projection and the step reach the formula the way every other
call does, by the translation reading a call as the callee's body over its
arguments, so no new primitive and no wider fragment is involved; an
obligation whose roles reach a construct this translation does not cover is
left unsettled with that reason, exactly like any other. Two of the three
also say, beside themselves, that the replay gate confirms no witness for
them: this tool calls a solution a counterexample only when running the role
function over it makes the reference semantics refuse, and neither an
initialiser answering a state outside the invariant nor a step leaving it is
a refusal. So an invariant that is not inductive on its own leaves
preservation unsettled, never `proved`, and no weaker predicate is put in
its place. Everything these three say is conditional on the model your
descriptor states (SPEC.md line 416): the assumptions it lists are carried
into the answer as stated and this tool checks none of them, and a proof
about the step functions is not a statement about the runtime that calls
them.

## How the three answers are decided

A claim is `assumptions implies conclusion`, and it is valid exactly when
`assumptions and not conclusion` has no solution. That is the one
question the solver is asked.

| The solver says | You are told | Execution status |
|---|---|---|
| no solution | `proved` | `completed` |
| a solution, and running the program over it is refused for this claim | `disproved`, with that input | `completed` |
| a solution that is **not** refused when run | `unknown`, saying the candidate did not replay | `completed` |
| it could not tell, out of time | `unknown` | `timed_out` |
| it could not tell, for its own reason | `unknown`, with that reason | `completed` |
| nothing was asked: outside the fragment | `unknown`, with the construct named | `unsupported` |
| nothing was asked: the solver could not be loaded | `unknown`, naming it | `tool_failure` |

A solution is only ever a **candidate**. SPEC.md requires a disproof to
carry a validated source-level witness and says a failed validation
yields `unknown` rather than an invented disproof. So the solution is
written back as values of your program and run through this tool's own
evaluator, and only an input the evaluator really refuses is reported to
you as a counterexample — written the way a program writes it, so you can
hand it straight to a run.

## What this tool does not claim

- **The solver's word is taken, not checked.** Every answer a solver
  really answered about carries that disclosure beside its result, and
  names the solver and its version. An answer carries none when every
  obligation was settled by a rule, when every one was left outside this
  fragment, or when a solver was needed and could not be loaded — in
  that last case nothing was answered, so there is nothing to disclose,
  and `stands_on` says a solver was needed and could not be had. This tool keeps no proof certificate and runs no
  checking kernel of its own. A defect in the solver, or in the
  translation described here, would reach you as a `proved`.
- Parser, type checker, this translation, the solver and the runtime are
  all trusted. That is not an empty list.
- `proved` is a statement about one revision of one source, named by the
  digest the answer carries, and about nothing else.
- Nothing here is a proof that the translation itself is correct. Its
  soundness is exercised by generated tests that run every proved
  program through the evaluator and require the two never to disagree,
  which is a search for counterexamples and not an assurance.
