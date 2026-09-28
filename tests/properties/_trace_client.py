"""Run the real `prova` entry point (or a control script) under the
execution tracer and classify what the trace shows.

Not a test module. See `_trace_harness.py` for what is observed and what is
not.
"""

from __future__ import annotations

import dataclasses
import json
import os
import pathlib
import re
import subprocess
import sys
import tempfile

HARNESS = pathlib.Path(__file__).resolve().parent / "_trace_harness.py"

# Names that identify the work a refused operation must not start.
WORK_NAME = re.compile(
    r"build|verif|prove|proof|solve|solver|smt|backend|compil|codegen|emit|artifact",
    re.IGNORECASE,
)
# Modules whose entry means the checked-evaluation stages ran.
WORK_MODULES = ("prova.evaluator", "prova.checker")


@dataclasses.dataclass
class TracedRun:
    returncode: int
    response: dict | None
    stdout: str
    stderr: str
    calls: list[tuple[str, str]]
    events: list[tuple[str, list[str]]]


def run_traced(request: dict, entry: str = "prova", timeout: float = 30.0) -> TracedRun:
    with tempfile.TemporaryDirectory() as scratch:
        trace_file = pathlib.Path(scratch) / "trace.json"
        proc = subprocess.run(
            [sys.executable, str(HARNESS), str(trace_file), entry],
            input=json.dumps(request),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        trace = json.loads(trace_file.read_text(encoding="utf-8"))
    try:
        response = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        response = None
    return TracedRun(
        proc.returncode,
        response,
        proc.stdout,
        proc.stderr,
        [tuple(c) for c in trace["calls"]],
        [(e[0], e[1]) for e in trace["events"]],
    )


def _real(path: str) -> str:
    return os.path.realpath(path)


def _ignorable(path: str) -> bool:
    return "__pycache__" in path or path.endswith(".pyc")


def mutations_under(run: TracedRun, root: pathlib.Path) -> list[tuple[str, list[str]]]:
    """Mutating audit events whose paths touch `root` or anything below it."""
    base = _real(str(root))
    hits = []
    for name, paths in run.events:
        if name in ("os.system", "subprocess.Popen"):
            continue
        for path in paths:
            real = _real(path)
            if real == base or real.startswith(base + os.sep):
                hits.append((name, paths))
                break
    return hits


def attempted_work(run: TracedRun) -> list[str]:
    """Every observed entry into build/verify/solver-style work: functions
    or modules with work-like names, the checked-evaluation stages, any
    process spawn, and any filesystem mutation other than bytecode caches."""
    found = []
    for module, qualname in run.calls:
        if module in WORK_MODULES:
            found.append(f"entered {module}.{qualname}")
        elif WORK_NAME.search(qualname) or WORK_NAME.search(module.rsplit(".", 1)[-1]):
            found.append(f"entered {module}.{qualname}")
    for name, paths in run.events:
        if name in ("open-write",) or name.startswith(("os.", "shutil.", "subprocess.", "ctypes.")):
            if paths and all(_ignorable(p) for p in paths):
                continue
            found.append(f"{name} {paths}")
    return found
