"""F14.B1 -- before it sends any work, a caller reads the input, time,
memory and answer budget every operation runs under, and reads that each
one is enforced.

A caller that cannot read a budget learns it by being refused, or worse
by waiting for an answer that never comes. The manifest now states the
four budgets of every operation this tool offers, each with its number,
the unit the number is counted in, the status and category of the
refusal it answers with, and the way a caller lowers it for one run.

still passes if: the tool published four budgets and enforced none of
them. The tests of F14.B2 to F14.B5 send a run past each published
budget and require the refusal the entry here promises.
"""

from __future__ import annotations

from _f14_budget_fixtures import (
    BUDGET_NAMES,
    CATEGORY_OF,
    DECLARED,
    RESOURCE_EXHAUSTED,
    discover,
    published_budgets,
    variable_for,
)


def test_every_operation_this_tool_offers_states_four_budgets():
    """Given a caller reading the manifest before it sends work, when it
    looks for the budgets, then every operation the tool offers states
    an input, time, memory and answer budget, and no operation is left
    without one.
    """
    manifest = discover()
    offered = sorted(
        name
        for name, availability in manifest["result"]["operations"].items()
        if availability == "available"
    )
    budgets = published_budgets(manifest)

    assert sorted(budgets) == offered, (
        f"the manifest states budgets for {sorted(budgets)} and offers "
        f"{offered}: every operation a caller may send work to runs under a "
        "budget, so each of them states one. An operation with no stated "
        "budget leaves a caller unable to size its request."
    )
    for operation in offered:
        assert sorted(budgets[operation]) == sorted(BUDGET_NAMES), (
            f"the {operation!r} operation states "
            f"{sorted(budgets[operation])}, expected "
            f"{sorted(BUDGET_NAMES)}: a caller sizes its source, its patience, "
            "the memory it asks for and the answer it can read, so all four "
            "are stated under their published names."
        )


def test_each_budget_is_marked_enforced_with_the_refusal_it_answers_with():
    """Given the budgets the manifest states, when a caller reads one,
    then it says it is enforced, gives a whole-number maximum with the
    unit it is counted in, and names the status and the category of the
    refusal a run past it meets.
    """
    manifest = discover()
    budgets = published_budgets(manifest)

    for operation, stated in sorted(budgets.items()):
        for name in BUDGET_NAMES:
            entry = stated[name]
            assert entry.get("enforced") is True, (
                f"the {name!r} budget of {operation!r} says enforced="
                f"{entry.get('enforced')!r}: {entry}. A budget that is stated "
                "but not enforced is a promise the tool does not keep, and a "
                "caller relying on it waits for an answer that never comes."
            )
            assert isinstance(entry.get("maximum"), int) and entry["maximum"] > 0, (
                f"the {name!r} budget of {operation!r} states "
                f"{entry.get('maximum')!r} as its maximum: {entry}. A caller "
                "sizes its request against a whole number greater than zero."
            )
            assert entry.get("unit"), (
                f"the {name!r} budget of {operation!r} states no unit: "
                f"{entry}. A number with no unit sizes nothing."
            )
            assert entry.get("status") == RESOURCE_EXHAUSTED, (
                f"the {name!r} budget of {operation!r} says a run past it is "
                f"answered {entry.get('status')!r}: {entry}. A caller reads "
                "the status it will meet from here; one that is not the status "
                "the tool answers with sends it to handle the wrong case."
            )
            assert entry.get("category") == CATEGORY_OF[name], (
                f"the {name!r} budget of {operation!r} says the refusal "
                f"carries {entry.get('category')!r}, expected "
                f"{CATEGORY_OF[name]!r}: {entry}. The category a caller "
                "matches on is read from here, and each budget has its own so "
                "a caller can tell which one stopped the run."
            )
            assert entry.get("reason"), (
                f"the {name!r} budget of {operation!r} states no reason for "
                f"its value: {entry}. A caller that must make its request "
                "smaller is owed the reason the number is what it is."
            )


def test_the_stated_numbers_are_the_ones_the_owner_decided_and_say_so():
    """Given the budgets the Owner decided -- 1 MiB of source, 10 s, 512
    MiB of memory and 1 MiB of answer -- when a caller reads them, then
    each is stated in its own unit and says it is a declared number, not
    one measured on this machine.
    """
    manifest = discover()
    budgets = published_budgets(manifest)

    for operation, stated in sorted(budgets.items()):
        for name in BUDGET_NAMES:
            entry = stated[name]
            assert entry["maximum"] == DECLARED[name], (
                f"the {name!r} budget of {operation!r} is "
                f"{entry['maximum']}, and the Owner decided "
                f"{DECLARED[name]} (docs/ROADMAP.md section 5 D5, approved in "
                "section 8): the tool states the number it was given, so a "
                "caller and the Owner read one number."
            )
            assert entry.get("basis") == "declared", (
                f"the {name!r} budget of {operation!r} says its basis is "
                f"{entry.get('basis')!r}: {entry}. These numbers were chosen, "
                "not measured on a run of this tool, and a caller told "
                "otherwise would read them as a measurement of what the tool "
                "needs."
            )
            assert entry.get("lower_with") == variable_for(name), (
                f"the {name!r} budget of {operation!r} says a caller lowers "
                f"it with {entry.get('lower_with')!r}, expected "
                f"{variable_for(name)!r}: {entry}. The way to lower a budget "
                "is published, so a caller never has to guess it."
            )
