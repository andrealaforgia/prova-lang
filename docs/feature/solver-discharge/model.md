# F18 — the model step: what was checked, and what could not be

## The decision

**No formal model.** This change has no state, no protocol of more than
one step, no concurrency and no crash window. The `verify` operation
reads one text, settles each obligation in the one process that was
asked, and prints one answer at the end. Nothing is written to disk,
nothing is locked, no thread and no child process is started. The solver
is a library call inside the same process.

`subprocess` appears in this change only in the tests, which run the
shipped command over its JSON surface the way the Owner does.

## The capability limit, stated plainly

There *is* a claim here a checker would be the right tool for, and it is
not about state: **whatever is answered `proved` must never be
contradicted by the reference evaluator**. That is a law over a pure
translation, and the method says to check such a law with a checker
rather than with examples alone.

**Quint is not installed on this machine.** So that check was not run.
It is recorded as a capability limit and the claim stands
`INDETERMINATE` as far as model checking goes — not as a pass. Nothing
in this delivery may be read as a proof of the translation.

## What stands beside it

Four generated laws, each a bounded search for a counterexample driving
the real command, and none of them a proof:

| | What it searches for |
|---|---|
| soundness | a program whose promise came back `proved` that the evaluator then refuses for that same promise — run at the smallest accepted numbers and at distances far past any machine word, because `Int` here is the mathematical integers |
| positive control | a tool that settles nothing at all, which would satisfy the soundness law perfectly; seven programs whose promise is true by construction must come back `proved` |
| definedness | a contract clause that has no value at some input of its declared types, which would undermine the rule that settles contract definedness without a solver |
| ending | a program the checker accepted that runs out of depth, which would undermine the rule that settles structural termination without a solver |

The last two were run at this step and pass against the tree as it
stands, which is the point: they pin premises that are true *before*
this feature and must stay true after it.

## What this does not cover

- No proof of the translation. A bounded search over generated programs
  is evidence, not assurance.
- The soundness law cannot fail until the feature exists; today it is
  satisfied by a tool that proves nothing. Its positive control is what
  makes it meaningful, and both are re-run after the build.
- Neither law reaches the solver's own correctness. That is trusted, and
  the answer says so.
