"""F12.B1 -- a valid program is answered with the tree the tool built, and
every node of that tree says where it stands in the source.

The law: an agent reads the program's structure from the answer instead of
guessing it from the source text, and can open the exact place any part of
it stands at.

still passes if: the tool answered a tree whose places were all line 1
column 1. The second test reads the source at each place and demands the
spelling the node carries stands there, so a default or a shifted place
fails.
"""

from __future__ import annotations

import json
import subprocess

from _f12_tree_fixtures import ask_for_the_tree, nodes_of, place_of, text_at

# This test owns the source it sends. The pair published under
# conformance is read by the fixture test alone, so that a change to
# what is published cannot quietly change what these tests observe.
SOURCE = (
    "(deftype Counter (record (held Int)))\n"
    "(defn held-of\n"
    "  (sig ((counter Counter)) -> Int ! pure)\n"
    "  (examples (example (held-of (Counter 1)) => 1))\n"
    "  (.held counter))\n"
)

# The node kinds that stand where a word of the source is written, and
# the part of the node that word spells. A node of any other kind stands
# where its parenthesised form opens, and is read only for standing on a
# character that is not a space.
SPELLED_BY = {
    "field": "name",
    "parameter": "name",
    "name": "name",
    "comment": "text",
}


def test_a_valid_program_is_answered_with_the_tree_of_its_declarations():
    answer = ask_for_the_tree(SOURCE)

    assert answer["status"] == "completed", (
        f"a valid program was answered {answer['status']!r}: {answer}. A program "
        "that breaks no rule is answered with its tree; make the answer carry "
        "the tree the tool built"
    )
    tree = answer["result"]["tree"]
    assert tree["kind"] == "program", (
        f"the answer's tree is a {tree.get('kind')!r}, not the program: {tree}. "
        "The whole program is the root of the tree an agent reads"
    )
    declared = [(node["kind"], node["name"]) for node in tree["declarations"]]
    assert declared == [("record_type", "Counter"), ("function", "held-of")], (
        f"the tree declares {declared}, and the source declares the record "
        "'Counter' and the function 'held-of', in that order. Every "
        "declaration of the source stands in the tree, in source order"
    )


def test_the_answer_says_which_source_it_is_about_and_claims_only_a_tree():
    answer = ask_for_the_tree(SOURCE)

    assert answer["claim"] == {"kind": "syntax_tree", "scope": "this input"}, (
        f"the answer claims {answer.get('claim')}: {answer}. Reading a program "
        "proves nothing about it beyond its shape; say so in the claim, as the "
        "operations beside it do"
    )
    assert len(answer["source_digest"]) == 64, (
        f"the answer carries the source revision {answer.get('source_digest')!r}: "
        "every answer about a submitted text says which text it is about; stamp "
        "the revision the way the operations beside it do"
    )


def test_every_node_stands_at_a_place_the_source_really_has():
    tree = ask_for_the_tree(SOURCE)["result"]["tree"]

    nodes = nodes_of(tree)
    placeless = sorted({node["kind"] for node in nodes if "position" not in node})
    assert placeless == [], (
        f"these node kinds carry no place: {placeless}. An agent that cannot "
        "open the line a node stands at is back to searching the source text; "
        "give every node its line and column"
    )
    for node in nodes:
        line, column = place_of(node)
        assert line >= 1 and column >= 1, (
            f"the {node['kind']!r} node stands at line {line} column {column}: "
            "places are counted from line 1 column 1; build the place from the "
            "form the node was read from"
        )
        rest = text_at(SOURCE, place_of(node))
        spelling = node.get(SPELLED_BY.get(node["kind"], ""))
        if spelling is not None and isinstance(spelling, str):
            assert rest.startswith(spelling), (
                f"the {node['kind']!r} node spells {spelling!r} but the source "
                f"at line {line} column {column} holds {rest[:20]!r}: a place "
                "that does not point at what the node says is worse than none; "
                "carry the place of the form the node was read from"
            )
        else:
            assert rest[:1] not in ("", " "), (
                f"the {node['kind']!r} node stands at line {line} column "
                f"{column}, where the source holds {rest[:20]!r}: a node stands "
                "where its form starts, never on blank space"
            )


def test_the_command_answers_the_same_tree_as_the_library():
    """The walking skeleton: the real command, over its standard input,
    answers the tree the library answers."""
    finished = subprocess.run(
        ["prova"],
        input=json.dumps({"prova": "i1", "operation": "parse", "source": SOURCE}),
        capture_output=True,
        text=True,
        timeout=30.0,
    )

    answered = json.loads(finished.stdout)
    assert answered["result"]["tree"] == ask_for_the_tree(SOURCE)["result"]["tree"], (
        "the command and the library answered different trees: "
        f"{finished.stdout}. One tool answers one tree for one source; build "
        "the answer in one place"
    )
