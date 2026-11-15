"""Acceptance test for F8: a client learns the new refusal from the
tool's own manifest before it meets it.

The tool publishes the words its refusals use. A refusal answered with a
word the manifest does not list would make a client guess; the word for
an example about another function is published like every other.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.

still passes if: the manifest listed every word anyone could invent. The
second test takes the word a real refusal carries and requires the
manifest to list exactly that one, so the published list and the answers
cannot drift apart.
"""

from __future__ import annotations

from _f8_example_subject_fixtures import (
    AN_EXAMPLE_ABOUT_ANOTHER_FUNCTION,
    UNRELATED_EXAMPLE_CATEGORY,
    categories,
    check,
    discover,
)


def _published_categories() -> list[str]:
    response = discover().response()
    return list(response.get("result", {}).get("diagnostic_categories") or [])


def test_the_word_for_an_example_about_another_function_is_published():
    """Given a client that has read no refusal yet, when it asks the tool
    what it answers with, then the list it gets names the word an example
    about another function carries."""
    published = _published_categories()

    assert UNRELATED_EXAMPLE_CATEGORY in published, (
        f"the manifest does not publish {UNRELATED_EXAMPLE_CATEGORY!r}, only "
        f"{published}. A client reads the words of the refusals it may meet from "
        "`discover`; publish every word the tool answers with."
    )


def test_the_word_a_real_refusal_carries_is_one_the_manifest_publishes():
    """Given the program whose example of `double` calls `triple`, when
    it is checked, then every word its refusal carries is one the
    manifest publishes."""
    published = _published_categories()

    answered = categories(check(AN_EXAMPLE_ABOUT_ANOTHER_FUNCTION).response())

    assert answered and set(answered) <= set(published), (
        f"the refusal answered with {answered}, which the manifest's {published} "
        "does not cover. Answer only with published words, and publish every word "
        "answered."
    )
