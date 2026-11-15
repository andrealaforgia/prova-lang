# F10, step 3: the craft

## What was built

**`626f9be` — the prefactor, no behaviour changed.** `service.py` built
nine refusals as hand-written dictionaries beside the one builder that
rendered the checker's diagnostics. They are now `checker.Diagnostic`
values rendered by that single builder, and the bare digest function is
a `SourceRevision` value object. Same categories, same sentences, same
keys; no test edited.

**`9712e47` — the feature.** One table of kinds in `checker.py` says what
each category carries. The diagnostic type reads it when it is built and
refuses a subject, a place or a cycle the category does not declare, and
refuses a place that stands at line 0 or column 0. The manifest
publishes the same table as `diagnostic_schemas`, and the published list
of categories is read from it, so a category cannot be announced without
its shape. Every refusal about a submitted source is stamped with that
source's revision in the one place every refusal passes.

**`fe0b519`** kept the generated laws off a crash older than the feature
(below). **`bcec4ec`** answered the first review: a `source` that is not
text, and the text a place stands in.

## What a client gets that it did not have

| | Before | Now |
|---|---|---|
| which text the answer is about | only for an accepted program | every diagnostic, by `source_revision` |
| which symbol is at fault | inside the sentence | `symbol` |
| what was expected and found | inside the sentence | `expected` and `actual`, types or counts |
| where | 14 categories of 22 | every category that has a place in the data |
| which text a place stands in | nowhere | `points_into`, for a category that can stand in two |
| the shape of a refusal | nowhere | `diagnostic_schemas` in the manifest |
| a `source` that is not text | a traceback, exit 1 | `malformed_request`, naming the field |

## One conflict with an existing test, and how it was settled

`tests/properties/test_i1_s1_p4_p5.py` traces every module the process
enters and requires that an unavailable or unrecognised operation enters
nothing of `prova.checker`: an operation the tool does not answer
attempts none of the work. Building a `checker.Diagnostic` for those two
refusals enters that module, so the test failed.

The test is right and was not edited. Those two refusals answer about the
*request*, not about a program: they name no symbol, stand at no place in
any text and carry no revision. They stay written where the dispatch
decides them, with the reason recorded beside them in the code. Every
refusal that is about a source goes through the one builder.

## Crashes that are older than this feature

- `src/prova/evaluator.py` raises `IndexError` when a program the checker
  accepts is then run: delete character 550 or 1191 of
  `examples/hour-clock.prova` and ask for `examples`. The pre-feature tree
  raises the same traceback. The laws of this feature therefore ask the
  two operations that run a program only for a source the checker
  refuses; nothing is lost, because an accepted program carries no
  diagnostic.
- `evaluate` with `"function": ["f"]` raises `TypeError: unhashable type`
  and with `"arguments": 7` raises `TypeError: 'int' object is not
  iterable`. Both raise on the pre-feature tree too. The review asked for
  the `source` field, which is repaired and tested; these two are
  reported, not repaired here.

## What was measured

Against `bcec4ec`, on `main` at `5498173`:

- **The suite**: `uv run pytest -q tests --durations=10` — **1042
  passed** in 109s. The same command without this feature's files
  (`--ignore-glob=*f10*` and the new unit file) gives **1011 passed**,
  which is what `main` carries: 31 checks are new and no existing test is
  edited. None of the new tests is among the ten slowest.
- **Test cost**: the eleven new files run nine times in a row, all green:
  31 passed, median 6.03s, slowest 6.10s. They drive the real command as
  a subprocess, which is seconds-grade work; the laws and the
  construction rules run in process.
- **Each repair turns a check red when it is removed**: the boundary
  guard (B9), the text a place stands in (B3, B8), the published
  granularity of `unbound_type` (B8), the rules a refusal is built under
  (the new unit file), and the place the reader stopped at when the text
  ran out (B3). Five of five, each run with the repair deleted and then
  restored.
- **Mechanical check**: `uv run python -m compileall -q src tests` exits
  0, before and after. This repository declares no linter or type
  checker; its CI runs `uv run pytest -q tests` and nothing else.
- **The prefactor holds the tests green**: recorded through
  `uv run pytest -q tests/unit` on its parent and on itself. The fuller
  check was run by hand in a clean detached checkout of the parent:
  `uv run pytest -q tests --ignore-glob=*f10*`, 1007 passed, exit 0,
  before the branch was rebased onto `5498173`.
- **The question service**: authorized for this run but unavailable, with
  `TYPESAFE_API_KEY` absent from the environment and the client exiting
  3. The four open semantic questions were decided locally and are
  written down in the oracle note.

## Reading the generated brief

`docs/diagnostic-fields/` is generated from the run's journal. Two things
in it come from the workspace's archived baseline, which predates the
rebase of this branch onto `main`, and not from this change:

- the craft section is marked `STALE`, because an earlier step was
  recorded again after it. It still holds: the numbers it records were
  measured again by hand against the branch as it stands and are written
  above, and the tool refuses a new craft revision while the baseline
  predates the rebase.
- the list of changed files includes `main`'s own `[F16fix]` files. They
  are not part of this change; `git log 5498173..HEAD` is the branch.

## What is still open

Two findings of the first review are follow-ups rather than repairs, and
are stated in the handoff: the role of `symbol` differs within one
category (a function name for one refusal of `malformed_value`, a
declared name for another), and the function a refusal stands in is
threaded through the checker as a bare `within: str` rather than a value
object. The crashes above belong to the evaluator and to the request
boundary of `evaluate`.
