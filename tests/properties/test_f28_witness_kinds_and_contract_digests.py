"""F28's three laws, generated.

- LAW1: for every counter whose step adds a fixed amount with no guard
  against its ceiling, preservation is disproved by an induction-step
  witness, and running the invariant on the witness state and on the
  state after the step answers true and then false.
- LAW2: nothing an answer carries is called a reachable counterexample
  unless it names the state the initialiser answers and at least one
  transition.
- LAW3: the digest of the contracts a machine's proofs rest on moves when
  a contract of a role function changes and stands still when a body
  changes.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool emitted no reachable counterexample anywhere --
LAW2 would then be vacuous. tests/acceptance/test_f28_b2 and b3 require
one for the two sources whose first transition is refused.
"""

from __future__ import annotations

import pathlib
import sys

from hypothesis import given, settings, strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "acceptance"))

import _f28_broken_guard_fixtures as broken  # noqa: E402

CEILINGS = st.integers(min_value=1, max_value=9)
AMOUNTS = st.integers(min_value=1, max_value=4)


@settings(derandomize=True, max_examples=4, deadline=None)
@given(ceiling=CEILINGS, by=AMOUNTS)
def test_f28_p1_an_unguarded_counter_is_disproved_by_a_witness_that_replays(
    ceiling, by
):
    """LAW1 -- given a counter whose invariant caps it at a ceiling and
    whose step adds a fixed amount whatever the state, when the Owner
    verifies it with its descriptor, then preservation is disproved by an
    induction-step witness whose state the invariant admits and whose
    state after the step the invariant refuses."""
    source, descriptor = broken.a_counter_whose_step_has_no_guard(ceiling, by)

    answered = broken.ask_to_verify(source, descriptor)

    entry = broken.the_three_obligations(answered).get(broken.PRESERVATION) or {}
    assert entry.get("result") == broken.DISPROVED, (
        f"WHAT: preservation of a counter capped at {ceiling} whose step "
        f"adds {by} stands as {entry.get('result')!r}: {entry}. "
        "WHY: the state at the ceiling leaves the invariant after one step, "
        "and a witness of that which the evaluator confirms is a disproof. "
        "HOW: replay the whole transition on the witness the solver found."
    )
    witness = broken.the_witness_of(entry)
    assert witness.get("kind") == broken.AN_INDUCTION_STEP_WITNESS, (
        f"WHAT: the disproof carries {witness.get('kind')!r} as its kind: "
        f"{witness}. "
        "WHY: the evidence type must be named. "
        f"HOW: name {broken.AN_INDUCTION_STEP_WITNESS!r}."
    )
    invariant = descriptor["roles"]["invariant"]
    before = broken.ask_to_evaluate(source, invariant, [witness.get("state")])
    after = broken.ask_to_evaluate(
        source, invariant, [witness.get("state_after_the_step")]
    )
    assert (before.get("result") or {}).get("value") == "true", (
        f"WHAT: the invariant answers "
        f"{(before.get('result') or {}).get('value')!r} on the witness state "
        f"{witness.get('state')!r}. "
        "WHY: a witness must satisfy what the obligation assumes. "
        "HOW: confirm the invariant on the witness state before reporting a "
        "disproof."
    )
    assert (after.get("result") or {}).get("value") == "false", (
        f"WHAT: the invariant answers "
        f"{(after.get('result') or {}).get('value')!r} on the state after "
        f"the step {witness.get('state_after_the_step')!r}. "
        "WHY: a disproof the Owner cannot reproduce is the worst thing this "
        "tool can say. HOW: carry the state the step's body answered."
    )


