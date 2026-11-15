# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 2)

- **decisions**:
  - S30: applied, after the conflict was reported. It fails 3 existing tests (measured, whole suite: 3 failed, 1007 passed), so the question went to the Owner, who decided that those 3 may be rewritten to the new text and nothing else in them. They were changed in their own commit, which is red on its own and says so, and the rule landed in the commit after it with the chain case the request asks for.
  - DEC1: no formal model, no Quint. The inventory keeps no state, runs no protocol, spawns nothing and writes no file; it is a pure function from one syntax tree to one list.
  - DEC2: findings 1 to 3 are gaps in the oracle, not defects: the walk over a body already visited every position, so they are closed by tests alone. Finding 4 is a defect and moves src/prova/obligations.py.
  - DEC5: the 3 rewritten tests are committed on their own, before the rule, so that what each one now states can be read without the code that satisfies it. That commit is red by itself and its message says so.
  - DEC3: the ten deletions are applied and restored by a script kept under the nwstep workspace and never committed; after each run src/prova/obligations.py is byte-identical to its committed form.
  - DEC4: typesafe unavailable: TYPESAFE_API_KEY is absent from this environment and the client exits 3, so the conflict decision was taken locally from a measured whole-suite run.
