"""Regression: `.field` access on a union-variant value must resolve the
variant's own field declarations, not `program.types[constructor]` (which
is keyed by declared type name and only coincides with the constructor for
records). Guards the fix for the crash reported against I1.S2.B2: a
core-0 program with a union type carrying fields, field-accessed on a
variant value, used to raise an unhandled KeyError in the evaluator.

`_fields_of` branches over two lookup strategies -- record-type-by-name and
search-all-union-variants -- so one example cannot prove the rule. The
functions below pin: a record accessed directly, a union with more than one
variant (so a loop bug cannot pass by matching only the first), a variant
with more than one field (so a loop bug cannot pass by always returning
index zero), a name shared between a record and a union variant, and the
failure path `_fields_of` takes when a constructor names neither.
"""

from __future__ import annotations

from prova import service, syntax
from prova.reader import read_program

UNION_SOURCE = """
(deftype Box (union (Full (value Int)) (Empty)))
(defn get-value (sig ((b Box)) -> Int ! pure)
  (examples (example (get-value (Full 5)) => 5))
  (.value b))
"""


def test_field_access_on_union_variant_resolves_its_own_field():
    response = service.handle({"prova": "i1", "operation": "examples", "source": UNION_SOURCE})

    assert response["status"] == "completed", response
    results = response["result"]["examples"]
    assert len(results) == 1
    assert results[0]["passed"] is True, results[0]
    assert results[0]["actual"] == "5"


RECORD_SOURCE = """
(deftype Point (record (x Int) (y Int)))
(defn get-x (sig ((p Point)) -> Int ! pure)
  (examples (example (get-x (Point 3 4)) => 3))
  (.x p))
"""


def test_field_access_on_record_type_resolves_via_the_type_declaration():
    response = service.handle({"prova": "i1", "operation": "examples", "source": RECORD_SOURCE})

    assert response["status"] == "completed", response
    results = response["result"]["examples"]
    assert results[0]["passed"] is True, results[0]
    assert results[0]["actual"] == "3"


TWO_VARIANT_SOURCE = """
(deftype Shape (union (Circle (radius Int)) (Square (side Int))))
(defn get-side (sig ((s Shape)) -> Int ! pure)
  (examples (example (get-side (Square 9)) => 9))
  (.side s))
"""


def test_field_access_on_the_second_union_variant_is_not_matched_by_the_first():
    response = service.handle({"prova": "i1", "operation": "examples", "source": TWO_VARIANT_SOURCE})

    assert response["status"] == "completed", response
    results = response["result"]["examples"]
    assert results[0]["passed"] is True, results[0]
    assert results[0]["actual"] == "9"


MULTI_FIELD_SOURCE = """
(deftype Range (union (Bounded (low Int) (high Int)) (Unbounded)))
(defn get-high (sig ((r Range)) -> Int ! pure)
  (examples (example (get-high (Bounded 1 9)) => 9))
  (.high r))
"""


def test_field_access_selects_the_declared_field_by_name_not_by_position_zero():
    response = service.handle({"prova": "i1", "operation": "examples", "source": MULTI_FIELD_SOURCE})

    assert response["status"] == "completed", response
    results = response["result"]["examples"]
    assert results[0]["passed"] is True, results[0]
    assert results[0]["actual"] == "9"


COLLISION_SOURCE = """
(deftype Marker (record (tag Int)))
(deftype Wrapper (union (Marker (value Int)) (Empty)))
(defn get-tag (sig ((m Marker)) -> Int ! pure)
  (examples (example (get-tag (Marker 7)) => 7))
  (.tag m))
"""


def test_a_constructor_name_shared_by_a_record_and_a_union_variant_is_refused():
    """Superseded expectation. This program used to be accepted and its
    `.tag` selection evaluated against the record `Marker`. SPEC.md
    lines 137-143 require constructor names to be unique across the
    whole program, and the program declares `Marker` twice, so the tool
    now refuses it before anything is evaluated. The resolution rule
    this case used to reach is pinned below, on the lookup that owns it.
    """
    response = service.handle({"prova": "i1", "operation": "examples", "source": COLLISION_SOURCE})

    assert response["status"] == "invalid_program", response
    assert [d["category"] for d in response["diagnostics"]] == ["duplicate_declaration"], response


def test_the_record_type_owns_a_constructor_name_a_union_variant_also_uses():
    """The branch the refused program above used to reach: asked for the
    fields of `Marker`, the lookup answers with the record's own field
    declarations, not the union variant's."""
    program = syntax.parse_program(read_program(COLLISION_SOURCE))

    assert syntax.resolve_constructor("Marker", program) == ("Marker", (("tag", "Int"),))


UNRESOLVABLE_CONSTRUCTOR_SOURCE = """
(deftype Box (record (value Int)))
(defn get-value (sig ((b Box)) -> Int ! pure)
  (examples (example (get-value (Mystery 5)) => 5))
  (.value b))
"""


def test_field_access_on_a_constructor_naming_no_declared_type_reports_a_diagnostic_instead_of_crashing():
    response = service.handle(
        {"prova": "i1", "operation": "examples", "source": UNRESOLVABLE_CONSTRUCTOR_SOURCE}
    )

    assert response["status"] != "completed", response
    assert response.get("diagnostics"), response


UNRESOLVABLE_CONSTRUCTOR_IN_BODY_SOURCE = """
(deftype Box (union (Full (value Int)) (Empty)))
(defn crash (sig () -> Int ! pure)
  (examples (example (crash) => 1))
  (.value (Bogus)))
"""


def test_constructor_call_naming_no_declared_type_in_a_function_body_reports_a_diagnostic_instead_of_crashing():
    response = service.handle(
        {"prova": "i1", "operation": "examples", "source": UNRESOLVABLE_CONSTRUCTOR_IN_BODY_SOURCE}
    )

    assert response["status"] != "completed", response
    assert response.get("diagnostics"), response
