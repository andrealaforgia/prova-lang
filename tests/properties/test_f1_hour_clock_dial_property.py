"""Property for F1's broad law: the hour clock this repository ships accepts
a tick from an hour on its dial and refuses one from any hour off it.

The dial has twelve hours, but the law quantifies over every integer a
caller can hand the clock, so it is generated rather than tabulated. No
example the shipped file declares, and no fixed case in the acceptance
tests, observes a refusal: the clock's four declared examples of its own
state check only ask whether an hour is on the dial, they never tick from
one that is not. An edit that drops the clock's entry condition would keep
every declared example passing; this property is what notices.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.
"""

from __future__ import annotations

import pathlib

from hypothesis import example, given, settings
from hypothesis import strategies as st

from _prova_client import run_prova

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SHIPPED_CLOCK = REPO_ROOT / "examples" / "hour-clock.prova"

FIRST_HOUR_ON_THE_DIAL = 1
LAST_HOUR_ON_THE_DIAL = 12


def load_hour_clock_source() -> str:
    """The hour clock program this repository ships.

    A missing or renamed file raises FileNotFoundError naming the path, so
    this property fails the run and is never skipped. The acceptance
    fixtures own the fuller refusal and the test that proves a run with no
    clock file fails (tests/acceptance/_hour_clock_fixtures.py).
    """
    return SHIPPED_CLOCK.read_text(encoding="utf-8")

# Hours just off each end of the dial, and hours far away from it. The first
# strategy keeps the two boundaries reachable; the second reaches hours no
# clock face has.
AN_HOUR = st.one_of(
    st.integers(min_value=-4, max_value=17),
    st.integers(min_value=-(10**9), max_value=10**9),
)


def _tick_from(source: str, hour: int) -> dict:
    _, response, raw, _ = run_prova(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": source,
            "function": "step",
            "arguments": [f"(Clock {hour})", "(Tick)"],
        }
    )
    assert response is not None, f"non-JSON response ticking from hour {hour}: {raw!r}"
    return response


@settings(max_examples=30, deadline=None)
@given(hour=AN_HOUR)
@example(hour=FIRST_HOUR_ON_THE_DIAL)
@example(hour=LAST_HOUR_ON_THE_DIAL)
@example(hour=FIRST_HOUR_ON_THE_DIAL - 1)
@example(hour=LAST_HOUR_ON_THE_DIAL + 1)
def test_the_shipped_clock_ticks_from_an_hour_on_its_dial_and_refuses_one_off_it(hour):
    """LAW2: for every hour a caller can name, a tick from an hour between 1
    and 12 produces a new hour and is accepted, and a tick from any other
    hour is refused and produces no hour at all."""
    source = load_hour_clock_source()
    on_the_dial = FIRST_HOUR_ON_THE_DIAL <= hour <= LAST_HOUR_ON_THE_DIAL

    response = _tick_from(source, hour)

    produced = (response.get("result") or {}).get("value")
    refusals = response.get("diagnostics") or []
    if on_the_dial:
        assert refusals == [] and produced is not None, (
            f"WHAT: a tick from hour {hour} was refused: {response}. "
            f"WHY: hour {hour} is on the dial, so the clock must accept the tick "
            "and show the next hour. "
            "HOW: restore the entry condition and the wrap in "
            "examples/hour-clock.prova."
        )
        assert produced.endswith(" true)"), (
            f"WHAT: a tick from hour {hour} produced {produced}, which is not "
            "accepted. "
            "WHY: every tick from an hour on the dial is promised to be accepted. "
            "HOW: repair `step` in examples/hour-clock.prova."
        )
    else:
        assert produced is None, (
            f"WHAT: a tick from hour {hour} produced {produced}. "
            f"WHY: hour {hour} is not on the dial, so the clock must refuse the "
            "tick rather than show an hour nobody can read. "
            "HOW: restore the entry condition of `step` in "
            "examples/hour-clock.prova."
        )
        assert [d.get("category") for d in refusals] == ["precondition_violation"], (
            f"WHAT: a tick from hour {hour} reported {refusals}, not one refusal of "
            "the entry condition. "
            "WHY: an hour off the dial is refused before the clock ticks, and the "
            "reason the Owner is given says exactly that. "
            "HOW: restore the entry condition of `step` in "
            "examples/hour-clock.prova."
        )
