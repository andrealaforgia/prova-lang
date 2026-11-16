"""A failure of this tool's own machinery never accepts a program.

F19 criterion 3: given a solver that fails to run, the answer is a tool
failure and the program is not accepted. SPEC.md, "Results and evidence
scope": "Tool failures and conflicting solver results block acceptance;
they do not become semantic counterexamples."

F18 already answers each obligation that needed the solver `unknown`
beside a `tool_failure` status. What was missing is the second half: an
answer that says, over the whole program, that nothing was shown and that
the reason was this tool and not the program.

The premise is forced from outside the tool, with no hook inside it: a
module named `z3` that refuses to be imported is put first on the path of
the command's own process. The entries of the answer are then read to
confirm that the premise really occurred -- they name the loading failure
-- and the same program is asked for again without it, which comes back
verified. A test that could not tell the two runs apart would prove
nothing.

Drives only the `prova` command's real JSON stdin/stdout surface. No
imports from src/prova.
"""

from __future__ import annotations

import json
import os
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# A module named like the solver package that raises as soon as it is
# read. Put first on the path, it is what `import z3` finds.
A_Z3_THAT_CANNOT_BE_LOADED = (
    '''"""Not the solver: a module of this test that refuses to load."""\n'''
    'raise ImportError("this z3 cannot be loaded")\n'
)

LABEL = "the shipped hour clock, asked for with no solver that can load"


def _hour_clock() -> str:
    return (REPO_ROOT / "examples" / "hour-clock.prova").read_text(encoding="utf-8")


def _verified_with(source: str, first_on_the_path: pathlib.Path | None) -> dict:
    environment = dict(os.environ)
    if first_on_the_path is not None:
        before = environment.get("PYTHONPATH")
        environment["PYTHONPATH"] = (
            str(first_on_the_path)
            if not before
            else f"{first_on_the_path}{os.pathsep}{before}"
        )
    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"operation": "verify", "source": source}),
        capture_output=True,
        text=True,
        timeout=60.0,
        env=environment,
    )
    assert proc.returncode == 0, (
        f"WHAT: the command exited {proc.returncode} instead of answering. "
        "WHY: a solver that cannot be loaded is a thing to report, not a run "
        "that stops: a caller left with nothing on standard output has no "
        "verdict at all. "
        f"HOW: read the failure on its error output: {proc.stderr[-600:]!r}"
    )
    return json.loads(proc.stdout)


def test_a_solver_that_cannot_be_loaded_is_reported_and_accepts_nothing(tmp_path):
    """Given the shipped hour clock and a solver package that refuses to
    load, when the Owner verifies it, then every obligation that needed
    the solver is unsettled with that reason, the aggregate is not
    verified, and it says the attempt failed in this tool.

    still passes if: the tool answered the same way whatever the solver
    did -- the control below asks for the same program with the solver
    working and requires `verified`.
    """
    broken = tmp_path / "z3.py"
    broken.write_text(A_Z3_THAT_CANNOT_BE_LOADED, encoding="utf-8")

    answer = _verified_with(_hour_clock(), tmp_path)

    assert answer.get("status") == "completed", (
        f"WHAT: the answer has status {answer.get('status')!r}. "
        "WHY: the tool was asked what the program owes and can still say "
        "that, with each entry carrying what became of it; refusing the whole "
        "request would lose the obligations a rule of core-0 settled. "
        f"HOW: inspect the answer: {answer}"
    )
    entries = ((answer.get("result") or {}).get("inventory") or {}).get(
        "obligations"
    ) or []
    failed = [
        entry for entry in entries if entry.get("execution_status") == "tool_failure"
    ]
    assert failed, (
        "WHAT: no obligation reports a failure of this tool. "
        "WHY: the premise of this test is that the solver could not be "
        "loaded; without an entry saying so the run under observation was not "
        "the run this test describes. "
        f"HOW: inspect the entries: "
        f"{[(e['id'], e.get('execution_status')) for e in entries]}"
    )
    assert all(entry["result"] == "unknown" for entry in failed), (
        f"WHAT: an obligation nothing could be asked about stands as "
        f"{sorted({entry['result'] for entry in failed})}. "
        "WHY: a failure of this tool is not a statement about the program. "
        f"HOW: inspect the entries: {failed}"
    )
    said = " ".join(str(entry.get("reason", "")) for entry in failed)
    assert "solver could not be loaded" in said, (
        f"WHAT: the entries say {said!r} about why nothing was asked. "
        "WHY: the reader must be told this was the tool's own installation "
        "and not their program, and this test must be able to see that the "
        "solver it broke is the one the answer is about. "
        "HOW: name the loading failure in the reason."
    )

    aggregate = answer.get("aggregate") or {}
    assert aggregate.get("result") == "not_verified", (
        f"WHAT: the aggregate over a program nothing could be asked about is "
        f"{aggregate.get('result')!r}. "
        "WHY: SPEC.md: tool failures block acceptance. A program accepted "
        "because the solver never ran would be the worst kind of wrong "
        "'verified'. "
        f"HOW: inspect the aggregate: {aggregate}"
    )
    assert aggregate.get("execution_status") == "tool_failure", (
        f"WHAT: the aggregate says the attempt ended as "
        f"{aggregate.get('execution_status')!r}. "
        "WHY: the Owner must be able to tell a program that was not shown "
        "from a run this tool could not finish; only the second is fixed by "
        "installing the dependencies. "
        f"HOW: inspect the aggregate: {aggregate}"
    )
    assert "trust" not in answer, (
        f"WHAT: an answer that reached no solver discloses {answer.get('trust')}. "
        "WHY: there is no word of a solver's to disclose where none answered. "
        f"HOW: inspect the answer: {sorted(answer)}"
    )


def test_the_same_program_with_the_solver_working_is_verified(tmp_path):
    """Control. Given the same hour clock and nothing on the path to stop
    the solver loading, when the Owner verifies it, then it comes back
    verified -- so the test above observes the broken solver and not a
    program that could never be shown."""
    answer = _verified_with(_hour_clock(), None)
    aggregate = answer.get("aggregate") or {}

    assert aggregate.get("result") == "verified", (
        f"WHAT: the shipped hour clock comes back {aggregate.get('result')!r} "
        "with a working solver. "
        "WHY: this control is what makes the test above about the solver that "
        "could not load; if the clock were unverifiable either way, that test "
        "would pass over a tool that ignored the solver entirely. "
        f"HOW: inspect the answer: {answer}"
    )
