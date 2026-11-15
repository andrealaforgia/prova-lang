# F11 - self-review and the review that preceded it

## What the independent review found

The reviewer read the manifest against the code, found it accurate, killed ten
of ten mutants and ran the suite green - and still rejected the candidate, on
one criterion. Three findings were this change's to repair and are repaired; two
are not this change's. All five, and what became of them, are in
`craft.md` under "What an independent review changed" and "Two findings that are
not this change's".

The rejection is worth keeping in view: a document said the three generated laws
were derandomised and the settings did not say it. Nothing was wrong with the
manifest; what was wrong was that a verdict about it depended on what the
generator happened to draw that day. A claim in prose that the code does not
make is a defect of the same kind as a wrong answer.

## What the self-review changed

Answering the seventeen dimensions turned up one more stale claim, this time in
the delivery record rather than in a document: the design step declared two
look-alike types, `RequestField` and `AnswerField`, and during the work they
became one `Field` with named constructors (`must_be_sent`, `may_be_sent`,
`in_every_answer`, `when_completed`, `when`). The code is the better of the two;
the record was simply out of date, and the tool refused the self-review until the
design was recorded again. Design revision 2 says what the code says.

Three dimensions are recorded as `fixed:` rather than `pass`, each with the
evidence of the repair: the derandomised laws, the two alternatives that were
typed as `object`, and the category a second operation could claim in silence.
One is recorded as `n/a`: no formal model, because the manifest is computed from
constant tables in one process, with no shared state, no protocol of more than
one step and no crash window.

## What a later reader should know

The craft step is marked stale and its replay is refused. The branch was rebased
after the craft run, so the history from the recorded pre-feature commit to HEAD
now starts with the commit `main` moved to, and the prefactor is no longer the
first commit counted from that base. The craft record keeps the run it measured,
the suite was green again on the rebased tree, and the owner left that refusal
standing rather than papering over it. It is a fact about the recording, not
about the code.
