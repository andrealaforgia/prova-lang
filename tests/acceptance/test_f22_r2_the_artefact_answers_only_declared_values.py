"""The artefact answers the values the program's own types hold, and
refuses the rest the way the compiler refuses them.

An independent review ran artefacts over values outside the declared
types -- `true` where an Int is declared, `7` where a Bool is, a record
field of the wrong type -- and got answers where `evaluate` refuses the
same call as invalid input. Each of those now carries the status of the
kind of wrong input it is: a value read but of a type the entry does not
declare is told from text that reads as no value at all, and a limit of
the artefact reached while writing a number is told from both. Worse, one of them came back as the exit of
an assurance failure, which says a contract of a verified program did
not hold: a wrong input must never be reported as that.

Beside them: an integer whose answer is longer than this tool writes, and
two texts the compiler's own reader settles one way and the artefact's
reader settled another.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import tempfile

from _f22_fixtures import (
    ANSWERED,
    ASSURANCE_FAILURE,
    ILL_TYPED,
    MALFORMED,
    RESOURCE_EXHAUSTED,
    artefact_of,
    build,
    evaluate,
    hour_clock,
    run_artefact,
)

A = "=>"

# A program of one function per type core-0 has of its own, and one over
# a record of two of them. Nothing in it promises anything, so every
# obligation it owes is settled by a rule of core-0 and the whole of it
# is shown: a build of it publishes an artefact for any of its entries.
THE_TYPES_OF_CORE_0 = f"""(deftype Pair (record (left Int) (right Bool)))

(defn ident
  (sig ((n Int)) -> Int ! pure)
  (examples (example (ident 1) {A} 1))
  n)

(defn flag
  (sig ((b Bool)) -> Bool ! pure)
  (examples (example (flag true) {A} true))
  b)

(defn unitly
  (sig ((u Unit)) -> Unit ! pure)
  (examples (example (unitly ()) {A} ()))
  u)

(defn pair-left
  (sig ((p Pair)) -> Int ! pure)
  (examples (example (pair-left (Pair 1 true)) {A} 1))
  (.left p))
"""


def _an_artefact_of(source: str, entry: str, destination: pathlib.Path):
    target = destination / f"{entry.replace('-', '_')}.py"
    artefact_of(build(source, entry, target), f"the program built for {entry}")
    return target


def test_a_value_outside_the_declared_type_is_refused_as_input():
    """Given artefacts of four entries declaring an Int, a Bool, a Unit
    and a record, when each is run over a value of another type, then
    each refuses as input -- exit 2 -- names the parameter and the type
    it declares, prints no answer and shows no traceback; and the
    compiler refuses the same call as invalid input.

    The exit matters as much as the refusal: exit 3 says a contract of a
    verified program did not hold, which is an assurance failure, and a
    caller that sent the wrong kind of value must never be told that.

    still passes if: the artefact had refused every value -- the valid
    value of each entry is required to be answered below.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        cases = [
            ("ident", "Int", "true", ILL_TYPED,
             "a flag where a number is declared"),
            ("ident", "Int", "()", ILL_TYPED,
             "the unit value where a number is declared"),
            ("flag", "Bool", "7", ILL_TYPED,
             "a number where a flag is declared"),
            ("unitly", "Unit", "7", ILL_TYPED,
             "a number where the unit type is declared"),
            (
                "pair-left",
                "Pair",
                "(Pair true true)",
                ILL_TYPED,
                "a field of the wrong type inside a record",
            ),
            (
                "pair-left",
                "Pair",
                "(Clock 1)",
                MALFORMED,
                "a constructor the program does not declare",
            ),
        ]
        built = {}
        for entry, declared, written, refused_as, about in cases:
            if entry not in built:
                built[entry] = _an_artefact_of(
                    THE_TYPES_OF_CORE_0, entry, destination
                )
            ran = run_artefact(built[entry], [written])

            assert ran.returncode == refused_as, (
                f"WHAT: the artefact of {entry!r} over {written!r} "
                f"({about}) exited {ran.returncode}, not "
                f"{refused_as}. "
                "WHY: a value outside the declared types is input this "
                "artefact cannot answer; an exit of 3 would say a contract "
                "of a verified program did not hold, and an exit of 0 would "
                "answer where the compiler refuses. "
                f"HOW: read what it printed: stdout={ran.stdout[-200:]!r} "
                f"stderr={ran.stderr[-400:]!r}"
            )
            assert ran.returncode != ASSURANCE_FAILURE, ran.stderr[-300:]
            assert ran.stdout.strip() == "", (
                f"WHAT: the artefact of {entry!r} printed "
                f"{ran.stdout[:120]!r} as an answer to {written!r}. "
                "WHY: a refusal has no answer. "
                "HOW: write the refusal on the error channel only."
            )
            assert "Traceback" not in ran.stderr, ran.stderr[-400:]
            for owed in (declared, written.split()[0].lstrip("(")):
                assert owed in ran.stderr, (
                    f"WHAT: the refusal of {written!r} for {entry!r} does not "
                    f"name {owed!r}: {ran.stderr[-400:]!r}. "
                    "WHY: the caller must be told which parameter, which "
                    "declared type and what was read. "
                    "HOW: name all three in the message."
                )

            refused = evaluate(THE_TYPES_OF_CORE_0, entry, [written])
            assert refused.get("status") == "invalid_input", (
                f"WHAT: the compiler answered {refused.get('status')!r} for "
                f"the same call ({entry} over {written!r}). "
                "WHY: this test rests on the two agreeing that the value is "
                "not one the program takes; if the compiler accepts it, the "
                "artefact must too. "
                f"HOW: inspect the answer: {refused}"
            )


