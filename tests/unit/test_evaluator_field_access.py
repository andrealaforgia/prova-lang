"""Regression: `.field` access on a union-variant value must resolve the
variant's own field declarations, not `program.types[constructor]` (which
is keyed by declared type name and only coincides with the constructor for
records). Guards the fix for the crash reported against I1.S2.B2: a
core-0 program with a union type carrying fields, field-accessed on a
variant value, used to raise an unhandled KeyError in the evaluator.
"""

from __future__ import annotations

from prova import service

SOURCE = """
(deftype Box (union (Full (value Int)) (Empty)))
(defn get-value (sig ((b Box)) -> Int ! pure)
  (examples (example (get-value (Full 5)) => 5))
  (.value b))
"""


def test_field_access_on_union_variant_resolves_its_own_field():
    response = service.handle({"prova": "i1", "operation": "examples", "source": SOURCE})

    assert response["status"] == "completed", response
    results = response["result"]["examples"]
    assert len(results) == 1
    assert results[0]["passed"] is True, results[0]
    assert results[0]["actual"] == "5"
