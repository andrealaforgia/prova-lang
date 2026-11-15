# F12 craft: reading a program, and what a review found in it

## What was built

Reading a program is answered now. `src/prova/tree.py` owns the published
tree and the schema; `src/prova/reader.py` keeps the comments it used to
drop; `src/prova/syntax.py` carries a place on every part of the typed
tree; `src/prova/service.py` answers the operation and publishes the
schema in its manifest.

Two commits came first and changed no answer the tool gives: one turned a
declared parameter and a `let` binding into value objects carrying their
place, the other took away the default place, so a part of a read program
that cannot say where it stands can no longer be built at all.

## What the review found, and what was done

| # | Finding | What was done |
|---|---|---|
| F1 | Two comments at the end of a document were published twice. | The comments left over are given up when the walk ends. A test with two trailing comments fails on the old behaviour; the law about comments now reaches that case too and fails on it as well. |
| F2 | The "exactly once" promise was never observed at the document end. | An example test with two trailing comments, and the law now writes none to several comments anywhere, including after everything the program declares. |
| F3 | Six published node kinds were never exercised, so their place, their entry and their name were unchecked. | A program written to use every part of core-0 is read, and the published kinds and the answered kinds are compared in both directions. Three mutants that survived before now fail. |
| F4 | The schema said every node stands where its form opens, which is untrue of a field and a parameter. | The schema says they stand at the name they declare. The behaviour is unchanged. |
| F5 | A placeless node was constructible and failed only when published. | The default place is gone from the parts read from a source. A signature, an example and a function keep theirs, because a caller that builds a program in memory has no text to point into. |
| F6 | A comment on a text ending its lines with two characters kept the first of them. | It is not kept, and the schema says a comment text carries no line terminator. |
| F7 | The three laws drew different cases on each run. | They are derandomised. Two consecutive runs against a known defect print byte-identical output. |
| F8 | "One table" was a claim nothing held in step. | The both-direction check of F3 holds it: a kind built but not published, or published but not built, fails by name. |

## What was measured

- Full suite: 1171 passed (1136 before this change).
- The seven test files this change adds: 9 runs in a row, 35 tests green
  each time, median 0.30s for the whole set, slowest single test 0.04s.
- Every repair has a delete-check: the wrong behaviour was put back and
  the test that must see it was observed failing, then the file restored.

## What is not claimed

No linter and no type checker is configured in this project, so the
scorecard only compiles the package and the tests. No style, type or
dead-code claim is made. Jev was unreachable for the whole run
(`TYPESAFE_API_KEY` absent), so every open choice was settled locally and
written down in the oracle record.

## Still open

The craft record cannot be re-recorded while this branch sits on main:
the workspace baseline is the commit this work started from, so after the
rebase the tool reads main's own docs commit as a feature commit standing
before the two refactor commits. The exact refusal was reported upward
and nothing was decided here.
