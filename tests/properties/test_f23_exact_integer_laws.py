"""LAW2: an integer goes into a built artefact and comes back exact,
whatever its size.

A CONTROL law of this delivery: measured before any code was written,
the built artefact already reads and writes arbitrary-precision
integers. It is read over generated numbers all the same, because
SPEC.md makes it a requirement of the boundary -- transport must
preserve arbitrary-precision integers, and passing a number through
binary floating point would violate integer semantics -- and because a
rounding would otherwise be noticed by nothing.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import sys

import pytest
from hypothesis import example, given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "acceptance"))

from _f22_fixtures import run_artefact  # noqa: E402
from _f23_fixtures import ANSWERED, an_artefact_of  # noqa: E402

A = "=>"

# A program that hands its argument back and one that doubles it: the
# first is the round trip, the second says a number computed inside the
# artefact is exact too. Neither promises anything, so the whole of each
# is shown by a rule of core-0.
THE_ROUND_TRIP = f"""(defn echo
  (sig ((n Int)) -> Int ! pure)
  (examples (example (echo 1) {A} 1))
  n)

(defn doubled
  (sig ((n Int)) -> Int ! pure)
  (examples (example (doubled 1) {A} 2))
  (* 2 n))
"""


@pytest.fixture(scope="module")
def two_artefacts(tmp_path_factory):
    destination = tmp_path_factory.mktemp("f23-integers")
    return {
        entry: an_artefact_of(THE_ROUND_TRIP, entry, destination)
        for entry in ("echo", "doubled")
    }


@settings(derandomize=True, max_examples=14, deadline=None)
@given(number=st.integers(min_value=-(2**220), max_value=2**220))
@example(number=2**53 + 1)
@example(number=2**63)
@example(number=-(2**63) - 1)
@example(number=2**200 + 12345)
def test_an_integer_goes_in_and_comes_back_exact(two_artefacts, number):
    """LAW2: for every integer up to 2^220 in either sign, the artefact
    answers the same digits it was given, and twice that number exactly
    for the doubling entry.

    The four named cases are the thresholds a generated module might
    lose a number at: just past what a binary double counts by ones,
    and just past a machine word of 64 bits in either direction.
    """
    back = run_artefact(two_artefacts["echo"], [str(number)])
    assert (back.returncode, back.stdout.strip()) == (ANSWERED, str(number)), (
        f"WHAT: the artefact exited {back.returncode} answering "
        f"{back.stdout.strip()[:80]!r} for the integer "
        f"{str(number)[:40]}... of {len(str(number))} characters. "
        "WHY: SPEC.md requires the boundary to preserve arbitrary-precision "
        "integers; a number that comes back changed has been through "
        "something that is not integer arithmetic. "
        f"HOW: read what it printed: {back.stderr[-300:]!r}"
    )

    twice = run_artefact(two_artefacts["doubled"], [str(number)])
    assert (twice.returncode, twice.stdout.strip()) == (
        ANSWERED,
        str(2 * number),
    ), (
        f"WHAT: doubling {str(number)[:40]}... answered "
        f"{twice.stdout.strip()[:80]!r}. "
        "WHY: a number computed inside the artefact is exact too, not only "
        "one that passes through it. "
        f"HOW: read what it printed: {twice.stderr[-300:]!r}"
    )
