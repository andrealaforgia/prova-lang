# F10, step 1: the oracle

## What this feature is for

A client that calls the tool and gets a failure should be able to act on
it without reading the sentence the tool wrote: which version of the
source the answer is about, which symbol is at fault, what was expected
there, what was found, and where it stands.

Today the tool writes all of that into one sentence, `reason`. Beside
the sentence it carries only a category, sometimes a place, and never a
revision. A client has to parse prose, and prose is the one part a
maintainer is free to reword.

## What was decided, and why

**"Source revision" means the SHA-256 of the exact bytes the request
submitted.** It is the value the tool already publishes as
`source_digest` for an accepted program. SPEC.md names source digests as
the provenance of a result (lines 270-278) and binds results to source
revisions so that evidence about an old text cannot certify a new one
(lines 476-482). A content digest changes exactly when the text changes,
needs no repository, no clock and no counter, and the client can
recompute it from what it sent. Each diagnostic will carry it as a new
field, `source_revision`.

**No new field at the top level of an answer.** An existing test pins
the top-level keys of a response to exactly six. The answer-level
revision therefore stays the `source_digest` that is already there; only
the diagnostics gain `source_revision`.

**Six refusals that said nothing about where will point at the
declaration they are about**: an unknown type, a record that leads back
to itself, two functions that call each other, an example about another
function, an example with the wrong number of arguments, and an example
value no constructor builds.

**Stated limit.** For those six, the place is the *declaration's* name,
not the offending word. The parsed tree keeps no position for a type
written inside a signature or a record field, for an individual example,
or for a value inside an example, so a finer place does not exist in the
data. The manifest will publish the granularity for each category so a
client is never told a place is the exact word when it is not.

**Two more limits.** The place on a refused argument value points into
the argument text the request supplied, not into the source. And the two
refusals about the request itself, `operation_unavailable` and
`unknown_operation`, carry no revision: no source was submitted for them
to be about.

**`expected` and `actual` carry a type name for a type error and a count
for a wrong number of arguments.** The manifest publishes which kind
each category uses, so one field name never means two things to a client
that read the schema.

**No formal model.** The tool answers one request in one pass, keeps
nothing between requests and writes nothing, so there is no state,
protocol, concurrency or crash behaviour for a model to explore.

**The question service (Jev) was authorized but unavailable**:
`TYPESAFE_API_KEY` is absent from the environment and the client exits
3. The four open semantic questions were decided locally and are written
down above.

## One question for the owner

An existing test says that when a source uses a construct the profile
does not have, the refusal carries "no digest of a source it did not
check through". It pins that absence at the top level of the answer
only. Criterion 1 of this request says *every* diagnostic carries the
source revision. Stamping the revision inside the diagnostic keeps that
test passing, but it does go against the sentence its docstring states.
The question is asked at the pause.

## What was built

Nineteen checks, none of which the tool passes today. They drive the
real `prova` command over its JSON surface; the three laws drive the
service's public operation contract in process, as the other property
tests in this repository do.

| File | What it proves |
|---|---|
| `test_f10_b1_...revision_of_its_source.py` | every refusal says which text it is about, and two texts are two revisions |
| `test_f10_b2_...symbol_expected_and_actual.py` | a type error names its symbol and both types, as separate fields |
| `test_f10_b3_a_reader_refusal_still_says_where.py` | a refused argument value and a refused source both say where the reader stopped |
| `test_f10_b4_the_fields_do_not_depend_on_the_prose.py` | one defect, three operations and extra unrelated text: the same fields |
| `test_f10_b5_...new_revision.py` | the repaired program is accepted and binds to its new revision |
| `test_f10_b6_...says_where_it_stands.py` | the six unplaced refusals now name a symbol and a place |
| `test_f10_b7_the_manifest_says_what_each_refusal_carries.py` | the manifest publishes the shape of every category, and the refusals match it |
| `tests/properties/test_f10_diagnostic_fields.py` | the three laws, over mutations of the shipped program crossed with the four operations that read source |

The red run is recorded in the workspace journal: `exit 1`, 19 failing
checks, run against the tree as it was before this feature.

## What is still open

The owner's answer to the question above. Nothing else: the design step
comes next and will say where each field is built and which object owns
it.
