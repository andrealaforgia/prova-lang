"""Mutate the encoder, the solver port and the discharge decision, one
change at a time, and report which changes no test notices.

Why this exists: six review rounds each found one more place where a
wrong translation would have been reported as `proved`, and each was
closed by hand. Closing shapes by hand does not end. This walks the
syntax of the four modules that decide a verdict, makes every change the
operators below can make, and asks the tests about each one. A change no
test notices is either a defect nobody would see or a change that cannot
be seen at all, and the second kind has to be argued in writing.

Each mutant gets its own copy of the source tree in a temporary
directory and is run with that copy first on the import path, so no
mutant can be read by another run -- a mutation that keeps a file the
same length and is undone within the same second otherwise leaves
CPython reading the mutant, which happened here and cost a false defect
report.

Run it:

    uv run python tools/mutate_encoder.py --sample 40
    uv run python tools/mutate_encoder.py --out mutants.json --report mutants.md

Stdlib only.
"""

from __future__ import annotations

import argparse
import ast
import concurrent.futures
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]

# The modules that decide what a program owes and whether it is shown.
THE_MODULES = (
    "src/prova/encoding.py",
    "src/prova/solving.py",
    "src/prova/discharge.py",
    "src/prova/obligations.py",
)

# What the tests are asked first: the cheap ones that watch the
# translation closely. A mutant that survives these is asked the slower
# families, and only then the whole suite.
THE_FIRST_PASS = (
    "tests/properties/test_f18_a_literal_keeps_its_value_everywhere.py",
    "tests/unit/test_f18_a_solver_verdict_becomes_a_finding.py",
    "tests/acceptance/test_f18_a_negative_factor_keeps_its_sign.py",
    "tests/acceptance/test_f18_the_shipped_examples_come_back_proved.py",
)
THE_SECOND_PASS = THE_FIRST_PASS + (
    "tests/acceptance/test_f18_overlapping_clauses_and_negated_conditions.py",
    "tests/acceptance/test_f18_a_guarded_call_keeps_its_path_condition.py",
    "tests/acceptance/test_f18_an_exact_value_is_settled.py",
    "tests/acceptance/test_f18_the_answer_says_what_settled_each_entry.py",
    "tests/acceptance/test_f18_a_false_postcondition_is_not_proved.py",
    "tests/properties/test_f18_solver_laws.py",
    "tests/properties/test_f18_profile_laws.py",
)
THE_WHOLE_SUITE = ("tests",)

_COMPARISONS = {
    ast.Lt: ast.LtE, ast.LtE: ast.Lt, ast.Gt: ast.GtE, ast.GtE: ast.Gt,
    ast.Eq: ast.NotEq, ast.NotEq: ast.Eq,
    ast.In: ast.NotIn, ast.NotIn: ast.In,
    ast.Is: ast.IsNot, ast.IsNot: ast.Is,
}
_ARITHMETIC = {ast.Add: ast.Sub, ast.Sub: ast.Add, ast.Mult: ast.Add}
_SWAPPED_NAMES = {"any": "all", "all": "any", "min": "max", "max": "min"}


class _Site:
    """One place a mutation can be made, named so a reader can find it."""

    def __init__(self, module, node, operator, apply):
        self.module = module
        self.line = getattr(node, "lineno", 0)
        self.operator = operator
        self.apply = apply
        self.function = "?"


