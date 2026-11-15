# F9 — craft: what was built, and what was measured

## The three commits

| Commit | What it does | Why it is separate |
|---|---|---|
| `6ee913b` | one `Refusal` owner answers a source the tool cannot check | behaviour-preserving; it edits no test, and it is what makes the new status land in one place instead of four |
| `f17fe1d` | the checks, and the fourteen preserved counterexamples wired in | recorded red before any source changed |
| `7e79d26` | the profile boundary and the `unsupported` status | the behaviour |
| `5701c86` | the four findings of the independent review of `1ea859a` | a review fix is its own commit, so what it changed stays readable |

Commit ids are those after the rebase onto `903f420`, where F7 is merged.

The history was reordered once so the prefactor stands before the checks; the tree is
byte-identical to what it was before the reorder, and the backup branch
`backup-f9-before-reorder` holds the earlier order.

## What the source now does

`ProfileBoundary` reads the reader's tree before the typed tree is built. It refuses the
first construct `core-0` does not have, in source order, naming it and the line and
column it stands on. The service turns that into the `unsupported` status, which is
built by the same `Refusal` the four source-reading operations already share, so all
four answer it identically without any of them knowing about it.

A refusal now reads, for example:

> the operator `'/'` is unsupported in the core-0 profile: core-0 declares no division
> operator, so the tool can give it no meaning here; write the calculation with an
> operator core-0 has, `'+'`, `'-'` or `'*'`; exact division arrives with a later numeric
> profile

What failed, why it cannot work here, how to write it instead — and a `location` and a
`construct` field beside it, so a caller does not have to read the prose.

## Measurements, each with the command that produced it

| What | Command | Result |
|---|---|---|
| full suite, after, rebased onto F7 | `uv run pytest -q tests --durations=5` | **981 passed**, exit 0, 93.6 s |
| full suite, before the rebase | `uv run pytest -q tests --durations=10` | 949 passed, exit 0, 103.1 s |
| full suite, after the prefactor only | `uv run pytest -q tests` | 935 passed, 14 failed — the 14 recorded red F9 cases and nothing else |
| the pre-existing suite, after the prefactor | `uv run pytest -q tests -k "not f9"` | 932 passed, 17 deselected, 98.5 s |
| the refactor check, exported trees | `uv run pytest -q tests/unit` | 53 passed before and 53 after |
| lint, against the pre-feature tree | `uvx ruff check --output-format=concise src tests docs` | exit 1 on both trees, **0 new findings** |
| spec-trace probes | `uv run python docs/spec-trace/probe.py` | 45/53 agree; G3, G4 and L5 agree for the first time |

**Test cost receipt.** The new test files were run nine times in a row:
`uv run pytest -q tests -k f9` — 17 passed every time, no flake. Median 1.07 s, slowest
run 1.09 s (wall clock 1.20 s median, 1.22 s slowest). The review fixes took the new
checks to 19, which run in 1.07 s. The slowest single new test is
0.08 s; every one that drives the real command is under a tenth of a second, and the
four generated laws are 0.02 s or less because they ask the service in process.

**Why the refactor check is `tests/unit` and not the whole suite.** The tool runs the
refactor check in a tree exported without `.git`. Fifteen existing tests read the
repository's git history — four property modules call `git show <sha>:SPEC.md` at
collection time, and the `char1` acceptance tests check a protected example at a named
revision — so they fail identically before and after in any exported tree, and pytest
reports the collection errors as an interrupted run. `tests/unit` runs clean there and
covers the refused-source path the prefactor moved. The whole-suite evidence for the
prefactor is the second and third rows above, run in the real worktree.

## Jev

`typesafe: unavailable` — `TYPESAFE_API_KEY` is absent from the environment; the client
was run from a shell command, not a tool kernel, and exited 3. The four questions it
would have been asked — the status name, the top-level rule, how the manifest publishes
a status, and how to read acceptance criterion 4 — were decided locally, recorded as
DEC1–DEC4, and accepted by the owner at the oracle pause.

## What is not verified

- Only the **first** out-of-profile construct in a source is reported. A reader repairing
  a file that uses several must run the tool again after each. Owner accepted this as a
  stated limit.
- `Decimal` and `Text` written as **type** names are still answered `unbound_type`
  (DEC6). A signature naming `Decimal` with no decimal literal in it therefore still gets
  the older, less honest answer.
- A value supplied as an `evaluate` **argument** keeps `malformed_value` (DEC7). The
  boundary is read over source text only.
- A trailing call to a function the source does **not** declare keeps today's spelling
  refusal (DEC2), because nothing in the source distinguishes it from a misspelled
  declaration word.
- The `tool_failure` status the command wrapper produces for a request that is not JSON
  is not published in the manifest; the manifest lists the five statuses the service
  itself answers with.

## The independent review of `1ea859a`, and what it changed

The reviewer rejected the candidate with four findings. All four are fixed in `5701c86`,
and each fix was probed by putting the defect back and watching a check fail:

| # | Finding | Fix | Probe: reverting it turns red |
|---|---|---|---|
| 1 (high) | a valid `defn` in one pair of parentheses too many, `((f) 1)` and `()` moved from `syntax` to `unsupported`, with a remedy no respelling can follow | a form whose head is not a symbol is not read as an expression, so it keeps the refusal that owns it; three controls pin it | `test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else` and the new control, 2 failed |
| 2 (medium) | the `construct` response field had no observation — deleting it kept every test green | one observation per construct family pins the word, and the five words are now stable tokens rather than prose | 2 failed |
| 3 (medium) | the `if not construct:` guard was unreachable and unobserved | deleted; `UnsupportedConstruct` carries the `OutOfProfileConstruct` itself, so no empty name can exist | passing `""` instead of the value object: 13 failed |
| 4 (low) | `tool_failure` is answered by the command, and the manifest did not say its list covers an answered request | the manifest says so, and a check pins the sentence | 1 failed |

Finding 1 is the one that mattered: the first version answered a misplaced parenthesis
with "core-0 does not have this and never will", which is both untrue and unactionable.
The boundary now has to recognise an expression before it refuses one.
