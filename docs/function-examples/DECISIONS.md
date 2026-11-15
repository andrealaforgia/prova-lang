# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 2)

- **decisions**:
  - DEC1: the refusal of an example about another function carries a new published word, unrelated_example, because none of the 13 published categories states that defect: they report a name that does not resolve, a count, a type, a repeated declaration, a cycle, a hidden binding or a reserved word. SPEC.md line 233 calls such an example unrelated, so the word is the language's own.
  - DEC2: an example that names its own function but writes another number of arguments is answered with the published word arity_mismatch, which the tool already answers with for a call, a constructor and a builtin operator written with the wrong number of arguments. One defect, one word.
  - DEC3: an example naming an undeclared function and an example naming another declared function are one defect with one word: in both the example is not about the function that declares it. The refusal adds that the name is not declared when it is not.
  - DEC4: these refusals carry no line and column. A parsed example keeps no position, and giving it one would change syntax.py, which a parallel delivery holds; the refusal names the function and the ordinal of the example instead.
  - DEC5: no owner is present in this run. Every decision above was taken by the executor and is recorded here for the reviewer.
  - DEC6: no formal model (Quint). The rule is a pure whole-program check over a parsed source: no state, no protocol, no concurrency and no crash window for a model to explore.
