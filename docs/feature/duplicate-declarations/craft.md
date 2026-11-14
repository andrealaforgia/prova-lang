# F3 craft: where the rule lives

## What was built

A repeated declaration used to disappear before any check could see it: the
program keeps one entry per name, so a later declaration replaced the earlier
one. Two changes fix that.

1. **The parser also keeps the declared names in source order.** Each one says
   what kind of thing it names (function, type, constructor, field), which
   record or variant it belongs to, and the line and column it stands at. A
   declared name with no spelling cannot be built: a refusal carrying it would
   not tell the reader which name to repair.
2. **The checker reads that list first.** A name declared twice in one scope,
   and a type named after a builtin, each produce one refusal in the new
   `duplicate_declaration` category, naming the symbol, every place and the
   repair.

The service change is one line: the new category name joins the list
`discover` publishes. No obligation or verify code was touched.

Fields are scoped to their own record or variant, so two records that each have
a field spelled `amount` stay accepted. That is the one case the accepted-side
test guards, and it differs there from the same spelling repeated inside one
record.

## Commits

- A behaviour-preserving prefactor first: the "a, b and c" wording that cycle
  refusals build moved into a helper beside them, so the new refusal does not
  spell the same join a second time. No test was edited in it.
- Then the feature itself, with its tests.

## The existing test that changed

`tests/unit/test_evaluator_field_access.py` pinned a program in which a record
and a union variant are both called `Marker` as accepted, and its `.tag`
selection as evaluating to `7`. SPEC.md lines 137-143 require constructor names
to be unique across the whole program, so that program is now refused. The
Owner decided to keep the rewritten expectation: the test now observes the
refusal, and a second test pins the record-over-variant resolution directly on
the lookup that owns it.

Honest consequence: after F3 no accepted program can reach the
record-over-variant branch of `syntax.resolve_constructor`, so that direct test
guards a branch that is unreachable through the tool. The Owner has put the
follow-up on the roadmap; this delivery does not touch it.

## How it was checked

- Every new test was seen failing on the pre-feature tree before the code
  existed; that run is recorded in the workspace journal.
- The full suite is green after the change.
- Test cost receipt: the added test files were run nine times in a row, 17
  tests each time, all passing. Median 0.56 s for the whole set, slowest run
  0.59 s, slowest single test 0.06 s (an acceptance test that runs the command
  twice). No test sleeps or reads a clock.
- Jev was unavailable (`TYPESAFE_API_KEY` absent, client exit 3).

## Still open

Nothing in this step. What was not verified is listed in `handoff.md`.
