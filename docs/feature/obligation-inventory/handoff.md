# Handoff: what the next reader gets

## What the Owner can do now

Ask the tool what must still be shown about a program, and read the answer:

```bash
echo "{\"prova\":\"i1\",\"operation\":\"verify\",\"source\":$(uv run python -c \
  'import json;print(json.dumps(open("examples/hour-clock.prova").read()))')}" | uv run prova
```

The hour clock owes 20 obligations, the reservation example SPEC.md publishes
owes 18. Every one of them reads `not_attempted`, the totals say `attempted: 0`,
and the note says the tool has no solver and ran none of them.

`discover` now advertises `verify` as available and says, in the same breath,
that the answer is an inventory only. `build` is still refused as unavailable.

## How it was checked

Acceptance tests drive the real command against the two shipped programs; four
generated laws check completeness, honesty, determinism and the unreachable
branch, with their oracle written as a plan in the test rather than taken from
the tool; unit tests cover the empty, unreadable and unchecked edges and the two
refusals the code raises for programs built by hand past the checker. Two
deliberate mutations were applied after green and reverted, each killing the two
tests that own it.

## What the next reader must not assume

- Nothing was attempted. The answer says what is owed and nothing about whether
  a program is in any state. There is no encoder and no solver.
- Whether this is the list a solver will want is the next feature's question.
- Concurrency and crash behaviour are argued, not observed: the operation writes
  nothing and keeps nothing between requests, so there is no window to see from
  outside. No test proves it.
- No independent review took place, and the blind examiner has not read the
  candidate.
- Jev was unavailable in this run, so four open design questions were settled
  locally against SPEC.md and recorded as decisions.
- Only `core-0` programs were exercised, none of them large. No resource bound
  is enforced, and none was measured.
