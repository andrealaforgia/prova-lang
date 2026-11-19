"""A contract that does not hold inside the artefact is reported as an
assurance failure: never as an answer, and never as one of the ordinary
rejections of an input.

SPEC.md: an internal contract failure in a supposedly verified execution
is an assurance failure, not an ordinary domain error or success. It also
asks, of the reservation component, that a missing upper guard be
detected although the declared examples visit only non-full states.

A reachable contract failure inside a program this tool certified would
be an unsoundness of the verifier, and no input can produce one: a
source whose promise its body breaks is refused a build. So the failure
is reached the one way a reader can reach it from outside -- the
artefact they hold on disk is changed, as a careless edit or a damaged
copy would change it, so that the translated program answers a state its
own promise forbids. What is asserted is how the artefact reports a
contract that does not hold; nothing here claims that a build of an
unchanged source can reach it.

Drives only the `prova` command's real JSON stdin/stdout surface, the
artefact it writes, and that artefact run by a plain interpreter. No
imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from _f22_fixtures import run_artefact
from _f23_fixtures import (
    ANSWERED,
    ASSURANCE_FAILURE,
    ILL_TYPED,
    MALFORMED,
    PRECONDITION_UNMET,
    an_artefact_of,
    first_line_word,
    reservation_source,
    with_the_upper_guard_relaxed,
)

# The four shapes of wrong input a caller can send, none of which is a
# contract failure of the program.
THE_ORDINARY_REJECTIONS = (
    ("text that is not a value", ["(Reserv", "(Reserve)"], MALFORMED),
    ("a value of the wrong type", ["(Reserve)", "(Reserve)"], ILL_TYPED),
    (
        "a state outside the precondition",
        ["(Reservation 4)", "(Reserve)"],
        PRECONDITION_UNMET,
    ),
    ("one argument where the entry takes two", ["(Reservation 0)"], MALFORMED),
)


@pytest.fixture(scope="module")
def the_component_as_built_and_changed():
    """The built reservation component, and a copy of it whose
    translated program no longer stops a reserve at the full count."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        as_built = an_artefact_of(reservation_source(), "step", destination)
        changed = destination / "changed.py"
        changed.write_text(
            with_the_upper_guard_relaxed(as_built.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
        yield as_built, changed


def test_the_component_as_built_answers_the_full_count_as_the_table_says(
    the_component_as_built_and_changed,
):
    """Given the built reservation component, when it is run over the
    full count of 2 and a reserve, then it answers that the state is
    unchanged and the event was not accepted -- the row SPEC.md writes
    -- so the failure below is caused by the change and not by the
    input."""
    as_built, _ = the_component_as_built_and_changed
    ran = run_artefact(as_built, ["(Reservation 2)", "(Reserve)"])
    assert (ran.returncode, ran.stdout.strip()) == (
        ANSWERED,
        "(Outcome (Reservation 2) false)",
    ), (
        f"WHAT: the component as built exited {ran.returncode} answering "
        f"{ran.stdout.strip()!r} for a reserve at the full count. "
        "WHY: SPEC.md's table writes that row as the state unchanged and the "
        "event rejected; this test rests on the built artefact answering it. "
        f"HOW: read what it printed: {ran.stderr[-300:]!r}"
    )


def test_a_contract_that_does_not_hold_is_reported_as_an_assurance_failure(
    the_component_as_built_and_changed,
):
    """Given a copy of the artefact whose translated program no longer
    stops a reserve at the full count, when it is run over the full
    count of 2 and a reserve -- so that it computes a count of 3, which
    the program's own promise forbids -- then it exits with the status
    reserved for an assurance failure, opens its refusal with the word
    ASSURANCE, names the promise that did not hold and the function that
    made it, prints no answer, and ends in no traceback.

    still passes if: the artefact had refused the input instead -- the
    status is required to be the assurance one and to differ from every
    status an ordinary rejection carries, which the next test asserts.
    """
    _, changed = the_component_as_built_and_changed
    ran = run_artefact(changed, ["(Reservation 2)", "(Reserve)"])

    assert ran.returncode == ASSURANCE_FAILURE, (
        f"WHAT: the changed artefact exited {ran.returncode}, not "
        f"{ASSURANCE_FAILURE}, where the program it carries answers a state "
        "its own promise forbids. "
        "WHY: a contract that does not hold in a supposedly verified "
        "execution is an assurance failure; reporting it as an answer would "
        "hand the Owner a wrong result, and reporting it as a rejection "
        "would blame their input. "
        f"HOW: read what it printed: stdout={ran.stdout[-200:]!r} "
        f"stderr={ran.stderr[-400:]!r}"
    )
    assert ran.stdout.strip() == "", (
        f"WHAT: the changed artefact printed {ran.stdout[:160]!r} as an "
        "answer. "
        "WHY: a run whose contract did not hold has no result value at all. "
        "HOW: write nothing on standard output once a contract has failed."
    )
    assert first_line_word(ran) == "ASSURANCE", (
        f"WHAT: the report opens with {first_line_word(ran)!r} and not "
        f"'ASSURANCE': {ran.stderr[:200]!r}. "
        "WHY: a reader sorts what an artefact reports by the category word "
        "on the first line; an assurance failure is the one word that is "
        "about the program rather than about the input. "
        "HOW: write the category word first on the first line."
    )
    assert "Traceback" not in ran.stderr, (
        f"WHAT: the changed artefact ended in a traceback: "
        f"{ran.stderr[-400:]!r}. "
        "WHY: an artefact never ends in a Python traceback, not even when "
        "the program it carries breaks its own promise. "
        "HOW: refuse by name where the failure happens."
    )
    for owed in ("step", "postcondition", "valid-state"):
        assert owed in ran.stderr, (
            f"WHAT: the report does not name {owed!r}: "
            f"{ran.stderr[-500:]!r}. "
            "WHY: the Owner must be told which function and which promise of "
            "it did not hold, or they cannot tell a damaged artefact from a "
            "wrong one. "
            "HOW: name the function, the kind of contract and the condition."
        )


def test_no_wrong_input_is_ever_reported_as_an_assurance_failure(
    the_component_as_built_and_changed,
):
    """Given the built reservation component, when it is run over the
    four shapes of wrong input a caller can send, then none of them
    exits with the assurance status and none opens with the word
    ASSURANCE -- that report is kept for a contract of the program that
    did not hold.

    still passes if: the four had all carried one status -- the status
    of each kind is asserted here and in the test of the three kinds of
    wrong input.
    """
    as_built, _ = the_component_as_built_and_changed
    reported = {}
    for about, arguments, status in THE_ORDINARY_REJECTIONS:
        ran = run_artefact(as_built, arguments)
        reported[about] = (ran.returncode, first_line_word(ran))
        assert ran.returncode == status, (
            f"WHAT: {about} exited {ran.returncode}, not {status}. "
            "WHY: each kind of wrong input carries the status of its own "
            "kind. "
            f"HOW: read what it printed: {ran.stderr[-300:]!r}"
        )

    assert all(
        status != ASSURANCE_FAILURE and word != "ASSURANCE"
        for status, word in reported.values()
    ), (
        f"WHAT: the four shapes of wrong input were reported as {reported}. "
        "WHY: an assurance failure says a verified program broke its own "
        "promise; a caller who sent wrong input must never be told that, and "
        "an Owner reading their logs must be able to trust the word. "
        "HOW: report wrong input under its own status and word."
    )
