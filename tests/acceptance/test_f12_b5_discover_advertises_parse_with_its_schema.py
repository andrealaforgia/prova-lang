"""F12.B5 -- the manifest advertises reading a program as available and
publishes the schema the tree it answers is written in.

The law: an agent discovers the shape of the tree from the tool, and
never guesses an undocumented one.

still passes if: the manifest published a schema that named no node kind
the tool actually answers. The last test reads the tree of the shipped
example and demands the manifest publish every kind it holds.
"""

from __future__ import annotations

from _f12_tree_fixtures import (
    ask_for_the_manifest,
    ask_for_the_tree,
    nodes_of,
    oracle_programs,
)
from _reservation_fixtures import reservation_source


def test_reading_a_program_is_advertised_as_available():
    operations = ask_for_the_manifest()["result"]["operations"]

    assert operations["parse"] == "available", (
        f"the manifest advertises reading a program as {operations['parse']!r}: "
        "an agent reads what a tool answers from its manifest, and this tool "
        "answers a tree; advertise it as available"
    )


def test_the_manifest_publishes_the_schema_the_tree_is_written_in():
    result = ask_for_the_manifest()["result"]

    assert "tree_schema" in result, (
        f"the manifest publishes no tree schema: {sorted(result)}. A tree an "
        "agent cannot read the shape of is a tree it guesses at; publish the "
        "schema beside the operation that answers it"
    )
    schema = result["tree_schema"]
    assert schema["kinds"], (
        f"the published schema names no node kind: {schema}. The schema says "
        "which kinds of node a tree holds and what each one carries"
    )
    for kind, published in schema["kinds"].items():
        assert published.get("carries") is not None, (
            f"the published schema says nothing about what a {kind!r} node "
            f"carries: {published}. An agent reads the fields of a node from "
            "the schema"
        )


def test_the_published_schema_names_every_kind_the_tool_answers():
    schema = ask_for_the_manifest()["result"]["tree_schema"]
    tree = ask_for_the_tree(reservation_source())["result"]["tree"]

    answered = {node["kind"] for node in nodes_of(tree)}
    unpublished = sorted(answered - set(schema["kinds"]))
    assert unpublished == [], (
        f"the tool answers node kinds the manifest does not publish: "
        f"{unpublished}. A kind an agent meets but cannot look up is an "
        "undocumented API; publish the schema from the same table the tree is "
        "built from"
    )


def test_the_published_kinds_and_the_answered_kinds_are_one_set():
    """The two tables -- the kinds published and the kinds built -- are
    read against each other in both directions, over every program this
    suite reads a tree of.
    """
    published = set(ask_for_the_manifest()["result"]["tree_schema"]["kinds"])

    answered: set[str] = set()
    for why, source in oracle_programs().items():
        answer = ask_for_the_tree(source)
        assert answer["status"] == "completed", (
            f"{why} was answered {answer['status']!r}: {answer}"
        )
        answered |= {node["kind"] for node in nodes_of(answer["result"]["tree"])}

    unexercised = sorted(published - answered)
    assert unexercised == [], (
        f"the manifest publishes {unexercised}, and no program this suite "
        "reads is answered with a node of those kinds: a published kind no "
        "test exercises is a promise nothing checks, so a change to how it is "
        "built, or to its name, would pass unseen; write a program that uses "
        "it, or stop publishing it"
    )
    unpublished = sorted(answered - published)
    assert unpublished == [], (
        f"the tool answers {unpublished}, which the manifest does not "
        "publish: an agent that meets one of those kinds has nothing to look "
        "it up in"
    )
