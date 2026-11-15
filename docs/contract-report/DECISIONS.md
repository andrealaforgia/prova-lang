# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 1)

- **decisions**:
  - DEC1: the report is carried by the answer of check and by no other operation. check is the answer whose completed status a reader can mistake for a meaningful result, the criteria say when the program is checked, and the verify answer already states that nothing was attempted. The owner is absent, so this is the executor decision.
  - DEC2: a block whose every clause is the literal true is recorded trivial, and a block holding one clause that is not the literal true is recorded stated, because SPEC.md reads the clauses of a block as a conjunction and a conjunction with one real clause promises that clause.
  - DEC3: an empty block written as (requires) is recorded omitted, because the parsed program keeps no mark that tells it from an absent block; this limit is written in the documents.
  - DEC4: triviality is recognised only for the literal true, as SPEC.md asks for explicitly trivial contracts; a clause such as (or p (not p)) is recorded stated and that limit is written in the documents.
