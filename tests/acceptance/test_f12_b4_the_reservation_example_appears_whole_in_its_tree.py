"""F12.B4 -- the tree of the reservation example holds every declaration,
every contract clause and every example the source writes.

The law: the tree is the whole program, not a summary of it, so an agent
that reads it needs the source for nothing.

still passes if: the tree held the right number of declarations but lost
the values an example is written with. Each example is rebuilt from the
tree and looked for in the source text, so a dropped or altered value
fails.
"""

from __future__ import annotations

from _f12_tree_fixtures import ask_for_the_tree
from _reservation_fixtures import reservation_source

SOURCE = reservation_source()

# What the reservation example of SPEC.md declares, read from that
# source: three types, three functions, and for each function the
# preconditions, postconditions and examples it writes.
DECLARED_TYPES = ["Reservation", "Event", "Outcome"]
DECLARED_FUNCTIONS = ["valid-state", "initial", "step"]
CONTRACT_CLAUSES = {
    "valid-state": (0, 0),
    "initial": (0, 1),
    "step": (1, 3),
}
EXAMPLES_PER_FUNCTION = {"valid-state": 2, "initial": 1, "step": 4}


def _tree() -> dict:
    answer = ask_for_the_tree(SOURCE)
    assert answer["status"] == "completed", (
        f"the reservation example was answered {answer['status']!r}: {answer}. "
        "The shipped example breaks no rule and must be answered with its tree"
    )
    return answer["result"]["tree"]


def _functions(tree: dict) -> dict:
    return {
        node["name"]: node
        for node in tree["declarations"]
        if node["kind"] == "function"
    }


def test_every_type_and_function_the_source_declares_stands_in_the_tree():
    tree = _tree()

    types = [n["name"] for n in tree["declarations"] if n["kind"].endswith("_type")]
    functions = [n["name"] for n in tree["declarations"] if n["kind"] == "function"]
    assert types == DECLARED_TYPES, (
        f"the tree declares the types {types}, and the source declares "
        f"{DECLARED_TYPES}: every declaration of the source stands in the "
        "tree, in source order"
    )
    assert functions == DECLARED_FUNCTIONS, (
        f"the tree declares the functions {functions}, and the source declares "
        f"{DECLARED_FUNCTIONS}: every declaration of the source stands in the "
        "tree, in source order"
    )
    assert len(tree["declarations"]) == len(DECLARED_TYPES) + len(DECLARED_FUNCTIONS), (
        f"the tree holds {len(tree['declarations'])} declarations and the "
        f"source writes {len(DECLARED_TYPES) + len(DECLARED_FUNCTIONS)}: "
        f"{[n['name'] for n in tree['declarations']]}"
    )


def test_every_contract_clause_the_source_writes_stands_in_the_tree():
    functions = _functions(_tree())

    counted = {
        name: (len(node["requires"]), len(node["ensures"]))
        for name, node in functions.items()
    }
    assert counted == CONTRACT_CLAUSES, (
        f"the tree holds the contract clauses {counted} and the source writes "
        f"{CONTRACT_CLAUSES}: a promise a function makes is part of its "
        "declaration; answer every clause it writes"
    )


def test_every_example_the_source_writes_stands_in_the_tree_with_its_values():
    functions = _functions(_tree())

    counted = {name: len(node["examples"]) for name, node in functions.items()}
    assert counted == EXAMPLES_PER_FUNCTION, (
        f"the tree holds the examples {counted} and the source writes "
        f"{EXAMPLES_PER_FUNCTION}: an example is part of the declaration it "
        "stands in; answer every one of them"
    )
    for name, node in functions.items():
        for example in node["examples"]:
            call = " ".join([example["function"], *example["arguments"]]).strip()
            written = f"(example ({call}) => {example['expected']})"
            assert written in SOURCE, (
                f"the tree writes the example {written} for {name!r}, and the "
                "source does not hold it: the values an example is written "
                "with are part of it; answer them as the source writes them"
            )
