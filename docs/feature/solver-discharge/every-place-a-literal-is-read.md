# Every place the encoder reads or writes a literal, and what watches it

Three review rounds each found one more place where a literal's sign or
magnitude could be mangled with nothing noticing. This table exists so
that the next one is a lookup rather than a discovery: it lists every
place in `src/prova/encoding.py` and `src/prova/solving.py` that reads a
literal value, a sign or a boolean, with the test cell that observes it.

The grid in `tests/properties/test_f18_a_literal_keeps_its_value_everywhere.py`
crosses 16 values — nothing, one and two either way, the edges of a
32-bit and a 64-bit word from both sides, past an unsigned 64-bit word,
and 30 digits either way — with 19 positions, and every cell is a
program whose promise sits exactly at the boundary the literal sets.
304 cells, under two seconds, no sampling.

| Place in the code | What it reads | Cell that observes it |
|---|---|---|
| `encoding.Translation._integer` → `Term.integer` | every integer literal of an expression | all 304 cells; a value read wrongly breaks the boundary |
| `encoding.Translation._boolean` → `truth`/`falsity` | `true` and `false` in an expression | the boolean-clause position, and the promise about a boolean |
| `encoding.Translation._unit` → `unit` | `()` | none: no program in the oracle has a `Unit`-typed expression, and the profile's `Unit` has one value, so no cell could tell a right reading from a wrong one. Stated, not claimed |
| `encoding.Translation._operator` rows `<` `<=` `>` `>=` | a literal on either side of each of the four orders | eight positions: each order with the literal left and right |
| `encoding.Translation._operator` row `=` | a literal on either side of an equality | the equality position, and the negative literal in an equality |
| `encoding.Translation._operator` rows `and` `or` `not` | a literal inside a connective of a promise | the and-or-inside-a-promise position; `not` by the negated-condition tests |
| `encoding.Translation._operator` rows `+` `-` | a literal as either operand | the sum position and both difference positions |
| `encoding.Translation._product` | a literal factor, and the refusal when neither operand is one | both factor positions; the out-of-fragment law for the refusal |
| `encoding.Translation._matched` `PatInt` | a literal as a match pattern | the first-clause and middle-clause positions, and the negative literal as a pattern |
| `encoding.Translation._matched` `PatBool` | `true`/`false` as a match pattern | the boolean-clause position |
| `encoding.Translation._matched` `PatUnit` / `PatConstructor` | the unit pattern and a nullary constructor pattern | constructor patterns by the two shipped examples and the clause tests; the unit pattern has no cell, for the reason above |
| `encoding.Translation._construction` → `shape` | a literal as the value of a record field or a union payload | the record-field position; a union payload carries no literal in this fragment's programs |
| `encoding.Translation._expanded_call` → `_arguments_of` | a literal inside the argument of a call | the call-argument position |
| `encoding.Translation.term_of_value` | the literal arguments and expected value of a declared example | the expected-value position, and every cell's own example |
| `solving` row `INTEGER` → `IntVal` | the value handed to the solver | all 304 cells |
| `solving` row `TRUTH`/`FALSITY` → `BoolVal` | the boolean handed to the solver | the boolean-clause position |
| `solving` rows `SUM` `DIFFERENCE` `PRODUCT` | the arithmetic the solver is given | the sum, difference and factor positions |
| `solving` rows `LESS` `AT_MOST` `GREATER` `AT_LEAST` `EQUALS` | the comparison the solver is given | the eight order positions and the equality position |
| `solving` rows `CONJUNCTION` `DISJUNCTION` `NEGATION` `CONDITIONAL` | the connectives and the choice | the and-or position, the negated-condition tests, every match cell |
| `solving._written` integer branch | a number read back out of a solution | every disproved case: the witness is asserted to be the one value that breaks the promise |
| `solving._written` boolean branch | a boolean read back out of a solution | the promise about a boolean, whose witness is `false` |
| `solving._written` constructor branch | a record or variant read back out of a solution | the hour clock with its wrap removed, whose witness is a `Clock` |
| `solving._written` unit branch | `()` read back out of a solution | none: no program here has a `Unit` parameter, so no solution assigns one |

## What this table does not do

It says which cell would notice a place being read wrongly. It does not
say the reading is correct: that rests on the cells, on the differential
check against the evaluator inside each of them, and on the mutants put
back one at a time. Three places are named as having no cell, with the
reason; they are not counted as covered.
