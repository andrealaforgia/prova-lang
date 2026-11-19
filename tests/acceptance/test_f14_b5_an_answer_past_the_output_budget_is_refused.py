"""F14.B5 -- an answer larger than the answer budget is replaced by a
refusal that says so, never cut short.

A caller reads one complete JSON answer per request. Half an answer is
not one: it cannot be parsed, and a caller that managed to parse a
prefix would read a result the tool never finished writing.

still passes if: the tool refused every answer. The third test asks for
the same answer with nothing lowered and requires the whole manifest.
"""

from __future__ import annotations

import json

from _f14_budget_fixtures import (
    ANSWER_SIZE,
    CATEGORY_OF,
    RESOURCE_EXHAUSTED,
    assert_claims_nothing,
    assert_names_the_budget,
    discover,
    run,
    the_refusal,
)

MANIFEST_REQUEST = {"prova": "i1", "operation": "discover"}


def _full_answer_size() -> int:
    """How many bytes the whole manifest answer is, measured from the
    command's own output."""
    printed = run(MANIFEST_REQUEST).assert_answered("the whole manifest")
    return len(json.dumps(printed).encode("utf-8"))


def test_an_answer_one_byte_too_large_is_replaced_by_the_budget_refusal():
    """Given a caller whose answer budget is one byte under the size of
    the manifest, when it asks for the manifest, then it gets the answer
    budget refusal naming the size allowed beside the size withheld, and
    none of the manifest.
    """
    size = _full_answer_size()
    allowed = size - 1

    answer = run(MANIFEST_REQUEST, {ANSWER_SIZE: allowed})
    response = answer.assert_answered("an answer one byte past the budget")

    why = f"an answer of {size} bytes against a budget of {allowed}"
    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: "
        f"{str(response)[:400]}. An answer the caller cannot be given is a "
        "budget of this tool, answered as one."
    )
    refusal = the_refusal(response, CATEGORY_OF[ANSWER_SIZE], why)
    assert_names_the_budget(refusal, ANSWER_SIZE, allowed, size, why)
    assert_claims_nothing(response, why)
    assert "profile" not in answer.stdout, (
        f"the answer for {why} still carries part of the manifest: "
        f"{answer.stdout[:400]!r}. An answer that did not fit is withheld "
        "whole; a caller never reads the start of one."
    )


def test_a_refusal_is_delivered_even_when_it_is_larger_than_the_budget():
    """Given an answer budget of 20 bytes, smaller than any refusal this
    tool can write, when a caller asks for the manifest, then it still
    gets one complete JSON refusal naming the answer budget: the budget
    sizes the answer an operation produced, and the refusal that
    replaces it is this tool's smallest answer.
    """
    answer = run(MANIFEST_REQUEST, {ANSWER_SIZE: 20})
    response = answer.assert_answered("an answer budget of 20 bytes")

    refusal = the_refusal(
        response, CATEGORY_OF[ANSWER_SIZE], "an answer budget of 20 bytes"
    )
    assert refusal.get("expected") == 20, (
        f"the refusal reports {refusal.get('expected')!r} allowed against the "
        f"20 bytes the caller set: {refusal}. The number the caller set is the "
        "number it reads back."
    )


def test_an_answer_that_fits_is_given_whole():
    """Given nothing lowered, when a caller asks for the manifest, then
    it reads the whole manifest, with its 9 operations and its profile.
    """
    manifest = discover()

    assert manifest["status"] == "completed", (
        f"the manifest was answered {manifest.get('status')!r} with nothing "
        f"lowered: {str(manifest)[:400]}. It is far inside the declared 1 MiB "
        "answer budget, so a refusal here means the budget is counted wrongly."
    )
    assert len(manifest["result"]["operations"]) == 9, (
        f"the manifest lists {len(manifest['result']['operations'])} "
        "operations, expected the 9 this tool names: "
        f"{manifest['result']['operations']}. The answer budget work must "
        "leave the manifest exactly as it was."
    )
