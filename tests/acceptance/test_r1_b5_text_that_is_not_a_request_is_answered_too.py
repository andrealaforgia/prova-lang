"""R1.B5 -- text this tool cannot read as a request is answered, not
reported as a failure of the tool.

A client that sent nothing, or stopped writing partway, used to be told
the tool had failed and to find a non-zero exit code waiting for it. It
then had no way to tell its own bad request from a broken tool, and
would go looking in the wrong place. It is now answered like every other
unreadable input: by name, with the place its text stopped at, and the
tool exits 0.

still passes if: the tool answered everything with the same refusal. The
last test sends one readable request through the same door and requires
it to be answered about itself.
"""

from __future__ import annotations

import json
import subprocess

import pytest

from _r1_robustness_fixtures import (
    INVALID_INPUT,
    MALFORMED_REQUEST,
    SYMBOL,
    REPO_ROOT,
    ToolRun,
    the_refusal,
)

NOT_A_REQUEST = {
    "nothing at all": "",
    "only blank space": "   \n  \t\n",
    "an object that stops partway": '{"operation":',
    "an opening brace and a word": "{not json",
    "two requests in one text": '{"operation": "discover"}{"operation": "discover"}',
    "a word on its own": "discover",
}


def _send(text: str) -> ToolRun:
    """The command, given exactly `text` on its standard input."""
    finished = subprocess.run(
        ["prova"],
        input=text,
        capture_output=True,
        text=True,
        timeout=30.0,
        check=False,
        cwd=REPO_ROOT,
    )
    return ToolRun(finished.returncode, finished.stdout, finished.stderr)


@pytest.mark.parametrize("why", sorted(NOT_A_REQUEST))
def test_text_that_is_not_a_request_comes_back_as_one_answer(why):
    """Given text that is not a JSON request -- nothing, blank space, an
    object that stops partway, or a bare word -- when the command reads
    it, then it answers invalid input naming the request, says where the
    text stopped, and exits 0.
    """
    run = _send(NOT_A_REQUEST[why])

    response = run.assert_answered(f"text that is {why}")
    assert response.get("status") == INVALID_INPUT, (
        f"the tool answered {response.get('status')!r} for text that is "
        f"{why}: {response}. The client wrote a bad request; saying the tool "
        "failed sends it to look at the tool instead of at what it sent."
    )
    refusal = the_refusal(response, MALFORMED_REQUEST, f"text that is {why}")
    assert refusal.get(SYMBOL) == "request", (
        f"the refusal for text that is {why} names {refusal.get(SYMBOL)!r}: "
        f"{refusal}. There is no field to name yet; what could not be read is "
        "the request itself."
    )
    assert "line" in refusal.get("reason", "") and "column" in refusal.get("reason", ""), (
        f"the refusal for text that is {why} does not say where the text "
        f"stopped: {refusal.get('reason')!r}. A client repairing a generated "
        "request is sent to the place it stopped being readable."
    )


@pytest.mark.parametrize("why", sorted(NOT_A_REQUEST))
def test_the_tool_says_nothing_on_standard_error_about_it(why):
    """Given the same text, when the command reads it, then standard
    error is empty: a client reading only standard output is not left
    with half the story told somewhere it is not looking.
    """
    run = _send(NOT_A_REQUEST[why])

    assert run.stderr.strip() == "", (
        f"the tool wrote {run.stderr[-600:]!r} on standard error for text that "
        f"is {why}. Everything a client acts on is in the one JSON answer."
    )


def test_the_published_statuses_still_leave_out_a_failure_of_the_tool():
    """Given the manifest, when a caller reads what its list of statuses
    covers, then the list is for answered requests and the name reserved
    for a failure of the tool itself is not among them, so the two
    remain different things.
    """
    manifest = json.loads(_send('{"operation": "discover"}').stdout)
    statuses = manifest["result"]["statuses"]

    assert "tool_failure" not in statuses, (
        f"the manifest lists a status this tool never answers with: "
        f"{sorted(statuses)}. A failure of the tool is not an answer to a "
        "request, and must not be read as one."
    )
    assert INVALID_INPUT in statuses, (
        f"the manifest does not list {INVALID_INPUT!r}: {sorted(statuses)}. It "
        "is the status unreadable text now carries."
    )


def test_a_readable_request_through_the_same_door_is_still_answered():
    """Given one complete JSON request on standard input, when the
    command reads it, then it answers that request rather than refusing
    it, so a tool refusing everything would not pass the tests above.
    """
    run = _send('{"operation": "discover"}')

    response = run.assert_answered("a complete JSON request")
    assert response.get("operation") == "discover", (
        f"the tool answered {response.get('operation')!r}: {str(response)[:300]}. "
        "A complete request is answered about itself."
    )
    assert response.get("status") == "completed", (
        f"the tool answered {response.get('status')!r} for a complete request: "
        f"{str(response)[:300]}."
    )
