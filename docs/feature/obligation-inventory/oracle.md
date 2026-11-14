# Oracle: the tool lists every obligation it owes

## What the Owner asked for

`verify` answers with the complete list of what would have to be shown for a
program, every entry marked `not_attempted`, so the size and shape of the job
are visible before any solver exists.

Eight promises came out of the request:

| | Promise |
|---|---|
| P1 | The Owner sees the complete list of obligations a program owes. |
| P2 | Each call the program can evaluate owes one precondition entry, under the condition that reaches it -- including a call in a branch that can never be taken. |
| P3 | Each function owes one body-to-postcondition entry, one contract-definedness entry and one structural-termination entry; each declared example owes its own validity entry. |
| P4 | Every entry reads `not_attempted`, the counts say none was attempted, and no word in the answer reports work the tool did not do. |
| P5 | Two runs on the same source owe the same list, with the same identities, in the same order. |
| P6 | The manifest advertises `verify` as available and says it answers the inventory only. |
| P7 | A built artefact is still refused as unavailable. |
| P8 | A program that does not read, or does not check, is refused with the diagnostics the whole-program check already gives. |

## The conflict with what the tool does today, and what was decided

Today `verify` sits in `UNAVAILABLE_OPERATIONS` and is refused. Four shipped
tests state that refusal. The Owner approved the roadmap, so `verify` now
answers; nothing about `build` changes. **Every shipped test whose expectation
changes, and why:**

| Test | What changes | Why |
|---|---|---|
| `tests/acceptance/test_s1_b3_build_and_verify_refused_as_unavailable.py` (renamed `..._build_refused_as_unavailable.py`) | Its operation list drops `verify`; the two test names and the docstring now speak of `build` alone. | `verify` is no longer refused. The file name and titles would otherwise say something false. |
| `tests/acceptance/test_i1_int_checked_evaluator_end_to_end.py` | Step 7 of the session now reads the inventory `verify` answers and checks every entry is `not_attempted`; it still sees `build` refused. | The Owner's end-to-end session should show what the tool really answers now. Step 8's scan for claim words still covers every answer in the session, the new one included. |
| `tests/properties/test_i1_s1_p4_p5.py` | Its operation list drops `verify`; the control scripts that prove the detector fires are untouched. | P4/P5 state that a refused operation attempts no work. `verify` is not refused any more; what it answers, and that it attempts nothing, is stated in the new tests. |
| `tests/unit/test_service_discover.py` | `verify` is advertised `available`; one new case reads its documentation entry. | The manifest must advertise `verify` accurately. |

`build` stays refused as unavailable in all four, and a new unit test asks for a
build right after listing the obligations to make that explicit.

## Decisions taken without the Owner (the request settles them)

- **Every call owes an entry, even when the callee declares no precondition.**
  SPEC.md says every potentially evaluated call emits a precondition obligation.
  Neither the hour clock nor the reservation example has a callee that declares
  one, so the narrow reading would show the Owner no calls at all. The entry
  carries `precondition_clauses: 0` when there is nothing to show.
- **Every function owes a body-to-postcondition entry**, even one that declares
  no postcondition (`postcondition_clauses: 0`), so no function is missing.
- **`verify` is advertised `available`** inside the manifest's existing
  two-value vocabulary, with a documentation entry saying the answer is the
  inventory and every entry is `not_attempted`. A third value would change a
  published vocabulary for no gain the documentation does not already give.
- **"Nothing ran" is said structurally**: `attempted: 0`, every result
  `not_attempted`, and a note that the tool has no solver -- using no word that
  reports an outcome, so the answer cannot be misread as a result.
- **Obligation identity is `kind:function:site`** with a structural site
  (`contract`, `body`, `calls`, `requires[0]`, `ensures[1]/arg[0]`,
  `body/then`, `body/case[0]`, `example[2]`), never a line number, so
  reformatting a program leaves identities unchanged.
- **No formal model (Quint).** `verify` is a pure function from the request's
  source text to a list: no state, no writes, no processes, no protocol.

## What was proved, and what was not

The tests were written first and run against the tree as it was before this
feature. Fifteen of them failed there, for the right reason -- the answer did
not exist:

```
uv run pytest -q tests/acceptance/test_verify_lists_the_obligations_owed.py \
  tests/properties/test_obligation_inventory_laws.py \
  tests/unit/test_verify_inventory_edges.py tests/unit/test_service_discover.py
```

Four laws are generated from a plan written in the test, not from the
implementation: every function, example and call owes its entry; no obligation
is ever answered as attempted; the same source always owes the same list;
moving a call out of reach keeps its obligation and changes only the condition.

Not proved at this step: nothing is implemented yet, so no statement here says
the tool behaves this way. Concurrency and crash cases are recorded as not
applicable, because the operation writes nothing and holds no state between
requests -- that is an argument, not an observation.
