"""R3.B2 -- a budget written in the environment as a run of digits no
reader turns into a number is refused by name, not left to break the
command before it reads its request.

A caller lowers a budget by writing a number in a variable. A number of
5000 digits is still only text, and the command that cannot read it owes
the caller the name of the variable to repair -- the same answer the
caller already gets for a variable holding a word.

still passes if: the command refused every budget a caller writes. The
second test lowers a budget the published way and requires the run to be
measured against the lowered number.
"""

from __future__ import annotations

from _r3_fixtures import (
    BUDGET_TIME_VARIABLE,
    BUDGET_VARIABLE,
    DECLARED_OPERATION_TIME,
    DECLARED_INPUT_SIZE,
    INVALID_INPUT,
    MALFORMED_REQUEST,
    RESOURCE_EXHAUSTED,
    answered,
    diagnostic_of,
    send,
)

A_RUN_OF_5000_DIGITS = "9" * 5000


def test_a_budget_written_as_5000_digits_is_refused_by_name():
    """Given a caller that wrote 5000 digits in the variable that lowers
    how large a source this tool reads, when it asks for the manifest,
    then the command exits 0 with one refusal naming that variable, and
    nothing on standard error.
    """
    run = send({"operation": "discover"}, {BUDGET_VARIABLE: A_RUN_OF_5000_DIGITS})
    response = run.assert_answered("a budget written as 5000 digits")

    assert response["status"] == INVALID_INPUT, (
        f"the answer carries status {response.get('status')!r}: "
        f"{str(response)[:400]}. A variable this tool cannot read is a request "
        "the caller must repair."
    )
    refusal = diagnostic_of(
        response, MALFORMED_REQUEST, "a budget written as 5000 digits"
    )
    assert refusal.get("symbol") == BUDGET_VARIABLE, (
        f"the refusal is about {refusal.get('symbol')!r}: {refusal}. A caller "
        "with several budgets set must be told which variable to repair."
    )
    assert "5000" in refusal.get("reason", ""), (
        f"the refusal says {refusal.get('reason', '')[:300]!r}, which does not "
        "say how long the text it could not read is. A caller that wrote a "
        "number it believed small learns here how many digits arrived."
    )
    assert "result" not in response and "claim" not in response, (
        f"the answer carries a result or a claim: {str(response)[:400]}. The "
        "run stopped before it read its request, so it answers nothing about "
        "any program."
    )


def test_a_budget_a_caller_may_write_still_lowers_the_run():
    """Given a caller that lowers how large a source this tool reads to
    4096 bytes, the published way, when it sends a source of 5000 bytes,
    then the run is refused against the lowered budget as before.
    """
    response = answered(
        {"operation": "check", "source": "x" * 5000},
        "a source of 5000 bytes under a lowered budget",
        {BUDGET_VARIABLE: "4096"},
    )

    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"a 5000-byte source under a 4096-byte budget was answered "
        f"{str(response)[:300]}. A budget a caller may write is still read and "
        "still measured against: the new refusal is about texts no reader "
        "turns into a number, and about nothing else."
    )
    refusal = diagnostic_of(
        response, "input_budget_exceeded", "a source of 5000 bytes"
    )
    assert refusal.get("expected") == 4096, (
        f"the run was measured against {refusal.get('expected')!r}, not the "
        f"4096 the caller wrote: {refusal}."
    )


def test_a_budget_above_the_declared_number_is_still_refused():
    """Given a caller that writes a number larger than the 1048576 bytes
    this tool declares, when it asks for the manifest, then the command
    refuses it by name: a caller may lower a budget and never raise one.
    """
    response = answered(
        {"operation": "discover"},
        "a budget above the declared maximum",
        {BUDGET_VARIABLE: str(DECLARED_INPUT_SIZE + 1)},
    )

    assert response["status"] == INVALID_INPUT, (
        f"a budget above the declared maximum was answered "
        f"{str(response)[:300]}. A caller that could raise a budget would be "
        "given a promise this tool never made."
    )
    refusal = diagnostic_of(
        response, MALFORMED_REQUEST, "a budget above the declared maximum"
    )
    assert refusal.get("symbol") == BUDGET_VARIABLE, refusal


def test_a_number_above_a_budget_is_still_answered_with_the_sentence_it_had():
    """Given a caller that writes 123456 where this tool declares 10000
    milliseconds, and another that writes 10485761 where it declares
    1048576 bytes, when each asks for the manifest, then each is told
    its number is above the one this tool declares -- not that it was
    refused by its length, which would send it to count characters.
    """
    for variable, written, declared in (
        (BUDGET_TIME_VARIABLE, "123456", DECLARED_OPERATION_TIME),
        (BUDGET_VARIABLE, "10485761", DECLARED_INPUT_SIZE),
    ):
        response = answered(
            {"operation": "discover"},
            f"{variable} written as {written}",
            {variable: written},
        )
        refusal = diagnostic_of(
            response, MALFORMED_REQUEST, f"{variable} written as {written}"
        )
        reason = refusal.get("reason", "")
        assert f"is {int(written)}, above the {declared}" in reason, (
            f"{variable} written as {written} was refused with "
            f"{reason[:300]!r}. A number this tool reads is answered against "
            "the number it declares, in the sentence callers already read."
        )
        assert "characters long" not in reason, (
            f"{variable} written as {written} was refused for its length: "
            f"{reason[:300]!r}. Six or eight digits are read as one number; "
            "only a run no reader turns into a number is refused by length."
        )