def _sites_in(module: str, tree: ast.AST) -> list:
    """Every mutation this file can make, with the change it would make."""
    found: list[_Site] = []

    def add(node, operator, apply):
        found.append(_Site(module, node, operator, apply))

    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and len(node.ops) == 1:
            kind = type(node.ops[0])
            if kind in _COMPARISONS:
                other = _COMPARISONS[kind]
                add(node, f"compare {kind.__name__} to {other.__name__}",
                    lambda n=node, o=other: setattr(n, "ops", [o()]))
        elif isinstance(node, ast.BoolOp):
            other = ast.Or if isinstance(node.op, ast.And) else ast.And
            add(node, "and/or swap", lambda n=node, o=other: setattr(n, "op", o()))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            add(node, "not removed",
                lambda n=node: (setattr(n, "op", ast.UAdd()),
                                setattr(n, "operand", n.operand)))
        elif isinstance(node, ast.BinOp) and type(node.op) in _ARITHMETIC:
            other = _ARITHMETIC[type(node.op)]
            add(node, f"{type(node.op).__name__} to {other.__name__}",
                lambda n=node, o=other: setattr(n, "op", o()))
            add(node, "operands reversed",
                lambda n=node: (lambda a, b: (setattr(n, "left", b),
                                              setattr(n, "right", a)))(
                    n.left, n.right))
        elif isinstance(node, ast.Constant):
            if isinstance(node.value, bool):
                add(node, "True/False swap",
                    lambda n=node: setattr(n, "value", not n.value))
            elif isinstance(node.value, int):
                for delta, name in ((1, "+1"), (-1, "-1")):
                    add(node, f"int constant {name}",
                        lambda n=node, d=delta: setattr(n, "value", n.value + d))
                if node.value != 0:
                    add(node, "int constant sign flip",
                        lambda n=node: setattr(n, "value", -n.value))
        elif isinstance(node, ast.Subscript) and isinstance(
            node.slice, ast.Constant
        ) and node.slice.value in (0, 1):
            add(node, "index 0/1 swap",
                lambda n=node: setattr(n.slice, "value", 1 - n.slice.value))
        elif isinstance(node, ast.IfExp):
            add(node, "branches of a conditional swapped",
                lambda n=node: (lambda a, b: (setattr(n, "body", b),
                                              setattr(n, "orelse", a)))(
                    n.body, n.orelse))
        elif isinstance(node, ast.Call):
            name = getattr(node.func, "id", None) or getattr(
                node.func, "attr", None)
            if name == "reversed" and len(node.args) == 1:
                add(node, "reversed() removed",
                    lambda n=node: setattr(n, "func", ast.Name(id="tuple",
                                                               ctx=ast.Load())))
            if name in _SWAPPED_NAMES:
                add(node, f"{name} to {_SWAPPED_NAMES[name]}",
                    lambda n=node, o=_SWAPPED_NAMES[name]: setattr(
                        n.func, "id", o) if isinstance(n.func, ast.Name)
                    else setattr(n.func, "attr", o))
            if len(node.args) >= 2:
                add(node, "call arguments reversed",
                    lambda n=node: setattr(n, "args", list(reversed(n.args))))
        elif isinstance(node, ast.If) and node.orelse:
            add(node, "if/else bodies swapped",
                lambda n=node: (lambda a, b: (setattr(n, "body", b),
                                              setattr(n, "orelse", a)))(
                    n.body, n.orelse))

    owners = [
        (owner.lineno, getattr(owner, "end_lineno", owner.lineno), owner.name)
        for owner in ast.walk(tree)
        if isinstance(owner, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    for site in found:
        enclosing = [
            (end - start, name)
            for start, end, name in owners
            if start <= site.line <= end
        ]
        if enclosing:
            site.function = min(enclosing)[1]
        else:
            site.function = "(module level)"
            site.operator = "module constant: " + site.operator
    return found


def _mutant_source(module: str, index: int):
    """The text of one mutant, and what it changed, or None when the
    change cannot be unparsed."""
    original = (ROOT / module).read_text()
    tree = ast.parse(original)
    sites = _sites_in(module, tree)
    if index >= len(sites):
        return None
    site = sites[index]
    site.apply()
    try:
        return ast.unparse(tree), site
    except Exception:  # noqa: BLE001 - an unparseable change is skipped
        return None


def _run(tests, source_root: pathlib.Path, seconds: int):
    env = {
        **os.environ,
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONPATH": str(source_root),
    }
    try:
        done = subprocess.run(
            ["uv", "run", "--no-sync", "python", "-m", "pytest", "-q", "-x",
             "-p", "no:cacheprovider", *tests],
            cwd=ROOT, capture_output=True, text=True, env=env, timeout=seconds,
        )
    except subprocess.TimeoutExpired:
        return None, "timed out"
    killer = next(
        (l.split(" ")[0].removeprefix("FAILED ")
         for l in done.stdout.splitlines() if l.startswith("FAILED")), "")
    return done.returncode, killer


def _with_source(text: str, module: str):
    """A temporary copy of the source tree with one module replaced."""
    where = pathlib.Path(tempfile.mkdtemp(prefix="prova-mutant-"))
    shutil.copytree(ROOT / "src", where / "src")
    (where / module.replace("src/", "src/")).write_text(text)
    return where


def _judge(job, seconds: int) -> dict:
    module, index = job
    built = _mutant_source(module, index)
    if built is None:
        return {"module": module, "index": index, "verdict": "unmutatable"}
    text, site = built
    where = _with_source(text, module)
    try:
        code, killer = _run(THE_FIRST_PASS, where / "src", seconds)
        reached = "first"
        if code == 0:
            code, killer = _run(THE_SECOND_PASS, where / "src", seconds)
            reached = "second"
        return {
            "module": module, "index": index, "function": site.function,
            "line": site.line, "operator": site.operator,
            "verdict": "killed" if code else "survived the cheap passes",
            "killed_by": killer, "pass": reached,
        }
    finally:
        shutil.rmtree(where, ignore_errors=True)


def _asked_the_whole_suite(answer: dict, seconds: int) -> dict:
    """One survivor of the cheap passes, asked the whole suite.

    Run only for a survivor, and once each: a mutant no close cell
    notices may still be noticed by some other test, and that is the
    difference between a survivor to argue about and one to close.
    """
    built = _mutant_source(answer["module"], answer["index"])
    if built is None:
        return {**answer, "verdict": "unmutatable"}
    text, _ = built
    where = _with_source(text, answer["module"])
    try:
        code, killer = _run(THE_WHOLE_SUITE, where / "src", seconds)
        return {
            **answer,
            "verdict": "killed" if code else "SURVIVED",
            "killed_by": killer or answer.get("killed_by", ""),
            "pass": "whole suite" if code else "survived everything",
        }
    finally:
        shutil.rmtree(where, ignore_errors=True)


def _control(seconds: int) -> None:
    where = pathlib.Path(tempfile.mkdtemp(prefix="prova-control-"))
    shutil.copytree(ROOT / "src", where / "src")
    code, _ = _run(THE_FIRST_PASS, where / "src", seconds)
    print(f"CONTROL unmutated copy -> {'green' if code == 0 else 'RED (broken harness)'}")
    swapped = (where / "src/prova/solving.py").read_text().replace(
        "lambda q, p, c: p[0] - p[1]", "lambda q, p, c: p[1] - p[0]")
    (where / "src/prova/solving.py").write_text(swapped)
    code, _ = _run(THE_FIRST_PASS, where / "src", seconds)
    print(f"CONTROL same-length mutant -> {'red' if code else 'GREEN (harness blind)'}")
    shutil.rmtree(where, ignore_errors=True)


FINAL = ("killed", "SURVIVED", "unmutatable")


def _already_decided(ledger: pathlib.Path) -> dict:
    """What a previous run settled, so a run that was stopped loses
    nothing: a mutant with a final verdict is not asked again, and one
    that only survived the cheap passes is asked the suite again."""
    settled = {}
    if not ledger.exists():
        return settled
    for line in ledger.read_text().splitlines():
        if not line.strip():
            continue
        try:
            answer = json.loads(line)
        except json.JSONDecodeError:
            continue
        settled[(answer["module"], answer["index"])] = answer
    return settled


def _note(ledger, answer: dict) -> None:
    """One decided mutant, on disk before the next one starts."""
    ledger.write(json.dumps(answer) + "\n")
    ledger.flush()
    os.fsync(ledger.fileno())


def _report(judged: list, where: str) -> None:
    lines = ["| module | function | line | operator | verdict | killed by |",
             "|---|---|---|---|---|---|"]
    for a in judged:
        lines.append(
            f"| {a['module']} | {a.get('function','?')} | {a.get('line','?')} "
            f"| {a.get('operator','?')} | {a['verdict']} | "
            f"{a.get('killed_by','') or ''} |")
    pathlib.Path(where).write_text("\n".join(lines) + "\n")


def main() -> None:
    asked = argparse.ArgumentParser(description=__doc__)
    asked.add_argument("--sample", type=int, default=0)
    asked.add_argument("--workers", type=int, default=4)
    asked.add_argument("--seconds", type=int, default=120)
    asked.add_argument("--out", default="")
    asked.add_argument("--report", default="")
    asked.add_argument("--ledger", default="",
                       help="append one JSON line per decided mutant here, "
                            "and skip what it already settled")
    asked.add_argument("--report-from", default="",
                       help="write the markdown report from a ledger and stop")
    said = asked.parse_args()

    if said.report_from:
        judged = list(_already_decided(pathlib.Path(said.report_from)).values())
        _report(judged, said.report or "mutants.md")
        print(f"{len(judged)} decided mutants written to "
              f"{said.report or 'mutants.md'}")
        return

    jobs = []
    for module in THE_MODULES:
        tree = ast.parse((ROOT / module).read_text())
        jobs.extend((module, index) for index in range(len(_sites_in(module, tree))))
    print(f"{len(jobs)} mutants over {len(THE_MODULES)} modules")
    if said.sample:
        jobs = jobs[: said.sample]
        print(f"sampling the first {len(jobs)}")

    _control(said.seconds)
    ledger_path = pathlib.Path(said.ledger or "mutants.jsonl")
    settled = _already_decided(ledger_path)
    final = {k for k, a in settled.items() if a["verdict"] in FINAL}
    if final:
        print(f"{len(final)} mutants were decided by an earlier run and are "
              "not asked again", flush=True)
    jobs = [job for job in jobs if job not in final]

    judged = [a for k, a in settled.items() if k in final]
    ledger = ledger_path.open("a", encoding="utf-8")
    with concurrent.futures.ThreadPoolExecutor(max_workers=said.workers) as pool:
        for answer in pool.map(lambda job: _judge(job, said.seconds), jobs):
            judged.append(answer)
            _note(ledger, answer)
            if answer["verdict"] != "killed":
                print(f"{answer['verdict']:12} {answer.get('operator', '')} "
                      f"at {answer['module']}:{answer.get('line', '?')} "
                      f"({answer.get('function', '?')})", flush=True)
    cheap_survivors = [
        a for a in judged if a["verdict"] == "survived the cheap passes"
    ]
    print(f"\n{len(cheap_survivors)} survived the cheap passes; "
          "asking each the whole suite once", flush=True)
    if cheap_survivors:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=said.workers
        ) as pool:
            asked_the_suite = list(
                pool.map(lambda a: _asked_the_whole_suite(a, 480), cheap_survivors)
            )
        by_key = {(a["module"], a["index"]): a for a in asked_the_suite}
        judged = [by_key.get((a["module"], a["index"]), a) for a in judged]
        for a in asked_the_suite:
            _note(ledger, a)
        for a in asked_the_suite:
            if a["verdict"] == "SURVIVED":
                print(f"SURVIVED EVERYTHING {a['operator']} at "
                      f"{a['module']}:{a['line']} ({a['function']})", flush=True)
    survived = [a for a in judged if a["verdict"] == "SURVIVED"]
    print(f"\nkilled {sum(1 for a in judged if a['verdict'] == 'killed')}, "
          f"survived {len(survived)}, "
          f"unmutatable {sum(1 for a in judged if a['verdict'] == 'unmutatable')}")
    if said.out:
        pathlib.Path(said.out).write_text(json.dumps(judged, indent=1))
    ledger.close()
    if said.report:
        _report(judged, said.report)
    sys.exit(1 if survived else 0)


if __name__ == "__main__":
    main()
