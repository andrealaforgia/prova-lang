# Prova roadmap: from a half-built front end to a finished `core-0` / `verify-0` / `machine-0` compiler

Author: product owner. Written 13 November 2026 against `main` at commit `2bea72c`.

Authority: `SPEC.md` (restart draft 0.2) only. This roadmap proposes no change to
any requirement in it. Where I think a requirement should change, I say so in
section 7 as a proposal for the Owner, and I plan around the text as it stands.

Scope note: I ignored `.relay/`, `docs/RELAY.md`, `docs/relay*`,
`docs/user-stories.md` and all I1/I2 story numbering. Nothing in this roadmap
depends on them. The 772 existing tests keep their current `I1.Sx` file names;
renaming them is churn with no product value, so I do not plan it.

---

## 1. Where the compiler is today

**Verdict: the front end works and is about half honest. The verifier, the state
machine layer and the executable do not exist.**

| Layer | State | Evidence |
|---|---|---|
| Read, parse, type-check `core-0` | Works for well-formed programs | `docs/spec-trace.md` §1-§3; 772 tests pass in 65 s (I ran `uv run pytest -q tests`) |
| Refuse ill-formed `core-0` programs | Half missing | 14 Missing rows in `docs/spec-trace.md`; 22 of 53 probes disagree with SPEC.md (I ran `uv run python docs/spec-trace/probe.py`) |
| Run a program and check its contracts on one input | Works | `src/prova/evaluator.py:100-116`; `examples/hour-clock.prova` runs (see below) |
| `verify-0` | Inventory only, nothing attempted | `docs/spec-trace.md` §5: `verify` lists the obligations a program owes, every one `not_attempted`; no encoding and no solver exist |
| `machine-0` | Not started | `docs/spec-trace.md` §7: every row Not started |
| `build`, `parse`, `format` | Advertised unavailable and refused | `src/prova/service.py:15`, probes S1-S3 |
| Resource budgets | None | `src/prova/service.py:92-95` reports `"enforced": false` |

The whole compiler is 1,661 lines of Python in 7 files (`src/prova/*.py`).

What I confirmed myself, in the working tree at `2bea72c`:

- `examples/hour-clock.prova` passes `check` with no diagnostics, all 8 of its
  declared examples pass, and `evaluate` of `step` on `(Clock 12) (Tick)` returns
  `(Outcome (Clock 1) true)`. So the hour clock is already a working `core-0`
  program.
- **No test anywhere reads `examples/hour-clock.prova`.** `grep -rln hour-clock
  tests src docs .github` returns nothing, while the same search for `Reservation`
  in `tests` returns matches. So the search did run. The file is unguarded: any
  edit to it breaks nothing.
- `conformance/add-one.prova` *is* read by tests
  (`tests/acceptance/_i1_s6_acceptance_fixtures.py:15`).
- The 14 fixtures in `evidence/cases/` are read by no test
  (`grep -rn "evidence/cases" tests src` is empty, while the same grep for
  `.prova` in `tests` returns five hits, so the search ran).

Four defects I found that `docs/spec-trace.md` does not list, each probed with one
small program through `prova.service.handle` at `2bea72c`:

| New finding | Current behaviour | SPEC.md |
|---|---|---|
| Signature markers are not checked | `(sig ((n Int)) XX Int ZZ impure)` is accepted and checks clean | lines 71-74, 100 |
| The example arrow is not checked | `(example (f 1) ZZ 1)` is accepted; the good-marker control also passes | line 106 |
| An empty program is accepted | source `""` returns `check` completed | line 92 (`program ::= declaration+`) |
| An empty `(examples)` block is accepted | a function with no example at all checks clean | lines 104, 230 |
| Duplicate type names are silently last-wins | two `(deftype T ...)` give a confusing missing-field error, not a duplicate-declaration error | line 138 |

The cause is structural, not accidental: `src/prova/checker.py:29-83` walks
declarations one at a time and checks types and scope. It has no pass that asks
whole-program questions ("is this name declared twice?", "is this graph acyclic?").
Nine of the Missing rows are that one absent pass.

Where I disagree with the trace: it marks row 9.4 ("missing upper guard, flipped
flag and always-reject bodies detected") as Done. That detection is by running
examples (`tests/acceptance/test_s4_*`). A run of three example inputs is not the
same claim as a check over all inputs. I treat 9.4 as open, as the trace's own
footnote admits.

---

## 2. The roadmap

Five increments, in order. Each one ends in a command the Owner can run in a
terminal and judge. Nothing after increment 1 is worth starting before increment 1
lands, because every later layer reads the same typed program the checker admits:
a verifier that trusts a checker which accepts recursion will loop or lie.

### Increment 1 — "A wrong program is refused, and the examples in the repo are guarded"

Finish the `core-0` front end: every rule in SPEC.md §Source and values and
§Types, scope and composition is enforced, and out-of-profile source is refused as
unsupported rather than mislabelled.

Features: F1 F2 F3 F4 F5 F6 F7 F8 F9. All READY.

Try it in a terminal:

```
uv run pytest -q tests                      # green, including the hour clock
uv run python docs/spec-trace/probe.py       # every scored probe agrees
```

Exit condition: the probe table reports every scored row agreeing with SPEC.md
(E1 stays "not observable"), and the suite proves the hour clock and the
reservation example still check, run and reproduce their tables.

### Increment 2 — "An agent can discover what the tool does, and is told exactly what failed"

Make the JSON service match SPEC.md §Agent interface: a manifest that describes
every operation and its schema, diagnostics that carry the source revision and the
symbol they are about, `parse` and `format` available, and declared budgets that
are actually enforced.

Features: F10 F11 F12 F13 (READY), F14 (needs D5), F15 (needs D7).

Try it in a terminal:

```
echo '{"operation":"discover"}' | uv run prova
echo '{"operation":"parse","source":"(deftype T (record (a Int)))"}' | uv run prova
echo '{"operation":"format","source":"(deftype    T (record (a Int)))"}' | uv run prova
```

Exit condition: `discover` lists every operation with its request and response
schema and its enforced limits; `parse` returns the tree; `format` returns
canonical text twice with the same bytes and keeps comments.

### Increment 3 — "The compiler says, obligation by obligation, what it proved and what it could not"

Deliver `verify-0` for the stated fragment. The honest inventory comes first and
needs no solver, so work can start before the solver decision.

Features: F16 F17 (READY), F18 F19 F20 F21 (need D1).

Try it in a terminal:

```
echo "{\"operation\":\"verify\",\"source\":$(uv run python -c 'import json,sys;print(json.dumps(open("examples/hour-clock.prova").read()))')}" | uv run prova
```

Exit condition: the response lists every required obligation for the hour clock
with `proved`, `disproved`, `unknown` or `not_attempted`, its claim kind, its
scope and the solver and compiler versions; a program with a deliberately false
postcondition comes back `disproved` with a replayed witness; a nonlinear
obligation comes back `unknown` with its reason.

### Increment 4 — "A verified program becomes an executable the Owner can feed fresh inputs"

Deliver `build`: it publishes an artefact only when the whole required inventory is
discharged, and the artefact decodes fresh input, checks entry preconditions and
runs.

Features: F22 F23 F24. All need D2; F23 also needs D3.

Try it in a terminal:

```
echo '{"operation":"build","source":"...","entry":"step","output":"out/clock"}' | uv run prova
out/clock '(Clock 11)' '(Tick)'        # -> (Outcome (Clock 12) true)
```

Exit condition: build refuses and writes nothing while any obligation is not
`proved`; after verification succeeds it writes one artefact; the artefact returns
the exact next hour for inputs no example used, and refuses `(Clock 13)` without
returning a value.

### Increment 5 — "The hour clock and the reservation component are checked as state machines"

Deliver `machine-0`: a descriptor naming the five roles, the three inductive
obligations, and a sequential runtime whose boundary rejection is distinguishable
from a business rejection.

Features: F25 F26 F27 F28. All need D6; F26 and F28 also need D1; F27 also needs D3.

Try it in a terminal:

```
echo '{"operation":"verify","source":"...","machine":"examples/hour-clock.machine.json"}' | uv run prova
echo '{"operation":"verify","source":"...","machine":"examples/reservation.machine.json"}' | uv run prova
```

Exit condition: both machines report initialisation, enabledness and preservation
obligations proved for their invariant; the reservation source with the upper guard
removed reports the preservation obligation `disproved`; the report never calls an
induction witness a reachable trace.

### After increment 5

The compiler is finished as SPEC.md defines `core-0`, `verify-0` and `machine-0`.
Only then do the sample programs start (Owner ruling): Pricing and Huffman, Huffman
in small slices. Tetris is removed. Recursion, Decimal, Text, collections, effects,
liveness, model-checker export and self-hosting stay deferred (SPEC.md lines
602-613).

### Rules that hold in every increment

1. A feature's checks and its code land in one change (Owner ruling). Trunk stays
   green; work is on `main` with no PRs.
2. A runtime check is never described as a proof. `evaluate` passing examples is
   evidence about those inputs only (`src/prova/service.py:86-90` already says this;
   keep it true everywhere).
3. The reservation example's semantics and its six-row table (SPEC.md lines
   515-587) do not change. Neither do its expected outcomes.
