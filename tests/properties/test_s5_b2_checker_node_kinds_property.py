"""Property tests for `checker.py`'s node kinds that Story I1.S5.B2 left
covered by at most one example each: `match` clause disagreement, field
access on an unknown field, constructor-call field-type mismatch, and
call argument-type mismatch. The module docstring in `checker.py` claims
`_infer` "catches a type error anywhere in the program" for every one of
these node kinds; a single hand-built example per kind cannot carry that
universal claim; a bug tied to one specific type pair would pass unnoticed.

Each property sweeps declared/actual type pairs across `core-0`'s three
primitive types and pairs every rejection sweep with a positive control
over the same type set, so the property cannot pass by over-rejecting.

Derandomized with a fixed seed and a bounded example count so the verdict
does not depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from prova import service

from _i1_s5_fixtures import diagnostic_categories, literal

TYPES = ("Bool", "Int", "Unit")


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


_type_pairs_disagreeing = st.tuples(
    st.sampled_from(TYPES), st.sampled_from(TYPES)
).filter(lambda pair: pair[0] != pair[1])
_types = st.sampled_from(TYPES)
_ints = st.integers(min_value=-5, max_value=5)


# --- match clauses disagree ---

def _match_source(clause_a_type: str, clause_b_type: str, n: int) -> str:
    return f"""
(deftype Ev (union (A) (B)))
(defn f (sig ((e Ev)) -> {clause_a_type} ! pure)
  (examples (example (f (A)) => {literal(clause_a_type, 0)}))
  (match e
    ((A) {literal(clause_a_type, n)})
    ((B) {literal(clause_b_type, n)})))
"""


@settings(derandomize=True, max_examples=20, deadline=None)
@given(types=_type_pairs_disagreeing, n=_ints)
def test_match_clauses_disagreeing_are_always_rejected(types, n):
    """Given a `match` whose two clauses produce different types, when
    `check` runs, then it is rejected with a `type_mismatch` diagnostic,
    for every disagreeing type pair."""
    clause_a_type, clause_b_type = types
    response = _check(_match_source(clause_a_type, clause_b_type, n))
    assert response["status"] == "invalid_program", response
    assert diagnostic_categories(response) == {"type_mismatch"}, response


@settings(derandomize=True, max_examples=15, deadline=None)
@given(type_name=_types, n=_ints)
def test_match_clauses_agreeing_are_always_accepted(type_name, n):
    """Positive control: when both `match` clauses produce the same type
    (and that type is the function's declared return type), `check`
    completes with no diagnostics, for every type."""
    response = _check(_match_source(type_name, type_name, n))
    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


# --- field access on an unknown field ---

def _field_access_source(field_name: str) -> str:
    return f"""
(deftype Rec (record (foo Int)))
(defn f (sig ((r Rec)) -> Int ! pure)
  (examples (example (f (Rec 1)) => 1))
  (.{field_name} r))
"""


@settings(derandomize=True, max_examples=15, deadline=None)
@given(field_name=st.sampled_from(("bar", "baz", "quux", "reserved", "state")))
def test_field_access_on_unknown_field_is_always_rejected(field_name):
    """Given a field selector naming a field the target's record type does
    not declare, when `check` runs, then it is rejected with an
    `unbound_field` diagnostic, for every unknown field name tried."""
    response = _check(_field_access_source(field_name))
    assert response["status"] == "invalid_program", response
    assert diagnostic_categories(response) == {"unbound_field"}, response


def test_field_access_on_declared_field_is_accepted():
    """Positive control: selecting the record's one declared field is
    accepted with no diagnostics."""
    response = _check(_field_access_source("foo"))
    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


# --- constructor-call field-type mismatch ---

def _constructor_call_source(arg_type: str, n: int) -> str:
    return f"""
(deftype Rec (record (foo Int)))
(defn f (sig () -> Rec ! pure)
  (examples (example (f) => (Rec 1)))
  (Rec {literal(arg_type, n)}))
"""


_non_int_types = st.sampled_from(("Bool", "Unit"))


@settings(derandomize=True, max_examples=15, deadline=None)
@given(arg_type=_non_int_types, n=_ints)
def test_constructor_call_field_type_mismatch_is_always_rejected(arg_type, n):
    """Given a constructor call whose argument type disagrees with the
    declared field type, when `check` runs, then it is rejected with a
    `type_mismatch` diagnostic, for every disagreeing argument type."""
    response = _check(_constructor_call_source(arg_type, n))
    assert response["status"] == "invalid_program", response
    assert diagnostic_categories(response) == {"type_mismatch"}, response


@settings(derandomize=True, max_examples=10, deadline=None)
@given(n=_ints)
def test_constructor_call_field_type_matching_is_always_accepted(n):
    """Positive control: an `Int` argument for an `Int` field is accepted
    with no diagnostics."""
    response = _check(_constructor_call_source("Int", n))
    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


# --- call argument-type mismatch ---

def _call_source(arg_type: str, n: int) -> str:
    return f"""
(defn g (sig ((n Int)) -> Int ! pure)
  (examples (example (g 1) => 1))
  n)
(defn f (sig () -> Int ! pure)
  (examples (example (f) => 1))
  (g {literal(arg_type, n)}))
"""


@settings(derandomize=True, max_examples=15, deadline=None)
@given(arg_type=_non_int_types, n=_ints)
def test_call_argument_type_mismatch_is_always_rejected(arg_type, n):
    """Given a call whose argument type disagrees with the callee's
    declared parameter type, when `check` runs, then it is rejected with
    a `type_mismatch` diagnostic, for every disagreeing argument type."""
    response = _check(_call_source(arg_type, n))
    assert response["status"] == "invalid_program", response
    assert diagnostic_categories(response) == {"type_mismatch"}, response


@settings(derandomize=True, max_examples=10, deadline=None)
@given(n=_ints)
def test_call_argument_type_matching_is_always_accepted(n):
    """Positive control: an `Int` argument for an `Int` parameter is
    accepted with no diagnostics."""
    response = _check(_call_source("Int", n))
    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


# --- call return type propagates through the caller's own body ---

def _call_return_propagation_source(callee_return_type: str, caller_return_type: str) -> str:
    return f"""
(defn g (sig () -> {callee_return_type} ! pure)
  (examples (example (g) => {literal(callee_return_type, 0)}))
  {literal(callee_return_type, 0)})
(defn f (sig () -> {caller_return_type} ! pure)
  (examples (example (f) => {literal(caller_return_type, 0)}))
  (g))
"""


@settings(derandomize=True, max_examples=20, deadline=None)
@given(types=_type_pairs_disagreeing)
def test_call_result_type_disagreeing_with_caller_return_type_is_always_rejected(types):
    """Given a function whose body is a bare call to another function
    whose return type disagrees with the caller's own declared return
    type, when `check` runs, then it is rejected with a `type_mismatch`
    diagnostic, for every disagreeing type pair -- confirming `Call`
    itself (not just a wrapping literal) propagates its inferred type."""
    callee_return_type, caller_return_type = types
    response = _check(_call_return_propagation_source(callee_return_type, caller_return_type))
    assert response["status"] == "invalid_program", response
    assert diagnostic_categories(response) == {"type_mismatch"}, response


@settings(derandomize=True, max_examples=10, deadline=None)
@given(type_name=_types)
def test_call_result_type_matching_caller_return_type_is_always_accepted(type_name):
    """Positive control: a caller whose body is a bare call to a function
    with the same return type is accepted with no diagnostics."""
    response = _check(_call_return_propagation_source(type_name, type_name))
    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response
