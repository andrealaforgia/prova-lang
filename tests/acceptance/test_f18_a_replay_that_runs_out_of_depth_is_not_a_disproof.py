"""A witness this tool cannot finish running is not a counterexample.

An eighth review round found the last way a disproof could be invented.
When the solver offers an input, this tool runs the program over it to
see whether the program really refuses it. That run can fail for a
reason that says nothing about the program: it can nest deeper than the
evaluator goes. The code treats that as "not confirmed" and leaves the
obligation unsettled; turning the guard into a confirmation instead
publishes this tool's own depth-budget message as the refusal a
counterexample carries, and the Owner is sent to chase a defect that is
not there.

The chain below is inside the bound on how far calls are expanded, so
the obligation is translated and the solver does find an input -- and
running the program over that input runs out of depth.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the tool answered unknown for everything. The second
test requires the obligations of the same program that are settled to
come back proved.
"""

from __future__ import annotations

from _f18_fixtures import completed, entry_named, results_by_identity, verify

A = "=>"
HOW_MANY = 40
HOW_DEEP = 4


def _a_chain_too_deep_to_replay() -> str:
    """40 functions, each nesting four expressions around the call to
    the one before it, under a promise that is false at 0."""
    written = [
        f"(defn f0\n  (sig ((n Int)) -> Int ! pure)\n"
        f"  (examples (example (f0 1) {A} 1))\n  n)"
    ]
    for step in range(1, HOW_MANY):
        body = f"(f{step - 1} n)"
        for _ in range(HOW_DEEP):
            body = f"(+ {body} 0)"
        written.append(
            f"(defn f{step}\n  (sig ((n Int)) -> Int ! pure)\n"
            f"  (examples (example (f{step} 1) {A} 1))\n  {body})"
        )
    written.append(
        f"(defn top\n  (sig ((n Int)) -> Int ! pure)\n"
        f"  (ensures (> result 0))\n"
        f"  (examples (example (top 1) {A} 1))\n  (f{HOW_MANY - 1} n))"
    )
    return "\n\n".join(written) + "\n"


LABEL = "a chain too deep to replay a witness through"


def test_a_witness_the_tool_cannot_finish_running_is_not_published():
    """Given a chain whose promise is false and whose replay runs out of
    depth, when the Owner reads that obligation, then it is unsettled
    and carries no counterexample at all."""
    entry = entry_named(
        completed(verify(_a_chain_too_deep_to_replay()), LABEL),
        "body_postcondition:top:body",
        LABEL,
    )

    assert entry["result"] == "unknown", (
        f"WHAT: this obligation is answered {entry['result']!r}. "
        "WHY: the solver offered an input and running the program over it "
        "ran out of the depth this tool goes to, which says nothing about "
        "the program; SPEC.md requires a witness that replays, and a failed "
        "validation yields unknown rather than an invented disproof. "
        f"HOW: inspect the entry: {entry}"
    )
    assert entry["execution_status"] == "completed", entry
    assert "counterexample" not in entry, (
        f"WHAT: an unsettled entry carries {entry.get('counterexample')}. "
        "WHY: the only thing that could be published here is this tool's own "
        "depth-budget message dressed as a refusal of the program, which "
        "would send the Owner to chase a defect that is not there. "
        f"HOW: inspect the entry: {entry}"
    )


def test_the_rest_of_the_same_chain_is_still_settled():
    """Given the same chain, when the Owner reads the rest of the
    answer, then the contract and the ending of every function in it
    still come back proved."""
    stood = results_by_identity(verify(_a_chain_too_deep_to_replay()), LABEL)

    unsettled = [
        identity
        for identity, result in stood.items()
        if identity.startswith(("contract_definedness:", "structural_termination:"))
        and result != "proved"
    ]
    assert not unsettled, (
        f"WHAT: {len(unsettled)} of the contract and ending obligations are "
        f"not proved: {unsettled[:5]}. "
        "WHY: a rule of core-0 settles those whatever the body contains; a "
        "tool that gave up on the whole program would pass the test above by "
        f"settling nothing. HOW: inspect the answer: {stood}"
    )
