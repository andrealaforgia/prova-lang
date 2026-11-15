"""F9.B6 -- a caller learns the new answer from the tool: the manifest
lists the `unsupported` status beside the statuses already answered, and
the out-of-profile category beside the categories already published.

Follows F3, F4 and F5, which each published their new category the same
way.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the manifest listed every string anyone invented. The
test also requires what the manifest already published to still be
there, requires an invented name to be absent, and requires each listed
status to be one the tool really answers with.
"""

from __future__ import annotations

from _f9_profile_fixtures import (
    OUT_OF_PROFILE,
    UNSUPPORTED_CATEGORY,
    UNSUPPORTED_STATUS,
    check,
    discover,
)

CATEGORIES_THE_TOOL_ALREADY_PUBLISHED = (
    "syntax",
    "unbound_name",
    "cyclic_dependency",
    "duplicate_declaration",
    "recursive_type",
    "shadowed_binding",
    "reserved_name",
)

STATUSES_THE_TOOL_ALREADY_ANSWERS_WITH = (
    "completed",
    "invalid_program",
    "invalid_input",
    "unavailable",
)


def test_the_manifest_lists_the_status_and_the_category_this_rule_adds():
    """Given a caller that asks the tool what it can answer, when it
    reads the manifest, then `unsupported` is listed among the statuses
    with a sentence saying what it means, the out-of-profile category is
    listed beside the 7 already published, and a name the tool never
    answers with is absent."""
    result = discover().response().get("result", {})
    statuses = result.get("statuses", {})
    published = result.get("diagnostic_categories", [])

    assert UNSUPPORTED_STATUS in statuses, (
        f"the manifest does not list the {UNSUPPORTED_STATUS!r} status, so a "
        f"caller cannot learn that the tool answers with it: {statuses}. A "
        "caller that only knows 'invalid_program' would read an out-of-profile "
        "source as a program that breaks a rule."
    )
    meaning = statuses[UNSUPPORTED_STATUS]
    assert "core-0" in meaning and "profile" in meaning, (
        f"the manifest does not say what {UNSUPPORTED_STATUS!r} means: "
        f"{meaning!r}. Publish the meaning with the name."
    )
    missing_statuses = [
        status
        for status in STATUSES_THE_TOOL_ALREADY_ANSWERS_WITH
        if status not in statuses
    ]
    assert not missing_statuses, (
        f"the manifest lists {sorted(statuses)} and leaves out {missing_statuses}, "
        "which the tool already answers with. A list of statuses that is not "
        "every status sends a caller to guess the rest."
    )

    assert UNSUPPORTED_CATEGORY in published, (
        f"the manifest does not list {UNSUPPORTED_CATEGORY!r}: {published}. "
        "Publish every category the tool can answer with."
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
    assert "out_of_profile" not in published and "out_of_profile" not in statuses, (
        f"the manifest publishes a name the tool never answers with: {result}. "
        "Publish only what the tool reports."
    )


def test_the_published_status_is_the_one_an_out_of_profile_source_gets():
    """Given the status the manifest publishes for an out-of-profile
    source, when such a source is checked, then that is the status the
    answer carries, so the manifest and the tool cannot drift apart."""
    published = discover().response()["result"]["statuses"]
    answered = check(OUT_OF_PROFILE["division"].source).response()["status"]

    assert answered in published, (
        f"the tool answered {answered!r}, which the manifest does not list: "
        f"{sorted(published)}. A caller reads the vocabulary from the manifest."
    )
    assert answered == UNSUPPORTED_STATUS, (
        f"a source using division was answered {answered!r}: the status the "
        "manifest describes for an out-of-profile source must be the one it "
        "gets."
    )
