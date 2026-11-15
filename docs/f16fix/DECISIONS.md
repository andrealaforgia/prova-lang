# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 1)

- **decisions**:
  - S30: not applied. Applying it fails 3 existing tests (measured, whole suite: 3 failed, 1007 passed), and the request forbids editing an existing test's expected result and tells me to stop and report. Findings 1 to 3 are delivered; finding 4 goes back to the owner with the measurement.
  - DEC1: no formal model, no Quint. The inventory keeps no state, runs no protocol, spawns nothing and writes no file; it is a pure function from one syntax tree to one list.
  - DEC2: no production code is changed. Findings 1 to 3 are gaps in the oracle, not defects: the walk over a body already visits every position, so this delivery is tests and documents only.
  - DEC3: the nine deletions are applied and restored by a script kept under the nwstep workspace and never committed; after each run src/prova/obligations.py is byte-identical to its committed form.
  - DEC4: typesafe unavailable: TYPESAFE_API_KEY is absent from this environment and the client exits 3, so the conflict decision was taken locally from a measured whole-suite run.
