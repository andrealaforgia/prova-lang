"""F22 criterion 2: given a fully verified program and an entry function,
then `build` writes one artefact and records which entry and which
configuration it used.

SPEC.md lines 491-494: build once and execute fresh inputs; the first
adapter invokes the named entry function selected in build metadata. So
the artefact is one file, it says which entry it was built for and under
which configuration, and it computes the answer when it is run by an
interpreter that has never heard of this compiler.

Drives only the `prova` command's real JSON stdin/stdout surface and the
file it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

from _f22_fixtures import (
    PRECONDITION_UNMET,
    REFUSED_THE_INPUT,
    answered,
    artefact_of,
    build,
    digest_of,
    files_under,
    header_of,
    hour_clock,
    run_artefact,
    the_manifest,
)


def test_c2_one_artefact_is_written_and_nothing_else():
    """Given the shipped hour clock, whose every obligation is discharged
    and whose 8 examples all pass, and an empty destination directory,
    when the Owner asks for a build of its `step` function into
    `clock.py`, then exactly that one file is there afterwards, and the
    answer records the path it wrote.

    still passes if: the build had left its temporary file behind beside
    the artefact -- the destination is required to hold exactly one file.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        target = destination / "clock.py"
        answer = build(hour_clock(), "step", target)
        written = files_under(destination)
        published = artefact_of(answer, "the shipped hour clock")

        assert sorted(written) == ["clock.py"], (
            f"WHAT: the destination holds {sorted(written)} after one build. "
            "WHY: a build publishes one artefact; a temporary file left "
            "beside it, or a second file, is something the Owner did not ask "
            "for and must not find. "
            f"HOW: write through a temporary file in the same directory and "
            f"rename it over the destination."
        )
        assert published["path"] == str(target), (
            f"WHAT: the answer records {published.get('path')!r} and the "
            f"request named {str(target)!r}. "
            "WHY: the Owner must be told which file they now hold. "
            f"HOW: inspect the answer: {published}"
        )
        assert target.read_text(encoding="utf-8").startswith('"""'), (
            "WHAT: the artefact does not begin with a docstring saying what "
            f"it is: {target.read_text(encoding='utf-8')[:120]!r}. "
            "WHY: a reader who finds this file must learn from the file "
            "itself what it is and what it was built from. "
            "HOW: write the docstring first."
        )


def test_c2_the_artefact_records_its_entry_and_its_configuration():
    """Given a build of the hour clock's `step` function, when the Owner
    reads the artefact, then it records as data the entry it invokes, the
    profile it was built for, the solver pin behind the evidence and the
    four budgets the build ran under -- and the build answer records the
    same.

    still passes if: the artefact recorded a configuration of its own
    invention -- the profile, the solver pin and the budget maxima are
    compared against what the `discover` manifest publishes.
    """
    manifest = (the_manifest().get("result") or {})
    the_profile = manifest["profile"]
    the_solver = manifest["solver"]
    the_budgets = manifest["resource_limits"]["budgets"]["build"]

    with tempfile.TemporaryDirectory() as tmp_dir:
        target = pathlib.Path(tmp_dir) / "clock.py"
        answer = build(hour_clock(), "step", target)
        published = artefact_of(answer, "the shipped hour clock")
        recorded = header_of(target)

    assert recorded["entry"] == "step" == published["entry"], (
        f"WHAT: the artefact records the entry {recorded.get('entry')!r} and "
        f"the answer records {published.get('entry')!r}; the request asked "
        "for 'step'. "
        "WHY: SPEC.md line 494: the adapter invokes the entry named in the "
        "build metadata, so the metadata must name the one that was asked "
        "for. "
        f"HOW: inspect the artefact: {recorded}"
    )
    configuration = recorded["configuration"]
    assert configuration["profile"] == the_profile, (
        f"WHAT: the artefact records the profile {configuration.get('profile')} "
        f"and this tool publishes {the_profile}. "
        "WHY: verification binds to the profile the output was built for; a "
        "profile of the artefact's own invention cannot be looked up. "
        f"HOW: record the profile the manifest publishes: {configuration}"
    )
    assert configuration["solver"] == the_solver, (
        f"WHAT: the artefact records the solver {configuration.get('solver')} "
        f"and this tool publishes {the_solver}. "
        "WHY: the evidence that certified this program rests on that solver "
        "at that pinned version, and an artefact that does not name it "
        "cannot be checked against the word it carries. "
        f"HOW: record the solver the manifest publishes: {configuration}"
    )
    assert configuration["budgets"] == the_budgets, (
        f"WHAT: the artefact records the budgets "
        f"{sorted(configuration.get('budgets') or {})} and this tool "
        f"publishes {sorted(the_budgets)} for the verification behind a "
        "build. "
        "WHY: the configuration an answer binds to includes the budgets the "
        "run stood inside; one number, in one place. "
        f"HOW: record the budgets the manifest publishes: {configuration}"
    )
    assert published["configuration"] == configuration, (
        "WHAT: the build answer and the artefact record different "
        f"configurations: {published['configuration']} against "
        f"{configuration}. "
        "WHY: the Owner reads one of the two and must not be told two "
        "different things. "
        "HOW: write both from one record."
    )
    assert recorded["evidence_digest"] == published["evidence_digest"], (
        f"WHAT: the artefact records the evidence digest "
        f"{recorded.get('evidence_digest')!r} and the answer records "
        f"{published.get('evidence_digest')!r}. "
        "WHY: the digest ties the artefact to the evidence that certified "
        "it; two different digests tie it to neither. "
        f"HOW: write both from one record."
    )
    assert len(recorded["evidence_digest"]) == 64, (
        f"WHAT: the evidence digest is {recorded.get('evidence_digest')!r}. "
        "WHY: it is a SHA-256 over the evidence, as every other digest this "
        "tool publishes is, so the Owner recomputes it the same way. "
        "HOW: take the digest over the evidence with SHA-256."
    )
    assert recorded["source_revision"] == digest_of(hour_clock()), (
        f"WHAT: the artefact records the revision "
        f"{recorded.get('source_revision')!r} for a source whose SHA-256 is "
        f"{digest_of(hour_clock())!r}. "
        "WHY: criterion 3: the recorded revision is the verified one. "
        f"HOW: inspect the artefact: {recorded}"
    )


