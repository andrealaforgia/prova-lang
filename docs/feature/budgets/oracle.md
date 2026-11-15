# Budgets: the oracle

## What this feature promises

Every operation this tool offers says, before it is asked for anything, how large
a source it reads, how long it runs, how much memory it takes and how large an
answer it gives. A run that passes one of those four is stopped and told which
one stopped it. A run inside all four is answered exactly as it always was.

Nine promises were drawn from the request, one per outcome sentence:

| | Promise |
|---|---|
| P1 | A caller reads the four budgets of every operation from the manifest, each marked enforced. |
| P2 | A source larger than the input budget is refused for that budget, by name, with the size allowed beside the size sent. |
| P3 | A run with no time left is answered with the time budget: not half an answer, not a command that never returns. |
| P4 | A budget refusal reports the budget and nothing about the program. |
| P5 | A program well inside every budget is answered as it was before any budget existed. |
| P6 | A caller lowers a budget for one run the published way; a budget it cannot set is refused by name, never ignored. |
| P7 | The nesting limit and the evaluation depth published before stand unchanged; the budgets join them in the same block. |
| P8 | An answer larger than the answer budget is replaced whole by a refusal, never cut short. |
| P9 | A run that has taken more memory than it was given is refused for the memory budget, by name. |

Twenty-four of the request's thirty-seven sentences are process or context (the
worktree, the commit line, the criterion numbers); each is recorded with the
reason it states no outcome a caller can observe.

## What was decided, and why

* **One refusal category per budget.** `input_budget_exceeded`,
  `time_budget_exceeded`, `memory_budget_exceeded`, `output_budget_exceeded`.
  Every other distinct refusal of this tool already has its own category, and a
  caller that must handle "the source was too large" differently from "the run
  ran out of time" should not have to read prose to tell them apart.
* **A caller lowers a budget through a named environment variable** that the
  manifest publishes beside the budget (`PROVA_BUDGET_INPUT_SIZE` and its three
  siblings). A field in the request would let any caller rewrite the budgets of
  the published protocol; an argument inside the program alone could not be
  reached by a test that drives the real command. A value that is not a whole
  number, a value above the number this tool declares, and a name this tool does
  not publish are all refused by name: a caller that believed it had lowered a
  budget and had not would read the run that followed as proof that its work
  fits.
* **The answer budget is enforced where the answer is written.** One place owns
  the bytes a caller reads. A refusal is always delivered, even when the refusal
  is itself larger than the budget the caller set: the budget sizes the answer an
  operation produced, and the refusal that replaces it is this tool's smallest
  answer.
* **Time and memory are observed between the stages of an operation** and before
  each declared example is run. A stage already running is not interrupted part
  way; what keeps a stage short is the input budget. This is published as
  enforced, with that granularity stated, rather than as a budget nobody keeps.
* **The four numbers are published as declared, not measured.** The Owner's
  decision (roadmap section 5, D5, approved in section 8) is 1 MiB of source,
  10 s, 512 MiB of memory and 1 MiB of answer, to be measured on CI first.
  Measured by this work: the two sizes, which are counted in bytes and compared
  exactly, and the fact that every program this repository ships and every test
  in the suite completes inside all four. Only declared: that 10 s and 512 MiB
  are the right numbers on any machine but this one. No timing or memory figure
  was taken on CI.
* **No formal model.** There is no protocol here, no concurrency and no stored
  state: a budget is one number compared with another inside one process.

## What the tests prove

Twelve scenarios, written as ten acceptance test files and four generated laws,
all driving the real command over its standard input and output:

* the manifest states four budgets for each of the six operations offered -- 24
  entries, `parse` being the sixth -- with the Owner's numbers, each marked
  enforced and each saying how to lower it;
* a 200 byte source under a 64 byte budget, and a 1048577 byte source under the
  declared 1 MiB, are both refused by name with the two numbers;
* a run with no time left, a run past a 1 byte memory budget, and an answer one
  byte larger than its budget are each refused by their own category;
* none of those four answers carries a claim, a result or a digest, and none of
  them uses a word that would make the mathematics of a program a matter of this
  tool's budgets;
* the hour clock, 1474 bytes, still steps from 11 o'clock to 12 with no
  diagnostics, and the three programs this repository ships still check;
* the nesting limit of 128 forms and the evaluation depth of 160 steps are
  unchanged.

Every one of those tests was run against the tree as it stands before this
feature: 23 of them failed and none of them broke on an import or a fixture.
The seven that already pass are the twins that hold the old answers fixed, kept
so that a tool which simply refused everything would not pass either.

## Added after the first review

A tenth acceptance file was added when an independent review found two defects:
one for a request longer than this tool reads, which is now answered against the
input budget without being read, and one for a source whose bytes outnumber its
characters, which is now sized in bytes. The new cases are listed with the
repairs in `craft.md`.

## What is still open

* The time and memory numbers are declared, not measured. A CI measurement is
  owed before they can be called anything else.
* A stage already running is not interrupted part way. Today no program can run
  without end -- the checker refuses a cyclic call graph, so a core-0 program has
  no loop and no recursion -- but that is a property of the profile, not of the
  budget.
* Whether the memory budget can be enforced on a platform that offers no reading
  of a process's own peak memory. The design step decides what such a platform is
  told.
