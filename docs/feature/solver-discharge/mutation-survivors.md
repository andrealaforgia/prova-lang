# Changes no test notices, and why each one is allowed to

`tools/mutate_encoder.py` walks the syntax of the four modules that
decide a verdict and makes every change its operators can make: 507
mutants over the translation, the solver port, the discharge decision
and the obligations. Each gets its own copy of the source tree, first on
the import path, with bytecode writing off, and a control runs before
any judging -- an unmutated copy must be green and a same-length mutant
red -- so the harness proves it carries nothing between runs.

Every mutant is asked the close-watching cells, then the slower
families. A mutant that survives both is asked the whole suite once.
What is left after that is a change no test in this repository notices,
and this file is where each one has to be accounted for.

## How a survivor is classified

| Class | Meaning | What it obliges |
|---|---|---|
| **(b)** | a demonstrated wrong `proved`, `disproved` or `unknown`: a program exists that shows the tool answering wrongly | write the program here, add a cell or an acceptance case, re-run the mutant until it is red |
| **(c)** | an argued equivalence: the change cannot alter any answer a reader acts on -- a message, a text, a count nobody reads, a limit no program approaches, performance | one line here with the argument, and nothing else |
| **(d)** | unreachable by design: the branch cannot be entered by any input the profile admits | one line here naming why it cannot be entered |

A class (b) survivor is a defect in the oracle and is not allowed to
remain. Classes (c) and (d) are allowed to remain **only** with their
line in this file.

## Survivors

The full run is in progress; this table is filled from its report at
`work/mutants.json`. The entries below are the ones already judged.

| Module | Function | Line | Operator | Class | Argument |
|---|---|---|---|---|---|
| `encoding.py` | (module level) | 39 | module constant: int constant +1 | (c) | `EXPANSION_LIMIT = 64` is a bound on how far calls are expanded, chosen rather than measured. The deepest expansion any program in the oracle needs is 3, so 63, 64 and 65 are indistinguishable to every test. A program that did approach the bound would be answered `unknown` either way, with the bound named in its reason |
| `encoding.py` | (module level) | 39 | module constant: int constant -1 | (c) | the same bound, the same argument |

## What this file does not claim

That the four modules are correct. A mutation harness searches for
changes the tests cannot see; it says nothing about changes nobody
thought to make, and nothing about the solver, the parser or the type
checker, which stay trusted. Nor does a (c) argument become true by
being written down: each one is an argument a reviewer can read and
reject.
