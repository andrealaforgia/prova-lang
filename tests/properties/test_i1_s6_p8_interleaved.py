"""I1.S6.P8: admitting a large Int in add-one does not admit an invalid
Reservation state. Successful add-one evaluations are interleaved with
reservation `step` calls on invalid counts and on the valid boundary
controls, all against fresh requests, and each keeps its own outcome.
"""

from __future__ import annotations

import pytest

from _i1_s6_fixtures import evaluate_add_one, load_reservation_source, parse_value, run_prova

_LARGE = [
    9223372036854775808,
    -9223372036854775810,
    9007199254740993,
    2**128,
    -(2**64),
    41,
]
_INVALID = [3, -1, 2**63, -(2**63) - 1, 2**53 + 1, -9007199254740995]
_VALID = [(0, "Reserve", 1, True), (2, "Reserve", 2, False), (2, "Release", 1, True), (0, "Release", 0, False)]


def _step(count: int, event: str):
    return run_prova(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": load_reservation_source(),
            "function": "step",
            "arguments": [f"(Reservation {count})", f"({event})"],
        }
    )


def _assert_rejected(count: int, event: str) -> None:
    returncode, response, stdout, stderr = _step(count, event)
    assert returncode == 0, stderr
    assert response is not None, stdout
    assert not response.get("result"), f"step({count}, {event}) returned a value: {response}"
    categories = [d.get("category") for d in response.get("diagnostics") or []]
    assert "precondition_violation" in categories, f"step({count}, {event}): {response}"


def _assert_valid(count: int, event: str, after: int, accepted: bool) -> None:
    returncode, response, stdout, stderr = _step(count, event)
    assert returncode == 0, stderr
    assert response is not None and response.get("status") == "completed", stdout
    ctor, (state, flag) = parse_value(response["result"]["value"])
    assert ctor == "Outcome" and state == ("Reservation", (after,)) and flag is accepted, response


@pytest.mark.parametrize("event", ["Reserve", "Release"])
def test_p8_add_one_successes_do_not_change_reservation_rejections(event):
    for large, invalid in zip(_LARGE, _INVALID):
        returncode, response, stdout, stderr = evaluate_add_one(large)
        assert returncode == 0 and response is not None, (stdout, stderr)
        assert response["status"] == "completed"
        assert parse_value(response["result"]["value"]) == large + 1
        _assert_rejected(invalid, event)


def test_p8_valid_boundary_controls_survive_interleaved_add_one_and_rejections():
    for (count, event, after, accepted), large, invalid in zip(_VALID, _LARGE, _INVALID):
        _assert_valid(count, event, after, accepted)
        _assert_rejected(invalid, "Reserve")
        returncode, response, stdout, stderr = evaluate_add_one(large)
        assert returncode == 0 and response is not None, (stdout, stderr)
        assert parse_value(response["result"]["value"]) == large + 1
        _assert_rejected(invalid, "Release")
