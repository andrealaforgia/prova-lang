"""I1.S6.P5 / I1.S6.B1-B4: across mixed sequences of fresh positive and
negative large integers and the control 41, each response corresponds to
that request's exact n + 1, with every exposed result representation
agreeing and no stale, precomputed, echoed or floating-point-corrupted
result.

Two checks: (1) a live sequence of requests against the one fixed add-one
source, each compared with the independent oracle; (2) an analytic check,
without a live tool, that the assertion used above (exact equality against
`independent_add_one`) actually distinguishes four named fault models --
echo, constant-result, binary64-rounding and signed-64-wrap -- for
generated inputs, so a mutant exhibiting one of them could not slip through
undetected.

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

from _i1_s6_fixtures import (
    FAULT_MODELS,
    assert_add_one_result,
    evaluate_add_one,
    independent_add_one,
    load_add_one_source,
    parse_value,
)

_sequence_domain = st.one_of(
    st.integers(min_value=2**63, max_value=2**256 - 1),
    st.integers(min_value=-(2**256), max_value=-(2**63) - 1),
    st.integers(min_value=2**53 + 1, max_value=2**63 - 1),
    st.integers(min_value=-(2**63), max_value=-(2**53) - 1),
    st.just(41),
)


@settings(derandomize=True, max_examples=12, deadline=None)
@given(sequence=st.lists(_sequence_domain, min_size=2, max_size=6))
@example(sequence=[41, 2**63, -(2**63) - 1, 41])
@example(sequence=[9007199254740993, -9007199254740995, 2**128 - 1])
def test_p5_mixed_sequence_each_response_matches_its_own_request(sequence):
    source = load_add_one_source()
    for n in sequence:
        returncode, response, stdout, stderr = evaluate_add_one(n, source=source)
        assert_add_one_result(returncode, response, stdout, stderr, n=n)


# Pinned adjacent-distinct integers near 2^53, 2^63 and 2^128, in several
# orders (ascending, descending, interleaved, sign-changing, repeated), all
# against one fixed source. Adjacent values differ by one, so an echoed,
# stale, cached or binary64-rounded result cannot match its own request.
_ADJACENT = {
    "2^53": [2**53 - 1, 2**53, 2**53 + 1, 2**53 + 2, 2**53 + 3],
    "2^63": [2**63 - 2, 2**63 - 1, 2**63, 2**63 + 1, 2**63 + 2],
    "2^128": [2**128 - 1, 2**128, 2**128 + 1, 2**128 + 2],
}
_NEG_ADJACENT = [-(2**53) - 2, -(2**53) - 1, -(2**63) - 2, -(2**63) - 1, -(2**63), -(2**128) - 1, -(2**128)]
_PINNED_SEQUENCES = {
    "2^53-ascending": _ADJACENT["2^53"],
    "2^53-descending": list(reversed(_ADJACENT["2^53"])),
    "2^63-ascending": _ADJACENT["2^63"],
    "2^63-descending": list(reversed(_ADJACENT["2^63"])),
    "2^128-ascending": _ADJACENT["2^128"],
    "2^128-descending": list(reversed(_ADJACENT["2^128"])),
    "interleaved": [2**53 + 1, 2**63 + 1, 2**128 + 1, 2**53 + 2, 2**63 + 2, 2**128 + 2],
    "sign-changes": [2**63, -(2**63) - 1, 2**63 + 1, -(2**63) - 2, 2**128, -(2**128), 41],
    "repeats": [2**63, 2**63, 2**63 + 1, 2**63, 41, 41, -(2**64)],
    "negatives-adjacent": _NEG_ADJACENT,
    "negatives-reversed": list(reversed(_NEG_ADJACENT)),
    "mixed-permutation-a": [9007199254740993, 41, -9007199254740995, 2**128 - 1, 2**63, -(2**63) - 1],
    "mixed-permutation-b": [-(2**63) - 1, 2**63, 2**128 - 1, -9007199254740995, 41, 9007199254740993],
}


@pytest.mark.parametrize("name", sorted(_PINNED_SEQUENCES))
def test_p5_pinned_adjacent_and_permuted_sequences(name):
    sequence = _PINNED_SEQUENCES[name]
    source = load_add_one_source()
    seen_results = []
    for n in sequence:
        returncode, response, stdout, stderr = evaluate_add_one(n, source=source)
        assert_add_one_result(returncode, response, stdout, stderr, n=n)
        seen_results.append(parse_value(response["result"]["value"]))
    assert seen_results == [n + 1 for n in sequence]


def test_p5_permutations_of_one_multiset_give_permuted_results():
    a = _PINNED_SEQUENCES["mixed-permutation-a"]
    b = _PINNED_SEQUENCES["mixed-permutation-b"]
    assert sorted(a) == sorted(b)
    source = load_add_one_source()
    by_input = {}
    for seq in (a, b):
        for n in seq:
            _, response, _, _ = evaluate_add_one(n, source=source)
            value = parse_value(response["result"]["value"])
            assert by_input.setdefault(n, value) == value, f"order-dependent result for {n}"
            assert value == n + 1


# Values chosen so that none of the four fault models coincides with the
# true successor by construction: every magnitude is far enough from a
# power of two (for binary64-rounding) and far enough outside the signed
# 64-bit range (for signed-64-wrap and echo), and none equals 41/42 (for
# constant-result).
_FAULT_CHECK_VALUES = [
    2**63 + 5,
    2**64 + 7,
    2**100 + 3,
    2**128 + 9,
    2**200 + 1,
    -(2**63) - 9,
    -(2**64) - 3,
    -(2**100) - 7,
    -(2**128) - 11,
    -(2**200) - 5,
]


@example(n=2**63 + 5)
@example(n=-(2**64) - 3)
@given(n=st.sampled_from(_FAULT_CHECK_VALUES))
@settings(derandomize=True, max_examples=len(_FAULT_CHECK_VALUES), deadline=None)
def test_p5_assertion_distinguishes_named_fault_models(n):
    expected = independent_add_one(n)
    for name, fault in FAULT_MODELS.items():
        corrupted = fault(n)
        assert corrupted != expected, (
            f"fault model {name!r} coincides with the exact successor for "
            f"n={n}; the assertion would not catch it for this input"
        )
