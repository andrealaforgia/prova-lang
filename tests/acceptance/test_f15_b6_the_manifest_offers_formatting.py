"""F15.B6 -- an agent reading the manifest finds formatting offered, with
the shape of what it sends and the shape of what it gets back.

SPEC.md lines 465-470 ask the manifest to list the operations with their
request and response schemas and to advertise an unimplemented operation
as unavailable. Formatting was advertised as unavailable while it was
refused; an agent plans its work from that word, so the word and the
shapes change together with the behaviour.

still passes if: the manifest had said 'available' while the operation
still refused. The last test asks for the operation and compares what it
answers with the word the manifest carries.
"""

from __future__ import annotations

from _f15_format_fixtures import ask_for_the_manifest, ask_to_format

A_PROGRAM_TO_WRITE_OUT = (
    "(defn add-one\n"
    "  (sig ((n Int)) -> Int ! pure)\n"
    "  (examples (example (add-one 41) => 42))\n"
    "  (+ n 1))\n"
)


def test_formatting_is_advertised_as_one_an_agent_may_ask_for():
    result = ask_for_the_manifest()["result"]

    assert result["operations"].get("format") == "available", (
        f"the manifest says formatting is "
        f"{result['operations'].get('format')!r}: {result['operations']}. An "
        "agent that reads 'unavailable' never sends the request; say the "
        "word that matches what the tool answers"
    )
    assert result["categories"]["formatting"] == {
        "operation": "format",
        "availability": "available",
    }, (
        f"the formatting category of the profile says "
        f"{result['categories']['formatting']}: SPEC.md line 467 names "
        "formatting among the operation categories, and the category and the "
        "operation list are one decision read twice"
    )


def test_the_manifest_says_what_to_send_and_what_comes_back():
    schemas = ask_for_the_manifest()["result"]["operation_schemas"]

    assert "format" in schemas, (
        f"the manifest publishes shapes for {sorted(schemas)} and none for "
        "formatting: SPEC.md line 475 says an agent must discover what to "
        "send without guessing an undocumented API"
    )
    request_fields = schemas["format"]["request"]["fields"]
    answer_fields = schemas["format"]["response"]["fields"]

    assert "source" in request_fields, (
        f"the published request carries {sorted(request_fields)} and not the "
        "program to write out: an agent would have nothing to send"
    )
    assert "result" in answer_fields, (
        f"the published answer carries {sorted(answer_fields)} and nothing "
        "the canonical text arrives in: an agent would not know where to "
        "read it"
    )
    assert "status" in answer_fields and "diagnostics" in answer_fields, (
        f"the published answer carries {sorted(answer_fields)}: every answer "
        "of this tool says what happened and carries the refusals it met"
    )


def test_the_word_the_manifest_carries_is_the_one_the_tool_answers_with():
    word = ask_for_the_manifest()["result"]["operations"]["format"]

    answered = ask_to_format(A_PROGRAM_TO_WRITE_OUT)

    refused_as_unavailable = answered["status"] == "unavailable"
    assert refused_as_unavailable == (word == "unavailable"), (
        f"the manifest advertises formatting as {word!r} and asking for it "
        f"answered {answered['status']!r}: {answered}. An agent plans its "
        "work from the word the manifest carries, so the two must agree"
    )
