# Handoff to Relay delivery protocol 2

This is a project brief, not Relay configuration or an event payload. It follows
the framework's `docs/EXPECTATION-DRIVEN-DEVELOPMENT.md` as read on 2026-09-27.
Use the installed framework's actual schemas when creating the engagement.

## Authority and starting state

Publishing the restart baseline does not approve a compiler architecture, roadmap
or first iteration. Prepare the proposed first scope through the protocol's normal
owner decision process before dependent implementation. Do not import old plans'
automatic-push instructions. Protocol 2 needs committed candidates for receipts;
do not fabricate receipts for an uncommitted working tree or reuse old evidence.

The previous `prova-lang` workers were stopped. Historical global state and Redis
ledger were preserved outside this working tree. Starting that same swarm resumes
old work. Use a fresh, unused engagement identity, for example
`prova-lang-restart`, after checking it is unused. Do not import the old queue,
deadlines, story IDs, completion credit, approval records or security waivers.

Begin with [specification draft 0.2](../SPEC.md),
[expectations and questions](EXPECTATIONS.md), and
[historical fixtures](../evidence/README.md). The archived implementation is not
the new implementation template. No compiler architecture or first iteration has
been approved by the preparation alone.

The owner subsequently requested a functional language aligned with formal
verification and TLA+ principles and authorised updating the specification accordingly.
Draft 0.2 supplies the small `core-0`, `verify-0` and `machine-0` semantic targets.
Treat those written rules as the current draft, not unresolved questions for each
builder. A semantic change must be recorded explicitly with revised expectations.
The reservation example is the recommended first conformance target; decide its
delivery scope through the normal roadmap process, without importing old iterations.

Do not interpret alignment with TLA+, Dafny, F* or Lean as an instruction to build
all their features. Follow the specification's profile boundaries. Formal obligations,
finite model exploration, compiler tests and Relay execution receipts establish
different claims. An analyst answer must identify which kind of evidence it cites.

## Required delivery shape

The new roadmap must explicitly declare `protocol_version: 2`. Before specification
or build dispatch, the analyst records the approved expectations, exact owner-source
references and scoped property questions. The proposed questions in this repository
must be refined into the framework's real story obligations, not marked supported
by copying prose from this brief.

The specifier writes executable checks before implementation. Independent QA reviews
their relevance, boundaries, coverage and ability to detect a wrong implementation.
Only after that review does implementation proceed with test-first delivery.

The toolgate executes every required expectation, property and integration check
against one candidate commit. The builder's completion statement is a claim, not
an execution receipt. Preserve the real command, environment, source SHA, obligation
digest, executed case identities, output and exit status through the framework.

The analyst answers every original property question with `supported`,
`contradicted` or `insufficient_evidence`, cites its receipt and explains the scope
of what was established. All questions must be supported before a story is accepted.
Changing the candidate or obligations requires fresh evidence and answers. The
iteration candidate also receives its integration verification.

Missing, skipped, xfailed, stale or unexecuted checks do not establish completion.
Environment failures return to environment diagnosis; compiler failures return to
implementation; inadequate tests return to specification with the original question
intact. A waived or dropped obligation remains visible accepted risk, never proof.

## Execution setup to validate before dispatch

The framework's initial receipt adapter uses pytest file or node selectors. Keep
acceptance and property files separate, and use real tests of the public compiler
interface. Focused implementation-language unit tests can supplement these checks.
Do not recreate a wrapper that recursively runs every suite for each selected check.

Provision the selected pinned toolchain and dependencies in an isolated evidence
runner, then demonstrate that the actual worker environment can launch its model
executable, compiler tools and test runner. A command working in an interactive
shell is insufficient evidence about a detached worker's PATH. Do not copy the old
machine-specific paths or make native execution permission implicit.

Validate one passing check, one deliberately failing check, a missing selector,
and a timeout. Verify actual execution and cleanup. Set budgets from measured runs,
distinguish queue delay from execution time, and bound concurrency so heavy runs do
not invalidate each other's evidence. Do not diagnose a silent worker as frozen
without checking its process state, output and outstanding request identity.

No Relay worker, monitoring loop or engagement is started by this handoff.
