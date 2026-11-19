"""A field selector written on a union-typed operand is refused.

SPEC.md line 142: "Field selection is defined only for records and
resolves from the operand's nominal type." A union has no fields of its
own: each of its variants does, and which variant a value carries is not
known where the selector stands. Reading a union's variant field through
a selector used to be accepted, so `check` completed, `verify` said the
contract that reads it is defined for every value of the type, and
running the function on the other variant ended in a failure of the tool
itself.

Every case drives the real command over its stdin and stdout, because
the answer a caller reads -- including a traceback that reaches no
answer at all -- is what these tests are about. Each refusal is paired
with the same selection on a record, which must still be accepted: a
tool that refused every selector would not pass.
"""

from __future__ import annotations

from _r1_robustness_fixtures import answered, run

UNION_SELECTION = (
    "(deftype E (union (A (x Int)) (B)))\n"
    "(defn f (sig ((e E)) -> Int ! pure)\n"
    "  (requires (= (.x e) 0))\n"
    "  (examples (example (f (A 0)) => 0)) 0)\n"
)

RECORD_SELECTION = (
    "(deftype R (record (x Int)))\n"
    "(defn f (sig ((r R)) -> Int ! pure)\n"
    "  (requires (= (.x r) 0))\n"
    "  (examples (example (f (R 0)) => 0)) 0)\n"
)


def _selector_refusal(response: dict) -> dict:
    refusals = [d for d in response["diagnostics"] if d["category"] == "unbound_field"]
    assert len(refusals) == 1, response
    return refusals[0]


def test_check_refuses_a_selector_written_on_a_union():
    response = answered(
        {"prova": "i1", "operation": "check", "source": UNION_SELECTION},
        "a selector on a union-typed operand",
    )

    assert response["status"] == "invalid_program", response
    refusal = _selector_refusal(response)
    assert refusal["symbol"] == "E.x", refusal
    assert refusal["location"] == {"line": 3, "column": 16}, refusal
    assert "union" in refusal["reason"], refusal


def test_check_accepts_the_same_selection_on_a_record():
    response = answered(
        {"prova": "i1", "operation": "check", "source": RECORD_SELECTION},
        "a selector on a record-typed operand",
    )

    assert response["status"] == "completed", response
    assert response["diagnostics"] == [], response


def test_verify_proves_nothing_about_a_selector_written_on_a_union():
    response = answered(
        {"prova": "i1", "operation": "verify", "source": UNION_SELECTION},
        "verifying a program whose contract selects on a union",
    )

    assert response["status"] == "invalid_program", response
    _selector_refusal(response)
    assert "findings" not in response, response
    assert "aggregate" not in response, response


def test_verify_still_settles_the_same_contract_on_a_record():
    response = answered(
        {"prova": "i1", "operation": "verify", "source": RECORD_SELECTION},
        "verifying a program whose contract selects on a record",
    )

    assert response["status"] == "completed", response
    assert response["aggregate"]["result"] == "verified", response


def test_evaluating_the_other_variant_is_refused_not_a_failure_of_the_tool():
    outcome = run(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": UNION_SELECTION,
            "function": "f",
            "arguments": ["(B)"],
        }
    )
    response = outcome.assert_answered("evaluating the variant without the field")

    assert response["status"] == "invalid_program", response
    categories = [d["category"] for d in response["diagnostics"]]
    assert "tool_failure" not in categories, response
    _selector_refusal(response)


def test_evaluating_the_record_program_still_answers():
    response = answered(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": RECORD_SELECTION,
            "function": "f",
            "arguments": ["(R 0)"],
        },
        "evaluating the record program",
    )

    assert response["status"] == "completed", response
    assert response["result"]["value"] == "0", response
