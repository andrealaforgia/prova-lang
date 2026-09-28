"""Shared helpers for I1.S3 property tests: entry-precondition rejection,
malformed/ill-typed argument rejection and the six-row success table.

Not a test module (no `test_` prefix); pytest will not collect it.
"""

from __future__ import annotations

from functools import lru_cache

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
    # No blanket status check: an entry precondition_violation is reported
    # under status "completed" (the checked pipeline ran to a diagnosed
    # verdict), per the I1.S1.B2 contract already established and judged.
    # malformed_value/ill_typed_value use "invalid_input" instead; either
    # way, "rejected" here means no successful result value, not a specific
    # status string.
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    result = response.get("result") or {}
    assert not result.get("value"), f"rejection carried a successful result: {response}"
    categories = diagnostic_categories(response)
    assert category in categories, f"expected category {category!r} in {categories}: {response}"
    if category == PRECONDITION_CATEGORY:
        assert_cites_precondition(response)
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
    return state_args[0]


_CITATION_MARKERS = ("precondition", "requires", "valid-state")


def assert_cites_precondition(response: dict) -> None:
    """The precondition diagnostic must name the function and its requires
    clause / valid-state check in its reason or location, not just carry a
    category label."""
    diagnostics = [
        d for d in (response.get("diagnostics") or []) if d.get("category") == PRECONDITION_CATEGORY
    ]
    assert diagnostics, f"no precondition diagnostic: {response}"
    text = " ".join(str(d.get(k, "")) for d in diagnostics for k in ("reason", "location", "path")).lower()
    assert "step" in text, f"precondition diagnostic does not name the function step: {diagnostics}"
    assert any(marker in text for marker in _CITATION_MARKERS), (
        f"precondition diagnostic does not cite the requires clause / valid-state: {diagnostics}"
    )


@lru_cache(maxsize=None)
def known_precondition_categories(event: str) -> frozenset:
    _, response, _, _ = evaluate_step("(Reservation 3)", event)
    categories = frozenset(diagnostic_categories(response or {}))
    assert PRECONDITION_CATEGORY in categories, f"reference precondition case not rejected: {response}"
    return categories


def assert_control_succeeds(event: str) -> None:
    """Corrected (Reservation 0) control paired with a rejected family, so a
    blanket rejection of every request is caught per case."""
    returncode, response, stdout, stderr = evaluate_step("(Reservation 0)", event)
    expected_state, expected_accepted = (1, True) if event == "Reserve" else (0, False)
    assert_success_outcome(
        returncode, response, stdout, stderr,
        expected_state=expected_state, expected_accepted=expected_accepted,
    )


def assert_distinct_from_precondition(response: dict, event: str) -> None:
    categories = diagnostic_categories(response)
    assert PRECONDITION_CATEGORY not in categories, f"conflated with precondition: {response}"
    assert categories != known_precondition_categories(event), (
        f"input failure reported with the same categories as a precondition rejection: {response}"
    )