4. Every negative check gets a positive control at the same stage
   (`docs/EXPECTATIONS.md` line 57).
5. Before building a feature, run its new checks against the current commit. If a
   check passes either way, it is not an expectation yet. Every increment-1
   feature below already has a failing probe, named in its row.

---

## 3. Feature list

Size key: **S** = one sitting. **M** = one delivery with new checks and a design
choice inside it. **L** = one delivery, but the largest unit I am willing to call
one feature.

| ID | Title | Size | Status | Depends on |
|---|---|---|---|---|
| F1 | The shipped examples are guarded by the suite | S | READY | — |
| F2 | A recursive program is refused, not a crash | M | READY | — |
| F3 | A name is never declared twice | S | READY | — |
| F4 | Types cannot depend on themselves | S | READY | — |
| F5 | A binding cannot hide another, and `result` stays reserved | M | READY | — |
| F6 | Names and markers must be spelled as the language defines them | M | READY | — |
| F7 | An operator takes exactly its own arguments | S | READY | — |
| F8 | A function's examples are about that function | S | READY | — |
| F9 | Out-of-profile source is refused as unsupported, not mislabelled | M | READY | — |
| F10 | A diagnostic says which revision, which symbol, expected and actual | M | READY | F2-F9 (same type) |
| F11 | The manifest describes every operation an agent may call | M | READY | — |
| F12 | `parse` returns the program's tree under a published schema | M | READY | — |
| F13 | A report says which contracts are missing or trivial | S | READY | — |
| F14 | Operations stop inside declared budgets instead of hanging | M | BLOCKED | D5 |
| F15 | `format` returns one canonical spelling and keeps comments | L | BLOCKED | D7 |
| F16 | The tool lists every obligation it owes, honestly unattempted | M | READY | — |
| F17 | Every result says what kind of claim it is and under what scope | M | READY | — |
| F18 | Obligations in the core fragment are discharged by a solver | L | BLOCKED | D1, F16, F17 |
| F19 | An obligation outside the fragment returns unknown with its reason | M | BLOCKED | D1, F18 |
| F20 | A disproof carries a witness that replays | M | BLOCKED | D1, F18 |
| F21 | "Verified" means the whole inventory was discharged | M | BLOCKED | D1, F16, F18 |
| F22 | `build` publishes an artefact only for a fully verified program | L | BLOCKED | D2, F21 |
| F23 | The artefact answers fresh inputs and refuses invalid entry states | M | BLOCKED | D2, D3, F22 |
| F24 | A build writes only where it is allowed, and a failed build breaks nothing | M | BLOCKED | D2, F22 |
| F25 | A machine descriptor names five checked roles | M | BLOCKED | D6 |
| F26 | The three inductive invariant obligations are stated and discharged | L | BLOCKED | D1, D6, F25, F18 |
| F27 | The runtime rejects inadmissible events without changing state | M | BLOCKED | D3, D6, F25 |
| F28 | A broken guard is caught statically, and witness kinds are never confused | M | BLOCKED | D1, D6, F26 |

---

### F1 — The shipped examples are guarded by the suite

**Outcome.** The Owner runs one command and sees that the hour clock and the
reservation example in this repository still check, run every declared example and
reproduce their transition tables. An edit that breaks one of them fails the suite.

**Acceptance criteria**

1. Given `examples/hour-clock.prova` as shipped, when the suite runs, then `check`
   completes with no diagnostics and all eight declared examples pass.
2. Given the clock at hour 12, when `step` is run with a tick, then the outcome is
   hour 1 and accepted.
3. Given hours 1 to 12 in turn, when `step` is run with a tick, then the next hour
   is 2..12 then 1, and each outcome is accepted.
4. Given a copy of the clock source with the wrap at 12 removed, when the suite
   runs that copy, then it reports a failure (the original file is not edited).
5. Given the example file is missing or renamed, when the suite runs, then it fails
   with a missing-file error and does not skip.

**SPEC.md** lines 228-239 (examples), 580-587 (use the real compiler for these
checks), 372-382 (the clock is the smaller machine target).
**Dependencies** none. **Size** S: tests only, no production change.
**Touches** `tests/acceptance/` (new file), `tests/properties/` fixtures. No
`src/` change.
**Why it is a real expectation** no test reads this file today (section 1).

### F2 — A recursive program is refused, not a crash

**Outcome.** A program whose calls form a cycle is refused when it is checked,
with the cycle named. The tool never dies with a Python traceback.

**Acceptance criteria**

1. Given a function whose body calls itself, when the program is checked, then the
   program is invalid and the diagnostic names the function in the cycle.
2. Given two functions that call each other, when the program is checked, then the
   program is invalid and the diagnostic names both.
3. Given a cycle that runs only through a contract clause, when the program is
   checked, then the program is invalid.
4. Given any of those programs, when a function is evaluated, then the answer is a
   structured refusal in valid JSON and the process exits normally.
5. Given a function whose examples call that function, when the program is checked,
   then it is accepted (those self-calls are not a cycle).
6. Given the hour clock and the reservation example, when they are checked, then
   both still pass.

**SPEC.md** lines 163-168 (acyclic body and contract graph), 186-189 (termination
follows from acyclicity), 322-325.
**Dependencies** none. **Size** M: needs a whole-program call graph over bodies and
contracts with the examples edge excluded.
**Touches** `src/prova/checker.py`, one new diagnostic category in
`src/prova/service.py:17-33`, tests.
**Why it is a real expectation** probes T17, T18, T19 all disagree today;
`docs/spec-trace.md` defect 1 records the uncaught `RecursionError`.

### F3 — A name is never declared twice

**Outcome.** A program that declares the same function, type, constructor or field
twice is refused, instead of silently keeping the last one.

**Acceptance criteria**

1. Given two functions with the same name, when the program is checked, then it is
   invalid and the diagnostic names the function and both places it was declared.
2. Given two types with the same name, likewise.
3. Given the same constructor name introduced by two different types, likewise.
4. Given a record or a variant with the same field name twice, likewise.
5. Given a program that redeclares `Int`, `Bool` or `Unit`, then it is invalid.
6. Given two different records that each have a field spelled `amount`, when the
   program is checked, then it is accepted.

**SPEC.md** lines 137-143. **Dependencies** none (same file as F4, F5, F7, F8).
**Size** S: one pass over the declaration tables.
**Touches** `src/prova/checker.py`, `src/prova/service.py` categories, tests.
**Why it is a real expectation** probes T3, T4, T5, T6 disagree today, plus my
duplicate-type-name finding in section 1.

