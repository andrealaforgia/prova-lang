"""F25 criteria 1, 4 and 5 over the thinnest machine there is: a counter
that counts up and accepts every count. The Owner writes the program in
ordinary core-0, writes a descriptor naming the five roles, hands the
tool both, and is told that each role resolves to a checked function of
the shape its role needs, in the version of the descriptor shape the
descriptor was written in.

The thinnest whole path of this feature, written so that it depends on
nothing this repository ships: the program and the descriptor are here.

The law: a descriptor whose five roles and three types resolve in the
submitted program is confirmed, with the version it was read in.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool answered 'completed' for anything it was sent.
The second case sends the same program with the descriptor naming the
step for the initialiser and requires that one to be refused.
"""

from __future__ import annotations

import json
import subprocess

# A counter with one event: it counts up and accepts every count. Every
# part of it is ordinary core-0, which is what criterion 5 promises.
A_COUNTER = """\
(deftype Counter (record (held Int)))
(deftype Event (union (Count)))
(deftype Outcome (record (state Counter) (accepted Bool)))

(defn sound
  (sig ((current Counter)) -> Bool ! pure)
  (examples
    (example (sound (Counter 0)) => true)
    (example (sound (Counter -1)) => false))
  (>= (.held current) 0))

(defn empty-counter
  (sig () -> Counter ! pure)
  (ensures (sound result))
  (examples (example (empty-counter) => (Counter 0)))
  (Counter 0))

(defn count-one
  (sig ((current Counter) (event Event)) -> Outcome ! pure)
  (requires (sound current))
  (ensures (sound (.state result)))
  (examples
    (example (count-one (Counter 0) (Count)) => (Outcome (Counter 1) true))
    (example (count-one (Counter 7) (Count)) => (Outcome (Counter 8) true)))
  (match event ((Count) (Outcome (Counter (+ (.held current) 1)) true))))

(defn counted-state
  (sig ((produced Outcome)) -> Counter ! pure)
  (examples (example (counted-state (Outcome (Counter 1) true)) => (Counter 1)))
  (.state produced))

(defn any-count
  (sig ((current Counter) (event Event)) -> Bool ! pure)
  (examples (example (any-count (Counter 0) (Count)) => true))
  true)
"""

A_DESCRIPTOR_FOR_THE_COUNTER = {
    "schema": "machine-descriptor/1",
    "types": {"state": "Counter", "event": "Event", "outcome": "Outcome"},
    "roles": {
        "init": "empty-counter",
        "step": "count-one",
        "state-of": "counted-state",
        "admissible": "any-count",
        "invariant": "sound",
    },
    "assumptions": [
        "The runtime applies one count at a time over one authoritative counter."
    ],
}

THE_SHAPE_OF_EACH_ROLE = {
    "state": "Counter",
    "event": "Event",
    "outcome": "Outcome",
    "init": "empty-counter",
    "step": "count-one",
    "state-of": "counted-state",
    "admissible": "any-count",
    "invariant": "sound",
}


def _ask_about_the_counter(descriptor: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(
            {"operation": "machine", "source": A_COUNTER, "descriptor": descriptor}
        ),
        capture_output=True,
        text=True,
        timeout=20.0,
    )
    assert proc.returncode == 0, (
        f"WHAT: the tool exited {proc.returncode}: stderr={proc.stderr!r}. "
        "WHY: the tool answers every request and never ends in a traceback. "
        "HOW: read the standard error above."
    )
    return json.loads(proc.stdout)


def test_the_owner_is_told_that_the_five_roles_of_a_counter_resolve():
    """Given a counter written in ordinary core-0 and a descriptor naming
    its initialiser, step, projection, admissibility predicate and
    invariant, when the Owner hands the tool both, then the answer
    confirms all eight parts with the names the descriptor gave them, and
    records that the descriptor was read in version
    `machine-descriptor/1`."""
    answer = _ask_about_the_counter(A_DESCRIPTOR_FOR_THE_COUNTER)

    assert answer.get("status") == "completed", (
        f"WHAT: the counter's descriptor was answered {answer.get('status')!r}: "
        f"{answer}. "
        "WHY: criterion 1 promises that a descriptor naming five functions "
        "that exist and have the required shapes is accepted. "
        "HOW: read the refusals above."
    )
    result = answer.get("result") or {}
    assert result.get("schema") == "machine-descriptor/1", (
        f"WHAT: the answer records the descriptor version "
        f"{result.get('schema')!r}: {answer}. "
        "WHY: criterion 4 promises the schema version is recorded in the "
        "answer. HOW: record the version read from the descriptor."
    )
    resolved = {
        role: entry.get("named") for role, entry in (result.get("roles") or {}).items()
    }
    assert resolved == THE_SHAPE_OF_EACH_ROLE, (
        f"WHAT: the answer resolves {resolved}, and the descriptor names "
        f"{THE_SHAPE_OF_EACH_ROLE}. "
        "WHY: the Owner reads the answer against the descriptor written; a "
        "part missing from it is a part nothing was said about. "
        "HOW: report one entry per part of the descriptor."
    )


def test_a_counter_whose_initialiser_is_the_step_is_refused_naming_that_role():
    """Given the same counter and a descriptor naming the step function as
    the initialiser, which takes a counter and an event rather than
    nothing, when the Owner hands the tool both, then it is refused and
    the refusal names the initialiser."""
    descriptor = json.loads(json.dumps(A_DESCRIPTOR_FOR_THE_COUNTER))
    descriptor["roles"]["init"] = "count-one"

    answer = _ask_about_the_counter(descriptor)

    assert answer.get("status") != "completed", (
        f"WHAT: a descriptor whose initialiser names a function taking a "
        f"counter and an event was accepted: {answer}. "
        "WHY: criterion 2 promises that a function with the wrong argument "
        "or result types is refused. "
        "HOW: read the shape the initialiser role needs."
    )
    named = [d.get("role") for d in (answer.get("diagnostics") or [])]
    assert "init" in named, (
        f"WHAT: the refusal names {named}, not the initialiser: {answer}. "
        "WHY: criterion 2 promises that the diagnostic names the role. "
        "HOW: carry the role in the refusal."
    )
