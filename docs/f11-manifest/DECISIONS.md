# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 1)

- **decisions**:
  - S28: The types and operators are published under the key language, holding types and operators, and the words builtin and builtins are kept out of the discover answer. The existing no-claim test is left exactly as it is, acceptance criterion 3 is met in full, and the owner is asked at the pause whether the name language is the one an agent should read.
  - DEC1: The operation list that discover already carries keeps its exact shape, a name to the word available or unavailable, because tests/unit/test_service_discover.py compares it with equality. The categories, the shapes and the language are published beside it as new parts of the manifest.
  - DEC2: The source field is published as optional, because a request without it is answered today as a program with nothing in it. Publishing it as required would make the tool refuse requests it answers today and turn existing tests red. Acceptance criterion 4 is read as being about the kind of value a published field carries.
  - DEC3: Request and answer shapes are published only for the operations advertised as available. An operation that is refused has no shape fixed yet, and publishing one would promise a request nobody can send.
  - DEC4: The operation field itself is not one of the per operation request fields. A request whose operation field carries another kind of value names no operation at all and is answered unavailable with unknown_operation, which is the existing behaviour and is not a refusal of a field of a known operation.

## design (revision 1)

- **reuse_decision**: Reused: the request reader, the diagnostic kinds and their published shapes, the contract report publisher and the two operation tuples of the dispatcher, all unchanged. Extended: the operator table and the type names of checker.py, which already own what an operator takes and which types exist; the argument and result types belong there and nowhere else, so no second table decides them. Created new: src/prova/manifest.py, for the catalogue of operations with their categories and their request and answer shapes. No existing module owns that question: the dispatcher owns which names exist and the checker owns the language, and neither knows what a request for an operation looks like. The new module also keeps the diff of service.py to one import and three keys, which the parallel delivery on the dispatch needs.
- **prefactoring_reason**: The operator table carries a number of arguments and the name of a group today, and the operand rules stand in a chain of four branches that reads that group name. Publishing the argument and result types from a second table would make two units decide one fact, so first the table learns its operand rule and its result type as an object, and the four branches are replaced by asking that object. The type names are restated the same way, as one table of entries that keeps BUILTIN_TYPES as the set of their names. Behaviour is unchanged: every refusal keeps its category, its sentence, the place it stands at and the two types it names, the group names and the four sets stay exactly as the existing table test reads them, and no test is edited.
