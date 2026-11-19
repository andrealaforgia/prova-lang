"""Shared helpers for F22's acceptance tests: how the Owner asks for a
build over the real `prova` command, and how an artefact it published is
read and run.

Not a test module (no `test_` prefix); pytest will not collect it.
Drives only the command's real JSON stdin/stdout surface and the artefact
file the command writes. No imports from src/prova: an artefact is run by
the interpreter a reader has, with the compiler nowhere in sight.
"""

from __future__ import annotations

import hashlib
import json
import pathlib
import subprocess
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# The line the generated artefact writes between everything the build
# recorded about this source and the program it translated. Two builds of
# two sources that differ only in their examples write the same
# characters after it, which is how a reader sees that no example answer
# reached the computation.
THE_PROGRAM_BEGINS = "# --- the program, translated ---"

# What the artefact's own exit status says. 0 is an answer; the others
# are refusals, and none of them is a traceback.
ANSWERED = 0
REFUSED_THE_INPUT = 2
ASSURANCE_FAILURE = 3


def hour_clock() -> str:
    """The hour clock this repository ships: every obligation of it is
    discharged and its 8 declared examples all pass, so it is the
    program a build may publish."""
    return (REPO_ROOT / "examples" / "hour-clock.prova").read_text(encoding="utf-8")


def digest_of(text: str) -> str:
    """The revision of a text, computed the way a client recomputes it
    from what it sent: the SHA-256 of its UTF-8 bytes."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def ask(request: dict, timeout: float = 60.0) -> dict:
    """The one answer the installed command gives to `request`."""
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    assert proc.returncode == 0, (
        f"WHAT: the command exited {proc.returncode} for "
        f"{request.get('operation')!r} instead of answering. "
        "WHY: every request is answered, and a run that stops with nothing "
        "on standard output leaves the Owner with no verdict at all. "
        f"HOW: read the failure on its error output: {proc.stderr[-600:]!r}"
    )
    try:
        return json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(
            f"WHAT: the answer to {request.get('operation')!r} is not JSON: "
            f"{proc.stdout[:600]!r}. "
            "WHY: the Owner reads one JSON object per answer. "
            "HOW: inspect what the command printed."
        )


def build(source: str, entry: str, output_file, **extra) -> dict:
    """What the Owner is told when they ask for one artefact of a
    program, naming the function to invoke and the file to write."""
    request = {"operation": "build", "source": source, "entry": entry}
    if output_file is not None:
        request["output_file"] = str(output_file)
    request.update(extra)
    return ask(request)


def evaluate(source: str, function: str, arguments: list) -> dict:
    """What the compiler answers when it runs one function of a program
    over values written the way a program writes them."""
    return ask(
        {
            "operation": "evaluate",
            "source": source,
            "function": function,
            "arguments": list(arguments),
        }
    )


def the_manifest() -> dict:
    return ask({"operation": "discover"})


def artefact_of(answer: dict, about: str) -> dict:
    """What the build answer records about the artefact it published."""
    assert answer.get("status") == "completed", (
        f"WHAT: the build answer about {about} has status "
        f"{answer.get('status')!r}, not 'completed'. "
        "WHY: an artefact is published only by a completed build; a refusal "
        "publishes none. "
        f"HOW: inspect the answer: {answer}"
    )
    published = (answer.get("result") or {}).get("artefact")
    assert isinstance(published, dict), (
        f"WHAT: the completed build about {about} records no artefact: "
        f"{answer.get('result')}. "
        "WHY: the Owner must read which entry and which configuration the "
        "artefact they now hold was built with. "
        f"HOW: inspect the answer: {answer}"
    )
    return published


def run_artefact(path: pathlib.Path, arguments: list) -> subprocess.CompletedProcess:
    """One run of the artefact over fresh input, by the interpreter a
    reader has rather than by the compiler's own environment: each
    argument is the text of a value, the way a program writes it.

    Run with `sys.executable -I`: isolated, so the artefact answers out
    of itself and not out of anything the compiler left on the path.
    """
    return subprocess.run(
        [sys.executable, "-I", str(path), *[str(a) for a in arguments]],
        capture_output=True,
        text=True,
        timeout=30.0,
        cwd=str(path.parent),
    )


def answered(ran: subprocess.CompletedProcess, about: str) -> str:
    """The one value the artefact answered, as the text it printed."""
    assert ran.returncode == ANSWERED, (
        f"WHAT: running the artefact over {about} exited {ran.returncode}. "
        "WHY: a built program answers its input; an exit of its own is a "
        "refusal, and this input was meant to be answered. "
        f"HOW: read what it printed: stdout={ran.stdout[-400:]!r} "
        f"stderr={ran.stderr[-400:]!r}"
    )
    assert "Traceback" not in ran.stderr, (
        f"WHAT: the artefact ended in a traceback over {about}: "
        f"{ran.stderr[-600:]!r}. "
        "WHY: an artefact never ends in a traceback; it answers or it "
        "refuses in words. "
        "HOW: catch the failure where it happens and refuse by name."
    )
    return ran.stdout.strip()


def header_of(path: pathlib.Path) -> dict:
    """What the artefact records about itself, read as the data it is by
    running the artefact and asking it, not by reading its characters."""
    ran = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            "import json,runpy,sys;"
            "m=runpy.run_path(sys.argv[1]);"
            "print(json.dumps(m['ARTEFACT']))",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=30.0,
    )
    assert ran.returncode == 0, (
        f"WHAT: the artefact at {path} could not be read as a Python module "
        f"holding an ARTEFACT record: exit {ran.returncode}. "
        "WHY: the build records what it built as data in the artefact, so "
        "the Owner can read it back without parsing prose. "
        f"HOW: read the failure: {ran.stderr[-600:]!r}"
    )
    return json.loads(ran.stdout)


def files_under(root: pathlib.Path) -> dict:
    """Every file under `root` with its bytes, so a refusal that touched
    nothing is told apart from one that wrote and tidied up."""
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
