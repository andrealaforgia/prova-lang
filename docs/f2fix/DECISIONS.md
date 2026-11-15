# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 1)

- **decisions**:
  - S25: Annotate defect 2 as fixed by F3, and defect 3 as fixed by F3, F4 and F5, naming which clause each feature closed. The owner is absent, so this is my decision: writing F3 alone over all 7 clauses of defect 3 would put a false claim in the record, and the request asks for the record of a closed gap, not for a particular feature name.
  - DEC1: No formal model. This change adds no state machine, protocol, concurrency or crash behaviour; the one law over a broad domain already has a generated property, so a Quint model would restate the test.
  - DEC2: The 4-function shapes are pinned as fixed examples on the existing property, because the generator draws at most 3 functions and could never reach them; the 3-function shapes are pinned as acceptance tests through the real command, where the order of the names is observable. The example budget stays at 60.
  - DEC3: The order of the names also became a generated property, not only 2 fixed examples, because it is a law over every program the generator draws.
  - DEC4: The RED run applies the 2 surviving mutants together, because each of them kills only part of the tests this change adds: the first one changes which functions are named, the second one changes only their order.
