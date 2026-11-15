"""Acceptance test for F7's published vocabulary: the refusal a wrongly
counted operator call carries is one the tool's manifest already lists,
so a client that read the manifest can act on it without reading prose.

The tool publishes the categories it answers with through its `discover`
operation. This feature adds no twelfth word to that list: an operator
given the wrong number of arguments is the same defect as a call or a
constructor given the wrong number, and is answered with the same
category they already use.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the manifest listed every word in the language. The
second test takes the category out of a real refusal and looks for that
one, so a manifest that dropped it fails.
"""

from __future__ import annotations

from _f7_operator_arity_fixtures import (
    ARITY_MISMATCH_CATEGORY,
    NOT_WITH_TWO_ARGUMENTS,
    check,
    discover,
    of_category,
)


def _published_categories() -> list[str]:
    response = discover().response()
    return list((response.get("result") or {}).get("diagnostic_categories") or [])


def test_the_refusal_a_wrongly_counted_operator_carries_is_published():
    """Given the program whose `not` has two arguments, when it is
    checked and the tool's manifest is read, then the word the refusal
    carries is one the manifest lists, so a client can recognise it
    without reading the sentence."""
    refusals = of_category(check(NOT_WITH_TWO_ARGUMENTS).response(), ARITY_MISMATCH_CATEGORY)
    assert refusals, (
        "the program whose `not` has two arguments was not refused with a word "
        f"about the number of arguments: {check(NOT_WITH_TWO_ARGUMENTS).response()}."
    )

    published = _published_categories()

    assert refusals[0]["category"] in published, (
        f"the refusal carries {refusals[0]['category']!r}, which the tool's "
        f"manifest does not list: {published}. A client reads the manifest to know "
        "what it may be answered with; publish every word the tool uses."
    )


def test_the_manifest_lists_that_word_once():
    """The manifest is a list a client reads: the word for a wrong
    number of arguments appears in it exactly once, whatever else it
    lists."""
    published = _published_categories()

    assert published.count(ARITY_MISMATCH_CATEGORY) == 1, (
        f"the manifest lists {ARITY_MISMATCH_CATEGORY!r} "
        f"{published.count(ARITY_MISMATCH_CATEGORY)} time(s): {published}. One "
        "defect has one published word."
    )
