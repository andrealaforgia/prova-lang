# Changes no test notices, and why each one is allowed to

`tools/mutate_encoder.py` walks the syntax of the four modules that
decide a verdict and makes every change its operators can make: 507
mutants over the translation, the solver port, the discharge decision
and the obligations. Each gets its own copy of the source tree, first on
the import path, with bytecode writing off, and a control runs before
any judging -- an unmutated copy must be green and a same-length mutant
red -- so the harness proves it carries nothing between runs.

Every mutant is asked the close-watching cells, then the slower
families. A mutant that survives both is asked the whole suite once.
What is left after that is a change no test in this repository notices,
and this file is where each one has to be accounted for.

## How a survivor is classified

| Class | Meaning | What it obliges |
|---|---|---|
| **(b)** | a demonstrated wrong `proved`, `disproved` or `unknown`: a program exists that shows the tool answering wrongly | write the program here, add a cell or an acceptance case, re-run the mutant until it is red |
| **(c)** | an argued equivalence: the change cannot alter any answer a reader acts on -- a message, a text, a count nobody reads, a limit no program approaches, performance | one line here with the argument, and nothing else |
| **(d)** | unreachable by design: the branch cannot be entered by any input the profile admits | one line here naming why it cannot be entered |

A class (b) survivor is a defect in the oracle and is not allowed to
remain. Classes (c) and (d) are allowed to remain **only** with their
line in this file.

## Survivors

**The whole-suite pass was stopped by the Owner part way through.** The
harness printed a line only for a mutant that survived a pass, never for
one a pass killed, so the output does not say how many of the 135 were
asked the whole suite before the stop -- only that **none of those it
reached survived it**. That silence is a defect of the harness, not a
result: the ledger added afterwards records every verdict as it is
decided, so the next run cannot lose this again.

The table below is therefore what is known and nothing more. Every row
survived the two cheap passes. A row is marked **not asked** where the
whole-suite pass did not reach it, which is all of them except those the
stop had already passed, and the output cannot say which those were.
**None of these rows is classified.** A mutant that no cheap cell
notices may well be killed by a test outside those passes -- the twenty
`_declare` reversals below swap each primitive's name with its meaning,
which the shipped-document test almost certainly catches, and that test
is in the suite but in neither cheap pass. Calling them survivors now
would be a claim this run did not earn.

### Argued, from the sample run that did complete

| Module | Function | Line | Operator | Class | Argument |
|---|---|---|---|---|---|
| `encoding.py` | (module level) | 39 | module constant: int constant +1 | (c) | `EXPANSION_LIMIT = 64` bounds how far calls are expanded, chosen rather than measured. The deepest expansion any program in the oracle needs is 3, so 63, 64 and 65 are indistinguishable to every test. A program that did approach the bound is answered `unknown` either way, with the bound named in its reason |
| `encoding.py` | (module level) | 39 | module constant: int constant -1 | (c) | the same bound, the same argument |

### Survived the two cheap passes, not classified

