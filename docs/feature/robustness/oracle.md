# Robustness R1 - the oracle

## What this delivery is about

Today the tool ends in a Python traceback on some inputs. A caller that
sends one of them sees nothing on standard output and an exit code that
says the tool broke, when in fact its input was wrong. This delivery
makes every request come back as one JSON answer.

## What was reproduced before anything was written

Four families of crash, all on the branch as it stands:

| What a caller sends | What happens today |
|---|---|
| The shipped hour clock with character 550 or 1191 deleted | the checker accepts it, then the tool reaches for a field of a record that has none, and raises |
| `function` or `operation` holding a list or an object | the tool raises while looking the value up |
| `arguments` holding a number, or an argument holding one | the tool raises while reading the value |
| A text nested about 500 forms deep | the tool follows the nesting until the interpreter runs out of stack |

A sweep of 10249 mangled requests over all five operations, built from
the three programs this repository ships cut and dented at every
character, found 56 of these and no other kind. No request exited with a
code other than 0 without first raising.

## The cause of the first one

The hour clock declares `Clock` with one field. Deleting the character
that holds the `1` inside `(Clock 1)` leaves an example writing
`(Clock)`: a record with no field at all. The checker tests that the
record's name is declared and never that it carries one value per
declared field, so the program is accepted and the tool then reads a
field that is not there.

The same defect written in an expression rather than in an example is
already refused, with the record named and the two counts beside it.
The rule exists; the value written in an example simply does not go
through it. The repair belongs there, not in the part that runs the
program.

## What is promised

1. Any request the tool can receive comes back as one JSON answer, and
   the command exits 0.
2. Input that breaks a rule comes back as a located refusal in a
   published category.
3. A record written without one value per declared field is refused,
   naming the record, the count declared, the count written and where.
4. A `function` that is not a name, or `arguments` that are not a list
   of texts, is refused naming the one field to repair.
5. A text nested deeper than the tool reads is refused, saying the
   limit, how deep the text went and where.
6. The manifest publishes the nesting limit, so a caller never has to
   meet it to learn it.
7. Fields of the wrong kind, and a request that is not an object, are
   answered rather than raised.
8. Everything the tool accepted before is answered exactly as before.

## What is still open

Two questions go to the owner before any code is written. Both are
recorded in the step as conflicts with their decisions, and both can be
reversed cheaply at this point because only test files exist so far.

1. **How deep may a text nest?** The proposal is 128 forms. Measured on
   this branch, the deepest path through the tool costs 2 interpreter
   frames per level, so 128 costs 269 of the 1000 Python allows, leaving
   over 700 for the caller's own stack. The deepest program this
   repository ships or tests nests 10. The cost is that a text nested
   between 129 and about 500, which the tool answers today, is refused
   from now on.

2. **What does a `function` field holding a number or nothing get?**
   Today it is answered "no function of that name". The criterion asks
   for "that field holds the wrong kind of value" instead. The proposal
   follows the criterion, because a list is not a misspelled name.

## One thing found and not fixed

A record written with the right number of values but the wrong kind of
value in one of them (`(Clock true)` where the field is a whole number)
is accepted and run. It does not crash, so it is outside this request,
but it is a gap in the same rule and belongs to whoever owns the
checker's value rules.

## What was seen fail

The six new test files were run against the branch as it stands: 34
failed, 11 passed. The 11 that passed are the controls beside each
refusal - the untouched programs, a record written correctly, a request
with every field of the right kind - which must keep passing so that a
tool refusing everything could not satisfy the other 34.
