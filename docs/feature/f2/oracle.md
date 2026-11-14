# F2 - Oracle: what "a recursive program is refused" must mean

Feature F2: a program whose calls form a cycle is refused when it is
checked, with the cycle named, and the tool never dies with a Python
traceback.

## What the request promises

Six promises come out of the request, one per acceptance criterion.

| # | A user of the tool can see |
|---|---|
| P1 | A function whose body calls itself is refused when the program is checked, and the refusal names that function. |
| P2 | Two functions that call each other are refused, and the refusal names both. |
| P3 | A program whose only cycle runs through a contract clause is refused. |
| P4 | Asking a cyclic program for an answer gives a refusal in valid JSON and the process exits normally. |
| P5 | A function whose declared examples name that same function is still accepted. |
| P6 | The hour clock and the reservation example still pass, and no existing expected result changes. |

Every sentence of the request is accounted for: the sentences above map
to these promises, and the rest (the project setting, the commit rules,
the file names, the citations of the authority) are recorded as not
testable, each with its reason.

## What was proved before any code was written

The seven new test files were run against the code as it is today. The
tool ran them itself on a copy of the tree at commit `f2bbb73`:

- 9 tests failed, 0 collection or setup errors, exit code 1, 2.5 seconds.
- Every test that carries a promise was among the failures.

They fail for exactly the reason `docs/spec-trace.md` records as defect 1:
all three cyclic programs pass `check` today, and asking one of them for
an answer ends the process with exit 1 and an uncaught `RecursionError`
on standard error, with nothing on standard output.

The five tests that pass today are the controls: the same programs with
one call removed, which must stay accepted.

## How the tests avoid proving nothing

Two promises (P5, P6) describe behaviour the tool already has, so a test
that only asserted "still accepted" would pass whatever the code did.
Each of those tests therefore also builds the one program it must stay
distinguishable from -- the same function whose body calls itself, the
hour clock whose guard is replaced by a call to itself -- and requires
the two to get different answers. A tool that refuses everything, accepts
everything, or quietly stops checking these programs fails the test.

The property test decides whether a generated program is cyclic with a
transitive closure over the edges the generator drew, which is not the
search the tool will run, and every generated function declares an
example naming itself, so "examples are not calls" is exercised in every
case, accepted and refused alike.

## Decisions taken here

- **No formal model (Quint).** The rule is a property of one immutable
  parsed program: no state machine, no protocol, no concurrency and no
  crash window to explore. A generated property over call graphs observes
  the same law and runs in the ordinary suite.
- **Paradigm and layout follow the sibling code,** since the request names
  none: module-level functions and frozen dataclasses, acceptance tests
  driving the installed command over JSON, property tests calling the
  service in process.
- **The remote question service was not used.** `TYPESAFE_API_KEY` is not
  set in this environment and is declared in no shell profile, so the
  client exits 3 (service unavailable). The naming choices below were
  decided locally and are open for the person to change.

## Three choices, put to the person and settled

These were put to the Owner at the pause after this step, before any code
was written, and answered:

1. The name of the new diagnostic category: **`cyclic_dependency`**.
2. The shape of the refusal: **one diagnostic per cycle, carrying the
   members in a machine-readable `cycle` field** beside the sentence that
   also names them.
3. The exit code for a refused program: **0**, with the refusal in the
   response.

The tests already used all three, so none of them had to change.

## Still open

Nothing from this step.
