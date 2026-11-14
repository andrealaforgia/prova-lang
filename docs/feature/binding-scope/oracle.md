# F5 oracle: a binding cannot hide another, and `result` stays reserved

## What this feature promises

A program is refused when one of its bindings takes a name that is
already in use where the binding appears, and when any binder uses the
word `result`, which only a postcondition may read.

Ten promises were read out of the request and the owner's answer:

| | Promise |
|---|---|
| P1 | A `let` binding that takes a parameter's name makes the program invalid, and the refusal names the binding it hides. |
| P2 | A pattern variable spelled like a declared function does the same. |
| P3 | A binding spelled like a builtin operator does the same. |
| P4 | Any binder named `result` makes the program invalid: a parameter, a `let` binding or a pattern variable. |
| P5 | `result` read in a body or in a precondition makes the program invalid; a postcondition may still read it. |
| P6 | A pattern that binds the same name twice makes the program invalid. |
| P7 | The same name in two disjoint `match` clauses is accepted. |
| P8 | The tool publishes the two new refusals in its own manifest. |
| P9 | The programs the project ships stay accepted. |
| P10 | A parameter that hides a declared function, or an earlier parameter of its own signature, makes the program invalid. |

Everything else in the request is an instruction about the delivery (the
branch, the commit message, the parallel work), not a behaviour of the
tool, and is recorded as such.

## What was decided, and why

- **Two new published refusals, not one and not a reuse.**
  `shadowed_binding` answers every binding that hides a name already
  visible, which includes a pattern that binds one spelling twice: the
  second binder hides the first. `reserved_name` answers a binder that
  uses `result`. The existing `duplicate_declaration` was not reused: it
  reports a *top-level declaration* made twice, with the place of each
  and the uniqueness rule of a declaration, so a caller filtering on it
  would start receiving local binder defects it never asked for.
- **"Builtin" means the operator names.** The authority forbids hiding
  "a visible value binding, function or builtin". The builtin *types*
  (`Unit`, `Bool`, `Int`) live in the type namespace, where a value
  binding cannot hide them; the operators (`+ - * < <= > >= = and or
  not`) are the only builtins reachable where a value binding is
  visible, so they are what the rule protects.
- **A parameter is a binder too (the owner's answer).** The request's
  outcome sentence stops at `let` bindings and pattern variables, while
  the authority's line 145 lists parameters among the bindings the rule
  governs. The owner was asked and chose the wider reading: a parameter
  may hide neither a declared function nor an earlier parameter of its
  own signature, and a parameter named `result` is refused. One
  acceptance test observes each of those two cases, with a twin that
  differs only in the parameter's name and stays accepted.
- **The manifest is updated.** The request names `checker.py` and tests,
  but F3 and F4 both published their new category in the tool's
  manifest, and a category the manifest hides cannot be relied on.
- **No formal model.** These rules are a pure function of one parsed
  program: no state, protocol, concurrency or crash. Two generated
  properties carry the laws instead.
- **The remote question service was unavailable** (no API key in this
  environment, the client exited 3 before sending anything), so the four
  open questions above were settled locally against the authority and
  the F3 and F4 code.

## Conflicts with what exists today

None. Every program text in `tests`, `examples` and `conformance` was
searched for a binder the new rules would refuse, and none was found;
the two programs the project ships use `result` only in postconditions,
which stays allowed. The suite was green before anything was written.

## What was built and proved

Ten acceptance test files and one property file, all driving the real
`prova` command or its published request interface, no internal symbol
of the checker. They were run against the tree as it is today: 28 of
their observations fail because the rule does not exist yet, and the 16
control observations beside them already pass, so no test is simply
"refuse everything".

Three laws are stated as generated properties: a binder is refused
exactly when its name is taken; a pattern variable is visible only in
its own clause, however many clauses there are; and a nested `let` may
bind its own name at any depth but not an enclosing one.

## Still open

The rules themselves are not implemented: the design and the code
follow. The refusal sentences are fixed by the oracle only in what they
must name (the binder, what it hides, where it is); their exact wording
is written with the rule.
