"""F22 criterion 5: nothing in the artefact replaces the program with
precomputed example answers.

SPEC.md line 491: "Build once and execute fresh inputs. Constant-folding
is permitted; replacing a runtime program with precomputed example output
is not conformance."

Two programs that differ only in one declared example are built, and the
translated part of the two artefacts is compared character for character.
If an example answer reached the computation, the two would differ there.
Beside that, the artefact answers inputs no example of the program
mentions.

Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

from _f22_fixtures import (
    THE_PROGRAM_BEGINS,
    answered,
    build,
    hour_clock,
    run_artefact,
)


def _translated_part(path: pathlib.Path) -> str:
    text = path.read_text(encoding="utf-8")
    assert THE_PROGRAM_BEGINS in text, (
        f"WHAT: the artefact at {path} does not separate what the build "
        f"recorded from the program it translated: {THE_PROGRAM_BEGINS!r} is "
        "not in it. "
        "WHY: a reader must be able to see the translated program apart from "
        "the revision and the evidence of this one build, which is what lets "
        "two builds be compared. "
        f"HOW: write that line between the two parts."
    )
    return text.split(THE_PROGRAM_BEGINS, 1)[1]


def test_c5_two_programs_differing_only_in_an_example_translate_the_same():
    """Given the shipped hour clock and a copy of it whose first
    `valid-state` example asks about the hour 2 instead of the hour 1 --
    both true, so both programs are verified -- when both are built, then
    the two artefacts differ (each records its own source revision) and
    the translated program in them is the same text character for
    character.

    still passes if: the generator had emitted an empty program -- the
    translated part is required to be longer than the two headers and the
    artefacts are required to answer the same fresh input correctly below.
    """
    one_example = "(example (valid-state (Clock 1)) => true)"
    the_same_example_about_another_hour = "(example (valid-state (Clock 2)) => true)"
    first = hour_clock()
    second = first.replace(one_example, the_same_example_about_another_hour)
    assert second != first, (
        f"WHAT: the shipped clock does not contain {one_example!r}. "
        "WHY: a test that changed nothing would compare one program with "
        "itself, and pass over a generator that pastes the examples in. "
        "HOW: read examples/hour-clock.prova and fix the text above."
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        first_target = destination / "first.py"
        second_target = destination / "second.py"
        build(first, "valid-state", first_target)
        build(second, "valid-state", second_target)

        assert first_target.read_bytes() != second_target.read_bytes(), (
            "WHAT: the two artefacts are the same bytes for two different "
            "sources. "
            "WHY: each records the revision it was built from, and two "
            "sources have two revisions; identical files would mean the "
            "artefact records nothing of its own source. "
            "HOW: record the source revision in the artefact."
        )
        assert _translated_part(first_target) == _translated_part(second_target), (
            "WHAT: the translated program differs between two sources that "
            "differ only in one declared example. "
            "WHY: SPEC.md line 491: replacing a runtime program with "
            "precomputed example output is not conformance; an example "
            "answer that reached the computation shows up exactly here. "
            "HOW: translate the declarations of the program and not its "
            "examples."
        )
        assert len(_translated_part(first_target)) > 200, (
            f"WHAT: the translated program is "
            f"{len(_translated_part(first_target))} characters. "
            "WHY: two empty files are also equal; this test needs the "
            "program to be there. "
            "HOW: inspect the artefact."
        )

        for target in (first_target, second_target):
            ran = run_artefact(target, ["(Clock 7)"])
            assert answered(ran, "(Clock 7)") == "true", (
                f"WHAT: {target.name} answered {ran.stdout.strip()!r} for the "
                "hour 7, which the program says is a valid state. "
                "WHY: 7 is in none of the four examples either program "
                "declares, so only a translated program answers it. "
                f"HOW: read the artefact at {target}"
            )
            refused = run_artefact(target, ["(Clock 13)"])
            assert answered(refused, "(Clock 13)") == "false", (
                f"WHAT: {target.name} answered {refused.stdout.strip()!r} for "
                "the hour 13, which the program says is not a valid state. "
                "WHY: an artefact that answered every hour true would pass "
                "the line above. "
                f"HOW: read the artefact at {target}"
            )


def test_c5_an_example_answer_made_wrong_cannot_reach_the_artefact():
    """Given the shipped hour clock and a copy whose `initial` example
    claims the clock starts at 6, when both are built, then the second
    build is refused -- the wrong example does not pass -- and the
    artefact of the first still answers 12 for `initial`, which is what
    the program computes.

    This is the other half of criterion 5: an example answer can neither
    enter the artefact nor be published at all.
    """
    the_true_example = "(example (initial) => (Clock 12))"
    the_wrong_example = "(example (initial) => (Clock 6))"
    source = hour_clock()
    wrong = source.replace(the_true_example, the_wrong_example)
    assert wrong != source, (
        f"WHAT: the shipped clock does not contain {the_true_example!r}. "
        "WHY: a test that changed nothing would build the shipped clock "
        "twice. "
        "HOW: read examples/hour-clock.prova and fix the text above."
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        good = destination / "good.py"
        build(source, "initial", good)
        refused = build(wrong, "initial", destination / "wrong.py")

        assert refused.get("status") == "not_verified", (
            f"WHAT: a program whose own example claims the wrong answer was "
            f"answered {refused.get('status')!r}. "
            "WHY: the build rests on the examples passing. "
            f"HOW: inspect the answer: {refused}"
        )
        assert sorted(p.name for p in destination.iterdir()) == ["good.py"], (
            f"WHAT: the destination holds "
            f"{sorted(p.name for p in destination.iterdir())}. "
            "WHY: the refused build publishes nothing, and the artefact of "
            "the first build is untouched. "
            "HOW: write nothing on a refusal."
        )
        ran = run_artefact(good, [])
        assert answered(ran, "no arguments, as initial takes none") == "(Clock 12)", (
            f"WHAT: the artefact answered {ran.stdout.strip()!r} for the "
            "initial state, which the program computes as (Clock 12). "
            "WHY: the entry takes no argument here, so a build that can only "
            "answer by reading one would fail; and the answer is the "
            "program's, not an example's. "
            f"HOW: read the artefact at {good}"
        )
