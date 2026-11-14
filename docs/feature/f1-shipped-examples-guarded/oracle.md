# F1 — the shipped examples are guarded by the suite

This note is for a human reader. It says what was decided, what was built,
what was proved and what is still open.

## What the Owner gets

One command, `uv run pytest -q tests`, now shows that the hour clock this
repository ships still works:

- it checks with no diagnostic at all, and every one of the 8 examples
  written in `examples/hour-clock.prova` is run and passes;
- the clock at hour 12 ticks round to hour 1, and the tick is accepted;
- each hour from 1 to 12 ticks to the next hour on the dial, 2 to 12 and
  then 1, and every one of those ticks is accepted;
- a copy of the clock with the wrap at 12 taken out is reported as a
  failure, and the shipped file keeps the same bytes while that copy runs;
- a run that cannot find the shipped file fails naming the file, and skips
  nothing.

Before this change no test anywhere read `examples/hour-clock.prova`, so an
edit to it broke nothing.

The other half of the same outcome, the reservation example, was already
guarded and is left alone: its clean check by
`test_s5_b1_unmodified_source_accepted_with_no_errors`, its declared
examples and a wrong copy by
`test_s2_int_examples_pass_and_wrong_copy_fails_end_to_end`, and its
six-row transition table by `test_b1_every_table_row_is_reproduced_by_direct_evaluation`.
Writing those tests again would have added no observation.

## What was built

| File | State |
|---|---|
| `tests/acceptance/_hour_clock_fixtures.py` | Created |
| `tests/acceptance/test_f1_shipped_hour_clock_is_guarded.py` | Created |
| `tests/properties/test_f1_hour_clock_dial_property.py` | Created |

No file under `src/` changed, no existing test changed, `SPEC.md` is
untouched, and no existing expected result was edited.

## Decisions

- **The clock has no published transition table.** `SPEC.md` gives a table
  only for the reservation example. The twelve-hour dial written out in the
  request's criterion 3 is taken as the clock's table for this feature. It
  is written by hand in the fixtures from the request, never derived from
  the clock source the tests observe. No authority document was changed.
- **The reservation half is mapped to the tests that already prove it**, and
  no duplicate test is written.
- **The dial is enumerated, not generated**: twelve hours is a closed finite
  domain. The hours a caller can name are unbounded, so that law gets the
  generated property instead.
- **No formal model (Quint).** This feature has no state machine, protocol,
  concurrency or crash behaviour of its own; it observes a pure evaluator
  through one short-lived command.
- **The clock file path is stated in both test directories.** An acceptance
  test run on its own cannot import from `tests/properties`: a probe of that
  import failed with `ModuleNotFoundError`. The property test therefore
  reads the shipped file itself rather than through a shared fixture, and
  `tests/properties/_prova_client.py` was left unchanged.

## What the generated property adds

The acceptance tests observe only hours on the dial. The property observes
every hour a caller can name and asserts that a tick is accepted exactly
inside 1 to 12 and refused outside it. Deleting the clock's entry condition
leaves all 8 declared examples passing and all 17 acceptance cases green;
only this property fails, at hours 0 and 13. That is the observation it
adds.

## What was proved, and how

Each check below was run and its result observed.

| Injected fault | What was observed |
|---|---|
| The wrap at 12 removed from the shipped step | 6 of the 17 guard tests failed, including the dial case for hour 12; run over a temporary copy of the tree, with the shipped file's digest identical before and after (`0b3a9803...`) |
| The whole clock file absent from the tree | 17 tests failed, 0 skipped |
| The refusal replaced by a skip | the missing-file test failed, reporting 16 skipped |
| The wrap-removed copy made a copy that removes nothing | the copy test failed: "0 of the 8 declared examples of the copy failed, not exactly one" |
| The clock's entry condition deleted | only the generated property failed, at hours 0 and 13 |

The remedy the missing-file message names,
`git checkout -- examples/hour-clock.prova`, was run and restored the file
byte for byte.

## Test cost

`uv run pytest -q tests` : 790 passed in 67.56 s (772 before this change).

The two new files were run nine times in a row and passed nine times:
median 2.24 s, slowest 2.35 s. The slowest single test is the generated
property at about 0.99 s; the missing-file test, which starts three short
runs of pytest, takes about 0.58 s. Every other new test is a single call
to the real command, about 30 ms. No test sleeps and none reads the clock.

## Still open

The step tool refused to record this work, and the refusal is not about the
tests. It runs the oracle's test command on the tree as it was before the
change, with the change's test files copied over it, and refuses a test that
passes there. All 18 new tests pass there, because the compiler already
satisfies every acceptance criterion: the gap this feature closes is that
nothing guarded it. Its words:

```
WHAT: command for 'red' exited 0 but expect is fail;
      last output: 18 passed in 3.08s
```

Every shipped schema (v9, v10, v11) makes that command required and
failing, and the tool has no declaration for an oracle that is green by
design. So this feature carries no recorded step and no generated brief; the
injected-fault table above is the evidence it can honestly give instead.
This is a question for the Owner, not a defect of the tests.
