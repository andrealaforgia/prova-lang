"""Shared fixtures for I1.S4 property tests: mutation-based runtime detection
of a missing entry-boundary guard, a flipped acceptance flag and an
always-reject body, plus the unmodified source as a positive control.

Not a test module (no `test_` prefix); pytest will not collect it.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from _prova_client import SPEC_ORACLE_SHA, load_reservation_source_at, run_prova

EVENTS = ["Reserve", "Release"]
COUNTS = [0, 1, 2]

# The exact literal text of `step`'s body only (the final top-level form of
# `defn step`, plus the paren that closes the `defn` itself), transcribed by
# hand from SPEC.md at SPEC_ORACLE_SHA. Everything before this text --
# deftypes, `valid-state`, `initial`, and `step`'s signature, `requires`,
# `ensures` and `examples` -- is the protected material no mutation may
# touch.
STEP_BODY_OLD = (
    "  (match event\n"
    "    ((Reserve)\n"
    "      (if (< (.reserved current) 2)\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) true)\n"
    "          (Outcome current false)))\n"
    "    ((Release)\n"
    "      (if (> (.reserved current) 0)\n"
    "          (Outcome (Reservation (- (.reserved current) 1)) true)\n"
    "          (Outcome current false)))))\n"
)

# Missing-guard: the Reserve branch always takes the increment path,
# dropping the `(< (.reserved current) 2)` upper check. The Release branch
# is untouched.
MISSING_GUARD_BODY_NEW = (
    "  (match event\n"
    "    ((Reserve)\n"
    "      (if true\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) true)\n"
    "          (Outcome current false)))\n"
    "    ((Release)\n"
    "      (if (> (.reserved current) 0)\n"
    "          (Outcome (Reservation (- (.reserved current) 1)) true)\n"
    "          (Outcome current false)))))\n"
)

# Flipped-flag: every returned `accepted` literal is negated in both
# branches; the state calculation (which branch computes which count) is
# untouched.
FLIPPED_FLAG_BODY_NEW = (
    "  (match event\n"
    "    ((Reserve)\n"
    "      (if (< (.reserved current) 2)\n"
    "          (Outcome (Reservation (+ (.reserved current) 1)) false)\n"
    "          (Outcome current true)))\n"
    "    ((Release)\n"
    "      (if (> (.reserved current) 0)\n"
    "          (Outcome (Reservation (- (.reserved current) 1)) false)\n"
    "          (Outcome current true)))))\n"
)

# Always-reject: the body ignores `event` and `current` entirely and always
# returns the unchanged state with `accepted=false`.
ALWAYS_REJECT_BODY_NEW = "  (Outcome current false))\n"


@dataclass(frozen=True)
class Mutant:
    id: str
    behaviour_id: str
    new_body: str


MUTANTS = [
    Mutant("missing-guard", "I1.S4.B1", MISSING_GUARD_BODY_NEW),
    Mutant("flipped-flag", "I1.S4.B2", FLIPPED_FLAG_BODY_NEW),
    Mutant("always-reject", "I1.S4.B3", ALWAYS_REJECT_BODY_NEW),
]

assert len(MUTANTS) == 3
assert len({m.id for m in MUTANTS}) == 3


def protected_source() -> str:
    return load_reservation_source_at(SPEC_ORACLE_SHA)


def digest(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def protected_prefix() -> str:
    """Everything in the protected source before `step`'s body (declarations,
    the other two functions, and step's own signature/requires/ensures/
    examples)."""
    source = protected_source()
    return source[: source.rindex(STEP_BODY_OLD)]


def mutated_source(mutant: Mutant) -> str:
    source = protected_source()
    occurrences = source.count(STEP_BODY_OLD)
    if occurrences != 1:
        raise AssertionError(
            f"expected exactly one occurrence of step's protected body in the "
            f"protected source, found {occurrences}"
        )
    mutated = source.replace(STEP_BODY_OLD, mutant.new_body, 1)
    assert mutated != source
    prefix = protected_prefix()
    assert mutated[: len(prefix)] == prefix, "a mutation changed material before step's body"
    assert mutated[len(prefix) :] == mutant.new_body
    return mutated


def independent_expected_outcome(mutant_id: str | None, count: int, event: str) -> tuple[int, bool]:
    """Independently derive the (resulting count, accepted) pair the named
    mutant's stated semantics produce for a given (count, event) input.
    `mutant_id=None` means the unmodified protected source.

    This is a hand-derivation from each mutation's description, not a call
    into `mutated_source`/`STEP_BODY_OLD` or the tool under test.
    """
    if mutant_id is None:
        if event == "Reserve":
            return (count + 1, True) if count < 2 else (count, False)
        return (count - 1, True) if count > 0 else (count, False)

    if mutant_id == "missing-guard":
        if event == "Reserve":
            return (count + 1, True)
        return (count - 1, True) if count > 0 else (count, False)

    if mutant_id == "flipped-flag":
        if event == "Reserve":
            return (count + 1, False) if count < 2 else (count, True)
        return (count - 1, False) if count > 0 else (count, True)

    if mutant_id == "always-reject":
        return (count, False)

    raise ValueError(f"unknown mutant id: {mutant_id!r}")


def independent_postcondition_holds(count: int, event: str, result_count: int, accepted: bool) -> bool:
    """Independent re-evaluation of step's three `ensures` clauses against a
    concrete (input, result) pair, mirroring SPEC.md's contract without
    reusing any tool or fixture code."""
    valid_result_state = 0 <= result_count <= 2
    expected_accepted = (count < 2) if event == "Reserve" else (count > 0)
    accepted_matches = accepted == expected_accepted
    expected_count = count + (1 if event == "Reserve" else -1) if accepted else count
    count_matches = result_count == expected_count
    return valid_result_state and accepted_matches and count_matches


def evaluate_step(source: str, count: int, event: str) -> tuple[int, dict | None, str, str]:
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": "step",
        "arguments": [f"(Reservation {count})", f"({event})"],
    }
    return run_prova(request)


def assert_postcondition_violation(returncode, response, stdout, stderr):
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") != "completed", f"expected a rejection, got: {response}"
    assert not response.get("result"), f"rejection carried a successful result: {response}"
    categories = {d.get("category") for d in (response.get("diagnostics") or [])}
    assert "postcondition_violation" in categories, (
        f"expected postcondition_violation among {categories}: {response}"
    )


def assert_success(returncode, response, stdout, stderr, *, expected_count: int, expected_accepted: bool):
    assert returncode == 0, f"tool failure: stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") == "completed", f"expected success, got: {response}"
    result = response.get("result") or {}
    value_text = result.get("value")
    assert value_text, f"no successful result value: {response}"
    from _prova_client import parse_value

    ctor, args = parse_value(value_text)
    assert ctor == "Outcome" and len(args) == 2, f"unexpected result shape: {value_text!r}"
    state_value, accepted_value = args
    state_ctor, state_args = state_value
    assert state_ctor == "Reservation" and len(state_args) == 1
    assert state_args[0] == expected_count, f"expected count {expected_count}, got {state_args[0]}: {response}"
    assert accepted_value is expected_accepted, f"expected accepted={expected_accepted}: {response}"


FORBIDDEN_UNIVERSAL_WORDS = ("verified", "proved", "proven", "universal", " holds ", "guarantee")


def assert_no_universal_claim(response: dict) -> None:
    import json

    text = json.dumps(response).lower()
    for word in FORBIDDEN_UNIVERSAL_WORDS:
        assert word not in text, f"response claims more than a runtime check ({word!r}): {response}"