### F4 — Types cannot depend on themselves

**Outcome.** A record or union whose fields lead back to itself is refused, because
recursive data belongs to a later profile.

**Acceptance criteria**

1. Given a record with a field of its own type, when the program is checked, then
   it is invalid and the diagnostic names the cycle.
2. Given two records that each hold the other, likewise.
3. Given a union whose variant payload closes a cycle, likewise.
4. Given three types in a chain with no cycle, when the program is checked, then it
   is accepted.
5. Given the refusal, then it says recursive data is outside this profile, not that
   a type is unknown.

**SPEC.md** lines 135-136, 51-54 (unsupported must not be misdiagnosed).
**Dependencies** none (serial with F3, F5, F7, F8). **Size** S.
**Touches** `src/prova/checker.py`, tests.
**Why it is a real expectation** probe T2 disagrees today.

### F5 — A binding cannot hide another, and `result` stays reserved

**Outcome.** A `let` or pattern variable that would hide a parameter, a function or
a builtin is refused, and `result` can only be read in a postcondition.

**Acceptance criteria**

1. Given a `let` that binds a name already bound as a parameter, when the program
   is checked, then it is invalid and the diagnostic names the hidden binding.
2. Given a pattern variable that hides a declared function name, likewise.
3. Given any binder named `result`, when the program is checked, then it is invalid.
4. Given `result` read in a body or in a precondition, then it is invalid.
5. Given a pattern that binds the same name twice, then it is invalid.
6. Given the same variable name used in two different match clauses of one
   expression, when the program is checked, then it is accepted.

**SPEC.md** lines 145-149, 156-161 (a pattern variable binds once).
**Dependencies** none (serial with F3, F4, F7, F8). **Size** M: three related rules
and the scope bookkeeping they share.
**Touches** `src/prova/checker.py`, tests.
**Why it is a real expectation** probes T8, T10, T16 disagree today.

### F6 — Names and markers must be spelled as the language defines them

**Outcome.** Source that uses a reserved word as a name, an upper-case function
name, or a mangled `->` / `!` / `=>` marker is refused at the place it appears.

**Acceptance criteria**

1. Given a function named `let`, `if`, `match` or any other reserved word, when the
   program is checked, then it is invalid and the diagnostic names the reserved word.
2. Given a function or parameter whose name starts with a capital, then it is
   invalid; given a type name that starts lower-case, then it is invalid.
3. Given a signature whose arrow or effect marker is anything other than `->` and
   `! pure`, then it is invalid.
4. Given an example whose arrow is not `=>`, then it is invalid.
5. Given a source with no declarations at all, then it is invalid.
6. Given a function with an empty `(examples)` block, then it is invalid.
7. Given the hour clock and the reservation example, then both still check.

**SPEC.md** lines 65-74 (name shape, reserved words, marker tokens), 92, 99-106.
**Dependencies** none, but it shares `src/prova/syntax.py` with F9. **Size** M:
touches the reader-to-tree boundary where diagnostics currently lose their position.
**Touches** `src/prova/syntax.py`, `src/prova/checker.py`, tests.
**Why it is a real expectation** probes L3, L4 disagree, plus the three marker and
empty-block findings in section 1.

### F7 — An operator takes exactly its own arguments

**Outcome.** A builtin operator applied to the wrong number of arguments is
refused, rather than quietly ignoring the extras.

**Acceptance criteria**

1. Given `not` with two arguments, when the program is checked, then it is invalid
   and the diagnostic gives the expected and the actual count.
2. Given `+` with one argument or three, likewise.
3. Given each comparison, equality and boolean operator with a wrong count,
   likewise.
4. Given every operator applied correctly, when the program is checked, then it is
   accepted.

**SPEC.md** lines 178-189 (the operator table and "no variable arity").
**Dependencies** none (serial with F3, F4, F5, F8). **Size** S: one arity table.
**Touches** `src/prova/checker.py`, tests.
**Why it is a real expectation** probe E5 disagrees today.

### F8 — A function's examples are about that function

**Outcome.** An example that calls some other function no longer counts as that
function's example.

**Acceptance criteria**

1. Given a function whose only example calls a different function, when the program
   is checked, then it is invalid and the diagnostic names both functions.
2. Given an example calling a function that does not exist, then it is invalid.
3. Given an example whose argument count does not match the function, then it is
   invalid at check time, not only when examples run.
4. Given a function with one correct self-calling example, then it is accepted.

**SPEC.md** lines 228-234. **Dependencies** none (serial with F3, F4, F5, F7).
**Size** S. **Touches** `src/prova/checker.py`, tests.
**Why it is a real expectation** probe C3 disagrees today.

### F9 — Out-of-profile source is refused as unsupported, not mislabelled

**Outcome.** Source using something `core-0` does not have — division, a decimal
literal, text, `fn`, `defspec`, `trust`, `module`, a trailing top-level expression —
is refused with a message that says it is outside this profile.

**Acceptance criteria**

1. Given a program using division, when it is checked, then it is refused and the
   diagnostic says the construct is unsupported in this profile and names it.
2. Given a decimal or text literal, then the refusal says unsupported, not that a
   name is unbound.
3. Given a trailing top-level expression, then the refusal says unsupported, not a
   generic syntax error.
4. Given each of the fourteen fixtures in `evidence/cases/`, when each is checked,
   then the ones meant to be refused are refused and the ones meant to pass pass.
5. Given an unsupported refusal, then nothing in the response claims the program's
   deeper meaning was checked.

**SPEC.md** lines 51-54, 79-80, 125-128, 191-196, 472-474 (the three kinds of
failure are distinct).
**Dependencies** none, but shares `src/prova/syntax.py` with F6. **Size** M: needs a
separate "unsupported" status alongside `invalid_program`.
**Touches** `src/prova/syntax.py`, `src/prova/service.py`, `evidence/cases/` wired
into tests, tests.
**Why it is a real expectation** probes G4, L5 disagree; no test reads
`evidence/cases/` today (section 1).

### F10 — A diagnostic says which revision, which symbol, expected and actual

**Outcome.** A client can act on a failure without reading prose: which source
revision, which function or obligation, what was expected, what was found, and
where.

**Acceptance criteria**

1. Given any invalid program, when it is checked, then every diagnostic carries the
   source revision the answer is about.
2. Given a type error, then the diagnostic names the symbol it is about and gives
   the expected and the actual type as separate fields.
3. Given a syntax error from the reader, then the diagnostic still carries a
   position.
4. Given the same failure with reworded prose, then the category and the fields are
   unchanged.
5. Given a repaired program, when it is checked again, then it is accepted and the
   revision in the answer is the new one.

**SPEC.md** lines 472-482, 270-278 (provenance).
**Dependencies** F2-F9: it changes the diagnostic type those features add rows to,
so doing it first means redoing it. **Size** M.
**Touches** `src/prova/checker.py` (the diagnostic type), `src/prova/service.py`,
tests.
**Why it is a real expectation** probes S4, S6 disagree; probe S5 shows location is
only partly present.

### F11 — The manifest describes every operation an agent may call

**Outcome.** `discover` is enough to use the tool: every operation, whether it is
available, its request and response shape, the diagnostic schema, the profile
coverage and the limits.

**Acceptance criteria**

1. Given `discover`, when it runs, then every operation named in SPEC.md's initial
   categories appears with available or unavailable.
2. Given `discover`, then each available operation carries its request and its
   response schema.
3. Given `discover`, then each builtin type and operator appears with its argument
   and result types.
4. Given an operation advertised as available, when it is called with a request
   matching the published schema, then it answers; when it is called with a request
   that violates the schema, then it is refused as invalid input.
