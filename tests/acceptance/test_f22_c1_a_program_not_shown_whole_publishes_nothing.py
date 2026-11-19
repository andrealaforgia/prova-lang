"""F22 criterion 1: given a program with any obligation not discharged,
when `build` runs, then it refuses and writes nothing.

SPEC.md line 290: "The standard `build` operation fails closed while
required verification is incomplete or unavailable and publishes no
executable artefact." The fail-closed rule has never been tested against
a build that could otherwise have succeeded: until now `build` was
refused because it was unavailable, so no refusal of it rested on the
evidence.

A snapshot taken only at the end cannot tell a build that never touched
the destination from one that wrote an artefact and removed it again, so
the destination is read continuously while the command runs.

Drives only the `prova` command's real JSON stdin/stdout surface and the
files it writes. No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import tempfile
import time

from _f22_fixtures import build, files_under, hour_clock

POLL_BUDGET_SECONDS = 30.0


def _refused_without_touching_the_destination(request: dict, destination: pathlib.Path):
    """The answer to `request`, and every state the destination was
    seen in while the command ran.

    The command is watched rather than inspected afterwards: a build that
    wrote an artefact and deleted it again before answering would leave a
    final state equal to the first one.
    """
    before = files_under(destination)
    proc = subprocess.Popen(
        ["prova"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    proc.stdin.write(json.dumps(request))
    proc.stdin.close()
    deviations = []
    started = time.monotonic()
    while proc.poll() is None:
        if time.monotonic() - started > POLL_BUDGET_SECONDS:
            proc.kill()
            proc.wait()
            raise TimeoutError(
                f"the build did not answer within {POLL_BUDGET_SECONDS}s"
            )
        try:
            seen = files_under(destination)
        except FileNotFoundError:
            deviations.append("a path vanished while the destination was read")
            continue
        if seen != before:
            deviations.append(sorted(seen))
    stdout = proc.stdout.read()
    stderr = proc.stderr.read()
    proc.wait()
    after = files_under(destination)
    if after != before:
        deviations.append(sorted(after))
    assert proc.returncode == 0, (
        f"WHAT: the command exited {proc.returncode} asking for a build. "
        "WHY: every request is answered; a run that stops with nothing on "
        "standard output leaves the Owner with no verdict. "
        f"HOW: read its error output: {stderr[-600:]!r}"
    )
    return json.loads(stdout), deviations, before, after


def test_c1_a_failing_example_withholds_the_artefact_and_writes_nothing():
    """Given the shipped hour clock with one of its 8 examples made wrong,
    and a destination that already holds two files from before, when the
    Owner asks for a build of it, then the answer refuses with
    `not_verified`, names the example that did not pass, carries no
    artefact, and the destination is never seen holding anything else --
    not even while the command is running.

    still passes if: the tool refused every build whatever the evidence --
    test_f22_c2 builds this same program with its examples as shipped and
    requires one artefact.
    """
    a_true_example = "(example (valid-state (Clock 1)) => true)"
    the_same_example_made_wrong = "(example (valid-state (Clock 1)) => false)"
    source = hour_clock().replace(a_true_example, the_same_example_made_wrong)
    assert source != hour_clock(), (
        "WHAT: the shipped clock does not contain the example this test "
        f"makes wrong: {a_true_example}. "
        "WHY: a test that silently changed nothing would ask for a build of "
        "a program that is verified, under the name of one that is not. "
        "HOW: read examples/hour-clock.prova and fix the text above."
    )

    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        (destination / "notes.txt").write_bytes(b"kept from an earlier session\n")
        (destination / "clock.py").write_bytes(b"placeholder from a previous build")

        answer, deviations, before, after = _refused_without_touching_the_destination(
            {
                "operation": "build",
                "source": source,
                "entry": "step",
                "output_file": str(destination / "clock.py"),
            },
            destination,
        )

    assert answer.get("operation") == "build", answer
    assert answer.get("status") == "not_verified", (
        f"WHAT: a build of a program one of whose own examples does not pass "
        f"was answered {answer.get('status')!r}. "
        "WHY: SPEC.md line 290: a build fails closed while verification is "
        "incomplete, and the Owner must be able to tell that refusal from a "
        "program the checker refused and from a request it could not read. "
        f"HOW: inspect the answer: {answer}"
    )
    assert not answer.get("result"), (
        f"WHAT: the refusal carries a result: {answer.get('result')}. "
        "WHY: a refused build publishes nothing at all. "
        f"HOW: inspect the answer: {answer}"
    )
    reasons = " ".join(d.get("reason", "") for d in answer.get("diagnostics") or [])
    assert "valid-state" in reasons, (
        f"WHAT: the refusal does not name the example that did not pass: "
        f"{reasons!r}. "
        "WHY: the Owner told their program was not shown must be told which "
        "part of it was not, or they cannot repair it. "
        f"HOW: name the blocking items of the aggregate: {answer}"
    )
    assert deviations == [], (
        "WHAT: the destination was seen holding something other than the two "
        f"files it held before, while the refused build ran: {deviations}. "
        "WHY: a refused build writes nothing, not even for the lifetime of "
        "the request. "
        f"HOW: decide the refusal before anything is written: before={sorted(before)}"
    )
    assert after == before, f"before={sorted(before)} after={sorted(after)}"


def test_c1_an_obligation_the_tool_cannot_settle_withholds_the_artefact():
    """Given a program whose promise is about the product of two unknown
    numbers, which this tool does not translate, when the Owner asks for a
    build, then it refuses with `not_verified`, names that obligation, and
    writes no file at the destination.

    still passes if: the tool refused because it could not read the
    program -- the refusal is required to be `not_verified` rather than
    `invalid_program`, and the obligation is required to be named.
    """
    a_product_of_two_unknown_numbers = """(defn product
  (sig ((n Int) (m Int)) -> Int ! pure)
  (requires (and (>= n 0) (>= m 0)))
  (ensures (>= result 0))
  (examples (example (product 2 3) => 6))
  (* n m))
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        answer = build(
            a_product_of_two_unknown_numbers,
            "product",
            destination / "product.py",
        )
        written = files_under(destination)

    assert answer.get("status") == "not_verified", (
        f"WHAT: a build of a program with an obligation this tool cannot "
        f"settle was answered {answer.get('status')!r}. "
        "WHY: an obligation left unsettled is an obligation not discharged, "
        "and a build fails closed while any of them is. "
        f"HOW: inspect the answer: {answer}"
    )
    reasons = " ".join(d.get("reason", "") for d in answer.get("diagnostics") or [])
    assert "product" in reasons, (
        f"WHAT: the refusal names no undischarged obligation: {reasons!r}. "
        "WHY: the Owner must read which obligation stopped the build. "
        f"HOW: inspect the answer: {answer}"
    )
    assert written == {}, (
        f"WHAT: the refused build left {sorted(written)} at the destination. "
        "WHY: a refused build publishes no file at all. "
        f"HOW: decide the refusal before anything is written."
    )


