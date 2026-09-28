"""I1.S1.P1 and I1.S1.P2: `step` matches SPEC.md's six-row transition table.

Given the reservation source and the complete six-element (state, event)
domain, when each pair is submitted to the real `evaluate` operation on the
protected `step` function, then the returned state and acceptance flag match
the independently recorded table (P1), and separately satisfy the general
before/accepted/after transition rule the table encodes (P2), without either
check deriving its expected values from the other or from production code.
"""

from __future__ import annotations

import itertools

import pytest

from _prova_client import load_reservation_source, parse_value, run_prova

# The independent oracle: SPEC.md's six-row transition table, copied by hand.
TABLE = [
    (0, "Reserve", 1, True),
    (1, "Reserve", 2, True),
    (2, "Reserve", 2, False),
    (0, "Release", 0, False),
    (1, "Release", 0, True),
    (2, "Release", 1, True),
]


def _evaluate_step(before: int, event: str, source: str | None = None):
    source = load_reservation_source() if source is None else source
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": "step",
        "arguments": [f"(Reservation {before})", f"({event})"],
    }
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0, f"tool failure evaluating step({before}, {event}): stderr={stderr!r}"
    assert response is not None, f"non-JSON response evaluating step({before}, {event}): {stdout!r}"
    assert response.get("operation") == "evaluate", response
    assert response.get("status") == "completed", response
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text, f"no result value for step({before}, {event}): {response}"
    ctor, args = parse_value(value_text)
    assert ctor == "Outcome" and len(args) == 2, f"unexpected result shape: {value_text!r}"
    state_value, accepted_value = args
    state_ctor, state_args = state_value
    assert state_ctor == "Reservation" and len(state_args) == 1, f"unexpected state shape: {value_text!r}"
    after = state_args[0]
    # Types, not just values: Python's `True == 1`, so an integer flag or a
    # boolean count would otherwise satisfy an equality against the table.
    assert type(after) is int, f"state count is not an integer: {value_text!r}"
    assert type(accepted_value) is bool, f"accepted flag is not a boolean: {value_text!r}"
    return after, accepted_value, response


assert {(before, event) for before, event, _, _ in TABLE} == {
    (0, "Reserve"), (1, "Reserve"), (2, "Reserve"),
    (0, "Release"), (1, "Release"), (2, "Release"),
}, "TABLE must cover the complete six-pair domain, including (1, Reserve) and (2, Release)"


def _check_p1_row(before, event, expected_after, expected_accepted, source=None):
    after, accepted, response = _evaluate_step(before, event, source)
    assert (after, accepted) == (expected_after, expected_accepted), (
        f"step({before}, {event}) expected (after={expected_after}, accepted={expected_accepted}), "
        f"got (after={after}, accepted={accepted}); full response={response}"
    )


@pytest.mark.parametrize("before,event,expected_after,expected_accepted", TABLE)
def test_p1_step_matches_table_row(before, event, expected_after, expected_accepted):
    _check_p1_row(before, event, expected_after, expected_accepted)


def judge_transition(before, event_name, after, accepted):
    """Independent P2 rule: acceptance predicate, +1/-1 delta when accepted,
    unchanged when rejected, state within 0..2, with exact types. Returns the
    list of violated clauses."""
    expected_accepted = (before < 2) if event_name == "Reserve" else (before > 0)
    delta = 1 if event_name == "Reserve" else -1
    expected_after = before + delta if expected_accepted else before
    violations = []
    if type(after) is not int or type(accepted) is not bool:
        violations.append("types")
    if not (0 <= after <= 2):
        violations.append("range")
    if accepted != expected_accepted:
        violations.append("acceptance predicate")
    if after != expected_after:
        violations.append("delta")
    if not expected_accepted and after != before:
        violations.append("rejected must preserve count")
    return violations


@pytest.mark.parametrize(
    "before,event_name",
    list(itertools.product((0, 1, 2), ("Reserve", "Release"))),
)
def test_p2_transition_rule_holds(before, event_name):
    after, accepted, response = _evaluate_step(before, event_name)
    assert judge_transition(before, event_name, after, accepted) == [], (
        f"step({before}, {event_name}) returned (after={after}, accepted={accepted}); response={response}"
    )


# Controlled result mutations: the rule must reject each wrong result, so an
# implementation that merely stays in bounds cannot pass.
ALL_PAIRS = list(itertools.product((0, 1, 2), ("Reserve", "Release")))


def test_p2_rule_rejects_an_always_reject_result():
    caught = [(b, e) for b, e in ALL_PAIRS if judge_transition(b, e, b, False)]
    assert set(caught) == {(0, "Reserve"), (1, "Reserve"), (1, "Release"), (2, "Release")}


def test_p2_rule_rejects_an_always_accept_result():
    caught = [(b, e) for b, e in ALL_PAIRS if judge_transition(b, e, min(2, max(0, b + (1 if e == "Reserve" else -1))), True)]
    assert set(caught) == {(2, "Reserve"), (0, "Release")}


def test_p2_rule_rejects_a_flipped_acceptance_flag_that_keeps_the_invariant():
    for before, event in ALL_PAIRS:
        truth = (before < 2) if event == "Reserve" else (before > 0)
        after = before + ((1 if event == "Reserve" else -1) if truth else 0)
        assert judge_transition(before, event, after, not truth), (before, event)


def test_p2_rule_rejects_a_missing_upper_guard():
    assert judge_transition(2, "Reserve", 3, True)  # overflows the range
    assert judge_transition(2, "Reserve", 2, True)  # wrong flag with unchanged count


def test_p2_rule_rejects_a_missing_lower_guard():
    assert judge_transition(0, "Release", -1, True)


def test_p2_rule_rejects_wrong_types():
    assert judge_transition(0, "Reserve", 1, 1)  # integer flag
    assert judge_transition(0, "Reserve", True, True)  # boolean count


# Wrong-body controls through the real tool: each mutated `step` body must be
# caught by the P1 table check for at least one of the six rows.
_ORIGINAL_GUARD = "(if (< (.reserved current) 2)"
_ORIGINAL_RESERVE = "(Outcome (Reservation (+ (.reserved current) 1)) true)"
_ORIGINAL_REJECT = "(Outcome current false)"


def _mutated(old: str, new: str) -> str:
    source = load_reservation_source()
    assert source.count(old) >= 1, old
    return source.replace(old, new, 1)


WRONG_BODIES = {
    "missing upper guard": _mutated(_ORIGINAL_GUARD, "(if true"),
    "flipped acceptance flag": _mutated(_ORIGINAL_REJECT, "(Outcome current true)"),
    "always reject": _mutated(_ORIGINAL_RESERVE, "(Outcome current false)"),
}


@pytest.mark.parametrize("name", sorted(WRONG_BODIES))
def test_p1_table_check_fails_on_wrong_body_control(name):
    source = WRONG_BODIES[name]
    failures = []
    for before, event, expected_after, expected_accepted in TABLE:
        try:
            _check_p1_row(before, event, expected_after, expected_accepted, source)
        except AssertionError as error:
            failures.append((before, event, str(error)[:80]))
    assert failures, f"the P1 check passed all six rows on the {name!r} wrong-body control"
