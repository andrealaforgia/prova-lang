"""F15.B7 -- every pair published under conformance/format is answered
exactly as it is published.

SPEC.md lines 83-84 require the canonical layout to be fixed in
conformance fixtures before `format` ships. These pairs are that fixing:
each is a source a reader might write beside the one text the tool
answers for it, and both halves were written by hand from the layout
policy and not by running the tool. A change to the layout is therefore a
change a reader must publish, not one that happens quietly.

still passes if: the tool had answered its own input unchanged, had the
two halves of a pair been equal. Each published source is deliberately
written in a spelling the canonical half does not use, and the first
test below states that the two halves differ.
"""

from __future__ import annotations

import pytest

from _f15_format_fixtures import (
    PUBLISHED_PAIRS,
    ask_to_format,
    canonical_text,
    pair_canonical,
    pair_source,
    published_names,
)

# The pairs this suite reads. Named here rather than discovered, so that
# a pair that stops being published fails instead of disappearing from
# the run.
PUBLISHED = ("clauses", "comments", "integers", "nested", "shapes")


def test_every_published_pair_is_one_this_suite_reads():
    assert published_names() == sorted(PUBLISHED), (
        f"the sources published under {PUBLISHED_PAIRS.name} are "
        f"{published_names()} and this suite reads {sorted(PUBLISHED)}: a "
        "fixture nothing reads fixes nothing, and a layout nothing publishes "
        "is not fixed at all; publish each source with its canonical text "
        "beside it and read it here"
    )


@pytest.mark.parametrize("name", PUBLISHED)
def test_the_published_source_is_answered_with_the_published_text(name):
    source_file = PUBLISHED_PAIRS / f"{name}.prova"
    canonical_file = PUBLISHED_PAIRS / f"{name}.canonical.prova"
    assert source_file.exists() and canonical_file.exists(), (
        f"the pair {name!r} is not published: {source_file} and "
        f"{canonical_file} fix the layout this tool writes; publish the "
        "source beside the text it is answered with"
    )

    source = pair_source(name)
    published = pair_canonical(name)
    assert source != published, (
        f"the two halves of the pair {name!r} are the same text, so the pair "
        "fixes no layout at all: write the source in a spelling the canonical "
        "text does not use"
    )

    answered = ask_to_format(source)
    assert answered["status"] == "completed", (
        f"the published source {name!r} was answered {answered['status']!r}: "
        f"{answered}. A fixture that fixes the layout must be a program the "
        "tool accepts"
    )
    assert canonical_text(answered) == published, (
        f"writing {name!r} out answered a text that differs from the one "
        f"published beside it.\nanswered:\n{canonical_text(answered)}\n"
        f"published:\n{published}\nThe published fixture is the layout: "
        "change the fixture deliberately, or make the answer match it"
    )


@pytest.mark.parametrize("name", PUBLISHED)
def test_the_published_text_is_answered_with_itself(name):
    published = pair_canonical(name)

    answered = ask_to_format(published)

    assert answered["status"] == "completed", (
        f"the canonical half of the pair {name!r} was answered "
        f"{answered['status']!r}: {answered}. The text the tool writes must "
        "be a text the tool reads"
    )
    assert canonical_text(answered) == published, (
        f"writing the canonical half of {name!r} out answered\n"
        f"{canonical_text(answered)}\nand not the text itself:\n{published}\n"
        "A canonical text is already canonical; writing it out again must "
        "change nothing"
    )
