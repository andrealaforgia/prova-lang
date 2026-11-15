# F17, step 1 of 5: the oracle

## What this feature is for

Every answer this tool gives should say what kind of statement it makes,
how far that statement reaches, which text it is about and which tool
produced it. Without that, a reader can take a run of two examples for a
statement about every input, or read an answer kept from last week as an
answer about the file edited since.

## What was promised

| Promise | In plain words |
|---|---|
| P1 | A completed answer says its claim kind, its scope, the revision of the source and the digest of the dependencies behind it. |
| P2 | A completed answer names the compiler, the encoding, the solver and the runtime it used, or says which do not apply and why. |
| P3 | An examples run calls itself an examples run and reaches the declared examples, no further. |
| P4 | A verify answer keeps what an obligation would have to show apart from what happened when something tried. |
| P5 | A failure of the tool itself is answered as a failure of the tool and reports nothing about a program. |
| P6 | An answer kept from before an edit does not read as an answer about the text held now. |

Seventeen sentences of the request are process instructions (where to
work, how to commit, which directory to leave alone). They are recorded
as not testable, with the reason for each.

## What was found in the code before any was written

One real conflict, reported to the owner and not yet settled:

The accepted test `tests/properties/test_i1_s4_p6_transcript.py` pins the
completed answer of the `evaluate` operation to exactly six top-level
fields and its claim to exactly two keys. P1 and P2 say "any completed
operation". The two cannot both hold as written: the new block cannot
reach the `evaluate` answer unless that test is widened, and the request
forbids editing an existing test's expected result.

The recorded decision, pending the owner's answer, is to carry the new
block on the six operations the profile names (`check`, `verify`,
`examples`, `parse`, `format`, `discover`) and to leave `evaluate`, which
this tool adds beyond the profile, exactly as it is.

Other decisions taken, with no conflict behind them:

- A failure of the tool is answered with the status `tool_failure`, which
  stays out of the published list of statuses of an answered request. Two
  accepted tests require that, and the manifest already explains why.
- The dependency digest is the SHA-256 of the profile, the published
  language and the four versions, published by `discover` so a client can
  compare a kept answer with the tool it holds now.
- An obligation keeps `result` for its logical standing and gains
  `execution_status`, whose word `unsupported` comes from the execution
  vocabulary of SPEC.md lines 270-284.
- No formal model: this change adds no state, no protocol, no concurrency
  and no crash behaviour.
- Jev was not asked: its key is absent from this environment, so the
  client exits 3. Every choice was settled locally.

## What was built in this step

Seven test files, all new, none of them editing anything that existed:

- `tests/acceptance/test_f17_b1_every_answer_says_what_it_stands_on.py`
- `tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py`
- `tests/acceptance/test_f17_b3_an_examples_run_reaches_only_the_declared_examples.py`
- `tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py`
- `tests/acceptance/test_f17_b5_an_answer_about_an_older_source_says_so.py`
- `tests/unit/test_f17_b6_a_failure_of_the_tool_is_not_an_answer_about_a_program.py`
- `tests/properties/test_f17_provenance_laws.py`

They were run against the tool as it stands today, before any production
line was written. Fourteen of the twenty checks failed, each because the
promised thing is absent; six passed, because they state what the tool
already does and what this change must not break.

## What this step does not prove

- That a failure of the tool can be reached through the command's own
  input. It cannot, without planting a defect, so the failure is induced
  through the public entry point the command calls, with a request object
  that breaks while a field of it is read. The documents keep that limit.
- Nothing about the `evaluate` answer, which is the open question above.

## Still open

The one question for the owner, above.
