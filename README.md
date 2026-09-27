# Prova: compiler restart

Prova is a functional programming language intended for LLMs to generate and change
software. Its core combines immutable values, explicit claims, checkable evidence
and state-transition semantics compatible with TLA+ principles.
The goal is independently correct software within a measured token and compute
budget. Whether a new language improves that outcome remains an open hypothesis.

This working tree starts the compiler again from requirements. There is no compiler,
test runner, build system, CI pipeline or active Relay engagement here yet. No old
implementation, test result or iteration completion counts as delivery of the restart.

Read these documents in order:

| Document | Purpose |
|---|---|
| [SPEC.md](SPEC.md) | Restart draft 0.2: functional core, proof obligations, state-machine semantics and reference alignment |
| [docs/EXPECTATIONS.md](docs/EXPECTATIONS.md) | Proposed first outcome, evidence questions and unresolved decisions |
| [evidence/README.md](evidence/README.md) | Small historical counterexamples to turn into independently reviewed checks |
| [docs/RELAY.md](docs/RELAY.md) | Handoff for Relay delivery protocol 2 |
| [Design review](docs/spec-review-2026-09-27.md) | Assessment of the earlier baseline that motivated draft 0.2 |

The owner's restart instruction on 2026-09-27 was:

> Remove anything that is not strictly required to re-implement a compiler from scratch

The owner specified the second Relay protocol, based on expectations, evidence and
questions to be validated. The documents here are a prepared starting brief, not an
approved roadmap or fabricated execution evidence. Proposed scope and open decisions
are labelled accordingly.

Draft 0.2 defines three incremental targets: `core-0` for total pure functions,
`verify-0` for explicit verification, and `machine-0` for state invariants. It includes
a reservation example with exact expected behaviour. Full temporal proof automation,
concurrency and broad libraries remain later work. None of these targets is implemented.

The previous working tree was archived outside this repository, including its full
v0.9.1 specification, reviews, samples, untracked files and local agent state. The
original Git history remains available locally. Historical source revision:
`093fb86443c057c1d3abb4f1c033d1a6bf601d38`.

Origin is `git@github.com:andrealaforgia/prova-lang.git`. Publishing this restart
baseline does not approve a roadmap or establish compiler correctness. Begin the
new engagement with analysis and independently reviewed expectations.
