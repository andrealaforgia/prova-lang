"""An integer beyond the 64-bit range goes into the artefact and comes
back exact.

A CONTROL of this delivery: measured before any code was written, the
built artefact already reads and writes arbitrary-precision integers.
It is asserted all the same, because SPEC.md makes it a requirement of
the boundary -- transport must preserve arbitrary-precision integers,
and passing a number through binary floating point would violate
integer semantics -- and because nothing else in this delivery would
notice if a later change rounded a number.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

import pytest

from _f22_fixtures import evaluate, run_artefact
from _f23_fixtures import (
    ANSWERED,
    MALFORMED,
    an_artefact_of,
    first_line_word,
)

A = "=>"

# A program that hands its argument back, and one that doubles it: the
# first says what a number loses between going in and coming out, the
# second says that a number computed from it is exact too. Neither
# promises anything, so every obligation each owes is settled by a rule
# of core-0 and the whole of each is shown.
THE_NUMBERS_IN_AND_OUT = f"""(deftype Holding (record (held Int)))

(defn echo
  (sig ((n Int)) -> Int ! pure)
  (examples (example (echo 1) {A} 1))
  n)

(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 1) {A} 2))
  (* 2 n))

(defn held
  (sig ((h Holding)) -> Int ! pure)
  (examples (example (held (Holding 1)) {A} 1))
  (.held h))
"""

# Numbers on both sides of the two thresholds a reader of a generated
# module might reasonably fear: 2^53, where a binary double stops
# counting by ones, and 2^63, where a machine word of 64 bits stops.
BEYOND_64_BITS = (
    2**63,
    2**63 + 7,
    -(2**63) - 7,
    2**64 + 1,
    2**127 - 1,
    2**200 + 12345,
    -(2**200) - 12345,
)
WITHIN_64_BITS_BEYOND_A_DOUBLE = (2**53 + 1, -(2**53) - 1)


@pytest.fixture(scope="module")
def three_artefacts():
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        yield {
            entry: an_artefact_of(THE_NUMBERS_IN_AND_OUT, entry, destination)
            for entry in ("echo", "doubled", "held")
        }


def test_an_integer_beyond_the_64_bit_range_comes_back_exact(three_artefacts):
    """Given a built artefact that hands its argument back, when it is
    run over nine integers outside the 64-bit range and outside what a
    binary double counts by ones, and then over two texts that are not
    integers of this language, then each number comes back digit for
    digit, and each text that is not a number is refused as malformed
    with no result value.

    `1_0` is ten to Python's own reader and nothing at all to this
    language; `7.5` is no integer either. A number that cannot be read
    and a number read wrongly are the two ways a round trip is lost, so
    both halves stand here.

    still passes if: the artefact had printed a rounded number for the
    largest cases only -- every number is asserted digit for digit, and
    2^53+1 and 2^63+7 are the two a rounding would lose first.
    """
    numbers = BEYOND_64_BITS + WITHIN_64_BITS_BEYOND_A_DOUBLE
    answers = {}
    for number in numbers:
        ran = run_artefact(three_artefacts["echo"], [str(number)])
        assert ran.returncode == ANSWERED, (
            f"WHAT: the artefact exited {ran.returncode} over the integer "
            f"{number}. "
            "WHY: an integer of core-0 is a whole number of any size; the "
            "boundary must carry it rather than refuse it. "
            f"HOW: read what it printed: {ran.stderr[-300:]!r}"
        )
        assert "Traceback" not in ran.stderr, ran.stderr[-300:]
        answers[number] = ran.stdout.strip()

    assert answers == {number: str(number) for number in numbers}, (
        f"WHAT: the artefact answered {answers} for {len(numbers)} integers "
        "outside the 64-bit range. "
        "WHY: SPEC.md requires the boundary to preserve arbitrary-precision "
        "integers; a number that comes back changed has been through "
        "something that is not integer arithmetic. "
        "HOW: read and write the number as its digits, never as a float."
    )

    refused = {}
    for written in ("1_0", "7.5"):
        ran = run_artefact(three_artefacts["echo"], [written])
        refused[written] = (
            ran.returncode,
            first_line_word(ran),
            ran.stdout.strip(),
        )
        assert "Traceback" not in ran.stderr, ran.stderr[-300:]

    assert refused == {
        written: (MALFORMED, "MALFORMED", "") for written in ("1_0", "7.5")
    }, (
        f"WHAT: the two texts that are not integers of this language were "
        f"answered with {refused}. "
        "WHY: a round trip is lost either by a number read wrongly or by a "
        "text read as a number it is not; `1_0` is ten to Python's reader and "
        "nothing to this language, and the refusal must say that the text "
        "could not be read rather than that it was of the wrong type. "
        "HOW: read an integer by the grammar the compiler reads one with."
    )


def test_an_integer_beyond_64_bits_is_computed_with_exactly(three_artefacts):
    """Given built artefacts that double a number and that read one out
    of a record, when each is run over 2^200 + 12345, then the doubling
    answers twice that number exactly and the record hands back exactly
    what it held; and the compiler answers the same for both calls."""
    number = 2**200 + 12345

    doubled = run_artefact(three_artefacts["doubled"], [str(number)])
    assert doubled.stdout.strip() == str(2 * number), (
        f"WHAT: doubling {number} answered {doubled.stdout.strip()[:60]!r}..., "
        f"and twice that number is {2 * number}. "
        "WHY: a number computed inside the artefact is exact too, not only "
        "one that passes through it. "
        f"HOW: read what it printed: {doubled.stderr[-300:]!r}"
    )

    held = run_artefact(three_artefacts["held"], [f"(Holding {number})"])
    assert held.stdout.strip() == str(number), (
        f"WHAT: the record holding {number} answered "
        f"{held.stdout.strip()[:60]!r}... "
        "WHY: a field of a record carries an integer as exactly as an "
        "argument does. "
        f"HOW: read what it printed: {held.stderr[-300:]!r}"
    )

    by_the_compiler = evaluate(THE_NUMBERS_IN_AND_OUT, "doubled", [str(number)])
    assert (by_the_compiler.get("result") or {}).get("value") == str(2 * number), (
        f"WHAT: the compiler answered "
        f"{(by_the_compiler.get('result') or {}).get('value')!r} for the same "
        "call. "
        "WHY: the compiler and what it builds answer one arithmetic. "
        f"HOW: inspect the answer: {by_the_compiler}"
    )
