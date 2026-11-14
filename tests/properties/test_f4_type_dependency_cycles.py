"""Property test for F4's design law (LAW1): a program is refused with a
recursive-data diagnostic exactly when the declared types of its fields
let some type lead back to itself, and the refusal names exactly the
types that do.

The hand-written acceptance tests fix four shapes (a record holding
itself, a mutual pair, a recursive union variant, an acyclic chain of
three). The law is about every shape: a cycle of length three, a type
that holds a cyclic pair without joining the cycle, a union payload that
closes a cycle a record opened, and the many programs with no cycle at
all. A table of examples cannot carry that.

Whether a generated program is recursive is decided here by a transitive
closure over the generated edge list -- a different algorithm from any
graph search the tool performs, computed from the generator's own data
before the source text is built.

Derandomized with a bounded example count so the verdict does not depend
on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from prova import service

RECURSIVE_CATEGORY = "recursive_type"
MAX_TYPES = 3


def _name(index: int) -> str:
    return f"Type{index}"


def _square_matrix(size: int):
    return st.lists(
        st.lists(st.booleans(), min_size=size, max_size=size),
        min_size=size,
        max_size=size,
    )


_programs = st.integers(min_value=1, max_value=MAX_TYPES).flatmap(
    lambda size: st.tuples(
        st.just(size),
        _square_matrix(size),
        st.lists(st.booleans(), min_size=size, max_size=size),
    )
)


def _source(size: int, edges, as_union) -> str:
    """One `core-0` program with a type per node: every edge is a field
    whose declared type is the type it points at, written as a record
    field or as the payload of a one-variant union."""
    declarations = []
    for holder in range(size):
        fields = " ".join(
            f"(field{held} {_name(held)})" for held in range(size) if edges[holder][held]
        )
        body = f"(count Int) {fields}".strip()
        if as_union[holder]:
            declarations.append(f"(deftype {_name(holder)} (union (Mk{_name(holder)} {body})))")
        else:
            declarations.append(f"(deftype {_name(holder)} (record {body}))")
    return "\n\n".join(declarations) + "\n"


def _types_that_lead_back_to_themselves(size: int, edges) -> set[str]:
    """The names of the types that can reach themselves, by transitive
    closure over the generated edge set."""
    reaches = {
        (holder, held)
        for holder in range(size)
        for held in range(size)
        if edges[holder][held]
    }
    growing = True
    while growing:
        growing = False
        for first, middle in sorted(reaches):
            for other, last in sorted(reaches):
                if other == middle and (first, last) not in reaches:
                    reaches.add((first, last))
                    growing = True
    return {_name(node) for node in range(size) if (node, node) in reaches}


def _check(source: str) -> dict:
    return service.handle({"prova": "i1", "operation": "check", "source": source})


def _reported_members(response: dict) -> set[str]:
    members: set[str] = set()
    for diagnostic in response.get("diagnostics") or []:
        if diagnostic.get("category") == RECURSIVE_CATEGORY:
            members |= set(diagnostic.get("cycle") or ())
    return members


@settings(derandomize=True, max_examples=60, deadline=None)
@given(program=_programs)
def test_a_program_is_refused_exactly_when_a_type_leads_back_to_itself(program):
    """LAW1: for every type-dependency graph over records and union
    payloads, the program is refused if and only if some type can reach
    itself, and the types the refusal names are exactly those types."""
    size, edges, as_union = program
    source = _source(size, edges, as_union)
    recursive = _types_that_lead_back_to_themselves(size, edges)

    response = _check(source)

    if not recursive:
        assert response.get("status") == "completed", (
            f"a program whose types are acyclic was refused: {response}. Source:\n"
            f"{source}\nOnly a type that can lead back to itself may be refused; "
            "every other program stays accepted."
        )
        assert not response.get("diagnostics"), (
            f"an acyclic program carried diagnostics: {response}. Source:\n{source}"
        )
        return

    assert response.get("status") == "invalid_program", (
        f"a program in which {sorted(recursive)} lead back to themselves was "
        f"accepted: {response}. Source:\n{source}\nRefuse every program whose "
        "type-dependency graph has a cycle."
    )
    assert set(d.get("category") for d in response["diagnostics"]) == {
        RECURSIVE_CATEGORY
    }, (
        f"a recursive program was refused for some other reason as well: "
        f"{response}. Source:\n{source}\nThese declarations are otherwise "
        "well formed; the recursion is the only fault to report."
    )
    assert _reported_members(response) == recursive, (
        f"the refusal names {sorted(_reported_members(response))} but the types "
        f"that lead back to themselves are {sorted(recursive)}: {response}. "
        f"Source:\n{source}\nName every type on a cycle, and no type that is not "
        "on one."
    )
