# Craft: the tool now says what it owes

## What was built

`src/prova/obligations.py` (new) turns a checked program into the list of
obligations it owes. `src/prova/service.py` gains one dispatch branch, one
handler and one manifest entry; nothing else in the tool changed.

Asking the shipped hour clock what must be shown now answers 20 obligations:

| Kind | Hour clock | Reservation example |
|---|---|---|
| contract definedness (one per function) | 3 | 3 |
| call precondition (one per call, under the condition that reaches it) | 3 | 2 |
| body to postcondition (one per function) | 3 | 3 |
| example validity (one per declared example) | 8 | 7 |
| structural termination (one per function) | 3 | 3 |
| **total** | **20** | **18** |

Every entry reads `result: not_attempted`. The answer's totals say
`attempted: 0`, and its note says the tool has no solver and ran none of them.
No word in the answer reports an outcome: the suite scans the whole answer,
keys included, for `verified`, `proved`, `proof`, `holds`, `sound`, `correct`
and six more, and the scan is shown able to fire on a sentence that does report
one.

A call keeps its obligation when it can never run. `(if false (tiny n) 0)` owes
`call_precondition:caller:body/then` with `path_condition: "false"`; moving the
same call into the branch that does run changes that one field to `"true"` and
nothing else.

## What the design makes impossible

`Obligation` takes no result: `not_attempted` is a constant of the type. An
answer reporting attempted work cannot be built, only written by hand elsewhere
-- and nothing else writes one, because the service renders obligations only
through their own `as_dict`.

An `Inventory` refuses two obligations with one identity at construction, and
identities are structural (`call_precondition:step:ensures[0]`), so reformatting
a program leaves every one unchanged.

Two things can only be reached by building a program by hand, past the reader
and the checker: a call to a function nothing declares, and two obligations
claiming one identity. Both refuse loudly with what failed, why it matters and
how to fix it; both refusals have a test, beside a positive control that builds
a valid program the same way.

## Proof that the tests can fail

Two deliberate mutations, applied after green and then reverted:

| Mutation | Result |
|---|---|
| the result constant reads `proved` instead of `not_attempted` | `test_no_obligation_is_ever_answered_as_attempted` and `test_nothing_in_the_answer_reports_work_the_tool_never_did` both fail |
| the walk forgets the condition on an `if` then-branch | `test_putting_a_call_out_of_reach_keeps_what_it_owes` and `test_a_call_that_can_never_run_still_owes_its_obligation` both fail |

## Test cost

The four new files, run nine times in a row: nine passes, 16 tests each,
median 3.95 s, slowest run 4.00 s. The slowest single test is a generated
property at 0.98 s; the three remaining properties are 0.81-0.97 s, every
acceptance test is at or under 0.07 s, and the 48 unit tests in the suite
finish together in 0.08 s. Whole suite: `821 passed in 79.60s`.

The property files are the cost: each generated case runs the real `prova`
command in its own process. They are bounded at 15-25 cases with a fixed seed,
which keeps the file under four seconds.

## One oracle expectation corrected, and why

The oracle's edge matrix predicted that a call to an undeclared function would
be refused under the category `unknown_function`. The checker's own category for
it is `unbound_name`; `unknown_function` is what the tool reports when an
*evaluate* request names a function the program does not declare. The promise
being tested -- `verify` refuses with the whole-program check's own diagnostics
and no inventory -- is unchanged, and the test now names the category the
checker really gives. This is a correction to a guess in the oracle, not a
change of what was promised.

## Documents corrected

`docs/spec-trace.md` §5 said nothing in the section existed. Rows 5.1, 5.2, 5.6
and 5.8 move from Not started to Partial, with what is listed and what is still
never attempted; the summary counts and the `verify-0` reading move with them.
The `verify-0` row of `docs/ROADMAP.md`'s state table now reads "Inventory only,
nothing attempted".

## Not verified

No obligation was attempted, so nothing here says anything about whether a
program is in any state. Whether these are the obligations a solver will want is
the next feature's question. Concurrency and crash behaviour are argued, not
observed: the operation writes nothing and keeps nothing between requests, so
there is no window to observe from outside.
