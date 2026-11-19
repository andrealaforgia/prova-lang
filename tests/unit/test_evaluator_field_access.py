"""Regression: `.field` access must resolve the field declarations of the
operand's own type, not `program.types[constructor]` (which is keyed by
declared type name and only coincides with the constructor for records).
Guards the fix for the crash reported against I1.S2.B2: a core-0 program
with a record type, field-accessed, used to raise an unhandled KeyError
in the evaluator.

Three cases here are superseded expectations: they selected a field
through a union-typed operand, which SPEC.md line 142 does not define and
the checker now refuses, so the evaluator is never asked. Each says so
where it stands, and the lookup each used to reach is pinned below on the
function that owns it, which every constructed value still reaches.

The functions below pin: a record accessed directly, the refusal a union
operand now gets at one, two and more variants and fields, a name shared
between a record and a union variant, and the failure path `_fields_of`
takes when a constructor names neither.
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


def test_field_access_on_a_union_typed_operand_is_refused():
    """Superseded expectation. This program used to be accepted and
    `.value` evaluated against whichever variant the value carried.
    SPEC.md line 142 defines field selection only for records and
    resolves it from the operand's nominal type, and `b` is of the union
    type `Box`, so the tool now refuses it before anything is evaluated:
    the selection is defined for `Full` and undefined for `Empty`, which
    is what used to reach the evaluator as a failure of the tool. The
    lookup this case used to reach is pinned below, on the function that
    owns it."""
    response = service.handle({"prova": "i1", "operation": "examples", "source": UNION_SOURCE})

    assert response["status"] == "invalid_program", response
    assert [d["category"] for d in response["diagnostics"]] == ["unbound_field"], response
    assert response["diagnostics"][0]["symbol"] == "Box.value", response


def test_the_fields_of_a_union_variant_are_resolved_from_the_variant():
    """The branch the refused program above used to reach: asked for the
    fields of `Full`, the lookup answers with the variant's own field
    declarations, not `program.types['Full']`, which holds nothing."""
    program = syntax.parse_program(read_program(UNION_SOURCE))

    assert syntax.resolve_constructor("Full", program) == ("Box", (("value", "Int"),))
    assert syntax.resolve_constructor("Empty", program) == ("Box", ())


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


def test_a_field_two_variants_of_one_union_both_declare_is_refused_too():
    """Superseded expectation. `.side` used to be read off whichever
    variant the value carried. A selector resolves from the operand's
    nominal type (SPEC.md line 142), and `Shape` is a union, so this is
    refused whether or not every variant happens to declare the field.
    The resolution it used to reach is pinned on the lookup below."""
    response = service.handle({"prova": "i1", "operation": "examples", "source": TWO_VARIANT_SOURCE})

    assert response["status"] == "invalid_program", response
    assert [d["category"] for d in response["diagnostics"]] == ["unbound_field"], response
    assert response["diagnostics"][0]["symbol"] == "Shape.side", response


def test_the_second_variant_of_a_union_is_not_matched_by_the_first():
    program = syntax.parse_program(read_program(TWO_VARIANT_SOURCE))

    assert syntax.resolve_constructor("Square", program) == ("Shape", (("side", "Int"),))


MULTI_FIELD_SOURCE = """
(deftype Range (union (Bounded (low Int) (high Int)) (Unbounded)))
(defn get-high (sig ((r Range)) -> Int ! pure)
  (examples (example (get-high (Bounded 1 9)) => 9))
  (.high r))
"""


def test_a_selector_on_a_union_carrying_several_fields_is_refused():
    """Superseded expectation. `.high` used to be read off the
    `Bounded` variant by name. The operand is of the union type
    `Range`, so the selector is refused before anything runs; selecting
    by name rather than by position zero is pinned below, where it is
    still decided, and on the record case above."""
    response = service.handle({"prova": "i1", "operation": "examples", "source": MULTI_FIELD_SOURCE})

    assert response["status"] == "invalid_program", response
    assert [d["category"] for d in response["diagnostics"]] == ["unbound_field"], response
    assert response["diagnostics"][0]["symbol"] == "Range.high", response


def test_the_declared_fields_of_a_variant_keep_their_names_and_order():
    program = syntax.parse_program(read_program(MULTI_FIELD_SOURCE))

    assert syntax.resolve_constructor("Bounded", program) == (
        "Range",
        (("low", "Int"), ("high", "Int")),
    )


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