def test_the_declared_value_of_each_entry_is_answered():
    """Given the same four artefacts, when each is run over a value of
    the type it declares, then each answers what the program computes --
    so the refusals above are about the values and not about the
    artefacts."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        for entry, written, expected in (
            ("ident", "7", "7"),
            ("flag", "false", "false"),
            ("unitly", "()", "()"),
            ("pair-left", "(Pair 4 true)", "4"),
        ):
            target = _an_artefact_of(THE_TYPES_OF_CORE_0, entry, destination)
            ran = run_artefact(target, [written])
            assert ran.returncode == ANSWERED, (
                f"WHAT: the artefact of {entry!r} over {written!r} exited "
                f"{ran.returncode}. "
                "WHY: that value is of the type the entry declares. "
                f"HOW: read what it printed: {ran.stderr[-400:]!r}"
            )
            assert ran.stdout.strip() == expected, (
                f"WHAT: it answered {ran.stdout.strip()!r} and the program "
                f"computes {expected!r}. "
                f"HOW: read the artefact at {target}"
            )


def test_a_wrong_typed_field_of_the_hour_clock_is_refused_not_answered():
    """Given the artefact of the hour clock's `step`, when it is run over
    `(Clock true)` -- a record whose own field is of the wrong type -- and
    over `(Tick)` where a Clock is declared, then each is refused as
    input and neither is reported as a contract that did not hold.

    still passes if: the artefact had only checked the outermost
    constructor -- the first case is a declared constructor of the right
    type with a wrong field inside it.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        target = _an_artefact_of(hour_clock(), "step", pathlib.Path(tmp_dir))
        for arguments, about in (
            (["(Clock true)", "(Tick)"], "a flag inside the hour of a clock"),
            (["(Tick)", "(Tick)"], "an event where a clock is declared"),
        ):
            ran = run_artefact(target, arguments)
            assert ran.returncode == ILL_TYPED, (
                f"WHAT: the artefact over {about} exited {ran.returncode}. "
                "WHY: neither value is of the type `step` declares, and the "
                "program promises nothing about either. "
                f"HOW: read what it printed: {ran.stderr[-400:]!r}"
            )
            assert "Traceback" not in ran.stderr, ran.stderr[-400:]
            assert "Clock" in ran.stderr, ran.stderr[-400:]

            refused = evaluate(hour_clock(), "step", arguments)
            assert refused.get("status") == "invalid_input", (
                f"WHAT: the compiler answered {refused.get('status')!r} for "
                f"the same call over {about}. "
                f"HOW: inspect the answer: {refused}"
            )


