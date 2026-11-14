"""Acceptance test for F3 criterion 5: a program that redeclares `Int`,
`Bool` or `Unit` is refused.

SPEC.md lines 137-143: builtin types cannot be redeclared.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool refused every program that declares a record
with one `Int` field. The control in
test_f3_b6_programs_that_declare_each_name_once_are_accepted.py declares
the same record under a name the language does not reserve and requires
it to be accepted.
"""

from __future__ import annotations

import pytest

from _f3_duplicate_fixtures import (
    BUILTIN_TYPE_NAMES,
    DUPLICATE_CATEGORY,
    check,
    duplicate_reasons,
    redeclaring_a_builtin,
)


@pytest.mark.parametrize("builtin_name", BUILTIN_TYPE_NAMES)
def test_redeclaring_a_builtin_type_is_refused(builtin_name):
    """Given a program that declares a record type called `Int`, `Bool`
    or `Unit`, when the program is checked, then it is invalid and the
    refusal names the builtin it redeclares."""
    source = redeclaring_a_builtin(builtin_name)

    response = check(source).response()

    assert response.get("status") == "invalid_program", (
        f"a program that redeclares the builtin type {builtin_name!r} was not "
        f"refused: {response}. A builtin type cannot be redeclared; report such a "
        "program as invalid."
    )
    reasons = duplicate_reasons(response)
    assert reasons and all(builtin_name in reason for reason in reasons), (
        f"no refusal in the {DUPLICATE_CATEGORY!r} category names {builtin_name!r}, "
        f"so a reader cannot tell which declaration to remove: {response}. Name the "
        "redeclared builtin type in the reason."
    )
