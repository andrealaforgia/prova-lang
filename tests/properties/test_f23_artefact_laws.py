"""The two laws F23 reads over generated input.

LAW1: for every state of the declared type and every event, the built
artefact answers exactly what the compiler answers, or -- where the
compiler gives no value because the entry's precondition refuses the
state -- refuses with the status of an unmet precondition and no result
value. It never reports an assurance failure, and never a traceback.

LAW3: every refusal a built artefact gives opens with exactly one
category word the tool publishes, and exits with the status published
for that word.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import sys

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "acceptance"))

from _f22_fixtures import evaluate, run_artefact  # noqa: E402
from _f23_fixtures import (  # noqa: E402
    ANSWERED,
    ASSURANCE_FAILURE,
    PRECONDITION_UNMET,
    THE_REFUSALS,
    an_artefact_of,
    first_line_word,
    reservation_source,
    the_published_table,
)

THE_WORDS = {word: status for word, status, _ in THE_REFUSALS}


@pytest.fixture(scope="module")
def the_built_component(tmp_path_factory):
    """One artefact of SPEC.md's reservation component, built once for
    every case these laws are read over."""
    return an_artefact_of(
        reservation_source(), "step", tmp_path_factory.mktemp("f23")
    )


@settings(derandomize=True, max_examples=16, deadline=None)
@given(
    count=st.integers(min_value=-3, max_value=5),
    event=st.sampled_from(("Reserve", "Release")),
)
def test_the_artefact_answers_a_state_as_the_compiler_does_or_refuses_it(
    the_built_component, count, event
):
    """LAW1: for every count from -3 to 5 and both events, the artefact
    and the compiler answer the same value, or the compiler gives no
    value and the artefact refuses the state as outside the entry's
    precondition, with nothing on standard output.

    still passes if: both sides had been wrong in the same way -- the
    six rows of SPEC.md's table are asserted against the document in
    tests/acceptance/test_f23_b2.
    """
    arguments = [f"(Reservation {count})", f"({event})"]
    source = reservation_source()

    by_the_compiler = evaluate(source, "step", arguments)
    value = (by_the_compiler.get("result") or {}).get("value")
    ran = run_artefact(the_built_component, arguments)

    assert "Traceback" not in ran.stderr, (
        f"WHAT: the artefact ended in a traceback over {arguments}: "
        f"{ran.stderr[-400:]!r}. "
        "WHY: an artefact answers or refuses in words, never in a traceback. "
        "HOW: refuse by name where the failure happens."
    )

    if value is not None:
        assert (ran.returncode, ran.stdout.strip()) == (ANSWERED, value), (
            f"WHAT: the compiler answers {value!r} for {arguments} and the "
            f"artefact exited {ran.returncode} answering "
            f"{ran.stdout.strip()!r}. "
            "WHY: SPEC.md requires parsing, checking, encoding, examples and "
            "generated execution to implement the same semantics. "
            f"HOW: read the refusal: {ran.stderr[-300:]!r}"
        )
        return

    assert ran.returncode == PRECONDITION_UNMET, (
        f"WHAT: the compiler gives no value for {arguments} "
        f"({by_the_compiler.get('status')!r}) and the artefact exited "
        f"{ran.returncode}, not {PRECONDITION_UNMET}. "
        "WHY: a state the entry's precondition refuses is a rejection of the "
        "input, under a status of its own; answering it would promise more "
        "than the program, and reporting an assurance failure would say a "
        "verified program broke its own promise. "
        f"HOW: read what it printed: stdout={ran.stdout[-200:]!r} "
        f"stderr={ran.stderr[-300:]!r}"
    )
    assert ran.returncode != ASSURANCE_FAILURE, ran.stderr[-300:]
    assert ran.stdout.strip() == "", (
        f"WHAT: the artefact printed {ran.stdout[:160]!r} for {arguments}, "
        "which its precondition refuses. "
        "WHY: a rejection has no successful return value. "
        "HOW: decide the refusal before anything is written."
    )
    assert first_line_word(ran) == "PRECONDITION", (
        f"WHAT: the refusal of {arguments} opens with "
        f"{first_line_word(ran)!r}: {ran.stderr[:200]!r}. "
        "WHY: a reader sorts refusals by the word on the first line. "
        "HOW: write the category word first."
    )


def _an_input_of_the_kind(kind: str, number: int, flag: bool) -> str:
    """One first argument of the kind `kind`, built so that it is of
    that kind by construction rather than by filtering."""
    if kind == "malformed":
        # Text no reader of this language settles on a value: an
        # unclosed value, a word that is not one, and two values where
        # one is taken.
        return (
            f"(Reservation {number}"
            if flag
            else f"(Reservation {number}) (Reservation {number})"
        )
    if kind == "ill-typed":
        # A value this program's own reader settles, of a type the entry
        # does not declare: a number, a flag, or an event.
        return str(number) if flag else ("true" if number % 2 else "(Reserve)")
    # A well-formed state of the declared type that the entry's
    # precondition refuses: the capacity is 2 and no count is negative.
    return f"(Reservation {3 + abs(number)})" if flag else f"(Reservation {-1 - abs(number)})"


@settings(derandomize=True, max_examples=18, deadline=None)
@given(
    kind=st.sampled_from(("malformed", "ill-typed", "precondition")),
    number=st.integers(min_value=0, max_value=40),
    flag=st.booleans(),
)
def test_every_refusal_carries_a_published_word_and_its_published_status(
    the_built_component, kind, number, flag
):
    """LAW3: for every input of each of the three kinds, the refusal
    opens with one word the tool publishes, exits with the status that
    word is published with, prints no answer and shows no traceback.

    still passes if: every kind had carried one word -- the word of each
    kind is pinned in tests/acceptance/test_f23_b4, and the three are
    required there to differ.
    """
    published = the_published_table()
    written = _an_input_of_the_kind(kind, number, flag)
    ran = run_artefact(the_built_component, [written, "(Reserve)"])

    assert ran.returncode != ANSWERED, (
        f"WHAT: the artefact answered {ran.stdout.strip()!r} for the "
        f"{kind} first argument {written!r}. "
        "WHY: none of the three kinds is input this artefact answers. "
        f"HOW: read the artefact's boundary: {ran.stderr[-300:]!r}"
    )
    assert "Traceback" not in ran.stderr, ran.stderr[-400:]
    assert ran.stdout.strip() == "", (
        f"WHAT: the artefact printed {ran.stdout[:160]!r} while refusing "
        f"{written!r}. "
        "WHY: a refusal has no result value. "
        "HOW: write the refusal on the error channel only."
    )

    word = first_line_word(ran)
    assert word in published and word in THE_WORDS, (
        f"WHAT: the {kind} argument {written!r} was refused with the word "
        f"{word!r}; the tool publishes {sorted(published)}. "
        "WHY: a client reads the vocabulary of every refusal from the tool. "
        f"HOW: publish the word or stop using it: {ran.stderr[:200]!r}"
    )
    assert published[word].get("exit_status") == ran.returncode == THE_WORDS[word], (
        f"WHAT: {written!r} was refused with the word {word!r} and the "
        f"status {ran.returncode}; the tool publishes "
        f"{published[word].get('exit_status')!r} for it and this delivery "
        f"decided {THE_WORDS[word]}. "
        "WHY: the number a caller branches on is the number the tool "
        "publishes. "
        "HOW: write the artefact's statuses from the one published table."
    )
