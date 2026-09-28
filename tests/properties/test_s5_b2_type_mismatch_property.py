"""Property test accompanying I1.S5.B2's unit tests in
tests/unit/test_checker_return_and_contract_types.py.

That module's claims are universal -- ANY body whose inferred type
disagrees with a function's declared return type is rejected as
`type_mismatch`, and ANY non-`Bool` `requires`/`ensures` clause is rejected
the same way -- but each was tested with exactly one example (one
Bool-declared/Int-bodied function, one `1`-literal clause). A checker bug
tied to a specific type pair (say, correct for Bool-vs-Int but silent for
Int-vs-Unit) or to flat literals only (silent once the mismatched value is
wrapped in an `if` or `let`) would pass every one of those single examples.

This generates the declared/body type pair, which contract clause (if any)
is under test, and the syntactic shape wrapping the value (a bare literal,
an `if` with agreeing branches, or a `let` binding) across all three
`core-0` primitive types (`Bool`, `Int`, `Unit`). It also sweeps the
positive control -- declared type equals body type, contracts hold -- across
the same type/shape matrix, so the property test cannot pass by making the
checker reject everything.

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from prova import service

TYPES = ("Bool", "Int", "Unit")
SHAPES = ("flat", "if", "let")


def _literal(type_name: str, n: int) -> str:
    if type_name == "Bool":
        return "true" if n % 2 == 0 else "false"
    if type_name == "Int":
        return str(n)
    return "()"


def _shaped(expr_text: str, shape: str) -> str:
    if shape == "flat":
        return expr_text
    if shape == "if":
        return f"(if true {expr_text} {expr_text})"
    return f"(let ((y {expr_text})) y)"


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _has_type_mismatch(response: dict) -> bool:
    diagnostics = response.get("diagnostics") or []
    return any(d["category"] == "type_mismatch" for d in diagnostics)


_type_pairs_disagreeing = st.tuples(
    st.sampled_from(TYPES), st.sampled_from(TYPES)
).filter(lambda pair: pair[0] != pair[1])
_shapes = st.sampled_from(SHAPES)
_ints = st.integers(min_value=-5, max_value=5)


@settings(derandomize=True, max_examples=40, deadline=None)
@given(types=_type_pairs_disagreeing, shape=_shapes, n=_ints)
def test_body_type_disagreeing_with_declared_return_type_is_always_rejected(types, shape, n):
    """Given any declared return type and a body of a different type,
    wrapped in a bare literal, an `if` or a `let`, when `check` runs, then
    it is rejected with a `type_mismatch` diagnostic, for every type pair
    and every shape."""
    declared_type, body_type = types
    body = _shaped(_literal(body_type, n), shape)
    source = f"""
(defn f (sig () -> {declared_type} ! pure)
  (examples (example (f) => {_literal(declared_type, 0)}))
  {body})
"""
    response = _check(source)
    assert response["status"] != "completed", response
    assert _has_type_mismatch(response), response


_non_bool_types = st.sampled_from(("Int", "Unit"))
_clause_kinds = st.sampled_from(("requires", "ensures"))


@settings(derandomize=True, max_examples=30, deadline=None)
@given(clause_kind=_clause_kinds, clause_type=_non_bool_types, shape=_shapes, n=_ints)
def test_non_bool_contract_clause_is_always_rejected(clause_kind, clause_type, shape, n):
    """Given a `requires` or `ensures` clause whose inferred type is `Int`
    or `Unit`, wrapped in any shape, when `check` runs, then it is rejected
    with a `type_mismatch` diagnostic, for both clause kinds, both non-Bool
    types and every shape."""
    clause = _shaped(_literal(clause_type, n), shape)
    source = f"""
(defn f (sig ((n Int)) -> Int ! pure)
  ({clause_kind} {clause})
  (examples (example (f 1) => 1))
  n)
"""
    response = _check(source)
    assert response["status"] != "completed", response
    assert _has_type_mismatch(response), response


@settings(derandomize=True, max_examples=30, deadline=None)
@given(type_name=st.sampled_from(TYPES), shape=_shapes, n=_ints)
def test_matching_body_and_bool_contracts_are_always_accepted(type_name, shape, n):
    """Given a declared return type equal to the body's type (across all
    three `core-0` primitive types and every shape), with `true` `requires`
    and `ensures` clauses, when `check` runs, then it completes with no
    diagnostics -- the positive control that keeps the rejection tests
    above from passing by over-rejecting."""
    body = _shaped(_literal(type_name, n), shape)
    source = f"""
(defn f (sig () -> {type_name} ! pure)
  (requires true)
  (ensures true)
  (examples (example (f) => {_literal(type_name, n)}))
  {body})
"""
    response = _check(source)
    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response
