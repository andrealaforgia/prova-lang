"""Acceptance test for F2 criterion 5: a function whose declared examples
name that same function is still accepted -- those self-calls are not a
cycle.

SPEC.md line 164: "Examples' calls to their own function are excluded
from that graph."

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

This states a behaviour the tool must keep, so the test also builds the
one program the promise must stay distinguishable from: the same function
whose *body* calls it. Accepting both, or refusing both, fails the test.
"""

from __future__ import annotations

from _f2_cycle_fixtures import (
    EXAMPLES_NAME_THEIR_OWN_FUNCTION,
    EXAMPLES_PLUS_A_SELF_CALLING_BODY,
    accepted,
    check,
    reported_cycles,
)


def test_a_function_whose_examples_name_it_is_accepted_unlike_one_that_calls_itself():
    """Given `doubled`, whose two declared examples both name `doubled`
    and whose body is `(+ n n)`, when the program is checked, then it is
    accepted; the same function with `(doubled n)` added to its body is
    refused."""
    examples_only = check(EXAMPLES_NAME_THEIR_OWN_FUNCTION)
    body_calls_itself = check(EXAMPLES_PLUS_A_SELF_CALLING_BODY)

    assert accepted(examples_only), (
        f"a function whose declared examples name it was refused: "
        f"{examples_only.response()}. An example's call to its own function is "
        "excluded from the dependency graph; it is not a cycle."
    )
    refused = body_calls_itself.response()
    assert refused.get("status") == "invalid_program", (
        f"the same function, with a call to itself in its body, was not refused: "
        f"{refused}. The examples are excluded from the graph; the body is not."
    )
    assert reported_cycles(refused) == [frozenset({"doubled"})], (
        f"the refusal does not name `doubled` as the cycle: {refused}. The body's "
        "self-call is the cycle to report."
    )
