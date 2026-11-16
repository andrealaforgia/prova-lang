# R3 craft: what was built

## What changed, and where

| File | What it now owns |
|---|---|
| `src/prova/values.py` | `DigitsWritten`, the 4000 digits an answer writes, and `TooLargeToWrite`, raised by `render` instead of letting the interpreter refuse the number |
| `src/prova/checker.py` | one more refusal category, `written_integer_digits_exceeded`, placed at a declaration and carrying two counts |
| `src/prova/service.py` | `RequestNesting` (64 arrays and objects, counted before the text is read as JSON), `unwritable_budget_variable`, `printable_answer`, the refusal an operation field gets, the answer a computed integer too large to write gets, and the two new documentation entries |
| `src/prova/budgets.py` | a budget variable refused by the digits it writes, before anything tries to read it as a number |
| `src/prova/__main__.py` | the two new checks at the boundary, and every answer printed through the one printer |

Nothing was renamed and nothing was removed. `encoding.py`, `solving.py`,
`discharge.py` and `obligations.py`, which another delivery owns, are
untouched.

## How each input is answered now

1. **An integer too large to write.** `values.render` asks `DigitsWritten`
   whether the value passes 4000 digits before it writes anything, using
   the bits of the number so the cheap question is asked first. Past the
   limit it raises; `evaluate` and `examples` answer
   `resource_exhausted` with the refusal standing at the function that
   computed the number, carrying 4000 beside the digits reached and no
   result. A value at or below the limit is written exactly as before.
2. **A budget variable of 5000 digits.** `Budget.lowered_to` compares the
   digits written, after leading zeros, with the digits of the number
   this tool declares, and refuses by name before `int` is ever called.
   A zero-padded small number is still read, so nothing a caller could
   lower to has changed.
3. **A request nesting 20000 deep.** The command counts the arrays and
   objects of the request text before the JSON reader sees it, stepping
   over quoted text as that reader does, and stops counting as soon as
   the 64 is passed. A deeper request is `invalid_input` with
   `malformed_request`. The bounded read of F14 still runs first, so a
   request too long to read is still refused unread.
4. **Half a character echoed back.** One rule decides whether a text can
   be written as UTF-8. The operation field now asks it (texts inside a
   list or an object there too), the budget variables ask it before they
   are read, and the one place an answer becomes characters asks it of
   the whole answer. None of the three repeats the text it refuses.

## What was measured

| Check | Command | Result |
|---|---|---|
| Whole suite | `uv run pytest -q tests --durations=10` | 1344 passed in 208.38s, exit 0 (the run the workspace recorded after the review fixes) |
| The new tests, nine times | the six new files, `-q --durations=5` | passed all nine times; median run 1.30s, slowest run 1.35s (measured on the first 21 of the 22, before the last unit test was added) |
| Slowest new test | same runs | 0.10s, the request too long to read |
| Mechanical check | `uv run python -m compileall -q src tests` | exit 0 here and on the pre-feature tree: no new finding |

The suite was 1317 tests before this change and is 1344 now: 27 added,
none edited, none removed.

## What the independent review changed

The review rejected the first version and named ten findings; seven were
repaired here.

| Finding | What was wrong | What it is now |
|---|---|---|
| F1 | the refusal for a value the *interpreter* will not write carried the tool's own 4000 as the digits reached | it carries the number the interpreter writes as the limit and the real digit count as what was reached, and a test starts the command with `PYTHONINTMAXSTRDIGITS=1000` to see it |
| F2 | a budget written as `123456` or `10485761` was refused "by its length", which is false: a reader reads both | only a run of digits longer than the interpreter turns into one number is refused by length; every number a reader reads keeps the sentence it had |
| F3, F4 | a negative result past the limit, and the first number past the limit, were not pinned | the family now carries 3999, 4000, 4001 and ten to the 4000, above and below zero |
| F8 | the decision table said the deepest request nests 3 | it says 2, which is what the shipped sentence and the measurement say |
| F9 | two conversion constants were written as bare numbers | they are named once, from `math` |
| F10 | the documented length did not say whether the sign counts | it says the sign is left out, as the limit on a literal already does |

F5 and F6 are recorded narrowings, not defects. F7 -- a 1000-digit
*literal* read under `PYTHONINTMAXSTRDIGITS=640` ending in
`tool_failure` from `reader.py` -- is a pre-existing defect of the digit
limit R2 added: it behaves identically on the tree before this change,
and it is out of this delivery's scope.

Each repair was probed by putting the defect back: every one of the four
mutants turned its test red, and the tree was restored afterwards.

## What is not proved here

A budget variable whose name is not UTF-8 text is observed only through
a real command, because a running process cannot hold one in memory.
The behaviour of this tool under an interpreter whose digit limit is
lowered is proved for a value it *computes*, not for a literal a source
writes: that path is F7 above, which this delivery does not touch.
