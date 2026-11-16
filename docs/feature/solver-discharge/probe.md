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
red. **That sentence used to read "survivors: none of the seven", and it
overstated what had been shown.** Those seven were the defects I thought
of. An independent review of the same code found four more that survived
the whole suite, two of them giving a `proved` the evaluator
contradicts: a match whose clauses are read in source order rather than
innermost-first, a negation translated as the thing it negates, a
timed-out query read as settled, and a solver's "cannot tell" read as
"nothing refutes it". Each now has its own expectation -- the first two
in the verify-driven oracle, the last two at the seam where a verdict
becomes a finding -- and the honest statement is this one: no defect
from either list survives, and a defect neither list thought of is one
this probe says nothing about.

## After two independent reviews: thirteen defects, none surviving

The reviews found no wrong `proved` in 4600 generated programs covering
44,007 obligations — and four defects that survived this whole suite
anyway, two of them giving a `proved` the evaluator contradicts. Each
now has its own expectation, and every defect from either list was put
back one at a time and turned a test red:

| Defect | Turned red by |
|---|---|
| a match read in source order, not innermost first | the promise true only of a later clause |
| a negation read as the thing it negates | the call reached because a test failed |
| a timed-out query read as settled | the verdict-to-finding seam |
| a solver's "cannot tell" read as "nothing refutes it" | the three answers read on their own |
| the witness replay gate removed | the candidate that does not replay |
| a rule of the profile labelled as the solver | what settled each entry |
| the disclosure carried where no solver was asked | the program outside the fragment |
| the five from the first probe list | as before |

The last of those needed the code to change, not only the oracle: the
third answer a solver can give was read inside the question that asked
it, where no program of this fragment can reach it. It is read in one
place now, which a test can hand an answer to directly.

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
