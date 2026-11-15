"""F17.B6 -- when this tool fails inside itself, what comes back says the
tool failed and reports nothing about a program.

SPEC.md lines 280-284: a tool failure is not a semantic result. A client
that met a status of the ordinary vocabulary, or a claim, a result or a
revision, would read a failure of this tool as a statement about its
program.

Drives the public entry point the command calls to turn one request into
the one text it prints. A failure of the tool cannot be reached through
the command's own input without planting a defect in the tool, so the
request submitted here is an object that breaks while the tool reads a
field of it: the premise is the failure the answer then names, and the
positive control in the same file sends an ordinary request through the
same entry point and reads an ordinary answer.

still passes if: the tool answered a failure to everything. The control
at the end requires an ordinary request to be answered as before.
"""

from __future__ import annotations

import json

from prova import service

A_PROGRAM = (
    "(defn twice\n"
    "  (sig ((n Int)) -> Int ! pure)\n"
    "  (examples (example (twice 2) => 4))\n"
    "  (* n 2))\n"
)

THE_STATUSES_OF_AN_ANSWERED_REQUEST = (
    "completed",
    "invalid_program",
    "unsupported",
    "invalid_input",
    "resource_exhausted",
    "unavailable",
)

WHAT_AN_ANSWER_ABOUT_A_PROGRAM_CARRIES = (
    "claim",
    "result",
    "source_digest",
    "stands_on",
    "contract_report",
)


class ARequestThatBreaksWhileItIsRead(dict):
    """A request object that raises when the tool reads a field of it.

    The one way to make this tool fail inside itself from outside it,
    without planting a defect in the tool.
    """

    def get(self, *arguments, **named):
        raise RuntimeError("this request breaks while it is read")


def _answer_to(submitted: object) -> dict:
    return json.loads(service.answer_text(submitted))


def test_a_failure_inside_the_tool_is_answered_as_a_failure_of_the_tool():
    """Given a request that breaks while the tool reads a field of it,
    when the tool answers, then the answer carries the status of a tool
    failure and 1 refusal that says so."""
    answer = _answer_to(ARequestThatBreaksWhileItIsRead(operation="check"))

    assert answer["status"] == "tool_failure", (
        f"WHAT: the tool answered {answer['status']!r} after failing inside "
        f"itself: {answer}. WHY: a status of the ordinary vocabulary would "
        "tell a client something was decided about its program. "
        "HOW: answer 'tool_failure'."
    )
    categories = [entry.get("category") for entry in answer.get("diagnostics") or []]
    assert categories == ["tool_failure"], (
        f"WHAT: the answer carries {categories}. WHY: a client sorts answers "
        "by the category of the refusal they carry. HOW: carry 1 refusal of "
        "category 'tool_failure'."
    )
    reason = (answer["diagnostics"][0].get("reason") or "").lower()
    assert "this request breaks while it is read" in reason, (
        f"WHAT: the refusal says {reason!r} and does not name what failed. "
        "WHY: a reader has to be told what broke to report or repair it. "
        "HOW: name the failure that was raised."
    )


def test_a_failure_of_the_tool_reports_nothing_about_a_program():
    """Given the same failing request, then the answer carries none of
    the 5 fields an answer about a program carries."""
    answer = _answer_to(ARequestThatBreaksWhileItIsRead(operation="check"))

    carried = [field for field in WHAT_AN_ANSWER_ABOUT_A_PROGRAM_CARRIES if field in answer]
    assert carried == [], (
        f"WHAT: the answer to a failure of the tool carries {carried}: "
        f"{answer}. WHY: the tool read no program, so anything it says about "
        "one is a statement nobody made. HOW: answer the failure alone."
    )
    assert answer["status"] not in THE_STATUSES_OF_AN_ANSWERED_REQUEST, (
        f"WHAT: a failure of the tool took the status {answer['status']!r}, "
        "which an answered request takes. WHY: a client could not tell the "
        "two apart. HOW: keep the failure of the tool out of that vocabulary."
    )


def test_an_ordinary_request_is_still_answered_as_before():
    """Control: given an ordinary check request, when the same entry
    point answers it, then the answer is completed and is about the
    program, so a tool that answered a failure to everything would be
    seen."""
    answer = _answer_to({"operation": "check", "source": A_PROGRAM})

    assert answer["status"] == "completed", answer
    assert answer.get("claim", {}).get("kind") == "static_check", answer
    assert answer.get("source_digest"), answer
