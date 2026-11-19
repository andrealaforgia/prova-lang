# Prova

Prova is a functional programming language for LLMs to write and change software. Its
core combines immutable values, explicit claims, checkable evidence and state-transition
semantics compatible with TLA+ principles. The aim is software that is independently
correct, inside a measured budget of tokens and compute.

A Prova program says what it promises (`requires`, `ensures`, worked `examples`) and the
toolchain says, per claim, what it has checked and what it has not. Evidence for one kind
of claim is never reported as evidence for another: a passing example is not a proof, a
proof is about one revision of one source, and a refusal that a program is outside the
supported profile is different from a refusal that it is wrong.

The compiler in this repository is a JSON service: one request on standard input, one
JSON answer on standard output, always, whatever the input.

## Status

| Profile | What it covers | State |
|---|---|---|
| `core-0` | total pure first-order functions, records, unions, `match`, contracts, examples | implemented and checked |
| `verify-0` | proof obligations discharged by a pinned Z3, each answer saying what rests on the solver and what on a rule of the language; one aggregate word `verified` or `not_verified` | implemented for the linear integer arithmetic fragment |
| `machine-0` | state machines: a separate JSON descriptor names five roles; the three inductive obligations are proved; a machine can be driven event by event | implemented; broken guards are caught by proof and named as induction-step witnesses |

Operations: `discover`, `check`, `examples`, `evaluate`, `parse`, `format`, `verify`,
`machine`, `step` and `build`. `build` writes one generated Python file, and only for a
program whose aggregate is `verified`. The file answers like `evaluate` and refuses with
six distinct statuses. A build writes only inside the directory the request names, and
replaces an existing file only when the request says so.

## Quick start

You need [uv](https://docs.astral.sh/uv/) and Python 3.12.

```sh
uv sync
printf '%s' '{"operation":"discover"}' | uv run prova
```

Check and verify the hour clock from Lamport's *Specifying Systems*:

```sh
python3 - <<'EOF' | uv run prova
import json
print(json.dumps({"operation": "verify", "source": open("examples/hour-clock.prova").read()}))
EOF
```

Every obligation of that program comes back `proved`, each marked as settled by the
solver or by a written rule of the language. `discover` describes every operation, its
request and response shape, the diagnostic categories, the resource budgets and the
language's types and operators, so a client needs nothing else to use the tool.

## What the tool promises

- **One answer, always.** Malformed requests, unreadable programs, over-long or deeply
  nested input and unwritable text are refused with a located diagnostic in a published
  category. The command never ends in a traceback.
- **Declared budgets.** Input size, time, memory and answer size are declared per
  operation and enforced; exceeding one is a refusal that claims nothing about the
  program.
- **Honest verification.** `proved`, `disproved` and `unknown` are per obligation. A
  disproof carries a witness that the evaluator really refuses; otherwise the answer is
  `unknown`. The solver's word is disclosed as trusted, not re-checked.

## Repository layout

| Path | Contents |
|---|---|
| `SPEC.md` | the language specification (restart draft 0.2), the authority for behaviour |
| `src/prova/` | reader, syntax, checker, evaluator, obligations, solver encoding, service |
| `tests/` | acceptance, property and unit tests; they drive the real command |
| `examples/`, `conformance/`, `evidence/` | example programs, hand-written expected outputs, historical counterexamples |
| `docs/ROADMAP.md` | the delivery roadmap and what has shipped |
| `docs/translation-to-the-solver.md` | what each logical primitive means and why discharging an obligation establishes the source claim |
| `tools/` | development tools (not part of the package) |

## Development

```sh
uv sync
uv run pytest -q tests      # about 7 minutes
```

Continuous integration runs the same command on every push. The tests read `SPEC.md` at a
pinned revision, so CI checks out the full history.

## Contributing

Behaviour is decided by `SPEC.md`. A change starts from a failing test that states the
behaviour through the public JSON interface, and keeps the existing tests green. The
roadmap in `docs/ROADMAP.md` lists what is planned and what is deliberately out of scope.

The repository is `git@github.com:andrealaforgia/prova-lang.git`.
