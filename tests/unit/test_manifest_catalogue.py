"""One operation per operation category, and a refusal when two claim one.

An agent reads one operation per category out of the manifest. Two
operations claiming one category is a mistake in the catalogue, not
something a request can cause, so it cannot be reached through the
command and is observed here on the module that owns the rule.

Reads the published contract of the manifest module.
"""

from __future__ import annotations

import pytest

from prova import manifest


def test_a_second_operation_claiming_one_category_is_refused():
    """The first claim would quietly disappear from the manifest while
    the tool still answered it, so the second is refused instead."""
    standings = manifest.Standings()
    standings.covers_a_category("checking", "check", "available")

    with pytest.raises(ValueError) as refusal:
        standings.covers_a_category("checking", "inspect", "available")

    said = str(refusal.value)
    for part in ("'check'", "'inspect'", "'checking'", "manifest.py"):
        assert part in said, (
            f"the refusal says {said!r} and does not name {part}: a reader "
            "has to be told which two operations claim which category, and "
            "where to repair it."
        )
    assert standings.published()["categories"]["checking"] == {
        "operation": "check",
        "availability": "available",
    }, (
        "the refused claim changed the category it was refused for; a "
        "refusal leaves what was already there exactly as it was."
    )


def test_each_category_keeps_the_one_operation_that_covers_it():
    """The control: two claims on two categories are both kept, so the
    refusal above is about the repeated category and nothing else."""
    standings = manifest.Standings()
    standings.covers_a_category("checking", "check", "available")
    standings.covers_a_category("building", "build", "unavailable")

    assert standings.published()["categories"] == {
        "checking": {"operation": "check", "availability": "available"},
        "building": {"operation": "build", "availability": "unavailable"},
    }, (
        "two operations covering two categories are not both published: an "
        "agent reads which operation to send for each category from here."
    )
