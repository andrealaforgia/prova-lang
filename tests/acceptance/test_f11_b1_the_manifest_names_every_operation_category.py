"""F11.B1 -- an agent asks `discover` once and learns which of SPEC.md's
seven operation categories this tool can be used for, and which it
cannot.

The walking skeleton of F11: the real `prova` command, a real JSON
request on its standard input, and a real answer read back.

still passes if: the tool named the seven categories and nothing else
agreed with them. The second test reads the availability word of every
category back from the per-operation list the tool already publishes and
from the answer each of those operations actually gives, so a category
that advertised the wrong word fails.
"""

from __future__ import annotations

from _f11_manifest_fixtures import (
    AVAILABILITY_WORDS,
    THE_CATEGORIES_SPEC_NAMES,
    ask,
    availability_of_each_operation,
    published_categories,
)


def test_every_operation_category_the_profile_names_is_there_with_its_word():
    """Given the tool as it ships, when an agent asks `discover`, then
    all 7 categories SPEC.md names are there, each with the operation
    that covers it and the word 'available' or 'unavailable'."""
    categories = published_categories()

    assert set(categories) == set(THE_CATEGORIES_SPEC_NAMES), (
        f"the manifest names the categories {sorted(categories)}, and "
        f"SPEC.md lines 467-468 name {sorted(THE_CATEGORIES_SPEC_NAMES)}. An "
        "agent reads from this list what this tool can be used for; a "
        "category left out reads as a tool that was never asked to have it, "
        "and one added reads as profile conformance that SPEC.md does not "
        "name."
    )
    for category in THE_CATEGORIES_SPEC_NAMES:
        entry = categories[category]
        assert isinstance(entry, dict), (
            f"the category {category!r} carries {entry!r} and not an entry "
            "naming its operation and whether it can be used."
        )
        assert isinstance(entry.get("operation"), str) and entry["operation"], (
            f"the category {category!r} names no operation: {entry}. An "
            f"agent that wants {category} has to know what to send."
        )
        assert entry.get("availability") in AVAILABILITY_WORDS, (
            f"the category {category!r} says {entry.get('availability')!r}, "
            f"which is neither of {AVAILABILITY_WORDS}. SPEC.md lines "
            "469-470 ask for unimplemented operations to be advertised as "
            "unavailable."
        )


def test_the_word_a_category_carries_is_the_one_the_operation_answers_with():
    """Given the 7 categories, when the operation each of them names is
    called, then an operation advertised as 'unavailable' answers
    'unavailable' and an available one answers something else."""
    categories = published_categories()
    advertised = availability_of_each_operation()

    for category, entry in categories.items():
        operation = entry["operation"]
        assert advertised.get(operation) == entry["availability"], (
            f"the category {category!r} says its operation {operation!r} is "
            f"{entry['availability']!r} and the operation list says "
            f"{advertised.get(operation)!r}. The two are one decision read "
            "twice and must agree."
        )
        status = ask({"operation": operation, "source": ""})["status"]
        refused = status == "unavailable"
        assert refused == (entry["availability"] == "unavailable"), (
            f"the category {category!r} advertises {operation!r} as "
            f"{entry['availability']!r} and asking for it answers "
            f"{status!r}. An agent plans its work from the word the "
            "manifest carries."
        )
