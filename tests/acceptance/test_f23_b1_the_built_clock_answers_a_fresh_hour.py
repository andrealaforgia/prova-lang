"""The built clock answers every hour of its dial, including hours no
example used, and refuses every hour outside it.

Half of this is a CONTROL: measured before any code was written, the
artefact already computes a fresh hour, and that half is asserted all
the same, because the whole of F23 rests on the built artefact computing
rather than reciting what an example claimed. The other half is new: an
hour outside the dial is input the program promises nothing about, and
it must be refused under a status of its own rather than under the one
that says a contract of a verified program did not hold.

The hours the shipped clock declares examples for are 1, 11 and 12 for
`step` and 1, 12, 0 and 13 for `valid-state`. Every hour answered here
is outside both sets, and every expected hour comes from the dial the
request states, never from the clock source.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from _f22_fixtures import evaluate, hour_clock, run_artefact
from _f23_fixtures import (
    ANSWERED,
    PRECONDITION_UNMET,
    an_artefact_of,
    first_line_word,
)
from _hour_clock_fixtures import DIAL

# The hours no declared example of the shipped clock visits.
FRESH_HOURS = (2, 3, 4, 5, 6, 7, 8, 9, 10)

# Hours the dial does not carry, which the clock's own precondition
# refuses: one below it and one above it.
HOURS_OFF_THE_DIAL = (0, 13)


@pytest.fixture(scope="module")
def the_built_clock():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield an_artefact_of(hour_clock(), "step", pathlib.Path(tmp_dir))


def test_every_hour_of_the_dial_is_answered_and_the_rest_refused(
    the_built_clock,
):
    """Given the built hour clock, when it is run on each of the nine
    hours no declared example uses and on the two hours outside its
    dial, then every hour of the dial ticks to the next one with the
    tick accepted and exits 0, and each hour outside the dial is refused
    with no result value, under the status reserved for an unmet
    precondition and the word PRECONDITION.

    still passes if: the artefact had recited the three example answers
    only -- hours 2 to 10 are outside every declared example, and the
    answer for each of them is required; and if it had answered
    something for an hour off the dial -- the two halves together are
    the whole of what the entry does with an hour.
    """
    answers = {}
    for hour in FRESH_HOURS:
        ran = run_artefact(the_built_clock, [f"(Clock {hour})", "(Tick)"])
        assert ran.returncode == ANSWERED, (
            f"WHAT: the built clock exited {ran.returncode} on hour {hour}, "
            f"which no declared example uses, instead of answering. "
            "WHY: the Owner runs the artefact on fresh input and gets the "
            "right answer; an hour inside the dial is input it answers. "
            f"HOW: read what it printed: stderr={ran.stderr[-300:]!r}"
        )
        assert "Traceback" not in ran.stderr, (
            f"WHAT: the artefact ended in a traceback on hour {hour}: "
            f"{ran.stderr[-400:]!r}. "
            "WHY: an artefact answers or refuses in words, never in a "
            "traceback. "
            "HOW: refuse by name where the failure happens."
        )
        answers[hour] = ran.stdout.strip()

    expected = {
        hour: f"(Outcome (Clock {DIAL[hour]}) true)" for hour in FRESH_HOURS
    }
    assert answers == expected, (
        f"WHAT: the built clock answered {answers} for the nine fresh hours "
        f"and the dial the request states gives {expected}. "
        "WHY: every tick is accepted and every hour ticks to the next one of "
        "the 12-hour dial; a wrong hour is a wrong answer about a program "
        "this tool said it had verified. "
        f"HOW: read the artefact at {the_built_clock}"
    )

    refused = {}
    for hour in HOURS_OFF_THE_DIAL:
        ran = run_artefact(the_built_clock, [f"(Clock {hour})", "(Tick)"])
        refused[hour] = (ran.returncode, first_line_word(ran), ran.stdout.strip())
        assert "Traceback" not in ran.stderr, (
            f"WHAT: the artefact ended in a traceback on hour {hour}, which "
            f"its dial does not carry: {ran.stderr[-400:]!r}. "
            "WHY: an artefact refuses in words, never in a traceback. "
            "HOW: refuse by name where the failure happens."
        )

    assert refused == {
        hour: (PRECONDITION_UNMET, "PRECONDITION", "")
        for hour in HOURS_OFF_THE_DIAL
    }, (
        f"WHAT: the hours outside the dial were answered with {refused}. "
        "WHY: an hour the clock's own precondition refuses is input the "
        "program promises nothing about: the refusal has no result value, "
        "carries a status of its own, and is not the status that says a "
        "contract of a verified program did not hold. "
        f"HOW: read the artefact at {the_built_clock}"
    )


def test_the_built_clock_and_the_compiler_agree_on_a_fresh_hour(the_built_clock):
    """Given the built clock and the compiler, when both are asked for
    the tick of hour 7 -- an hour no example uses -- then they answer the
    same value.

    still passes if: both had been wrong in the same way -- the hours
    above are asserted against the dial the request states.
    """
    by_the_artefact = run_artefact(the_built_clock, ["(Clock 7)", "(Tick)"])
    by_the_compiler = evaluate(hour_clock(), "step", ["(Clock 7)", "(Tick)"])
    value = (by_the_compiler.get("result") or {}).get("value")

    assert by_the_artefact.stdout.strip() == value, (
        f"WHAT: the artefact answered {by_the_artefact.stdout.strip()!r} and "
        f"the compiler answered {value!r} for the same call. "
        "WHY: SPEC.md requires parsing, checking, encoding, examples and "
        "generated execution to implement the same semantics. "
        f"HOW: read the refusal if there was one: "
        f"{first_line_word(by_the_artefact)!r} "
        f"{by_the_artefact.stderr[-300:]!r}"
    )
