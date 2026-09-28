"""I1.S6.P5: every exposed representation of an add-one result agrees with
the request's exact successor, and the response checker demonstrably
rejects the four named faulty outputs.

Two kinds of evidence, kept apart:
(1) execution evidence -- live responses from the public interface, with the
    source digest matching the fixed add-one source, every string leaf that
    parses as an integer equal to the successor, and no JSON number carrying
    an integer;
(2) checker-sensitivity evidence -- hand-built faulty responses (echo,
    constant 42, binary64 rounding, signed-64 wrap, float leaf, structured
    field disagreeing with the text) fed to the same checker, each of which
    must be rejected, plus a correct response that must be accepted.
"""

from __future__ import annotations

import hashlib
import re

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s6_fixtures import (
    assert_add_one_result,
    evaluate_add_one,
    fault_binary64_rounding,
    fault_constant_result,
    fault_echo,
    fault_signed_64_wrap,
    load_add_one_source,
)

_INTEGER_TEXT = re.compile(r"^[+-]?[0-9]+$")


def _string_leaves(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _string_leaves(value)
    elif isinstance(node, list):
        for value in node:
            yield from _string_leaves(value)
    elif isinstance(node, str):
        yield node


def _number_leaves(node):
    if isinstance(node, dict):
        for value in node.values():
            yield from _number_leaves(value)
    elif isinstance(node, list):
        for value in node:
            yield from _number_leaves(value)
    elif isinstance(node, (int, float)) and not isinstance(node, bool):
        yield node


def assert_all_representations_agree(response: dict, n: int) -> None:
    """Every integer-looking string in the result, and the value text itself,
    must equal n + 1; no JSON number may appear anywhere in the result."""
    result = response.get("result") or {}
    expected = n + 1
    assert result.get("value") is not None, f"no result value: {response}"
    integer_leaves = [s for s in _string_leaves(result) if _INTEGER_TEXT.match(s)]
    assert integer_leaves, f"no integer representation in result: {response}"
    for leaf in integer_leaves:
        assert int(leaf) == expected, (
            f"representation {leaf!r} disagrees with exact successor {expected}: {response}"
        )
    numbers = list(_number_leaves(result))
    assert not numbers, f"result carries JSON number(s) {numbers}, not decimal strings: {response}"


@settings(derandomize=True, max_examples=12, deadline=None)
@given(
    n=st.one_of(
        st.integers(min_value=2**63, max_value=2**256 - 1),
        st.integers(min_value=-(2**256), max_value=-(2**63) - 1),
        st.integers(min_value=2**53 + 1, max_value=2**63 - 1),
        st.integers(min_value=-(2**63), max_value=-(2**53) - 1),
    )
)
@example(n=2**63)
@example(n=-(2**63) - 2)
@example(n=9007199254740993)
@example(n=2**128 - 1)
def test_p5_live_responses_agree_in_every_exposed_representation(n):
    source = load_add_one_source()
    returncode, response, stdout, stderr = evaluate_add_one(n, source=source)
    assert_add_one_result(returncode, response, stdout, stderr, n=n)
    assert_all_representations_agree(response, n)
    assert response.get("source_digest") == hashlib.sha256(source.encode("utf-8")).hexdigest(), (
        f"response digest does not identify the fixed add-one source: {response}"
    )


def _good(n: int) -> dict:
    return {
        "operation": "evaluate",
        "status": "completed",
        "diagnostics": [],
        "result": {"value": str(n + 1)},
    }


def _run_checker(response: dict, n: int) -> None:
    assert_add_one_result(0, response, "", "", n=n)
    assert_all_representations_agree(response, n)


_N = 2**63 + 5
_M = -(2**64) - 3


@pytest.mark.parametrize("n", [_N, _M, 9007199254740993, -9007199254740995])
def test_p5_checker_accepts_a_correct_response(n):
    _run_checker(_good(n), n)


def _faulty_cases():
    for n in (_N, _M, 2**128 + 9, -(2**128) - 11):
        for name, fault in (
            ("echo", fault_echo),
            ("constant-42", fault_constant_result),
            ("binary64-rounding", fault_binary64_rounding),
            ("signed-64-wrap", fault_signed_64_wrap),
        ):
            response = _good(n)
            response["result"] = {"value": str(fault(n))}
            yield pytest.param(n, response, id=f"{name}-{n}")
        float_leaf = _good(n)
        float_leaf["result"] = {"value": str(n + 1), "approx": float(n + 1)}
        yield pytest.param(n, float_leaf, id=f"float-leaf-{n}")
        disagreeing = _good(n)
        disagreeing["result"] = {"value": str(n + 1), "structured": {"int": str(n)}}
        yield pytest.param(n, disagreeing, id=f"structured-disagrees-{n}")
        rejected = _good(n)
        rejected["status"] = "invalid_input"
        yield pytest.param(n, rejected, id=f"rejection-{n}")
        missing = _good(n)
        missing["result"] = None
        yield pytest.param(n, missing, id=f"missing-result-{n}")


@pytest.mark.parametrize("n,response", list(_faulty_cases()))
def test_p5_checker_rejects_each_faulty_output(n, response):
    with pytest.raises(AssertionError):
        _run_checker(response, n)
