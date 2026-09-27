"""Shared helpers for I1.S3 property tests: entry-precondition rejection,
malformed/ill-typed argument rejection and the six-row success table.

Not a test module (no `test_` prefix); pytest will not collect it.
"""

from __future__ import annotations

from _prova_client import load_reservation_source, parse_value, run_prova

EVENTS = ["Reserve", "Release"]

PRECONDITION_CATEGORY = "precondition_violation"
MALFORMED_CATEGORY = "malformed_value"
ILL_TYPED_CATEGORY = "ill_typed_value"

# Independent copy of SPEC.md's six-row transition table (before, event,
# after, accepted), transcribed by hand -- not derived from the mutation
# matrix or fixtures used by any other story's tests.
TABLE = [
    (0, "Reserve", 1, True),
    (1, "Reserve", 2, True),
    (2, "Reserve", 2, False),
    (0, "Release", 0, False),
    (1, "Release", 0, True),
    (2, "Release", 1, True),
]


def evaluate_step(current_text: str, event: str, source: str | None = None):
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source if source is not None else load_reservation_source(),
        "function": "step",
        "arguments": [current_text, f"({event})"],
    }
    return run_prova(request)


def diagnostic_categories(response: dict) -> set[str]:
    return {d.get("category") for d in (response.get("diagnostics") or [])}


def assert_rejected(returncode, response, stdout, stderr, *, category: str, forbidden=()):
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") != "completed", f"expected a rejection, got: {response}"
    assert not response.get("result"), f"rejection carried a successful result: {response}"
    categories = diagnostic_categories(response)
    assert category in categories, f"expected category {category!r} in {categories}: {response}"
    for forbidden_category in forbidden:
        assert forbidden_category not in categories, (
            f"unexpected category {forbidden_category!r} present: {response}"
        )


def assert_success_outcome(returncode, response, stdout, stderr, *, expected_state: int, expected_accepted: bool):
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") == "completed", f"expected success, got: {response}"
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text, f"no successful result value: {response}"
    ctor, args = parse_value(value_text)
    assert ctor == "Outcome" and len(args) == 2, f"unexpected result shape: {value_text!r}"
    state_value, accepted_value = args
    state_ctor, state_args = state_value
    assert state_ctor == "Reservation" and len(state_args) == 1, f"unexpected state shape: {state_value!r}"
    assert state_args[0] == expected_state, (
        f"expected resulting count {expected_state}, got {state_args[0]}: {response}"
    )
    assert accepted_value is expected_accepted, (
        f"expected accepted={expected_accepted}, got {accepted_value}: {response}"
    )
