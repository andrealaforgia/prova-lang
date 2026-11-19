"""F25 criterion 6 -- the two machines this repository ships, the hour
clock and the reservation component, are both accepted; and the tool
publishes the machine operation, the shape of a descriptor and the
refusals it can answer, so an Owner writes a descriptor from what the
tool says rather than from a guess.

The law: a shipped descriptor is accepted against the program it ships
beside, that program carries its owner's text unchanged, and every part
of the answer and of the refusals is published.

Drives only the installed `prova` command over its JSON stdin/stdout
surface. No imports from src/prova.

still passes if: the published schema named parts no answer ever carries.
The last test reads the answer about both shipped machines and requires
the published schema to name every role it reports, in both directions.
"""

from __future__ import annotations

import pytest

import _f25_machine_fixtures as machines


@pytest.mark.parametrize("machine", machines.MACHINES)
def test_the_shipped_descriptor_is_accepted_against_the_program_it_ships_with(machine):
    """Given the descriptor and the program this repository ships for the
    hour clock and for the reservation component, when the Owner asks the
    tool about each pair, then both are accepted."""
    source, descriptor = machines.shipped_machine(machine)

    answer = machines.ask_about_a_machine(source, descriptor)

    assert answer.get("status") == "completed", (
        f"WHAT: the shipped {machine} machine was answered "
        f"{answer.get('status')!r}: {answer}. "
        "WHY: criterion 6 promises that the descriptors for the hour clock "
        "and the reservation component are both accepted. "
        f"HOW: read the refusals above against examples/{machine}.machine.json."
    )


def test_the_hour_clock_machine_program_carries_the_shipped_clock_unchanged():
    """Given the machine program for the hour clock, then it carries the
    hour clock this repository ships word for word, with only the
    projection and admissibility helpers added: the clock has one
    owner."""
    program = machines.machine_source("hour-clock")
    shipped = machines.shipped_hour_clock_source()

    assert program.startswith(shipped), (
        "WHAT: examples/hour-clock.machine.prova does not begin with the "
        "text of examples/hour-clock.prova. "
        "WHY: two copies of the hour clock that can drift apart would let "
        "the machine confirm a clock the Owner does not run. "
        "HOW: write the machine program as the shipped clock plus the "
        "helpers SPEC.md lines 570-572 ask for."
    )
    added = program[len(shipped) :]
    assert "(defn state-of" in added and "(defn admissible" in added, (
        f"WHAT: what the machine program adds to the shipped clock is "
        f"{added!r}. "
        "WHY: the descriptor needs a projection and an admissibility "
        "predicate, and nothing else is added to the clock. "
        "HOW: add those two helpers alone."
    )


def test_the_reservation_machine_program_carries_the_spec_example_unchanged():
    """Given the machine program for the reservation component, then it
    carries SPEC.md's core conformance example word for word, with only
    the projection and admissibility helpers added: the specification
    stays the owner of that component."""
    program = machines.machine_source("reservation")
    from_the_spec = machines.spec_reservation_source()

    assert program.startswith(from_the_spec), (
        "WHAT: examples/reservation.machine.prova does not begin with "
        "SPEC.md's core conformance example. "
        "WHY: the specification owns that component; a second copy that can "
        "drift from it would let the machine confirm something SPEC.md does "
        "not state. "
        "HOW: write the machine program as the example from SPEC.md plus the "
        "helpers its lines 570-572 ask for."
    )


def test_the_tool_offers_the_machine_operation_as_its_own():
    """Given the tool, when an agent reads the manifest, then the machine
    operation is offered as available and marked as this tool's own with
    a reason, because SPEC.md lines 467-468 name it in none of the seven
    operation categories."""
    result = machines.ask_for_the_manifest().get("result") or {}

    assert (result.get("operations") or {}).get("machine") == "available", (
        f"WHAT: the manifest says the machine operation is "
        f"{(result.get('operations') or {}).get('machine')!r}. "
        "WHY: an agent reads what a tool answers from its manifest, and this "
        "tool answers about a machine descriptor. "
        "HOW: advertise it as available."
    )
    beyond = result.get("beyond_profile") or {}
    assert len(beyond.get("machine") or "") > 30, (
        f"WHAT: the manifest marks the machine operation as beyond the "
        f"profile with {beyond.get('machine')!r}. "
        "WHY: SPEC.md lines 467-468 name seven operation categories and this "
        "is in none of them; an agent reading the operation list must not "
        "take it for profile conformance. "
        "HOW: say so with the reason."
    )


