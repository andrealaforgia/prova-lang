"""What the answer says about where each result came from, and what the
tool publishes about the solver it requires.

Added after an independent review: the word that says whether a solver
or a rule of `core-0` settled an obligation could be swapped for the
other and nothing noticed; the answer to a program outside the fragment
was pinned nowhere; the published rule about contract definedness said
one thing could stop a run when three can; and nothing published which
solver this tool requires.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool wrote the same word on every entry. The first
test requires the two kinds a rule settles and the three a solver
settles to carry different words, read from the same answer.
"""

from __future__ import annotations

from _f18_fixtures import (
    completed,
    entry_named,
    obligations_of,
    results_by_identity,
    the_manifest,
    verify,
)

# A program whose five kinds of obligation are all in the fragment, so
# each of them is settled and each says what settled it.
EVERY_KIND = """(defn positive
  (sig ((n Int)) -> Bool ! pure)
  (examples (example (positive 3) => true))
  (> n 0))

(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (positive n))
  (ensures (= result (* n 2)))
  (examples (example (twice 2) => 4))
  (* n 2))
"""

# A program the translation does not cover: a let binding, which this
# fragment leaves for a later one.
OUTSIDE_THE_FRAGMENT = """(defn f
  (sig ((n Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (f 1) => 1))
  (let ((m n)) m))
"""

# A call reached where the callee refuses it: the solver finds an input
# that breaks the obligation, and the body it is about is a claim the
# evaluator refuses for another reason than the one this entry names.
A_CANDIDATE_THAT_DOES_NOT_REPLAY = """(defn only-big
  (sig ((y Int)) -> Int ! pure)
  (requires (> y 100))
  (ensures (> result 0))
  (examples (example (only-big 101) => 101))
  y)

(defn below
  (sig ((x Int)) -> Int ! pure)
  (ensures (>= result 0))
  (examples (example (below 101) => 0))
  (if (> x 100) 0 (only-big x)))
"""

BY_A_RULE = (
    "contract_definedness:twice:contract",
    "structural_termination:twice:calls",
)
BY_THE_SOLVER = (
    "body_postcondition:twice:body",
    "example_validity:twice:example[0]",
    "call_precondition:twice:requires[0]",
)


def test_an_entry_says_whether_a_solver_or_a_rule_settled_it():
    """Given a program whose five kinds of obligation are all settled,
    when the Owner reads the answer, then the two a rule of core-0
    settles say so and the three a solver settles say so, and the two
    words are not the same word."""
    label = "a program of all five kinds"
    answer = completed(verify(EVERY_KIND), label)

    said = {
        entry["id"]: entry.get("discharged_by")
        for entry in obligations_of(answer, label)
    }
    for identity in BY_A_RULE:
        assert said[identity] == "structure", (
            f"WHAT: {identity} says {said[identity]!r} settled it. "
            "WHY: no solver is asked about it; it rests on a rule of core-0, "
            "and a reader judging what a proved entry is worth has to see "
            "which of the two it was. "
            f"HOW: inspect the answer: {said}"
        )
    for identity in BY_THE_SOLVER:
        assert said[identity] == "solver", (
            f"WHAT: {identity} says {said[identity]!r} settled it. "
            "WHY: a solver was asked about it, and a reader told a rule "
            "settled it would look for that rule in the document and find "
            "nothing about this claim. "
            f"HOW: inspect the answer: {said}"
        )
    assert len({said[i] for i in BY_A_RULE} | {said[i] for i in BY_THE_SOLVER}) == 2


def test_the_rule_about_definedness_names_every_way_a_run_can_stop():
    """Given the answer's published rules, when the Owner reads the one
    about a contract being defined, then it names the callee's
    postcondition and the depth a run may reach, and not only the
    callee's precondition."""
    label = "a program of all five kinds"
    published = (
        (completed(verify(EVERY_KIND), label).get("result") or {}).get("inventory")
        or {}
    ).get("rules") or {}
    sentence = published.get("totality_of_the_profile", "")

    for owed in ("precondition", "postcondition", "depth"):
        assert owed in sentence, (
            f"WHAT: the rule about a contract being defined does not name "
            f"{owed!r}: {sentence!r}. "
            "WHY: three things can stop a run of a contract clause -- a "
            "callee's precondition, a callee's postcondition, and the depth "
            "budget -- and a reader told only one of them would read this "
            "entry as promising more than it does. "
            "HOW: name all three in THE_RULES_OF_THE_PROFILE."
        )


