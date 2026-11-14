# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 2)

- **decisions**:
  - DEC1: the refusal gets its own category recursive_type instead of reusing cyclic_dependency, because the subject (declared data types, not functions), the repair (wait for a later profile, not remove a call) and the published F2 law (cyclic_dependency means the call graph) differ, and a consumer filters by category; service.py grows by 1 name, the smallest edit that keeps the two apart.
  - DEC2: when a type cycle is found the function checks do not run, and the refusal says so. Measured on the pre-feature tree: a recursive union read by a match ends in RecursionError, because match coverage and value shape checks follow the fields of a type and are defined only on acyclic types.
  - DEC3: the refusal carries no line and column, mirroring the F2 cycle diagnostic, because a cycle spans several declarations; the machine-readable cycle member list carries the names instead.
  - DEC4: no formal model (Quint) is written: the rule is a pure function of the program text with no state, protocol, concurrency or crash-recovery question in it.
  - DEC5: the owner is absent for this run, so DEC1 to DEC4 are my own decisions, recorded here and in the brief for review.
