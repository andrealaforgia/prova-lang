# F2 - Craft: what was built and what was proved

## What was built

One more whole-program pass in `src/prova/checker.py`, beside the passes
that were already there, and two lines in `src/prova/service.py` that
publish its result.

| Part | What it does |
|---|---|
| `Cycle` | One cycle: the functions that depend on each other, in declaration order. Refuses to exist with no member. Owns the sentence it carries. |
| `_calls_in` | Every call written inside one expression. |
| `_callees_of` | The declared functions one function depends on: body and contract clauses only. |
| `_cycles_in` | Every such set of functions, found with an iterative search. |
| `service.py` | Lists the new category in the manifest and puts the members of the cycle in the answer. |

Nothing else changed. No operation needed editing, because `check`,
`examples` and `evaluate` already check a program before evaluating
anything; removing the crash was a matter of refusing earlier.

## What the user sees now

Asking the tool about a program whose calls form a cycle answers:

- status `invalid_program`;
- one diagnostic per cycle, category `cyclic_dependency`;
- a sentence that names the functions, says the rule they break, and says
  what to remove, with the reminder that an example calling its own
  function is not part of the graph;
- a `cycle` field listing those same functions, so a caller does not have
  to read English;
- exit code 0, and nothing on standard error.

Before this change the same request ended the process with exit 1, an
uncaught `RecursionError` and no answer at all.

## Evidence

| Check | Command | Result |
|---|---|---|
| Whole suite | `uv run pytest -q tests --durations=10` | 788 passed in 65.29 s |
| Same suite before the change | same | 772 passed in 67.90 s |
| New tests, nine runs | the eight new files | 16 passed every time; median 0.98 s, slowest run 1.02 s |
| Mechanical check | `uv run pytest -q tests --collect-only -W error` | 788 collected, exit 0 |
| The repository's own SPEC probes | `uv run python docs/spec-trace/probe.py` | T17, T18, T19 agree; 34 of 53 against 31 of 53 before |

772 + 14 new acceptance and property tests + 2 new unit tests = 788. No
existing test changed its expected result, and none was edited.

Slowest new test: 0.44 s, the law that checks the same program in two
separate processes. Every other new test is at or under 0.05 s.

## Deliberate breaks (each one restored)

| Break | A test that caught it |
|---|---|
| Read only the body, not the contract clauses | the contract-cycle test |
| Report only groups of more than one function | the self-call test |
| Stop publishing the members in the answer | the mutual-call test |

## Honest limits

- A declared example cannot contribute a dependency for two reasons, not
  one: the rule reads only bodies and contracts, and an examples clause
  holds values rather than expressions. A mutation that pointed the rule
  at the examples would therefore change nothing, so that half of the
  promise is structural, not guarded.
- The rule is enforced where the program is checked, not by a type. The
  source arrives as untrusted text, so this is a boundary check.
- Expression depth is still walked recursively, in the existing type pass
  and in the new call walk. A deep enough expression still ends the
  process; that limit is older than this change and is untouched by it.
  The new search over functions is iterative, so program size does not
  add a second such limit.
- `docs/spec-trace.md` keeps the table it measured at an older commit. A
  dated note under its defect 1 records that this feature fixes it, with
  the probe numbers before and after. The table itself is not re-scored.
