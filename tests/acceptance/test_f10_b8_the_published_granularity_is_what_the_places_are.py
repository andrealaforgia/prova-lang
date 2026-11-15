"""F10.B8 -- a place is as fine as the manifest says it is.

The manifest publishes, for every category, whether a place of that
category stands at a declaration, at an expression or at a token of the
text. A client decides from that whether the place takes it to the word
at fault or only to the declaration around it, so the published word
must be the truth about the places the tool gives.

Drives only the `prova` command's real JSON stdin/stdout surface. The
declaration places are computed here from the submitted text, never read
from the tool.

still passes if: the manifest published one granularity for everything.
Each case pins its own word, every word must be one the manifest
publishes for that category, and the two groups are checked in opposite
directions: a declaration place must be at a declared name and an
expression or token place must not be.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    PLACED_CASES,
    check,
    declared_places,
    discover,
    the_one_refusal,
)


def _location_schema(category: str) -> dict:
    schemas = (discover().get("result") or {}).get("diagnostic_schemas") or {}
    assert category in schemas, f"the manifest says nothing about {category!r}"
    place = schemas[category]["location"]
    assert place is not None, (
        f"the manifest publishes {category!r} as carrying no place, but a "
        "refusal of it carried one"
    )
    return place


def test_every_place_is_as_fine_as_its_category_publishes():
    """Given the 14 refused programs that carry a place, when each is
    checked, then the granularity the manifest publishes for its
    category covers the place it gives: at a declared name for the 6
    published as standing at a declaration, and anywhere but a declared
    name for the others."""
    for why, case in PLACED_CASES.items():
        entry = the_one_refusal(check(case.source), why)
        published = _location_schema(entry["category"])

        assert case.granularity in published["granularity"], (
            f"the refusal for {why} stands at a {case.granularity}, but the "
            f"manifest publishes {published['granularity']} for "
            f"{entry['category']!r}: {entry}. A client reads how fine a place "
            "is from the manifest, so the two must agree."
        )

        place = (entry["location"]["line"], entry["location"]["column"])
        declarations = declared_places(case.source)
        if case.granularity == "declaration":
            assert place in declarations, (
                f"the refusal for {why} is published as standing at a "
                f"declaration but stands at {place}, and the declarations of "
                f"that source stand at {sorted(declarations)}: {entry}."
            )
        else:
            assert place not in declarations, (
                f"the refusal for {why} stands at the declaration {place}, but "
                f"its category is published as standing at a {case.granularity}: "
                f"{entry}. A client told the place is the word at fault would "
                "be sent to the declaration instead."
            )


def test_a_category_that_can_point_into_two_texts_says_which_one():
    """Given each refused program, when it is checked, then a refusal
    whose category can stand in more than 1 text carries the text it
    stands in, and one whose category has a single text carries no such
    field."""
    for why, case in PLACED_CASES.items():
        entry = the_one_refusal(check(case.source), why)
        published = _location_schema(entry["category"])

        if len(published["points_into"]) > 1:
            assert entry.get("points_into") in published["points_into"], (
                f"the refusal for {why} does not say which of "
                f"{published['points_into']} its place stands in: {entry}."
            )
        else:
            assert "points_into" not in entry, (
                f"the refusal for {why} carries a text its category does not "
                f"need, because every place of it stands in "
                f"{published['points_into']}: {entry}."
            )
