# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 2)

- **decisions**:
  - DEC1: Two new published categories, not one and not a reuse. shadowed_binding carries every binding that hides a name already visible, including a pattern that binds one spelling twice, because the second binder hides the first. reserved_name carries a binder that uses result. duplicate_declaration was not reused: it reports a top-level declaration with a place and a declaration uniqueness rule, and a caller filtering on it would start receiving local binder defects.
  - DEC2: builtin in the SPEC sentence is read as the builtin operator names (+ - * < <= > >= = and or not), because they are the only builtins reachable where a value binding is visible; the builtin type names live in the type namespace and a value binding cannot hide them.
  - DEC3: the owner answered option A on this delivery: a parameter is a binding too, so a parameter may hide neither a declared function nor an earlier parameter of its own signature, and a parameter named result is refused; SPEC.md line 145 lists parameters among the bindings the rule governs, and the request outcome sentence alone would have stopped at let bindings and pattern variables.
  - DEC4: service.DIAGNOSTIC_CATEGORIES is edited although the request names only checker.py and tests, because F3 and F4 both published their category there and a category the manifest hides cannot be relied on by a caller.
  - DEC5: no formal model (Quint). The rules are pure functions of one parsed program, with no state, protocol, concurrency or crash: the two generated properties over binder names and clause counts carry the laws.
  - DEC6: typesafe: unavailable: TYPESAFE_API_KEY is absent from this process environment, so jev_decide.py exited 3 before sending anything; the four open questions behind DEC1, DEC2 and DEC3 were settled locally against SPEC.md lines 145-149 and the F3 and F4 code.

## design (revision 1)

- **reuse_decision**: Reused: the Diagnostic value and its category, reason and location fields, so the response shape does not change; syntax.OPERATORS as the one list of builtin operator names; the existing walks of _infer and _pattern_bindings, which keep deciding types. Created new: three small frozen values in checker.py (the names visible at a binding, a binding that hides one of them, a binder that uses the reserved word) and one walk that visits every binder of every function, placed beside the declaration, function-cycle and type-cycle rules. No existing owner fits because nothing in the program today knows what introduced a name: the environment of the type inference maps a name to its type, which cannot say parameter or function, and the duplicate-declaration rule reads top-level declarations only, never a local binder.
- **prefactoring_reason**: The existing code needs no preparation. The rule is a walk over the parsed program that returns its own refusals, added beside the declaration rule, the function-cycle rule and the type-cycle rule in check_program, exactly as F2, F3 and F4 were added; no existing function changes its signature, its result or its behaviour, and no primitive has to be wrapped first because the new values are built from the names and places syntax already carries.
