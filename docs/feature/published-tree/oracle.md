# F12 oracle: what the tool must promise about the tree it answers

## What this step decided

The request asks that `parse` answer the tree the compiler actually built,
under a schema an agent can read. Seven promises were written from it:

| Promise | In plain words |
|---|---|
| P1 | A valid program is answered with its tree, and every node says where it stands. |
| P2 | A comment is answered on the node that follows it, or at the end of the document. |
| P3 | A program that breaks a rule is refused exactly as `check` refuses it, with no tree. |
| P4 | The tree of the reservation example holds every declaration, contract clause and example. |
| P5 | The manifest advertises reading a program, and publishes the schema of the tree. |
| P6 | The schema is fixed in conformance fixtures: each source published beside its tree. |
| P7 | Reading a program answers like the operations beside it: one claim, the source revision, and the request reader refusing a source that is not text. |

Eleven scenarios were written with concrete data, and every sentence of
the request was mapped to a promise or to a reason it states a process
rule rather than a behaviour.

## What was built

Seven new test files, all seen failing before any code exists:

- six acceptance files (`tests/acceptance/test_f12_b1...b6`), one per
  promise group, asking the service through its public operation;
- one property file (`tests/properties/test_f12_published_tree_laws.py`)
  holding the three laws: every node stands at a real place; every comment
  is answered exactly once on the first node after it; a tree is published
  exactly when a check of the same source completes;
- two published pairs under `conformance/parse/`, each a source and the
  tree it must be answered with, written by hand from the schema.

The recorded RED run lists 25 failing tests on the tree as it was before
this work.

## Decisions taken here

- **The schema (D7 was delegated).** The published tree is the typed tree
  the compiler already builds, written as JSON. Every node carries a
  `kind` and a `position`. Declarations, signatures, parameters, fields,
  examples, expressions, patterns and comments are all nodes.
- **Comments keep their characters**, from the `;` to the end of the line,
  so a later formatter can write them back unchanged.
- **Attachment rule.** A comment belongs to the first node, reading the
  tree outermost first, that stands after it; a comment no node follows is
  answered at the end of the document.
- **No formal model (Quint).** Reading a program keeps no state between
  requests, has no protocol and writes nothing, so there is no state space
  to explore.
- **Jev was not reachable** (`TYPESAFE_API_KEY` absent), so the two open
  design questions were settled locally and written down above.

## What is still open

One conflict with an existing test. `tests/unit/test_service_discover.py`
pins the whole table of operations by equality, including
`"parse": "unavailable"`. Criterion 5 of the request requires `parse` to be
advertised as available. The request forbids editing an existing test's
expected result, so this is the owner's call, asked at this pause.
