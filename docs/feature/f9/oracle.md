# F9 — the oracle: what "outside this profile" has to mean

## What the feature promises

`core-0` is deliberately small. SPEC.md says so twice: unsupported features must be
identified as unsupported and not misdiagnosed as type errors (lines 51–54), and the
profile has no trailing top-level expression, no `defspec`, `fn`, `trust` or `module`,
no division, and no decimal or text literals (lines 79–80, 96–99).

Today the tool breaks that promise in three different ways. A program that divides is
told the name `/` is unbound. A decimal literal is told the name `1.5` is unbound, or
that `1.0` is "not a value". A call written after the declarations is told the reader
expected a `deftype` or a `defn`. Each of those sends the reader to repair something
that is not the problem: the problem is that `core-0` does not have the construct at
all, and no spelling repairs that.

So the feature adds a second refusal **status**, `unsupported`, beside
`invalid_program`, and one diagnostic category, `unsupported_construct`. An
`invalid_program` answer means *this is a program of the profile and it breaks one of
the profile's rules*. An `unsupported` answer means *this is not a program of this
profile at all*. SPEC.md line 192 requires exactly that distinction.

## What was decided, and why

**The status name was not a choice.** The request names it: a separate `unsupported`
status alongside `invalid_program`. It is taken verbatim.

**A misspelled declaration word is not an out-of-profile feature.** `(deftypo T ...)`
and `(f 1)` reach the same refusal today. Only the second is a trailing top-level
expression. The rule therefore reports an out-of-profile top-level expression only when
the head is recognisably an expression — an operator, a special form, a selector, a
constructor, or the name of a function the same source declares. `deftypo` keeps the
refusal it has today, because telling a reader to wait for a later profile when the
repair is one letter is the same mislabelling in the other direction.

**The manifest gains a `statuses` map.** A caller learns the vocabulary from the tool,
not from a document. Publishing only the new category would leave a caller believing
`invalid_program` is still the only refusal for a source it can read.

**All fourteen preserved files are refused, and none of them passes.** This is the one
place where the request's wording and the repository disagree, and it is recorded as a
decision rather than a conflict, because nothing in the system contradicts it:

- every one of the fourteen ends with a trailing call, or uses `defspec`, a decimal
  literal or a text literal, so under `core-0` all fourteen are outside the profile;
- the criterion's other half — "the ones meant to pass pass" — would therefore be
  vacuous, and a test that only ever observes refusals proves nothing;
- so each file also yields a **core-0 adaptation**, derived from the file's own text by
  recorded substitutions (drop the trailing form, write whole numbers instead of
  decimals, write `defn` instead of `defspec`), and each adaptation must be answered by
  the ordinary rules and never as `unsupported`. Six of them are accepted outright; the
  rest are refused for the semantic defect the file was kept for — a type error, an
  unbound name, a wrong arity.
- the files themselves stay byte-for-byte unchanged. They are provenance. If one is
  ever edited the substitutions stop matching and the test says so.

**Two limits are named rather than hidden.** `Decimal` and `Text` written as *type*
names keep the checker's `unbound_type` answer: a program may legally declare a record
called `Decimal` today, and refusing the spelling everywhere would make a program that
is valid now invalid. And a value supplied as an `evaluate` argument keeps its
`malformed_value` refusal: the profile boundary is read over source text, and an
argument is not source.

**No formal model.** The change is a pure function from one source text to one
response. There is no state, protocol, concurrency or crash behaviour for a model to
describe, so Quint would pay for nothing.

## What was built, and what it proves

Seven test files, and no existing test touched. Every refusal test is paired with a
control: the same program with the one out-of-profile construct replaced by one
`core-0` has, required to be accepted. Without those controls a tool that refused
everything would pass.

Four laws are generated over closed families rather than written out case by case:

| Law | What is generated | What would break it |
|---|---|---|
| LAW1 | 9 constructs × 4 operations that read source | one operation answering `invalid_program` |
| LAW2 | each construct's reason and its line and column | a reason that does not name the construct |
| LAW3 | the 14 preserved files and their adaptations | refusing every source as out of profile |
| LAW4 | out-of-profile sources against sources already answered | calling every non-declaration top-level form an expression |

LAW4 is the one that guards the rest of the system: the shipped programs stay accepted,
an unbound name stays `unbound_name`, and a misspelled declaration word stays `syntax`.

The tests were seen red before any source changed. The recorded RED run on the
pre-feature tree, with these test files copied over it, exited 1 with 14 of the 17 new
test cases failing in 2.7 s. The three that passed are controls — the accepted twin
keeps its claim and digest, a misspelled declaration word keeps today's refusal, and the
preserved directory holds fourteen files — and no promise is mapped to any of them.

## What is still open

- Whether the manifest should publish a `statuses` map at all, or whether publishing
  the category alone is the scope the owner wants.
- Whether reporting the *first* out-of-profile construct in source order is enough, or
  whether a reader should get every one of them in one pass.
