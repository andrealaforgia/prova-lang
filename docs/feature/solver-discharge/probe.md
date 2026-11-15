# F18 — the probe: what was tried against the real build

Two kinds of probing were done. Neither is an independent review.

## Seven soundness defects, put back one at a time

A `proved` that is wrong is the worst thing this tool can do, so the
translation was broken deliberately, one defect at a time, to see which
test noticed. Each defect is a change a careless hand could really make.

| Defect re-injected | Noticed by |
|---|---|
| the sign of an inequality is wrong | the reservation example is no longer fully proved |
| a comparison becomes non-strict | the reservation example is no longer fully proved |
| the condition that reaches a call is dropped | the call behind a test is no longer proved |
| the precondition of the callee is dropped | the same call with nothing in front of it is proved, which it must not be |
| a literal multiplication is off by one | **nothing, at first** |
| the union tag asked about is the wrong one | the reservation example is no longer fully proved |
| the clauses of a match are tried in the wrong order | **nothing, at first** |

**The two survivors, and why they survived.** Every program in the
oracle that multiplied wrote the same product on both sides of its
promise, so a translation wrong by the same amount in both places agreed
with itself. And every match in the oracle was over variants that cannot
both match, so the order the clauses are tried in made no difference to
the answer.

Two programs were added to close that: one triples the number 2 and
promises 6 — a literal the product cannot cancel against — and one
matches 0 against a literal clause and then a catch-all, where both
clauses match and the first must win. Each defect now turns one of them
red. **Survivors after tightening: none of the seven.**

## Every edge of the two public surfaces

Thirteen cases, one per cell of the edge matrix that was not marked not
applicable, each run against the real command on this tree and on the
tree before the change. Eight of them fail before the change — that is
what makes them evidence. Five hold on both, because the behaviour they
describe is older than this change: a source that is not a program, a
request naming no operation, and a run stopped before it could finish,
which prints nothing and leaves nothing behind.

Beside them, the twelve scenarios the oracle promised were each run as
their own case, so each is reported as held rather than assumed.

## One prediction was wrong, and is reported as wrong

The edge matrix predicted that a request with an empty source would be
answered with an inventory of 0 obligations. It is not. A `core-0`
program must hold at least one declaration, so an empty source is
refused before any obligation is listed — and that refusal is older than
this change. The case records what the tool really answers, and this
paragraph records that the prediction was wrong rather than quietly
fixing the prediction.

## What the probe does not show

- Nothing here is independent. A defect I did not think to re-inject is
  a defect this probe says nothing about.
- The two surviving defects were found by probing, not by the oracle.
  That is the honest reading: the oracle had two blind spots, and the
  probe is what found them.
- The crash cases stop a run 20 ms in and observe that nothing was
  printed and nothing left behind. That is a run interrupted while
  answering; it is not a kill during a write, because this operation
  writes nothing at all.
