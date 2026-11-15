# Craft: the answer now says what each function promises

## What was built

`src/prova/checker.py` gains the rule, beside the other whole-program
rules:

- one table of the three words a block can be recorded with, each beside
  the meaning the manifest publishes;
- `ContractStrength`, which refuses any other word, and reads a block:
  no clause is omitted, every clause the literal `true` is trivial, one
  clause that is not is stated;
- `FunctionContracts`, what the two blocks of one function promise;
- `ContractReport`, one entry per declared function in declaration order,
  refusing to name one function twice.

`src/prova/service.py` gains three things and nothing else: the list of
operations that carry the report, one field in the `check` answer and the
published shape in the manifest. The dispatcher stays the only place that
knows operation names, so it passes that list to the publisher.

A checked program now answers, beside its digest:

```json
"contract_report": {
  "functions": [{"function": "step", "precondition": "stated", "postcondition": "stated"}],
  "totals": {"functions": 3, "contracts": 6, "omitted": 3, "trivial": 0, "stated": 3},
  "states_a_contract": true,
  "note": "..."
}
```

The shipped hour clock reads that way: `valid-state` omitted/omitted,
`initial` omitted/stated, `step` stated/stated.

## What a review of the first revision changed

Four findings: two defects of the answer, and two gaps in what the tests
would have caught. All four are closed here.

- **Defect.** The note was answered but never published; the manifest now
  describes it, and the test that compares the published parts with the
  answered ones fails if either grows without the other.
- **Test gap.** `(requires false)` and `(ensures false)` already read as
  stated: the rule read the value of a literal, not only that the clause
  was one. Nothing, however, would have noticed that rule going wrong --
  reading only "is a literal" would have made `false` trivial, and every
  test stayed green when it was tried. The fixtures and the generated
  block texts now carry both literals, expected to read stated, so that
  mutation turns three tests red.
- **Test gap.** Two of the three notes were never observed, so one
  sentence for every program would have passed. The three readings --
  promises nothing, promises something, declares no function -- are now
  asserted to differ.
- **Defect.** The published meaning of `stated` claimed the block says something
  about the function. That is false for `(ensures (and true true))`, so
  it now reads: the block has a clause that is not the literal `true`,
  and this tool does not decide whether that clause promises anything.
  That is DEC4: only the literal `true` is recognised as trivial,
  because deciding more would need a solver.

## What the design makes impossible

A strength is one of three published words: any other refuses at
construction, so an answer can never record a word a client cannot look
up in the manifest. A report cannot name one function twice, so its
totals can always be read against the source. Both refusals say what
failed, why it matters and how to repair it, and both have a test beside a
positive control that builds a valid report the same way.

The published shape and the answered report are read from one table, so
they cannot drift apart; a test checks every field and every word of six
real answers against the published shape.

## What the tests prove, and what they do not

They prove that each block of a function is recorded from its own text,
that the entries and the totals agree, that the totals partition the
blocks, and that no word of an answer about a program promising nothing
describes it as meaningfully correct. The scan is shown able to fire on a
sentence that does.

They do not prove that a written contract is true of its function:
nothing in this tool attempts that, and the report says so in its own
note.

## Formal model

No Quint model. The change adds no state, no protocol and no concurrency:
the report is computed from one parsed program and written into one
answer.

## Jev

typesafe: unavailable. `TYPESAFE_API_KEY` is absent from this
environment, checked from a shell command and from a login shell; the
client answered exit 3 before any question was sent. The two open choices
(where the report lives, how a block with one real clause reads) were
decided locally and are recorded in the oracle step as DEC1 and DEC2.

## Test cost

Measured, not guessed.

| | |
|---|---|
| the 7 new files, 9 runs in a row | 22 passed each time; real 3.00 s to 3.07 s, median 3.02 s |
| slowest new test | 0.46 s, each of the 4 property tests (12 generated cases, each case one real `prova` process) |
| slowest new acceptance test | 0.28 s |
| new unit tests | under 5 ms each |
| whole suite | 1067 passed |

The property cases cost about 40 ms each rather than the 10 ms a unit
case is budgeted: the law is observed through the real command, as every
property test in this repository does, so each case pays one process
start. That is a stated cost, not an unnoticed one.
