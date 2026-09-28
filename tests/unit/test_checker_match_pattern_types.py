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


PAIR_DECL = "(deftype Pair (record (a Int) (b Int)))\n"
MAYBE_DECL = "(deftype Maybe (union (None) (Some (v Bool))))\n"


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _categories(response: dict) -> list[str]:
    return [d["category"] for d in response.get("diagnostics") or []]


def _pair_match(pattern: str) -> str:
    return (
        PAIR_DECL
        + "(defn f (sig ((p Pair)) -> Int ! pure)\n"
        + "  (examples (example (f (Pair 1 2)) => 1))\n"
        + f"  (match p ({pattern} 1)))\n"
    )


def test_pattern_with_too_many_subpatterns_is_rejected():
    response = _check(_pair_match("(Pair a b extra)"))

    assert response["status"] != "completed", response
    assert "arity_mismatch" in _categories(response), response


def test_pattern_with_too_few_subpatterns_is_rejected():
    response = _check(_pair_match("(Pair a)"))

    assert response["status"] != "completed", response
    assert "arity_mismatch" in _categories(response), response


def test_pattern_with_exactly_the_declared_subpatterns_is_accepted():
    response = _check(_pair_match("(Pair a b)"))

    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


def _int_match(clauses: str) -> str:
    return (
        "(defn f (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (f 1) => 1))\n"
        f"  (match n {clauses}))\n"
    )


def test_int_match_without_catch_all_is_rejected_as_non_exhaustive():
    response = _check(_int_match("(0 0) (1 1)"))

    assert response["status"] != "completed", response
    assert "non_exhaustive_match" in _categories(response), response


def test_int_match_with_variable_catch_all_is_accepted():
    response = _check(_int_match("(0 0) (k k)"))

    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


def test_int_match_with_wildcard_catch_all_is_accepted():
    response = _check(_int_match("(0 0) (_ 1)"))

    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


def _bool_match(clauses: str) -> str:
    return (
        "(defn f (sig ((b Bool)) -> Int ! pure)\n"
        "  (examples (example (f true) => 1))\n"
        f"  (match b {clauses}))\n"
    )


def test_bool_match_covering_true_and_false_is_accepted():
    response = _check(_bool_match("(true 1) (false 0)"))

    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


def test_bool_match_missing_false_is_rejected_as_non_exhaustive():
    response = _check(_bool_match("(true 1)"))

    assert "non_exhaustive_match" in _categories(response), response


def test_unit_pattern_covers_a_unit_scrutinee():
    response = _check(
        "(defn f (sig ((u Unit)) -> Int ! pure)\n"
        "  (examples (example (f ()) => 1))\n"
        "  (match u (() 1)))\n"
    )

    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


def _maybe_match(clauses: str) -> str:
    return (
        MAYBE_DECL
        + "(defn f (sig ((m Maybe)) -> Int ! pure)\n"
        + "  (examples (example (f (None)) => 0))\n"
        + f"  (match m {clauses}))\n"
    )


def test_union_match_covering_every_variant_is_accepted():
    response = _check(_maybe_match("((None) 0) ((Some v) 1)"))

    assert response["status"] == "completed", response
    assert response.get("diagnostics") in (None, []), response


def test_union_match_missing_a_variant_is_rejected_as_non_exhaustive():
    response = _check(_maybe_match("((None) 0)"))

    assert "non_exhaustive_match" in _categories(response), response


def test_union_payload_patterns_must_be_recursively_exhaustive():
    partial = _check(_maybe_match("((None) 0) ((Some true) 1)"))
    complete = _check(_maybe_match("((None) 0) ((Some true) 1) ((Some false) 2)"))

    assert "non_exhaustive_match" in _categories(partial), partial
    assert complete["status"] == "completed", complete
    assert complete.get("diagnostics") in (None, []), complete


def test_non_exhaustive_match_in_a_branch_no_example_reaches_is_rejected():
    response = _check(
        "(defn f (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (f 1) => 1))\n"
        "  (if (> n 100) (match n (0 0)) n))\n"
    )

    assert "non_exhaustive_match" in _categories(response), response


def test_literal_pattern_of_a_type_other_than_the_scrutinee_is_rejected():
    response = _check(_int_match("(true 1) (_ 0)"))

    assert response["status"] != "completed", response
    assert "type_mismatch" in _categories(response), response


def test_wrong_arity_pattern_does_not_also_report_non_exhaustive():
    response = _check(_pair_match("(Pair a)"))

    assert "non_exhaustive_match" not in _categories(response), response
