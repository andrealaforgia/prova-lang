# F16fix - what the tests had to start noticing

## What this delivery is about

A late review of the obligation inventory made 22 small deletions in the code
that walks a program and lists what it owes. Nine of them left the whole test
suite green while real obligations disappeared from the answer. The review also
found one real defect in what the answer says.

## The tests that were not looking (findings 1 to 3)

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

None of these three needed the product to move. The walk was already right; the
tests were simply not looking at most of it.

## The defect (finding 4)

A call in a function's postcondition, or in its body, was listed as reached
under `true`. SPEC.md states the claim as `Pre_f(x) implies ...`: a
postcondition is checked under the precondition, and the body answers it for
every input that meets the precondition. So `a4`, which may only run where
`(> (a3 n) 0)` holds, appeared to owe `a1`'s precondition everywhere, with its
own assumption dropped.

A call inside a `requires` is different and was already right. A precondition
must be well-defined for every typed input and cannot assume itself true to
justify a partial call, so nothing is put in front of it.

## The conflict, and how it was settled

Three existing tests stated the old condition as their expected result. I
applied the rule to a throwaway copy, ran the whole suite, and measured exactly
which ones fail:

| Test | What it pinned |
|---|---|
| `test_each_call_owes_its_precondition_under_the_condition_that_reaches_it` | every call of the shipped hour clock is reached under `true`; `step` declares `requires (valid-state current)` and calls from its `ensures` |
| `test_every_function_example_and_call_owes_its_entry` | a body call of a generated function with a `requires` is reached under `true` |
| `test_putting_a_call_out_of_reach_keeps_what_it_owes` | the same call reads `true` when reachable and `false` when not |

The request forbids changing an existing test's expected result, so I stopped
and reported the three, with the measurement and one question. **The Owner
decided that those three may be rewritten to the new text, and nothing else in
them.** They were changed on their own, in a commit that is red by itself and
says so, before the commit that makes them green again.

Nothing else in the repository pinned these conditions: no other test, fixture
or document stated them.

## Still open

- Path conditions name let-bound values whose definition is in no entry. The
  request assigns that to another delivery; nothing was done about it here.
- An independent reviewer has not yet read this change.