5. Given an operation the tool runs that SPEC.md does not name as a profile
   operation, then the manifest says so rather than presenting it as profile
   conformance.

**SPEC.md** lines 463-470, 476-478. **Dependencies** none. **Size** M.
**Touches** `src/prova/service.py`, tests, new schema fixtures.
**Why it is a real expectation** `docs/spec-trace.md` rows 8.2 and 8.3 are Partial;
3 of 7 categories exist and `evaluate` is not one of SPEC.md's named categories
(see proposal P1).

### F12 — `parse` returns the program's tree under a published schema

**Outcome.** An agent can read the tree the compiler actually built, instead of
guessing from source text.

**Acceptance criteria**

1. Given a valid program, when `parse` runs, then the answer is a tree matching the
   published schema, with a position on every node.
2. Given a program with a comment, then the comment appears attached to the node
   that follows it, or to the document end.
3. Given an invalid program, then `parse` refuses with the same diagnostic
   categories `check` would use and publishes no tree.
4. Given the tree for the reservation example, then every declaration, contract
   clause and example in the source appears in it.
5. Given `discover`, then `parse` is advertised available with that schema.

**SPEC.md** lines 81-84 (the tree schema must be fixed in fixtures), 463-470.
**Dependencies** none; the schema choice is D7 if the Owner wants to approve it.
**Size** M. **Touches** `src/prova/service.py`, `src/prova/syntax.py`,
`conformance/` fixtures, tests.
**Why it is a real expectation** `parse` is refused today
(`src/prova/service.py:15`, probe S2).

### F13 — A report says which contracts are missing or trivial

**Outcome.** The Owner can see at a glance which functions promise nothing, so a
clean result is not mistaken for a meaningful one.

**Acceptance criteria**

1. Given a function with no `requires`, when the program is checked, then the
   report records that precondition as omitted.
2. Given a function whose `ensures` is literally `true`, then the report records it
   as trivial.
3. Given a function with a real contract, then it is recorded as neither.
4. Given a program where every contract is omitted or trivial, then nothing in the
   answer describes the program as meaningfully correct.

**SPEC.md** lines 204-206. **Dependencies** none. **Size** S.
**Touches** `src/prova/service.py`, `src/prova/checker.py`, tests.
**Why it is a real expectation** probe C8 disagrees today.

### F14 — Operations stop inside declared budgets instead of hanging

**Outcome.** Every operation declares an input, time, memory and output budget, and
exceeding one gives a clean diagnostic instead of a hang or a crash.

**Acceptance criteria**

1. Given `discover`, when it runs, then each operation's input, time, memory and
   output budgets are stated and marked enforced.
2. Given a source larger than the input budget, then the operation is refused for
   exhausting that budget and names which one.
3. Given work that exceeds the time budget, then the answer is a budget diagnostic,
   not a partial result and not a hang.
4. Given a budget refusal, then nothing in the answer claims a semantic result, and
   the program's mathematical domain is not described as bounded.
5. Given a program well inside every budget, then it completes normally.

**SPEC.md** lines 503-508, 280-284. **Dependencies** D5. **Size** M.
**Touches** `src/prova/service.py`, `src/prova/__main__.py`, tests.
**Why it is a real expectation** probe S7 shows `enforced: false`.

### F15 — `format` returns one canonical spelling and keeps comments

**Outcome.** The Owner can run `format` on any accepted source and get the same
canonical text every time, with comments intact.

**Acceptance criteria**

1. Given any accepted program, when `format` runs, then it returns canonical text;
   when `format` runs on that output, then the bytes are identical.
2. Given a program with comments, then every comment appears once, in order,
   attached to the following declaration, or at the end.
3. Given non-canonical integer spellings such as `+002`, then the output is
   canonical and the program's meaning is unchanged.
4. Given formatted output, when it is checked and its examples run, then the
   results equal those of the original source.
5. Given an invalid program, then `format` refuses and returns no text.

**SPEC.md** lines 60-63, 81-84. **Dependencies** D7. **Size** L: a layout policy
plus the fixtures SPEC.md requires before shipping it.
**Touches** new formatter area, `src/prova/service.py`, `conformance/` fixtures,
tests.
**Why it is a real expectation** `format` is refused today
(`src/prova/service.py:15`).

### F16 — The tool lists every obligation it owes, honestly unattempted

**Outcome.** `verify` answers with the complete list of what would have to be
proved for a program, every entry marked `not_attempted`. The Owner can see the
size and shape of the job before any solver exists.

**Acceptance criteria**

1. Given the hour clock, when `verify` runs, then the answer lists one obligation
   for each potentially evaluated call's precondition, under the condition that
   reaches it.
2. Given the hour clock, then the answer lists one obligation per function
   connecting body to postcondition, plus separate entries for example validity,
   contract definedness and structural termination.
3. Given a program with an unreachable branch, then the obligation for that branch
   still appears.
4. Given every obligation in the answer, then its result is `not_attempted` and
   nothing in the answer says verified or proved.
5. Given the reservation example, then its inventory matches the obligations
   SPEC.md names for it, with no missing function.
6. Given two runs on the same source, then the inventory and the obligation
   identities are identical.

**SPEC.md** lines 243-250, 270-284, 286-290. **Dependencies** none — this is the
largest piece of `verify-0` that needs no solver. **Size** M.
**Touches** new `src/prova/obligations.py`, `src/prova/service.py`, tests.
**Why it is a real expectation** `verify` is refused today; `docs/spec-trace.md`
rows 5.1, 5.2, 5.8 are Not started.

### F17 — Every result says what kind of claim it is and under what scope

**Outcome.** Any answer the tool gives carries its claim kind, its scope and the
versions behind it, so evidence of one kind is never read as evidence of another.

**Acceptance criteria**

1. Given any completed operation, when it answers, then the answer states the claim
   kind, the scope and the source and dependency digests.
2. Given any completed operation, then it states the compiler, encoding, solver and
   runtime versions it used, or says which are not applicable.
3. Given an examples run, then the claim kind is examples and the scope is the
   declared examples only.
4. Given a verify answer, then each obligation's logical result and its execution
   status are separate fields.
5. Given a tool failure, then the answer is a tool failure, not a semantic result.
6. Given a result from an earlier revision, when the source has changed, then the
   answer does not present that result as current.

**SPEC.md** lines 270-284, 476-482. **Dependencies** none, but it is cheapest
together with F16. **Size** M.
**Touches** `src/prova/service.py`, tests.
**Why it is a real expectation** probe S8 shows only `source_digest` is present.

### F18 — Obligations in the core fragment are discharged by a solver

**Outcome.** The Owner runs `verify` on the hour clock and the reservation example
and sees each in-fragment obligation come back `proved`, with the translation
written down.

**Acceptance criteria**

1. Given the hour clock, when `verify` runs, then every in-fragment obligation is
   `proved` and nothing is silently skipped.
2. Given the reservation example, likewise, including the step precondition.
3. Given a program with a postcondition that is false for some typed input, then
   that obligation is not `proved`.
4. Given a conditional or a match, then the obligation keeps the path condition
   that reaches it.
5. Given the answer, then it names the solver and its version, and discloses that
   its validity result is trusted.
6. Given the delivered change, then it includes the document stating what each
   emitted logical primitive means and why discharging an obligation establishes
   the source claim.

**SPEC.md** lines 251-268, 302-305. **Dependencies** D1, F16, F17. **Size** L: the
encoder is the single biggest unit of work in this roadmap, and SPEC.md lines
264-265 require its written justification in the same delivery.
**Touches** new encoder and solver-adapter area, `src/prova/service.py`, new
dependency, tests, new document under `docs/`.

### F19 — An obligation outside the fragment returns unknown with its reason

**Outcome.** Reasoning the tool cannot do is reported as unknown with the reason,
never as success and never translated unsoundly.

**Acceptance criteria**