def test_a_program_outside_the_fragment_is_answered_without_a_disclosure():
    """Given a program the translation does not cover, when the Owner
    asks what it owes, then the answer completes with 2 obligations
    proved and 2 unknown, carries no disclosure of trust, and says no
    solver stood behind it."""
    label = "a program outside the fragment"
    answer = completed(verify(OUTSIDE_THE_FRAGMENT), label)
    stood = results_by_identity(answer, label)

    assert sorted(stood.values()) == ["proved", "proved", "unknown", "unknown"], (
        f"WHAT: the 4 obligations of this program stand as {stood}. "
        "WHY: its contract and its ending rest on a rule of core-0 and are "
        "settled; its body and its example need a let binding, which this "
        "fragment leaves for a later one. "
        f"HOW: inspect the answer: {answer}"
    )
    assert "trust" not in answer, (
        f"WHAT: the answer carries a disclosure of trust: {answer.get('trust')}. "
        "WHY: no solver was asked about any obligation of this program, so "
        "there is no solver's word to disclose, and disclosing one would say "
        "a solver stood behind an answer it did not. "
        f"HOW: carry it only where a solver was asked: {sorted(answer)}"
    )
    said = (answer.get("stands_on") or {})["versions"]["solver"]
    assert said.startswith("not applicable:"), (
        f"WHAT: the answer says {said!r} about the solver behind it. "
        "WHY: it asked none, and naming one would name a version that "
        "answered nothing here. "
        f"HOW: inspect what it stands on: {answer.get('stands_on')}"
    )


def test_a_candidate_the_program_does_not_refuse_is_not_a_disproof():
    """Given a program where the solver finds an input breaking an
    obligation that running the program does not refuse for it, when the
    Owner reads that entry, then it is unknown with its attempt
    completed and carries no counterexample at all."""
    label = "a candidate that does not replay"
    entry = entry_named(
        completed(verify(A_CANDIDATE_THAT_DOES_NOT_REPLAY), label),
        "body_postcondition:below:body",
        label,
    )

    assert entry["result"] == "unknown", (
        f"WHAT: this obligation is answered {entry['result']!r}. "
        "WHY: SPEC.md requires a disproof to carry a witness that replays "
        "against the reference semantics; this one does not, and a failed "
        "validation yields unknown rather than an invented disproof. "
        f"HOW: inspect the entry: {entry}"
    )
    assert entry["execution_status"] == "completed", (
        f"WHAT: the attempt is reported as {entry['execution_status']!r}. "
        "WHY: the solver answered and the replay ran; nothing was "
        "unsupported, timed out or broken, which are the other ways an "
        "obligation goes unsettled, and a reader must be able to tell them "
        f"apart. HOW: inspect the entry: {entry}"
    )
    assert "counterexample" not in entry, (
        f"WHAT: an unsettled entry carries {entry.get('counterexample')}. "
        "WHY: only a validated witness may be published; an input the "
        "program does not refuse would send the Owner looking for a defect "
        "that is not there. "
        f"HOW: inspect the entry: {entry}"
    )


def test_the_manifest_publishes_the_solver_this_tool_requires():
    """Given the manifest, when the Owner reads what solver this tool
    requires, then it names the package and the exact version, and names
    the same solver a verify answer says it asked."""
    required = (the_manifest().get("result") or {}).get("solver") or {}

    assert required.get("package") and required.get("name"), required
    assert "==" in required.get("required", "") and any(
        character.isdigit() for character in required["required"]
    ), (
        f"WHAT: the manifest says {required.get('required')!r} is required of "
        f"{required.get('package')!r}. "
        "WHY: the word proved is only as good as the version that said it, so "
        "a client has to be able to read which version this tool is pinned "
        "to without running it. "
        f"HOW: inspect the published requirement: {required}"
    )
    asked = (
        completed(verify(EVERY_KIND), "a program of all five kinds").get("stands_on")
        or {}
    )["versions"]["solver"]
    assert asked.startswith(required["name"]), (
        f"WHAT: the manifest requires {required['name']!r} and an answer says "
        f"{asked!r} answered it. "
        "WHY: a client comparing the two reads one as the promise and the "
        "other as what kept it; two different names make that comparison "
        "impossible. "
        f"HOW: name the same solver in both places: {required}"
    )
