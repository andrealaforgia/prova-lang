"""The built reservation component answers all six rows of the table
SPEC.md writes, on fresh input.

A CONTROL of this delivery: measured before any code was written, the
built component already answers the six rows. It is asserted all the
same, because it is the promise the Owner reads first, and because the
rows are the whole of the finite model SPEC.md defines.

Two of the six rows -- a reserve at count 1 and a release at count 2 --
are visited by no declared example of the component, so an artefact that
recited its examples could not answer them.

The rows are read out of SPEC.md, never copied here. Drives only the
`prova` command's real JSON stdin/stdout surface and the artefact it
writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from _f22_fixtures import run_artefact
from _f23_fixtures import (
    ANSWERED,
    PRECONDITION_UNMET,
    an_artefact_of,
    first_line_word,
    reservation_source,
)
from _f27_runtime_fixtures import the_spec_table

# The two counts just outside the invariant of this finite model: its
# capacity is 2, and no count is negative.
COUNTS_OUTSIDE_THE_MODEL = (3, -1)


@pytest.fixture(scope="module")
def the_built_component():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield an_artefact_of(
            reservation_source(), "step", pathlib.Path(tmp_dir)
        )


def test_the_document_still_defines_six_rows():
    """Given SPEC.md, when its transition table is read, then it defines
    six rows over the counts 0, 1 and 2 and the two events."""
    rows = the_spec_table()
    assert len(rows) == 6, (
        f"WHAT: SPEC.md's reservation table defines {len(rows)} rows: "
        f"{rows}. "
        "WHY: the promise is that the built component is run through all "
        "six rows of that table; a table of another size means the test "
        "below covers something else. "
        "HOW: read SPEC.md around the core conformance example."
    )
    assert {row[0] for row in rows} == {0, 1, 2}, rows
    assert {row[1] for row in rows} == {"Reserve", "Release"}, rows


def test_every_row_of_the_table_is_answered_and_every_other_count_refused(
    the_built_component,
):
    """Given the built reservation component, when it is run over the
    state and the event of each of the six rows SPEC.md defines and then
    over the two counts just outside that model, then every row is
    answered with the state after and the acceptance flag that row
    writes, and each count outside the model is refused with no result
    value under the status reserved for an unmet precondition.

    The two halves are the whole of this finite model: SPEC.md says the
    table defines all its transitions, and that a conformance check must
    also reject invalid entry states.

    still passes if: the component had answered only the four rows its
    declared examples visit -- the reserve at count 1 and the release at
    count 2 are visited by no example and are required here; and if it
    had answered a count outside the model.
    """
    rows = the_spec_table()
    answers = {}
    expected = {}
    for before, event, after, accepted in rows:
        ran = run_artefact(
            the_built_component, [f"(Reservation {before})", f"({event})"]
        )
        assert ran.returncode == ANSWERED, (
            f"WHAT: the built component exited {ran.returncode} for the row "
            f"{before} {event}, instead of answering it. "
            "WHY: every state of that table meets the entry's precondition, "
            "so every row is input the artefact answers. "
            f"HOW: read what it printed: stderr={ran.stderr[-300:]!r}"
        )
        assert "Traceback" not in ran.stderr, ran.stderr[-400:]
        answers[(before, event)] = ran.stdout.strip()
        expected[(before, event)] = (
            f"(Outcome (Reservation {after}) {accepted})"
        )

    assert answers == expected, (
        f"WHAT: the built component answered {answers} and the six rows of "
        f"SPEC.md's table write {expected}. "
        "WHY: acceptance is observable: a component that rejected everything "
        "would be safe and wrong, and a state that moved where the table "
        "says it does not is a wrong answer about a verified program. "
        f"HOW: read the artefact at {the_built_component}"
    )

    refused = {}
    for count in COUNTS_OUTSIDE_THE_MODEL:
        ran = run_artefact(
            the_built_component, [f"(Reservation {count})", "(Reserve)"]
        )
        refused[count] = (
            ran.returncode,
            first_line_word(ran),
            ran.stdout.strip(),
        )
        assert "Traceback" not in ran.stderr, ran.stderr[-400:]

    assert refused == {
        count: (PRECONDITION_UNMET, "PRECONDITION", "")
        for count in COUNTS_OUTSIDE_THE_MODEL
    }, (
        f"WHAT: the counts outside the model were answered with {refused}. "
        "WHY: the six rows are every transition of this model, so a count "
        "outside it is an invalid entry state: the refusal has no result "
        "value and carries a status of its own, apart from the one that says "
        "a contract of a verified program did not hold. "
        f"HOW: read the artefact at {the_built_component}"
    )
