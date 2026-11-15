# F16fix - what is handed over

## What a reader of the answer gets that they did not have

A call in a function's postcondition or body is now listed under the
function's own precondition, as SPEC.md's `Pre_f(x) implies ...` says, so the
assumption the work may use is no longer dropped. A call inside a `requires`
keeps an empty condition, because a precondition may not assume itself true.

And the tests now notice when the answer loses something: every position a body
can put a call in is read, a condition made of several parts is read whole, and
the count of calls on the entry that says a function ends is read against the
program.

## Review

| | Verdict | Findings | How they were settled |
|---|---|---|---|
| REV1 | REJECT, of the merged F16 at `371d1d8` | 7 | findings 1 to 4 fixed in `bd12621` and `fde357c`; 5 to 7 were notes |
| REV2 | APPROVE, at `b171e36` | 0 | nothing to resolve |

## Notes the reviewer left open

**The seeded clauses are not simplified.** The precondition is carried into the
condition exactly as the program writes it. A clause that is trivially true,
or one that repeats a branch test already in the list, is still printed. The
answer is therefore honest but wordy. This is an input for F18, not a defect
here: nothing attempts an obligation yet, so nothing depends on the condition
being minimal.

**`joined()` in the property test re-implements `PathCondition.text`.** The
generated test writes out the same joining rule the product uses, so a test
derived from a wrong idea of the rule would agree with a product that had the
same wrong idea. What stops that is the acceptance test beside it, which states
its conditions as literal strings read from the program by hand - `(and (not
(matches n 0)) (matches n 1) (> n 5))` and the rest - and does not compute them.
Both would have to be wrong in the same way for the error to pass, and the
second one is not computed at all.

**Let-bound names appear in conditions with no entry defining them.** A
condition can name a value bound by a `let` whose definition is in no entry of
the inventory, so a reader cannot resolve it from the answer alone. The request
assigns this to F18; nothing was done about it here.

## What this delivery does not establish

- That the condition reported is the one a solver would need. Nothing attempts
  an obligation: every entry still carries `not_attempted`.
- That a deletion other than the ten re-run here would be noticed. Ten were
  re-run, which is not a whole mutation sweep.
- Any claim about performance, memory or external behaviour. None was measured
  and none is made.

## State

The change sits on `feat/f16fix`, not pushed and not merged. The whole suite is
green: 1011 passed, 0 failed.
