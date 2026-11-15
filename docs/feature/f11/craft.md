# F11 - craft: what was built and what it costs

## Two commits, in this order

1. `80d766b` **prefactor, behaviour unchanged, no test edited.** The operator
   table now carries the rule its operands are read by and the type it answers,
   and the four-branch chain in the operand checks became one question asked of
   that rule. The type names became one table that also says what the values of
   each type are, with the set of names read from it. `uv run pytest -q
   tests/unit` passed on the parent commit and on this commit (70 tests).
2. `9b5754c` **the feature.** A new module, `src/prova/manifest.py`, owns the
   catalogue of operations; `src/prova/service.py` gains one import, one
   spread of the new parts into the answer, one sentence of documentation, and
   reads the names of the three request fields from the published fields.

## What an agent now reads from `discover`

| Part | What it says |
|---|---|
| `categories` | the seven categories of SPEC.md, each with the operation covering it and whether that operation can be called |
| `operation_schemas` | per operation an agent may call: the fields its request takes and the fields its answer carries, each with its kind, when it is there and what it is for |
| `language` | the three types of core-0 with what their values are, and the eleven operators with the types each takes and answers |
| `beyond_profile` | `evaluate`, with the reason it is this tool's own and not one of SPEC.md's categories |

The parts that were there before - the profile, the operations with their
availability, the statuses, the diagnostic schemas, the contract report and the
resource limits - are unchanged, and the existing operation list keeps the exact
shape an existing test compares it with.

## What cannot be built wrongly, and what is only tested

Built in: a catalogue over a different set of names than the dispatcher
advertises raises rather than publishing; an operation carries one standing, so
it cannot be in a category and beyond the profile at once, nor in neither; an
available operation without its two shapes, or a refused one carrying them,
raises.

Tested only: that the *kind* of value each published field names is the kind the
reader really refuses (LAW1), and that an answer carries exactly the fields
published for it (LAW2). Those two are generated laws over the real command, not
guarantees of construction. The refusal messages belong to the robustness work
and were not rewritten.

## Test cost, measured

The whole suite: `uv run pytest -q tests --durations=10`, **1153 passed in
137.09 s** (the run the delivery record keeps; a second run of the same tree
took 141.02 s) (1136 before this change, 17 added). Before the change the fifteen
that state the promises were seen failing in 1.95 s, each because the promised
part of the manifest was absent; the two added later, on the module itself, are
named under the review repairs below.

The seven files added, run nine times in a row, all nine green, 17 tests each:

| | seconds |
|---|---|
| median of the nine runs | 4.82 |
| slowest of the nine runs | 5.37 |
| slowest single test | 1.02 (`test_the_published_signature_of_an_operator_is_the_one_the_tool_keeps`) |

Fifteen of the seventeen drive the real `prova` command as a subprocess, so they
are integration tests and none of them is under the 10 ms unit budget; the
slowest is just over one second and the whole set is under six. The two that
read the module directly run in well under 10 ms each. No test sleeps, and none
reads the clock to decide its outcome.

## Mechanical checks

The repository declares no lint and no type checker: its CI runs
`uv run pytest -q tests` and nothing else. The scorecard is therefore
`uv run python -m compileall -q src tests`, which exits 0 on this tree and on
the pre-feature tree. No new mechanical finding.

## Jev

`typesafe: unavailable` - `TYPESAFE_API_KEY` is absent from the process
environment and from the login shell, so the client exits 3 before any call.
The three choices it would have been asked (where the catalogue lives, where the
operator signatures come from, whether a formal model pays) were settled locally
and are written in `design.md`.

## What an independent review changed

The review read the manifest against the code and found it accurate, but
rejected the work on one criterion and asked for two more repairs. All three are
done:

1. **The three properties were not derandomised.** Their docstring said they
   were, and the settings did not say it: two consecutive runs drew different
   cases, so a verdict depended on what the generator happened to draw. With
   `derandomize=True` two consecutive runs now send the same 52 requests, line
   for line (0 of 52 differ); with it taken out again, 33 of the same 52 differ.
2. **Two alternatives were typed as `object`.** An operation's standing and its
   traffic, and the operand rule of an operator, now name the two shapes each of
   them can have, so a reader sees the alternatives in the signature.
3. **A category claimed twice was silently overwritten.** The second claim is
   now refused, naming both operations, the category and where to repair it, and
   leaving the first claim exactly as it was. Two operations claiming one
   category cannot be caused by a request, so the check is observed on the module
   itself in `tests/unit/test_manifest_catalogue.py`. With the refusal taken out,
   that test fails and its control (two categories, two operations) still passes.

## Two findings that are not this change's

- **Pre-existing, reported to its owner, not repaired here.** A `check` request
  whose source carries a lone surrogate character (`"\udccc"`) ends in a
  `UnicodeEncodeError` while the revision of the source is computed, instead of
  being answered. It is older than this change, this change neither caused nor
  touched it, and repairing it would widen the delivery; the roadmap carries it.
- A fifth observation was recorded as informational by the reviewer and asks for
  no change here; its text is in the review record, not restated from memory.

## What is still open

Nothing in the code. The self-review step is next; it needs the independent
review entry, which an executor may not write for itself.
