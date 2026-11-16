# F18 — the refactor: two moves after green

Both are behaviour-preserving, each in its own commit, with the same
check green on the parent and on each of them. No test file was touched.

## One place spells each word two units compare

Three literals were spelled in two modules at once. The word for an
obligation nobody attempted was declared both where a program's
obligations are listed and where they are settled, so the entry carrying
it and the count reading it could have drifted apart. The four words
naming which refusal confirms a candidate counterexample were declared
as bare strings on the obligation kinds and compared as bare strings
where a candidate is replayed.

Each now has one owner, beside the kinds that carry it. A method nothing
called went with them, and so did the word for an attempt nothing
supported, which no entry has written since every one of them says what
became of it.

## Every primitive is built from one table

How a term became a term of the solver was decided in two places: eight
primitives in a chain of tests inside the method, and twelve in a table
beside it. A primitive the translation declares and the adapter cannot
build was then a case missing from a chain, which reads as working code.
One table now holds one row per primitive, and a primitive with no row
refuses by name and says which table to add it to.

## One deliberate break, with its cost

The rows of that table read three things from the question they are
handed, which breaks the rule against getters. It was taken because the
unit is the solver adapter, which the design rules exempt. The cost is
that the rows reach into the question rather than being told; the
benefit is one place deciding how every primitive is built.

## What needed no refactor

Eleven other changed units, each with its reason in the step record:

| Unit | Why none was needed |
|---|---|
| `encoding.Translation` | one method per kind of expression, each 1 to 6 lines, dispatched once |
| `encoding.Term` | a value with named constructors and no behaviour to move |
| `encoding.published_primitives` | the one declaration the manifest and the document both read |
| `solving._Sorts` | one responsibility: the types of one claim in the solver's terms |
| `solving.PinnedZ3` | the port itself: three small methods, each loading the solver inside the call that needs it |
| `discharge.ValidatedWitness` | a value built in one place, by the replay that confirmed it |
| `obligations.Inventory` | one responsibility, and its refusal of an obligation with no finding is the rule that nothing is skipped |
| `obligations.PathCondition` | prepared before the feature, in its own commit |
| `provenance.SolverStanding` | two constructors and four small readers, refusing the state that names a solver and a reason at once |
| `budgets.Run` | one method added, one line |
| `budgets.Budgets` | one method added, one line |
