# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 2)

- **decisions**:
  - S3: Change it. The acceptance criteria and SPEC.md lines 137-143 are the authority for what the tool refuses, so exactly one superseded expected result was changed, named in the craft record, and nothing else was touched
  - S23: Refuse it, as the criterion and SPEC.md lines 137-143 require. The superseded unit test now observes that refusal, and the record-over-variant resolution it used to guard is pinned directly on the lookup that owns it
  - DEC1: Both declaration places are named inside the reason text as "line L column C", because a diagnostic carries a single location field and the request limits the service change to one new category name
  - DEC2: The new category is named duplicate_declaration, as suggested, because one name covers functions, types, constructors, fields and redeclared builtins and keeps the published vocabulary small
  - DEC3: Redeclaring Int, Bool or Unit carries that same category, because it is a second declaration of a name the language already declares
  - DEC4: A record declares a type and a constructor of the same name at the same place, so declaring one record twice is reported once: one defect with one repair, not two refusals
  - DEC5: The single location field of the diagnostic points at the later declaration, the one a reader removes; every place still appears in the reason
  - DEC6: No formal model (Quint): the rule is one pass over a list of declared names, with no state, protocol, concurrency or crash behaviour to model
  - DEC7: Jev was unavailable (TYPESAFE_API_KEY absent from the environment, client exit 3), so the decisions above were taken locally and are recorded here for review
  - DEC8: The owner is absent; every decision here is mine and is recorded so a reviewer can overturn it
  - DEC9: No new characterization test for the shipped programs: the existing test_f2_char1_shipped_programs_still_check.py already proves they are still accepted
