"""Cells that close changes a mutation of the verdict could make without
any test in this repository noticing.

Each one is here because `tools/mutate_encoder.py` made that exact change
to `src/prova/verdict.py` and the cheap passes stayed green: a sentence
about how many examples were never run that disagreed with the count
beside it, and a reason that named the obligations before it counted
them. The commit that added these cells names the run that found them.

The module is imported inside each test, as the table beside it does, so
a module this tool cannot answer yet fails as the case it is.
"""

from __future__ import annotations

import pytest


def _verdict():
    from prova import verdict

    return verdict


def _findings(pairs):
    from prova import discharge

    return {
        f"o{number}": discharge.Finding(result, status)
        for number, (result, status) in enumerate(pairs, start=1)
    }


def _all_eight_passed():
    verdict = _verdict()
    return verdict.ExamplesRun.of(
        [
            {"function": "valid-state", "ordinal": ordinal, "passed": True}
            for ordinal in range(8)
        ],
        8,
    )


def test_a_verdict_asked_for_without_the_static_check_evidence_is_refused():
    """Given findings and an example run but no evidence that the static
    checks passed, when a verdict is asked for, then it refuses and says
    where the evidence comes from.

    The word rests on three things. A caller that could leave one of
    them out would be deciding the word on two.
    """
    with pytest.raises(ValueError) as refusal:
        _verdict().Verdict.over(
            _findings((("proved", "completed"),)), _all_eight_passed(), None
        )

    said = str(refusal.value)
    assert "static checks" in said and "StaticChecksPassed" in said, (
        f"WHAT: the refusal says {said!r}. "
        "WHY: the reader is the author of the caller, who needs to know "
        "which of the three the verdict was asked for without, and where "
        "the evidence for it comes from. "
        "HOW: name the evidence and the way to build it in the refusal."
    )


def test_the_reason_counts_the_undischarged_before_it_names_them():
    """Given 1 of 3 obligations left unsettled, when the reason is read,
    then it says how many of how many were not discharged and then names
    them, in that order.

    A reader who sees the identities and not the count cannot tell one
    missing obligation from twenty, and one who sees them in the wrong
    order reads a sentence that is not one.
    """
    aggregate = _verdict().Verdict.over(
        _findings(
            (
                ("proved", "completed"),
                ("unknown", "unsupported"),
                ("proved", "completed"),
            )
        ),
        _all_eight_passed(),
        _verdict().StaticChecksPassed.of(()),
    )

    said = aggregate.published()["reason"]
    counted = "1 of the 3 obligations"
    assert counted in said, (
        f"WHAT: the reason is {said!r} and does not say {counted!r}. "
        "WHY: a reader told which obligations were not discharged and not "
        "how many of how many cannot tell a program nearly shown from one "
        "barely started. "
        "HOW: count the undischarged against the obligations they are part "
        "of, in the sentence."
    )
    assert said.index(counted) < said.index("o2"), (
        f"WHAT: the reason names the obligation before it counts them: "
        f"{said!r}. "
        "WHY: the sentence is read left to right; the count introduces the "
        "list it is about. "
        "HOW: put the count before the identities."
    )


def test_the_reason_and_the_counts_agree_about_the_examples_never_run():
    """Given a run of 8 declared examples stopped after 3, when the
    aggregate is read, then the count of examples never run and the
    sentence about them say the same 5.

    One place states each number: a sentence and a count that disagree
    leave a reader with no idea which to believe.
    """
    verdict = _verdict()
    stopped = verdict.ExamplesRun.stopped_at(
        [
            {"function": "valid-state", "ordinal": ordinal, "passed": True}
            for ordinal in range(3)
        ],
        8,
        "resource_exhausted",
        "the run reached the evaluation depth this tool allows",
    )
    aggregate = verdict.Verdict.over(
        _findings((("proved", "completed"),)),
        stopped,
        verdict.StaticChecksPassed.of(()),
    )
    published = aggregate.published()

    assert published["examples"]["not_run"] == 5, (
        f"WHAT: the aggregate counts {published['examples']} over a run that "
        "saw 3 of the 8 examples the program declares. "
        "WHY: every declared example passed, failed or was never run, and "
        "the three must add up to the 8. "
        "HOW: count the examples never run from the same run."
    )
    assert "5 of 8" in published["reason"], (
        f"WHAT: the reason is {published['reason']!r} and the count beside "
        f"it says {published['examples']['not_run']} examples were never "
        "run. "
        "WHY: one place states each number; a sentence that says one thing "
        "and a count that says another cannot both be read. "
        "HOW: read the number in the sentence from the same place the count "
        "is read from."
    )
