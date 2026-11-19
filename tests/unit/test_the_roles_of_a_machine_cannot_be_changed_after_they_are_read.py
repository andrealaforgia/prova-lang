"""The cell that closes a change to the machine's roles no test in this
repository noticed.

It is here because `tools/mutate_encoder.py --modules
src/prova/induction.py` made exactly one change -- the roles a descriptor
resolved to became changeable after they were read -- and every test in
the repository stayed green, the whole suite included. The roles are read
once from the resolved descriptor and every one of the three obligations
is written over them, so a value that can be changed between two of them
would let one obligation be shown over one machine and the next over
another. Nothing in the tool changes it today; nothing may.

The module is imported inside the test, as the other cells here do, so a
module this tool cannot answer yet fails as the case it is.
"""

from __future__ import annotations

import dataclasses

import pytest


def _the_roles_of_a_machine():
    from prova import induction

    return induction.TheRolesOfAMachine(
        init="initial",
        step="step",
        state_of="state-of",
        admissible="admissible",
        invariant="valid-state",
        event_type="Event",
    )


def test_the_function_that_filled_a_role_cannot_be_changed_afterwards():
    """Given the roles one descriptor resolved to, when something tries
    to put another function in one of them, then it is refused and the
    roles still name what the descriptor named."""
    roles = _the_roles_of_a_machine()

    with pytest.raises(dataclasses.FrozenInstanceError):
        roles.invariant = "something-else"

    assert roles.invariant == "valid-state", (
        f"WHAT: the invariant role now names {roles.invariant!r}. "
        "WHY: the three obligations of a machine are each written over "
        "these names; a role that could change between two of them would "
        "let one obligation be shown over one machine and the next over "
        "another, and the answer would report both as that machine's. "
        "HOW: keep the roles a value nothing can change once it is read."
    )


def test_every_role_the_obligations_are_written_over_is_closed_the_same_way():
    """Given the roles one descriptor resolved to, when something tries
    to put another name in any one of them, then every one of them is
    refused."""
    roles = _the_roles_of_a_machine()
    named = {
        field.name: getattr(roles, field.name)
        for field in dataclasses.fields(roles)
    }

    refused = []
    for role in named:
        try:
            setattr(roles, role, "something-else")
        except dataclasses.FrozenInstanceError:
            refused.append(role)

    assert sorted(refused) == sorted(named), (
        f"WHAT: {sorted(set(named) - set(refused))} of the roles took a new "
        f"name: the roles now read {dataclasses.asdict(roles)}. "
        "WHY: an obligation is written over each of these names, so all of "
        "them must be as fixed as the descriptor that resolved them. "
        "HOW: keep every one of them closed, not only the invariant."
    )
