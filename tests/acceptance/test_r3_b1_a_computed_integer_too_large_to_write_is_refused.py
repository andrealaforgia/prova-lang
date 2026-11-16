"""R3.B1 -- an integer the tool computes but cannot write is refused
where the function stands, not reported as a failure of the tool.

A program may multiply numbers each of which this tool reads happily
and reach a result with more digits than the tool writes into an
answer. A caller that meets that is owed the limit, the number of
digits its program reached and the place to repair, exactly as it is
owed them when a text nests too deep.

still passes if: the tool refused every computed value. The third test
runs the same shape of program just under the limit and requires the
exact number back, and the fourth requires a value far past 64 bits.
"""

from __future__ import annotations

from _r3_fixtures import (
    A_THOUSAND_NINES,
    A_THOUSAND_NINES_VALUE,
    RESOURCE_EXHAUSTED,
    WRITTEN_DIGITS_EXCEEDED,
    WRITTEN_DIGITS_LIMIT,
    WRITTEN_DIGITS_NAME,
    answered,
    diagnostic_of,
    multiplying,
)

# Five 1000-digit literals multiplied together: every literal is inside
# the 1000 digits this tool reads, and the result is 5000 digits long.
TOO_LARGE = multiplying(A_THOUSAND_NINES, 5)
TOO_LARGE_DIGITS = 5000

# Four of them: exactly the 4000 digits this tool writes.
AT_THE_LIMIT = multiplying(A_THOUSAND_NINES, 4)


def test_an_evaluation_whose_result_cannot_be_written_is_refused_where_the_function_stands():
    """Given a program whose function multiplies five 1000-digit numbers
    into a result of 5000 digits, when a caller evaluates that function,
    then the answer refuses with the written-digit limit, saying 4000
    was the most and 5000 was reached, at the line the function is
    declared on -- and says nothing about the tool having failed.
    """
    response = answered(
        {"operation": "evaluate", "source": TOO_LARGE, "function": "big",
         "arguments": []},
        "an evaluation whose result has 5000 digits",
    )

    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the answer carries status {response.get('status')!r}: "
        f"{str(response)[:400]}. A result the tool will not write is a limit "
        "of the tool, answered the way every other limit is, and never a "
        "report that the tool itself failed."
    )
    refusal = diagnostic_of(
        response, WRITTEN_DIGITS_EXCEEDED, "an evaluation of 5000 digits"
    )
    assert refusal.get("symbol") == WRITTEN_DIGITS_NAME, (
        f"the refusal is about {refusal.get('symbol')!r}: {refusal}. It names "
        f"the limit {WRITTEN_DIGITS_NAME!r} so a caller can look the number up "
        "where the tool publishes it."
    )
    assert refusal.get("expected") == WRITTEN_DIGITS_LIMIT, (
        f"the refusal says the most this tool writes is "
        f"{refusal.get('expected')!r}, not {WRITTEN_DIGITS_LIMIT}: {refusal}. A "
        "caller that must shorten its result reads the number from here."
    )
    assert refusal.get("actual") == TOO_LARGE_DIGITS, (
        f"the refusal says the result reached {refusal.get('actual')!r} "
        f"digits, not {TOO_LARGE_DIGITS}: {refusal}. The digits reached say "
        "how far past the limit the program went."
    )
    assert refusal.get("location", {}).get("line") == 1, (
        f"the refusal stands at {refusal.get('location')!r}: {refusal}. A "
        "refusal about a program sends its reader to the line to open, and "
        "the function is declared on line 1."
    )
    assert "result" not in response and "claim" not in response, (
        f"the answer carries a claim or a result beside the refusal: "
        f"{str(response)[:400]}. A run the tool stopped answers nothing about "
        "the program."
    )


def test_running_the_examples_of_such_a_program_is_refused_the_same_way():
    """Given the same program, whose declared example runs the function,
    when a caller runs the examples, then the answer carries the same
    refusal with the same 2 numbers, and no report that the tool failed.
    """
    response = answered(
        {"operation": "examples", "source": TOO_LARGE},
        "the examples of a program computing 5000 digits",
    )

    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the answer carries status {response.get('status')!r}: "
        f"{str(response)[:400]}. Running the examples meets the same limit as "
        "evaluating by hand and answers it the same way."
    )
    refusal = diagnostic_of(
        response, WRITTEN_DIGITS_EXCEEDED, "the examples of a 5000-digit program"
    )
    assert (refusal.get("expected"), refusal.get("actual")) == (
        WRITTEN_DIGITS_LIMIT,
        TOO_LARGE_DIGITS,
    ), (
        f"the refusal says {refusal.get('expected')!r} and "
        f"{refusal.get('actual')!r}: {refusal}. One limit, one pair of numbers, "
        "whichever operation met it."
    )
    assert "tool_failure" not in str(response), (
        f"the answer says the tool failed: {str(response)[:400]}. The program "
        "asked for more digits than the tool writes, which is an answer about "
        "the request and not a broken tool."
    )


def test_a_result_at_the_limit_is_written_exactly_as_before():
    """Given a program multiplying four 1000-digit numbers, whose result
    is exactly the 4000 digits this tool writes, when a caller evaluates
    it, then the answer carries that number exactly.
    """
    response = answered(
        {"operation": "evaluate", "source": AT_THE_LIMIT, "function": "big",
         "arguments": []},
        "an evaluation whose result has 4000 digits",
    )

    assert response["status"] == "completed", (
        f"a result of exactly {WRITTEN_DIGITS_LIMIT} digits was answered "
        f"{str(response)[:300]}. A value at the limit is written, not refused: "
        "a limit that refuses what it declares it writes moves the limit."
    )
    written = response["result"]["value"]
    assert int(written) == A_THOUSAND_NINES_VALUE**4, (
        f"the answer carries a number {len(written)} digits long that is not "
        "the product of the four literals the program multiplies. An integer "
        "the tool writes is the exact number it computed."
    )


def test_an_integer_far_beyond_64_bits_is_still_exact():
    """Given a program multiplying 9223372036854775807 by itself, a
    result of 38 digits that no 64-bit number holds, when a caller
    evaluates it, then the exact product comes back.
    """
    response = answered(
        {"operation": "evaluate", "source": multiplying("9223372036854775807", 2),
         "function": "big", "arguments": []},
        "an evaluation whose result passes 64 bits",
    )

    assert response["status"] == "completed", str(response)[:300]
    assert int(response["result"]["value"]) == 9223372036854775807**2, (
        f"the answer carries {response['result']['value']!r}, not the exact "
        "product. An integer past 64 bits is kept exactly: the limit is on "
        "the digits an answer writes, not on what a program may mean."
    )
