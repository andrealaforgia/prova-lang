"""R1.P3 -- law: a record written in an example carries exactly one
value per field its type declares, or the program is refused.

This is where the hour clock's crash came from. A record written with
too few values was accepted, and the tool then reached for a field that
was never there while running the example. The counts are compared here
against a model the test builds itself: the number of fields it asked
for when it wrote the type, and the number of values it wrote in the
example.

still passes if: the tool refused every program. The matching case in
each draw requires the program with the right number of values to be
accepted and its example to run.
"""

from __future__ import annotations

import json

from hypothesis import HealthCheck, given, settings, strategies as st

from _r1_mangled_requests import ask

DERANDOMIZED = settings(
    derandomize=True,
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

ARITY_MISMATCH = "arity_mismatch"
FIELD_NAMES = ("a", "b", "c", "d", "e")


def _program(declared: int, written: int) -> str:
    """A record type with `declared` whole-number fields, and a function
    whose example writes that record with `written` values."""
    fields = " ".join(f"({FIELD_NAMES[i]} Int)" for i in range(declared))
    values = " ".join(str(i + 1) for i in range(written))
    record = f"(Box {values})" if values else "(Box)"
    return (
        f"(deftype Box (record {fields}))\n"
        "\n"
        "(defn boxed\n"
        "  (sig ((b Box)) -> Int ! pure)\n"
        f"  (examples (example (boxed {record}) => 0))\n"
        "  0)\n"
    )


def _answer(source: str) -> dict:
    answer = ask({"operation": "examples", "source": source})
    assert answer.crash is None, (
        f"a program whose example writes a record came back as "
        f"{type(answer.crash).__name__}: {answer.crash}. Source:\n{source}"
    )
    assert answer.exit_code == 0, (
        f"the tool exited {answer.exit_code} for:\n{source}"
    )
    return json.loads(answer.stdout)


@DERANDOMIZED
@given(
    declared=st.integers(min_value=1, max_value=5),
    written=st.integers(min_value=0, max_value=5),
)
def test_a_record_written_with_the_wrong_number_of_values_is_refused(
    declared, written
):
    """LAW3: an example that writes a record with a number of values
    other than the number of fields the type declares is refused, naming
    the record, the count declared and the count written; one that
    writes exactly as many is run.
    """
    answer = _answer(_program(declared, written))

    if declared == written:
        assert answer["status"] == "completed", (
            f"a record declaring {declared} field(s) written with {written} "
            f"value(s) was answered {answer['status']!r}: {answer}. The counts "
            "agree, so the program is correct and the example runs."
        )
        return

    assert answer["status"] == "invalid_program", (
        f"a record declaring {declared} field(s) written with {written} "
        f"value(s) was answered {answer['status']!r}: {answer}. The example "
        "cannot be run against a value that has no shape the type declares, so "
        "the program is refused before it is run."
    )
    refusals = [
        entry
        for entry in answer.get("diagnostics", [])
        if entry.get("category") == ARITY_MISMATCH
        and entry.get("symbol") == "Box"
    ]
    assert refusals, (
        f"a record declaring {declared} field(s) written with {written} "
        f"value(s) drew no count refusal naming 'Box': {answer}. A caller "
        "repairs the record the refusal names."
    )
    refusal = refusals[0]
    assert (refusal.get("expected"), refusal.get("actual")) == (declared, written), (
        f"the refusal reports {refusal.get('expected')!r} expected and "
        f"{refusal.get('actual')!r} written, while the program declares "
        f"{declared} and writes {written}: {refusal}. A caller counts the "
        "values to add or remove from these two numbers."
    )
    assert refusal.get("location", {}).get("line"), (
        f"the count refusal says where nowhere: {refusal}."
    )
