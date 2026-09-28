"""Regression: `check_program` inferred a type for a function's body and for
its `requires`/`ensures` clauses but never compared the result to anything,
so a body that disagrees with the declared return type, or a contract
clause that isn't `Bool`, passed static checking silently. A caller relying
on `check` to guarantee the evaluator never runs unchecked code could then
hit a `Bool`-declared function that actually returns `Int`, or a malformed
precondition, with no diagnostic ever raised.
"""

from __future__ import annotations

from prova import service

BOOL_RETURN_BUT_INT_BODY = """
(defn bad (sig () -> Bool ! pure)
  (examples (example (bad) => true))
  1)
"""


def test_body_type_disagreeing_with_declared_return_type_is_rejected():
    response = service.handle({"prova": "i1", "operation": "check", "source": BOOL_RETURN_BUT_INT_BODY})

    assert response["status"] != "completed", response
    diagnostics = response.get("diagnostics") or []
    assert any(d["category"] == "type_mismatch" for d in diagnostics), diagnostics


NON_BOOL_REQUIRES = """
(defn bad (sig ((n Int)) -> Int ! pure)
  (requires 1)
  (examples (example (bad 1) => 1))
  n)
"""


def test_requires_clause_that_is_not_bool_is_rejected():
    response = service.handle({"prova": "i1", "operation": "check", "source": NON_BOOL_REQUIRES})

    assert response["status"] != "completed", response
    diagnostics = response.get("diagnostics") or []
    assert any(d["category"] == "type_mismatch" for d in diagnostics), diagnostics


NON_BOOL_ENSURES = """
(defn bad (sig ((n Int)) -> Int ! pure)
  (ensures 1)
  (examples (example (bad 1) => 1))
  n)
"""


def test_ensures_clause_that_is_not_bool_is_rejected():
    response = service.handle({"prova": "i1", "operation": "check", "source": NON_BOOL_ENSURES})

    assert response["status"] != "completed", response
    diagnostics = response.get("diagnostics") or []
    assert any(d["category"] == "type_mismatch" for d in diagnostics), diagnostics


MATCHING_BODY_AND_CONTRACTS = """
(defn ok (sig ((n Int)) -> Int ! pure)
  (requires (>= n 0))
  (ensures (>= result 0))
  (examples (example (ok 1) => 1))
  n)
"""


def test_matching_body_and_bool_contracts_are_accepted():
    response = service.handle({"prova": "i1", "operation": "check", "source": MATCHING_BODY_AND_CONTRACTS})

    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response
