"""Acceptance test for F4 criterion 4: three types in a chain with no
cycle are accepted.

SPEC.md lines 135-136 forbid a cycle in the type-dependency graph, not a
field whose type is another declared type.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool accepted every program. The refusals in
test_f4_b1..b3 observe the refusal of programs that differ from this one
only in the edge that closes a cycle.
"""

from __future__ import annotations

from _f4_recursive_type_fixtures import CHAIN_OF_THREE_TYPES, check


def test_three_types_in_a_chain_with_no_cycle_are_accepted():
    """Given 3 record types where `Invoice` holds a `Line` and `Line`
    holds a `Money`, when the program is checked, then it is accepted
    with no diagnostics."""
    response = check(CHAIN_OF_THREE_TYPES).response()

    assert response.get("status") == "completed", (
        f"a chain of 3 types with no cycle was not accepted: {response}. A field "
        "whose type is another declared type is ordinary core-0 data; refuse only "
        "a type that can lead back to itself."
    )
    assert response.get("diagnostics") == [], (
        f"an acyclic chain of 3 types carried diagnostics: {response}. Report "
        "nothing about a program whose type-dependency graph is acyclic."
    )