def test_c1_a_program_the_checker_refuses_is_never_built():
    """Given a program whose body does not have the type its signature
    declares, when the Owner asks for a build, then the answer is the
    refusal the checker already gives, it carries no artefact, the word
    `verified` appears nowhere in it, and nothing is written.

    still passes if: the tool answered `not_verified` for a program it
    never read -- the status is required to be the checker's own, so a
    reader tells a program that breaks a rule of core-0 from one that was
    read and not shown.
    """
    the_checker_refuses = """(defn truthy
  (sig ((n Int)) -> Bool ! pure)
  (examples (example (truthy 1) => true))
  n)
"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        destination = pathlib.Path(tmp_dir)
        answer = build(the_checker_refuses, "truthy", destination / "truthy.py")
        written = files_under(destination)

    assert answer.get("status") == "invalid_program", (
        f"WHAT: a program the checker refuses was answered "
        f"{answer.get('status')!r} by a build. "
        "WHY: a program that breaks a rule of core-0 is refused the way "
        "every other operation refuses it; nothing was shown about it to "
        "aggregate. "
        f"HOW: inspect the answer: {answer}"
    )
    assert "verified" not in json.dumps(answer).lower(), (
        f"WHAT: the word 'verified' appears in the refusal: {answer}. "
        "WHY: the word may be said only where the evidence behind it is "
        "published, and this answer has none. "
        "HOW: refuse through the checker's own refusal."
    )
    assert written == {}, f"the refused build wrote {sorted(written)}"
