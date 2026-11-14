"""Acceptance test for the request's note that a new diagnostic category
is published by `discover`: a caller that reads the manifest learns the
name of the refusal this feature adds, before meeting it.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the manifest advertised a category the tool never
emits. The refusals in test_f4_b1..b3 observe that same category name in
a real response, so an advertised-but-unused name fails there.
"""

from __future__ import annotations

from _f4_recursive_type_fixtures import RECURSIVE_TYPE_CATEGORY, run


def test_the_manifest_publishes_the_recursive_data_category():
    """Given the tool's manifest, when it is asked for, then the list of
    diagnostic categories it can emit contains the recursive-data
    category."""
    response = run({"prova": "i1", "operation": "discover"}).response()

    categories = response.get("result", {}).get("diagnostic_categories", [])
    assert RECURSIVE_TYPE_CATEGORY in categories, (
        f"the manifest does not publish {RECURSIVE_TYPE_CATEGORY!r} among the "
        f"{len(categories)} categories it advertises: {categories}. A caller reads "
        "the manifest to learn every refusal it may receive; publish every "
        "category the tool can emit."
    )
