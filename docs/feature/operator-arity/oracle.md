# F7 oracle: an operator takes exactly its own arguments

## What the request asks for

SPEC.md lines 178-189 give every builtin operator a fixed number of
arguments - one for `not`, two for `+ - * < <= > >= =` `and` and `or` -
and say operators have no variable arity. The tool used to read
`(not flag flag)`, `(+ cents)` and `(+ cents cents cents)` as valid
programs, quietly ignoring whatever did not fit. This feature refuses
them and says, in the refusal, how many arguments the operator takes and
how many the program gave.

Six promises were written from the request:

| | Promise |
|---|---|
| P1 | `not` with two arguments is refused, with both counts |
| P2 | `+` with one argument, or with three, is refused the same way |
| P3 | Every comparison, equality and boolean operator with a wrong count is refused the same way |
| P4 | Every operator applied to its own number of arguments is still accepted and still answers what the language says it answers |
| P5 | The refusal carries a word the tool already publishes in its manifest |
| P6 | An operator with no arguments at all is answered with that refusal instead of stopping the command without an answer |

Everything else in the request is a constraint on the change (which
files to touch, what the commit says, where the work happens) and is
recorded as not testable, with its reason, in the delivery record.

## What was decided, and why

**The refusal uses the word the tool already publishes.** A call to a
declared function given the wrong number of arguments, and a constructor
given the wrong number of fields, already answer with `arity_mismatch`,
and both already state the expected and the actual count. An operator is
the same defect for a reader, so it is the same word. Nothing new is
published, which also leaves the manifest file alone while another
delivery is working there. The repository's own probe for this clause
(`docs/spec-trace/probe.py`, probe `E5`) already expected that word.

**A wrong count and a wrong operand are two defects, told together.** A
program that writes `(+ cents cents flag)` breaks two rules, and the
rule for a call to a declared function already reports both in one pass.
Operands of the right type never add a second refusal: a program whose
only defect is the count hears only about the count.

**No formal model.** The rule compares two numbers inside one
expression. There is no state, protocol, concurrency or interruption for
a model to explore.

**The owner was absent for this run**, so these are the author's
decisions, taken inside what the request already allows: it lets an
existing category be reused when it fits, and the sibling rule settles
the second question.

## Conflicts looked for, and found

Every sentence of the request was checked against what the tool already
does. No conflict was found. The search that matters: every program
text in the repository - the shipped example, the conformance program,
the evidence cases and every program written inside a test - was parsed
and searched for an operator applied to a number of arguments other than
its own. There are none, so no existing test's expected result changes.
The same search reports a planted case when one is given to it, so the
zero is a real zero and not a search that never ran.

## What proves it

| Promise | Test |
|---|---|
| P1 | `test_negation_written_with_two_arguments_is_refused_with_both_counts` |
| P2 | `test_a_sum_written_with_one_argument_is_refused_with_both_counts` (and the three-argument case beside it) |
| P3 | `test_each_operator_written_with_a_wrong_number_of_arguments_is_refused` |
| P4 | `test_an_operator_is_accepted_exactly_when_it_has_its_own_number_of_arguments` |
| P5 | `test_the_refusal_a_wrongly_counted_operator_carries_is_published` |
| P6 | `test_running_that_program_answers_a_refusal_instead_of_stopping` |

Every one of those failed on the tree as it was before the feature, for
the promised reason: the tool accepted the program. The tool ran that
red command itself and kept the list of failing tests.

Two laws are checked with generated input through the published `check`
operation: a program is accepted exactly when every operator in it has
its own number of arguments, and every refusal states both counts at the
place of the call. Generated checks are evidence, not proof; they sample
these claims over the eleven operators and counts from none to six.

Each refusal is paired with a control that accepts almost the same
program, so a tool that refused everything would fail here.

After the review, three more refusals were added where an expression may
also stand - in a precondition, in a postcondition and in the body of a
`match` clause - each pointing at the place the test works out from its
own program text, with one control that writes correct operators in all
three at once.

## Still open

- The recorded edge case "an empty source is accepted with no
  diagnostics" is **stale**. While this feature was being built, the
  rule that a program is one or more declarations landed beside it, so
  an empty source is now refused for a reason of its own. The control
  that pinned acceptance was moved onto a whole valid program that
  writes no operator anywhere, which is what it was always for; the
  recorded edge line itself was not re-recorded.
- `docs/spec-trace.md` still records this clause as missing. That
  document is a snapshot measured at a named commit and already carries
  other rows a later delivery overtook (row 2.13, which its own probe
  now reports as satisfied), so it is left to its owner rather than
  half-updated here.
