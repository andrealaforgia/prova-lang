# A function's examples are about that function — the change

## What was built

One owner in `src/prova/checker.py`, `DeclaredExample`, reads a declared
example as what it demonstrates: which function declares it, where it
stands among that function's examples, which function it calls and with
how many arguments. It answers with nothing when the example calls its
own function with the number of arguments that function takes, and
otherwise with the one refusal its defect carries. The refusals are
built beside the rule, as `Cycle` and `TypeCycle` already do.

`check_program` asks that owner where it already reads a function's
examples. One line was added to the published list of categories in
`src/prova/service.py`, so a client reads the new word from `discover`.

## What a reader is told

- An example about another function:
  `example 0 of function 'double' calls 'triple': core-0 requires every
  function to have an example directly calling that same function, so
  this example demonstrates 'triple' and leaves 'double' with no example
  of its own; write the example as a call to 'double', or declare it
  among the examples of 'triple'`
- An example whose call names no function of the program — a name
  declared nowhere, but a declared constructor or a builtin operator
  too: the same word, with `, which is not a function this program
  declares` after the name, and without the repair that would send a
  reader to a function that is not there.
- An example with the wrong number of arguments:
  `example 0 of function 'double' passes 2 argument(s), expected 1: an
  example supplies one closed value for each parameter the function
  declares, so this example cannot be run against 'double'; write
  exactly 1 argument(s) in the example`

## What the tests prove, and what they do not

- They prove the `check` and `examples` operations of the real `prova`
  command answer as above, over the programs listed in
  `tests/acceptance/_f8_example_subject_fixtures.py`, and that the two
  programs this repository ships stay accepted with their examples
  passing.
- The property test samples the law over programs of at most 3 functions
  of at most 2 parameters. That is evidence, not proof: nothing here
  says anything about a larger program.
- Nothing here proves an example's arguments have the *types* the
  function declares. The rule reads the name and the count only; the
  value checks that already existed are unchanged.
- The crash case is observed from outside: the command's exit status and
  the JSON on its standard output, not an internal signal.

## Test cost

| what | measured |
|---|---|
| full suite after the change | 1007 passed in 100.11s (`uv run pytest -q tests`), after the branch was rebased on main |
| the 8 new files, 9 runs in a row | 26 passed every time; pytest-reported 1.22-1.24s, median wall 1.34s, slowest 1.39s |
| slowest new test | under 0.2s; the acceptance tests each start the real `prova` command once |

The new acceptance tests are integration tests: each one runs the real
command in a subprocess, which costs about 40 ms. The property tests run
in-process. No test sleeps, reads a clock or depends on the order of a
set.

## Deliberate breaks (probe)

Three wrong behaviours were injected into the new rule, the tests were
run, and the code was restored:

| injected | caught by |
|---|---|
| a checker that never reads the name an example calls | 7 tests failed |
| a checker that never counts an example's arguments | 5 tests failed |
| a refusal naming only the function that declares the example | 2 tests failed |
| every name called treated as a declared function | 3 tests failed |
| no name called treated as a declared function | 2 tests failed |
| the earlier wording, which called a constructor and an operator undeclared | 3 tests failed |

## Jev

`typesafe: unavailable`. `TYPESAFE_API_KEY` is absent from this
environment, so the client exited 3 on the three open questions (which
word carries an example about another function; whether an undeclared
name is the same defect; which word carries a wrong argument count).
They were decided locally and recorded as decisions 1 to 3 in
`oracle.md`.

## Mechanical checks

The repository declares no linter and no type checker; its CI runs
`uv run pytest -q tests` alone. The scorecard command recorded for this
delivery is `uv run python -m compileall -q src tests`, which exits 0
here and on the pre-feature tree.


## What the independent review found, and what changed

Two findings, both non-blocking, both now fixed and each with a check
that turns red when the fix is removed:

1. **The branch for a name that is no function had no falsifier.**
   Treating every name called as a declared function kept the whole
   suite green. The tests now state both halves: a refusal about a
   declared function offers to move the example to it and says nothing
   about the name being unknown; a refusal about a name that is no
   function says so and offers no such move.
2. **The wording was false for a constructor and for an operator.**
   `(example (Box 3) => 4)` and `(example (+ 2 2) => 4)` were answered
   with "which this program does not declare", although `Box` is a
   declared constructor and `+` is a builtin operator. The refusal now
   says "which is not a function this program declares", which is true
   of all three, and both programs are observed in the tests.
