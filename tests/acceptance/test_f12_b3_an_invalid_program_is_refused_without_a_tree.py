"""F12.B3 -- a program that breaks a rule is refused the way a check
refuses it, and no tree is published for it.

The law: one source gets one answer, whichever operation read it, and a
refused source leaves an agent with no tree to mistake for a result.

still passes if: the refusal carried a category of its own invention but
no tree. Every case below demands the identical categories and status the
check of that same source carries.
"""

from __future__ import annotations

import pytest

from prova import service

from _f12_tree_fixtures import ask_for_the_check, ask_for_the_tree, categories_of

VALID = "(deftype Counter (record (held Int)))\n"

REFUSED_SOURCES = {
    "a source that declares nothing": "",
    "a form that is never closed": "(deftype Counter (record (held Int))\n",
    "a name that is declared twice": VALID + VALID,
    "a body naming what is not bound": (
        "(defn one\n"
        "  (sig () -> Int ! pure)\n"
        "  (examples (example (one) => 1))\n"
        "  missing)\n"
    ),
    "a division the profile does not have": (
        "(defn half\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (half 2) => 1))\n"
        "  (/ n 2))\n"
    ),
    "a body of the wrong type": (
        "(defn one\n"
        "  (sig () -> Int ! pure)\n"
        "  (examples (example (one) => 1))\n"
        "  true)\n"
    ),
}


@pytest.mark.parametrize("why, source", sorted(REFUSED_SOURCES.items()))
def test_a_refused_program_is_refused_the_way_a_check_refuses_it(why, source):
    refusal = ask_for_the_tree(source)
    checked = ask_for_the_check(source)

    assert refusal["status"] == checked["status"], (
        f"{why} was answered {refusal['status']!r} when read, and "
        f"{checked['status']!r} when checked: one source gets one answer "
        "whichever operation reads it; refuse it through the rule both share"
    )
    assert categories_of(refusal) == categories_of(checked), (
        f"{why} was refused with {categories_of(refusal)} when read and "
        f"{categories_of(checked)} when checked: an agent that moves between "
        "the two operations must not meet two vocabularies"
    )


def test_a_source_that_is_not_a_text_is_refused_by_name():
    """The request reader answers for reading a program as it answers for
    every operation that reads one."""
    refusal = service.handle({"prova": "i1", "operation": "parse", "source": 7})

    assert refusal["status"] == "invalid_input", (
        f"a 'source' field holding 7 was answered {refusal['status']!r}: "
        f"{refusal}. A value that is not a text holds no program to read"
    )
    assert categories_of(refusal) == ["malformed_request"], (
        f"the refusal carries {categories_of(refusal)}: a field the tool "
        "cannot read is refused by name, through the one reader of a request"
    )
    assert "result" not in refusal, refusal


@pytest.mark.parametrize("why, source", sorted(REFUSED_SOURCES.items()))
def test_a_refused_program_is_answered_with_no_tree_at_all(why, source):
    refusal = ask_for_the_tree(source)

    assert "result" not in refusal, (
        f"{why} was refused and still carried {refusal.get('result')}: a tree "
        "beside a refusal reads as a program the tool understood; publish none"
    )
    assert refusal["diagnostics"], (
        f"{why} was refused with no diagnostic at all: {refusal}. A refusal "
        "says what was wrong and where"
    )
