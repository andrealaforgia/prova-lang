"""F15.B4 -- the canonical text is accepted, declares the same program
and answers the same examples as the source it was written from.

SPEC.md line 84 says formatting policy must not alter language validity,
and line 82 that formatting preserves meaning. The reservation program
SPEC.md publishes is the program this repository treats as its
conformance target, so it is the one read here.

still passes if: the tool had answered the source unchanged. F15.B1
states that a one-line program comes back on several lines, so an echo
is already refused there; here the three readings below are compared
between two texts that differ.
"""

from __future__ import annotations

from _f15_format_fixtures import (
    ask_for_the_examples,
    ask_for_the_tree,
    ask_to_check,
    ask_to_format,
    canonical_text,
    example_results,
    meaning_of,
    the_reservation_program,
)


def _canonical_reservation() -> str:
    source = the_reservation_program()
    answered = ask_to_format(source)
    assert answered["status"] == "completed", (
        f"the reservation program SPEC.md publishes was answered "
        f"{answered['status']!r}: {answered}. It is the conformance target "
        "of this tool, so it must be a program the tool can write out"
    )
    canonical = canonical_text(answered)
    assert isinstance(canonical, str) and canonical != source, (
        "the canonical text of the published reservation program is the "
        "submitted text itself, so nothing shows a layout was applied"
    )
    return canonical


def test_the_canonical_text_is_still_an_accepted_program():
    canonical = _canonical_reservation()

    before = ask_to_check(the_reservation_program())
    after = ask_to_check(canonical)

    assert before["status"] == "completed", before
    assert after["status"] == "completed", (
        f"the canonical text of an accepted program was refused "
        f"{after['status']!r}: {after}\n{canonical}\nSPEC.md line 84 says "
        "formatting policy must not alter language validity; a text the tool "
        "writes itself must be a text the tool reads"
    )
    assert after["contract_report"] == before["contract_report"], (
        f"the contracts of the program read\n{before['contract_report']}\n"
        f"before and\n{after['contract_report']}\nafter: writing a program "
        "out must not change what it promises"
    )


def test_the_canonical_text_declares_the_same_program():
    canonical = _canonical_reservation()

    before = ask_for_the_tree(the_reservation_program())["result"]["tree"]
    after = ask_for_the_tree(canonical)["result"]["tree"]

    assert meaning_of(after) == meaning_of(before), (
        "the tree of the canonical text differs from the tree of the source "
        "in something other than where its nodes stand and which node holds "
        f"each comment:\n{canonical}\nThe layout may move a part of the "
        "program; it may not add, drop or change one"
    )


def test_the_canonical_text_answers_the_same_examples():
    canonical = _canonical_reservation()

    before = ask_for_the_examples(the_reservation_program())
    after = ask_for_the_examples(canonical)

    assert example_results(before), (
        f"the published reservation program declared no examples to run: "
        f"{before}. Every function of core-0 declares at least one"
    )
    assert example_results(after) == example_results(before), (
        f"the examples answered\n{example_results(before)}\nfor the source "
        f"and\n{example_results(after)}\nfor its canonical text. SPEC.md "
        "line 82 says formatting preserves meaning, so every example must "
        "answer exactly what it answered before"
    )
