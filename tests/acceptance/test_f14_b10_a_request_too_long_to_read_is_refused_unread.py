"""F14.B10 -- a request longer than this tool reads is refused against
the input budget without being read, and a source is sized in bytes
rather than in characters.

Reading a request this tool cannot answer, and then refusing it, costs
the memory of the whole request twice over: once to hold what was sent
and once to measure it. The tool now reads one byte past what it can
answer and stops there, so a request far too large is refused having
cost a page or two -- and, because it never read the request, it says
plainly that it does not know which operation was asked for.

still passes if: the tool refused every request. The third case sends a
source well under the budget and requires it not to be refused for its
size.
"""

from __future__ import annotations

import resource

from _f14_budget_fixtures import (
    CATEGORY_OF,
    INPUT_SIZE,
    RESOURCE_EXHAUSTED,
    answered,
    assert_claims_nothing,
    assert_names_the_budget,
    budget_entry,
    check,
    discover,
    the_refusal,
)

# A text of 200000 characters, far past the 64 KiB a request may carry
# around its source: sent as an argument, which is not the source at
# all, so a tool that sized only the source would read all of it.
A_LONG_ARGUMENT = "7" * 200_000


def test_the_manifest_says_how_much_of_a_request_this_tool_reads():
    """Given a caller sizing its request, when it reads the input
    budget, then it finds how much this tool allows a request to carry
    around its source, as a whole number of bytes with its reason.
    """
    stated = budget_entry(discover(), "evaluate", INPUT_SIZE)

    allowance = stated.get("request_allowance")
    assert isinstance(allowance, int) and allowance > 0, (
        f"the input budget states {allowance!r} as the request this tool "
        f"reads around a source: {stated}. A caller sizing a request with "
        "arguments and fields beside its source has no second number to size "
        "them against."
    )
    assert str(allowance) in stated.get("request_allowance_reason", ""), (
        f"the input budget states no reason for the {allowance} bytes it "
        f"allows around a source: {stated}. A caller asked to send less is "
        "owed the reason the number is what it is."
    )


def test_a_request_longer_than_this_tool_reads_is_refused_unread():
    """Given a caller whose input budget is 100 bytes and whose request
    carries a 200000 character argument, when it sends that request,
    then it is refused against the input budget, told that the operation
    it asked for was never read, and given one complete JSON answer.
    """
    response = answered(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": "(defn f (sig () -> Int ! pure) 1)",
            "function": "f",
            "arguments": [A_LONG_ARGUMENT],
        },
        "a request far longer than the tool reads",
        {INPUT_SIZE: 100},
    )

    why = "a request of about 200000 bytes against an input budget of 100"
    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: "
        f"{str(response)[:300]}. Everything a request carries is read through "
        "the same input, so a request too long to answer is answered against "
        "the budget that sizes it."
    )
    refusal = the_refusal(response, CATEGORY_OF[INPUT_SIZE], why)
    assert_names_the_budget(refusal, INPUT_SIZE, 100, None, why)
    assert_claims_nothing(response, why)
    assert response["operation"] is None, (
        f"the answer to {why} says it is about the "
        f"{response.get('operation')!r} operation: {str(response)[:300]}. The "
        "tool stopped before reading the request, so it does not know which "
        "operation was asked for and may not say that it does."
    )
    assert "never read which operation" in refusal["reason"], (
        f"the refusal for {why} says: {refusal['reason']!r}. A caller whose "
        "operation was never read is told so, or it will look for the fault "
        "in an operation the tool never reached."
    )


def test_a_source_is_sized_in_the_bytes_it_takes_not_the_characters():
    """Given an input budget of 100 bytes and a source of 50 characters
    that take 148 bytes, when a caller checks it, then it is refused for
    the input budget with 148 reported: a budget counted in bytes is
    measured in bytes.
    """
    source = ";" + "€" * 49
    assert len(source) == 50 and len(source.encode("utf-8")) == 148

    response = check(source, "50 characters of 148 bytes", {INPUT_SIZE: 100})

    why = "a source of 50 characters taking 148 bytes against a budget of 100"
    refusal = the_refusal(response, CATEGORY_OF[INPUT_SIZE], why)
    assert_names_the_budget(refusal, INPUT_SIZE, 100, 148, why)


def test_a_source_well_under_the_budget_is_not_refused_for_its_size():
    """Given the same budget of 100 bytes and a source of 21 characters
    taking 61 bytes, when a caller checks it, then whatever the tool
    says about the program, it does not refuse it for its size.
    """
    source = ";" + "€" * 20
    assert len(source) == 21 and len(source.encode("utf-8")) == 61

    response = check(source, "21 characters of 61 bytes", {INPUT_SIZE: 100})

    refused_for_size = [
        entry
        for entry in (response.get("diagnostics") or [])
        if entry.get("category") == CATEGORY_OF[INPUT_SIZE]
    ]
    assert not refused_for_size, (
        f"a source of 61 bytes was refused against an input budget of 100: "
        f"{response}. Sizing a text by its characters rather than its bytes "
        "refuses texts that fit, and a caller that sized its source against "
        "the stated number cannot tell why."
    )


# A request of 20 MiB: far past anything this tool answers, and large
# enough that holding it in memory to refuse it shows up in what the
# operating system reports the command took.
A_HUGE_SOURCE = "x" * (20 * 1024 * 1024)


def _greatest_memory_a_child_has_taken() -> int:
    """The greatest memory any command this test has started has taken.

    A high-water mark over every child of this test process, which is
    why the case below starts a small run first and compares the two.
    """
    return resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss


def test_a_request_far_too_long_is_not_held_in_memory_to_be_refused():
    """Given an input budget of 100 bytes, when a caller sends a 20 MiB
    request, then the tool refuses it for the input budget without ever
    having taken more memory than it takes to answer a small one: a
    request too large to answer is not copied into memory first.
    """
    check(";small", "a small request", {INPUT_SIZE: 100})
    answering_a_small_request = _greatest_memory_a_child_has_taken()

    response = check(A_HUGE_SOURCE, "a 20 MiB request", {INPUT_SIZE: 100})
    answering_a_huge_request = _greatest_memory_a_child_has_taken()

    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"a 20 MiB request under an input budget of 100 bytes was answered "
        f"{response.get('status')!r}: {str(response)[:300]}."
    )
    assert answering_a_huge_request <= answering_a_small_request * 1.5, (
        f"answering a 20 MiB request took {answering_a_huge_request} where "
        f"answering a small one took {answering_a_small_request} (the "
        "greatest either child has taken, as the operating system reports "
        "it): the tool is reading a request it cannot answer into memory and "
        "refusing it afterwards, which spends the very memory the budgets "
        "exist to hold down. Read one character past what the budgets allow "
        "and answer without reading the rest."
    )
