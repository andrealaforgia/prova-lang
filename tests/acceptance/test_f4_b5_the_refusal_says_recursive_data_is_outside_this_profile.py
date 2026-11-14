"""Acceptance test for F4 criterion 5: the refusal says recursive data
is outside this profile, and never reports the self-held type as an
unknown one.

SPEC.md lines 51-54: unsupported features must be identified as
unsupported, not misdiagnosed as type errors. SPEC.md lines 135-136 say
where recursive data belongs: a later profile.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the refusal named a later profile but gave the reader
no idea which declaration to look at. test_f4_b1..b3 require the same
refusal to name every type on the cycle.
"""

from __future__ import annotations

import pytest

from _f4_recursive_type_fixtures import (
    RECORD_HOLDING_ITSELF,
    TWO_RECORDS_HOLDING_EACH_OTHER,
    UNION_WITH_A_RECURSIVE_VARIANT,
    UNKNOWN_TYPE_CATEGORY,
    categories,
    check,
    recursive_type_diagnostics,
)

RECURSIVE_PROGRAMS = {
    "a record holding itself": RECORD_HOLDING_ITSELF,
    "two records holding each other": TWO_RECORDS_HOLDING_EACH_OTHER,
    "a union with a recursive variant": UNION_WITH_A_RECURSIVE_VARIANT,
}


@pytest.mark.parametrize("described, source", sorted(RECURSIVE_PROGRAMS.items()))
def test_the_refusal_sends_the_reader_to_a_later_profile(described, source):
    """Given a refused recursive program, when its refusal is read, then
    it says recursive data belongs to a later profile and that core-0
    requires the type-dependency graph to be acyclic."""
    response = check(source).response()

    reasons = [d.get("reason", "") for d in recursive_type_diagnostics(response)]
    assert len(reasons) == 1, (
        f"{described} was not refused with 1 recursive-data reason: {response}. "
        "Recursive data is a supported-profile question, so say so once."
    )
    assert "later profile" in reasons[0], (
        f"the refusal of {described} does not tell the reader that recursive data "
        f"belongs to a later profile: {reasons[0]!r}. Identify the unsupported "
        "feature as unsupported."
    )
    assert "acyclic" in reasons[0], (
        f"the refusal of {described} does not state the rule it applies: "
        f"{reasons[0]!r}. Say that core-0 requires the type-dependency graph to be "
        "acyclic, so the reader can check the claim against SPEC.md."
    )


@pytest.mark.parametrize("described, source", sorted(RECURSIVE_PROGRAMS.items()))
def test_a_self_held_type_is_never_reported_as_an_unknown_type(described, source):
    """Given a refused recursive program, when its diagnostics are read,
    then none of them calls a declared type unknown: the 0 unknown-type
    diagnostics keep the unsupported feature from being misdiagnosed."""
    response = check(source).response()

    reported = categories(response)
    assert UNKNOWN_TYPE_CATEGORY not in reported, (
        f"{described} was refused with {reported}, which calls a type the program "
        "declares unknown. Every type on the cycle is declared; report the "
        "unsupported recursion instead of an unknown type."
    )
