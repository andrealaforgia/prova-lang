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

## What was run

The commands and their output are in the brief, with the test cost
measured over nine runs of the new files.

## What this step does not prove

- Nothing about `evaluate`, which keeps the answer it had.
- The failure of the tool is observed through the public entry point the
  command calls, not through the command's own input: no input of the
  command can make the tool fail inside itself without a defect planted
  on purpose.