| Module | Function | Line | Operator | Whole suite |
|---|---|---|---|---|
| `discharge.py` | `(module level)` | 141 | module constant: True/False swap | not asked |
| `discharge.py` | `(module level)` | 55 | module constant: True/False swap | not asked |
| `discharge.py` | `(module level)` | 76 | module constant: True/False swap | not asked |
| `discharge.py` | `_finding_for` | 193 | call arguments reversed | not asked |
| `discharge.py` | `_if_answered_another_value` | 270 | call arguments reversed | not asked |
| `discharge.py` | `_if_answered_another_value` | 272 | call arguments reversed | not asked |
| `discharge.py` | `_value_of` | 302 | call arguments reversed | not asked |
| `discharge.py` | `_value_of` | 302 | int constant +1 | not asked |
| `discharge.py` | `_value_of` | 302 | int constant -1 | not asked |
| `discharge.py` | `_value_of` | 302 | int constant sign flip | not asked |
| `discharge.py` | `_value_of` | 303 | int constant -1 | not asked |
| `discharge.py` | `disclosure` | 162 | True/False swap | not asked |
| `discharge.py` | `not_attempted_because` | 126 | call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 101 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 102 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 103 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 104 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 109 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 114 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 118 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 133 | module constant: True/False swap | not asked |
| `encoding.py` | `(module level)` | 192 | module constant: True/False swap | not asked |
| `encoding.py` | `(module level)` | 225 | module constant: True/False swap | not asked |
| `encoding.py` | `(module level)` | 241 | module constant: True/False swap | not asked |
| `encoding.py` | `(module level)` | 249 | module constant: True/False swap | not asked |
| `encoding.py` | `(module level)` | 39 | module constant: int constant +1 | not asked |
| `encoding.py` | `(module level)` | 39 | module constant: int constant -1 | not asked |
| `encoding.py` | `(module level)` | 48 | module constant: True/False swap | not asked |
| `encoding.py` | `(module level)` | 66 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 71 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 76 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 77 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 78 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 79 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 80 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 83 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 88 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 89 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 92 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 93 | module constant: call arguments reversed | not asked |
| `encoding.py` | `(module level)` | 96 | module constant: call arguments reversed | not asked |
| `encoding.py` | `__init__` | 283 | int constant +1 | not asked |
| `encoding.py` | `__init__` | 283 | int constant -1 | not asked |
| `encoding.py` | `_constructor_owning` | 419 | int constant -1 | not asked |
| `encoding.py` | `_declare` | 59 | call arguments reversed | not asked |
| `encoding.py` | `_expanded_call` | 487 | int constant +1 | not asked |
| `encoding.py` | `_expanded_call` | 487 | int constant -1 | not asked |
| `encoding.py` | `_expanded_call` | 487 | int constant sign flip | not asked |
| `encoding.py` | `_expanded_call` | 488 | compare Gt to GtE | not asked |
| `encoding.py` | `_matched` | 471 | and/or swap | not asked |
| `encoding.py` | `_operator` | 381 | Add to Sub | not asked |
| `encoding.py` | `_operator` | 381 | operands reversed | not asked |
| `encoding.py` | `all_of` | 187 | int constant -1 | not asked |
| `encoding.py` | `all_of` | 187 | int constant sign flip | not asked |
| `encoding.py` | `all_of` | 188 | int constant -1 | not asked |
| `obligations.py` | `(module level)` | 113 | module constant: True/False swap | not asked |
| `obligations.py` | `(module level)` | 125 | module constant: True/False swap | not asked |
| `obligations.py` | `(module level)` | 136 | module constant: True/False swap | not asked |
| `obligations.py` | `(module level)` | 148 | module constant: True/False swap | not asked |
| `obligations.py` | `(module level)` | 164 | module constant: True/False swap | not asked |
| `obligations.py` | `(module level)` | 454 | module constant: True/False swap | not asked |
| `obligations.py` | `(module level)` | 98 | module constant: True/False swap | not asked |
| `obligations.py` | `__post_init__` | 466 | int constant +1 | not asked |
| `obligations.py` | `_by_kind` | 559 | Add to Sub | not asked |
| `obligations.py` | `_by_kind` | 559 | int constant +1 | not asked |
| `obligations.py` | `_by_kind` | 559 | int constant -1 | not asked |
| `obligations.py` | `_by_kind` | 559 | int constant sign flip | not asked |
| `obligations.py` | `_by_kind` | 559 | operands reversed | not asked |
| `obligations.py` | `_by_result` | 527 | operands reversed | not asked |
| `obligations.py` | `_in_scope_at_the_call` | 278 | int constant -1 | not asked |
| `obligations.py` | `_note` | 543 | Add to Sub | not asked |
| `obligations.py` | `_note` | 543 | int constant +1 | not asked |
| `obligations.py` | `_note` | 543 | int constant -1 | not asked |
| `obligations.py` | `_note` | 543 | operands reversed | not asked |
| `obligations.py` | `_note` | 546 | call arguments reversed | not asked |
| `obligations.py` | `_note` | 546 | int constant +1 | not asked |
| `obligations.py` | `_note` | 546 | int constant -1 | not asked |
| `obligations.py` | `_note` | 547 | call arguments reversed | not asked |
| `obligations.py` | `_note` | 547 | int constant +1 | not asked |
| `obligations.py` | `_note` | 547 | int constant -1 | not asked |
| `obligations.py` | `_note` | 548 | call arguments reversed | not asked |
| `obligations.py` | `_note` | 548 | int constant +1 | not asked |
| `obligations.py` | `_note` | 548 | int constant -1 | not asked |
| `obligations.py` | `_note` | 549 | call arguments reversed | not asked |
| `obligations.py` | `_note` | 549 | int constant +1 | not asked |
| `obligations.py` | `_note` | 549 | int constant -1 | not asked |
| `obligations.py` | `_owed_by` | 572 | Add to Sub | not asked |
| `obligations.py` | `_owed_by` | 572 | operands reversed | not asked |
| `obligations.py` | `_parts_of` | 696 | operands reversed | not asked |
| `obligations.py` | `_parts_of_match` | 719 | operands reversed | not asked |
| `obligations.py` | `_parts_of_match` | 721 | operands reversed | not asked |
| `obligations.py` | `as_dict` | 500 | operands reversed | not asked |
| `obligations.py` | `as_dict` | 504 | call arguments reversed | not asked |
| `obligations.py` | `pattern_text` | 802 | branches of a conditional swapped | not asked |
| `obligations.py` | `text` | 187 | int constant -1 | not asked |
| `obligations.py` | `text_of` | 741 | branches of a conditional swapped | not asked |
| `obligations.py` | `text_of` | 750 | call arguments reversed | not asked |
| `obligations.py` | `text_of` | 752 | call arguments reversed | not asked |
| `obligations.py` | `text_of` | 754 | call arguments reversed | not asked |
| `obligations.py` | `text_of` | 759 | call arguments reversed | not asked |
| `solving.py` | `(module level)` | 221 | module constant: int constant -1 | not asked |
| `solving.py` | `(module level)` | 221 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 222 | module constant: int constant -1 | not asked |
| `solving.py` | `(module level)` | 223 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 223 | module constant: operands reversed | not asked |
| `solving.py` | `(module level)` | 224 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 225 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 225 | module constant: operands reversed | not asked |
| `solving.py` | `(module level)` | 226 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 227 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 228 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 229 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 230 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 233 | module constant: int constant -1 | not asked |
| `solving.py` | `(module level)` | 35 | module constant: int constant +1 | not asked |
| `solving.py` | `(module level)` | 35 | module constant: int constant -1 | not asked |
| `solving.py` | `(module level)` | 35 | module constant: int constant sign flip | not asked |
| `solving.py` | `(module level)` | 38 | module constant: True/False swap | not asked |
| `solving.py` | `(module level)` | 44 | module constant: True/False swap | not asked |
| `solving.py` | `(module level)` | 62 | module constant: True/False swap | not asked |
| `solving.py` | `(module level)` | 71 | module constant: True/False swap | not asked |
| `solving.py` | `__init__` | 309 | operands reversed | not asked |
| `solving.py` | `_written` | 362 | operands reversed | not asked |
| `solving.py` | `asked` | 106 | compare Lt to LtE | not asked |
| `solving.py` | `asked` | 107 | call arguments reversed | not asked |
| `solving.py` | `could_not_tell` | 265 | operands reversed | not asked |
| `solving.py` | `could_not_tell` | 267 | branches of a conditional swapped | not asked |

## What this file does not claim

That the four modules are correct. A mutation harness searches for
changes the tests cannot see; it says nothing about changes nobody
thought to make, and nothing about the solver, the parser or the type
checker, which stay trusted. Nor does a (c) argument become true by
being written down: each one is an argument a reviewer can read and
reject.
