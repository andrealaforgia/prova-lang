# nwstep decisions

kit: 70665f43199a1bd55f2513590e3e4580069d3ebc2dfa38f1c14d28495b6dbeb3 commit: none

## oracle (revision 1)

- **decisions**:
  - DEC1: Reuse the published word for a wrong number of arguments rather than publish a twelfth one. It already answers a call to a declared function and a constructor given the wrong number, both of which state the expected and the actual count, and the repository probe for this rule already expects that word. Reusing it also leaves the manifest in service.py untouched, which keeps this change clear of the delivery running in parallel there.
  - DEC2: When an operator has both a wrong number of operands and an operand of the wrong type, report both, as the sibling rule for a call to a declared function already does, so a reader repairs the expression in one pass. An operand of the right type never adds a second refusal.
  - DEC3: The owner is absent for this run. DEC1 and DEC2 are the author decisions taken in the owner place, both inside what the request already allows: the request lets an existing category be reused when it fits, and the sibling behaviour settles the second.
  - DEC4: No formal model. The rule is a pure comparison of two numbers in one expression, with no state, protocol, concurrency or crash sequence for a model to explore.
