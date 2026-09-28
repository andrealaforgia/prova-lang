"""I1.S2.P3 / I1.S2.P2: every single-example wrong expectation is reported
as exactly that example failing, across every Outcome-field category.

For each of the seven declared examples, a separate copy replaces only that
example's expected value with a different value of the same type: a Boolean
flip, a different `Reservation n`, or, for the four `step` examples, a
changed count alone, a flipped flag alone and both changed. Counts include
-1, 0, 1, 2 and 3 where they differ from the original, plus integers drawn
by Hypothesis (derandomized, bounded). The same public `examples` operation
must fail precisely the selected identity and pass the other six, and the
failed identity must move with the edit (P2). Calls, bodies and the other
six expectations are never touched.
"""

from __future__ import annotations

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from _prova_client import parse_value
from _i1_s2_fixtures import (
    INVENTORY,
    extract_results,
    index_by_identity,
    protected_source,
    run_examples,
)

SOURCE = protected_source()
IDENTITIES = [(e["function"], e["ordinal"]) for e in INVENTORY]


def _example_line(entry: dict) -> str:
    call = " ".join([entry["function"], *entry["arguments"]])
    return f"({call}) => {entry['expected']}"


def _copy_with_expected(entry: dict, new_expected: str) -> str:
    """Copy of the protected source with one expected value replaced."""
    old = _example_line(entry)
    assert SOURCE.count(old) == 1, f"{old!r} must occur exactly once in the protected source"
    new = f"({' '.join([entry['function'], *entry['arguments']])}) => {new_expected}"
    mutated = SOURCE.replace(old, new, 1)
    # Structural single-edit check: undoing the one replacement restores the
    # protected source byte for byte, so nothing else differs.
    assert mutated.replace(new, old, 1) == SOURCE
    assert mutated != SOURCE
    return mutated


def _assert_only_fails(entry: dict, mutated: str, label: str) -> dict:
    returncode, response, stdout, stderr = run_examples(mutated)
    assert returncode == 0, f"{label}: tool failure: stderr={stderr!r}"
    assert response is not None, f"{label}: non-JSON response: {stdout!r}"
    assert response.get("status") == "completed", (
        f"{label}: a wrong expected value is an example verdict, not a rejection: {response}"
    )
    results = extract_results(response)
    assert len(results) == 7, f"{label}: expected seven results, got {results}"
    indexed = index_by_identity(results)
    assert set(indexed) == set(IDENTITIES), f"{label}: inventory changed: {sorted(indexed)}"
    target = (entry["function"], entry["ordinal"])
    failed = sorted(i for i, r in indexed.items() if r["passed"] is not True)
    assert failed == [target], f"{label}: expected only {target} to fail, failed={failed}"
    # The actual result is not adjusted to the expectation: it is still the
    # protected source's original expected value.
    assert parse_value(indexed[target]["actual"]) == parse_value(entry["expected"]), (
        f"{label}: actual result moved: {indexed[target]}"
    )
    assert parse_value(indexed[target]["expected"]) != parse_value(entry["expected"]), (
        f"{label}: reported expected value is not the edited one: {indexed[target]}"
    )
    return indexed


def _ctor(count: int, flag: bool | None = None) -> str:
    return f"(Reservation {count})" if flag is None else f"(Outcome (Reservation {count}) {str(flag).lower()})"


BOOL_ENTRIES = [e for e in INVENTORY if e["expected"] in ("true", "false")]
INITIAL_ENTRY = next(e for e in INVENTORY if e["function"] == "initial")
STEP_ENTRIES = [e for e in INVENTORY if e["function"] == "step"]


def _step_parts(entry: dict) -> tuple[int, bool]:
    ctor, (state, flag) = parse_value(entry["expected"])
    assert ctor == "Outcome"
    return state[1][0], flag


@pytest.mark.parametrize("entry", BOOL_ENTRIES, ids=lambda e: f"{e['function']}-{e['ordinal']}")
def test_p3_boolean_flip_fails_only_that_example(entry):
    flipped = "false" if entry["expected"] == "true" else "true"
    _assert_only_fails(entry, _copy_with_expected(entry, flipped), f"{entry['function']}#{entry['ordinal']} flip")


@pytest.mark.parametrize("count", [-1, 1, 2, 3])
def test_p3_initial_with_different_count_fails_only_initial(count):
    _assert_only_fails(INITIAL_ENTRY, _copy_with_expected(INITIAL_ENTRY, _ctor(count)), f"initial -> {count}")


def _step_cases():
    for entry in STEP_ENTRIES:
        count, flag = _step_parts(entry)
        for other in [-1, 0, 1, 2, 3]:
            if other == count:
                continue
            yield pytest.param(entry, _ctor(other, flag), id=f"step{entry['ordinal']}-state-{other}")
            yield pytest.param(entry, _ctor(other, not flag), id=f"step{entry['ordinal']}-both-{other}")
        yield pytest.param(entry, _ctor(count, not flag), id=f"step{entry['ordinal']}-flag")


@pytest.mark.parametrize("entry,replacement", list(_step_cases()))
def test_p3_step_outcome_field_mutations_fail_only_that_example(entry, replacement):
    _assert_only_fails(entry, _copy_with_expected(entry, replacement), f"step#{entry['ordinal']} -> {replacement}")


_ints = st.integers(min_value=-(10**30), max_value=10**30)


@settings(derandomize=True, max_examples=12, deadline=None)
@given(n=_ints, position=st.sampled_from(range(len(STEP_ENTRIES))), flip=st.booleans())
def test_p3_generated_unequal_counts_in_step_outcomes_fail_only_that_example(n, position, flip):
    entry = STEP_ENTRIES[position]
    count, flag = _step_parts(entry)
    if n == count:
        n += 1
    replacement = _ctor(n, (not flag) if flip else flag)
    _assert_only_fails(entry, _copy_with_expected(entry, replacement), f"step#{position} -> {replacement}")


@settings(derandomize=True, max_examples=12, deadline=None)
@given(n=_ints)
def test_p3_generated_unequal_counts_in_initial_fail_only_initial(n):
    if n == 0:
        n = 7
    _assert_only_fails(INITIAL_ENTRY, _copy_with_expected(INITIAL_ENTRY, _ctor(n)), f"initial -> {n}")


def test_p2_failed_identity_moves_with_each_edit():
    """Editing example i fails identity i, for every i, so identities are
    attributable independently of expected values (several share `true`,
    `false` and `Reservation 0`)."""
    seen = []
    for entry in INVENTORY:
        if entry["expected"] in ("true", "false"):
            replacement = "false" if entry["expected"] == "true" else "true"
        elif entry["function"] == "initial":
            replacement = _ctor(5)
        else:
            count, flag = _step_parts(entry)
            replacement = _ctor(count, not flag)
        indexed = _assert_only_fails(entry, _copy_with_expected(entry, replacement), "identity move")
        seen.append(next(i for i, r in indexed.items() if r["passed"] is not True))
    assert seen == IDENTITIES, f"failed identities did not track the edited examples: {seen}"
