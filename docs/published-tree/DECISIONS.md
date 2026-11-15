# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 1)

- **decisions**:
  - S33: put to the owner before any code lands; my recommendation is that the single expectation pinning parse as unavailable in tests/unit/test_service_discover.py be updated to "available" as part of this delivery, because criterion 5 of the request outranks a compatibility expectation that only records what was unbuilt; recorded as asked, not as settled.
  - DEC1: the published tree is the typed tree the tool already builds, written as JSON nodes that each carry a "kind" and a "position"; a declaration, a signature, a parameter, a field, an example, every expression, every pattern and every comment is a node, and the kinds are published by the manifest.
  - DEC2: a comment is published with the characters it was written with, from its ";" to the end of its line, so that a later formatter can write it back unchanged rather than guess the spacing a reader chose.
  - DEC3: a comment attaches to the first node, in the order the tree is walked outermost first, whose place is after the comment; a comment that no node follows is published at the end of the document, on the program node.
  - DEC4: reading a program is an operation that reads source, so it reads the "source" field through the one request reader, refuses a value that is not a text by name, and carries the claim and the source revision its siblings carry.
  - DEC5: no formal model (Quint) pays here: reading a program holds no state between requests, has no protocol of several steps, runs nothing concurrently and writes nothing, so there is no state space a model would explore.
  - DEC6: a field keeps the (name, type) pair the typed tree has today, because an existing test pins that shape by equality; the place of a field node is read from the table of declared names the program already owns, so nothing is counted twice.
  - DEC7: typesafe: unavailable: TYPESAFE_API_KEY is absent from this environment, so the two open questions (which parts are nodes, and how a comment attaches) were settled locally and recorded as DEC1, DEC3 and DEC6.

## design (revision 1)

- **reuse_decision**: Reused: the reader for the forms and their places, the typed tree for the structure, the shared rule in service.py that refuses a source every operation refuses the same way, the table of declared names for the place of a field, values.render for the text of an example value, and the manifest for publishing. Created new: src/prova/tree.py, which owns the published node kinds, the attachment of a comment and the schema the manifest publishes. No existing owner fits: syntax.py owns the tree the checker walks and must not learn a wire format, and service.py owns operations and answers, not the shape of a tree. reader.py gains the comments it already meets and today throws away, because it is the only place that reads characters.
- **prefactoring_reason**: The typed tree keeps a declared parameter and a let binding as bare pairs of strings, and its declarations, signatures, examples, match clauses and patterns carry no place at all. Publishing a tree needs a place on each of them and needs a parameter and a binding to be able to carry one, so the pairs become value objects and the places are filled first, in commits that change no answer the tool gives and edit no test. A field keeps its pair, because an existing test pins that shape by equality; its place is read from the table of declared names instead.
