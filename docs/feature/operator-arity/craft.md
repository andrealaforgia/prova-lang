# F7 craft: the rule, and what was measured

## What was built

One table and one rule in `src/prova/checker.py`.

`BUILTIN_OPERATORS` is the one place the checker learns which operators
exist: each entry holds the number of arguments SPEC.md lines 178-189
give that operator and the group whose operands it reads. The four
groups the operand checks ask about are derived from it, and `arity_of`
answers from it, so an operator added to the language is added here
once. A unit test holds that table and the language's own list of
operators to the same names, and fails when an operator is in one and
not the other.

`_check_operator` compares the number of arguments written with the
number the table gives before it looks at the operands, and reports the
difference where the call stands, saying how many the operator takes,
how many the program gave, and that operators have no variable arity.
The operand checks still run afterwards, so a program with both defects
hears about both in one pass.

Nothing else changed. No existing test was edited, `SPEC.md` was not
touched, and `src/prova/syntax.py` and `src/prova/service.py` were not
touched: the parser already accepts a call with any number of arguments,
and the refusal uses a word the manifest already publishes.

## What passed

Measured again after the review, with the figures restated:

| Run | Collected | Passed | Failed |
|---|---|---|---|
| The tree this branch started from (`5024bf2`) | 932 | 931 | 1 |
| This branch, whole suite | 962 | 961 | 1 |
| This branch, without the one test named below | 962 | 961 | 0 (1 deselected) |

The 30 observations this feature adds are all green. **The one failure
is not this feature's**: `tests/properties/test_f5_binding_scope.py::test_a_binder_is_refused_exactly_when_its_name_is_taken`
fails on the tree this branch started from as well, for a defect in its
own generator (see "What this does not establish"). An earlier version
of this document reported 899 and 921; those were the counts before this
branch was rebased, and they are wrong for this tree.

- Scorecard: `uv run python -m compileall -q src`, exit 0, on this tree
  and on the pre-feature tree. **No linter or type checker is configured
  in this project** (nothing in `pyproject.toml`, no `.nwave` config),
  so the scorecard compiles the package and nothing more. It is not a
  substitute for a linter, and no style or type claim is made here.
- `uv run python docs/spec-trace/probe.py`: the repository's own probe
  `E5` for this clause now reports `yes` with the word `arity_mismatch`,
  where it reported the program accepted before.

## The deliberate breaks

Three, each one restored afterwards:

- The comparison changed from "different from" to "more than", so only
  extra arguments were refused: six observations failed, among them the
  one-argument sum, the operator with no arguments at all and both
  generated laws.
- The comparison switched off altogether: the three observations in a
  precondition, a postcondition and a `match` clause body failed.
- One operator removed from the table: the unit test that holds the
  table to the language failed, naming the missing operator.

## Test cost

The ten files this feature adds (30 observations) were run nine times in
a row. All nine passed, 30 of 30 each time: 1.22, 1.23, 1.21, 1.22,
1.23, 1.22, 1.22, 1.22, 1.22 seconds, **median 1.22 s, slowest 1.23 s**
for the whole set. Nothing is flaky across those nine runs.

Per observation, the slowest is 0.07 s. The acceptance observations each
run the real `prova` command as a separate process, which is where that
time goes; the two generated laws run a hundred cases each, in process,
in 0.03 s. The whole suite takes about 105 s, and its ten slowest tests
are all older ones, none from this feature.

## What this does not establish

- The tool refuses a wrong number of arguments. It does not change what
  a correctly written operator computes, and nothing here claims a new
  guarantee about evaluation.
- The generated laws sample the eleven operators and counts from none to
  six. They are evidence over those bounds, not proof.
- **A defect in another feature's test, reported to its owner, not
  fixed here.** `tests/properties/test_f5_binding_scope.py` draws a
  "free" binder name from any lower-case word of one to eight letters,
  excluding a list that does not hold the word-shaped builtin operators.
  When it draws `and`, `or` or `not`, the tool refuses the binding -
  correctly, by F5's own rule - and the test reads that as a defect.
  Measured: it failed 5 of 10 runs on this branch before its example
  database learned the case, 6 of 6 after, and it fails the same way on
  `5024bf2` with a clean checkout. The fix belongs in that generator's
  exclusion list; no test of another feature was edited here.
- `docs/spec-trace.md` is a snapshot measured at a named commit and
  still records this clause as missing. It already carried rows an
  earlier delivery overtook (row 2.13, which its own probe now reports
  as satisfied), so it is left to its owner rather than half-updated
  here.
