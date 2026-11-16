"""An input offered as a counterexample says what bounded the run that
confirmed it.

F20 criterion 4: given a witness, the replay happened inside a declared
budget and the budget is stated. SPEC.md, "Results and evidence scope":
"Function witnesses must replay against the reference semantics within a
declared replay budget; failed validation yields unknown, not an invented
disproof."

F18 already runs every candidate through the evaluator and already stops
that run at the depth this tool declares, answering `unknown` when it
cannot finish. What was missing is the statement: a reader looking at a
counterexample was not told which budget the confirming run stood inside,
and so could not tell a confirmation that finished from one that was cut
short.

The number is not written twice. This test reads the limit the manifest
publishes before a request is sent, and requires the witness to name that
same limit and that same number.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

from _f18_fixtures import completed, entry_named, obligations_of, the_manifest, verify
from _reservation_fixtures import reservation_source

A = "=>"

# Adding one to a whole number does not always answer a positive number:
# at -1 it answers 0. The solver finds that input and the tool runs the
# program over it to confirm, which is the run this file is about.
A_PROGRAM_THAT_PROMISES_TOO_MUCH = f"""(defn add-one
  (sig ((n Int)) -> Int ! pure)
  (ensures (> result 0))
  (examples (example (add-one 1) {A} 2))
  (+ n 1))
"""

LABEL = "a program promising a positive answer for every whole number"
THE_FALSE_PROMISE = "body_postcondition:add-one:body"


def _published_limits() -> dict:
    limits = (
        ((the_manifest().get("result") or {}).get("resource_limits") or {}).get(
            "limits"
        )
    ) or {}
    assert limits, (
        "WHAT: the manifest publishes no resource limits. "
        "WHY: this test compares the budget a witness names with the one a "
        "caller can read before sending a request; with none published there "
        "is nothing to compare. "
        f"HOW: inspect the manifest: {the_manifest()}"
    )
    return limits


def test_a_counterexample_names_the_budget_its_replay_stood_inside():
    """Given a promise that is false at -1, when the Owner reads the
    input the answer offers, then that input is reported beside the
    budget the confirming run stood inside, and the budget is one the
    manifest publishes with the same number.

    still passes if: the tool invented a budget of its own for the
    answer -- the limit and the number are both compared with what
    `discover` publishes.
    """
    answer = completed(verify(A_PROGRAM_THAT_PROMISES_TOO_MUCH), LABEL)
    entry = entry_named(answer, THE_FALSE_PROMISE, LABEL)
    witness = entry.get("counterexample") or {}

    assert witness.get("arguments"), (
        f"WHAT: the entry carries {witness} and no input that breaks the "
        "promise. "
        "WHY: this test is about what a witness says; without one there is "
        "nothing to read. "
        f"HOW: inspect the entry: {entry}"
    )
    stated = witness.get("replayed_within")
    assert isinstance(stated, dict), (
        f"WHAT: the witness {witness} says nothing about what bounded the run "
        "that confirmed it. "
        "WHY: a reader told that an input was run through the tool and "
        "refused must be able to tell a run that finished from one that was "
        "cut short; the budget is what says so. "
        "HOW: state the budget beside the witness."
    )

    published = _published_limits()
    assert stated.get("limit") in published, (
        f"WHAT: the witness names the budget {stated.get('limit')!r} and the "
        f"manifest publishes {sorted(published)}. "
        "WHY: a budget a caller cannot look up before sending a request is "
        "not declared. "
        f"HOW: name the published limit: {stated}"
    )
    assert stated.get("maximum") == published[stated["limit"]]["maximum"], (
        f"WHAT: the witness says the replay stood inside "
        f"{stated.get('maximum')} and the manifest publishes "
        f"{published[stated['limit']]['maximum']} for that limit. "
        "WHY: one place states each number; two that disagree leave a reader "
        "with no idea which run they are reading about. "
        f"HOW: read the number from the limit this tool declares: {stated}"
    )


def test_the_reservation_example_as_it_ships_offers_no_input_at_all():
    """Given the reservation example SPEC.md publishes, unmodified, when
    the Owner verifies it, then no entry carries an input that breaks it.

    F20 criterion 5. A tool that offered a witness here would be offering
    one for a program whose every obligation it had just proved.
    """
    about = "the reservation example as SPEC.md publishes it"
    answer = completed(verify(reservation_source()), about)
    entries = obligations_of(answer, about)

    offered = [
        (entry["id"], entry["counterexample"])
        for entry in entries
        if entry.get("counterexample") is not None
    ]
    assert offered == [], (
        f"WHAT: the unmodified reservation example is answered with "
        f"{offered} as inputs that break it. "
        "WHY: every obligation of this program is discharged; an input "
        "offered as a counterexample beside that would send the Owner to "
        "chase a defect that is not there. "
        f"HOW: inspect the entries: "
        f"{[(e['id'], e['result']) for e in entries]}"
    )
