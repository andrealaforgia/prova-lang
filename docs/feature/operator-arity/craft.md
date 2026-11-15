# F7 craft: the rule, and what was measured

## What was built

One table and one rule in `src/prova/checker.py`.

`OPERATOR_ARITIES` writes down what SPEC.md lines 178-189 give each of
the eleven builtin operators: one argument for `not`, two for every
other. `arity_of` is the one place that answers "how many does this
operator take", so the refusal and the operand checks below it read the
same number. An operator the table does not know is a fault in the tool
itself, not in the program, and is raised as one.

`_check_operator` now compares the number of arguments written with that
number before it looks at the operands, and reports the difference where
the call stands, saying how many the operator takes, how many the
program gave, and that operators have no variable arity. The operand
checks still run afterwards, so a program with both defects hears about
both in one pass.

Nothing else changed. No existing test was edited, `SPEC.md` was not
touched, and `src/prova/syntax.py` and `src/prova/service.py` were not
touched: the parser already accepts a call with any number of arguments,
and the refusal uses a word the manifest already publishes, so the
delivery working in those files is not disturbed.

## What passed

- `uv run pytest -q tests --durations=10`: **921 passed**, 0 failed. The
  899 tests that were green before this work are still green; the 22
  observations this feature adds were red before it and are green now.
- Scorecard: `uv run python -m compileall -q src`, exit 0, on this tree
  and on the pre-feature tree. **No linter or type checker is configured
  in this project** (nothing in `pyproject.toml`, no `.nwave` config),
  so the scorecard compiles the package and nothing more. It is not a
  substitute for a linter, and no style or type claim is made here.
- `uv run python docs/spec-trace/probe.py`: the repository's own probe
  `E5` for this clause now reports `yes` with the word `arity_mismatch`,
  where it reported the program accepted before.

## The one deliberate break

With the comparison changed from "different from" to "more than", so
that only extra arguments were refused, six of the new observations
failed, among them the one-argument sum, the operator with no arguments
at all and both generated laws. The code was restored and the suite is
green again. One deliberate break, not a mutation campaign.

## Test cost

The eight new test files (22 observations) were run nine times in a row.
All nine passed, 22 of 22 each time: 0.92, 0.94, 0.94, 0.91, 0.90, 0.92,
0.91, 0.92, 0.93 seconds, **median 0.92 s, slowest 0.94 s** for the
whole set. Nothing is flaky across those nine runs.

Per observation, the slowest is 0.07 s and every other is 0.04 s or
less. The twenty acceptance observations each run the real `prova`
command as a separate process, which is where that time goes; the two
generated laws run a hundred cases each, in process, in 0.03 s. The
whole suite takes 96 s, and its ten slowest tests are all older ones,
none from this feature.

## What this does not establish

- The tool refuses a wrong number of arguments. It does not change what
  a correctly written operator computes, and nothing here claims a new
  guarantee about evaluation.
- The generated laws sample the eleven operators and counts from none to
  six. They are evidence over those bounds, not proof.
- `docs/spec-trace.md` is a snapshot measured at a named commit and
  still records this clause as missing. It already carried rows an
  earlier delivery overtook (row 2.13, which its own probe now reports
  as satisfied), so it is left to its owner rather than half-updated
  here.
