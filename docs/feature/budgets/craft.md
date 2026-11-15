# Budgets: what was built

## What a caller gets

Every operation now runs under four numbers it states before it is asked for
anything, and a run that passes one is stopped and told which one.

* `src/prova/budgets.py` (new) owns the four numbers, the name a caller reads
  each by, the unit it is counted in, the category of its refusal, the reason for
  its value, and the one way to lower it. It knows no operation name, reads no
  request and writes no answer.
* `src/prova/service.py` starts a run under those budgets, measures it at each
  boundary between the stages of an operation and before each declared example,
  compares the source against the input budget before any rule of the language is
  read over it, catches the one exhaustion where the answer is built, and renders
  the one text the command prints.
* `src/prova/__main__.py` reads the environment once, answers by name a budget it
  cannot read, and prints what the dispatcher rendered.
* `src/prova/checker.py` publishes the shape of the four new refusals in the one
  table of shapes, beside the two limits that were already there.

## What was run

| Check | Command | Result |
|---|---|---|
| The whole suite | `uv run pytest -q tests --durations=10` | 1230 passed, 153.5 s, exit 0 |
| Mechanical check | `uv run python -m compileall -q src tests` | exit 0, clean against the pre-feature tree |
| The new tests, nine times | the nine new files plus the laws | 32 passed every time; median 4.42 s, slowest 4.46 s |

No new test is among the ten slowest in the suite. The slowest new test is a
generated law at 0.92 s for ten cases, each of which starts the real command as a
child process; every example-based case is at or under 0.05 s. This repository has
no lint or type checker to run: its CI runs the test suite and nothing else, so
the mechanical check is byte-compilation of the source and the tests.

**test_cost receipt.** Nine consecutive runs of the new files: 4.39, 4.42, 4.40,
4.42, 4.43, 4.42, 4.43, 4.44, 4.46 seconds as pytest reports them (4.49 to 4.56
by the shell's own clock). Median 4.42 s, slowest 4.46 s, no run failed.

**Jev.** `typesafe: unavailable` -- `TYPESAFE_API_KEY` is absent from this
environment and the client exited 3 when the four design questions were put to
it. Every choice was settled locally and recorded as a decision.

## One test was revised after the code existed

The case for a budget name this tool does not publish required the refusal to
quote back the *value* the caller wrote (`5`). The value is not what is at fault
there -- the name is, and the message quotes the name. The case now requires the
refusal to quote back whatever was at fault: the value for a value, the name for
a name. The revised file was run against the archived copy of the pre-feature
tree under the workspace, together with the laws, and failed there for the
promised outcome, not for a setup reason:

```
uv run pytest -q tests/acceptance/test_f14_b8_a_caller_lowers_a_budget_the_published_way.py \
              tests/properties/test_f14_budget_laws.py
9 failed, 1 passed in 35.82s
```

That archived tree is the baseline this work started from, before two other
deliveries merged into the trunk; this branch now stands on the trunk that
carries them.

## What is measured and what is only declared

| Budget | Measured | Declared |
|---|---|---|
| `input_size`, 1 MiB | The size compared is the exact bytes of the source; a text at the number is read and a text past it is refused | That 1 MiB is the right ceiling for any caller |
| `answer_size`, 1 MiB | The size compared is the exact bytes of the text that would be printed | That 1 MiB is the right ceiling |
| `operation_time`, 10 s | That a run with no time left is stopped at the next boundary between stages | That 10 s is the right number on a machine other than this one; nothing was timed on CI |
| `peak_memory`, 512 MiB | That a run past the number is stopped, reading what the operating system reports this process has taken | That 512 MiB is the right number; nothing was measured on CI |

## What is not verified

* No run was observed passing a budget in the middle of a single stage, because
  no such run can be built from outside: the checker refuses a cyclic call graph,
  so a program of this profile has neither loop nor recursion, and the size of a
  stage is held down by the input budget.
* The memory figure is the greatest memory the *process* has taken, which includes
  the interpreter itself; it is not the memory one operation added.
* A platform that cannot report that figure is answered from the code that reads
  it, which says the budget is stated and not enforced there. No such platform was
  run: macOS and Linux both report it.
