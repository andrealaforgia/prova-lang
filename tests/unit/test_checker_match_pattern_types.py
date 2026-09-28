"""Regression: `_pattern_bindings` resolved a `match` clause's constructor
pattern only to bind its fields, never checking the constructor could be
resolved at all or that its owning type agreed with the scrutinee's type.
A pattern naming an undeclared constructor, or naming a real constructor of
a type unrelated to the scrutinee, passed static checking silently even
though the module docstring claims every match clause is checked.
"""

from __future__ import annotations

from prova import service

UNBOUND_CONSTRUCTOR_PATTERN = """
(defn bad (sig ((n Int)) -> Int ! pure)
  (examples (example (bad 1) => 1))
  (match n ((X y) 1) (z z)))
"""


def test_pattern_naming_an_undeclared_constructor_is_rejected():
    response = service.handle(
        {"prova": "i1", "operation": "check", "source": UNBOUND_CONSTRUCTOR_PATTERN}
    )

    assert response["status"] != "completed", response
    diagnostics = response.get("diagnostics") or []
    assert any(d["category"] == "unbound_constructor" for d in diagnostics), diagnostics


PATTERN_TYPE_DISAGREES_WITH_SCRUTINEE = """
(deftype X (record (y Int)))
(defn bad (sig ((n Int)) -> Int ! pure)
  (examples (example (bad 1) => 1))
  (match n ((X y) y) (z z)))
"""


def test_pattern_constructor_of_unrelated_type_to_scrutinee_is_rejected():
    response = service.handle(
        {"prova": "i1", "operation": "check", "source": PATTERN_TYPE_DISAGREES_WITH_SCRUTINEE}
    )

    assert response["status"] != "completed", response
    diagnostics = response.get("diagnostics") or []
    assert any(d["category"] == "type_mismatch" for d in diagnostics), diagnostics


PATTERN_TYPE_AGREES_WITH_SCRUTINEE = """
(deftype Pair (record (a Int) (b Int)))
(defn first (sig ((p Pair)) -> Int ! pure)
  (examples (example (first (Pair 1 2)) => 1))
  (match p ((Pair a b) a)))
"""


def test_pattern_constructor_matching_scrutinee_type_is_accepted():
    response = service.handle(
        {"prova": "i1", "operation": "check", "source": PATTERN_TYPE_AGREES_WITH_SCRUTINEE}
    )

    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response
