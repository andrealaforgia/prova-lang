"""F14.B2 -- a source larger than the input budget is refused for that
budget, by name, before any rule of the language is read over it.

A caller that sends a text too large for this tool is owed the news that
it was too large, with the size allowed and the size sent, not a long
wait and not a refusal that blames the program.

still passes if: the tool refused every source. The third test below
sends a source of exactly the size allowed and requires it to be
answered as before.
"""

from __future__ import annotations

from _f14_budget_fixtures import (
    CATEGORY_OF,
    DECLARED,
    INPUT_SIZE,
    RESOURCE_EXHAUSTED,
    assert_claims_nothing,
    assert_names_the_budget,
    check,
    source_of_exactly,
    the_refusal,
    within_every_budget,
)


def test_a_source_past_the_budget_a_caller_set_is_refused_by_name():
    """Given a caller that lowered its input budget to 64 bytes and a
    source of 200 bytes, when it checks that source, then the tool stops
    inside the budget, names the input budget, and reports 64 allowed
    beside 200 sent.
    """
    source = source_of_exactly(200)

    response = check(source, "a 200 byte source under a 64 byte budget", {INPUT_SIZE: 64})

    why = "a source of 200 bytes against an input budget of 64"
    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: {response}. "
        "The text breaks no rule of the language -- the tool never read it -- "
        "so calling it an invalid program would turn a budget of this tool "
        "into a rule about what a program may be."
    )
    refusal = the_refusal(response, CATEGORY_OF[INPUT_SIZE], why)
    assert_names_the_budget(refusal, INPUT_SIZE, 64, 200, why)
    assert_claims_nothing(response, why)


def test_a_source_past_the_declared_budget_is_refused_with_no_budget_lowered():
    """Given a source one byte larger than the 1 MiB this tool declares,
    when a caller checks it with nothing lowered, then it is refused for
    the input budget with 1048576 allowed beside 1048577 sent.
    """
    size = DECLARED[INPUT_SIZE] + 1
    source = source_of_exactly(size)

    response = check(source, "a source one byte past the declared input budget")

    why = f"a source of {size} bytes against the declared budget"
    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: "
        f"{str(response)[:400]}. The number the manifest states is the number "
        "the tool enforces; a caller that sized its source against it meets "
        "the budget exactly where it was told it would."
    )
    refusal = the_refusal(response, CATEGORY_OF[INPUT_SIZE], why)
    assert_names_the_budget(refusal, INPUT_SIZE, DECLARED[INPUT_SIZE], size, why)
    assert_claims_nothing(response, why)


def test_a_source_of_exactly_the_size_allowed_is_answered_as_before():
    """Given the 1474 byte hour clock and an input budget lowered to
    exactly its size, when a caller checks it, then it is answered
    normally: the budget refuses what is past it, not what reaches it.
    """
    source = within_every_budget()
    size = len(source.encode("utf-8"))

    response = check(
        source, "a program of exactly the size allowed", {INPUT_SIZE: size}
    )

    assert response["status"] == "completed", (
        f"a program of {size} bytes under an input budget of {size} was "
        f"answered {response.get('status')!r}: {response}. A caller that sized "
        "its source to the number it read is refused at the number it was "
        "promised, so the size allowed is allowed."
    )
