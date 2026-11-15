# F16fix - what the tests had to start noticing

## What this delivery is about

A late review of the obligation inventory made 22 small deletions in the code
that walks a program and lists what it owes. Nine of them left the whole test
suite green while real obligations disappeared from the answer. A deletion that
nobody notices is a gap in the tests, not in the product: the walk itself was
right, the tests were simply not looking at most of it.

This delivery closes that gap. It changes no production code.

## What the tests now say

**Every position a body can put a call in.** The plan the property tests write
placed a generated call in three positions only: the body itself, the then arm
of an `if`, and the first clause of a `match`. It now places one in each of the
nine positions a `core-0` body has, and a second test puts all of them in a
single program at once, so a position stops being watched only if the generator
and that program both lose it.

**A condition made of several parts.** Only the conditions `true` and `false`
were ever read. A new program calls from behind three match clauses, with an
`if` inside a `let` inside the second clause, so the whole joined condition is
read - including the clause whose pattern matches anything and therefore adds
no condition of its own.

**How many calls a function makes.** The entry that says a function ends
reports a count of calls that nothing read. It is now read against a count
taken from the program by hand: four for the function that calls, none for the
one that calls nothing.

## The conflict I could not decide

The request also asks for a change of behaviour: an obligation arising in a
function's `ensures` block or in its body should be reported under that
function's own `requires`, not under `true`. SPEC.md lines 210 to 220 support
it: a postcondition is checked under the precondition.

I applied that rule to a throwaway copy and ran the whole suite. **Three
existing tests state the old text as their expected result and fail:**

| Test | What it pins |
|---|---|
| `tests/acceptance/.../test_each_call_owes_its_precondition_under_the_condition_that_reaches_it` | every call of the shipped hour clock is reached under `true`; `step` declares `requires (valid-state current)` and calls from its `ensures` |
| `tests/properties/.../test_every_function_example_and_call_owes_its_entry` | a body call of a generated function with a `requires` is reached under `true` |
| `tests/properties/.../test_putting_a_call_out_of_reach_keeps_what_it_owes` | the same call reads `true` when reachable and `false` when not |

The request forbids changing an existing test's expected result and tells me to
stop and report when one pins the old text. So the rule is **not applied**, no
test was edited, and the question goes back to the Owner. Findings 1 to 3,
which close all nine surviving deletions, are delivered.

Nothing else in the repository pins these conditions: no other test, fixture or
document states them.

## Still open

- The Owner's answer about the rule above.
- Path conditions name let-bound values whose definition is in no entry. The
  request assigns that to another delivery; nothing was done about it here.
