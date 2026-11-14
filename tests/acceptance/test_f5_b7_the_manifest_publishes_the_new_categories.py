"""Acceptance test for F5's published vocabulary: the two refusals this
feature adds are listed by the tool's own manifest, so a caller can read
them from the tool instead of from a document.

Follows F3 and F4, which each published their new category the same way.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the manifest listed every string anyone invented. The
test also requires the categories the tool already published to still be
there, and requires an invented name to be absent.
"""

from __future__ import annotations

from _f5_binding_fixtures import (
    RESERVED_NAME_CATEGORY,
    SHADOWED_BINDING_CATEGORY,
    discover,
)

CATEGORIES_THE_TOOL_ALREADY_PUBLISHED = (
    "cyclic_dependency",
    "duplicate_declaration",
    "recursive_type",
    "unbound_name",
)


def test_the_manifest_lists_the_two_refusals_this_rule_adds():
    """Given a caller that asks the tool what it can report, when it
    reads the manifest, then the 2 new refusal categories are listed
    beside the 4 the tool already published, and a name the tool does
    not report is absent."""
    response = discover().response()
    published = response.get("result", {}).get("diagnostic_categories", [])

    for category in (SHADOWED_BINDING_CATEGORY, RESERVED_NAME_CATEGORY):
        assert category in published, (
            f"the manifest does not list {category!r}, so a caller cannot learn that "
            f"the tool reports it: {published}. Publish every category the tool can "
            "answer with."
        )
    missing = [
        category
        for category in CATEGORIES_THE_TOOL_ALREADY_PUBLISHED
        if category not in published
    ]
    assert not missing, (
        f"the manifest lost the categories {missing}, which the tool already "
        f"published: {published}. Adding a category must not remove one."
    )
    assert "hidden_binding" not in published, (
        f"the manifest lists a category the tool never answers with: {published}. "
        "Publish only the categories the tool reports."
    )
