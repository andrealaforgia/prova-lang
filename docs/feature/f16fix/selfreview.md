# F16fix - my own review of this change

Seventeen questions are asked of every delivery. This one adds tests to three
parts of the inventory that nothing was reading, and moves one rule in the
product itself.

## Design and code

**D1 architecture.** The one production change keeps the shape that was there:
the walk over a body already carried a condition down, and it now starts from
the function's own precondition instead of from nothing. No new collaborator,
no new layer, no new file.

**D2 one source of truth.** The condition a site is reached under is decided in
one place, `_precondition_of`, and read by the two call sites that need it. The
expected answer in the tests is still derived once, from the plan the property
tests write.

**D3 boundaries.** The property tests and the acceptance tests drive the
`prova` command over its JSON surface and import nothing from `src/prova`.

**D4 wrong states unrepresentable.** `PathCondition` stays the only way a
condition is carried, and it is extended, never replaced, so a condition cannot
lose the clauses already in front of it. `BODY_SHAPES` holds a call position
and its condition as one entry, so a position cannot be planned without the
condition that reaches it.

**D5 small and cohesive.** `_precondition_of` answers one question and says in
its own words why a `requires` site is not seeded. The plan's helpers each
answer one question: which identities are owed, which conditions, how many
calls.

**D6 patterns.** Nothing new. The walk is the same recursive descent it was.

**D7 domain-driven design.** The names are the language of the specification -
precondition, postcondition, path condition, the condition that reaches a call
- and the rule lives beside the type that carries it.

**D8 infrastructure.** None is involved: the operation reads no file, opens no
socket and spawns nothing.

## Tests

**D9 public interface only.** Every new assertion reads the answer the `prova`
command prints. No production symbol is imported and no internal is named.

**D10 naming.** The new tests are named for what the Owner is owed: a call in
every position a body can hold owes its entry; a call behind several conditions
is owed under all of them; a call in a contract or a body is owed under the
function's own precondition.

**D11 helpers.** The new tests reuse the plan, the renderer and the runner
already in those files and add no parallel machinery.

**D12 generated tests.** The generated plan draws from all nine call positions
and now derives the expected condition from the plan's own precondition, so the
law holds for a generated function with a contract as well as without one.
Because a run draws only some positions, a fixed program holds every position
at once.

**D13 speed.** Measured, not guessed; the numbers are in `craft.md`. These
tests start a process each, so they are integration tests, measured in seconds.
None of them sleeps or reads a clock.

**D14 duplication.** The two acceptance tests on the nested program read it for
two different questions - the conditions, and the call counts - so a failure
names which of the two the tool got wrong.

**D15 failure messages.** Each new assertion says what was found, why it is
owed and prints the program that produced it.

## The rest

**D16 formal model.** Not needed: the inventory keeps no state, runs no
protocol and has no concurrency. It is a pure function from one syntax tree to
one list, so a model would restate the code.

**D17 honest documents.** Every number in these documents comes from a run
recorded in this delivery. The three tests whose expected text changed are
named, with the Owner decision that allowed it.

## What this change does not prove

- That the seeded condition is the one a solver would need. Nothing here
  attempts an obligation; the inventory still says every entry is
  `not_attempted`.
- That no deletion other than the ten re-run here would go unnoticed.
- I did not review this change for the Owner. An independent reviewer still
  has to.