1. Given an obligation needing the product of two unknown integers, when `verify`
   runs, then it is `unknown` and the reason says the fragment does not cover it.
2. Given a controlled solver timeout, then the obligation is `unknown` with a
   timed-out execution status, not `disproved`.
3. Given a solver that fails to run, then the answer is a tool failure and the
   program is not accepted.
4. Given a mix of in-fragment and out-of-fragment obligations, then the aggregate
   is not verified, and the in-fragment results stay visible.
5. Given an obligation that uses multiplication by a literal constant, then it is
   inside the fragment and gets a real result.

**SPEC.md** lines 251-256, 280-284. **Dependencies** D1, F18. **Size** M.
**Touches** encoder area, `src/prova/service.py`, tests.

### F20 — A disproof carries a witness that replays

**Outcome.** When the tool says a claim is false, it shows concrete inputs, and it
has run them through its own evaluator to confirm.

**Acceptance criteria**

1. Given a function whose postcondition fails for some input, when `verify` runs,
   then the answer is `disproved` with concrete argument values.
2. Given that witness, when the tool replays it, then the precondition holds and
   the postcondition fails.
3. Given a candidate witness that does not replay, then the answer is `unknown`,
   not `disproved`.
4. Given a witness, then the replay happened inside a declared budget and the
   budget is stated.
5. Given the reservation example unmodified, then no witness is produced.

**SPEC.md** lines 295-300. **Dependencies** D1, F18. **Size** M.
**Touches** encoder area, `src/prova/evaluator.py` (reuse for replay), tests.

### F21 — "Verified" means the whole inventory was discharged

**Outcome.** The word verified appears only when every required obligation for the
selected profile is discharged, all examples pass and all static checks pass.

**Acceptance criteria**

1. Given a program whose inventory is fully discharged with passing examples, when
   `verify` runs, then the aggregate is verified and the inventory is in the answer.
2. Given one obligation `unknown`, then the aggregate is not verified.
3. Given one failing example, then the aggregate is not verified even if every
   obligation is `proved`.
4. Given an unsupported function anywhere in the program, then it does not remove
   obligations for the rest.
5. Given the inventory, then structurally discharged checks are distinguishable
   from solver-discharged ones.

**SPEC.md** lines 286-293. **Dependencies** D1, F16, F17, F18. **Size** M.
**Touches** `src/prova/service.py`, obligation area, tests.

### F22 — `build` publishes an artefact only for a fully verified program

**Outcome.** The Owner runs `build` and either gets one executable artefact, or a
refusal and no file.

**Acceptance criteria**

1. Given a program with any obligation not discharged, when `build` runs, then it
   refuses and writes nothing.
2. Given a fully verified program and an entry function, then `build` writes one
   artefact and records which entry and which configuration it used.
3. Given the artefact, then its recorded source revision equals the verified one.
4. Given a changed source, when the old artefact is inspected, then its evidence
   does not certify the new source.
5. Given the artefact, then nothing in it replaces the program with precomputed
   example answers.

**SPEC.md** lines 286-293, 484-496. **Dependencies** D2, F21. **Size** L: a backend
and an artefact format, even a minimal one.
**Touches** new build area, `src/prova/service.py`, tests.
**Why it is a real expectation** `build` is refused today only because it is
unavailable (probe S3); the fail-closed rule has never been tested against a build
that could have succeeded.

### F23 — The artefact answers fresh inputs and refuses invalid entry states

**Outcome.** The Owner runs the built artefact on inputs no example used and gets
the right answer, with big integers intact and bad inputs refused.

**Acceptance criteria**

1. Given the built clock, when it is run on an hour no example used, then the next
   hour is correct and the outcome is accepted.
2. Given the built reservation component, when it is run through all six table
   rows on fresh input, then every state and acceptance flag matches the table.
3. Given an input outside the entry precondition, then the artefact refuses and
   returns no result value.
4. Given a malformed value, then the refusal distinguishes malformed from
   well-formed-but-wrong-type.
5. Given an integer beyond 64-bit range, when it goes in and comes back, then it is
   exact.
6. Given a contract failure inside the artefact, then it is reported as an
   assurance failure, not as an ordinary rejection or a success.

**SPEC.md** lines 484-501, 515-587. **Dependencies** D2, D3, F22. **Size** M.
**Touches** build area, runtime adapter, tests.

### F24 — A build writes only where it is allowed, and a failed build breaks nothing

**Outcome.** A build cannot write outside its authorised destination, and a failure
leaves whatever was there before untouched.

**Acceptance criteria**

1. Given an output path that escapes the authorised destination through `..`, when
   `build` runs, then it refuses before writing anything.
2. Given a symlink pointing outside the destination, likewise.
3. Given an existing artefact and a build that then fails, when the build returns,
   then the existing artefact is byte-identical to before.
4. Given a replacement that was explicitly authorised, then the old artefact is
   replaced and the answer says so.
5. Given a refusal, then it names the authority rule, not just "error".

**SPEC.md** lines 510-513. **Dependencies** D2, F22. **Size** M.
**Touches** build area, tests.
**Why it is a real expectation** `docs/spec-trace.md` row 8.13 is Partial: a refused
build writes nothing only because there is no build.

### F25 — A machine descriptor names five checked roles

**Outcome.** The Owner can hand the tool a descriptor for the hour clock or the
reservation component and have it confirm that the five roles resolve to checked
functions of the right shapes.

**Acceptance criteria**

1. Given a descriptor naming initialiser, step, projection, admissibility and
   invariant functions that exist and have the required shapes, when it is checked,
   then it is accepted.
2. Given a descriptor naming a function that does not exist, or one with the wrong
   argument or result types, then it is refused and the diagnostic names the role.
3. Given a descriptor whose initialiser, projection, invariant or admissibility
   function has a precondition that is not valid for every input of its type, then
   it is refused.
4. Given the descriptor, then its schema version is recorded in the answer.
5. Given a descriptor, then it adds no new language syntax: the source it refers to
   is ordinary `core-0`.
6. Given descriptors for the hour clock and the reservation component, then both
   are accepted.

**SPEC.md** lines 348-370. **Dependencies** D6. **Size** M.
**Touches** new machine area, `src/prova/service.py`, new descriptor files under
`examples/`, tests.

### F26 — The three inductive invariant obligations are stated and discharged

**Outcome.** The Owner sees the initialisation, enabledness and preservation
obligations listed and proved for both machines.

**Acceptance criteria**

1. Given an accepted descriptor, when `verify` runs, then the answer lists exactly
   the initialisation, step-enabledness and preservation obligations, each
   separately.
2. Given the hour clock, then all three are `proved` for its invariant.
3. Given the reservation component, likewise.
4. Given an unbounded event type, then the obligations range over typed events
   symbolically and the answer does not claim an enumeration.
5. Given an invariant that is not inductive on its own, then preservation is not
   `proved`, and no weaker safety predicate is substituted.
6. Given an initial condition that is unsatisfiable, then the machine is not
   certified.

**SPEC.md** lines 372-418. **Dependencies** D1, D6, F25, F18. **Size** L: the
machine obligations plus their encoding over typed events.
**Touches** machine area, encoder area, tests.

### F27 — The runtime rejects inadmissible events without changing state

**Outcome.** The Owner can drive a machine event by event in a terminal, and see a
boundary rejection as something different from a business rejection.

**Acceptance criteria**

1. Given a machine at a valid state, when an admissible event arrives, then the new
   state and the outcome are published together.
2. Given an event outside the admissible domain, then the answer is a boundary
   rejection and the state is unchanged.
3. Given an admissible event whose business result is a rejection, then the answer
   is distinguishable from case 2.
4. Given a sequence of events, then each transition uses the state the previous one
   published, in order.
5. Given malformed event data, then it is refused before any transition.
6. Given any answer, then nothing claims host atomicity or delivery guarantees.

