"""F27 against the manifest -- what the Owner may send to drive a
machine, the words an answer publishes and the refusal a state outside
the invariant carries are all published by `discover` before any answer
carries them.

The law: every word the runtime publishes is a word an agent can look up
in the manifest, and every field the manifest names is one the runtime
reads.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the manifest published the words and the runtime never
emitted them -- the last test here drives the three answers and requires
each word it reads to be published; or the manifest published a field
the runtime ignores, which the request built from the published shape
alone catches.
"""

from __future__ import annotations

import _f27_runtime_fixtures as machines

THE_MANIFEST = machines.ask_for_the_manifest().get("result") or {}


def test_the_runtime_is_advertised_as_an_operation_an_agent_may_call():
    """Given the manifest, when an agent reads the operations, then the
    one that drives a machine is advertised as available."""
    advertised = THE_MANIFEST.get("operations") or {}
    assert advertised.get(machines.THE_OPERATION) == "available", (
        f"WHAT: the manifest advertises {machines.THE_OPERATION!r} as "
        f"{advertised.get(machines.THE_OPERATION)!r}: {sorted(advertised)}. "
        "WHY: an agent reads what it may call from the tool, and an "
        "operation that answers while the manifest stays silent is an "
        "undocumented API. HOW: advertise it."
    )
    assert machines.THE_OPERATION in (THE_MANIFEST.get("beyond_profile") or {}), (
        f"WHAT: the manifest does not say where "
        f"{machines.THE_OPERATION!r} stands in the profile: "
        f"{THE_MANIFEST.get('beyond_profile')}. "
        "WHY: SPEC.md names seven operation categories and driving a "
        "machine is in none of them, so answering it is no conformance to "
        "the profile and the manifest must say so, as it does for the two "
        "other operations this tool added. "
        "HOW: record it as this tool's own with the reason."
    )


def test_the_four_fields_a_request_carries_are_published():
    """Given the manifest, when an agent reads the shape of the
    operation that drives a machine, then it names the program, the
    descriptor, the state and the events, and nothing else."""
    schema = (THE_MANIFEST.get("operation_schemas") or {}).get(
        machines.THE_OPERATION
    ) or {}
    fields = ((schema.get("request") or {}).get("fields")) or {}
    assert sorted(fields) == ["descriptor", "events", "source", "state"], (
        f"WHAT: the published request names {sorted(fields)}. "
        "WHY: an agent writes its request from this shape alone, so a "
        "field left out cannot be sent and one named here must be read. "
        "HOW: publish the four fields the request reader reads."
    )
    answered = ((schema.get("response") or {}).get("fields")) or {}
    assert "result" in answered and "stands_on" in answered, (
        f"WHAT: the published answer names {sorted(answered)}. "
        "WHY: the Owner reads the transitions from the result and what the "
        "answer stands on beside it. HOW: publish both."
    )


def test_a_request_built_from_the_published_shape_alone_is_answered():
    """Given only the field names the manifest publishes, when a request
    is built out of them for the shipped hour clock, then it is answered
    and not refused."""
    schema = (THE_MANIFEST.get("operation_schemas") or {}).get(
        machines.THE_OPERATION
    ) or {}
    fields = sorted(((schema.get("request") or {}).get("fields")) or {})
    source, descriptor = machines.shipped_machine("hour-clock")
    written = {
        "source": source,
        "descriptor": descriptor,
        "state": "(Clock 11)",
        "events": ["(Tick)"],
    }

    answer = machines.run(
        {"operation": machines.THE_OPERATION, **{name: written[name] for name in fields}}
    )

    assert answer.get("status") == "completed", (
        f"WHAT: a request carrying exactly the published fields {fields} "
        f"was answered {answer.get('status')!r}: {answer}. "
        "WHY: an agent that reads the manifest and sends what it says must "
        "be answered; a field it cannot learn about is an undocumented "
        "API. HOW: read the refusals above."
    )


