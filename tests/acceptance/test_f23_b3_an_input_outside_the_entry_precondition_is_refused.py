"""An input outside the entry's precondition is refused, with no result
value and under a status of its own.

SPEC.md: external inputs must decode to the declared types and satisfy
the entry preconditions before compiled code is called, and a rejection
has no successful return value; an internal contract failure in a
supposedly verified execution is an assurance failure and not an
ordinary domain error. A caller who sends a count of 3 to a component
whose capacity is 2 has sent input the program promises nothing about:
that is a rejection of the input, and it must not be reported with the
status that says a contract of a verified program did not hold.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from _f22_fixtures import evaluate, hour_clock, run_artefact
from _f23_fixtures import (
    ASSURANCE_FAILURE,
    PRECONDITION_UNMET,
    an_artefact_of,
    first_line_word,
    reservation_source,
)

# Counts the reservation component's own precondition refuses -- its
# capacity is 2 and a count below 0 is no state at all -- and hours the
# shipped clock's precondition refuses, its dial being 1 to 12. Each is
# a well-formed value of the declared type.
OUTSIDE_THE_PRECONDITION = (
    ("the reservation component", ["(Reservation 7)", "(Reserve)"]),
    ("the reservation component", ["(Reservation -5)", "(Release)"]),
    ("the hour clock", ["(Clock 99)", "(Tick)"]),
)


@pytest.fixture(scope="module")
def the_two_artefacts():
    """The source and the built artefact of each of the two shipped
    programs, each in a directory of its own because both entries are
    called `step`."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        for_the_component = pathlib.Path(tmp_dir) / "component"
        for_the_clock = pathlib.Path(tmp_dir) / "clock"
        for_the_component.mkdir()
        for_the_clock.mkdir()
        yield {
            "the reservation component": (
                reservation_source(),
                an_artefact_of(reservation_source(), "step", for_the_component),
            ),
            "the hour clock": (
                hour_clock(),
                an_artefact_of(hour_clock(), "step", for_the_clock),
            ),
        }


def test_an_input_outside_the_entry_precondition_is_refused_with_no_result(
    the_two_artefacts,
):
    """Given the built reservation component and the built hour clock,
    when each is run over a well-formed state its entry's precondition
    refuses, then the run exits with the status reserved for an unmet
    precondition, prints nothing as an answer, opens its refusal with
    the word PRECONDITION, names the condition that did not hold, and
    ends in no traceback.

    still passes if: the refusal had been reported as an assurance
    failure -- the status is required to differ from the one that says a
    contract of a verified program did not hold, which is asserted
    directly below.
    """
    for about, arguments in OUTSIDE_THE_PRECONDITION:
        source, target = the_two_artefacts[about]
        ran = run_artefact(target, arguments)

        assert ran.returncode == PRECONDITION_UNMET, (
            f"WHAT: {about} run over {arguments} exited {ran.returncode}, "
            f"not {PRECONDITION_UNMET}. "
            "WHY: that value is outside the entry's precondition, so the "
            "program promises nothing about it; this is a rejection of the "
            "input and has a status of its own, apart from the status that "
            "says a contract of a verified program did not hold. "
            f"HOW: read what it printed: stdout={ran.stdout[-200:]!r} "
            f"stderr={ran.stderr[-400:]!r}"
        )
        assert ran.returncode != ASSURANCE_FAILURE, (
            f"WHAT: {about} reported an unmet precondition as an assurance "
            f"failure for {arguments}. "
            "WHY: an assurance failure says a verified program broke its own "
            "promise; a caller who sent input outside the precondition must "
            "never be told that. "
            f"HOW: refuse the input before the compiled code is called: "
            f"{ran.stderr[-300:]!r}"
        )
        assert ran.stdout.strip() == "", (
            f"WHAT: {about} printed {ran.stdout[:160]!r} as an answer to "
            f"{arguments}, which its precondition refuses. "
            "WHY: a rejection has no successful return value. "
            "HOW: decide the refusal before anything is written."
        )
        assert first_line_word(ran) == "PRECONDITION", (
            f"WHAT: the refusal of {arguments} opens with "
            f"{first_line_word(ran)!r} and not 'PRECONDITION': "
            f"{ran.stderr[:200]!r}. "
            "WHY: a reader sorts refusals by the category word on the first "
            "line, before any prose. "
            "HOW: write the category word first on the first line."
        )
        assert "Traceback" not in ran.stderr, (
            f"WHAT: {about} ended in a traceback over {arguments}: "
            f"{ran.stderr[-400:]!r}. "
            "WHY: an artefact never ends in a Python traceback. "
            "HOW: refuse by name where the failure happens."
        )
        assert "valid-state" in ran.stderr, (
            f"WHAT: the refusal of {arguments} does not name the condition "
            f"that did not hold: {ran.stderr[-400:]!r}. "
            "WHY: the caller must be told which precondition refused their "
            "input, not only that one did. "
            "HOW: name the condition the entry declares."
        )

        refused = evaluate(source, "step", arguments)
        assert (refused.get("result") or {}).get("value") is None, (
            f"WHAT: the compiler answered "
            f"{(refused.get('result') or {}).get('value')!r} for the same "
            f"call over {arguments}. "
            "WHY: this test rests on the two agreeing that the input is "
            "outside what the program promises; if the compiler answers it, "
            "the artefact must answer it too. "
            f"HOW: inspect the answer: {refused}"
        )


def test_a_state_the_precondition_admits_is_still_answered(the_two_artefacts):
    """Given the same two artefacts, when each is run over a state its
    precondition admits, then each answers what the program computes --
    so the refusals above are about the inputs and not about the
    artefacts."""
    for about, arguments, expected in (
        (
            "the reservation component",
            ["(Reservation 2)", "(Reserve)"],
            "(Outcome (Reservation 2) false)",
        ),
        ("the hour clock", ["(Clock 4)", "(Tick)"], "(Outcome (Clock 5) true)"),
    ):
        _, target = the_two_artefacts[about]
        ran = run_artefact(target, arguments)
        assert (ran.returncode, ran.stdout.strip()) == (0, expected), (
            f"WHAT: {about} over {arguments} exited {ran.returncode} "
            f"answering {ran.stdout.strip()!r}, and the program computes "
            f"{expected!r}. "
            "WHY: the two states above are inside the precondition, so the "
            "refusals of this file are about the inputs that are outside it. "
            f"HOW: read what it printed: {ran.stderr[-300:]!r}"
        )
