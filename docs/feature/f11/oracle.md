# F11 - oracle: what the manifest must say, and the tests that say it

## What this feature promises

`discover` is the one answer an agent reads before it uses the tool. Today it
carries the profile, a list of operations with a word beside each, the statuses,
the diagnostic schemas and the resource limits. It does not say which of
SPEC.md's seven operation categories the tool covers, what a request for an
operation looks like, what the answer carries, or which types and operators a
program may use. An agent therefore has to guess an undocumented API, which
SPEC.md line 475 says it must never have to do.

Five promises came out of the request:

| | Promise |
|---|---|
| P1 | Every operation category SPEC.md names is there, with the operation that covers it and whether it is available or unavailable. |
| P2 | Every operation an agent may call carries the fields its request takes and the fields its answer carries, beside the parts the manifest already publishes. |
| P3 | Every type core-0 has and every operator is there, with the types each operator takes and the type it answers. |
| P4 | An available operation answers a request that matches its published shape, and refuses one that carries a published field as another kind of value, naming the field. |
| P5 | An operation this tool answers that SPEC.md names in none of its categories is shown as the tool's own, not as profile conformance. |

Sixteen sentences of the request are process promises (where the work happens,
how it is committed, which directories it leaves alone). They are kept by the
diff and the run, not by a test, and are written down as such.

## What was built

Six new test files, all driving the real `prova` command over its JSON standard
input and standard output. No test imports anything from `src/prova`, and every
expected value is read by hand from SPEC.md.

- `tests/acceptance/test_f11_b1_...` - the seven categories and their words.
- `tests/acceptance/test_f11_b2_...` - the request and answer shape of each
  operation, and real answers read back against the published shape.
- `tests/acceptance/test_f11_b3_...` - the three type names and the eleven
  operators with their argument and result types.
- `tests/acceptance/test_f11_b4_...` - a matching request is answered; a
  published field sent as another kind of value is refused by name.
- `tests/acceptance/test_f11_b5_...` - `evaluate` is marked beyond the profile.
- `tests/properties/test_f11_manifest_laws.py` - three generated laws: a
  published field of the wrong kind is always refused; an answer carries exactly
  the published fields; a published operator signature is the one the checker
  keeps.

All fifteen tests were seen failing against the tree as it stands, each for the
promised outcome being absent rather than for a broken import or fixture.

## What was decided

- **The existing operation list is left exactly as it is.** An existing unit
  test compares it with equality, so the categories, the shapes and the language
  are published beside it as new parts of the manifest.
- **The `source` field is published as optional.** A request without it is
  answered today as a program with nothing in it. Publishing it as required
  would make the tool refuse requests it answers today.
- **Shapes are published only for the operations advertised as available.** An
  operation that is refused has no shape fixed yet.
- **The `operation` field is not one of the per-operation request fields.** A
  request whose operation field carries another kind of value names no operation
  at all, and the tool already answers that as unavailable.

## What is still open

One question for the owner, raised at the pause after this step: an existing
test forbids the letters of the word "built" anywhere in the `discover` answer,
and the words "builtin" and "builtins" carry them. The types and operators are
therefore published under the name `language`, and the owner is asked whether
that is the name an agent should read.
