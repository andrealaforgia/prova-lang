"""The boundary of a built artefact reads every argument before it
types any of them, refuses bytes that are no text, refuses a value
nested past the limit this tool publishes, and reaches no limit of the
interpreter it happens to run under.

An adversarial review found four ways in: an argument carrying a byte
that is not UTF-8 was answered because the comment scanner stepped over
it; a wrong type was reported where one of the arguments could not be
read at all, which the compiler reports the other way round; a value
nested 129 forms deep was answered and one nested 500 deep ended as a
failure of the file; and a caller who lowered the interpreter's own
limit on the digits of a decimal number got a failure of the file for an
input, or a file that could not even be imported.

Every case runs the BUILT artefact as the Owner runs it. The two cases
that need a lowered interpreter limit set it in the environment of that
run, which is the way a caller lowers it.

Drives only the `prova` command's real JSON stdin/stdout surface and the
artefact it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

import pytest

from _f22_fixtures import evaluate, run_artefact
from _f23_fixtures import (
    ANSWERED,
    A_FAILURE_OF_THE_FILE,
    ILL_TYPED,
    MALFORMED,
    RESOURCE_EXHAUSTED,
    an_artefact_of,
    first_line_word,
    reservation_source,
)

A = "=>"

# The nesting this tool publishes under 'expression_nesting', and the
# digits it publishes under 'integer_literal_digits'. Both are read from
# what `discover` publishes, so this file pins no number of its own.
from _f23_fixtures import the_published_table  # noqa: E402

# A program of one entry that hands its argument back, and one of an
# entry that takes nothing and answers a number of 641 digits -- one
# digit more than the lowest limit on decimal digits a caller may set.
SIX_HUNDRED_AND_FORTY_ONE_DIGITS = "9" * 641
THE_LONG_WAY_ROUND = f"""(defn echo
  (sig ((n Int)) -> Int ! pure)
  (examples (example (echo 1) {A} 1))
  n)

(defn constant
  (sig () -> Int ! pure)
  (examples (example (constant) {A} {SIX_HUNDRED_AND_FORTY_ONE_DIGITS}))
  {SIX_HUNDRED_AND_FORTY_ONE_DIGITS})
