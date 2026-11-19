"""F26 criteria 1, 2 and 3 -- the Owner hands the tool a program and the
descriptor of its machine, asks it to verify, and is told the three
inductive obligations of SPEC.md lines 395-401 separately: that the
initialiser's state satisfies the invariant, that the step is defined for
every event the machine admits in an invariant state, and that the
invariant holds again after the step. For the hour clock and for the
reservation component all three are proved.

The law: an accepted descriptor adds exactly the three inductive
obligations of its machine to the obligations the program already owes,
each listed on its own and each settled by the same route, with the same
words, as the program's own obligations.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the tool answered 'proved' for every machine it is sent.
test_f26_b3 and test_f26_b4 send machines whose invariant the step can
leave and whose initialiser starts outside the invariant, and require
that those are not proved, so a tool that proves everything fails there.
"""

from __future__ import annotations

import pytest

import _f26_induction_fixtures as induction


@pytest.mark.parametrize("machine", induction.MACHINES)
def test_the_three_obligations_are_listed_each_on_its_own(machine):
    """Given the hour clock or the reservation component with the
    descriptor this repository ships for it, when the Owner asks the tool
    to verify, then the answer lists the initialisation, the
    step-enabledness and the preservation obligation, each as one entry
    of its own, beside every obligation the program itself owes."""
    source, descriptor = induction.shipped_machine(machine)

    answered = induction.ask_to_verify(source, descriptor)
    without = induction.ask_to_verify(source)

    assert answered.get("status") == "completed", (
        f"WHAT: verifying the {machine} with its descriptor was answered "
        f"{answered.get('status')!r}: {answered}. "
        "WHY: criterion 1 promises the three machine obligations beside the "
        "program's own, which an answer that refuses carries none of. "
        f"HOW: read the refusals above against examples/{machine}.machine.json."
    )
    listed = induction.the_three_obligations(answered)
    assert sorted(listed) == sorted(induction.THE_THREE), (
        f"WHAT: the answer lists the machine obligations {sorted(listed)}, "
        f"not the three {sorted(induction.THE_THREE)}. "
        "WHY: criterion 1 promises the initialisation, the step-enabledness "
        "and the preservation obligation, each separately; one missing is one "
        "the Owner was told nothing about, and one extra is a claim nobody "
        "asked for. HOW: list one entry per obligation of SPEC.md lines "
        "395-401."
    )
    identities = [entry.get("id") for entry in listed.values()]
    assert len(set(identities)) == len(induction.THE_THREE), (
        f"WHAT: the three machine obligations carry the identities "
        f"{identities}. "
        "WHY: an identity names one obligation so that two answers can be "
        "compared entry by entry; two entries sharing one cannot be told "
        "apart. HOW: give each of the three its own site."
    )
    for kind, entry in listed.items():
        assert (entry.get("to_show") or "").strip(), (
            f"WHAT: the {kind!r} entry says nothing it has to show: {entry}. "
            "WHY: the Owner reads what each obligation is about; an entry "
            "with no statement is a word with no claim behind it. "
            "HOW: state what the obligation shows, in the Owner's words."
        )
    own = [
        entry
        for entry in induction.listed_obligations(answered)
        if entry.get("kind") not in induction.THE_THREE
    ]
    assert own == induction.listed_obligations(without), (
        "WHAT: sending a descriptor changed the obligations the program "
        "itself owes. "
        "WHY: the machine obligations stand beside the program's own; a "
        "descriptor must not rewrite, reorder or drop one of them. "
        "HOW: add the three and leave the rest of the inventory as it was."
    )


@pytest.mark.parametrize("machine", induction.MACHINES)
def test_all_three_are_proved_for_each_shipped_machine(machine):
    """Given the hour clock or the reservation component, when the Owner
    asks the tool to verify it with its descriptor, then each of the
    three obligations stands as 'proved'."""
    source, descriptor = induction.shipped_machine(machine)

    standing = induction.how_the_three_stand(
        induction.ask_to_verify(source, descriptor)
    )

    assert standing == {kind: induction.PROVED for kind in induction.THE_THREE}, (
        f"WHAT: the three obligations of the {machine} stand as {standing}. "
        "WHY: criteria 2 and 3 promise the Owner all three proved for both "
        "shipped machines: the initialiser starts inside the invariant, the "
        "step is defined for every event the machine admits there, and the "
        "invariant holds again afterwards. "
        "HOW: read the reason beside each entry that is not proved."
    )


