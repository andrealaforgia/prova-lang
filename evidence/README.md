# Historical compiler counterexamples

These 14 small source files preserve useful failure cases and positive controls.
They are not executable tests, new-run receipts or evidence of a working compiler.
No compiler exists in this restart yet. No fixture has been run during preparation.

Sources were copied byte-for-byte from the previous repository at
`093fb86443c057c1d3abb4f1c033d1a6bf601d38`. The original paths are
`docs/investigations/compiler-review-<date>/<filename>.prova`, with dates below.
The original reports, observed JSON results and full specification remain in Git
history and the external archive; historical defect reports are not present-tense
claims about a replacement compiler.

| Case | Source date | Meaning to preserve when its features are supported |
|---|---|---|
| [false-contract](cases/false-contract.prova) | 2026-09-21 | Identity over all integers cannot ensure a nonnegative result. Its supplied positive example misses negative inputs. |
| [false-contract-plus-unencoded](cases/false-contract-plus-unencoded.prova) | 2026-09-21 | Adding another function whose contract uses `let` cannot make the same false claim pass. If that form is unsupported, disclose the limitation; never silently discard the false obligation. |
| [missing-call-precondition](cases/missing-call-precondition.prova) | 2026-09-21 | An unconstrained caller cannot call a function requiring a strictly positive argument. The example with input 1 is insufficient. |
| [hidden-unknown-name](cases/hidden-unknown-name.prova) | 2026-09-21 | Resolve names in the branch that the supplied example never visits. |
| [hidden-operator-type](cases/hidden-operator-type.prova) | 2026-09-21 | Reject arithmetic on a boolean in an unvisited branch. |
| [exact-division](cases/exact-division.prova) | 2026-09-21 | With the argument constrained to decimal 3, division by decimal 3 is exact and returns 1. A positive control for the intended decimal fragment. |
| [constant-division](cases/constant-division.prova) | 2026-09-21 | Constant decimal 3 divided by 3 is valid and returns 1. |
| [inexact-division](cases/inexact-division.prova) | 2026-09-21 | An unrestricted decimal divided by 3 is not always finitely representable. Input 1 exposes the violation even though the example with 3 passes. |
| [builtin-hides-name](cases/builtin-hides-name.prova) | 2026-09-25 | A builtin argument cannot hide an unresolved name in an unvisited branch. |
| [builtin-hides-type](cases/builtin-hides-type.prova) | 2026-09-25 | Descend into builtin arguments and reject their invalid arithmetic, rather than trusting the builtin's result type. |
| [non-bool-condition](cases/non-bool-condition.prova) | 2026-09-25 | Reject an integer condition, including in a nested unvisited branch. |
| [named-call-arity](cases/named-call-arity.prova) | 2026-09-25 | Reject a call with too many arguments, even when no supplied example executes it. |
| [boolean-operands](cases/boolean-operands.prova) | 2026-09-25 | `and` requires boolean operands; integers have no truthiness conversion. |
| [valid-builtin](cases/valid-builtin.prova) | 2026-09-25 | A valid `length-text` branch must remain acceptable when that builtin is supported. Call both branches in the new test. |

The spellings and declaration forms belong to the historical syntax. If the new
approved grammar changes, adapt a fixture explicitly while preserving its semantic
question and provenance. Merely rejecting every fixture as unsupported syntax does
not establish any of the checking properties above.

For every selected negative case, write a minimally corrected positive control and
assert the semantic reason for rejection through the public interface. A crash,
timeout, parser error or unrelated diagnostic is not the expected result. Decimal
positives belong in acceptance only when the declared fragment supports them;
unknown must still be distinguished from a false disproof.

These fixtures are seeds for independent expectations. Add fresh properties and
counterexamples for each selected feature; do not reconstruct the old test harness.
