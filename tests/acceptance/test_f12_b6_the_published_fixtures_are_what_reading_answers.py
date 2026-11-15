"""F12.B6 -- every source published under conformance is answered with
exactly the tree published beside it.

SPEC.md lines 81-84 require the syntax-tree interchange schema to be fixed
in conformance fixtures. These pairs are that fixing: the tree in each
file was written by hand from the source and the schema, so a change to
what the tool answers is a change a reader must publish.

still passes if: the tool answered a tree with parts added. The
comparison is equality with the published file, so any difference fails.
"""

from __future__ import annotations

import pytest

from _f12_tree_fixtures import (
    PUBLISHED_FIXTURES,
    ask_for_the_tree,
    fixture_source,
    fixture_tree,
    published_pairs,
)

# The pairs this suite reads. Named here rather than discovered, so that
# a pair that stops being published fails instead of disappearing from
# the run.
PUBLISHED = ("comments", "let-and-match", "record-and-function")


def test_every_published_source_is_one_this_suite_reads():
    assert published_pairs() == sorted(PUBLISHED), (
        f"the sources published under {PUBLISHED_FIXTURES.name} are "
        f"{published_pairs()} and this suite reads {sorted(PUBLISHED)}: a "
        "fixture nothing reads fixes nothing; publish each source with the "
        "tree beside it and read it here"
    )


@pytest.mark.parametrize("name", PUBLISHED)
def test_the_published_source_is_answered_with_the_published_tree(name):
    source_file = PUBLISHED_FIXTURES / f"{name}.prova"
    tree_file = PUBLISHED_FIXTURES / f"{name}.tree.json"
    assert source_file.exists() and tree_file.exists(), (
        f"the pair {name!r} is not published: {source_file} and {tree_file} "
        "fix the schema a reader of this tool writes against; publish the "
        "source beside the tree it is answered with"
    )

    answer = ask_for_the_tree(fixture_source(name))
    assert answer["status"] == "completed", (
        f"the published source {name!r} was answered {answer['status']!r}: "
        f"{answer}. A fixture that fixes the schema must be a program the "
        "tool reads"
    )
    assert answer["result"]["tree"] == fixture_tree(name), (
        f"reading {name!r} answered a tree that differs from the one published "
        f"beside it.\nanswered: {answer['result']['tree']}\npublished: "
        f"{fixture_tree(name)}\nThe published fixture is the schema: change "
        "the fixture deliberately, or make the answer match it"
    )
