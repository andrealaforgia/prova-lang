# F18 — the build: what the Owner can now do, and what it cost

## What works now

Ask the tool what the hour clock owes and all 20 obligations come back
`proved`. Ask it about the reservation example and all 18 do, the one
about the state `step` asks for included. Nothing is skipped: the totals
count the whole list as attempted, and an answer that lists an
obligation with nothing said about it refuses to be written at all.

A promise that is false for some input of its own declared types is not
`proved`. It is `disproved`, and the answer names an input that breaks
it — written the way a program writes a value, so it can be pasted
straight into a run. That input is only reported after the tool has run
the program over it and seen its own evaluator refuse it; a candidate
the evaluator accepts is reported as `unknown` instead.

A call standing in a branch or in a match clause is settled under the
condition that reaches it. The same call with nothing in front of it is
not `proved` — which is how you can tell the condition is doing the
work rather than decorating the answer.

Every answer that asked the solver names it with its version, names the
translation with its own version, and says in as many words that the
word `proved` is the solver's and is not checked again here.

## Three new units, and why each exists

| Unit | What it owns |
|---|---|
| `src/prova/encoding.py` | what a `core-0` construct means as a logical term, and where the fragment ends. It asks no solver, so the whole translation can be read, tested and published on a machine with none. |
| `src/prova/solving.py` | the one place a solver is asked anything, bounded by the time the run has left. It loads the solver inside the call that asks it. |
| `src/prova/discharge.py` | the three answers, and the rule that a solution is only a candidate until the evaluator refuses it. |

Each obligation states its own claim, so there is no place that switches
on what kind of obligation it is holding.

## What was prepared first

One commit, before any behaviour: the condition that reaches a site was
held as text, and text can be printed but not translated. It now holds
the conditions it already was — an expression holding or failing, a
pattern matching or an earlier one not matching — and each still writes
itself out exactly as before. No test changed and every reported
condition is the same characters it was.

## The two things that cost more than expected

**A rule written out 1200 times.** An obligation settled by a rule of
`core-0` first carried the whole sentence of that rule. A program of 600
functions owes 2999 obligations, so one answer repeated the same two
paragraphs about 1200 times. An entry now names its rule and the
sentences stand once beside the inventory.

**A narrowing worth knowing about.** Asking what a program owes now
settles each obligation and says what became of it, so an answer carries
more per entry than the bare list did. Measured: a chain of 240
functions answers in about 0.5 MB and well under a second; a chain of
600 answers in about 1.3 MB, which passes the 1 MiB an answer may be,
and is withheld whole. Before this change that same answer was just
under the megabyte — so any added field at all would have passed it.
Reading such a program is unaffected: `check` still accepts the chain of
600.

## The eight expectations this change made false

Five were found before any code was written and taken to the Owner.
Three more surfaced while building, all of the same family: written when
this tool had no solver, and now stating the opposite of what it
promises. Each was repaired in a commit of its own, keeping what it
protected and re-aiming it:

| Expectation | Re-aimed to |
|---|---|
| the two examples are `not_attempted` | no entry is left for nobody to have attempted, and the scan for words claiming work now reads entries that really are unsettled |
| every entry is `not_attempted` beside `unsupported` | no entry is unattempted, and `proved` must carry a completed attempt |
| no obligation is ever attempted, for any program | the same, over the generated programs |
| the inventory reads `not_attempted` | unchanged, and now passing the findings that say so — because writing the list takes one per obligation |
| every answer says the solver does not apply | the five answers that ask none still say so with a reason; the one that asks a solver must name it |
| the manifest never says `proved` | it may, and only where it also publishes what that word rests on |
| the session never says `proved` | the same, over a whole session's answers |
| a chain of 600 is listed | it is still *checked*; what it owes is asked of a chain of 240, which is just as far past the depth limit |

## One decision worth stating plainly

The disclosure of trust is carried when **a solver answered about at
least one obligation**, and not otherwise. Three kinds of answer carry
none: one whose every obligation a rule of `core-0` settled, one whose
obligations were all left outside what this tool translates, and one
that needed a solver and could not load it -- there a solver was reached
for and answered nothing, so there is no word of its to disclose. All
three say what stood behind them under `stands_on` instead.

An audit-trail limit worth naming: the two edits to existing tests that
this round needed rode in the same commit as production code rather than
in commits of their own. History is not rewritten to hide that.

## What is still open

- The time budget bounding the solver is implemented and is not forced
  by any test: the fragment admits no instance slow enough to time out
  without racing the wall clock. It is stated here as unproven.
- The 1 MiB answer budget now binds `verify` for programs of a few
  hundred functions. Whether that limit should rise is the Owner's to
  decide.
- No remote question service was used, as the request requires.