@pytest.mark.parametrize("machine", induction.MACHINES)
def test_the_answer_says_which_machine_the_three_are_about(machine):
    """Given a descriptor stating its machine's runtime assumptions, when
    the Owner asks the tool to verify, then the answer says which
    descriptor version it read, which function filled each role and which
    assumptions the evidence is conditional on, as the descriptor states
    them."""
    source, descriptor = induction.shipped_machine(machine)

    said = induction.machine_block_of(induction.ask_to_verify(source, descriptor))

    assert said.get("schema") == induction.THE_SCHEMA_VERSION, (
        f"WHAT: the answer says it read the descriptor version "
        f"{said.get('schema')!r}, not {induction.THE_SCHEMA_VERSION!r}: {said}. "
        "WHY: the three obligations are about the machine one descriptor "
        "names; an answer kept beside a descriptor of another version must "
        "say which shape it was read in. HOW: record the version read."
    )
    assert (said.get("roles") or {}).keys() >= set(descriptor["roles"]), (
        f"WHAT: the answer names the roles {sorted((said.get('roles') or {}))} "
        f"and the descriptor names {sorted(descriptor['roles'])}. "
        "WHY: the Owner reads the three obligations against the functions "
        "they are about; a role left out leaves the obligations about "
        "something unnamed. HOW: report the function each role resolved to."
    )
    assert said.get("assumptions_stated") == descriptor["assumptions"], (
        f"WHAT: the answer carries the assumptions "
        f"{said.get('assumptions_stated')!r} and the descriptor states "
        f"{descriptor['assumptions']!r}. "
        "WHY: SPEC.md line 416 says the evidence about a machine is "
        "conditional on its model, and these sentences are that model: an "
        "answer that drops or rewrites them hides what the three proved "
        "obligations rest on. HOW: carry the stated sentences through "
        "unchanged, under a name that says they are stated."
    )


@pytest.mark.parametrize("machine", induction.MACHINES)
def test_the_word_over_the_whole_program_counts_the_three(machine):
    """Given a shipped machine whose program and machine obligations are
    all proved and whose examples all pass, when the Owner asks the tool
    to verify it with its descriptor, then the whole is 'verified' and
    the three obligations are counted among the ones that word rests
    on."""
    source, descriptor = induction.shipped_machine(machine)

    answered = induction.ask_to_verify(source, descriptor)
    without = induction.ask_to_verify(source)

    aggregate = induction.aggregate_of(answered)
    assert aggregate.get("result") == induction.VERIFIED, (
        f"WHAT: the {machine} with its descriptor stands as "
        f"{aggregate.get('result')!r}: {aggregate}. "
        "WHY: every obligation of it is promised proved and every example it "
        "declares passes, and the word over the whole is said when and only "
        "when that holds. HOW: read the reason the aggregate gives."
    )
    counted = (aggregate.get("obligations") or {}).get("of")
    before = (
        (induction.aggregate_of(without).get("obligations") or {}).get("of")
    )
    assert counted == before + len(induction.THE_THREE), (
        f"WHAT: the word over the whole rests on {counted} obligations, and "
        f"the same program without a descriptor owes {before}. "
        "WHY: the word 'verified' must account for the machine obligations "
        "when a descriptor is given; a word that counted only the program's "
        "own would read as covering a machine nothing was shown about. "
        "HOW: settle the three beside the program's own and count them."
    )


@pytest.mark.parametrize("machine", induction.MACHINES)
def test_a_proved_machine_obligation_says_what_it_rests_on(machine):
    """Given the three obligations proved by the pinned solver, when the
    Owner reads the answer, then each entry says what settled it and the
    answer discloses the trust it takes from that solver."""
    source, descriptor = induction.shipped_machine(machine)

    answered = induction.ask_to_verify(source, descriptor)

    listed = induction.the_three_obligations(answered)
    assert sorted(listed) == sorted(induction.THE_THREE), (
        f"WHAT: the answer lists the machine obligations {sorted(listed)}, "
        f"not the three {sorted(induction.THE_THREE)}. "
        "WHY: there is nothing to read about what settled an obligation the "
        "answer does not carry. HOW: list the three."
    )
    for kind, entry in listed.items():
        assert entry.get("discharged_by"), (
            f"WHAT: the {kind!r} entry stands as {entry.get('result')!r} and "
            f"says nothing about what settled it: {entry}. "
            "WHY: a reader told an obligation is proved and not told what "
            "that rests on would take a trusted result for one this tool "
            "established itself (SPEC.md lines 302-305). "
            "HOW: say whether a solver was asked or a rule of core-0 settled "
            "it."
        )
    assert (answered.get("trust") or {}).get("solver"), (
        f"WHAT: the answer names no solver behind the three obligations: "
        f"{answered.get('trust')}. "
        "WHY: the same honesty the program's own obligations are answered "
        "with holds for the machine's: the word 'proved' discloses the "
        "solver it was taken from. HOW: disclose the solver asked."
    )
