# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 1)

- **decisions**:
  - S23: Answer the over-long literal with the published syntax category, whose reason names both lengths, and document the length in the discover answer under integer_literals: a third entry under resource_limits.limits would fail tests/acceptance/test_f14_b9, which the request forbids editing, and the sentence itself offers the syntax category as the other answer. The owner is absent, so this is recorded as my decision.
  - DEC1: The limit is 1000 digits. It stands far below the 4300 of the interpreter, so every conversion this tool makes is well inside the interpreter own limit, and far above the 20 digits a value that fills 64 bits is written with; an integer below it is answered exactly.
  - DEC2: The UTF-8 rule is enforced once, in the request reader, by the SubmittedText value object every text field of a request is built through; SourceRevision.of now takes that object, so the hashing site cannot be reached with a text that has no bytes.
  - DEC3: An arguments element or a function name holding a lone surrogate is now refused as malformed_request naming that element, where a surrogate argument used to be answered malformed_value: one rule for every text a request carries. No existing test covered that case.
  - DEC4: No formal model, Quint or otherwise, pays here: the change adds no state, no protocol, no concurrency and no crash behaviour; it is one refusal decided from the text of one request.
  - DEC5: Found and not fixed, for the owner: an integer the evaluator computes, as three multiplications over 1000-digit literals, still ends in ValueError from values.render with exit 1. It is not a literal being converted, answering it needs a refusal for a value too large to write, and values.py is outside the files this delivery changes.
  - DEC6: Found and not fixed, for the owner: a budget variable set to a 5000-digit number ends in ValueError at budgets.py int(written). It enters from the environment and not from a request, so it is outside both families of this request.
  - DEC7: No prefactor commit was needed: service.py is the adapter that reads the request, the domain modules already take value objects, and the one text threaded through it became the SubmittedText value object inside this change.
