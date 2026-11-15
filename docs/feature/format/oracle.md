# F15 oracle — one canonical spelling, comments kept

## What this step decided

The Owner asked for one thing: run `format` on a program the tool accepts and
get the same text every time, with the reader's comments still in it. Seven
promises carry that outcome, and every sentence of the request maps either to
one of them or to a reason it states no behaviour (most of them are process:
where to work, what to write in the commit, which directory to leave alone).

### The canonical layout

Nobody had written the layout down before, and SPEC.md lines 83-84 say it must
be fixed in conformance fixtures *before* `format` ships. So it is written down
here, as six rules, and published as three hand-computed pairs under
`conformance/format/`. Each pair is a source a reader might write beside the one
text the tool answers for it. Both halves were written by hand from the rules,
not by running a formatter.

1. Every declaration starts at column 1; exactly one empty line stands between
   two declarations; the text ends with exactly one line terminator.
2. A `deftype` is written on one line.
3. A `defn` is broken: its name stands on the opening line, and its signature,
   its `requires`, its `ensures`, its `examples` and its body each start on a
   line of their own, two columns further in.
4. An `examples` clause is broken, one example per line.
5. Every other form is written on one line, unless it holds a `let`, an `if` or
   a `match` anywhere inside it. Such a form writes its head and — when that
   part is itself written on one line — its first part on the opening line, and
   every remaining part on its own line two columns further in.
6. Whole numbers are written canonically: no leading plus, no leading zero,
   and `-0` written `0`.

Nothing here measures a line width. The layout is a function of the tree alone,
which is what makes writing a program out twice give the same characters.

### Where the comments go

Each comment stands on its own line above the declaration that follows it, in
the order the reader wrote them, with no empty line between the comment and that
declaration. A comment no declaration follows stands after the last one,
separated by an empty line.

A comment written *inside* a declaration therefore rises to stand above the next
declaration. That is what SPEC.md line 63 asks for ("the following syntax node
or the document end"), and it is also what makes the layout idempotent: write
the program out again and the rule finds that comment exactly where it had
already put it.

## What was built

Three published pairs — `integers`, `comments`, `shapes` — and eight test files:
seven acceptance files that drive the tool through its public JSON surface, and
one property file that states the four laws over generated programs.

The generator writes programs a reader might have written: a closed set of
declaration shapes, with the whole numbers, their spelling, the layout of each
declaration and the placing of the comments all varied. It was run against the
tool as it stands today: 200 generated programs are accepted, their examples all
pass, and their comments come back in the order they were written. So a failure
of a law will be a failure of the formatter, not of the generator.

Every one of these checks was watched failing on the tree as it was before this
work: 27 failed, 5 passed. The five that pass are the part of the promise the
tool already keeps — today `format` refuses *everything*, and a refusal already
carries no text.

## What is still open

Two sentences of the request contradict something the repository already does.
Both are recorded with the question they raise, and both are asked of the Owner
at this pause.

1. **One pinned expectation.** `tests/unit/test_service_discover.py` asserts
   that the published operations list carries `"format": "unavailable"`. Making
   formatting available makes that line false. The request allows this one
   expectation to change minimally; the proposal is to change that single word,
   in a commit of its own, and list it in the report.
2. **"the results equal those of the original source".** Every completed answer
   carries `source_digest`, the SHA-256 of the exact characters submitted. Two
   different texts can never carry the same one. The proposal is to read the
   sentence as the status, the diagnostics and the result payload, leaving each
   answer to say honestly which text it is about.

## What this step does not claim

Nothing here shows that the formatter works: no formatter exists yet. It shows
that the checks fail for the right reason on the tree as it was, that the
published pairs are programs the tool accepts, and that the generator produces
programs it accepts. Whether the layout is a *good* layout is a judgement the
Owner was offered and delegated; the fixtures are there to be reviewed.
