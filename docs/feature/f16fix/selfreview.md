# F16fix - my own review of this change

Seventeen questions are asked of every delivery. This one moves no production
code, so several of them have nothing to grip on; where that is so I say why
rather than claim a pass.

## Design and code

**D1 architecture.** Nothing in the design moved. The walk over a body, the
value that carries a path condition and the kinds of obligation are as they
were.

**D2 one source of truth.** The expected answer is still derived in one place:
the plan the property tests write. The new positions extend that plan, and the
new count of calls is derived from the same plan rather than written out a
second time. The fixed program in the acceptance test states its conditions by
hand, which is the point of it: it is the independent reading of the plan.

**D3 boundaries.** The property tests and the acceptance tests drive the
`prova` command over its JSON surface and import nothing from `src/prova`.
That was already true and is still true.

**D4 wrong states unrepresentable.** No new type was added, so the question is
about the plan. It holds one entry per call position, so a position with
no expected site cannot be written - `BODY_SHAPES` carries the site and the
condition together, and every reader takes both from it
(`tests/properties/test_obligation_inventory_laws.py:52`).

**D5 small and cohesive.** The plan's helpers each answer one question: which
identities are owed, which conditions, how many calls
(`tests/properties/test_obligation_inventory_laws.py:177`).

**D6 patterns, D7 domain-driven design, D8 infrastructure.** Nothing to report:
no new unit of production code exists in this change.

## Tests

**D9 public interface only.** Every new assertion reads the answer the `prova`
command prints. No production symbol is imported and no internal is named
(`tests/acceptance/test_verify_lists_the_obligations_owed.py:305`).

**D10 naming.** The new tests are named for what the Owner is owed: a call in
every position a body can hold owes its entry; a call behind several
conditions is owed under all of them; the ending entry says how many calls the
function makes.

**D11 helpers.** The new tests reuse the helpers already there - the plan, the
renderer, the runner - and add no parallel machinery.

**D12 generated tests.** The generated plan now draws from all nine call
positions, and the law it states is unchanged
(`tests/properties/test_obligation_inventory_laws.py:302`). Because a run draws
only some of them, a second, fixed program holds every position at once; that
is what makes a lost position impossible to miss rather than unlikely to be
missed.

**D13 speed.** Measured, not guessed: the two files run in about 5 s, nine
times out of nine, and the whole suite in 113 s. The numbers are in `craft.md`.
These tests start a process each, so they are integration tests; none of them
sleeps or reads a clock.

**D14 duplication.** The two new acceptance tests read the same program for two
different questions - the conditions, and the call counts - rather than
asserting both in one test. That is deliberate: a failure then names which of
the two the tool got wrong.

**D15 failure messages.** Every new assertion says what was found, why it is
owed and where to look, and prints the program that produced it
(`tests/acceptance/test_verify_lists_the_obligations_owed.py:320`).

## The rest

**D16 formal model.** Not needed, and the reason is in `craft.md`: the
inventory has no state, no protocol and no concurrency.

**D17 honest documents.** Every number in these documents comes from a run
recorded in the same delivery. The one behaviour the request asks for and this
delivery does not carry is named in `oracle.md`, with the three tests that
contradict it and the question for the Owner.

## What I did not do

I did not review this change for the Owner. An independent reviewer still has
to, and the question in `oracle.md` is still unanswered.
