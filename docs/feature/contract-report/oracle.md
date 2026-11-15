# Oracle: which contracts promise nothing

## What the request asks for

A reader of a clean answer must see at a glance which functions promise
nothing, so an accepted program is not mistaken for a meaningful one
(SPEC.md lines 204-206: reports identify omitted and explicitly trivial
contracts, and acceptance of a trivial claim is not meaningful domain
correctness).

Five promises were read from the request:

| | Promise |
|---|---|
| P1 | a function declaring no `requires` has its precondition recorded as omitted |
| P2 | a block written as the literal `true` is recorded as trivial |
| P3 | a function with a real contract is recorded as neither |
| P4 | when every contract of a program is omitted or trivial, nothing in the answer describes it as meaningfully correct |
| P5 | the shape of the report is read from the tool itself |

Every sentence of the request maps to one of these or to a recorded
reason why it states no observable behaviour (a heading, a list number, a
promise about the commit, the branch or the scratch directory).

## Decisions taken here

The owner was absent, so these were decided by the executor and recorded
with the step.

- **Where the report lives.** In the answer of `check`, and nowhere else.
  That is the answer whose `completed` status a reader can mistake for a
  meaningful result, and the criteria say "when the program is checked".
  `verify` already answers that nothing was attempted, and an answer that
  refuses a program carries no report because no program was read.
- **A block with one real clause.** The clauses of a block are a
  conjunction, so a block holding the literal `true` beside a real clause
  is recorded as stated: it promises that clause.
- **An empty block.** `(requires)` is recorded as omitted. The parsed
  program keeps no mark that tells an empty block from an absent one.
- **Only the literal `true` is trivial.** SPEC.md asks for *explicitly*
  trivial contracts. `(ensures (or p (not p)))` is recorded as stated;
  deciding otherwise would need a solver, and this tool has none.

## Conflicts

Every one of the 34 request sentences was checked against what the tool
does today and none of them conflicts. In particular, no existing test
pins the key set of a `check` or a `discover` answer, so a new field
breaks none.

One existing expectation did fire during craft and was obeyed rather than
edited: `tests/unit/test_service_discover.py` refuses the words
"verified", "proved", "built" and "holds" anywhere in the manifest. The
first wording of a published sentence used "holds"; the sentence was
reworded. No test was changed.

## What is still open

Nothing in the request. The limits above (an empty block, a contract that
is true for every input without being written `true`) are recorded limits,
not open questions.
