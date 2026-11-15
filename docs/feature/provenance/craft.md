# F17, step 3 of 5: the craft

## What was built

| Part | Where | What it owns |
|---|---|---|
| `Digest` | `src/prova/provenance.py` | the SHA-256 of a text, written in one place |
| `Version` | `src/prova/provenance.py` | one of the four things behind an answer, built as used or as not applicable, never as both and never empty |
| `Versions` | `src/prova/provenance.py` | exactly the four the authority names; another set refuses to be built |
| `Provenance` | `src/prova/provenance.py` | the digest over this tool and its language, beside those versions |
| `_stands_on` | `src/prova/service.py` | the one place an answer learns what it stands on |
| `tool_failure` | `src/prova/service.py` | the answer a run that failed inside the tool gives |
| `execution_status` | `src/prova/obligations.py` | what happened to the attempt, beside what the obligation stands as |
| `stands_on` field | `src/prova/manifest.py` | the published shape, for the six operations that carry it |

## The name a client reads

The field is spelled `stands_on`, not `provenance`. The word provenance
says the concept best and names the module, but it carries `proven`
inside it, and several accepted tests refuse any answer whose text says
something was proven, reading the text as characters rather than as
words. The whole suite named that collision the first time the change was
run; the field was renamed, and no test was edited. The reason is written
in `manifest.py` and in the class that publishes it, so nobody renames it
back without reading why.

## What a completed answer now carries

```json
"stands_on": {
  "dependency_digest": "7d6459...9c5",
  "versions": {
    "compiler": "prova 0.0.0",
    "encoding": "not applicable: this tool turns no obligation into the language of a solver, so nothing here is encoded for one",
    "solver": "not applicable: this tool has no solver and attempts none of the obligations it lists",
    "runtime": "cpython 3.12.13"
  }
}
```

The six operations of the profile carry it. The `evaluate` operation does
not: that is the gap the owner accepted, and `discover` says so in words
under `documentation.stands_on`, so a client reading the manifest is not
left to find it out.

## The order of the commits

1. A prefactor commit moves the SHA-256 out of `SourceRevision` into
   `provenance.Digest`, which `SourceRevision` then asks. No test edited,
   no field added, the unit suite green before and after.
2. The feature commit adds everything above.

## What was run, and what it cost

Measured on the change as it now stands, after the repairs below.

| Command | Result |
|---|---|
| `uv run pytest -q tests --durations=10` | 1317 passed in 215.47 s, exit 0 |
| `uv run pytest -q tests/unit` on the prefactor commit and on its parent | exit 0 on both |
| `uv run python -m compileall -q src tests` | exit 0 here and on the tree before the change; no new finding |

The seven new test files were then run nine times in a row. All nine runs
passed all 20 checks: 6.61, 6.59, 6.67, 6.59, 6.61, 6.67, 6.58, 6.63 and
6.56 seconds, a median of 6.61 s and a slowest run of 6.67 s. Each of the
three laws now sends one request per cell of its grid, which is what the
file costs; the three checks that start no process at all run in under
5 ms each. Nothing here sleeps or reads a clock to decide an outcome.

An earlier count is worth keeping as a warning: this document first said
1297 passed, the figure measured before the branch was brought onto the
current main and before the repairs below. A count copied forward is a
count nobody measured.

## What changed after the review

| Finding | What was wrong | What was done |
|---|---|---|
| F1 | `discover` published its claim, what it stands on and its manifest as fields every answer carries, and the sentence beside that said a condition there could never fail. Under `PROVA_BUDGET_ANSWER_SIZE=200` the answer is a refusal carrying none of the three. | They are published as every other operation does, when the answer completes; the false sentence is gone with the method that held it. A new law reads what is left of an answer a budget stopped against what is published. Re-injecting the old publication fails that law. |
| F2 | This document reported a count measured on an earlier tree. | Re-measured on the final tree and reported above. |
| F3 | The sentence published beside the `verify` shape named only one of an entry's two fields. | It names both, and says the two are read apart. |
| F4 | Two of the three laws drew 12 cases from a closed grid of 30 cells. | They draw one case per cell. Removing the block from one operation alone now fails the first law. |
| F5 | The word `holds` appears in two messages that were there before this change. | Nothing: they are not this change's, and neither claims anything was shown. |

## What this step does not prove

- Nothing about `evaluate`, which keeps the answer it had.
- The failure of the tool is observed through the public entry point the
  command calls, not through the command's own input: no input of the
  command can make the tool fail inside itself without a defect planted
  on purpose.
