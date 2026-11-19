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
    ANSWERED,
    ASSURANCE_FAILURE,
    REFUSED_THE_INPUT,
    answered,
    artefact_of,
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


# Three programs that read the rest of what this slice translates: a
# match whose clauses overlap, so the order they are tried in decides
# the answer; equality over values built by a constructor; and a record
# read through its field. Each one promises nothing, so every obligation
# it owes is settled by a rule of core-0.
OVERLAPPING_CLAUSES = f"""(defn classify
  (sig ((n Int)) -> Int ! pure)
  (examples
    (example (classify 1) {A} 10)
    (example (classify 7) {A} 20))
  (match n (1 10) (_ 20)))
"""

EQUALITY_OVER_CONSTRUCTED_VALUES = f"""(deftype Point (record (x Int) (y Int)))

(defn same
  (sig ((a Point) (b Point)) -> Bool ! pure)
  (examples
    (example (same (Point 1 2) (Point 1 2)) {A} true)
    (example (same (Point 1 2) (Point 2 1)) {A} false))
  (= a b))
"""

A_RECORD_AND_A_BIG_NUMBER = f"""(deftype Holder (record (held Int) (flagged Bool)))

(defn held-twice
  (sig ((h Holder)) -> Int ! pure)
  (examples (example (held-twice (Holder 3 true)) {A} 6))
  (* 2 (.held h)))
"""

# The texts an argument may be written with that a reader settles one
# way and a careless one another: Python reads the underscores and the
# other bases, this language reads an optional sign and digits, and a
# comment runs from its ';' to the end of its line.
THIRTY_ODD_LITERALS = (
    "7", "-7", "+7", "0", "-0", "007", "1_0", "1__0", "_1", "1_", "0x10",
    "0b11", "0o17", "1e3", "1.0", ".5", "7.", "1j", "  7  ", "7;a comment",
    ";only a comment", "7 ;trailing", "nan", "inf", "true7", "7true", "--7",
    "+-7", "7+", str(10**30),
)


def _one_artefact(tmp_path_factory, source: str, entry: str):
    destination = tmp_path_factory.mktemp("agreeing")
    target = destination / f"{entry.replace('-', '_')}.py"
    artefact_of(build(source, entry, target), f"the program built for {entry}")
    return target


@pytest.fixture(scope="module")
def artefacts_of_the_three_programs(tmp_path_factory):
    """One artefact per entry the law below is read over, built once."""
    return {
        "classify": (
            OVERLAPPING_CLAUSES,
            _one_artefact(tmp_path_factory, OVERLAPPING_CLAUSES, "classify"),
        ),
        "same": (
            EQUALITY_OVER_CONSTRUCTED_VALUES,
            _one_artefact(
                tmp_path_factory, EQUALITY_OVER_CONSTRUCTED_VALUES, "same"
            ),
        ),
        "held-twice": (
            A_RECORD_AND_A_BIG_NUMBER,
            _one_artefact(tmp_path_factory, A_RECORD_AND_A_BIG_NUMBER, "held-twice"),
        ),
    }


@settings(derandomize=True, max_examples=20, deadline=None)
@given(number=st.integers(min_value=-3, max_value=9))
def test_the_artefact_answers_as_the_evaluator_does_over_the_rest_of_core_0(
    artefacts_of_the_three_programs, number
):
    """LAW2, read over the rest of what this slice translates: a match
    whose clauses overlap, equality over values a constructor built, a
    record read through its field, and a number far past 64 bits.

    The order of the clauses decides the answer of `classify`: 1 is
    answered 10 by the first clause and every other number is answered
    20 by the second, so a translation that tried them the other way
    round would answer 20 for 1. Equality over two constructed values is
    the program's own equality, not the identity of two objects.

    still passes if: both sides were wrong in the same way -- the
    examples each program declares are run by the compiler before a
    build is allowed, and the hand-computed answers of the hour clock
    are asserted in tests/acceptance/test_f22_c2 and test_f22_c5.
    """
    source, target = artefacts_of_the_three_programs["classify"]
    written = str(number)
    by_the_compiler = (
        evaluate(source, "classify", [written]).get("result") or {}
    ).get("value")
    assert answered(run_artefact(target, [written]), written) == by_the_compiler, (
        f"WHAT: for {written!r} the artefact of `classify` and the compiler "
        f"answer differently; the compiler answers {by_the_compiler!r}. "
        "WHY: the clauses of a match are tried in the order the source "
        "writes them, and these two overlap: 1 is answered by the first and "
        "every other number by the second. "
        f"HOW: read the artefact at {target}"
    )

    source, target = artefacts_of_the_three_programs["same"]
    for left, right in ((number, number), (number, number + 1)):
        arguments = [f"(Point {left} {left})", f"(Point {right} {right})"]
        by_the_compiler = (
            evaluate(source, "same", arguments).get("result") or {}
        ).get("value")
        assert answered(
            run_artefact(target, arguments), " ".join(arguments)
        ) == by_the_compiler, (
            f"WHAT: for {arguments} the artefact of `same` and the compiler "
            f"answer differently; the compiler answers {by_the_compiler!r}. "
            "WHY: two values of a record are the same value when their "
            "constructor and every field agree -- not when they are the same "
            "object, which is what a translation by the identity of two "
            "objects would answer. "
            f"HOW: read the artefact at {target}"
        )

    source, target = artefacts_of_the_three_programs["held-twice"]
    big = 10 ** 40 + number
    arguments = [f"(Holder {big} true)"]
    by_the_compiler = (
        evaluate(source, "held-twice", arguments).get("result") or {}
    ).get("value")
    assert answered(run_artefact(target, arguments), str(arguments)) == (
        by_the_compiler
    ), (
        f"WHAT: for {arguments} the artefact of `held-twice` and the compiler "
        f"answer differently; the compiler answers {by_the_compiler!r}. "
        "WHY: a record is read through the field its declaration names, and "
        "an integer far past 64 bits is answered exactly. "
        f"HOW: read the artefact at {target}"
    )