**SPEC.md** lines 404-418. **Dependencies** D3, D6, F25. **Size** M.
**Touches** machine runtime area, `src/prova/service.py`, tests.

### F28 — A broken guard is caught statically, and witness kinds are never confused

**Outcome.** The deliberate faults in SPEC.md's conformance section are caught by
proof, not just by running examples, and an induction witness is never labelled a
reachable run.

**Acceptance criteria**

1. Given the reservation source with the upper capacity guard removed, when
   `verify` runs with its descriptor, then preservation is `disproved`, even though
   no example visits a full state.
2. Given the source with the acceptance flag flipped, then an obligation is
   `disproved` while the invariant still holds.
3. Given an always-reject body, then an obligation about acceptance is `disproved`;
   safety alone does not make it pass.
4. Given a disproof of preservation, then the answer calls it an induction-step
   witness and does not call it a reachable trace.
5. Given a validated initial state and a sequence of transitions, then that, and
   only that, is called a reachable counterexample.
6. Given an attempt to pass by weakening a contract, strengthening a precondition
   or deleting an example, then the answer reports a requirement change, not an
   implementation repair.

**SPEC.md** lines 295-300, 307-318, 580-587; `docs/EXPECTATIONS.md` E9, E10.
**Dependencies** D1, D6, F26. **Size** M.
**Touches** machine area, obligation area, tests, mutation fixtures.
**Why it is a real expectation** today these three faults are caught only by
running examples (`tests/acceptance/test_s4_b1..b3`), which is a claim about three
inputs.

---

## 4. What can run in parallel

**Honest answer: very little, and that is a property of the codebase, not of the
plan.** `src/prova/service.py:36-70` is the only place that knows operation names
(its own docstring says so, lines 1-4), and `src/prova/checker.py` holds every
static rule. Nine of the increment-1 features add rules to that one file.

| Group | Features | Safe together? |
|---|---|---|
| A | F1 | Yes, with anything. Tests only, no `src/` change. |
| B | F3, F4, F5, F7, F8 | Logically independent of each other in any order, but all edit `src/prova/checker.py`. Deliver one at a time. |
| C | F6, F9 | Both edit `src/prova/syntax.py`. Deliver one at a time, and not at the same time as each other. |
| D | F2 | Alone: it adds a graph pass and a category, and F10 then rewrites the diagnostic shape. |
| E | F16, F17 | New files plus one dispatch entry. Safe alongside any one of group B. |
| F | F11, F12, F13 | All edit `src/prova/service.py`. One at a time. |

Safe parallel pairs I would actually run, two lanes at most (the project's WIP
limit is 2):

- **F1 + any one other feature.** Fully independent.
- **one of (F3, F4, F5, F7, F8) + one of (F16, F17).** Different files; only the
  manifest's operation list is shared, and F16's entry is one line.
- **F12 + F4.** Service file versus checker file.

Must wait, and why:

| Feature | Waits for | Reason |
|---|---|---|
| F10 | F2-F9 | It changes the diagnostic type those features add to. Doing it first means doing it twice. |
| F14 | D5 | Numbers must come from the Owner or from a measurement the Owner accepts. |
| F15 | D7 | SPEC.md lines 81-84 require the canonical layout fixed in fixtures first. |
| F18-F21 | D1 | No solver, no discharge. F16 and F17 do not wait. |
| F22-F24 | D2, F21 | SPEC.md lines 286-293: a standard build must fail closed until verification is complete, so there is nothing to publish before F21. |
| F25-F28 | D6 | SPEC.md line 356 requires the descriptor's versioned schema fixed before machine operations ship. |

---

## 5. Owner decisions

I need six answers. Four of them block nothing in increments 1 and 2, so please do
not hold those up: **F1 to F13 and F16 to F17 are READY and need none of these.**

### D1 — Which solver, and what do we trust it for?

**Context.** `verify-0` needs quantifier-free Boolean reasoning, linear integer
arithmetic and non-recursive algebraic data (SPEC.md lines 251-256). SPEC.md lines
302-305 allow the first implementation to trust a chosen solver's validity result,
as long as it discloses that trust, and forbid claiming extra assurance because two
solvers agree. `docs/EXPECTATIONS.md` lines 104-107 record that a hand-written
model of the reservation example was checked with Z3 5.0.0 during specification
authoring. That was a manual model, not a compiler translation.

**My recommendation: Z3, one pinned version, through its Python package, with the
trust disclosed in every answer.** It already matched the reservation model once,
it covers the whole stated fragment, and it keeps increment 3 to one new dependency.

| Option | Consequence |
|---|---|
| Z3, pinned (recommended) | Fastest to a real `verify` answer. One more dependency in the trusted base. Version drift must be pinned and recorded. |
| CVC5 instead | Comparable power. No existing result in this repository to compare against, so increment 3 starts colder. |
| Both, must agree | Doubles run time and still gives no extra assurance; SPEC.md line 304 explicitly refuses that claim. |
| Write our own decision procedure | Smallest trusted base, by far the slowest path; months before the hour clock is proved. |

**Blocks** F18, F19, F20, F21, F26, F28.

### D2 — What does `build` produce, and on what backend?

**Context.** SPEC.md lines 484-496 require building once, running fresh inputs,
invoking a named entry function from build metadata, and treating an internal
contract failure as an assurance failure. It does not name a target.

**My recommendation: generate one self-contained Python module plus a small JSON
metadata file, run by the same pinned interpreter the compiler uses.** It is the
shortest honest path to an artefact the Owner can run, and it keeps integer
semantics exact for free.

| Option | Consequence |
|---|---|
| Generate Python (recommended) | Working executable in one increment. Performance is irrelevant for the clock and the reservation component. The backend joins the trusted base. |
| Generate C or Rust | Real native output, but arbitrary-precision integers need a big-integer library and its own evidence; adds weeks. |
| Interpret the checked tree and call that the artefact | Least work, but SPEC.md lines 491-492 ask for build-once then run; an interpreter re-reads source every run, which blurs the boundary the spec draws. |
| No `build` at all for now | Increments 4 and 5's runtime disappear; `machine-0` could still be proved but never run. |

**Blocks** F22, F23, F24.

### D3 — How do values travel in and out at run time?

**Context.** SPEC.md lines 498-501 require arbitrary-precision integers preserved,
nominal types, constructors and fields distinguished, and forbid JSON numbers
through binary floating point. Today values go in as s-expression text in a JSON
string (`src/prova/service.py:233`) and come back as s-expression text
(`src/prova/service.py:302`, `src/prova/values.py:44-55`). That already preserves
big integers; the existing tests cover it (`tests/acceptance/test_s6_*`).

**My recommendation: keep the s-expression text form as the one canonical wire
form, and add nothing.** It is already tested, already exact, and already
distinguishes constructors.

| Option | Consequence |
|---|---|
| Keep s-expression text (recommended) | No migration, no new tests for integer exactness. Clients must parse a small value syntax. |
| Structured JSON objects per value | Easier for a generic client. Integers must become strings or risk floating point; every existing value test changes. |
| Both forms | Two code paths and two sets of fixtures to keep honest. |

**Blocks** F23, F27.

### D4 — Which language do we build the compiler in?

**Context.** The working compiler is Python 3.12 (`pyproject.toml`, 1,661 lines in
`src/prova/`), CI pins 3.12 (`.github/workflows/ci.yml`), 772 tests pass. SPEC.md
lines 636-640 list the bootstrap language as a decision still required; SPEC.md
line 611 puts self-hosting out of scope.

**My recommendation: stay on Python 3.12 until all three profiles are finished,
then reconsider.** Changing now throws away a working front end and a suite that
already encodes the semantics.

