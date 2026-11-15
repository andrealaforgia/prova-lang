# F10, step 3: the craft

## What was built

Two commits, in the order the design named.

**`72d5875` — the prefactor, no behaviour changed.** `service.py` built
nine refusals as hand-written dictionaries beside the one builder that
rendered the checker's diagnostics. They are now `checker.Diagnostic`
values rendered by that single builder, and the bare digest function is
a `SourceRevision` value object. Same categories, same sentences, same
keys; no test edited.

**`f609ad5` — the feature.** One table of kinds in `checker.py` says what
each category carries. The diagnostic type reads it when it is built and
refuses a subject, a place or a cycle the category does not declare, and
refuses a place that stands at line 0 or column 0. The manifest publishes
the same table as `diagnostic_schemas`, and the published list of
categories is now read from it, so a category cannot be announced without
its shape. Every refusal about a submitted source is stamped with that
source's revision in the one place every refusal passes.

## What a client gets that it did not have

| | Before | Now |
|---|---|---|
| which text the answer is about | only for an accepted program | every diagnostic, by `source_revision` |
| which symbol is at fault | inside the sentence | `symbol` |
| what was expected and found | inside the sentence | `expected` and `actual`, types or counts |
| where | 14 categories of 22 | every category that has a place in the data |
| the shape of a refusal | nowhere | `diagnostic_schemas` in the manifest |

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

## A crash that is older than this feature

The generated sources found an `IndexError` in `src/prova/evaluator.py`
when a program the checker accepts is then run. Delete character 550 or
character 1191 of `examples/hour-clock.prova` and ask for `examples`: the
pre-feature tree raises the same traceback, so this is not a regression
of F10 and it was not repaired here. It belongs to the evaluator's owner.
It breaks F6's law that every source gets one answer and never a
traceback, over a wider family of sources than F6's own closed family
reaches.

The laws of this feature therefore ask the two operations that run a
program only for a source the checker refuses. Nothing is lost: an
accepted program carries no diagnostic, so those cases say nothing about
what a diagnostic carries.

## What was measured

- **The suite**: `uv run pytest -q tests --durations=10` — 1026 passed in
  110s. The 1007 tests already on main are unedited; 19 are new. None of
  the new tests is among the ten slowest.
- **Test cost**: the eight new files run nine times in a row, all green:
  19 passed, median 2.80s, slowest 2.84s. They drive the real command as
  a subprocess, which is seconds-grade work, and the laws run in process.
- **Mechanical check**: `uv run python -m compileall -q src tests` exits
  0, before and after. This repository declares no linter or type
  checker; its CI runs `uv run pytest -q tests` and nothing else.
- **The prefactor holds the tests green**: recorded through
  `uv run pytest -q tests/unit` on the parent and on the prefactor
  commit. The fuller check was also run by hand in a clean detached
  checkout of the parent: `uv run pytest -q tests --ignore-glob=*f10*`
  gave 1007 passed, exit 0.
- **The question service**: authorized for this run but unavailable, with
  `TYPESAFE_API_KEY` absent from the environment and the client exiting
  3. The four open semantic questions were decided locally and are
  written down in the oracle note.

## What is still open

The independent review and the examination. The pre-existing crash above
is reported and left to its owner.
