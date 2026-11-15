"""F10.B7 -- the manifest publishes, for every diagnostic category, the
fields a refusal of that category carries.

A client reads the shape once from the tool instead of guessing it from
examples: which fields it gets, what kind of value each holds, whether
the refusal is placed and what the place points into.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the manifest published a schema nobody honours. The
last test checks every refusal the nine fixture programs draw against
the schema the manifest publishes for its category.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    ALL_CASES,
    check,
    diagnostics,
    discover,
)

SCHEMA_KEYS = {"fields", "location", "source_revision"}
PROSE_AND_CATEGORY = {"category", "reason"}


def _schemas() -> dict:
    result = discover().get("result") or {}
    schemas = result.get("diagnostic_schemas")
    assert isinstance(schemas, dict), (
        f"the manifest publishes no diagnostic schemas: {sorted(result)}. A "
        "client reads the shape of a refusal from the tool."
    )
    return schemas


def test_the_manifest_describes_every_category_it_publishes():
    """Given the manifest, then every category in
    `diagnostic_categories` has a schema saying its fields, its place and
    whether it carries a revision."""
    result = discover().get("result") or {}
    schemas = _schemas()

    for category in result.get("diagnostic_categories") or []:
        assert category in schemas, (
            f"the manifest publishes the category {category!r} but says nothing "
            f"about what a refusal of that category carries: {sorted(schemas)}."
        )
        schema = schemas[category]
        assert set(schema) == SCHEMA_KEYS, (
            f"the schema for {category!r} is {sorted(schema)}, expected "
            f"{sorted(SCHEMA_KEYS)}: {schema}."
        )
        assert isinstance(schema["fields"], dict), schema
        assert schema["source_revision"] in ("always", "never"), schema


def test_every_refusal_matches_the_schema_published_for_its_category():
    """Given the 9 refused programs, when each is checked, then every
    field of every refusal is one the schema for its category names, and
    every field the schema names is there."""
    schemas = _schemas()

    for why, case in ALL_CASES.items():
        for entry in diagnostics(check(case.source)):
            schema = schemas[entry["category"]]
            named = set(schema["fields"])
            if schema["source_revision"] == "always":
                named.add("source_revision")
            if schema["location"] is not None:
                named.add("location")
            carried = set(entry) - PROSE_AND_CATEGORY

            assert carried == named, (
                f"the refusal for {why} carries {sorted(carried)} but its "
                f"schema names {sorted(named)}: {entry}. A client reads the "
                "shape from the manifest, so the two agree."
            )