| Option | Consequence |
|---|---|
| Stay on Python 3.12 (recommended) | Keeps everything. Python is in the trusted base and must be disclosed. |
| Rewrite in a typed functional language | Better fit for the subject, and the trusted base becomes easier to argue about. Costs the whole front end and the 772 tests; every feature here restarts. |
| Rewrite in Prova itself | Impossible in these profiles: no recursion, no collections, no effects. |

**Blocks** nothing if the answer is "stay". If the answer is "rewrite", it blocks
everything in this roadmap.

### D5 — What are the resource budgets?

**Context.** SPEC.md lines 505-508 require declared input, time, memory and output
budgets with controlled failure, observable and part of the evidence, and they must
not become semantic bounds. The tool declares none (`src/prova/service.py:92-95`).
The full suite takes 65 s on my machine; one `prova` call in the test client has a
10 s timeout (`tests/properties/_prova_client.py:28`).

**My recommendation: declare 1 MiB source, 10 s wall clock and 512 MiB memory per
operation, and 1 MiB per response, then measure on CI before fixing the numbers.**
These are large enough for anything in these profiles and small enough to fail
fast.

| Option | Consequence |
|---|---|
| The numbers above, measured on CI first (recommended) | F14 can be delivered immediately after the measurement. Numbers may need one revision. |
| Per-operation budgets, with a longer one for `verify` | More honest once a solver exists. Needs D1 answered first, so F14 waits for increment 3. |
| Declare budgets but do not enforce them | Exactly today's state; SPEC.md line 505 says enforced. |

**Blocks** F14. Also sets the replay budget F20 needs.

### D6 — What does a machine descriptor look like?

**Context.** SPEC.md lines 350-356 require a descriptor identifying the state,
event and outcome types, the five role functions, runtime assumptions and a
versioned transport schema fixed before machine operations ship. SPEC.md line 350
says `machine-0` adds no new temporal syntax.

**My recommendation: a separate small JSON document per machine, versioned, holding
the role-to-function names, the type names and the stated assumptions, with one
descriptor each for the hour clock and the reservation component shipped as
fixtures.** Keeping it outside the `.prova` source honours "no new syntax" and lets
the schema version independently.

| Option | Consequence |
|---|---|
| Separate versioned JSON document (recommended) | No language change; descriptors are easy to version and to diff. One more file per machine. |
| A new `defmachine` form in the source | One file per machine, but it changes the grammar, which SPEC.md lines 91-118 fix for `core-0`. That is a specification change, not an implementation choice. |
| Infer the roles from function names | No schema to maintain; silently wrong when a program has two plausible step functions, and nothing to version. |

**Blocks** F25, F26, F27, F28.

### D7 — Canonical layout and tree schema: do you want to approve it?

**Context.** SPEC.md lines 81-84 require the canonical layout and the syntax-tree
interchange schema fixed in conformance fixtures before `format` ships, and say
formatting policy must not change language validity.

**My recommendation: delegate both to me.** I will choose a layout, publish the
fixtures in the same change, and record the reasoning. These are presentation
choices with no semantic effect.

| Option | Consequence |
|---|---|
| Delegate (recommended) | F15 and F12 proceed. You review the fixtures afterwards if you want. |
| You approve the layout first | F15 waits for you. F12 can still proceed with the tree schema alone. |

**Blocks** F15 only if you want to approve it. F12 does not wait either way.

---

## 6. Risks

| Risk | Why it matters | What I would do |
|---|---|---|
| Increment 1 breaks existing tests | Nine new refusals land in a suite of 772 tests whose fixtures were written when those programs were accepted. Some fixtures may use a shadowed `let` or an upper-case name incidentally. | Each feature's change may have to repair fixtures. Repairing a fixture is allowed; changing an expected *outcome* is a requirement change (SPEC.md lines 307-318) and must be disclosed. |
| The 772 tests are named after a dropped framework | `tests/*/test_i1_s*` names mean nothing now. Reading them costs time, and a reader may think I1 is live. | Leave the names. Note it once, here. Rename nothing. |
| The trace's row counts are one reader's split | `docs/spec-trace.md` lines 6-8 say so itself. "40% done" is not a measurement. | Plan from the Missing and Not-started *rows*, which I re-probed, not from the percentage. |
| `verify-0` may not prove the hour clock's wrap | The clock's postcondition uses `if` inside an equality over `Int`. I did not confirm that this is inside the stated fragment after expansion. | F16 lands first and prints the obligations; that tells us before the solver work starts. |
| The encoder is the one L feature with no fallback | If the translation turns out unsound or out of reach, increments 4 and 5 both stall. | F16 and F17 deliver real value with no solver. If F18 stalls, the tool still reports a complete honest inventory. |
| Budget numbers chosen without measurement become semantic bounds | SPEC.md lines 506-508 forbid exactly that. | Measure on CI before D5 is fixed; state the limits in every answer. |
| Adding solver time to the suite | The suite already takes 65 s and dies at Go-style default timeouts elsewhere in my experience; proof search time varies run to run (SPEC.md line 631). | Keep a fast lane and a bounded full lane; record run-to-run variation rather than averaging it away. |

### What I did not check

- I did not read the 772 tests. I read `tests/properties/_prova_client.py`, the
  file listings, and ran the suite. I do not know how many of them would need
  repair under increment 1.
- I did not measure anything about resource use: no timing of a large input, no
  memory figure. Every number in D5 is a proposal to measure, not a measurement.
- I did not check whether Z3 (or any solver) is installed, licensable or available
  in CI. D1 assumes it can be added as a dependency; that is unverified.
- I did not check mutation coverage of the existing suite, so I cannot say how much
  of the current green is load-bearing.
- I did not try to encode any obligation by hand, so I cannot confirm that the hour
  clock or the reservation example falls inside the stated fragment.
- I did not check any platform other than this one: macOS with Python 3.12 locally,
  ubuntu with Python 3.12 in CI (`.github/workflows/ci.yml`).
- I did not read `.relay/`, `docs/RELAY.md`, `docs/relay*` or `docs/user-stories.md`
  beyond noticing that `docs/relay/plans/I1.md` is the only file referencing
  `conformance/` and `examples/hour-clock`. I was told to ignore them and I did.
- I did not use the Jev question service: no `TYPESAFE_API_KEY` is set and there is
  no `.nwave/config.json`, so `typesafe: unavailable`. Every classification in this
  document is my own, from the files cited.
- I did not verify the four untracked `docs/relay-*` and `docs/coordinator-*` files
  or `prompt.md` in the working tree. They are not part of this plan.

---

## 7. Proposed changes to SPEC.md and the other documents

I changed nothing. These are proposals for the Owner.

| ID | Where | What I propose, and why |
|---|---|---|
| P1 | SPEC.md lines 468-469 | The named operation categories are discovery, parsing, formatting, checking, verification, examples and building. The tool also runs `evaluate` (`src/prova/service.py:14`), which is the only way to run a program today and is relied on by most tests. Either add it as a named development operation, explicitly outside profile conformance, or rule that it must disappear when `build` lands. Until this is settled, F11 will advertise it as a non-profile operation. |
| P2 | SPEC.md line 640 | "map the first slice to independently reviewed Relay expectations" refers to a framework that has been dropped. Propose deleting that clause. Nothing else in SPEC.md depends on it. |
| P3 | `docs/EXPECTATIONS.md` lines 63, 71 | Q1 ("what is the first increment?") is answered by increment 1 above. Q9 (Relay identity and evidence runner) is void. Propose marking both closed. |
| P4 | SPEC.md lines 612-613 | SPEC.md names reservations as the first recommended conformance target. `examples/hour-clock.prova` is a smaller, working `core-0` program with one event and one action, and it is already the cheaper first machine target. Propose naming the hour clock as the first target and reservations as the second. This changes no semantics for either. |
| P5 | `README.md` lines 9-12, 20 | The README says "There is no compiler, test runner, build system, CI pipeline" and points to `docs/RELAY.md` as required reading. All four exist now and Relay is dropped. Propose updating it, and pointing at this roadmap instead. |
| P6 | `docs/EXPECTATIONS.md` lines 38-51 | E1 to E11 are good acceptance themes and I mapped features to them. E12 (does Prova help LLMs?) is an experiment after a working compiler, and Q8 defines nothing yet. Propose stating plainly that E12 and Q8 are out of scope until increment 5 is finished, so nobody treats them as compiler work. |


