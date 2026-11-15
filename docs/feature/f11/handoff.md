# F11 - handoff: what a later reader gets, and what is not proved

## What is delivered

`discover` is now enough to use this tool. An agent reads from one answer which
of SPEC.md's seven operation categories this tool covers and which it does not,
what to send for each operation it may call and what will come back, every type
and operator a program may be written with, and which operation is this tool's
own rather than part of the profile. Everything the manifest carried before is
unchanged.

## What holds by construction and what holds by test

| Claim | How strongly |
|---|---|
| The manifest describes exactly the operations the tool advertises | cannot be built otherwise |
| An operation is in one category, or is this tool's own - never both, never neither | cannot be built otherwise |
| An operation that can be called has both its shapes; a refused one has none | cannot be built otherwise |
| A category claimed by two operations is refused | checked, with a unit test and a control |
| The published signature of an operator is the one the checker keeps | generated law over the eleven operators |
| A published field sent as another kind of value is refused, by name | generated law, 15 cases |
| An answer carries exactly the fields published for it | generated law, 15 cases |

The last three are evidence from generated cases, not proof. A field whose kind
is published wrongly in a way those laws never draw would not be caught.

## What was not verified

- **A pre-existing crash, not repaired here.** A `check` request whose source
  carries a lone surrogate (`"\udccc"`) ends in a `UnicodeEncodeError` while the
  revision of the source is computed, instead of being answered. Older than this
  change; this change neither caused it nor touched that path. The roadmap
  carries it.
- A fifth observation of the review was recorded as informational and asks for
  no change here; its text stays in the review record.
- Two of the three refusals inside the catalogue (a set of names that disagrees
  with the dispatcher, a shape that disagrees with the availability) are
  programming errors unreachable from the command, and have no test. The third
  has one.
- Nothing was run on another machine or another Python than 3.12. The branch is
  not merged and not pushed. F12 is not merged, so `parse` is still advertised
  as unavailable and answered as such.
- The manifest says what each operation answers. It says nothing about any
  answer being right, and no claim of this delivery reaches what a program means.
