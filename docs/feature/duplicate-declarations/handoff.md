# F3 handoff

## What a reader gets

Ask the tool to check a program that declares the same function, type,
constructor or field twice, or that declares a type called `Int`, `Bool` or
`Unit`, and it refuses the program. The refusal names the symbol, says which
uniqueness rule it breaks, names every place the symbol was declared as a line
and a column, and says to remove or rename all but one of them. It arrives in
the category `duplicate_declaration`, which `discover` publishes, so a caller
can learn the name before meeting it.

Two different records may still each have a field spelled the same. A field is
unique only within its own record or variant.

## How it was checked

Every new test was seen failing on the tree as it was before the feature, and
the full suite is green after it. The added test files were run nine times in
a row with no failure.

## What was not verified

- No independent review and no blind examination have happened; nothing here
  is an independent verdict.
- The repository declares no lint or type checker, so the mechanical check run
  here is a compile of the sources and tests, not a style or type verdict.
- Jev was unavailable, so no second opinion was obtained on any choice.
- After this change, no accepted program reaches the record-over-variant
  branch of `syntax.resolve_constructor`. The test that guards it now calls
  that lookup directly, so the branch is covered but no longer reachable
  through the tool. The follow-up sits with the Owner.
- The rule reads the declarations of one program in one process. Nothing was
  measured about very large programs, and no limit is enforced on how many
  declarations a program may carry.