---

## 8. Owner decisions (recorded 14 November 2026)

The Owner approved every recommendation in this roadmap:

| ID | Decision |
|---|---|
| D1 | Solver: a pinned Z3 |
| D2 | `build` produces generated Python |
| D3 | Runtime values travel in the s-expression text form already tested |
| D4 | Bootstrap language stays Python 3.12 |
| D5 | Budgets: 1 MiB input, 10 s, 512 MiB memory, 1 MiB output, measured on CI first |
| D6 | The machine descriptor is a separate versioned JSON document |
| D7 | The product owner's recommendation stands (see section 5) |
| F1 | Accepted as a guard-only feature on its injected-fault evidence. The `nwstep` oracle gate has no declaration for a green-by-design oracle; that is a tool gap, not a Prova defect. |
| F2 | Category `cyclic_dependency`; one diagnostic per cycle with a `cycle` field; refusal exits 0 |

Features blocked only by D1-D6 are now READY. This is the Owner's approval of the
product owner's recommendations as written in section 5. Details of each option are
there.

### Follow-ups raised during delivery

- **Extract the shared parse-and-check preamble in `src/prova/service.py`.** The
  handlers for `check`, `examples`, `evaluate` and (with F16) `verify` each repeat
  about 15 lines. Do it as one behaviour-preserving commit with no test changes,
  when no other delivery is editing `service.py`. (Owner, 14 November 2026.)
- **Remove or reconsider the record-over-union-variant branch of
  `syntax.resolve_constructor`.** After F3 (constructor names must be unique) no
  accepted program can reach it. Raised during F3.
- **One launcher for the tool in the tests (prepares an implementation-neutral
  contract suite).** Seven fixture modules (`_f2` to `_f9`) each define their own
  `ToolRun`, and about 48 test files start the tool as a subprocess. Consolidate them
  into one launcher that reads the command from an environment variable
  (default: `python -m prova`), so the acceptance suite can run against any
  implementation of the JSON protocol. Behaviour-preserving, no test expectation
  changes. Do it after F10 and F17 have fixed the response shapes. Reason: a possible
  later port of the compiler to Rust (D4 would be reopened, and D2 would need a
  decision on whether the artefact stays generated Python). The Owner chose to wait
  on the port itself. (14-15 November 2026.)
- **Unify the builtin type names.** `syntax.BUILTIN_TYPE_NAMES` duplicates
  `checker.BUILTIN_TYPES`. Raised during F6.
- **Locate `recursive_type` and `unbound_type` diagnostics.** Done by F10: they now
  point at the declaration they are about (a stated limit: the parsed tree keeps no
  position for a type inside a signature or a record field). Only refusals about the
  request itself carry no place by design. `docs/spec-trace.md` row 8.6 may be
  brought up to date when the trace is next revised.
- **Forms accepted with text dropped.** `(deftype T (record (x Int)) extra)`,
  `(requires)`, `(ensures)` and `(if true 1 2 3)` are accepted and the extra text is
  silently ignored. Same on the pre-F6 base. Raised by the F6 and F9 reviews.
- **The `source` field of a request must be a string.** `{"source": 7}` ends the
  command with a traceback. Pre-existing; raised by the F9 review.
- **Independent review owed for F2, F3 and F16.** They were merged on the author's
  checks and a green suite, not an independent review.
- **Tool never ends in a traceback (robustness delivery).** Known crashes found by
  the F6 to F10 reviews, all older than the features that found them: an
  `IndexError` in `src/prova/evaluator.py` for `examples` on `examples/hour-clock.prova`
  with character 550 or 1191 deleted; `evaluate` with `"function": ["f"]`
  (`TypeError: unhashable`) and with `"arguments": 7` (`TypeError: not iterable`);
  an expression nested about 700 deep (`RecursionError` in `syntax.parse_expr`;
  450 deep is answered) and 1000 or more in `reader._read_form`. Each should be
  answered with a located refusal (an explicit nesting limit for the last two),
  never a traceback. (Raised by the F9, F10 and F2/F3 reviews.)
- **F10 review notes.** `symbol`, `expected` and `actual` mean different things inside
  one category (`malformed_value`; symmetric disagreements such as `=` operands);
  publish the symbol's role per kind or give symmetric disagreements their own
  subject. The enclosing declaration is threaded through four checker functions as a
  bare `within: str`; move it into a small checker context.
- **F16 review notes, for F18.** Path conditions are not simplified
  (`(and (p n) (matches t (A)) (p n))`, `(and (small b) false)`), and they mention
  let-bound names whose definition is in no entry. The solver work needs a normalised
  form and self-contained entries.
- **nwstep baseline after a rebase.** Re-initialising the workspace baseline after
  rebasing a delivery would let `record craft` run again; today craft stays at the
  pre-rebase revision. Tool gap, not a Prova defect.
- **Request text that cannot be encoded.** `{"operation":"check","source":"\udccc"}`
  (a lone surrogate escape) ends in `UnicodeEncodeError` in `SourceDigest.of`
  (`src/prova/service.py`), on every source-reading operation. Refuse a source that
  cannot be encoded as UTF-8 with `invalid_input` naming the field, at the request
  reader that already refuses a wrong-kind `source`. Pre-existing; raised by the F11
  review.
- **`format` attaches a comment to the following syntax node (SPEC.md line 63).**
  F15 attaches a comment to the following declaration, as its acceptance criterion 2
  says, and hoists a comment written inside a function body up to the next declaration.
  `parse` (F12) attaches a comment to the first node that follows it, at any depth, as
  SPEC.md line 63 says. A later delivery should make `format` follow the SPEC (a rule is
  needed for a comment that precedes a part inside a form written on one line), then
  recompute the hand-written `conformance/format/` pairs. The Owner chose to ship the
  criterion first. (15 November 2026.)
- **Integer literals longer than Python's digit limit.** A source holding an integer
  literal of more than 4300 digits ends in `ValueError: Exceeds the limit (4300 digits)`
  from `reader.py:106` (`int(self.text)`) on `check`, and on every operation that
  reads source. Refuse the literal with a located diagnostic (`syntax` or a limit
  category), never a traceback. Pre-existing; raised by the F15 review. Deliver it
  together with the lone-surrogate source crash above as one small robustness
  delivery (R2).
- **Three more inputs that end in a traceback (robustness delivery R3).** Found by the
  R2 review and executor, all older than R2: (1) an integer the evaluator computes that
  is too large to write (for example four nested multiplications of 1000-digit
  literals) ends in `ValueError` from `values.render`; (2) a budget environment
  variable set to a 5000-digit number ends in `ValueError` at `budgets.py:176`; (3) a
  request whose JSON nests about 20000 arrays deep ends in `RecursionError` inside
  the JSON reader. Also decide whether `operation` holding a surrogate is echoed back
  unchanged (it is today). Each should answer one JSON response.
- **A lowered interpreter digit limit still fails in the reader.** With
  `PYTHONINTMAXSTRDIGITS=640` (or `-X int_max_str_digits`) and a 1000-digit integer
  literal in a program, `reader.py` `int(self.text)` raises and the command answers
  `tool_failure`, on every operation, before R3 and after it. R2's literal limit (1000
  digits) is only safe while the interpreter's own limit is at least that; read the
  limit actually in force and refuse a literal above it with the same `syntax`
  refusal. Pre-existing; raised by the R3 review.
