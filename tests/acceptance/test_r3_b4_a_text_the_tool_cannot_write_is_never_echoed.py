"""R3.B4 -- a text the tool cannot write as UTF-8 is named, never
copied back into the answer.

A client that decoded bytes badly sends half a character. The tool used
to copy the operation it was given straight into its answer, so the
client read back a text it could not write out again -- and a variable
of the environment went the same way. Now every text that reaches an
answer is one a client can write.

still passes if: the tool refused every operation it does not know. The
third test sends an ordinary unknown operation and requires the old
answer, naming the operation it was given.
"""

from __future__ import annotations

from _r3_fixtures import (
    BUDGET_VARIABLE,
    INVALID_INPUT,
    MALFORMED_REQUEST,
    answered,
    assert_every_text_can_be_written,
    diagnostic_of,
    send,
    send_text,
)

# Half a character: a high surrogate standing alone, as a client that
# decoded bytes badly sends it.
HALF_A_CHARACTER = "\ud800"


def test_an_operation_that_cannot_be_written_is_refused_by_field_and_position():
    """Given a request whose operation field opens with half a
    character, when it is sent, then the answer refuses the operation
    field, says the character at position 0 cannot be written, and
    carries no text a client cannot write out again.
    """
    run = send_text(
        '{"operation": "' + "\\ud800" + 'check", "source": "x"}'
    )
    response = run.assert_answered("an operation holding half a character")

    assert response["status"] == INVALID_INPUT, (
        f"the answer carries status {response.get('status')!r}: "
        f"{str(response)[:400]}. A field the tool cannot read is the caller's "
        "to repair."
    )
    refusal = diagnostic_of(
        response, MALFORMED_REQUEST, "an operation holding half a character"
    )
    assert refusal.get("symbol") == "operation", (
        f"the refusal is about {refusal.get('symbol')!r}: {refusal}. A client "
        "repairs the field the refusal names."
    )
    assert "position 0" in refusal.get("reason", ""), (
        f"the refusal says {refusal.get('reason', '')[:300]!r}, which does not "
        "say which character of the operation cannot be written."
    )
    assert_every_text_can_be_written(
        response, "an operation holding half a character"
    )


def test_a_budget_variable_that_cannot_be_written_is_refused_without_echoing_it():
    """Given a caller whose environment holds a budget variable whose
    name ends in half a character, when it asks for the manifest, then
    the command exits 0, says which character position cannot be
    written, and the answer carries no copy of that name.
    """
    mangled = BUDGET_VARIABLE + "\udcff"
    run = send({"operation": "discover"}, {mangled: "4096"})
    response = run.assert_answered("a budget variable named with half a character")

    assert response["status"] == INVALID_INPUT, (
        f"the answer carries status {response.get('status')!r}: "
        f"{str(response)[:400]}. A caller that believes it lowered a budget "
        "and did not is owed a refusal."
    )
    refusal = diagnostic_of(
        response, MALFORMED_REQUEST, "a budget variable named with half a character"
    )
    assert refusal.get("symbol") == "PROVA_BUDGET_", (
        f"the refusal is about {refusal.get('symbol')!r}: {refusal}. The name "
        "itself cannot be written back, so the refusal names the family of "
        "variables the caller must look through."
    )
    assert f"position {len(BUDGET_VARIABLE)}" in refusal.get("reason", ""), (
        f"the refusal says {refusal.get('reason', '')[:300]!r}, which does not "
        f"say that the character at position {len(BUDGET_VARIABLE)} is the one "
        "that cannot be written."
    )
    assert_every_text_can_be_written(
        response, "a budget variable named with half a character"
    )


def test_an_operation_this_tool_does_not_know_is_still_named_back():
    """Given a request asking for an operation this tool does not have,
    written in characters anyone can write, when it is sent, then the
    answer is the one callers already get: unavailable, naming the
    operation that was asked for.
    """
    response = answered(
        {"operation": "not-an-operation", "source": "x"},
        "an operation this tool does not have",
    )

    assert response["status"] == "unavailable", str(response)[:300]
    assert response["operation"] == "not-an-operation", (
        f"the answer names the operation as {response.get('operation')!r}: a "
        "caller that sent a name it can write reads its own name back, as "
        "before."
    )
    diagnostic_of(response, "unknown_operation", "an operation this tool does not have")
