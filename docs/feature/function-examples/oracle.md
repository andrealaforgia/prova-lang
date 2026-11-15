# A function's examples are about that function — the oracle

## What the request asks for

SPEC.md lines 228-234 say every function needs an example directly
calling that same function, that an example's arguments are closed
values of the declared types, and that an unrelated expression cannot
stand in for an example of the function. The tool did not read any of
that yet.

## What the tool did before this change

Probed through the `prova` command before writing any rule:

| program | answer before the change |
|---|---|
| `double` whose only example is `(example (triple 2) => 6)` | accepted, and the example reported as passing |
| `double` whose only example names an undeclared `treble` | accepted, and the example reported as passing |
| `double`, 1 parameter, example `(example (double 2 3) => 4)` | accepted; the extra argument was dropped |
| `double`, 1 parameter, example `(example (double) => 4)` | the command ended with a traceback while the examples ran |
| `double` whose example is `(example (double 2) => 4)` | accepted |

The fourth line is the sharpest: a reader asking for a program's
examples got no answer at all, only a crash.

## The promises and the scenarios

- **P1** A function whose only example calls a different function is
  refused, and the refusal names the function left without an example of
  its own and the function the example calls.
- **P2** An example calling a function the program does not declare is
  refused.
- **P3** An example whose number of arguments is not the number its
  function takes is refused when the program is checked, and asking for
  the examples answers with that refusal instead of running them.
- **P4** A function whose example calls that same function with the
  number of arguments it takes stays accepted.
- **P5** The word such a refusal carries is one the tool's manifest
  publishes.

Seven scenarios (SC1-SC7) carry those promises; they are recorded in the
workspace journal and rendered in `docs/function-examples/TRACE.md`.

## Conflicts

None. Every program text in the repository was parsed with the project's
own reader (188 candidate sources in files and in test modules), and
every program the suite builds at run time was read: no example names
another function, and no example writes a count its signature does not
take. No existing test's expected result had to change, and the full
suite stayed green after the rule arrived.

## Decisions taken without an owner

No owner was present in this run; the executor decided and recorded:

1. **A new published word, `unrelated_example`.** None of the 13 words
   the tool already publishes says "this example demonstrates another
   function": they report a name that does not resolve, a count, a type,
   a repeated declaration, a cycle, a hidden binding or a reserved word.
   SPEC.md line 233 calls such an example unrelated, so the word is the
   language's own.
2. **`arity_mismatch` is reused** for an example that names its own
   function but writes another number of arguments: it is the word the
   tool already answers with for a call, a constructor and a builtin
   operator written with the wrong number of arguments.
3. **One word for both wrong names.** An example naming another declared
   function and an example naming a name the program never declares are
   the same rule broken; the refusal adds that the name is not declared
   when it is not.
4. **No line and column on these refusals.** A parsed example keeps no
   position, and giving it one would change `syntax.py`, which a
   parallel delivery holds. The refusal names the function and the
   ordinal of the example instead.
5. **No formal model (Quint).** The rule is a pure whole-program check
   over a parsed source: no state, no protocol, no concurrency and no
   crash window for a model to explore.

## Seen red first

The eight new test files were run against the pre-feature tree before
any rule existed: 14 failures, 10 passes. The passes are the controls —
programs whose examples are about their own functions, an empty source,
an unclosed `examples` clause — which must stay accepted or keep the
refusal they already had.

One thing the pre-feature tree could not do: collecting
`tests/properties` there fails for 4 unrelated modules, because the
pre-feature copy's git history does not hold the SPEC revision those
modules read (`git show <sha>:SPEC.md` exits 128). The red command names
the eight new files directly for that reason. Those 4 modules pass in
the worktree and in the full suite.
