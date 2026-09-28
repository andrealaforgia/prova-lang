"""Property tests for `match` exhaustiveness (I1.S5.B4).

Exhaustiveness is a universal claim: for ANY set of constructors a `match`
covers, `check` reports `non_exhaustive_match` exactly when a constructor
is missing, and accepts with no diagnostics exactly when every constructor
is covered. Hand-picked examples cannot carry that claim; a `_covers` that
ignored nested columns, or that counted clauses rather than constructors,
would pass them.

Two finite domains are swept exhaustively (every non-empty subset):
- the constructors of a four-constructor union;
- the four value combinations of a two-column record of `Bool` fields,
  where coverage depends on BOTH columns.

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import itertools

from hypothesis import given, settings
from hypothesis import strategies as st

from prova import service

from _i1_s5_fixtures import diagnostic_categories

CONSTRUCTORS = ("Red", "Green", "Blue", "Amber")
COMBINATIONS = tuple(itertools.product(("true", "false"), repeat=2))


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _union_source(covered: list[str]) -> str:
    variants = " ".join(f"({name})" for name in CONSTRUCTORS)
    clauses = " ".join(f"(({name}) {index})" for index, name in enumerate(covered))
    return f"""
(deftype Colour (union {variants}))
(defn f (sig ((c Colour)) -> Int ! pure)
  (examples (example (f (Red)) => 0))
  (match c {clauses}))
"""


def _record_source(covered: list[tuple[str, str]]) -> str:
    clauses = " ".join(
        f"((BoolPair {a} {b}) {index})" for index, (a, b) in enumerate(covered)
    )
    return f"""
(deftype BoolPair (record (a Bool) (b Bool)))
(defn f (sig ((p BoolPair)) -> Int ! pure)
  (examples (example (f (BoolPair true true)) => 0))
  (match p {clauses}))
"""


def _assert_exhaustive_iff_complete(response: dict, complete: bool, covered) -> None:
    if complete:
        assert response["status"] == "completed", (covered, response)
        assert response.get("diagnostics") in (None, []), (covered, response)
    else:
        assert response["status"] == "invalid_program", (covered, response)
        assert diagnostic_categories(response) == {"non_exhaustive_match"}, (
            covered,
            response,
        )


@settings(derandomize=True, max_examples=40, deadline=None)
@given(covered=st.lists(st.sampled_from(CONSTRUCTORS), min_size=1, unique=True))
def test_union_match_is_non_exhaustive_exactly_when_a_constructor_is_missing(covered):
    """Given a union match covering any non-empty subset of the union's
    constructors, when `check` runs, then it reports exactly
    `non_exhaustive_match` if some constructor is missing and accepts it
    with no diagnostics if every constructor is covered."""
    _assert_exhaustive_iff_complete(
        _check(_union_source(covered)), set(covered) == set(CONSTRUCTORS), covered
    )


@settings(derandomize=True, max_examples=40, deadline=None)
@given(covered=st.lists(st.sampled_from(COMBINATIONS), min_size=1, unique=True))
def test_multi_column_record_match_is_non_exhaustive_exactly_when_a_combination_is_missing(
    covered,
):
    """Given a record match over two `Bool` columns covering any non-empty
    subset of the four value combinations, when `check` runs, then it
    reports exactly `non_exhaustive_match` if some combination is uncovered
    and accepts it with no diagnostics if all four are covered."""
    _assert_exhaustive_iff_complete(
        _check(_record_source(covered)), set(covered) == set(COMBINATIONS), covered
    )
