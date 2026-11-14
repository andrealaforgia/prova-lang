# F5 decisions taken after the first independent review

The reviewer rejected the first candidate with twelve findings. These are
the decisions behind the repairs, in the words of what was checked.

## The reserved word is refused on its own account, with nothing narrowed

A read of `result` in a body or in a precondition is now answered with
`reserved_name`, the agreed category, and no longer as an unbound name.

Before implementing it, every existing test that asserts `unbound_name`
was read to see whether one of them observes a bare read of `result`:
`tests/properties/test_i1_s5_p4.py`, `tests/properties/test_i1_s5_p5.py`,
`tests/acceptance/test_s5_b4_second_invalid_construct_rejected_distinctly.py`,
`tests/acceptance/test_s5_int_check_whole_program_and_reject_invalid_variants.py`
and `tests/unit/test_verify_inventory_edges.py`. All of them use an
ordinary missing name (`missing-count` and the like); none reads
`result`. **So nothing was narrowed and no pre-existing expectation was
weakened**: the owner's standing authorisation to narrow the rule for an
older test was not needed and was not used.

The unbound-name refusal is suppressed for this one name, so a reader
gets one defect with one repair instead of two sentences about the same
word.

## A refusal names the construct whose place the program carries

The parsed program carries no position for a binder itself, only for the
construct that introduces it. Rather than point at a place the tool does
not know, each refusal now says which construct it is reporting: "the
parameter `edge` of the function declared at line 1 column 7", "the let
binding `cents` introduced by the `let` at line 4 column 3", "the
pattern variable `n` of the `match` at line 6 column 3". The reported
line and column are that construct's.

`syntax.py` was deliberately not changed: another delivery owns it, and
per-binder positions belong there, not here.

## The binding rule runs only once the types are known to be acyclic

A program whose types lead back to themselves is answered with the
recursive-data refusal alone, as before. That refusal states that the
functions were not checked, so no refusal about a function's binders may
stand beside it.

## "Generated" was the wrong word

The three laws are checked by parametrized property files over sets of
cases written out by hand: five kinds of binder name across two binder
shapes, clause counts 2 to 5, nesting depths 2, 8 and 40. They sample a
universal claim; they neither enumerate every program nor generate
random input. The wording was corrected in the test file and in the
oracle, design and craft documents.

The tool-generated `docs/binding-scope/DECISIONS.md` still carries the
earlier wording of that decision, because it is rendered from the
recorded oracle; it is regenerated when that record is next revised.

## What is still not claimed

Nothing here has been independently reviewed. The remote question
service was never reached in this environment, so the choice of two
categories and the reading of "builtin" as the operator names carry
local judgment plus the owner's recorded answer about parameters.
