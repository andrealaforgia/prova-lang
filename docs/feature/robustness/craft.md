# Robustness R1 - what was built

## What changed, in order

| Commit | What it does |
|---|---|
| `33167eb` | Prepares the ground: one object now answers how many fields a constructor declares. Behaviour unchanged, no test edited. |
| `d310234` | The tests, all failing. |
| `e9166ba` | The design and its diagram. |
| `8ae3d9a` | The three gates. |

The prepare-first commit was needed because the number of fields a
constructor declares was compared in two places that did not know about
each other, and the new rule would have been a third. The two existing
places now ask one object. One of them also resolved the same
constructor twice, once for its fields and once for its owning type; it
resolves once now.

## The three gates

**A submitted request is read in one place.** Every field is answered
with its value or with a refusal naming that field. A list where a name
belongs, a number where a list belongs, an element of the argument list
that is not text, or something that is not an object at all, is refused
by name before any work starts. The two fields an evaluation needs are
read in one pass, so a client that wrote both wrongly is told about both
at once rather than repairing one and meeting the next.

**A text is read no deeper than the tool follows it.** The depth is
counted in the one place it grows, which covers the source of a program
and the text of an argument without either knowing about the other. The
limit is 128 nested forms. One object holds that number: the reader asks
it, and the manifest publishes it, so a caller that obeys what it read
cannot still meet a refusal. A text past it is answered as a budget that
was passed - a new status and a new category - never as a rule of the
language the program broke.

**A value written in a program is counted against the fields its type
declares.** This is where the shipped hour clock went wrong: deleting
the character holding the number inside a one-field record left an
example writing a record with nothing in it, which was accepted and then
read for a field that was never there.

## Evidence

| Check | Command | Result |
|---|---|---|
| Whole suite | `uv run pytest -q tests --durations=10` | 1086 passed in 124.19s |
| Baseline before any change | same | 1042 passed in 116.59s |
| Prepare-first commit preserves behaviour | `uv run pytest -q tests/unit` | 63 passed |
| Mechanical check | `uv run python -m compileall -q src tests` | exit 0 |

44 tests are new (1042 + 44 = 1086), plus 2 that check the law about
reading a field. No existing test was edited and none broke.

## Test cost

The new test files were run nine times in a row. All nine passed with
46 tests each. Median 4.98s, slowest 5.01s. The whole set is one
integration-level run, well inside seconds.

The single slowest test is the sweep of mangled requests at 2.74s. It
sends 10249 of them: the three programs this repository ships, cut off
and dented at every character, every field of every operation holding
every kind of JSON value, and 500 requests drawn from a fixed seed. It
calls the command's own entry point in this process with standard input
and output replaced, because 10249 subprocesses would cost minutes; the
acceptance tests keep one real subprocess per family, where the cost of
a process is paid once.

## Each new behaviour was broken on purpose

| What was broken | What failed |
|---|---|
| The reader stops counting how deep it has gone | 3 of 7 |
| A value is no longer counted against its declared fields | 5 of 9 |
| A function field of any kind is accepted as a name | 5 of 24 |
| The manifest publishes a number the reader does not enforce | 5 of 7 |
| A step reads a submitted field for itself again | 1 of 2 |

Each break was put back and the suite is green again.

## Jev

`typesafe: unavailable`. `TYPESAFE_API_KEY` is absent from this
environment, so the client exited 3 and nothing was transmitted. The
open choices - which component owns the refusal, which published
category it carries, which status an exceeded budget gets - were settled
against the table of diagnostic kinds, the arity rule that already
exists over expressions, and the status vocabulary the suite already
names.

## Deliberate break of a design rule

`DeclaredConstructor` holds three values where the house rule asks for
at most two. The three are the name, the type that owns it and its
fields: the parts of one declaration. Splitting them would add a
collaborator no rule asks for, and would separate the name a person
wrote from what that name resolves to, which is exactly the pair a
refusal must show together.

## What this does not claim

The limit is enforced where a text is read. A program with very many
shallow declarations can still make the evaluator call itself once per
declaration; nothing here bounds that, and no input in the sweep reaches
it.

Nothing is proved. Building a function name and the argument texts is
centralised, not proved: Python lets a caller build those objects around
any value by hand. The claim is that this tool has one path and that
path refuses.

## Found, not fixed

A record written with the right number of values but the wrong kind of
value in one of them is accepted and run. It does not crash, so it is
outside this request. It is a gap in the same rule about values and
belongs to whoever owns the checker's value rules.
