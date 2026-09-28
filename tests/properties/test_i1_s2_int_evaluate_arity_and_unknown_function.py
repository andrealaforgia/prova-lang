"""I1.S2.INT rework: `evaluate` rejects wrong argument counts and undeclared functions.

Given the reservation source, whose `step` function declares two parameters,
when `evaluate` is asked to call `step` with any number of arguments other
than two, then the response is status `invalid_input`, carries an
`arity_mismatch` diagnostic and no result. When it is asked to call a name the
program never declares, the response is `invalid_input` with an
`unknown_function` diagnostic and no result.
"""

from __future__ import annotations

from hypothesis import HealthCheck, given, settings, strategies as st

import pytest

from _prova_client import load_reservation_source, run_prova

DECLARED_ARITY = 2
VALID_ARGUMENTS = ["(Reservation 1)", "(Reserve)"]

DERANDOMIZED = settings(
    derandomize=True,
    max_examples=25,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


def _evaluate(function: str, arguments: list[str]) -> dict:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": load_reservation_source(),
        "function": function,
        "arguments": arguments,
    }
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    return response


def _assert_rejected(response: dict, category: str) -> None:
    assert response.get("status") == "invalid_input", response
    categories = [d.get("category") for d in response.get("diagnostics", [])]
    assert categories == [category], response
    assert "result" not in response, response


@pytest.mark.parametrize("count", [0, 1, 3])
def test_step_with_wrong_argument_count_is_arity_mismatch(count):
    response = _evaluate("step", (VALID_ARGUMENTS * 2)[:count])
    _assert_rejected(response, "arity_mismatch")


@DERANDOMIZED
@given(
    count=st.integers(min_value=0, max_value=6).filter(lambda n: n != DECLARED_ARITY),
    counts=st.lists(st.integers(min_value=0, max_value=3), min_size=6, max_size=6),
)
def test_any_argument_count_other_than_declared_is_arity_mismatch(count, counts):
    arguments = [
        f"(Reservation {counts[i]})" if i % 2 == 0 else "(Reserve)"
        for i in range(count)
    ]
    _assert_rejected(_evaluate("step", arguments), "arity_mismatch")


@DERANDOMIZED
@given(
    name=st.from_regex(r"[a-z][a-z0-9-]{0,11}", fullmatch=True).filter(
        lambda n: n not in {"step", "initial"}
    )
)
def test_undeclared_function_name_is_unknown_function(name):
    source = load_reservation_source()
    if f"(defn {name} " in source or f"(defn {name}\n" in source:
        return
    _assert_rejected(_evaluate(name, list(VALID_ARGUMENTS)), "unknown_function")


def test_declared_arity_still_evaluates_positive_control():
    response = _evaluate("step", list(VALID_ARGUMENTS))
    assert response.get("status") == "completed", response
    assert "result" in response, response
