"""Laws the answer about a driven machine obeys for any state and any
sequence of events, not only the ones F27's acceptance tests send.

LAW1 an answer about a run claims nothing about a host that would carry
     the events: no text of it speaks of atomicity, delivery, ordering
     across hosts or anything eventually happening. The assumptions the
     descriptor states are the Owner's own sentences, carried as stated,
     and the one block whose work is to disclaim is read apart: it must
     say that the answer settles nothing of the kind.
LAW2 a boundary rejection ends the run and moves nothing: it is the last
     entry, the state after it is the state before it, the stop names its
     position, and no event after it is run.
LAW3 driving a sequence in one request is driving it event by event: the
     entries of one request are the entries of the one-event requests
     that feed each published state into the next.

Drives the `prova` command over its JSON stdin/stdout surface, as the
other property tests here do. No imports from src/prova.

Derandomised with a bounded example count, so the verdict does not
depend on which cases Hypothesis happens to draw.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess

from hypothesis import given, settings
from hypothesis import strategies as st

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"

THE_OPERATION = "step"
A_TRANSITION = "transition"
A_BOUNDARY_REJECTION = "boundary_rejection"

# Spoken of a run of a machine, these words would claim something this
# operation does not establish: it says what the named functions answered
# for the state and the events it was sent, inside one run of this tool,
# and nothing about a host that would carry those events.
A_CLAIM_THIS_OPERATION_DOES_NOT_MAKE = re.compile(
    r"\b(atomic|atomically|atomicity|deliver|delivers|delivered|delivery|"
    r"liveness|eventually|guarantee|guarantees|guaranteed|"
    r"exactly.once|at.least.once|ordering)\b",
    re.IGNORECASE,
)

# The two blocks read apart from every other text of the answer: the
# sentences the descriptor states, which are the Owner's own and are
# carried as stated, and the block whose whole work is to say what the
# answer does not settle.
THE_STATED_ASSUMPTIONS = "assumptions_stated"
THE_DISCLAIMER = "what_this_says"

AN_EVENT = st.sampled_from(("(Reserve)", "(Release)"))
A_SEQUENCE = st.lists(AN_EVENT, min_size=1, max_size=3)
# 0, 1 and 2 are the states the component's invariant holds at; 3 is one
# it excludes, so the generated cases include the refusal too.
A_RESERVED_COUNT = st.integers(min_value=0, max_value=3)

THE_SHIPPED_ADMISSIBILITY = """(defn admissible
  (sig ((current Reservation) (event Event)) -> Bool ! pure)
  (examples
    (example (admissible (Reservation 0) (Reserve)) => true)
    (example (admissible (Reservation 2) (Release)) => true))
  true)"""

A_NARROWER_ADMISSIBILITY = """(defn admissible
  (sig ((current Reservation) (event Event)) -> Bool ! pure)
  (examples
    (example (admissible (Reservation 0) (Reserve)) => true)
    (example (admissible (Reservation 2) (Reserve)) => false))
  (match event
    ((Reserve) (< (.reserved current) 2))
    ((Release) (> (.reserved current) 0))))"""


def _source(admits: str) -> str:
    shipped = (EXAMPLES / "reservation.machine.prova").read_text(encoding="utf-8")
    assert THE_SHIPPED_ADMISSIBILITY in shipped, (
        "WHAT: examples/reservation.machine.prova no longer declares the "
        "admissibility predicate these laws narrow. WHY: the laws are read "
        "over the shipped component with one function replaced. HOW: update "
        "A_NARROWER_ADMISSIBILITY in this file."
    )
    return shipped.replace(THE_SHIPPED_ADMISSIBILITY, admits)


def _descriptor() -> dict:
    return json.loads(
        (EXAMPLES / "reservation.machine.json").read_text(encoding="utf-8")
    )


def _drive(source: str, state: str, events: list) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(
            {
                "operation": THE_OPERATION,
                "source": source,
                "descriptor": _descriptor(),
                "state": state,
                "events": events,
            }
        ),
        capture_output=True,
        text=True,
        timeout=30.0,
    )
    assert proc.returncode == 0, (
        f"WHAT: the tool exited {proc.returncode}: stderr={proc.stderr!r}. "
        "WHY: the tool answers every request and never ends in a traceback. "
        "HOW: read the standard error above."
    )
    return json.loads(proc.stdout)


def _texts_outside(value: object, apart: tuple[str, ...]) -> list:
    """Every text the answer carries, except the ones standing under the
    names read apart."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        found: list = []
        for key, held in value.items():
            if key in apart:
                continue
            found += _texts_outside(held, apart)
        return found
    if isinstance(value, list):
        return [text for held in value for text in _texts_outside(held, apart)]
    return []


