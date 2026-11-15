"""F17.B3 -- an examples run says it is an examples run and that it
reaches the examples the program declares, and nothing wider.

A reader of a passing examples run then cannot take it for a statement
about every input of the functions it ran.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the answer called itself an examples run and ran
something else. The second test counts the entries against the examples
written in the text that was sent and names the function each is about.
"""

from __future__ import annotations

from _f17_provenance_fixtures import (
    A_PROGRAM,
    answer_about,
    what_it_stands_on,
)

# The examples the sent program declares, read by hand from the text in
# the fixtures: one for each of its 2 functions, with the arguments and
# the value each one states.
THE_DECLARED_EXAMPLES = {
    ("positive", 0): (["3"], "true"),
    ("twice", 0): (["2"], "4"),
}


def _the_run() -> dict:
    return answer_about("examples", A_PROGRAM)


def test_an_examples_run_calls_itself_an_examples_run():
    """Given the 2-function program, when its examples are run, then the
    claim kind is "examples", its scope names the declared examples, and
    the answer stands on the revision of that text."""
    answer = _the_run()
    claim = answer.get("claim") or {}

    assert claim.get("kind") == "examples", (
        f"WHAT: the examples run claims {claim.get('kind')!r}. WHY: a reader "
        "of another kind of claim would take running 2 examples for a "
        "statement of that other kind. HOW: claim the kind 'examples'."
    )
    assert "declared examples" in str(claim.get("scope", "")), (
        f"WHAT: the examples run reaches {claim.get('scope')!r}. WHY: a scope "
        "that does not name the declared examples lets a reader believe more "
        "inputs than 2 were tried. HOW: write the declared examples as the "
        "scope."
    )
    what_it_stands_on(answer, "of the examples run")


def test_an_examples_run_answers_about_the_declared_examples_and_no_others():
    """Given the same program, which declares 2 examples, when they are
    run, then the answer carries exactly those 2 entries, each naming the
    function that declares it and the value that example states."""
    entries = (_the_run().get("result") or {}).get("examples") or []
    answered = {
        (entry["function"], entry["ordinal"]): (
            entry["arguments"],
            entry["expected"],
        )
        for entry in entries
    }

    assert answered == THE_DECLARED_EXAMPLES, (
        f"WHAT: the run answers about {sorted(answered)} and the program "
        f"declares {sorted(THE_DECLARED_EXAMPLES)}. WHY: an entry about "
        "anything else would be a run of something the program never asked "
        "for, under the name of its examples. HOW: run each declared example "
        "once and answer about those."
    )
    assert len(entries) == len(THE_DECLARED_EXAMPLES), (
        f"WHAT: {len(entries)} entries were answered for "
        f"{len(THE_DECLARED_EXAMPLES)} declared examples. WHY: a repeated "
        "entry would count one example twice. HOW: answer one entry per "
        "declared example."
    )
