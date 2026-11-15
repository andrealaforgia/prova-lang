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
| The whole suite | `uv run pytest -q tests --durations=5` | 1241 passed, 160.4 s, exit 0 |
| Mechanical check | `uv run python -m compileall -q src tests` | exit 0, clean against the pre-feature tree |
| The new tests, nine times | the ten new files plus the laws | 43 passed every time; median 4.94 s, slowest 4.98 s |

No new test is among the five slowest in the suite. The slowest new test is a
generated law at about 0.9 s for ten cases, each of which starts the real command
as a child process; every example-based case is at or under 0.05 s, except the
one that sends 20 MiB to measure what refusing it costs. This repository has no
lint or type checker to run: its CI runs the test suite and nothing else, so the
mechanical check is byte-compilation of the source and the tests.

**test_cost receipt.** Nine consecutive runs of the new files: 4.86, 4.88, 4.89,
4.91, 4.94, 4.98, 4.96, 4.95, 4.97 seconds as pytest reports them. Median 4.94 s,
slowest 4.98 s, no run failed.

**Jev.** `typesafe: unavailable` -- `TYPESAFE_API_KEY` is absent from this
environment and the client exited 3 when the four design questions were put to
it. Every choice was settled locally and recorded as a decision.

## What an independent review found, and what was repaired

**A budget written in other digits.** `PROVA_BUDGET_INPUT_SIZE=²` passed a guard
that asked whether the text was a digit and then broke the command on the way to
a number (exit 1, a traceback, 20 of 100 probed values); digits of other
alphabets (`٥٥٥`, `१२३`) were quietly taken as numbers of their own. A budget is
now written in the digits 0 to 9 and nothing else -- no sign, no surrounding
space, no digit of another alphabet, no digit above the line -- and anything else
is refused by name with the text quoted back. Six cases were added to the table
of mistakes a caller can make.

**A request too large to answer was read first.** The command read all of its
input, decoded it, and only then measured the source -- making a second full copy
to do it. Refusing a request now costs what answering a small one costs:

| Request | Peak memory before | Peak memory after |
|---|---|---|
| 50 MiB source | 182,304,768 bytes | 28,622,848 bytes |
| 200 MiB source | 654,229,504 bytes | 28,557,312 bytes |
| a small request (for comparison) | 28,639,232 bytes | 28,639,232 bytes |

Measured with `/usr/bin/time -l` around the real command on this machine. The
200 MiB case was past the 512 MiB this tool declares for itself.

The command now reads one character past `input_size` plus a stated allowance of
65536 bytes for everything a request carries around its source, and answers a
longer request against the input budget without reading it -- saying that the
operation asked for was never read, and naming none. A source is sized a page at
a time, and only when its characters alone cannot settle it: a text of more
characters than the budget allows is already past it, and one of a quarter as
many cannot be. The allowance also closes the gap the review named, that an
`arguments` entry, an unknown field or a long operation name was not sized at
all.

**The memory figure never falls.** `ru_maxrss` is a high-water mark, so a run
that has passed the budget cannot come back under it, and the old remedy ("send a
smaller program") was false advice for that case. The manifest now says the
figure is the greatest the process has taken and never falls, and the refusal
tells the caller to start again in a new process.

**The amount a refusal reports.** The sentence a person reads now carries the
same number the field a program reads carries, checked for every budget refusal.

## The repairs were delete-checked

Each repair was removed again and the case that covers it was run, to see it fail:

| Removed | Case run | Result |
|---|---|---|
| the guard that only the ten digits are a budget | the table of mistakes | 5 failed, 6 passed |
| the bounded read of a request | the over-long request cases | 1 failed, 4 passed |
| sizing a source in bytes rather than characters | the over-long request cases | 1 failed, 3 passed |
| the amount in a refusal's sentence | the input budget cases | 2 failed, 1 passed |

Each was restored immediately and the suite re-run.

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
| `input_size`, 1 MiB | The size compared is the exact bytes of the source; a text at the number is read and a text past it is refused; the memory refusing a 50 MiB and a 200 MiB request costs was measured | That 1 MiB is the right ceiling for any caller, and that 64 KiB is the right allowance around a source |
| `answer_size`, 1 MiB | The size compared is the exact bytes of the text that would be printed | That 1 MiB is the right ceiling |
| `operation_time`, 10 s | That a run with no time left is stopped at the next boundary between stages | That 10 s is the right number on a machine other than this one; nothing was timed on CI |
| `peak_memory`, 512 MiB | That a run past the number is stopped, reading what the operating system reports this process has taken | That 512 MiB is the right number; nothing was measured on CI |

## What is not verified

* No run was observed passing a budget in the middle of a single stage, because
  no such run can be built from outside: the checker refuses a cyclic call graph,
  so a program of this profile has neither loop nor recursion, and the size of a
  stage is held down by the input budget.
* The memory figure is the greatest memory the *process* has taken, which includes
  the interpreter itself; it is not the memory one operation added, and it never
  falls. The command answers one request per process, so a run is measured
  against its own work; a caller using this tool as a library inside a longer
  process is measured against everything that process has done, which the
  manifest now says.
* A platform that cannot report that figure is answered from the code that reads
  it, which says the budget is stated and not enforced there. No such platform was
  run: macOS and Linux both report it.
