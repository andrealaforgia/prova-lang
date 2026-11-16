# Every place the encoder reads or writes a literal, and what watches it

Three review rounds each found one more place where a literal's sign or
magnitude could be mangled with nothing noticing. This table exists so
that the next one is a lookup rather than a discovery: it lists every
place in `src/prova/encoding.py` and `src/prova/solving.py` that reads a
literal value, a sign or a boolean, with the test cell that observes it.

The grid in `tests/properties/test_f18_a_literal_keeps_its_value_everywhere.py`
crosses 16 values — nothing, one and two either way, the edges of a
32-bit and a 64-bit word from both sides, past an unsigned 64-bit word,
and 30 digits either way — with 27 positions, and every cell is a
program whose promise sits exactly at the boundary the literal sets.
432 cells, under a second, no sampling.

| Place in the code | What it reads | Cell that observes it |
|---|---|---|
| `encoding.Translation._integer` → `Term.integer` | every integer literal of an expression | all 432 cells; a value read wrongly breaks the boundary |
| `encoding.Translation._boolean` → `truth`/`falsity` | `true` and `false` written in an expression | two positions write them in both polarities, each promised against the test they stand for rather than against themselves, so swapping the two cannot cancel; the boolean-clause position and the promise about a boolean observe them too |
| `encoding.Term.all_of` with no parts → `truth()` | a contract clause list that is empty | 96 cells, whose functions declare no precondition, so the empty conjunction is what is assumed |
| `encoding.Translation._unit` → `unit` | `()` written in an expression | the unit-pattern position builds a `Unit`-typed function and its declared example sends `()`, so the value is read; the profile's `Unit` has one value, so a wrong reading of it can only be a failure to build the term, which that cell would show |
| `encoding.Translation._operator` rows `<` `<=` `>` `>=` | a literal on either side of each of the four orders | eight positions: each order with the literal left and right |
| `encoding.Translation._operator` row `=` | a literal on either side of an equality | the equality position, and the negative literal in an equality |
| `encoding.Translation._operator` rows `and` `or` `not` | a literal inside a connective of a promise | the and-or-inside-a-promise position; `not` by the negated-condition tests |
| `encoding.Translation._operator` rows `+` `-` | a literal as either operand | the sum position and both difference positions |
| `encoding.Translation._product` | a literal factor, and the refusal when neither operand is one | both factor positions; the out-of-fragment law for the refusal |
| `encoding.Translation._matched` `PatInt` | a literal as a match pattern | the first-clause and middle-clause positions, and the negative literal as a pattern |
| `encoding.Translation._matched` `PatBool` | `true`/`false` as a match pattern | the boolean-clause position |
| `encoding.Translation._matched` `PatWildcard` / `PatVar` / `PatUnit` → `truth()` | the three patterns that always match | five positions put one in a non-final clause -- a wildcard and a name in a first and in a middle clause, and the unit pattern in a first clause -- with a literal clause after it and the promise pinned to the first clause's answer, so a pattern that always matches read as one that never does answers the later clause instead; and three acceptance cases disprove the promise only a later clause would keep |
| `encoding.Translation._matched` `PatConstructor` | a nullary constructor pattern | the two shipped examples and the clause tests |
| `encoding.Translation._construction` → `shape` | a literal as the value of a record field or a union payload | the record-field position, which pins the field against the same number written another way. It is one site for both shapes: a union payload is constructible here and is settled the same way, through the same line |
| `encoding.Translation._expanded_call` → `_arguments_of` | a literal inside the argument of a call, and a literal as the whole argument | the two call-argument positions; the second pins what comes back against the same number written another way, because the first could not notice a sign dropped there |
| `encoding.Translation.term_of_value` | the literal arguments and expected value of a declared example | the expected-value position, and every cell's own example |
| `solving` row `INTEGER` → `IntVal` | the value handed to the solver | all 432 cells |
| `solving` row `TRUTH`/`FALSITY` → `BoolVal` | the boolean handed to the solver | the boolean-clause position |
| `solving` rows `SUM` `DIFFERENCE` `PRODUCT` | the arithmetic the solver is given | the sum, difference and factor positions |
| `solving` rows `LESS` `AT_MOST` `GREATER` `AT_LEAST` `EQUALS` | the comparison the solver is given | the eight order positions and the equality position |
| `solving` rows `CONJUNCTION` `DISJUNCTION` `NEGATION` `CONDITIONAL` | the connectives and the choice | the and-or position, the negated-condition tests, every match cell |
| `solving._written` integer branch | a number read back out of a solution | every disproved case: the witness is asserted to be the one value that breaks the promise |
| `solving._written` boolean branch | a boolean read back out of a solution | the promise about a boolean, whose witness is `false` |
| `solving._written` constructor branch | a record or variant read back out of a solution | the hour clock with its wrap removed, whose witness is a `Clock` |
| `solving._written` unit branch | `()` read back out of a solution | the unit-pattern acceptance case, whose witness is `()`. The branch is reachable, and a broken one could only lose a disproof rather than invent one |

## What this table does not do

It says which cell would notice a place being read wrongly. It does not
say the reading is correct: that rests on the cells, on the differential
check against the evaluator inside each of them, and on the mutants put
back one at a time, each run against the one cell this table names for
it.

Every site now has a cell. The earlier claim that three had none was
wrong twice over: it named a site that does have one, and it missed the
site that really had none -- the three patterns that always match, which
nothing put in a non-final clause.

## Two cells this table made stronger

Writing the table found two of its own rows watched by a cell that could
not have noticed: the record field and the call argument were pinned
against a bound a mangled value still satisfied. Both now pin the value
against the same number written another way, and a mutant dropping the
sign in either place turns them red. That is what the table is for.

## What the table got wrong, and what that cost

A structural check of this table, not of the code, found four things.
One site was missing altogether: the three patterns that always match,
read as a constant, which no cell put anywhere but the last clause --
and a mutant reading that constant as its opposite gave a `proved` the
evaluator contradicts. One row named cells that did not observe it: the
`true` and `false` of an expression were written on both sides of every
promise that mentioned them, so swapping the two cancelled out. One row
was missing for the empty conjunction. And two of the three no-cell
reasons were simply untrue: a union payload and a `Unit` parameter are
both constructible, and both are reached.

The lesson is the one this table was written for, turned on itself: a
place is covered when a mutant at that place turns a named cell red,
not when a table says it is.
