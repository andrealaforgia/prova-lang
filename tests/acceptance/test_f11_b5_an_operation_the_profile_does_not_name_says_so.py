"""F11.B5 -- the tool answers `evaluate`, which is in none of SPEC.md's
seven operation categories. The manifest says so, so that an agent
reading the list of operations never takes it for profile conformance.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool listed an operation as beyond the profile and
still claimed a category for it. The second test checks the two lists
against each other in both directions, so an operation that is in a
category and also beyond the profile, or in neither, fails.
"""

from __future__ import annotations

from _f11_manifest_fixtures import (
    THE_CATEGORIES_SPEC_NAMES,
    availability_of_each_operation,
    part_of_the_manifest,
    published_categories,
)


def _beyond_the_profile() -> dict:
    return part_of_the_manifest(
        "beyond_profile",
        "tell which operations of this tool are its own and which are the "
        "ones the profile names",
    )


def test_an_operation_the_profile_does_not_name_is_marked_as_the_tools_own():
    """Given the tool, which answers `evaluate`, when an agent reads the
    manifest, then `evaluate` is listed as beyond the profile with a
    reason, and not as one of the 7 categories."""
    beyond = _beyond_the_profile()
    categories = published_categories()

    assert "evaluate" in beyond, (
        f"the manifest marks {sorted(beyond)} as beyond the profile and "
        "says nothing about 'evaluate', which this tool answers and SPEC.md "
        f"lines 467-468 name in none of {list(THE_CATEGORIES_SPEC_NAMES)}. "
        "An agent reads the operation list as what the profile asks for."
    )
    assert isinstance(beyond["evaluate"], str) and len(beyond["evaluate"]) > 30, (
        f"'evaluate' is marked beyond the profile with {beyond['evaluate']!r} "
        "and no reason an agent can read."
    )
    claimed = {entry["operation"] for entry in categories.values()}
    assert "evaluate" not in claimed, (
        "'evaluate' is named as the operation of one of SPEC.md's "
        f"categories ({sorted(categories)}) and is also marked as beyond "
        "the profile. It cannot be both."
    )


def test_every_operation_is_either_in_a_category_or_marked_as_beyond_it():
    """Given the operations the tool advertises, then each one is either
    the operation of one of the 7 categories or marked beyond the
    profile, and none is both."""
    operations = set(availability_of_each_operation())
    in_a_category = {entry["operation"] for entry in published_categories().values()}
    beyond = set(_beyond_the_profile())

    assert not (in_a_category & beyond), (
        f"{sorted(in_a_category & beyond)} are published both as the "
        "operation of a category and as beyond the profile."
    )
    assert operations == in_a_category | beyond, (
        f"the tool advertises {sorted(operations)}; the categories cover "
        f"{sorted(in_a_category)} and {sorted(beyond)} are marked beyond "
        "the profile. An operation in neither list leaves an agent unable "
        "to tell what it is."
    )
