"""What the obligation inventory refuses to build at all.

Two things can only be reached by building a program by hand, past the
reader and the checker that stand in front of them in the product: a call
to a function the program never declares, and two obligations claiming one
identity. Both are programming errors, so both refuse loudly with what
failed, why it matters and how to fix it, rather than answering a list the
Owner would have to distrust.

The positive control in the same file builds a valid program the same way
and reads the five kinds of obligation out of it, so a refusal that fired
for the wrong reason cannot pass unnoticed.
"""

from __future__ import annotations

import pytest

from prova import discharge, obligations, syntax


def _function(name: str, body: object, requires: tuple = (), ensures: tuple = ()) -> syntax.Function:
    return syntax.Function(
        name=name,
        signature=syntax.Signature((("n", "Int"),), "Int", 1, 1),
        requires=requires,
        ensures=ensures,
        examples=(syntax.Example(name, (1,), 1, 1, 1),),
        body=body,
        line=1,
        column=1,
    )


def test_a_call_to_a_function_the_program_never_declares_is_refused():
    """Given a program built by hand whose body calls a function nothing
    declares, when its obligations are listed, then the attempt refuses and
    says who called what, where, and which operation reports it."""
    caller = _function("caller", syntax.Call("missing", (syntax.NameRef("n"),)))
    program = syntax.Program(types={}, functions={"caller": caller})

    with pytest.raises(ValueError) as refusal:
        obligations.inventory_for(program)

    message = str(refusal.value)
    for expected in ("caller", "missing", "body", "WHAT:", "WHY:", "HOW:", "check"):
        assert expected in message, (
            f"WHAT: the refusal does not mention {expected!r}: {message}. "
            "WHY: a refusal has to name the call it could not list and the operation "
            "that reports it, or the reader cannot act on it. "
            "HOW: read the message built in prova.obligations."
        )


def test_two_obligations_may_not_claim_one_identity():
    """Given two obligations built with the same identity, when they are
    gathered into one inventory, then the inventory refuses and names the
    identity they share."""
    site = obligations.Site(("contract",))
    twice = (
        obligations.ContractDefinedness("step", site, 1),
        obligations.ContractDefinedness("step", site, 1),
    )

    with pytest.raises(ValueError) as refusal:
        obligations.Inventory(twice)

    assert "contract_definedness:step:contract" in str(refusal.value), refusal.value


def _settling_none_of(inventory) -> dict:
    """One finding per obligation saying nobody attempted it.

    The inventory lists what a program owes and asks no solver, so this
    is what it says on its own. Written here because rendering the list
    now takes one finding per obligation: an obligation with none refuses
    to be written out at all, so nothing can be silently dropped.
    """
    return {
        obligation.identity: discharge.Finding.not_attempted_because(
            "this test lists what a program owes and settles none of it"
        )
        for obligation in inventory.obligations
    }


def test_a_program_built_by_hand_owes_all_five_kinds():
    """Given a one-function program that calls a function it does declare,
    when its obligations are listed, then the five kinds SPEC.md names are
    all there and every one of them is not attempted."""
    callee = _function("inner", syntax.NameRef("n"), requires=(syntax.BoolLit(True),))
    caller = _function("outer", syntax.Call("inner", (syntax.NameRef("n"),)))
    program = syntax.Program(types={}, functions={"inner": callee, "outer": caller})

    owed = obligations.inventory_for(program)
    listed = owed.as_dict(_settling_none_of(owed))

    assert set(listed["totals"]["by_kind"]) == {
        "call_precondition",
        "body_postcondition",
        "example_validity",
        "contract_definedness",
        "structural_termination",
    }, listed["totals"]
    assert {entry["result"] for entry in listed["obligations"]} == {"not_attempted"}
    called = [e for e in listed["obligations"] if e["kind"] == "call_precondition"]
    assert len(called) == 1 and called[0]["precondition_clauses"] == 1, called
