# Robustness R1 - what was built

## What changed, in order

This work sits on `f389095`. The commits below are its own, oldest
first; the one that prepares the ground is the first of them.

| Commit | What it does |
|---|---|
| `18d3066` | Prepares the ground: one object now answers how many fields a constructor declares. Behaviour unchanged, no test edited. |
| `eecd944` | The tests, all failing. |
| `e0cb22e` | The design and its diagram. |
| `55b477a` | The first three gates. |
| `7f5a75b` | This record, first written. |
| `fa36a23` | Two more inputs that still crashed: a program too long to run, and text that is not a request at all. |
| `c4e0717` | The record measured against the branch, and the two answers that changed. |
| `c3e6331` | The cost of the tests, measured over all of them. |
| `3d0eb88` | The law about reading an unchecked field narrowed, so it leaves ordinary code alone. |

The prepare-first commit was needed because the number of fields a
constructor declares was compared in two places that did not know about
each other, and the new rule would have been a third. The two existing
places now ask one object. One of them also resolved the same
constructor twice, once for its fields and once for its owning type; it
resolves once now.

## The gates

**A submitted request is read in one place.** Every field is answered
with its value or with a refusal naming that field. A list where a name
belongs, a number where a list belongs, an element of the argument list
that is not text, or something that is not an object at all, is refused
by name before any work starts. The two fields an evaluation needs are
read in one pass, so a client that wrote both wrongly is told about both
at once.

**Text that is not JSON is answered too.** Nothing, blank space, or an
object that stops partway used to be called a failure of the tool, with
a non-zero exit, so a client could not tell its own bad request from a
broken tool. It now carries the same category every other unreadable
field carries, and the place its text stopped at. The name reserved for
a failure of the tool itself keeps that meaning and stays out of the
published statuses.

**A text is read no deeper than the tool follows it.** 128 nested
forms. The depth is counted in the one place it grows, which covers the
source of a program and the text of an argument. One object holds the
number: the reader asks it and the manifest publishes it.

**A program is run no further than the tool reaches.** 160 evaluation
steps standing inside one another. The count is over every evaluation
step, not over calls alone: the expression written inside each call is
still standing on the same stack when the next call is made, so
counting calls would leave the mixture unbounded and a short chain of
deeply written functions would still exhaust the stack. One number
covers both because both stand on one stack.

**A value written in a program is counted against the fields its type
declares.** This is where the shipped hour clock went wrong: deleting
the character holding the number inside a one-field record left an
example writing a record with nothing in it, which was accepted and
then read for a field that was never there.

## Why 160, and what it costs

Measured on this branch, each evaluation step standing inside another
costs 2 interpreter frames, so 160 steps cost about 340 of the 1000
Python allows, leaving about 660 for whatever stack the caller already
has.

The cost is real and worth stating. A chain of up to about 490 calls
runs today; from now on a chain of more than 160 is refused. A longer
limit cannot be bought: the same counter has to absorb an expression
written at the published nesting limit of 128, and a program may mix
the two freely. 160 is far more than a person writes by hand and far
fewer than a generator emits without noticing.

## Two things that are answered differently than before

The request asks that everything accepted before be answered exactly as
before. Two answers changed, both deliberately, and both are stated
here rather than left to be discovered.

**A record written with the wrong number of values is now refused.**
That is the defect this delivery exists to repair, so programs that
were accepted and then crashed the tool are now refused instead. Some
of them did not crash. Swap characters 1289 and 1290 of the shipped
hour clock and an example reads `(Outcome (Clock 1)2 true)`: a record
written with three values where its type declares two. Before this
change that program was answered `completed`; it is now answered
`invalid_program` with an `arity_mismatch` naming `Outcome`. Verified
by running both, the first in a worktree at `988db32`.

**A field of the request is now refused before the program is read.**
A request whose `function` is missing and whose `source` is also broken
used to be answered `invalid_program` with a `syntax` refusal, because
the program was read first. It is now answered `invalid_input` with a
`malformed_request` naming the field. This is the decision recorded in
the design: a request that cannot be read is not a request about a
program yet, so there is nothing to report about a program.

## Evidence