def _entries(answer: dict) -> list:
    return ((answer.get("result") or {}).get("transitions")) or []


def _comparable(entry: dict) -> tuple:
    """One entry as the composition law compares it: everything it says
    except which place in its own request it stood at."""
    return (
        entry.get("result"),
        entry.get("event"),
        entry.get("state_before"),
        entry.get("state_after"),
        entry.get("outcome"),
    )


@given(reserved=A_RESERVED_COUNT, events=A_SEQUENCE)
@settings(max_examples=10, deadline=None, derandomize=True)
def test_an_answer_about_a_run_claims_nothing_about_a_host(reserved, events):
    """LAW1 -- no text of an answer about a run claims host atomicity,
    delivery, ordering across hosts or that anything eventually
    happens."""
    answer = _drive(_source(A_NARROWER_ADMISSIBILITY), f"(Reservation {reserved})", events)

    overclaimed = [
        text
        for text in _texts_outside(answer, (THE_STATED_ASSUMPTIONS, THE_DISCLAIMER))
        if A_CLAIM_THIS_OPERATION_DOES_NOT_MAKE.search(text)
    ]
    assert overclaimed == [], (
        f"WHAT: the answer carries {overclaimed}. "
        "WHY: this operation says what the named functions answered for the "
        "state and the events it was sent; a host that would carry those "
        "events is not modelled here, and a caller refuses an answer whose "
        "text claims it is. HOW: write the answer in the words of what ran."
    )
    assert answer.get("status") in ("completed", "invalid_input"), (
        f"WHAT: the run was answered {answer.get('status')!r}: {answer}. "
        "WHY: a state the invariant holds at is driven and one it excludes "
        "is refused; any other status means nothing was driven at all. "
        "HOW: answer the run."
    )
    if answer.get("status") != "completed":
        return
    disclaimed = (answer.get("result") or {}).get(THE_DISCLAIMER) or ""
    assert "settles nothing" in disclaimed, (
        f"WHAT: the block that says what this answer does not settle reads "
        f"{disclaimed!r}. "
        "WHY: the Owner must read, in the answer itself, that evidence "
        "about a machine is conditional on the model and that a host "
        "carrying these events is not part of it. "
        "HOW: say what the answer settles nothing about."
    )


