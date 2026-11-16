"""R3.B3 -- a request whose own JSON nests deeper than this tool reads
is refused as a request the caller must repair.

The reader that turns the text of a request into fields calls itself
once per array or object, so a request nesting thousands of them deep
used to exhaust the interpreter before the tool read which operation was
asked for. The tool now states how deeply a request may nest and refuses
past it, with room to spare, the way it already states how deeply a
program may nest.

still passes if: the tool refused every request that carries an array.
The second test sends a request nested exactly to the published limit
and requires the manifest back; the fourth requires a request too long
to read to be refused unread, as before.
"""

from __future__ import annotations

from _r3_fixtures import (
    INVALID_INPUT,
    MALFORMED_REQUEST,
    REQUEST_NESTING_LIMIT,
    RESOURCE_EXHAUSTED,
    WRITTEN_DIGITS_EXCEEDED,
    WRITTEN_DIGITS_LIMIT,
    answered,
    diagnostic_of,
    nesting,
    send_text,
)

# Far past anything a client writes, and the depth the tool used to
# break at.
VERY_DEEP = 20000


def test_a_request_nesting_20000_arrays_is_refused_as_nesting_too_deeply():
    """Given a request whose JSON nests 20000 arrays inside one another,
    when it is sent, then the command exits 0 with an invalid_input
    answer saying the request nests too deeply, and nothing on standard
    error.
    """
    run = send_text(nesting(VERY_DEEP))
    response = run.assert_answered("a request nesting 20000 arrays")

    assert response["status"] == INVALID_INPUT, (
        f"the answer carries status {response.get('status')!r}: "
        f"{str(response)[:400]}. A request the tool cannot read is the "
        "caller's to repair, and the tool read no operation out of it."
    )
    refusal = diagnostic_of(response, MALFORMED_REQUEST, "a request nesting 20000 deep")
    assert refusal.get("symbol") == "request", (
        f"the refusal is about {refusal.get('symbol')!r}: {refusal}. Nothing "
        "but the request itself was read, so the request is what it names."
    )
    reason = refusal.get("reason", "")
    assert "nest" in reason and str(REQUEST_NESTING_LIMIT) in reason, (
        f"the refusal says {reason[:300]!r}, which does not say that the "
        f"request nests too deeply nor name the {REQUEST_NESTING_LIMIT} this "
        "tool reads. A caller whose generator writes deep JSON has no number "
        "to stay under."
    )


def test_a_request_at_the_published_nesting_limit_is_answered_as_before():
    """Given a request nesting exactly the 64 arrays and objects this
    tool reads, when it asks for the manifest, then the manifest comes
    back completed.
    """
    response = send_text(nesting(REQUEST_NESTING_LIMIT)).assert_answered(
        f"a request nesting exactly {REQUEST_NESTING_LIMIT} deep"
    )

    assert response["status"] == "completed", (
        f"a request nested exactly to the limit was answered "
        f"{str(response)[:300]}. A limit that refuses what it declares it "
        "reads moves the limit."
    )


def test_the_manifest_states_how_deep_a_request_may_nest_and_how_long_a_number_may_be():
    """Given a caller that reads the manifest before it sends work, when
    it asks `discover`, then the documentation states the 64 nesting a
    request may have and the 4000 digits an answer writes, and the
    refusal about written digits is published with its shape.
    """
    manifest = answered({"operation": "discover"}, "the manifest")["result"]
    documentation = manifest.get("documentation") or {}

    nesting_said = documentation.get("request_nesting", "")
    assert str(REQUEST_NESTING_LIMIT) in nesting_said, (
        f"the manifest documents the nesting of a request as "
        f"{nesting_said[:200]!r}: a caller that must size its generator reads "
        f"the number from here. Published keys: {sorted(documentation)}."
    )
    digits_said = documentation.get("computed_integers", "")
    assert str(WRITTEN_DIGITS_LIMIT) in digits_said, (
        f"the manifest documents the integers it writes as "
        f"{digits_said[:200]!r}: a caller whose program computes large numbers "
        f"reads the number from here. Published keys: {sorted(documentation)}."
    )
    assert WRITTEN_DIGITS_EXCEEDED in (manifest.get("diagnostic_categories") or []), (
        f"the manifest does not publish the {WRITTEN_DIGITS_EXCEEDED!r} "
        "category a caller can now meet, so a client reading the published "
        "categories cannot know the refusal it may get."
    )
    assert WRITTEN_DIGITS_EXCEEDED in (manifest.get("diagnostic_schemas") or {}), (
        "the manifest publishes no shape for the refusal about written "
        "digits, so a client cannot read its fields from the tool."
    )
    assert sorted(manifest["resource_limits"]["limits"]) == [
        "evaluation_depth",
        "expression_nesting",
    ], (
        f"the two limits published under 'limits' are now "
        f"{sorted(manifest['resource_limits']['limits'])}: callers read those "
        "two names, and this delivery adds none of its own there."
    )


def test_a_request_too_long_to_read_is_still_refused_unread():
    """Given a request of more than 1114112 bytes nesting only 3 deep,
    when it is sent, then it is still refused against the input budget
    without being read, as it was before.
    """
    padding = "x" * (1024 * 1024 + 64 * 1024 + 10)
    response = send_text(
        '{"operation": "check", "source": "' + padding + '"}'
    ).assert_answered("a request longer than the tool reads")

    assert response["status"] == RESOURCE_EXHAUSTED, (
        f"a request past what the tool reads was answered "
        f"{str(response)[:300]}. The bounded read is what keeps a huge request "
        "out of memory, and it still runs before anything looks at the text."
    )
    diagnostic_of(response, "input_budget_exceeded", "a request too long to read")
