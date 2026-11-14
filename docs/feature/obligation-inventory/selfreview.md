# Self-review: what I checked in my own work, and what I could not

Seventeen dimensions were answered with evidence; none was left as debt. The
full answers are in the run record and in `docs/obligation-inventory/`.

## What was fixed during the review

`docs/spec-trace.md` §5 still said nothing in `verify-0` existed, and the
`verify-0` row of `docs/ROADMAP.md` still read "Not started". Both were false
the moment the code landed. Rows 5.1, 5.2, 5.6 and 5.8 now read Partial, each
saying what is listed and that nothing is ever attempted; the summary counts
moved with them, and the roadmap row reads "Inventory only, nothing attempted".

## What I accepted as a cost, in writing

- The parse-and-check preamble is now written four times in `service.py`. The
  Owner decided this against the alternative of extracting it, and the
  extraction is tracked as a roadmap follow-up.
- The obligation value objects carry three to five fields instead of two,
  because an entry's detail -- who is called, how many clauses, which example --
  belongs beside the entry a reader sees.

## The one stale line in the record

The oracle's edge matrix predicted the category `unknown_function` for a call
to a function the program never declares. The checker really gives
`unbound_name`; `unknown_function` is the category for an *evaluate* request
naming a function that does not exist. The promise is unchanged -- `verify`
refuses with the whole-program check's own diagnostics and lists nothing -- and
the test and the documents name the real category. The matrix row in the
recorded oracle is the one line that still names the guess.

## What a self-review cannot do

I wrote this change, so nothing here is an independent reading of it. Two
deliberate mutations show the tests can fail, which is my own check, not
someone else's judgment. No independent reviewer took part in this run, and the
blind examiner has not read the candidate. Both still have to happen before it
lands.
