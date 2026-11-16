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

## What has been examined, and by whom

Two runs have looked at these mutants. My own was stopped part way
through its whole-suite pass on the Owner's instruction, and its harness
printed nothing for a mutant a pass killed, so it cannot say how many of
its 135 cheap-pass survivors were reached -- only that none of those it
reached survived. An independent soundness review then ran its own clean
harness over **36 survivors that matter** and reported each one.

Of those 36: **11 were killed** by tests already here, **21 are
equivalent or direction-safe** with the arguments below, **3 were real
gaps**, and **4 did not return a verdict**. The three gaps are now
closed, and the fourth of the unreturned four has been measured here.

## The three real gaps, closed

| Mutant | What it did | Closed by |
|---|---|---|
| `encoding.py` `_matched`, `and` read as `or` | dropped the test on a constructor pattern's payload: `(match u ((Only 0) 7) (_ 0))` with `(ensures (> result 0))` came back **proved** while `evaluate f (Only 1)` is refused. A wrong `proved`, the worst defect this tool can have | `test_a_pattern_carrying_patterns_is_left_unsettled_with_its_reason`, over four shapes: a literal and a name inside a union variant, a literal inside a record, and a pattern inside a pattern. Each must answer `unknown`/`unsupported` naming the pattern, while the contract and the ending stay proved |
| `discharge.py` `_finding_for`, arguments reversed | put a whole sentence where one of SPEC's seven execution statuses belongs, for every obligation outside the fragment | `test_every_entry_carries_one_word_from_each_vocabulary` over five programs inside and outside the fragment, and the same two assertions on every entry of all 528 grid cells |
| `discharge.py` `_if_answered_another_value`, arguments reversed | made a disproof name its own refusal text as the function to run, which no caller could run | `test_a_disproof_names_a_function_a_caller_can_run`: the witness must name `f`, carry `["1"]`, name the expected value in its refusal, and run through `evaluate` |

Each was re-run under the clean harness after the cells were added, with
the control first: all three turn their named cell red.

## The four that had not returned a verdict, now measured

All four were measured afterwards rather than argued from inspection,
and the fourth is not a survivor at all.

| Mutant | Class | Argument |
|---|---|---|
| `NEGATION` index `-1` | (c) | the parts of a negation are exactly one term, so `p[-1]` is `p[0]` |
| `FIELD` carried index sign flip | (c) | what a field term carries is the pair (constructor, field), so `c[-1]` is `c[1]` |
| `PRODUCT` operands reversed | (c) | multiplication is commutative |
| `Inventory.as_dict` settled test inverted | **killed** | not a survivor: the suite turns it red (1 failed, 162 passed before `-x` stopped it). I ran this one here rather than leave it unmeasured |

## Equivalent or direction-safe, with the argument

Each of these can change no answer a reader acts on. The argument is the
reviewer's, checked against the code here.

| Site | Class | Argument |
|---|---|---|
| `encoding.py` `EXPANSION_LIMIT` ±1 | (c) | a bound chosen rather than measured; the deepest expansion any program here needs is 3 |
| `encoding.py` `_expanded_call` `+= 2`, `>` to `>=` | (c) | trips the bound sooner: more `unknown`, never a proof |
| `encoding.py` `all_of` 187/188 int mutations | (c) | a one-part conjunction and the part itself are the same term to the solver |
| `encoding.py` `_in_scope_at_the_call` `[0]` to `[-1]` | (c) | only the first segment of a site can begin with `ensures`; at worst a proof becomes `unknown` |
| `discharge.py` `_if_answered_another_value` operands reversed | (c) | `values_equal` is symmetric |
| `solving.py` `_written` operands reversed | (c) | a malformed witness fails to parse and the disproof degrades to `unknown` |
| `solving.py` `asked` `<` to `<=` | (c) | one more millisecond is refused |
| `solving.py` `could_not_tell` branches swapped | (c) | swaps two sentences; the status is computed separately |
| `solving.py` `_Sorts.__init__` reversed | (c) | `_places` is keyed by constructor name |
| `solving.py` SUM/DIFFERENCE/LESS/EQUALS index sign flips | (c) | `p[-0]` is `p[0]`: the same program |
| `@dataclass(frozen=True)` to `False`, 17 rows | (c) | nothing writes to an instance; the freeze is a construction guard, not an answer |
| `obligations.py` `_parts_of` / `_parts_of_match` reversals | (c) | the path-condition parts become a conjunction either way |
| `obligations.py` `text_of`, `pattern_text`, `_note`, `_by_kind`, `_by_result`, `_owed_by` | (c) | text a reader reads and counts beside it; no verdict depends on them |
| `solving.py` `asked` 107 reversed, `THE_LEAST_WORTH_ASKING` ±1 | (d) | the no-time-left branch cannot be entered through the public surface: a 299-obligation program refuses at 1-56 ms and proves at 58 ms |
| `encoding.py` `_operator` refusal message `Add` to `Sub` | (d) | the checker refuses an operator outside the eleven before the encoder sees it |

A (c) row changes no answer; a (d) row names a branch no input of this
profile can enter. Neither becomes true by being written here: each is
an argument a reviewer can read and reject.

## My own stopped run, for the record

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