@settings(derandomize=True, max_examples=4, deadline=None)
@given(ceiling=CEILINGS, by=AMOUNTS)
def test_f28_p2_nothing_is_called_reachable_without_an_initial_state_and_a_step(
    ceiling, by
):
    """LAW2 -- given any machine answer, when the Owner reads everything
    in it that is called a reachable counterexample, then each one names
    the state the initialiser answers and at least one transition."""
    source, descriptor = broken.a_counter_whose_step_has_no_guard(ceiling, by)

    answered = broken.ask_to_verify(source, descriptor)

    initial = broken.ask_to_evaluate(source, descriptor["roles"]["init"], [])
    answers = (initial.get("result") or {}).get("value")
    reachable = broken.reachable_counterexample_of(answered)
    if reachable is not None:
        assert reachable.get("initial_state") == answers, (
            f"WHAT: a trace called reachable starts at "
            f"{reachable.get('initial_state')!r} and the initialiser answers "
            f"{answers!r}. "
            "WHY: only a validated initial state may begin one. "
            "HOW: start the replay at the initialiser."
        )
        assert reachable.get("transitions"), (
            f"WHAT: a trace called reachable carries no transition: "
            f"{reachable}. "
            "WHY: a state alone is not an execution. "
            "HOW: carry the sequence replayed."
        )
    assert broken.A_REACHABLE_COUNTEREXAMPLE not in broken.every_kind_named_in(
        broken.the_three_obligations(answered)
    ), (
        f"WHAT: an obligation entry of a counter capped at {ceiling} names "
        f"the kind {broken.A_REACHABLE_COUNTEREXAMPLE!r}. "
        "WHY: an obligation witness is established over one step from an "
        "arbitrary admitted state and never by replaying from the "
        "initialiser. HOW: name that kind only on a trace that was."
    )
    published = broken.published_witness_kinds()
    assert (published.get(broken.A_REACHABLE_COUNTEREXAMPLE) or {}).get(
        "claims_reachability"
    ) is True, (
        f"WHAT: the tool publishes "
        f"{published.get(broken.A_REACHABLE_COUNTEREXAMPLE)!r} for the one "
        "kind of evidence that may claim a run reaches it. "
        "WHY: the name is reserved only if the tool says, in one place an "
        "agent can read, which kind claims reachability; otherwise a reader "
        "has no rule to hold an answer to. "
        f"HOW: publish the kind under {broken.THE_PUBLISHED_KINDS!r}."
    )


@settings(derandomize=True, max_examples=6, deadline=None)
@given(
    attempt=st.sampled_from(range(len(broken.THE_THREE_ATTEMPTS))),
    fault=st.sampled_from(range(len(broken.THE_FAULTS_OF_A_BODY_ALONE))),
)
def test_f28_p3_the_contracts_digest_moves_with_a_contract_and_not_with_a_body(
    attempt, fault
):
    """LAW3 -- given the reservation component edited once in a contract
    and once in a body alone, when the Owner compares the digest of the
    contracts each answer rests on with the unchanged component's, then
    the contract edit moves it and the body edit leaves it where it
    was."""
    shipped_source, descriptor = broken.shipped_reservation()
    changed_label, change = broken.THE_THREE_ATTEMPTS[attempt]
    faulty_label, break_a_body = broken.THE_FAULTS_OF_A_BODY_ALONE[fault]

    shipped = broken.contracts_digest_of(
        broken.ask_to_verify(shipped_source, descriptor)
    )
    changed = broken.contracts_digest_of(broken.ask_to_verify(*change()))
    faulty = broken.contracts_digest_of(broken.ask_to_verify(*break_a_body()))

    assert shipped, (
        "WHAT: the unchanged reservation component answers no contracts "
        "digest. WHY: there is nothing to compare two runs by. "
        f"HOW: carry it under {broken.THE_CONTRACTS_FIELD!r}."
    )
    assert changed != shipped, (
        f"WHAT: the component with {changed_label} answers the same digest "
        f"{changed!r} as the unchanged one. "
        "WHY: a requirement change must be visible as one. "
        "HOW: digest the signatures, preconditions, guarantees and declared "
        "examples of the role functions."
    )
    assert faulty == shipped, (
        f"WHAT: the component with {faulty_label}, whose contracts are "
        f"unchanged, answers the digest {faulty!r} and the unchanged one "
        f"answers {shipped!r}. "
        "WHY: a digest that moves for a body tells the Owner nothing about "
        "requirements. HOW: never digest a body."
    )
