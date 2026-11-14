"""Acceptance test for the edge of the binding rule: programs whose
binders are odd but still parseable are answered with one JSON
response, never with a crash.

A `let` that binds nothing, a binder written as a number, a binding with
one value too many and a `match` with no clause all reach the rule.
Whatever the tool decides about them, a caller must get an answer it can
read, and nothing on standard error that looks like a traceback.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered everything with the same refusal.
The empty program below is required to be accepted, so an answer is not
simply a refusal of all input.
"""

from __future__ import annotations

import pytest

from _f5_binding_fixtures import (
    EMPTY_SOURCE,
    ODD_BUT_PARSEABLE_BINDERS,
    assert_accepted,
    check,
)

ODD_PROGRAMS = [
    pytest.param(
        ODD_BUT_PARSEABLE_BINDERS[index + 1],
        ODD_BUT_PARSEABLE_BINDERS[index],
        id=ODD_BUT_PARSEABLE_BINDERS[index].replace(" ", "-"),
    )
    for index in range(0, len(ODD_BUT_PARSEABLE_BINDERS), 2)
]


@pytest.mark.parametrize("source,description", ODD_PROGRAMS)
def test_an_odd_binder_is_answered_and_not_crashed_on(source: str, description: str):
    """Given a program with an odd but parseable binder, when it is
    checked, then the command exits 0 with 1 readable JSON response
    whose status is either `completed` or `invalid_program`, and prints
    no traceback."""
    outcome = check(source)
    response = outcome.response()

    assert outcome.exit_code == 0, (
        f"the command exited {outcome.exit_code} on {description}: "
        f"{outcome.stderr[-400:]!r}. Every request is answered with one JSON "
        "response on standard output."
    )
    assert response.get("status") in ("completed", "invalid_program"), (
        f"{description} was answered with {response}. An odd binder is either "
        "accepted or refused; both are answers a caller can read."
    )
    assert "Traceback" not in outcome.stderr, (
        f"{description} ended in a traceback: {outcome.stderr[-400:]!r}. A program "
        "the tool can parse must not crash the rule that reads its binders."
    )


def test_the_empty_program_is_still_accepted():
    """Control: a source with 0 declarations is accepted, so an answer
    above is not simply a refusal of everything unusual."""
    assert_accepted(check(EMPTY_SOURCE), "a program with no declaration at all")
