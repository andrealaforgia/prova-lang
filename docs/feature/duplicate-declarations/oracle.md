# F3 oracle: a name is never declared twice

## What this feature promises

A program that declares the same function, type, constructor or field twice is
refused, instead of quietly keeping the last declaration. The refusal names the
symbol and every place it was declared. Redeclaring `Int`, `Bool` or `Unit` is
refused too. Two different records may each have a field spelled `amount`.

## The tests that state it

One test per criterion, each driving the real `prova` command over JSON on
standard input and output:

| Criterion | Test file |
|---|---|
| two functions with one name | `tests/acceptance/test_f3_b1_two_functions_with_one_name_are_refused.py` |
| two types with one name | `tests/acceptance/test_f3_b2_two_types_with_one_name_are_refused.py` |
| one constructor from two types | `tests/acceptance/test_f3_b3_one_constructor_from_two_types_is_refused.py` |
| one field spelled twice | `tests/acceptance/test_f3_b4_a_field_spelled_twice_is_refused.py` |
| a redeclared builtin type | `tests/acceptance/test_f3_b5_redeclaring_a_builtin_type_is_refused.py` |
| each name declared once | `tests/acceptance/test_f3_b6_programs_that_declare_each_name_once_are_accepted.py` |
| the published category | `tests/acceptance/test_f3_b7_the_manifest_publishes_the_new_category.py` |
| the law over every shape | `tests/properties/test_f3_duplicate_declarations.py` |

No test spells a line number out. Each reads the places its own fixture text
declares the symbol at, so a change to a fixture cannot leave a stale
expectation behind.

Every one of these tests was seen failing on the tree as it was before the
feature; the run is recorded in the workspace journal.

## What was decided, and why

- **The category is `duplicate_declaration`**, as the request suggested. One
  name covers functions, types, constructors, fields and redeclared builtins,
  which keeps the vocabulary a caller must learn small. `discover` publishes it.
- **Both places are named inside the reason text**, as `line L column C`. A
  diagnostic carries a single location field, and the request limits the
  service change to adding one category name, so the reason is where both
  places fit. The single location field points at the later declaration, the
  one a reader removes.
- **One repeat is reported once.** A record declares a type and a constructor
  of the same name at the same place, so declaring one record twice collides in
  two namespaces at the identical two places. That is one defect with one
  repair.
- **No formal model.** The rule reads one list of declarations and answers; it
  holds no state, speaks no protocol and runs nothing concurrently.
- **Jev was unavailable** (`TYPESAFE_API_KEY` absent, the client exited 3), so
  every decision here was taken locally.

## The two conflicts

Both were found by reading the code and running the suite, and both were
decided by the Owner.

1. **Request sentence S3** says no existing test's expected result may change.
   Acceptance criterion 3 cannot hold at the same time: an existing unit test
   pinned a program that declares one constructor name twice as accepted.
   **Owner decision: change that one superseded expected result.** SPEC.md
   lines 137-143 and the acceptance criteria are the authority for what the
   tool refuses.
2. **Acceptance criterion 3** against `resolve_constructor`, which prefers a
   record over a union variant of the same name. **Owner decision: refuse such
   a program**, as the criterion and SPEC.md say. The superseded test now
   observes that refusal, and the resolution rule it used to guard is pinned
   directly on the lookup that owns it.

## Still open

Nothing in the oracle. The consequence of conflict 2 is recorded in
`craft.md`: after this change no accepted program reaches the
record-over-variant branch of `resolve_constructor`.
