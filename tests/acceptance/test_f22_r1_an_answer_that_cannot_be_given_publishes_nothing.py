"""A build publishes a file only when the answer about it can be given
whole, and only when what it wrote is a module the interpreter reads.

Two things an independent review found. The first: with the answer
budget lowered, the build answered `resource_exhausted` -- and the
artefact was already there, complete and runnable, standing at a path no
answer of this tool ever named. The Owner is told the request was
refused and holds a file they were never told about. The second: a
program may nest its conditions deeper than any Python compiler reads
blocks, and the file written for it was published without being read
back, so the first time the Owner ran it, it failed.

Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile

from _f22_fixtures import artefact_of, build, files_under, hour_clock


def _a_program_nesting_matches(how_deep: int) -> str:
    """One function whose body nests `how_deep` matches inside one
    another, each with one clause that covers every value.

    Every rule of core-0 holds for it: there is no recursion, no clause
    is left out, and nothing is shadowed. The translation of a match is
    a block, so this is the program that asks the backend for more
    blocks than Python compiles.
    """
    body = "n"
    for _ in range(how_deep):
        body = f"(match n (_ {body}))"
    return (
        "(defn deep\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (deep 3) => 3))\n"
        f"  {body})\n"
    )


def _a_program_nesting_conditions(how_deep: int) -> str:
    """One function whose body nests `how_deep` conditions inside one
    another, which a backend may write as one expression."""
    body = "n"
    for step in range(how_deep):
        body = f"(if (> n {step}) {body} 0)"
    return (
        "(defn deep\n"
        "  (sig ((n Int)) -> Int ! pure)\n"
        "  (requires (>= n 0))\n"
        "  (examples (example (deep 0) => 0))\n"
        f"  {body})\n"
    )


def test_an_answer_too_large_to_give_leaves_no_artefact():
    """Given the shipped hour clock and the answer budget lowered to 1
    byte, when the Owner asks for a build, then the answer is
    `resource_exhausted` and the destination holds nothing: an artefact
    beside that refusal is a file the Owner was never told about.

    still passes if: the tool had refused every build under a lowered
    budget -- the same build under the declared budget is required to
    publish one artefact in the test below, and the refusal here is
    required to name the answer budget rather than anything else.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        answer = build(
            hour_clock(),
            "step",
            destination / "clock.py",
            lowered={"PROVA_BUDGET_ANSWER_SIZE": "1"},
        )
        written = files_under(destination)

    assert answer.get("status") == "resource_exhausted", (
        f"WHAT: a build whose answer does not fit the budget the caller set "
        f"was answered {answer.get('status')!r}. "
        "WHY: an answer this tool cannot write whole is replaced by the "
        "refusal that says so. "
        f"HOW: inspect the answer: {answer}"
    )
    categories = {d.get("category") for d in answer.get("diagnostics") or []}
    assert categories == {"output_budget_exceeded"}, (
        f"WHAT: the refusal carries {categories}. "
        "WHY: the budget that was passed is the one the refusal names. "
        f"HOW: inspect the answer: {answer}"
    )
    assert written == {}, (
        f"WHAT: the refused build left {sorted(written)} at the destination. "
        "WHY: the Owner was told the request was refused; a complete, "
        "runnable artefact standing at a path no answer named is a file they "
        "do not know they have, built from evidence they were never given. "
        "HOW: write the whole answer out and measure it against the budget "
        "before publishing anything."
    )


def test_a_build_under_the_declared_budget_still_publishes_one_artefact():
    """Given the same program and no budget lowered, when the Owner asks
    for a build, then one artefact is published -- so the refusal above
    is about the budget and not about the build.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        answer = build(hour_clock(), "step", destination / "clock.py")
        artefact_of(answer, "the shipped hour clock under the declared budgets")
        assert sorted(files_under(destination)) == ["clock.py"], files_under(
            destination
        )


def test_a_program_nesting_forty_matches_is_built_and_runs():
    """Given a program nesting 40 matches inside one another -- each
    written as a block, which is as deep as the reader of this tool
    reads a text -- when the Owner asks for a build, then one artefact is
    published, the interpreter reads it, and it answers 3 for 3.

    The module a build writes is read back by the interpreter it is
    written for before anything is published (a file that cannot be read
    is not an artefact). That refusal cannot be reached from any program
    this tool accepts: a module nests one block per match, 100 blocks is
    what the interpreter reads, and a text nesting the 200 forms that
    would take is already refused by the reader at 128. It is stated as
    an unproven limit rather than tested here, and the guard itself is
    exercised in
    tests/unit/test_f22_an_artefact_is_read_back_before_it_is_published.py.

    still passes if: the translation had nested one block per condition
    as well -- the test below nests 100 conditions, which no text of 200
    forms could carry.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        target = destination / "deep.py"
        answer = build(_a_program_nesting_matches(40), "deep", target)
        artefact_of(answer, "a program nesting 40 matches")

        ran = subprocess.run(
            [sys.executable, "-I", str(target), "3"],
            capture_output=True,
            text=True,
            timeout=30.0,
            cwd=str(destination),
        )
        assert ran.returncode == 0 and ran.stdout.strip() == "3", (
            f"WHAT: the artefact of a program nesting 40 matches exited "
            f"{ran.returncode} and answered {ran.stdout.strip()!r} for 3. "
            "WHY: every clause covers every value, so the answer is the "
            "argument itself. "
            f"HOW: read what it printed: {ran.stderr[-500:]!r}"
        )


def test_a_program_nesting_a_hundred_conditions_is_built_and_runs():
    """Given a program nesting 100 conditions inside one another, when
    the Owner asks for a build, then one artefact is published, the
    interpreter reads it, and it answers the number the program computes:
    for an input of 7 the outermost 7 conditions hold and the eighth does
    not, so the answer is 0.

    A condition is written as one Python expression, not as a block, so
    the depth of a program's conditions is not the depth of its module.

    still passes if: the translation had nested blocks and the file had
    been published unread -- the artefact is run here, and a module the
    interpreter cannot read is refused in the test above.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        target = destination / "deep.py"
        answer = build(_a_program_nesting_conditions(100), "deep", target)
        artefact_of(answer, "a program nesting 100 conditions")

        ran = subprocess.run(
            [sys.executable, "-I", str(target), "7"],
            capture_output=True,
            text=True,
            timeout=30.0,
            cwd=str(destination),
        )
        assert ran.returncode == 0, (
            f"WHAT: the artefact of a program nesting 100 conditions exited "
            f"{ran.returncode}. "
            "WHY: the module must be one the interpreter reads and runs. "
            f"HOW: read what it printed: {ran.stderr[-500:]!r}"
        )
        assert ran.stdout.strip() == "0", (
            f"WHAT: it answered {ran.stdout.strip()!r} for 7, and the program "
            "computes 0: the conditions ask whether 7 is greater than 0, 1, "
            "2 and so on, and the one asking about 7 does not hold. "
            f"HOW: read the artefact at {target}"
        )
