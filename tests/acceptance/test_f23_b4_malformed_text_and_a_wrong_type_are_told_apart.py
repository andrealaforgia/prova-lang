"""A refusal says which kind of wrong input it is about: text that
cannot be read as a value at all, a value read but of a type the entry
does not declare, or a value of the declared type that the entry's
precondition refuses.

SPEC.md asks a conformance check to reject malformed values and invalid
entry states, and keeps those apart from an assurance failure. Before
this delivery the first two were one exit status and the third carried
the status of an assurance failure, so a caller could not tell from the
status whether they had mistyped a value, sent the wrong kind of value,
or sent a state the program promises nothing about.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from _f22_fixtures import run_artefact
from _f23_fixtures import (
    ILL_TYPED,
    MALFORMED,
    PRECONDITION_UNMET,
    an_artefact_of,
    first_line_word,
    reservation_source,
)

# Each case: what the Owner sent, the kind of wrongness it is, and what
# the refusal must name. The three kinds are the three the request
# distinguishes at the boundary of a built artefact.
CASES = (
    ("(Reserv", "malformed", "MALFORMED", MALFORMED, "(Reserv"),
    ("oops", "malformed", "MALFORMED", MALFORMED, "oops"),
    ("", "malformed", "MALFORMED", MALFORMED, "argument 1"),
    ("(Reservation 1) (Reservation 2)", "malformed", "MALFORMED", MALFORMED,
     "argument 1"),
    ("(Reservation)", "malformed", "MALFORMED", MALFORMED, "Reservation"),
    ("(Clock 1)", "malformed", "MALFORMED", MALFORMED, "Clock"),
    ("(Reserve)", "ill-typed", "ILL-TYPED", ILL_TYPED, "Reservation"),
    ("7", "ill-typed", "ILL-TYPED", ILL_TYPED, "Reservation"),
    ("true", "ill-typed", "ILL-TYPED", ILL_TYPED, "Reservation"),
    ("(Reservation true)", "ill-typed", "ILL-TYPED", ILL_TYPED, "reserved"),
    ("(Reservation 5)", "outside the precondition", "PRECONDITION",
     PRECONDITION_UNMET, "valid-state"),
)


@pytest.fixture(scope="module")
def the_built_component():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield an_artefact_of(
            reservation_source(), "step", pathlib.Path(tmp_dir)
        )


def test_malformed_text_and_a_value_of_the_wrong_type_are_told_apart(
    the_built_component,
):
    """Given the built reservation component, when it is run over eleven
    first arguments -- six that cannot be read as a value, four that
    read as a value of another type, and one well-formed state the
    precondition refuses -- then each refusal carries the exit status
    and the first-line word of its own kind, the three statuses differ
    from one another, no refusal prints an answer, and none ends in a
    traceback.

    still passes if: every refusal had carried one status -- the three
    statuses are required to differ, and each case is required to carry
    the status of its own kind.
    """
    seen = {}
    for written, kind, word, status, named in CASES:
        ran = run_artefact(the_built_component, [written, "(Reserve)"])

        assert ran.returncode == status, (
            f"WHAT: the first argument {written!r} is {kind} and the "
            f"artefact exited {ran.returncode}, not {status}. "
            "WHY: a caller reads from the status which of the three things "
            "they got wrong: text that is not a value, a value of the wrong "
            "type, or a state the program promises nothing about. "
            f"HOW: read what it printed: stderr={ran.stderr[-400:]!r}"
        )
        assert first_line_word(ran) == word, (
            f"WHAT: the refusal of {written!r} opens with "
            f"{first_line_word(ran)!r} and not {word!r}: "
            f"{ran.stderr[:200]!r}. "
            "WHY: a reader sorts refusals by the category word on the first "
            "line, before any prose. "
            "HOW: write the category word first on the first line."
        )
        assert ran.stdout.strip() == "", (
            f"WHAT: the artefact printed {ran.stdout[:160]!r} as an answer "
            f"to {written!r}, which it refused. "
            "WHY: a refusal has no result value. "
            "HOW: write the refusal on the error channel only."
        )
        assert "Traceback" not in ran.stderr, (
            f"WHAT: the artefact ended in a traceback over {written!r}: "
            f"{ran.stderr[-400:]!r}. "
            "WHY: an artefact never ends in a Python traceback. "
            "HOW: refuse by name where the failure happens."
        )
        assert named in ran.stderr, (
            f"WHAT: the refusal of {written!r} does not name {named!r}: "
            f"{ran.stderr[-400:]!r}. "
            "WHY: a refusal names the value, the parameter and the declared "
            "type it is about, so the caller knows what to repair. "
            "HOW: name all three in the message."
        )
        seen.setdefault(kind, set()).add((word, ran.returncode))

    assert {kind: len(statuses) for kind, statuses in seen.items()} == {
        "malformed": 1,
        "ill-typed": 1,
        "outside the precondition": 1,
    }, (
        f"WHAT: the eleven cases were answered with {seen}. "
        "WHY: one status and one word per kind of wrong input; a kind that "
        "answers with two statuses cannot be read by a caller. "
        "HOW: give each kind one refusal of its own."
    )
    statuses = {status for pairs in seen.values() for _, status in pairs}
    assert len(statuses) == len(seen), (
        f"WHAT: the three kinds of wrong input carry the statuses "
        f"{sorted(statuses)}: {seen}. "
        "WHY: malformed text, a value of the wrong type and a state outside "
        "the precondition are three different repairs, so a caller must be "
        "able to tell them apart by the status alone. "
        "HOW: give each kind a stable exit status of its own."
    )
