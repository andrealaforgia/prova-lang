"""Property tests for `match` exhaustiveness (I1.S5.B4).

Exhaustiveness is a universal claim: for ANY set of constructors a `match`
covers, `check` reports `non_exhaustive_match` exactly when a constructor
is missing, and accepts with no diagnostics exactly when every constructor
is covered. Hand-picked examples cannot carry that claim; a `_covers` that
ignored nested columns, or that counted clauses rather than constructors,
would pass them.

Two finite domains are swept exhaustively, one parametrized case per
non-empty subset (15 each):
- the constructors of a four-constructor union;
- the four value combinations of a two-column record of `Bool` fields,
  where coverage depends on BOTH columns.

No random generation is involved, so the verdict cannot depend on a seed.
"""

from __future__ import annotations

import itertools

import pytest

from prova import service

from _i1_s5_fixtures import diagnostic_categories

CONSTRUCTORS = ("Red", "Green", "Blue", "Amber")
COMBINATIONS = tuple(itertools.product(("true", "false"), repeat=2))


def _non_empty_subsets(items: tuple) -> list[list]:
    return [
        list(subset)
        for size in range(1, len(items) + 1)
        for subset in itertools.combinations(items, size)
    ]


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


@pytest.mark.parametrize("covered", _non_empty_subsets(CONSTRUCTORS), ids="-".join)
def test_union_match_is_non_exhaustive_exactly_when_a_constructor_is_missing(covered):
    """Given a union match covering any non-empty subset of the union's
    constructors, when `check` runs, then it reports exactly
    `non_exhaustive_match` if some constructor is missing and accepts it
    with no diagnostics if every constructor is covered."""
    _assert_exhaustive_iff_complete(
        _check(_union_source(covered)), set(covered) == set(CONSTRUCTORS), covered
    )


@pytest.mark.parametrize(
    "covered",
    _non_empty_subsets(COMBINATIONS),
    ids=lambda subset: "-".join(a[0] + b[0] for a, b in subset),
)
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
