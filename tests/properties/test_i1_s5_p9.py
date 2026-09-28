"""I1.S5.P9 / I1.S5.B5: restoring the examples clause (signature, contracts
and body unchanged) makes `check`, `examples` and `evaluate` succeed with
independently calculated results, and rejected and repaired requests
interleaved in either order each keep their complete result.
"""

from __future__ import annotations

import itertools

import pytest

from _i1_s5_b5_fixtures import (
    BODIES,
    CONTRACTS,
    P7_ENSURES_REPAIRED,
    P7_PLAIN_REPAIRED,
    PLACEMENTS,
    assert_accepted_check,
    assert_missing_examples_rejection,
    call,
    declaration,
    place,
    request,
)

SOURCES = list(itertools.product(CONTRACTS, BODIES, PLACEMENTS))


def _fn(body):
    return lambda n: n if body == "n" else n + 1


def _assert_examples_pass(response, returncode, placement, where):
    assert returncode == 0 and response is not None, where
    assert response.get("status") == "completed", f"{where}: {response}"
    assert not response.get("diagnostics"), f"{where}: {response}"
    results = response["result"]["examples"]
    expected = {"f"} | ({"helper"} if placement != "sole" else set())
    assert {r["function"] for r in results} == expected, f"{where}: {results}"
    assert all(r["passed"] is True for r in results), f"{where}: {results}"


def _check_repaired(source, placement, body, where):
    rc, resp, _, _ = call(request("check", source, placement))
    assert_accepted_check(resp, rc, where)
    rc, resp, _, _ = call(request("examples", source, placement))
    _assert_examples_pass(resp, rc, placement, where)
    fns = [("f", _fn(body))] + ([("helper", lambda n: n)] if placement != "sole" else [])
    for name, fn in fns:
        for arg in (0, 2):
            rc, resp, out, err = call(request("evaluate", source, placement, arg, name))
            assert rc == 0 and resp is not None, f"{where}: {out!r} {err!r}"
            assert resp.get("status") == "completed", f"{where}/{name}({arg}): {resp}"
            assert resp["result"]["value"] == str(fn(arg)), f"{where}/{name}({arg}): {resp}"


@pytest.mark.parametrize("source", [P7_PLAIN_REPAIRED, P7_ENSURES_REPAIRED], ids=["plain", "ensures"])
def test_p9_repaired_p7_sources_check_pass_and_evaluate(source):
    _check_repaired(source, "sole", "n-plus-1", "p7-repaired")


@pytest.mark.parametrize("contract,body,placement", SOURCES)
def test_p9_repaired_matrix_sources_succeed(contract, body, placement):
    source = place(declaration(contract, body, with_examples=True), placement)
    _check_repaired(source, placement, body, f"{contract}-{body}-{placement}")


def _assert_good_full_result(operation, resp, rc, placement, where):
    """The complete successful result for `request(operation, ...)`: `check`
    accepted, all declared examples passed, `evaluate` returning the
    independently calculated value (f(0) = 1 for the incrementing body when
    sole; helper(0) = 0 when the helper is selected)."""
    assert rc == 0 and resp is not None, where
    if operation == "check":
        assert_accepted_check(resp, rc, where)
    elif operation == "examples":
        _assert_examples_pass(resp, rc, placement, where)
    else:
        assert resp.get("status") == "completed", f"{where}: {resp}"
        assert not resp.get("diagnostics"), f"{where}: {resp}"
        assert resp["result"]["value"] == ("1" if placement == "sole" else "0"), f"{where}: {resp}"


@pytest.mark.parametrize("contract", CONTRACTS)
@pytest.mark.parametrize("placement", PLACEMENTS)
@pytest.mark.parametrize("order", ["rejected-first", "repaired-first"])
def test_p9_interleaved_rejected_and_repaired_requests_keep_their_full_results(contract, placement, order):
    """Rejected and repaired requests alternate in both orders; every repaired
    response must still carry its complete success result and every rejected
    response its rejection, so neither outcome depends on what the tool ran
    before it."""
    bad = place(declaration(contract, "n-plus-1", with_examples=False), placement)
    good = place(declaration(contract, "n-plus-1", with_examples=True), placement)
    for operation in ("check", "examples", "evaluate"):
        pair = [("bad", bad), ("good", good), ("bad", bad)]
        if order == "repaired-first":
            pair = [("good", good), ("bad", bad), ("good", good)]
        for kind, source in pair:
            rc, resp, out, err = call(request(operation, source, placement))
            where = f"{order}/{contract}/{placement}/{operation}/{kind}"
            if kind == "bad":
                assert_missing_examples_rejection(operation, rc, resp, out, err, where)
            else:
                _assert_good_full_result(operation, resp, rc, placement, where)