def test_c2_the_artefact_computes_a_fresh_input_without_the_compiler():
    """Given a build of the hour clock's `step` function, when the
    artefact is run by an isolated interpreter over `(Clock 5)` and
    `(Tick)` -- an input no example of the program declares -- then it
    prints `(Outcome (Clock 6) true)`, computed by hand from the program:
    5 is not 12, so the hour becomes 6 and the tick is accepted.

    still passes if: the artefact had been a table of the three `step`
    examples -- 5 is in none of them.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        target = pathlib.Path(tmp_dir) / "clock.py"
        build(hour_clock(), "step", target)

        ran = run_artefact(target, ["(Clock 5)", "(Tick)"])
        assert answered(ran, "(Clock 5) and (Tick)") == "(Outcome (Clock 6) true)", (
            f"WHAT: the artefact answered {ran.stdout.strip()!r} for the hour "
            "5 and a tick, and the program computes (Outcome (Clock 6) true). "
            "WHY: SPEC.md line 491: build once and execute fresh inputs; an "
            "artefact that cannot answer an input outside its own examples "
            "has not translated the program. "
            f"HOW: read the artefact at {target}"
        )

        twice = run_artefact(target, ["(Clock 5)", "(Tick)"])
        assert answered(twice, "the same input a second time") == (
            "(Outcome (Clock 6) true)"
        ), "the artefact answered two different things for one input"

        at_the_turn = run_artefact(target, ["(Clock 12)", "(Tick)"])
        assert answered(at_the_turn, "(Clock 12) and (Tick)") == (
            "(Outcome (Clock 1) true)"
        ), (
            f"WHAT: the artefact answered {at_the_turn.stdout.strip()!r} at "
            "the hour 12, where the clock turns back to 1. "
            "WHY: the branch of the program must be in the artefact, not the "
            "answer of the example that happens to cover it. "
            f"HOW: read the artefact at {target}"
        )


def test_c2_the_artefact_refuses_what_it_cannot_answer_without_a_traceback():
    """Given a build of the hour clock's `step` function, when the
    artefact is run over too few arguments, over text that is not a
    value, and over an hour of 99 which its own precondition refuses,
    then each run refuses in words with its own exit status and none of
    them ends in a traceback.

    The hour of 99 is a well-formed value of the declared type that the
    entry's precondition refuses, which now carries the status of its
    own kind rather than the one that says a contract of a verified
    program did not hold.

    still passes if: the artefact had answered an input its precondition
    refuses -- the refusal of (Clock 99) is required, and its status is
    required to differ from the refusal of input it could not read.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        target = pathlib.Path(tmp_dir) / "clock.py"
        build(hour_clock(), "step", target)

        cases = [
            ("too few arguments", [], REFUSED_THE_INPUT, "2"),
            ("text that is not a value", ["(Clock", "(Tick)"], REFUSED_THE_INPUT, ""),
            (
                "a constructor the program does not declare",
                ["(Pocket 5)", "(Tick)"],
                REFUSED_THE_INPUT,
                "Pocket",
            ),
            (
                "an hour its own precondition refuses",
                ["(Clock 99)", "(Tick)"],
                PRECONDITION_UNMET,
                "valid-state",
            ),
        ]
        for about, arguments, expected_exit, named in cases:
            ran = run_artefact(target, arguments)
            assert ran.returncode == expected_exit, (
                f"WHAT: the artefact run over {about} exited "
                f"{ran.returncode}, not {expected_exit}. "
                "WHY: an artefact refuses in words, with a status that tells "
                "an input it could not read from a contract of the program "
                "it could not meet, and never answers either as a result. "
                f"HOW: read what it printed: stdout={ran.stdout[-300:]!r} "
                f"stderr={ran.stderr[-400:]!r}"
            )
            assert "Traceback" not in ran.stderr, (
                f"WHAT: the artefact ended in a traceback over {about}: "
                f"{ran.stderr[-500:]!r}. "
                "WHY: this tool never ends in a traceback and neither does "
                "what it builds. "
                "HOW: refuse by name where the failure happens."
            )
            assert ran.stdout.strip() == "", (
                f"WHAT: the artefact printed {ran.stdout[:200]!r} on its "
                f"answer channel while refusing {about}. "
                "WHY: a refusal has no answer, and a caller reading the "
                "answer channel must not find one. "
                "HOW: write the refusal on the error channel."
            )
            assert named in ran.stderr, (
                f"WHAT: the refusal of {about} does not name {named!r}: "
                f"{ran.stderr[-400:]!r}. "
                "WHY: a refusal names what failed, so the reader knows which "
                "input or which contract to look at. "
                "HOW: name it in the message."
            )