@given(reserved=st.integers(min_value=0, max_value=2), events=A_SEQUENCE)
@settings(max_examples=10, deadline=None, derandomize=True)
def test_a_boundary_rejection_ends_the_run_and_moves_nothing(reserved, events):
    """LAW2 -- an event outside the admissible domain is the last entry
    of the run, leaves the state as it was and names its position."""
    answer = _drive(_source(A_NARROWER_ADMISSIBILITY), f"(Reservation {reserved})", events)

    entries = _entries(answer)
    assert entries, (
        f"WHAT: driving {len(events)} events from {reserved} reserved "
        f"published no entry at all: {answer}. "
        "WHY: every event sent is either driven or refused, and the Owner "
        "reads one entry per event up to the stop. HOW: publish them."
    )
    assert [entry.get("position") for entry in entries] == list(
        range(1, len(entries) + 1)
    ), (
        f"WHAT: the entries stand at "
        f"{[entry.get('position') for entry in entries]}. "
        "WHY: the positions are the places of the events in the request, in "
        "order. HOW: number them from 1."
    )
    refused = [
        entry for entry in entries if entry.get("result") == A_BOUNDARY_REJECTION
    ]
    if not refused:
        assert len(entries) == len(events), (
            f"WHAT: {len(entries)} of the {len(events)} events sent were "
            f"driven and none was refused at the boundary: {entries}. "
            "WHY: a run with no refusal drives every event it was sent. "
            "HOW: drive them all."
        )
        return
    assert refused[0] is entries[-1], (
        f"WHAT: an event was refused at the boundary and the run went on: "
        f"{entries}. "
        "WHY: the chosen behaviour is to stop at a boundary rejection with "
        "the position named. HOW: stop there."
    )
    assert refused[0].get("state_before") == refused[0].get("state_after"), (
        f"WHAT: the refused event moved the state from "
        f"{refused[0].get('state_before')!r} to "
        f"{refused[0].get('state_after')!r}. "
        "WHY: an event outside the admissible domain leaves the state "
        "unchanged. HOW: publish the state it came in with."
    )
    stopped = (answer.get("result") or {}).get("stopped_at") or {}
    assert stopped.get("position") == refused[0].get("position"), (
        f"WHAT: the run says it stopped at {stopped!r} and the refused "
        f"event stands at {refused[0].get('position')!r}. "
        "WHY: the Owner reads which event to send again from the stop. "
        "HOW: name the position of the entry that stopped the run."
    )
    assert stopped.get("events_not_run") == len(events) - len(entries), (
        f"WHAT: the stop says {stopped.get('events_not_run')!r} events were "
        f"not run, and {len(events) - len(entries)} of the {len(events)} "
        f"sent stand after the stop: {stopped}. "
        "WHY: an Owner who cannot count what was left behind cannot resume. "
        "HOW: count the events after the stop."
    )


@given(reserved=st.integers(min_value=0, max_value=2), events=A_SEQUENCE)
@settings(max_examples=6, deadline=None, derandomize=True)
def test_one_request_drives_what_the_one_event_requests_drive(reserved, events):
    """LAW3 -- a sequence driven in one request answers exactly what the
    same events answer one request at a time, each from the state the
    one before it published."""
    source = _source(A_NARROWER_ADMISSIBILITY)
    together = _drive(source, f"(Reservation {reserved})", events)

    apart: list = []
    state = f"(Reservation {reserved})"
    for event in events:
        answer = _drive(source, state, [event])
        entry = _entries(answer)[0]
        apart.append(entry)
        if entry.get("result") != A_TRANSITION:
            break
        state = (answer.get("result") or {}).get("state_now")

    assert _entries(together), (
        f"WHAT: driving {events} in one request published no entry: "
        f"{together}. "
        "WHY: the law compares two runs, so the run under it must have "
        "driven something. HOW: publish the entries."
    )
    assert [_comparable(entry) for entry in _entries(together)] == [
        _comparable(entry) for entry in apart
    ], (
        f"WHAT: one request answered "
        f"{[_comparable(entry) for entry in _entries(together)]} and the "
        f"same events answered {[_comparable(entry) for entry in apart]} one "
        "at a time. "
        "WHY: criterion 4 promises each transition uses the state the "
        "previous one published, which is exactly what the Owner does by "
        "hand between two requests; the two must not disagree. "
        "HOW: drive each event from the state the previous one published."
    )
    assert (together.get("result") or {}).get("state_now") == (
        apart[-1].get("state_after")
    ), (
        f"WHAT: one request left the component at "
        f"{(together.get('result') or {}).get('state_now')!r} and the "
        f"one-at-a-time runs left it at {apart[-1].get('state_after')!r}. "
        "WHY: the Owner resumes from the published state whichever way they "
        "drove the events. HOW: publish the state the last entry reached."
    )
