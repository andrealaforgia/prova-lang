"""Property tests for F2's design law (LAW1): a program is refused
exactly when the dependency graph of its function bodies and contract
clauses has a cycle, and the refusal names exactly the functions that lie
on one. Declared examples name their own function in every generated
program, so the exclusion of example calls from that graph is exercised
by every case, accepted and refused alike.

The hand-written acceptance tests fix four shapes (self-call, mutual
call, contract-only cycle, no cycle). The law is about every shape: a
cycle of length three, a cycle reached only through a contract edge from
a function that is not itself on it, a function that calls a cyclic pair
without joining the cycle. A table of examples cannot carry that.

Whether a generated program is cyclic is decided here by a transitive
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

from _i1_s3_fixtures import diagnostic_categories
from _prova_client import run_prova

CYCLE_CATEGORY = "cyclic_dependency"
MAX_FUNCTIONS = 3


def _name(index: int) -> str:
    return f"task{index}"


def _square_matrix(size: int):
    return st.lists(
        st.lists(st.booleans(), min_size=size, max_size=size),
        min_size=size,
        max_size=size,
    )


_graphs = st.integers(min_value=1, max_value=MAX_FUNCTIONS).flatmap(
    lambda size: st.tuples(
        st.just(size), _square_matrix(size), _square_matrix(size)
    )
)


def _source(size: int, body_edges, contract_edges) -> str:
    """One `core-0` program with a function per node: every body edge is a
    call in a body, every contract edge is a call in an `ensures` clause,
    and every function declares an example naming itself."""
    declarations = []
    for caller in range(size):
        body = "n"
        for callee in reversed([c for c in range(size) if body_edges[caller][c]]):
            body = f"(+ ({_name(callee)} n) {body})"
        contract_callees = [c for c in range(size) if contract_edges[caller][c]]
        ensures = ""
        if contract_callees:
            clauses = " ".join(
                f"(= result ({_name(callee)} n))" for callee in contract_callees
            )
            ensures = f"\n  (ensures {clauses})"
        declarations.append(
            f"(defn {_name(caller)}\n"
            f"  (sig ((n Int)) -> Int ! pure){ensures}\n"
            f"  (examples (example ({_name(caller)} 1) => 1))\n"
            f"  {body})"
        )
    return "\n\n".join(declarations) + "\n"


def _functions_on_a_cycle(size: int, body_edges, contract_edges) -> set[str]:
    """The names of the functions that can reach themselves, by transitive
    closure over the union of the two edge sets."""
    reaches = {
        (caller, callee)
        for caller in range(size)
        for callee in range(size)
        if body_edges[caller][callee] or contract_edges[caller][callee]
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


def _reported_cycles(response: dict) -> list[frozenset[str]]:
    return [
        frozenset(diagnostic.get("cycle") or ())
        for diagnostic in response.get("diagnostics") or []
        if diagnostic.get("category") == CYCLE_CATEGORY
    ]


@settings(derandomize=True, max_examples=60, deadline=None)
@given(graph=_graphs)
def test_a_program_is_refused_exactly_when_its_calls_form_a_cycle(graph):
    """LAW1: for every call graph over bodies and contracts, the program
    is refused if and only if some function can reach itself; the
    functions the refusal names are exactly those functions; and an
    example naming its own function never makes a program cyclic."""
    size, body_edges, contract_edges = graph
    source = _source(size, body_edges, contract_edges)
    on_a_cycle = _functions_on_a_cycle(size, body_edges, contract_edges)

    response = _check(source)

    if not on_a_cycle:
        assert response.get("status") == "completed", (
            f"a program whose calls are acyclic was refused: {response}. Source:\n"
            f"{source}\nOnly a function that can reach itself may be refused as a "
            "cycle; every other program stays accepted."
        )
        assert not response.get("diagnostics"), (
            f"an acyclic program carried diagnostics: {response}. Source:\n{source}"
        )
        return

    assert response.get("status") == "invalid_program", (
        f"a program in which {sorted(on_a_cycle)} can reach themselves was "
        f"accepted: {response}. Source:\n{source}\nRefuse every program whose "
        "dependency graph has a cycle."
    )
    assert diagnostic_categories(response) == {CYCLE_CATEGORY}, (
        f"a cyclic program was refused for some other reason as well: {response}. "
        f"Source:\n{source}\nThese programs are well typed; the cycle is the only "
        "fault to report."
    )
    named = set().union(*_reported_cycles(response)) if _reported_cycles(response) else set()
    assert named == on_a_cycle, (
        f"the refusal names {sorted(named)} but the functions that can reach "
        f"themselves are {sorted(on_a_cycle)}: {response}. Source:\n{source}\n"
        "Name every function on a cycle, and no function that is not on one."
    )


@settings(derandomize=True, max_examples=8, deadline=None)
@given(graph=_graphs)
def test_checking_the_same_program_in_two_runs_gives_the_same_answer(graph):
    """LAW2: the answer depends on the program alone, so two separate runs
    of the command answer identically -- no set iteration order leaks into
    which cycle is reported first or how its members are written.

    The two runs are two processes on purpose: within one process a set of
    strings iterates in a stable order, so a second in-process call would
    agree with the first even when that order came from a set. Two
    processes get two hash seeds.
    """
    size, body_edges, contract_edges = graph
    source = _source(size, body_edges, contract_edges)
    request = {"prova": "i1", "operation": "check", "source": source}

    _, first, _, _ = run_prova(request)
    _, second, _, _ = run_prova(request)

    assert first == second, (
        f"checking the same program in two runs gave different answers:\n{first}\n"
        f"{second}\nSource:\n{source}\nOrder the report from the declaration order "
        "of the program, never from the iteration order of a set."
    )