def test_the_refusal_of_a_state_outside_the_invariant_is_published_first():
    """Given the manifest, when an agent reads the refusal categories,
    then the one a state outside the invariant carries is among them,
    with the shape it carries."""
    published = THE_MANIFEST.get("diagnostic_categories") or []
    assert machines.A_STATE_OUTSIDE_THE_INVARIANT in published, (
        f"WHAT: the manifest publishes {len(published)} categories and "
        f"{machines.A_STATE_OUTSIDE_THE_INVARIANT!r} is not among them: "
        f"{sorted(published)}. "
        "WHY: a caller reads the shape of every refusal from the tool, so "
        "a category it meets and cannot look up is an undocumented API. "
        "HOW: publish the category."
    )
    shape = (THE_MANIFEST.get("diagnostic_schemas") or {}).get(
        machines.A_STATE_OUTSIDE_THE_INVARIANT
    ) or {}
    assert sorted(shape.get("fields") or {}) == ["named", "role"], (
        f"WHAT: the published shape of that refusal carries "
        f"{sorted(shape.get('fields') or {})}. "
        "WHY: the Owner is sent to the role of the descriptor and to the "
        "function standing in it, so both are published. "
        "HOW: publish the fields the refusal carries."
    )


def test_every_word_an_answer_publishes_is_in_the_manifest():
    """Given the four answers a transition, a boundary rejection, a stop
    at the invariant and a refused contract produce, when the words they
    publish are read, then each of them stands in what the manifest
    documents for this operation."""
    documented = (THE_MANIFEST.get("documentation") or {}).get(
        machines.THE_OPERATION
    )
    assert documented, (
        f"WHAT: the manifest documents nothing for "
        f"{machines.THE_OPERATION!r}: "
        f"{sorted(THE_MANIFEST.get('documentation') or {})}. "
        "WHY: the words the result carries, and the rule that a machine is "
        "driven only from a state its invariant holds at, are what an Owner "
        "reads before sending anything. HOW: document the operation."
    )
    clock_source, clock_descriptor = machines.shipped_machine("hour-clock")
    narrow_source, narrow_descriptor = machines.reservation_that_admits_less()
    drifting_source, drifting_descriptor = machines.clock_that_leaves_its_invariant()
    asking_source, asking_descriptor = machines.clock_whose_step_asks_for_more()
    answers = (
        machines.drive(clock_source, clock_descriptor, "(Clock 11)", ["(Tick)"]),
        machines.drive(
            narrow_source, narrow_descriptor, "(Reservation 2)", ["(Reserve)"]
        ),
        machines.drive(
            drifting_source, drifting_descriptor, "(Clock 12)", ["(Tick)", "(Tick)"]
        ),
        machines.drive(
            asking_source, asking_descriptor, "(Clock 12)", ["(Tick)", "(Tick)"]
        ),
    )

    emitted = {
        entry.get("result")
        for answer in answers
        for entry in machines.transitions_of(answer)
    }
    emitted |= {
        (machines.stopped_at_of(answer) or {}).get("reason")
        for answer in answers
        if machines.stopped_at_of(answer)
    }
    assert emitted == {
        machines.A_TRANSITION,
        machines.A_BOUNDARY_REJECTION,
        machines.A_STATE_OUTSIDE_THE_INVARIANT,
        machines.A_CONTRACT_REFUSAL,
    }, (
        f"WHAT: the four answers published the words {sorted(emitted)}. "
        "WHY: this test compares what is published with what is emitted, so "
        "it must first have emitted every word a run can carry: the three a "
        "result entry carries and the stop reason a refused contract adds. "
        "HOW: read the four answers above."
    )
    for word in sorted(emitted):
        assert word in documented, (
            f"WHAT: an answer published the word {word!r}, and what the "
            f"manifest documents for {machines.THE_OPERATION!r} does not "
            f"mention it: {documented}. "
            "WHY: a word an agent meets in an answer and cannot look up is "
            "an undocumented API. HOW: document every word the result "
            "carries."
        )
