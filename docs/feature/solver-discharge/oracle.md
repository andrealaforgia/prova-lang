# F18 — the oracle: what the Owner will be able to see

This is the first step of F18. Nothing of the feature is built yet. What
exists now is the set of tests that say what "done" means, and every one
of them fails today. That is deliberate: a check nobody has seen fail is
not evidence.

## What the feature promises

The Owner asks the tool what a program owes, and is told that each of
those obligations is owed no longer — or exactly why one is not.

Nine promises were read out of the request:

| | Promise |
|---|---|
| P1 | All 20 obligations of the shipped hour clock come back `proved`. |
| P2 | All 18 obligations of the reservation example come back `proved`, including the one about the state `step` asks for. |
| P3 | A promise that is false for some input of its own declared types is never `proved`; it is `disproved`, with an input that really breaks it. |
| P4 | A call standing in a branch or a match clause keeps the condition that reaches it, and that condition is what settles it. |
| P5 | The answer names the solver and its version, and says plainly that the solver's word is taken and not checked again. |
| P6 | The change ships a document, named by the tool itself, explaining every logical primitive written for the solver. |
| P7 | Anything the translation does not cover comes back `unknown` with its reason, never `proved`. |
| P8 | Everything the answer carries is described in the manifest before a client sends a request. |
| P9 | The counts in the answer add up to the list they count. |

## The one conflict, and how it was decided

Five existing expectations state the opposite of this feature. They were
written by F16 and F17 to guarantee that this tool had no solver and
attempted nothing:

- `tests/acceptance/test_verify_lists_the_obligations_owed.py` — every
  obligation of the hour clock and the reservation example is
  `not_attempted`, and no word in either answer reports work done.
- `tests/acceptance/test_f17_b4_a_verify_answer_keeps_the_two_results_apart.py`
  — every entry is `not_attempted` beside `unsupported`.
- `tests/properties/test_obligation_inventory_laws.py` — the same, for
  any program at all.
- `tests/unit/test_obligation_inventory_refuses_what_it_cannot_list.py`
  — the same, read straight off the inventory.
- `tests/acceptance/test_f17_b2_every_answer_says_which_versions_it_used.py`
  — the solver and the encoding of every answer begin with the words
  "not applicable".

This was reported to the Owner before any code was written. The Owner
decided: the discharge lands on `verify` itself, and those five
expectations are updated as superseded by F18 — each in its own commit,
each keeping its protective intent, re-aimed at what was *not* shown
rather than deleted. Nothing is claimed that was not shown: an obligation
outside the fragment must come back `unknown` with its reason, and
`proved` must never appear for one.

A sixth expectation was checked and is **not** in conflict: the manifest's
`verify` documentation must mention `not_attempted`, which stays one of
the four results and can still be named truthfully.

## The fragment

The smallest translation that covers both shipped examples completely:
quantifier-free Boolean reasoning, linear integer arithmetic over
unbounded whole numbers, the non-recursive records and unions of
`core-0`, and the expansion of calls (which cannot be cyclic in this
profile). Multiplication only where one operand is written as a literal.
Everything else is answered `unknown` with its reason.

Both examples were worked through by hand before any code was written.
Every obligation of each is linear, so the fragment covers both with no
unsound shortcut, and there was nothing to ask the Owner about it.

## What the tests look at

All of them drive the real `prova` command over its JSON surface, the
way the Owner does. None of them imports the tool's own modules.

Two of the tests are discriminators rather than promises: the same
guarded call written with nothing in front of it, and the shipped hour
clock with the wrap at 12 taken out. They exist so that a tool which
simply answered `proved` for everything could not pass this file.

Five laws run over generated programs rather than fixed examples. The
most important is the soundness law: whatever is answered `proved` is
never contradicted by running the same program through the tool's own
evaluator. Beside it runs a positive control, because a tool that
settled nothing at all would satisfy the soundness law perfectly.

## What is still open

- The translation itself, the solver adapter, the pinned dependency and
  the document are all still to be built; that is the next step.
- The time budget must bound the solver. That mapping cannot be forced
  from outside without racing the wall clock — the fragment admits no
  instance slow enough — so it will be proved at the adapter's own
  contract during the build, and recorded as a limit here.
- Whether the pinned solver wheel installs in CI on Linux is not yet
  checked. It installs on this machine, on Python 3.12.
