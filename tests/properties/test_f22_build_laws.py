"""The three laws of F22, each over a family of programs rather than one.

LAW1: a build publishes an artefact only when the whole program was
shown; for a program it was not shown of, the answer carries no artefact
and the destination is left as it was.
LAW2: the artefact answers every input the way the compiler's own
evaluator answers it -- the same value, and a refusal where the evaluator
refuses.
LAW3: the revision an artefact records is the revision of the source that
was verified, for every verified program built.

Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import sys

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "acceptance"))

from _f22_fixtures import (  # noqa: E402
    ASSURANCE_FAILURE,
    answered,
    build,
    digest_of,
    evaluate,
    files_under,
    header_of,
    hour_clock,
    run_artefact,
)

A = "=>"


def _a_program_whose_example_is_wrong(k: int) -> str:
    """A program that adds `k`, and declares one example claiming an
    answer one too large. Every obligation of it is discharged and its
    one example does not pass, so the whole was never shown."""
    return (
        f"(defn plus-{abs(k)}\n"
        f"  (sig ((n Int)) -> Int ! pure)\n"
        f"  (requires (>= n 0))\n"
        f"  (ensures (>= result 0))\n"
        f"  (examples (example (plus-{abs(k)} 1) {A} {1 + k + 1}))\n"
        f"  (+ n {k}))\n"
    )


def _a_verified_program(k: int) -> str:
    """A program that adds `k`, with its example telling the truth."""
    return (
        f"(defn plus-{abs(k)}\n"
        f"  (sig ((n Int)) -> Int ! pure)\n"
        f"  (requires (>= n 0))\n"
        f"  (ensures (>= result 0))\n"
        f"  (examples (example (plus-{abs(k)} 1) {A} {1 + k}))\n"
        f"  (+ n {k}))\n"
    )


@settings(derandomize=True, max_examples=12, deadline=None)
@given(k=st.integers(min_value=0, max_value=40))
def test_only_a_program_shown_whole_is_ever_built(tmp_path_factory, k):
    """LAW1: for a program whose own example does not pass, the build
    refuses, carries no artefact and leaves the destination empty.

    still passes if: the tool refused every build -- LAW3 below builds
    the same family with its examples telling the truth and requires an
    artefact each time.
    """
    destination = tmp_path_factory.mktemp("refused")
    answer = build(
        _a_program_whose_example_is_wrong(k),
        f"plus-{k}",
        destination / f"plus_{k}.py",
    )
    assert answer.get("status") == "not_verified", (
        f"WHAT: a program whose only example claims the wrong answer was "
        f"answered {answer.get('status')!r} for k={k}. "
        "WHY: the build fails closed while the program was not shown whole. "
        f"HOW: inspect the answer: {answer}"
    )
    assert not answer.get("result"), f"the refusal carried a result: {answer}"
    assert files_under(destination) == {}, (
        f"WHAT: the refused build wrote {sorted(files_under(destination))}. "
        "WHY: a refused build writes nothing. "
        "HOW: decide the refusal before anything is written."
    )


@settings(derandomize=True, max_examples=12, deadline=None)
@given(k=st.integers(min_value=0, max_value=40))
def test_a_verified_program_is_built_and_records_its_own_revision(
    tmp_path_factory, k
):
    """LAW3: every verified program of this family is built, the artefact
    records the SHA-256 of the exact source that was verified, and it
    computes that program's own answer -- so each build translated the
    program it was given and not a copy of another.
    """
    source = _a_verified_program(k)
    destination = tmp_path_factory.mktemp("built")
    target = destination / f"plus_{k}.py"
    answer = build(source, f"plus-{k}", target)
    published = artefact_of(answer, f"the program adding {k}")
    recorded = header_of(target)

    assert recorded["source_revision"] == digest_of(source) == (
        published["source_revision"]
    ), (
        f"WHAT: for k={k} the artefact records "
        f"{recorded.get('source_revision')!r}, the answer records "
        f"{published.get('source_revision')!r} and the SHA-256 of the source "
        f"is {digest_of(source)!r}. "
        "WHY: the artefact stands on the verification of exactly those "
        "characters. "
        "HOW: record the revision of the submitted source."
    )
    ran = run_artefact(target, ["7"])
    assert answered(ran, f"7 through the program adding {k}") == str(7 + k), (
        f"WHAT: for k={k} the artefact answered {ran.stdout.strip()!r} for 7, "
        f"and the program computes {7 + k}. "
        "WHY: each artefact must be the program it was built from; one "
        "generated from another program would answer another number. "
        f"HOW: read the artefact at {target}"
    )


@pytest.fixture(scope="module")
def two_artefacts_of_the_hour_clock(tmp_path_factory):
    """One build of the shipped hour clock per entry this law is read
    over, built once for every input the law is read on."""
    destination = tmp_path_factory.mktemp("differential")
    built = {}
    for entry in ("valid-state", "step"):
        target = destination / f"{entry.replace('-', '_')}.py"
        build(hour_clock(), entry, target)
        built[entry] = target
    return built


@settings(derandomize=True, max_examples=30, deadline=None)
@given(hour=st.integers(min_value=-5, max_value=24))
def test_the_artefact_answers_as_the_evaluator_does(
    two_artefacts_of_the_hour_clock, hour
):
    """LAW2: for every hour, the artefact of `valid-state` answers the
    text the compiler's evaluator answers, and the artefact of `step`
    either answers the evaluator's value or refuses exactly where the
    evaluator refuses the call.

    The whole of the semantics this slice translates is read here: whole
    numbers, a record and its field, a union and a match over it,
    comparison, conjunction and a contract.

    still passes if: both sides were wrong in the same way -- the hours
    1, 12 and 13 are also asserted against answers computed by hand in
    tests/acceptance/test_f22_c2 and test_f22_c5.
    """
    source = hour_clock()
    written = f"(Clock {hour})"

    by_the_compiler = evaluate(source, "valid-state", [written])
    by_the_artefact = run_artefact(
        two_artefacts_of_the_hour_clock["valid-state"], [written]
    )
    expected = (by_the_compiler.get("result") or {}).get("value")
    assert expected is not None, (
        f"WHAT: the compiler answered no value for valid-state of {written}: "
        f"{by_the_compiler}. "
        "WHY: valid-state promises nothing about its argument, so every hour "
        "is answered; this law needs the compiler's own answer to compare "
        "with. "
        f"HOW: inspect the answer: {by_the_compiler}"
    )
    assert answered(by_the_artefact, written) == expected, (
        f"WHAT: for {written} the artefact answered "
        f"{by_the_artefact.stdout.strip()!r} and the compiler answered "
        f"{expected!r}. "
        "WHY: SPEC.md line 485: parsing, checking, encoding, examples and "
        "generated execution must implement the same semantics. "
        "HOW: translate the operator the way the evaluator runs it."
    )

    stepped = evaluate(source, "step", [written, "(Tick)"])
    ran = run_artefact(two_artefacts_of_the_hour_clock["step"], [written, "(Tick)"])
    value = (stepped.get("result") or {}).get("value")
    if value is not None:
        assert answered(ran, f"{written} and (Tick)") == value, (
            f"WHAT: for {written} the artefact answered "
            f"{ran.stdout.strip()!r} and the compiler answered {value!r}. "
            "WHY: the same semantics, through the record, the union and the "
            "match this program is written with. "
            "HOW: translate the match the way the evaluator runs it."
        )
    else:
        assert ran.returncode == ASSURANCE_FAILURE, (
            f"WHAT: the compiler refuses step of {written} and the artefact "
            f"exited {ran.returncode}: stdout={ran.stdout[-200:]!r} "
            f"stderr={ran.stderr[-300:]!r}. "
            "WHY: a contract the compiler refuses must be refused by what it "
            "built; answering it would be the artefact promising more than "
            "the program. "
            "HOW: check the precondition in the artefact and refuse by name."
        )
        assert "Traceback" not in ran.stderr, ran.stderr[-400:]