def test_an_answer_too_long_to_write_is_refused_as_the_compiler_refuses_it():
    """Given a program that multiplies its argument by a number of 4000
    digits -- so an answer of more than the 4000 digits this tool writes
    -- when the artefact is run over 10, then it refuses as input, names
    the limit, and shows no traceback; and the compiler refuses the same
    call with `resource_exhausted`.

    still passes if: the artefact had died in the conversion -- the
    refusal is required to name the limit, and a traceback is required
    to be absent.
    """
    # The tool reads an integer literal of at most 1000 digits, so the
    # 4000 digits this answer passes are reached by multiplying by a
    # literal of 1000 digits four times over. Each product has a literal
    # for one of its operands, which is what this profile translates.
    literal = "9" * 1000
    source = (
        "(defn big\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        f"  (examples (example (big 0) {A} 0))\n"
        f"  (* {literal} (* {literal} (* {literal} (* {literal} n)))))\n"
    )
    with tempfile.TemporaryDirectory() as tmp_dir:
        target = _an_artefact_of(source, "big", pathlib.Path(tmp_dir))

        ran = run_artefact(target, ["10"])
        assert ran.returncode == RESOURCE_EXHAUSTED, (
            f"WHAT: the artefact exited {ran.returncode} where its answer is "
            "longer than this tool writes. "
            "WHY: the limit on the digits an answer writes is the compiler's "
            "own, published and enforced for the same program; the artefact "
            "must refuse rather than die inside the conversion. "
            f"HOW: read what it printed: {ran.stderr[-500:]!r}"
        )
        assert "Traceback" not in ran.stderr, ran.stderr[-500:]
        assert "4000" in ran.stderr, (
            f"WHAT: the refusal does not name the limit: {ran.stderr[-400:]!r}. "
            "WHY: the caller has to know which number was passed. "
            "HOW: name the digits it writes and the digits the answer reached."
        )

        refused = evaluate(source, "big", ["10"])
        assert refused.get("status") == "resource_exhausted", (
            f"WHAT: the compiler answered {refused.get('status')!r} for the "
            "same call. "
            "WHY: this test rests on the two agreeing that the answer cannot "
            "be written. "
            f"HOW: inspect the answer: {refused}"
        )

        answered = run_artefact(target, ["0"])
        assert answered.returncode == ANSWERED and answered.stdout.strip() == "0", (
            f"WHAT: the artefact exited {answered.returncode} answering "
            f"{answered.stdout.strip()!r} for 0. "
            "WHY: the refusal above is about the length of one answer, not "
            "about the program. "
            f"HOW: read the artefact at {target}"
        )


def test_the_artefact_reads_a_value_the_way_the_compiler_reads_one():
    """Given the artefact of `ident`, when it is run over texts the
    compiler's own reader settles -- `1_0`, which it refuses, and
    `1;a comment`, which it reads as 1 -- then the artefact settles each
    one the same way.

    `1_0` is ten to Python's own reader and nothing at all to this
    language; a comment runs to the end of its line in both.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        target = _an_artefact_of(
            THE_TYPES_OF_CORE_0, "ident", pathlib.Path(tmp_dir)
        )

        refused = run_artefact(target, ["1_0"])
        assert refused.returncode == MALFORMED, (
            f"WHAT: the artefact answered {refused.stdout.strip()!r} for the "
            "text '1_0', which this language does not read as a number. "
            "WHY: a value the compiler refuses must not be a value the "
            "artefact answers; Python reads the underscore of 1_0 and core-0 "
            "does not. "
            f"HOW: read the artefact's reader: {refused.stderr[-300:]!r}"
        )
        assert evaluate(THE_TYPES_OF_CORE_0, "ident", ["1_0"]).get("status") == (
            "invalid_input"
        ), "the compiler reads 1_0 after all; this test describes the old rule"

        commented = run_artefact(target, ["1;a comment"])
        assert commented.returncode == ANSWERED, (
            f"WHAT: the artefact exited {commented.returncode} over "
            "'1;a comment', which the compiler reads as 1. "
            "WHY: a comment runs from its ';' to the end of its line in this "
            "language, wherever the text stands. "
            f"HOW: read what it printed: {commented.stderr[-300:]!r}"
        )
        assert commented.stdout.strip() == "1", commented.stdout
        answered = evaluate(THE_TYPES_OF_CORE_0, "ident", ["1;a comment"])
        assert (answered.get("result") or {}).get("value") == "1", answered
