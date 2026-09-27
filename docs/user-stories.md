# User stories: iteration I1 — a checked evaluator for the reservation source

## Iteration goal

Iteration I1 delivers a checked evaluator for the reservation source, shown
through two operations run from a terminal: checking (whole-program, static)
and direct evaluation (dynamic, per input). Every story below is a vertical
slice the Owner can run on its own through the Prova tool's real operations.
No story's output ever claims "verified", "proved" or "built".

## Out of scope

The following are explicitly not part of iteration I1, and each story's
acceptance criteria stop short of them:

- The build operation, in any form. The tool refuses a build request as
  unavailable rather than attempting one.
- The verify operation (`verify-0`) and any solver-backed obligation
  discharge.
- The `machine-0` descriptor, its projection/admissibility helpers, and any
  induction obligation.
- Any claim of universal proof or total correctness. A passed check is
  evidence about the one input or example exercised, never more.
- Adaptation of historical sample fixtures.

## Protected example rule

The reservation source's semantics, contracts, declared examples and the
six-row transition table are never changed to make a story's acceptance
criteria pass. Where a story needs a wrong or invalid variant (a malformed
input, a wrong function body, an invalid program), that variant is a
separate, hand-built artefact used only to prove rejection or detection; the
protected source itself is always also run, unchanged, as the positive
control confirming the checked behaviour still accepts it.

## Stories, in priority order

### Story 1: Directly evaluate the reservation step function on fresh inputs and see all six table rows reproduced

**Narrative:** As the Owner, I want to run the reservation source's `step`
function directly against inputs that have no declared example, so that I
can see the tool actually reproduce the transition table rather than take my
word for it. To see it working, the Owner will run the Prova tool's direct
evaluation operation against the reservation source, in a terminal, supplying
each of the six table rows' before-state and event in turn, and separately
request the build and verify operations to confirm they are refused.

- Priority: 1
- Risk: medium
- Size: M

**Acceptance criteria:**
- Given the reservation source, when the Owner runs the direct evaluation
  operation against `step` for each of the six table rows in turn, including
  the two no declared example covers ((1, Reserve) and (2, Release)), then
  the reported state and `accepted` flag match the table exactly for every
  row.
- Given the reported output of any of these runs, when the Owner reads it,
  then it describes itself only as evaluation output and contains no claim
  of "verified", "proved" or "built".
- Given the Owner instead requests the build operation or the verify
  operation against the reservation source, when either request runs, then
  the tool refuses it explicitly and reports the operation as unavailable
  rather than attempting it.

### Story 2: Run every function's declared examples and see them pass

**Narrative:** As the Owner, I want to run every function's declared
examples through direct evaluation and see them pass, so that I can trust
the declared examples are actually exercised and not merely documentation.
To see it working, the Owner will run the direct evaluation operation over
the reservation source's declared examples for `valid-state`, `initial` and
`step`, in a terminal, and once more against a separate copy with one
example's expected value deliberately wrong.

- Priority: 2
- Risk: low
- Size: S

**Acceptance criteria:**
- Given the reservation source's declared examples (two for `valid-state`,
  one for `initial`, four for `step`), when the Owner runs the direct
  evaluation operation over them, then all seven are reported as passed.
- Given the reported outcome, when the Owner reads it, then each example's
  pass is attributed to the specific function and example it belongs to,
  not folded into a single total.
- Given a separate copy of the reservation source with one declared
  example's expected value deliberately changed to an incorrect one, when
  the Owner runs the same direct evaluation operation against that copy,
  then that one example is reported as failed while the protected source's
  own examples continue to pass unchanged.

### Story 3: Reject invalid entry states and malformed inputs before evaluation proceeds

**Narrative:** As the Owner, I want entry precondition violations and
malformed or ill-typed inputs rejected rather than silently evaluated, so
that I can trust `step` never runs on a state it was never meant to handle.
To see it working, the Owner will run the direct evaluation operation
against `step` with `(Reservation 3)`, `(Reservation -1)`, a malformed
value, and a valid entry state as the positive control, in a terminal.

- Priority: 3
- Risk: medium
- Size: M

**Acceptance criteria:**
- Given the entry state `(Reservation 3)`, when the Owner runs the direct
  evaluation operation against `step` with any event, then the tool rejects
  the call with no successful result, citing the precondition.
