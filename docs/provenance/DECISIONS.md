# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 1)

- **decisions**:
  - S22: Carry the provenance block on the 6 operations the profile names (check, verify, examples, parse, format, discover) and leave the evaluate answer exactly as it is, because the pinned transcript test is an accepted guard this delivery may not edit; the gap is reported to the owner and written in the documents.
  - S25: Name the 4 versions in that same block, so the versions reach the same 6 operations and evaluate keeps the answer it has today; the owner is asked the same question once.
  - DEC1: A failure of this tool is answered by the one place that turns an answer into the text the command prints, with status tool_failure, and tool_failure stays out of the published statuses of an answered request, which the manifest already explains.
  - DEC2: The dependency digest is the SHA-256 of the canonical JSON of the profile, the published language and the 4 versions, published by discover so a client can compare a kept answer with this tool.
  - DEC3: An obligation keeps result as its logical standing and gains execution_status, whose word unsupported comes from the execution vocabulary of SPEC.md lines 270-284, because this tool has no solver.
  - DEC4: No formal model (Quint): this change adds no state, no protocol, no concurrency and no crash behaviour; every answer stays one function of one request, so a model would restate the code.
  - DEC5: Jev was not asked: TYPESAFE_API_KEY is absent from this environment and from a login shell, so the client exits 3; every choice below was settled locally and is recorded here.
  - DEC6: A failure of the tool is observed through the public entry point the command calls, because no input of the command can make the tool fail inside itself without planting a defect; the limit is written in the documents.
  - DEC7: The published scope of an examples run stays the words it has today, and the test proves the scope is really only the declared examples by counting the entries against the examples the sent text declares.

## design (revision 1)

- **reuse_decision**: Reused: the manifest field vocabulary (when completed), the one builder of a refusal, SourceRevision, the obligation entry and the statuses table; every one of them is extended where it already stands. Created new: src/prova/provenance.py, because no module owns what this tool is made of -- its own version, the interpreter under it, the absence of a solver and an encoder, and the digest over its published language; putting that in service.py would make the dispatcher decide facts about the tool, and putting it in manifest.py would make the catalogue of operations read the environment. The new module also takes over the SHA-256 of a text, which service.SourceRevision keeps using, so one place writes that algorithm.
- **prefactoring_reason**: One commit before the feature moves the SHA-256 of a text out of service.SourceRevision into the new provenance.Digest, with SourceRevision delegating to it. Behaviour is unchanged: the same algorithm over the same characters, the same hexadecimal rendered, no test edited and no answer field added. It comes first because the feature hashes a second thing, this tool own description, and without the move the algorithm would be written twice.
