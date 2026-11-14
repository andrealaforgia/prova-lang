# F5 craft: the rule, and what was measured

## What was built

One walk in `src/prova/checker.py`, added beside the rules about
declarations, function cycles and types, with the three values the
design named: the names visible at a binder, a binder that took one of
them, and a binder that took `result`. `src/prova/service.py` publishes
the two new category names in the tool's manifest.

A binder is read in the scope it stands in: the declared functions and
the builtin operators, then the parameters, then each enclosing `let`
binding, then the variables of its own pattern. A `let` initializer is
read before its own binding, and each `match` clause is read in the
scope of the whole expression, so disjoint clauses still share a
spelling. A binder that takes `result` carries that refusal alone: the
reader has one binder to rename either way, and a second refusal would
offer a second repair for one defect.

Nothing else changed. No existing test was edited, `SPEC.md` was not
touched, and no signature or name-shape parsing was touched, because
another delivery is working there.

## What passed

- `uv run pytest -q tests --durations=10`: **901 passed**, 0 failed. The
  857 tests that were green before this work are still green; the 44 F5
  observations that were red are green.
- Scorecard: `uv run python -m compileall -q src`, exit 0, on this tree
  and on the pre-feature tree. **No linter or type checker is configured
  in this project** (nothing in `pyproject.toml`, no `.nwave` config),
  so the scorecard compiles the package and nothing more. It is not a
  substitute for a linter, and no style or type claim is made here.

## Test cost

The ten F5 files (44 observations) were run nine times in a row. All
nine passed: 1.16, 1.16, 1.17, 1.16, 1.17, 1.18, 1.17, 1.16, 1.16
seconds, **median 1.16 s, slowest 1.18 s** for the whole set. Nothing
is flaky across those nine runs.

Nine of the ten files drive the real `prova` command in a subprocess, so
they are integration-level work, inside the seconds budget rather than
the 10 ms unit budget. The property file runs in process and draws its input: five taken
names over two binder shapes with a fresh generated name for the
accepted half, clause counts 2 to 6, nesting depths 2 to 8. No test sleeps
and none reads a clock.

## The probe: breaking the rule on purpose

Each refusal was removed once from the committed code, the tests were
run, and the code was restored.

| Break | Result |
|---|---|
| the scope never reports what a binder hides | 21 failed, 23 passed |
| `result` is not treated as reserved | 6 failed, 38 passed |
| restored | 44 passed |

So the tests observe each refusal separately: removing one does not hide
the loss of the other.

## What is not claimed

The remote question service was never reached (no key in this
environment, the client exited 3), so the choice of two categories, the
reading of "builtin" as the operator names, and the parameter rule carry
local judgment plus the owner's recorded answer on the last one.

Nothing here is an independent review. The work has not been reviewed by
anyone else yet.