def test_the_tool_publishes_the_shape_of_a_descriptor_it_accepts():
    """Given the tool, when an agent reads the manifest, then it publishes
    the version of the descriptor shape, the fields of the document and
    every role with what it resolves to, so a descriptor is written from
    what the tool says."""
    schema = machines.published_descriptor_schema()

    assert schema.get("version") == machines.THE_SCHEMA_VERSION, (
        f"WHAT: the manifest publishes the descriptor version "
        f"{schema.get('version')!r}, and the shipped descriptors are written "
        f"in {machines.THE_SCHEMA_VERSION!r}. "
        "WHY: an agent writes the version the tool asks for. "
        "HOW: publish the one version the tool reads."
    )
    published_roles = schema.get("roles") or {}
    assert sorted(published_roles) == sorted(machines.THE_ROLES), (
        f"WHAT: the manifest publishes the roles {sorted(published_roles)}, "
        f"not {sorted(machines.THE_ROLES)}. "
        "WHY: a role an agent must name but cannot look up is an "
        "undocumented API. HOW: publish every part of the descriptor."
    )
    for role, published in published_roles.items():
        assert published.get("resolves_to") in ("type", "function"), (
            f"WHAT: the manifest says the {role!r} role resolves to "
            f"{published.get('resolves_to')!r}. "
            "WHY: an agent needs to know whether to name a declared type or "
            "a declared function. HOW: publish one of the two."
        )
        assert published.get("shape"), (
            f"WHAT: the manifest says nothing about the shape the {role!r} "
            f"role needs: {published}. "
            "WHY: criterion 1 is about functions of the right shapes; an "
            "agent reads the shape it must declare from the tool. "
            "HOW: publish the shape beside the role."
        )
    document = schema.get("document") or {}
    assert sorted(document) == ["assumptions", "roles", "schema", "types"], (
        f"WHAT: the manifest publishes the descriptor fields "
        f"{sorted(document)}. "
        "WHY: the descriptor document has four parts -- its version, its "
        "types, its roles and its stated assumptions -- and an agent writes "
        "exactly those. HOW: publish the four."
    )


def test_every_refusal_about_a_machine_is_published_before_it_is_answered():
    """Given the tool, when an agent reads the manifest and then sends a
    descriptor with a role that does not resolve, then the category of
    every refusal it reads back is one the manifest publishes with its
    fields."""
    published = machines.ask_for_the_manifest().get("result") or {}
    categories = set(published.get("diagnostic_categories") or [])
    schemas = published.get("diagnostic_schemas") or {}

    source, descriptor = machines.shipped_machine("hour-clock")
    refused = machines.ask_about_a_machine(
        source,
        machines.naming(descriptor, "step", machines.A_NAME_NO_PROGRAM_DECLARES),
    )

    answered = set(machines.categories_of(refused))
    assert answered, f"no refusal to read in {refused}"
    unpublished = sorted(answered - categories)
    assert unpublished == [], (
        f"WHAT: the tool answers the refusal categories {unpublished}, which "
        "the manifest does not publish. "
        "WHY: a category an agent meets but cannot look up is an "
        "undocumented API. HOW: publish every category from the one table "
        "the refusals are built from."
    )
    for category in answered:
        assert "role" in (schemas.get(category) or {}).get("fields", {}), (
            f"WHAT: the manifest publishes {category!r} without a role "
            f"field: {schemas.get(category)}. "
            "WHY: criterion 2 promises that the diagnostic names the role, "
            "so the field an agent reads it from is published. "
            "HOW: publish the fields of that category from its own kind."
        )


@pytest.mark.parametrize("machine", machines.MACHINES)
def test_the_published_roles_are_the_roles_the_answer_reports(machine):
    """Given the tool's published descriptor shape and its answer about a
    shipped machine, then the two name the same roles, read against each
    other in both directions."""
    published = set((machines.published_descriptor_schema().get("roles") or {}))
    source, descriptor = machines.shipped_machine(machine)

    reported = set(machines.roles_of(machines.ask_about_a_machine(source, descriptor)))

    assert len(reported) == len(machines.THE_ROLES), (
        f"WHAT: the answer about the {machine} reports {sorted(reported)}, "
        f"not the {len(machines.THE_ROLES)} parts a descriptor names. "
        "WHY: an answer reporting nothing would agree with a manifest "
        "publishing nothing, and the two would say nothing at all. "
        "HOW: report one entry per part of the descriptor."
    )
    assert published == reported, (
        f"WHAT: the manifest publishes the roles {sorted(published)} and the "
        f"answer about the {machine} reports {sorted(reported)}. "
        "WHY: a published role no answer carries is a promise nothing "
        "checks, and a reported role nothing publishes is one an agent "
        "cannot look up. HOW: publish and report from the one table."
    )