| Check | Command | Result |
|---|---|---|
| Whole suite, here | `uv run pytest -q tests` | 1136 passed in 140.72s |
| The branch this work sits on | same, at `f389095` | 1067 passed in 121.68s |
| Prepare-first commit preserves behaviour | `uv run pytest -q tests/unit` | 63 passed |
| Mechanical check | `uv run python -m compileall -q src tests` | exit 0 |

**69 tests are new**: 1067 at `f389095` plus 69 is 1136. Both counts
were measured, the base one in a worktree checked out at `f389095`, not
carried over from an earlier run of the branch. No existing test was
edited and none broke.

Two earlier counts appear in the history of this record and are kept
here so they are not mistaken for the current one: 1045 at `988db32`
and 1091 at a point part way through this work. Neither is the base of
this delivery; `f389095` is.

## Test cost

All nine new test files were run nine times in a row at this commit:
69 tests each, all nine green, median 6.45s, slowest 6.46s. The nine
runs span 0.02s end to end, so nothing in them is flaky.

| | |
|---|---|
| Tests | 69 |
| Runs | 9, all green |
| Median | 6.45s |
| Slowest | 6.46s |
| Slowest single test | 3.29s, the sweep of mangled requests |
| Every other test | under 0.2s |

The sweep sends over ten thousand requests: the three programs this
repository ships, cut off and dented at every character, every field of
every operation holding every kind of JSON value, chains of functions
from 1 to 2000 long, and 500 requests drawn from a fixed seed. It calls
the command's own entry point in this process with standard input and
output replaced, because that many subprocesses would cost minutes; the
acceptance tests keep real subprocesses, one per family, where the cost
of a process is paid once.

## Each new behaviour was broken on purpose

| What was broken | What failed |
|---|---|
| The reader stops counting how deep it has gone | 3 of 7 |
| A value is no longer counted against its declared fields | 5 of 9 |
| A function field of any kind is accepted as a name | 5 of 24 |
| The manifest publishes a number the reader does not enforce | 5 of 7 |
| A step reads a submitted field for itself again | 1 of 2 |
| The evaluator stops counting how far it has gone | 3 of 7 |
| Unreadable text is called a failure of the tool again | 6 of 14 |
| The architectural check looks only for the polite spelling | 1 of 3 |
| The law also flags counting a place in a list it was handed | 1 of 4 |

Each break was put back and the suite is green again.

## Jev

`typesafe: unavailable`. `TYPESAFE_API_KEY` is absent from this
environment, so the client exited 3 and nothing was transmitted. The
open choices were settled against the table of diagnostic kinds, the
arity rule that already exists over expressions, and the status
vocabulary the suite already names.

## Deliberate break of a design rule

`DeclaredConstructor` holds three values where the house rule asks for
at most two. The three are the name, the type that owns it and its
fields: the parts of one declaration. Splitting them would add a
collaborator no rule asks for, and would separate the name a person
wrote from what that name resolves to, which is exactly the pair a
refusal must show together.

## What this does not claim

Nothing is proved. Building a function name and the argument texts is
centralised, not proved: Python lets a caller build those objects
around any value by hand. The claim is that this tool has one path and
that path refuses.

The two limits bound the stack the evaluator and the reader use. They
are not a claim about memory or about time: a program inside both
limits can still build a very large value, and nothing here measures
how long a run takes.

Nothing was measured on another interpreter. The frame counts behind
both limits were taken on the Python this repository pins, and a build
with a different frame layout would need them taken again.

## Found, not fixed

A record written with the right number of values but the wrong kind of
value in one of them is accepted and run. It does not crash, so it is
outside this request. It is a gap in the same rule about values and
belongs to whoever owns the checker's value rules.

## An existing test now describes the old behaviour

`test_f9_b6_the_manifest_publishes_the_unsupported_answer.py` still
passes unchanged: it requires the manifest to say what its list of
statuses covers, to mention the name reserved for a failure of the
tool, and to leave that name out of the list. All three still hold.
Its docstring, though, says the command answers an unreadable request
with that name and exits 1, which is no longer what happens. The
docstring was not edited, because the test belongs to another feature.
It is reported here for its owner.
