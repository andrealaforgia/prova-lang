# F6 — craft: what was built, what it costs, what was proved

## What was built

Four values in `src/prova/syntax.py` own the new rules at the reader-to-tree
boundary — `ValueName`, `TypeName`, `MarkerToken` and `AtLeastOne` — and one
builder in `src/prova/service.py`, `_syntax_diagnostic`, turns a reader refusal
into the one JSON diagnostic every source-reading operation answers with, now
carrying the line and column the reader already held. `src/prova/checker.py` was
not touched.

After the independent review, the same boundary was made **total**: every
grammar position core-0 fixes is read through one owner (`_required_at`,
`_required_list_at`, `_parse_pair`, `_parse_binding`, `_parse_clause`,
`MATCH_CLAUSES`) that refuses what is missing or of the wrong kind where it
stands, instead of indexing it raw. No blanket `except` was added anywhere.

## Test cost receipt

Nine consecutive runs of the eight F6 test files, each run `33 passed`:

| Measure | Value |
|---|---|
| Runs | 9 of 9 passed (no flake) |
| Wall time per run | 2.11, 2.26, 2.28, 2.30, 2.17, 2.22, 2.29, 2.17, 2.20 s |
| Median run | **2.22 s** |
| Slowest run | **2.30 s** |
| Slowest single test | `test_every_word_the_language_reserves_is_refused_as_a_function_name`, 0.93–1.04 s |

Over budget, with its reason: that one test is above the 10 ms unit budget
because it starts the real `prova` command once for each of the 27 words core-0
reserves, through the real process boundary. It stays an acceptance test within
the seconds budget; the cheap in-process form of the same law is the generated
property in `tests/properties/test_f6_name_and_marker_spelling.py`.

Whole suite at the recorded candidate: `uv run pytest -q tests` → **890 passed
in 96.63 s**.

## What was probed

One hand probe for the feature's own promise: the reserved-word refusal was
removed from `ValueName` and
`tests/acceptance/test_f6_b1_a_function_named_as_a_reserved_word_is_refused.py`
went **3 failed, 1 passed**; the source was restored. The one passing test there
is the control that observes an unreserved name still accepted, which must not
fail for this break.

Ten further delete-checks, one per guard added for the reader's totality, each
turned its covering test red: `_required_at`, `_required_list_at`, the
`(name Type)` shape, the `let` binding shape, the `match` clause shape,
match-has-at-least-one-clause, nothing-after-the-effect,
signature-carries-a-parameter-list, pattern-constructor-is-a-symbol, and
constructor-is-not-a-builtin-type-name. The ninth found a real gap first: before
the shape "a pattern whose constructor is a form" was added to the enumerated
family, deleting that guard left every test green.

## What is still open

- `selfreview` is not recorded; the independent reviewer sees this delta first.
- Recording `oracle` revision 2 (promises P8, P9, P10) re-opened the pause after
  the oracle step, so `design` and `craft` are marked stale until the person
  accepts that revision; their content is unchanged.
- `syntax.BUILTIN_TYPE_NAMES` duplicates `checker.BUILTIN_TYPES`. The comment at
  its definition names the duplication: `checker.py` belongs to the delivery
  running beside this one, and reconciling the two sets is one line once that
  file is free.