"""


def published_limit(named: str) -> int:
    """One resource limit this tool publishes, read from `discover` so
    that the number the artefact enforces is the number a caller is
    promised and no test invents one."""
    import json

    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"operation": "discover"}),
        capture_output=True,
        text=True,
        timeout=60.0,
    )
    assert proc.returncode == 0, proc.stderr[-300:]
    published = (json.loads(proc.stdout).get("result") or {}).get(
        "resource_limits"
    ) or {}
    limits = published.get("limits") or {}
    if named in limits:
        return limits[named]["maximum"]
    raise AssertionError(
        f"WHAT: the tool publishes no resource limit named {named!r}: "
        f"{sorted(limits)}. "
        "WHY: the artefact must enforce the number its compiler publishes, "
        "and this test reads that number rather than keeping a copy. "
        "HOW: read what 'discover' publishes under resource_limits."
    )


def run_with_raw_arguments(path: pathlib.Path, arguments: list):
    """One run of the artefact whose arguments are bytes, which is what
    a shell hands a program: an argument is not required to be text, and
    the artefact must answer about one that is not."""
    return subprocess.run(
        [sys.executable.encode(), b"-I", str(path).encode(), *arguments],
        capture_output=True,
        timeout=30.0,
    )


def run_with_lowered_digits(path: pathlib.Path, arguments: list, digits: int):
    """One run of the artefact by an interpreter whose own limit on the
    decimal digits of an integer the caller lowered."""
    import os

    environment = dict(os.environ, PYTHONINTMAXSTRDIGITS=str(digits))
    # `-X int_max_str_digits` is how a caller lowers the limit for one
    # run; the environment variable says the same thing, and an
    # isolated interpreter reads none, so the option is used here and
    # the variable is set beside it for a caller who reads this later.
    return subprocess.run(
        [
            sys.executable,
            "-I",
            "-X",
            f"int_max_str_digits={digits}",
            str(path),
            *arguments,
        ],
        capture_output=True,
        text=True,
        timeout=30.0,
        env=environment,
    )


@pytest.fixture(scope="module")
def the_built_component():
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield an_artefact_of(
            reservation_source(), "step", pathlib.Path(tmp_dir)
        )


@pytest.fixture(scope="module")
def two_long_way_round_artefacts():
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        yield {
            entry: an_artefact_of(THE_LONG_WAY_ROUND, entry, destination)
            for entry in ("echo", "constant")
        }


def test_an_argument_that_is_not_text_is_refused_as_malformed(
    the_built_component,
):
    """Given the built reservation component, when it is run over an
    argument carrying the byte 0xFF, which no UTF-8 text carries, then
    it is refused as malformed with no result value -- and not answered
    because a comment runs to the end of a line.

    still passes if: the refusal had come from the type check instead --
    the word is required to be MALFORMED, which is what text that cannot
    be read as a value carries.
    """
    ran = run_with_raw_arguments(the_built_component, [b"1;\xff", b"(Reserve)"])
    printed = ran.stdout.decode("utf-8", "replace")
    said = ran.stderr.decode("utf-8", "replace")

    assert ran.returncode == MALFORMED, (
        f"WHAT: the artefact run over the bytes 1;0xFF exited "
        f"{ran.returncode}, not {MALFORMED}, printing {printed[:80]!r}. "
        "WHY: an argument that is not UTF-8 text is not a value of this "
        "language at all; answering it would answer something the compiler "
        "never reads, and the comment that runs to the end of a line must "
        "not swallow a byte nobody can read. "
        f"HOW: read what it printed: {said[-400:]!r}"
    )
    assert printed.strip() == "", (
        f"WHAT: the artefact printed {printed[:80]!r} for an argument that is "
        "not text. "
        "WHY: a refusal has no result value. "
        "HOW: decide the refusal before anything is written."
    )
    assert said.splitlines()[0].split(":", 1)[0].strip() == "MALFORMED", (
        f"WHAT: the refusal opens with {said[:80]!r}. "
        "WHY: a reader sorts refusals by the word on the first line. "
        "HOW: write MALFORMED first."
    )
    assert "Traceback" not in said, said[-400:]


def test_an_argument_that_cannot_be_read_beats_one_of_the_wrong_type(
    the_built_component,
):
    """Given the built reservation component, when it is run over `true`
    and `(` -- the first a value of the wrong type, the second text that
    closes no value -- then it is refused as malformed, because every
    argument is read before any is typed, which is the order the
    compiler reads them in.

    still passes if: the artefact had refused everything as malformed --
    the case below sends two readable arguments, of which one is of the
    wrong type, and requires the ill-typed refusal.
    """
    for arguments in (["true", "("], ["(", "true"]):
        ran = run_artefact(the_built_component, arguments)
        assert (ran.returncode, first_line_word(ran)) == (
            MALFORMED,
            "MALFORMED",
        ), (
            f"WHAT: the artefact run over {arguments} exited "
            f"{ran.returncode} with the word {first_line_word(ran)!r}. "
            "WHY: text that carries no value at all is refused before any "
            "argument is typed, wherever it stands: the compiler reads every "
            "argument first and reports the unreadable one, and what it "
            "builds must not report a wrong type instead. "
            f"HOW: read what it printed: {ran.stderr[-400:]!r}"
        )
        assert ran.stdout.strip() == "", ran.stdout[:120]

        refused = evaluate(reservation_source(), "step", arguments)
        assert (refused.get("result") or {}).get("value") is None, (
            f"WHAT: the compiler answered a value for {arguments}. "
            "WHY: this case rests on the two agreeing that the input cannot "
            f"be read. HOW: inspect the answer: {refused}"
        )


def test_two_readable_arguments_of_which_one_is_wrongly_typed_are_ill_typed(
    the_built_component,
):
    """Given the built reservation component, when it is run over `true`
    and `(Reserve)` -- both readable, the first of the wrong type --
    then it is refused as ill-typed, so the rule above is about text
    that cannot be read and not about refusing everything one way."""
    ran = run_artefact(the_built_component, ["true", "(Reserve)"])
    assert (ran.returncode, first_line_word(ran)) == (ILL_TYPED, "ILL-TYPED"), (
        f"WHAT: the artefact exited {ran.returncode} with the word "
        f"{first_line_word(ran)!r} for two readable arguments of which the "
        "first is of the wrong type. "
        "WHY: every argument reads as a value here, so the refusal is about "
        "the type of one of them. "
        f"HOW: read what it printed: {ran.stderr[-400:]!r}"
    )


def test_a_value_nested_past_the_published_limit_is_a_limit_of_the_artefact(
    the_built_component,
):
    """Given the built reservation component and the nesting limit this
    tool publishes, when it is run over a value nested one form past
    that limit and then over one nested 500 forms deep, then each is
    refused as a limit of the artefact, naming the published number,
    with no result value and no failure of the file itself.

    still passes if: the artefact had refused every nested value -- a
    value nested exactly to the limit is read here and refused for its
    type instead.
    """
    limit = published_limit("expression_nesting")
    at_the_limit = "(Reservation " * limit + "0" + ")" * limit
    nested = {
        "one form past the limit": "(Reservation " * (limit + 1)
        + "0"
        + ")" * (limit + 1),
        "500 forms deep": "(Reservation " * 500 + "0" + ")" * 500,
    }

    read_to_the_limit = run_artefact(the_built_component, [at_the_limit, "(Reserve)"])
    assert read_to_the_limit.returncode == ILL_TYPED, (
        f"WHAT: a value nested exactly {limit} forms deep exited "
        f"{read_to_the_limit.returncode}, not {ILL_TYPED}. "
        "WHY: the limit is the greatest nesting the artefact reads, so a "
        "value at it is read and then refused for its type; if it were "
        "refused for its nesting the limit would be off by one. "
        f"HOW: read what it printed: {read_to_the_limit.stderr[-300:]!r}"
    )

    for about, written in nested.items():
        ran = run_artefact(the_built_component, [written, "(Reserve)"])
        assert (ran.returncode, first_line_word(ran)) == (
            RESOURCE_EXHAUSTED,
            "RESOURCE",
        ), (
            f"WHAT: a value nested {about} exited {ran.returncode} with the "
            f"word {first_line_word(ran)!r}. "
            "WHY: the artefact reads one form inside another by calling "
            "itself, so it declares the same greatest nesting its compiler "
            "publishes and refuses past it: answering such a value promises "
            "more than the compiler, and exhausting the interpreter's stack "
            "reports a failure of the file for what is really an input. "
            f"HOW: read what it printed: {ran.stderr[-400:]!r}"
        )
        assert ran.stdout.strip() == "", ran.stdout[:120]
        assert "Traceback" not in ran.stderr, ran.stderr[-400:]
        assert str(limit) in ran.stderr, (
            f"WHAT: the refusal of a value nested {about} does not name the "
            f"published limit {limit}: {ran.stderr[-400:]!r}. "
            "WHY: the caller must be told the number to write inside. "
            "HOW: name the published limit in the message."
        )


def test_an_integer_literal_past_the_read_limit_is_a_limit_of_the_artefact(
    the_built_component,
):
    """Given the built reservation component, when it is run over an
    integer literal of 10000 digits -- far past the digits this tool
    reads as one literal -- then it is refused as a limit of the
    artefact rather than as text that is no value, with no result
    value."""
    ran = run_artefact(
        the_built_component, [f"(Reservation {'1' * 10000})", "(Reserve)"]
    )
    assert (ran.returncode, first_line_word(ran)) == (
        RESOURCE_EXHAUSTED,
        "RESOURCE",
    ), (
        f"WHAT: a literal of 10000 digits exited {ran.returncode} with the "
        f"word {first_line_word(ran)!r}. "
        "WHY: turning a run of digits into a number costs time that grows "
        "with the square of its length, so the artefact refuses past the "
        "limit its compiler publishes; that is a limit of the file and not a "
        "statement that the text is no value. "
        f"HOW: read what it printed: {ran.stderr[-300:]!r}"
    )
    assert ran.stdout.strip() == "", ran.stdout[:120]
    assert "10000" in ran.stderr, (
        f"WHAT: the refusal does not say how many digits were sent: "
        f"{ran.stderr[-300:]!r}. "
        "WHY: the caller must be told what was too long. "
        "HOW: name the digits read and the digits this artefact reads."
    )


def test_a_lowered_limit_on_decimal_digits_refuses_rather_than_fails(
    two_long_way_round_artefacts,
):
    """Given a built artefact that hands its argument back and one that
    answers a constant of 641 digits, when each is run by an interpreter
    whose own limit on the decimal digits of an integer the caller
    lowered to 640, then each refuses as a limit of the artefact, with
    no result value and no failure of the file; and the file is read by
    that interpreter at all, which a decimal literal of 641 digits in it
    would stop.

    still passes if: both had refused under every limit -- the same two
    runs without the lowered limit are required to answer below.
    """
    for about, entry, arguments in (
        ("an argument of 641 digits", "echo", [SIX_HUNDRED_AND_FORTY_ONE_DIGITS]),
        ("a constant of 641 digits", "constant", []),
    ):
        ran = run_with_lowered_digits(
            two_long_way_round_artefacts[entry], arguments, 640
        )
        assert ran.returncode != 1, (
            f"WHAT: {about} exited 1, which is what an interpreter exits when "
            f"it cannot read the file at all: {ran.stderr[-400:]!r}. "
            "WHY: a caller may lower the interpreter's limit on decimal "
            "digits, and a generated file that writes a long number as a "
            "decimal literal cannot then be read: the Owner holds a file that "
            "runs nowhere. "
            "HOW: write a long integer in the generated file in a form that "
            "is read whatever that limit is."
        )
        assert ran.returncode != A_FAILURE_OF_THE_FILE, (
            f"WHAT: {about} was reported as a failure of the file: "
            f"{ran.stderr[-400:]!r}. "
            "WHY: a limit the caller lowered is a limit of this run, not a "
            "fault of the generated program. "
            "HOW: translate the exhaustion into the limit refusal."
        )
        assert (ran.returncode, first_line_word(ran)) == (
            RESOURCE_EXHAUSTED,
            "RESOURCE",
        ), (
            f"WHAT: {about} exited {ran.returncode} with the word "
            f"{first_line_word(ran)!r}. "
            "WHY: 641 digits is past the 640 the caller left, so the run "
            "reaches a limit of this artefact and says so. "
            f"HOW: read what it printed: {ran.stderr[-400:]!r}"
        )
        assert ran.stdout.strip() == "", ran.stdout[:120]
        assert "Traceback" not in ran.stderr, ran.stderr[-400:]


def test_the_same_two_runs_answer_under_the_limit_this_tool_declares(
    two_long_way_round_artefacts,
):
    """Given the same two artefacts, when each is run without a lowered
    limit, then each answers the 641-digit number exactly -- so the
    refusals above are about the limit the caller set and not about the
    program."""
    back = run_artefact(
        two_long_way_round_artefacts["echo"], [SIX_HUNDRED_AND_FORTY_ONE_DIGITS]
    )
    assert (back.returncode, back.stdout.strip()) == (
        ANSWERED,
        SIX_HUNDRED_AND_FORTY_ONE_DIGITS,
    ), (
        f"WHAT: the artefact exited {back.returncode} answering "
        f"{back.stdout.strip()[:40]!r}... for a number of 641 digits. "
        "WHY: this tool reads and writes far more than 641 digits, so the "
        "refusals above belong to the lowered limit alone. "
        f"HOW: read what it printed: {back.stderr[-300:]!r}"
    )
    computed = run_artefact(two_long_way_round_artefacts["constant"], [])
    assert (computed.returncode, computed.stdout.strip()) == (
        ANSWERED,
        SIX_HUNDRED_AND_FORTY_ONE_DIGITS,
    ), (
        f"WHAT: the artefact of the constant exited {computed.returncode} "
        f"answering {computed.stdout.strip()[:40]!r}... "
        "WHY: the constant is written into the generated program and must be "
        "the number the source wrote. "
        f"HOW: read what it printed: {computed.stderr[-300:]!r}"
    )


def test_a_file_whose_header_is_not_about_its_program_fails_as_the_file(
    the_built_component,
):
    """Given a copy of the built artefact whose recorded source no
    longer matches the source written in it, when it is run over a state
    the table admits, then it refuses as a failure of the file itself,
    with the word ARTEFACT first, no result value and no traceback.

    This is the one status that is about the file rather than about the
    input or the program, and this is a real run that reaches it.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        changed = pathlib.Path(tmp_dir) / "changed.py"
        lines = the_built_component.read_text(encoding="utf-8").splitlines(
            keepends=True
        )
        found = [
            place for place, line in enumerate(lines) if line.startswith("SOURCE = ")
        ]
        assert len(found) == 1, (
            f"WHAT: {len(found)} lines of the artefact record the source it "
            "was built from, and this probe needs the one. "
            "WHY: a probe that cannot find what it changes proves nothing. "
            "HOW: read the artefact and name that line."
        )
        line = lines[found[0]].rstrip("\n")
        lines[found[0]] = line[:-1] + " " + line[-1] + "\n"
        changed.write_text("".join(lines), encoding="utf-8")

        ran = run_artefact(changed, ["(Reservation 0)", "(Reserve)"])
        assert (ran.returncode, first_line_word(ran)) == (
            A_FAILURE_OF_THE_FILE,
            "ARTEFACT",
        ), (
            f"WHAT: the changed file exited {ran.returncode} with the word "
            f"{first_line_word(ran)!r}. "
            "WHY: a file whose header and whose program are not one text "
            "claims evidence it does not have: that is a failure of the file, "
            "neither a refusal of the input nor a contract of the program. "
            f"HOW: read what it printed: {ran.stderr[-400:]!r}"
        )
        assert ran.stdout.strip() == "", ran.stdout[:120]
        assert "Traceback" not in ran.stderr, ran.stderr[-400:]
