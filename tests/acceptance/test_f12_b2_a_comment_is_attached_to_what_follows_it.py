"""F12.B2 -- a comment is answered beside the node that follows it, and a
comment that nothing follows is answered at the end of the document.

The law: a reader's comment keeps the part of the program it was written
about, so an agent that reads the tree reads the prose with it.

still passes if: every comment were answered at the document end. The
first test demands the comment written above a declaration stand on that
declaration, so a tool that collected them all at the end fails.
"""

from __future__ import annotations

from _f12_tree_fixtures import ask_for_the_tree, nodes_of

# These tests own the sources they send; the pair published under
# conformance is read by the fixture test alone.
WITH_COMMENTS = (
    "; the counter a program keeps\n"
    "(deftype Counter (record (held Int)))\n"
    "; nothing follows this comment\n"
)

TWO_DECLARATIONS = (
    "; what a counter holds\n"
    "(deftype Counter (record (held Int)))\n"
    "\n"
    "; the whole of what a counter holds\n"
    "(defn held-of\n"
    "  (sig ((counter Counter)) -> Int ! pure)\n"
    "  (examples (example (held-of (Counter 1)) => 1))\n"
    "  (.held counter))\n"
)


TWO_AT_THE_END = (
    "(deftype Counter (record (held Int)))\n"
    "; one last word\n"
    "; and another after it\n"
)

WRITTEN_ON_ANOTHER_SYSTEM = (
    "; a comment ending in two characters\r\n"
    "(deftype Counter (record (held Int)))\r\n"
)


def _comments_of(node: dict) -> list[str]:
    return [comment["text"] for comment in node.get("comments", [])]


def test_each_comment_is_answered_on_the_declaration_written_under_it():
    tree = ask_for_the_tree(TWO_DECLARATIONS)["result"]["tree"]

    counter, held_of = tree["declarations"]
    assert _comments_of(counter) == ["; what a counter holds"], (
        f"the record 'Counter' carries {_comments_of(counter)}: the comment "
        "written on the line above it is about it; attach a comment to the "
        "node that follows it"
    )
    assert _comments_of(held_of) == ["; the whole of what a counter holds"], (
        f"the function 'held-of' carries {_comments_of(held_of)}: a blank line "
        "between a comment and the declaration under it does not separate "
        "them; attach a comment to the node that follows it"
    )


def test_a_comment_nothing_follows_is_answered_at_the_end_of_the_document():
    tree = ask_for_the_tree(WITH_COMMENTS)["result"]["tree"]

    trailing = [comment["text"] for comment in tree.get("trailing_comments", [])]
    assert trailing == ["; nothing follows this comment"], (
        f"the document ends carrying {trailing}: the last comment of this "
        "source has no node after it, so it belongs to the document end; "
        "answer it there rather than dropping it"
    )
    assert [comment["text"] for comment in tree["declarations"][0]["comments"]] == [
        "; the counter a program keeps"
    ], (
        "the first comment of the source did not reach the declaration under "
        f"it: {tree['declarations'][0]}"
    )


def test_two_comments_after_the_last_declaration_are_each_answered_once():
    tree = ask_for_the_tree(TWO_AT_THE_END)["result"]["tree"]

    trailing = [comment["text"] for comment in tree["trailing_comments"]]
    assert trailing == ["; one last word", "; and another after it"], (
        f"the document ends carrying {trailing}: both comments stand after "
        "the last declaration, in the order they were written"
    )
    answered = [node["text"] for node in nodes_of(tree) if node["kind"] == "comment"]
    assert answered == trailing, (
        f"the tree answers {answered} for the 2 comments the source writes: a "
        "comment answered twice, or answered inside another comment, makes a "
        "reader of the tree believe the source says it twice"
    )


def test_a_comment_on_a_text_that_ends_its_lines_with_two_characters():
    tree = ask_for_the_tree(WRITTEN_ON_ANOTHER_SYSTEM)["result"]["tree"]

    assert _comments_of(tree["declarations"][0]) == [
        "; a comment ending in two characters"
    ], (
        f"the comment was answered as "
        f"{_comments_of(tree['declarations'][0])}: what ends the line is not "
        "one of the characters the reader wrote, so it is no part of the "
        "comment; a client writing the source back out would write an "
        "invisible character into the middle of a line"
    )


def test_every_comment_of_the_source_is_answered_exactly_once():
    tree = ask_for_the_tree(TWO_DECLARATIONS)["result"]["tree"]

    written = [line for line in TWO_DECLARATIONS.split("\n") if line.startswith(";")]
    answered = [node["text"] for node in nodes_of(tree) if node["kind"] == "comment"]
    assert sorted(answered) == sorted(written), (
        f"the source writes {written} and the tree answers {answered}: a "
        "comment that is dropped, or answered twice, makes the tree disagree "
        "with the text it was read from; answer each comment once"
    )
    assert [node["position"]["line"] for node in nodes_of(tree) if node["kind"] == "comment"] == [
        1,
        4,
    ], "each comment stands on the line it was written on"
