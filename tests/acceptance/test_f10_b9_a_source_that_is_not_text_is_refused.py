"""F10.B9 -- a request whose `source` is not text is refused, not
crashed.

Every answer of an operation that reads source is about a text: the
revision it carries is the revision of those characters. A request that
sends a list, a number, nothing, or an object has no text in it, and the
tool says so instead of ending in a traceback.

Drives only the `prova` command's real JSON stdin/stdout surface, and
reads the exit code too, because a crash is what this test exists to
see.

still passes if: the tool refused every request. The last test sends the
same programs as text and requires them to be answered.
"""

from __future__ import annotations

from _f10_diagnostic_fixtures import (
    INVALID_INPUT,
    REVISION,
    WELL_FORMED,
    run,
    the_one_refusal,
)

# The four shapes a client can put in `source` that hold no text of a
# program, including the one a client writing its file line by line
# reaches for first.
NOT_TEXT = {
    "a list of lines": ["(defn f)"],
    "a whole number": 7,
    "nothing at all": None,
    "an object": {"text": "(defn f)"},
}

SOURCE_READING_OPERATIONS = ("check", "examples", "verify", "evaluate")


def _request(operation: str, source: object) -> dict:
    request = {"prova": "i1", "operation": operation, "source": source}
    if operation == "evaluate":
        request.update({"function": "fare", "arguments": ["1"]})
    return request


def test_a_source_that_is_not_text_is_answered_by_every_operation():
    """Given the 4 values that are not the text of a program, when each
    of the 4 operations that read source is asked with one, then the
    command exits 0 with status 'invalid_input' and one
    'malformed_request' refusal naming the field 'source'."""
    for why, value in NOT_TEXT.items():
        for operation in SOURCE_READING_OPERATIONS:
            result = run(_request(operation, value))
            assert result.exit_code == 0, (
                f"{operation} with {why} as its source exited "
                f"{result.exit_code} and printed {result.stderr[-400:]!r}. A "
                "request the tool cannot read is answered, never crashed."
            )
            response = result.response()
            assert response.get("status") == INVALID_INPUT, (why, operation, response)
            entry = the_one_refusal(response, f"{why} sent to {operation}")
            assert entry.get("category") == "malformed_request", entry
            assert entry.get("symbol") == "source", (
                f"the refusal for {why} does not name the field at fault: "
                f"{entry}. A client repairs the request by that name."
            )
            assert REVISION not in entry, (
                f"the refusal for {why} carries a revision: {entry}. A revision "
                "is the revision of a text, and this request carried none."
            )


def test_the_same_programs_as_text_are_still_answered():
    """Control: given the well-formed program as text, when each of the
    4 operations is asked with it, then all 4 answer 'completed'."""
    for operation in SOURCE_READING_OPERATIONS:
        response = run(_request(operation, WELL_FORMED)).response()
        assert response.get("status") == "completed", (
            f"{operation} refused a program sent as text: {response}. The "
            "refusals above are about the kind of value, not about every "
            "request."
        )
