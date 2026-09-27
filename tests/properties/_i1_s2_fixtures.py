"""Shared fixtures for I1.S2 property tests: the declared-example inventory
and the eleven-case single-expected-value mutation matrix.

Not a test module (no `test_` prefix); pytest will not collect it.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from _prova_client import SPEC_ORACLE_SHA, load_reservation_source_at, run_prova

# The `examples` operation's result shape this story's tests hold the
# implementation to: `result.examples` is a list with one entry per
# declared example, each carrying its owning function, a 0-based ordinal
# within that function, the arguments and expected value as submitted, the
# actual returned value, and a `passed` boolean. Ordinal plus function name
# is the identity this suite uses to attribute a result to its example;
# nothing about response field order or JSON key ordering is asserted.

# Independent inventory of the seven declared examples, transcribed by hand
# from SPEC.md's Core conformance example at SPEC_ORACLE_SHA. `ordinal` is
# 0-based within its own function, matching declaration order.
INVENTORY = [
    {
        "function": "valid-state",
        "ordinal": 0,
        "arguments": ["(Reservation 0)"],
        "expected": "true",
    },
    {
        "function": "valid-state",
        "ordinal": 1,
        "arguments": ["(Reservation 3)"],
        "expected": "false",
    },
    {
        "function": "initial",
        "ordinal": 0,
        "arguments": [],
        "expected": "(Reservation 0)",
    },
    {
        "function": "step",
        "ordinal": 0,
        "arguments": ["(Reservation 0)", "(Reserve)"],
        "expected": "(Outcome (Reservation 1) true)",
    },
    {
        "function": "step",
        "ordinal": 1,
        "arguments": ["(Reservation 2)", "(Reserve)"],
        "expected": "(Outcome (Reservation 2) false)",
    },
    {
        "function": "step",
        "ordinal": 2,
        "arguments": ["(Reservation 1)", "(Release)"],
        "expected": "(Outcome (Reservation 0) true)",
    },
    {
        "function": "step",
        "ordinal": 3,
        "arguments": ["(Reservation 0)", "(Release)"],
        "expected": "(Outcome (Reservation 0) false)",
    },
]

assert len(INVENTORY) == 7
assert {(e["function"], e["ordinal"]) for e in INVENTORY} == {
    ("valid-state", 0), ("valid-state", 1),
    ("initial", 0),
    ("step", 0), ("step", 1), ("step", 2), ("step", 3),
}


@dataclass(frozen=True)
class Mutation:
    id: str
    function: str
    ordinal: int
    kind: str  # "flag" (accepted/boolean) or "state" (reserved count)
    old: str
    new: str


# Each `old` substring is the right-hand side of one `(example ...)` form
# in the reservation source, independent of surrounding indentation. Every
# entry changes exactly one expected value; nothing else in the source
# text is touched.
MUTATIONS = [
    Mutation(
        "valid-state-ex0-flag", "valid-state", 0, "flag",
        "(valid-state (Reservation 0)) => true",
        "(valid-state (Reservation 0)) => false",
    ),
    Mutation(
        "valid-state-ex1-flag", "valid-state", 1, "flag",
        "(valid-state (Reservation 3)) => false",
        "(valid-state (Reservation 3)) => true",
    ),
    Mutation(
        "initial-ex0-state", "initial", 0, "state",
        "(initial) => (Reservation 0)",
        "(initial) => (Reservation 1)",
    ),
    Mutation(
        "step-ex0-flag", "step", 0, "flag",
        "(step (Reservation 0) (Reserve)) => (Outcome (Reservation 1) true)",
        "(step (Reservation 0) (Reserve)) => (Outcome (Reservation 1) false)",
    ),
    Mutation(
        "step-ex0-state", "step", 0, "state",
        "(step (Reservation 0) (Reserve)) => (Outcome (Reservation 1) true)",
        "(step (Reservation 0) (Reserve)) => (Outcome (Reservation 2) true)",
    ),
    Mutation(
        "step-ex1-flag", "step", 1, "flag",
        "(step (Reservation 2) (Reserve)) => (Outcome (Reservation 2) false)",
        "(step (Reservation 2) (Reserve)) => (Outcome (Reservation 2) true)",
    ),
    Mutation(
        "step-ex1-state", "step", 1, "state",
        "(step (Reservation 2) (Reserve)) => (Outcome (Reservation 2) false)",
        "(step (Reservation 2) (Reserve)) => (Outcome (Reservation 3) false)",
    ),
    Mutation(
        "step-ex2-flag", "step", 2, "flag",
        "(step (Reservation 1) (Release)) => (Outcome (Reservation 0) true)",
        "(step (Reservation 1) (Release)) => (Outcome (Reservation 0) false)",
    ),
    Mutation(
        "step-ex2-state", "step", 2, "state",
        "(step (Reservation 1) (Release)) => (Outcome (Reservation 0) true)",
        "(step (Reservation 1) (Release)) => (Outcome (Reservation 1) true)",
    ),
    Mutation(
        "step-ex3-flag", "step", 3, "flag",
        "(step (Reservation 0) (Release)) => (Outcome (Reservation 0) false)",
        "(step (Reservation 0) (Release)) => (Outcome (Reservation 0) true)",
    ),
    Mutation(
        "step-ex3-state", "step", 3, "state",
        "(step (Reservation 0) (Release)) => (Outcome (Reservation 0) false)",
        "(step (Reservation 0) (Release)) => (Outcome (Reservation 1) false)",
    ),
]

assert len(MUTATIONS) == 11
assert len({m.id for m in MUTATIONS}) == 11
assert {(m.function, m.ordinal) for m in MUTATIONS} == {
    (e["function"], e["ordinal"]) for e in INVENTORY
} | {("step", 0), ("step", 1), ("step", 2), ("step", 3)}
assert sum(1 for m in MUTATIONS if m.function == "step") == 8
assert sum(1 for m in MUTATIONS if m.function == "valid-state") == 2
assert sum(1 for m in MUTATIONS if m.function == "initial") == 1


def protected_source() -> str:
    return load_reservation_source_at(SPEC_ORACLE_SHA)


def digest(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def mutated_source(mutation: Mutation) -> str:
    source = protected_source()
    occurrences = source.count(mutation.old)
    if occurrences != 1:
        raise AssertionError(
            f"mutation {mutation.id!r}: expected exactly one occurrence of "
            f"{mutation.old!r} in the protected source, found {occurrences}"
        )
    mutated = source.replace(mutation.old, mutation.new, 1)
    assert mutated != source
    assert mutated.count(mutation.new) == 1
    return mutated


def run_examples(source: str) -> tuple[int, dict | None, str, str]:
    request = {"prova": "i1", "operation": "examples", "source": source}
    return run_prova(request)


def extract_results(response: dict) -> list[dict]:
    assert response.get("operation") == "examples", response
    assert response.get("status") == "completed", response
    results = ((response.get("result") or {}).get("examples")) or []
    assert results, f"examples response carried no per-example results: {response}"
    for entry in results:
        for key in ("function", "ordinal", "arguments", "expected", "actual", "passed"):
            assert key in entry, f"example result missing {key!r}: {entry}"
    return results


def index_by_identity(results: list[dict]) -> dict[tuple[str, int], dict]:
    indexed: dict[tuple[str, int], dict] = {}
    for entry in results:
        identity = (entry["function"], entry["ordinal"])
        assert identity not in indexed, f"duplicate example identity {identity}: {results}"
        indexed[identity] = entry
    return indexed


def expected_outcome_for(mutation_id: str | None) -> dict[tuple[str, int], bool]:
    """Map (function, ordinal) -> expected `passed` flag for a run.

    `mutation_id=None` means the unmodified protected source: every
    declared example must pass. Otherwise every example passes except the
    one the named mutation targets.
    """
    outcome = {(e["function"], e["ordinal"]): True for e in INVENTORY}
    if mutation_id is not None:
        targeted = next(m for m in MUTATIONS if m.id == mutation_id)
        outcome[(targeted.function, targeted.ordinal)] = False
    return outcome
