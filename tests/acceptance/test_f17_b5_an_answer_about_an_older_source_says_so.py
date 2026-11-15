"""F17.B5 -- an answer kept from before an edit does not read as an
answer about the text that is there now.

The answer names the revision it is about and the dependencies it stood
on, and the manifest says that both have to match for the answer to be
about what a client holds now. A client that edited its file can then see
that its kept answer is about the earlier text.

Drives only the `prova` command's real JSON stdin/stdout surface.

still passes if: the tool stamped the same revision on both answers,
which the first test forbids by computing each revision from the text it
sent; still passes if the manifest said nothing a client can act on,
which the last test checks by name.
"""

from __future__ import annotations

from _f17_provenance_fixtures import (
    A_LATER_REVISION,
    A_PROGRAM,
    answer_about,
    digest_of,
    what_it_stands_on,
    the_manifest,
)


def test_an_answer_kept_from_before_an_edit_is_about_the_earlier_text():
    """Given a check answer about the 2-function program, when 1 more
    function is added and the new text is checked, then the kept answer
    names the earlier revision, the new one names the new revision, and
    the 2 differ."""
    kept = answer_about("check", A_PROGRAM)
    now = answer_about("check", A_LATER_REVISION)

    assert kept["source_digest"] == digest_of(A_PROGRAM), (
        f"WHAT: the kept answer is about {kept['source_digest']!r} and the "
        f"text it was asked about is {digest_of(A_PROGRAM)!r}. WHY: a client "
        "compares what it holds with what the answer names. HOW: stamp the "
        "SHA-256 of the submitted characters."
    )
    assert now["source_digest"] == digest_of(A_LATER_REVISION), now
    assert kept["source_digest"] != now["source_digest"], (
        "WHAT: the answer about the text before the edit and the answer "
        "about the text after it name one revision: "
        f"{kept['source_digest']!r}. WHY: a client holding the edited file "
        "would read the kept answer as about the file it holds. "
        "HOW: compute the revision from the characters that were sent."
    )


def test_the_tool_behind_both_answers_is_the_same_one():
    """Given those 2 answers, then both stand on the same dependency
    digest, and it is the one the manifest publishes now, so the only
    thing that changed between them is the source."""
    behind_kept = what_it_stands_on(answer_about("check", A_PROGRAM), "kept")
    behind_now = what_it_stands_on(answer_about("check", A_LATER_REVISION), "current")
    published = what_it_stands_on(the_manifest(), "of the manifest")

    assert (
        behind_kept["dependency_digest"]
        == behind_now["dependency_digest"]
        == published["dependency_digest"]
    ), (
        f"WHAT: the kept answer stands on {behind_kept['dependency_digest']!r}, "
        f"the current one on {behind_now['dependency_digest']!r} and this tool "
        f"publishes {published['dependency_digest']!r}. WHY: a client comparing "
        "a kept answer with this tool has to see which of the two changed. "
        "HOW: read all three from the one place that computes it."
    )


def test_the_manifest_tells_a_client_what_makes_a_kept_answer_stale():
    """Given the manifest, when a client looks for how to tell whether a
    kept answer is still about what it holds, then the manifest names the
    2 digests it has to compare."""
    documentation = (the_manifest().get("result") or {}).get("documentation") or {}
    said = documentation.get("stands_on", "")

    assert isinstance(said, str) and said.strip(), (
        f"WHAT: the manifest says nothing under 'stands_on': "
        f"{sorted(documentation)}. WHY: a client that cannot read the rule "
        "has to guess whether a kept answer still applies. "
        "HOW: say what an answer stands on and when it stops applying."
    )
    for named in ("source_digest", "dependency_digest"):
        assert named in said, (
            f"WHAT: the rule the manifest publishes does not name {named!r}: "
            f"{said!r}. WHY: a client compares exactly those fields. "
            "HOW: name both fields in the rule."
        )