- Given the entry state `(Reservation -1)`, when the Owner runs the same
  operation, then the tool rejects the call with no successful result,
  citing the precondition.
- Given a malformed or ill-typed value offered in place of a valid
  `Reservation`, when the Owner runs the same operation, then the tool
  rejects the call with no successful result, reported distinctly from a
  precondition rejection.
- Given a valid entry state such as `(Reservation 0)` used as the positive
  control, when the Owner runs the same operation with a valid event, then
  the tool proceeds to a successful result, confirming the three rejections
  above are specific to the invalid inputs.

### Story 4: Detect postcondition violations in deliberately wrong step bodies

**Narrative:** As the Owner, I want three deliberately wrong versions of
`step`'s body caught by postcondition evaluation, while the reservation
source's contracts, examples and table stay exactly as published, so that I
can trust the postcondition check catches a real defect rather than only
ever agreeing with a correct implementation. To see it working, the Owner
will run the direct evaluation operation against three separately hand-built
wrong-body variants (missing upper guard, flipped `accepted` flag,
reject-everything) under the unchanged contract, and against the protected
reservation source as the positive control, in a terminal.

- Priority: 4
- Risk: medium
- Size: M

**Acceptance criteria:**
- Given a variant of `step` with the upper guard removed, when the Owner
  runs the direct evaluation operation with an input only that guard would
  have rejected, then the tool reports a postcondition violation, not a
  successful result.
- Given a variant of `step` with the `accepted` flag flipped, when the Owner
  runs the same operation with any valid input, then the tool reports a
  postcondition violation, not a successful result.
- Given a variant of `step` that rejects every event, when the Owner runs
  the same operation with an input the table marks accepted, then the tool
  reports a postcondition violation, not a successful result.
- Given the unmodified reservation source used as the positive control, when
  the Owner runs the same operation against it, then every result is
  reported as satisfying its postcondition, confirming the three detections
  above are specific to the wrong bodies.

### Story 5: Check the whole reservation program and reject invalid variants with a structured diagnostic

**Narrative:** As the Owner, I want whole-program checking to accept the
reservation source and reject invalid variants, including one with an error
placed in a branch none of the four declared examples reaches, so that I
can trust checking catches errors that evaluation alone might never
exercise. To see it working, the Owner will run the Prova tool's check
operation against the reservation source, and separately against hand-built
invalid variants, in a terminal.

- Priority: 5
- Risk: high
- Size: L

**Acceptance criteria:**
- Given the unmodified reservation source, when the Owner runs the check
  operation against it, then the tool reports the whole program as accepted
  with no errors.
- Given a hand-built variant with a type error placed inside
  one of `step`'s two branches, in a spot none of the four declared examples
  reaches, when the Owner runs the check operation against it, then the
  tool rejects the program.
- Given that rejection, when the Owner reads the reported diagnostic, then
  it names both the category of the error and its location within the
  source.
- Given a second, separate hand-built variant with a different invalid
  construct elsewhere in the source, when the Owner runs the check
  operation against it, then it is also rejected with its own category and
  location, confirming rejection is not limited to one specific error shape.

### Story 6: Preserve exact arbitrarily large integers through direct evaluation

**Narrative:** As the Owner, I want integers far beyond the range that
floating-point arithmetic represents exactly to be evaluated and returned
exactly, so that I can trust the tool's arbitrary-precision guarantee and
know values are never silently routed through binary floating point. The
reservation `step` cannot show this, because its precondition rejects any
count above two, so this story uses a small separate `core-0` source with an
integer function (for example, one that adds one to its argument). To see it
working, the Owner will run the direct evaluation operation on that function
in a terminal with very large positive and negative integers, and with a
small integer as the positive control.

- Priority: 6
- Risk: low
- Size: S

**Acceptance criteria:**
- Given a small `core-0` source whose function adds one to an integer, when
  the Owner directly evaluates it with 9007199254740993 (above the largest
  integer floating point represents exactly), then the reported result is
  exactly 9007199254740994.
- Given the same source, when the Owner directly evaluates it with
  -9007199254740995, then the reported result is exactly -9007199254740994.
- Given the same source, when the Owner directly evaluates it with 41 as the
  positive control, then the reported result is exactly 42.
