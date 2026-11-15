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
| the 7 new files, 9 runs in a row | 21 passed each time; real 3.04 s to 3.20 s, median 3.06 s |
| slowest new test | 0.50 s, each of the 4 property tests (12 generated cases, each case one real `prova` process) |
| slowest new acceptance test | 0.28 s |
| new unit tests | under 5 ms each |
| whole suite | 1066 passed in 121 s |

The property cases cost about 40 ms each rather than the 10 ms a unit
case is budgeted: the law is observed through the real command, as every
property test in this repository does, so each case pays one process
start. That is a stated cost, not an unnoticed one.
