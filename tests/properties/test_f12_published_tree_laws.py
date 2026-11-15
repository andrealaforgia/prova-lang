"""Property tests for F12's laws about the tree a read program is answered
with.

LAW1 -- every node of a published tree stands at a place the source really
has: a line the source holds, and a column where a character that is not a
space stands.

LAW2 -- every comment of the source is answered exactly once, on the first
node that stands after it, or at the document end when no node does.

LAW3 -- a tree is published exactly when a check of the same source
completes, and a source that is refused is refused with the same status
and the same categories a check gives it.

The programs are built from a closed family of declaration shapes, one
copy of each shape numbered so that no two declarations share a name.
Exercises the service's public operation contract in process, as the other
property tests here do.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from prova import service

CASES = 40


def _record(i: int) -> str:
    return f"(deftype T{i} (record (a{i} Int) (b{i} Bool)))"


def _union(i: int) -> str:
    return f"(deftype U{i} (union (Ona{i} (x{i} Int)) (Offa{i})))"


def _addition(i: int) -> str:
    return (
        f"(defn f{i}\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        f"  (examples (example (f{i} 1) => 2))\n"
        "  (+ n 1))"
    )


def _with_contracts(i: int) -> str:
    return (
        f"(defn g{i}\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (requires (> n 0))\n"
        "  (ensures (> result 0))\n"
        f"  (examples (example (g{i} 1) => 1))\n"
        "  n)"
    )


def _with_branches(i: int) -> str:
    return (
        f"(defn h{i}\n"
        "  (sig ((n Int) (p Bool)) -> Int ! pure)\n"
        f"  (examples (example (h{i} 1 true) => 1))\n"
        "  (let ((m n)) (if p m 0)))"
    )


def _with_a_match(i: int) -> str:
    return (
        f"(deftype M{i} (union (Yesa{i}) (Noa{i})))\n"
        f"(defn k{i}\n"
        f"  (sig ((m M{i})) -> Int ! pure)\n"
        f"  (examples (example (k{i} (Yesa{i})) => 1))\n"
        f"  (match m ((Yesa{i}) 1) ((Noa{i}) 0)))"
    )


SHAPES = (_record, _union, _addition, _with_contracts, _with_branches, _with_a_match)

programs = st.lists(st.sampled_from(SHAPES), min_size=1, max_size=4).map(
    lambda shapes: "\n".join(shape(i) for i, shape in enumerate(shapes)) + "\n"
)


def _read(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "parse", "source": source})


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _nodes(tree: object) -> list[dict]:
    found: list[dict] = []
    if isinstance(tree, dict):
        if "kind" in tree:
            found.append(tree)
        for value in tree.values():
            found.extend(_nodes(value))
    elif isinstance(tree, list):
        for item in tree:
            found.extend(_nodes(item))
    return found


def _place(node: dict) -> tuple[int, int]:
    return node["position"]["line"], node["position"]["column"]


def _categories(response: dict) -> list[str]:
    return sorted(d["category"] for d in response["diagnostics"])


@settings(max_examples=CASES, deadline=None)
@given(programs)
def test_every_node_stands_where_the_source_holds_a_character(source):
    """LAW1 -- every node of a published tree stands at a place the source
    really has."""
    answer = _read(source)
    assert answer["status"] == "completed", answer

    lines = source.split("\n")
    for node in _nodes(answer["result"]["tree"]):
        line, column = _place(node)
        assert 1 <= line <= len(lines), (
            f"a {node['kind']!r} node stands on line {line} of a source with "
            f"{len(lines)} line(s): a place outside the text sends a reader "
            "nowhere; carry the place of the form the node was read from"
        )
        standing = lines[line - 1][column - 1 : column]
        assert standing not in ("", " "), (
            f"a {node['kind']!r} node stands at line {line} column {column}, "
            f"where the source holds {standing!r}: a node stands where its "
            "form starts, never past the end of a line and never on blank space"
        )


@settings(max_examples=CASES, deadline=None)
@given(programs, st.integers(min_value=0, max_value=6))
def test_every_comment_is_answered_once_on_the_first_node_after_it(source, where):
    """LAW2 -- every comment of the source is answered exactly once, on the
    first node that stands after it, or at the document end."""
    lines = source.rstrip("\n").split("\n")
    at = where % (len(lines) + 1)
    written = f"; comment number {at}"
    commented = "\n".join(lines[:at] + [written] + lines[at:]) + "\n"

    answer = _read(commented)
    assert answer["status"] == "completed", answer
    tree = answer["result"]["tree"]

    answered = [node for node in _nodes(tree) if node["kind"] == "comment"]
    assert [node["text"] for node in answered] == [written], (
        f"the source writes one comment and the tree answers "
        f"{[n['text'] for n in answered]}: a comment is answered once, with "
        "the characters it was written with"
    )
    comment_place = _place(answered[0])
    following = sorted(
        _place(node)
        for node in _nodes(tree)
        if node["kind"] != "comment" and _place(node) > comment_place
    )
    holders = [
        node
        for node in _nodes(tree)
        if any(c["text"] == written for c in node.get("comments", []))
    ]
    trailing = [c["text"] for c in tree.get("trailing_comments", [])]
    if following:
        assert len(holders) == 1 and _place(holders[0]) == following[0], (
            f"the comment at {comment_place} was answered on "
            f"{[(_place(h), h['kind']) for h in holders]}, and the first node "
            f"after it stands at {following[0]}: a comment belongs to the node "
            "that follows it"
        )
        assert trailing == [], (
            f"the comment was answered at the document end as well: {trailing}"
        )
    else:
        assert trailing == [written] and holders == [], (
            f"nothing follows the comment at {comment_place}, and it was "
            f"answered on {[h['kind'] for h in holders]} instead of at the "
            f"document end: {trailing}"
        )


@settings(max_examples=CASES, deadline=None)
@given(programs, st.integers(min_value=0, max_value=4096))
def test_a_tree_is_published_exactly_when_a_check_completes(source, cut):
    """LAW3 -- a tree is published exactly when a check of the same source
    completes, and a refusal carries the categories a check gives it."""
    mangled = source[: cut % (len(source) + 1)]
    for text in (source, mangled):
        read = _read(text)
        checked = _check(text)
        assert read["status"] == checked["status"], (
            f"reading answered {read['status']!r} and checking answered "
            f"{checked['status']!r} for the same source: one source gets one "
            f"answer whichever operation reads it.\n{text!r}"
        )
        assert _categories(read) == _categories(checked), (
            f"reading refused with {_categories(read)} and checking refused "
            f"with {_categories(checked)} for the same source: the two "
            f"operations share one vocabulary.\n{text!r}"
        )
        assert ("result" in read) == (read["status"] == "completed"), (
            f"a tree was published beside the status {read['status']!r}: a "
            f"tree is published exactly when the source was read through.\n{read}"
        )