@settings(derandomize=True, max_examples=30, deadline=None)
@given(place=st.integers(min_value=0, max_value=len(THIRTY_ODD_LITERALS) - 1))
def test_the_artefact_reads_an_argument_as_the_compiler_reads_one(
    artefacts_of_the_three_programs, place
):
    """LAW2 over the reader: for each of 30 texts an argument may be
    written with, the artefact answers exactly what the compiler answers,
    and refuses exactly where the compiler refuses.

    Python's own reader accepts `1_0`, `0x10` and `1e3`; this language
    accepts an optional sign and digits, and a comment from its ';' to
    the end of its line. A value the compiler refuses must never be a
    value the artefact answers.
    """
    source, target = artefacts_of_the_three_programs["classify"]
    written = THIRTY_ODD_LITERALS[place]

    by_the_compiler = evaluate(source, "classify", [written])
    value = (by_the_compiler.get("result") or {}).get("value")
    ran = run_artefact(target, [written])

    if value is not None:
        assert ran.returncode == ANSWERED and ran.stdout.strip() == value, (
            f"WHAT: the compiler reads {written!r} and answers {value!r}; the "
            f"artefact exited {ran.returncode} answering "
            f"{ran.stdout.strip()!r}. "
            "WHY: one grammar for the values of this language, wherever they "
            "are read. "
            f"HOW: read the artefact's reader: {ran.stderr[-300:]!r}"
        )
        return
    assert ran.returncode == REFUSED_THE_INPUT, (
        f"WHAT: the compiler refuses {written!r} "
        f"({by_the_compiler.get('status')!r}) and the artefact exited "
        f"{ran.returncode} answering {ran.stdout.strip()!r}. "
        "WHY: a text that is not a value of this language is not a value the "
        "artefact answers either. "
        f"HOW: read the artefact's reader: {ran.stderr[-300:]!r}"
    )
    assert "Traceback" not in ran.stderr, ran.stderr[-300:]


def test_a_contract_that_is_not_a_flag_never_reaches_an_artefact():
    """Given a program whose precondition is a number rather than a
    flag, when the Owner asks the compiler about it, then it is refused
    before any build -- which is why an artefact that read a contract's
    value as Python reads the truth of a number, instead of as the one
    value `true`, cannot be told apart from one that does not.

    Recorded here rather than left unsaid: a mutation of that reading
    survives every test, and this is the rule that excludes the input
    which would show it.
    """
    a_number_for_a_contract = f"""(defn odd-contract
  (sig ((n Int)) -> Int ! pure)
  (requires n)
  (examples (example (odd-contract 1) {A} 1))
  n)
"""
    answer = evaluate(a_number_for_a_contract, "odd-contract", ["1"])
    assert answer.get("status") == "invalid_program", (
        f"WHAT: a precondition that is a number was answered "
        f"{answer.get('status')!r}. "
        "WHY: the argument that a contract's value is always the flag true "
        "or the flag false rests on this refusal; if the checker accepts "
        "such a program, the artefact must read the truth of a contract the "
        "way the evaluator does and a test must show it. "
        f"HOW: inspect the answer: {answer}"
    )
    assert "type_mismatch" in {
        d.get("category") for d in answer.get("diagnostics") or []
    }, answer
