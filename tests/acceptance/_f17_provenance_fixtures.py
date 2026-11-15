"""Shared helpers for the tests of F17: what every answer says it stands
on, and which versions it used.

Not a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface, as the
other acceptance tests here do. No imports from src/prova.

Every answer is asked once per process and kept, so a file that reads
several things about one answer pays for one run of the command.
"""

from __future__ import annotations

import hashlib
import json
import subprocess

# A program of 2 functions, the second calling the first from its
# contract, so the answers below carry obligations, examples and a tree
# rather than the emptiest case of each.
A_PROGRAM = """(defn positive
  (sig ((n Int)) -> Bool ! pure)
  (examples (example (positive 3) => true))
  (> n 0))

(defn twice
  (sig ((n Int)) -> Int ! pure)
  (requires (positive n))
  (ensures (positive result))
  (examples (example (twice 2) => 4))
  (* n 2))
"""

# The same program with 1 more function: another revision of the same
# file, as a client would hold after an edit.
A_LATER_REVISION = A_PROGRAM + """
(defn thrice
  (sig ((n Int)) -> Int ! pure)
  (examples (example (thrice 2) => 6))
  (* n 3))
"""

# A source that is no program at all, used where an answer must carry
# nothing about a program.
NOT_A_PROGRAM = "(defn"

# The operations that read a program and answer about it.
THE_OPERATIONS_THAT_READ_A_PROGRAM = ("check", "examples", "verify", "parse", "format")

# The four versions SPEC.md lines 270-284 ask every answer to name.
THE_VERSIONS_AN_ANSWER_NAMES = ("compiler", "encoding", "solver", "runtime")

# How a version that this tool does not use is written.
DOES_NOT_APPLY = "not applicable:"

_ANSWERS: dict = {}


def ask(request: dict) -> dict:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=20.0,
    )
    assert proc.returncode == 0, (
        f"WHAT: the command exited {proc.returncode} for {request.get('operation')!r} "
        f"instead of answering. WHY: every request is answered. "
        f"HOW: read the failure on its error output: {proc.stderr[-400:]!r}"
    )
    return json.loads(proc.stdout)


def answer_about(operation: str, source: str = A_PROGRAM) -> dict:
    """The answer to one operation over one source, asked once."""
    key = (operation, source)
    if key not in _ANSWERS:
        _ANSWERS[key] = ask({"operation": operation, "source": source})
    return _ANSWERS[key]


def the_manifest() -> dict:
    """What `discover` publishes, asked once."""
    if "manifest" not in _ANSWERS:
        _ANSWERS["manifest"] = ask({"operation": "discover"})
    return _ANSWERS["manifest"]


def digest_of(source: str) -> str:
    """The revision of a text, computed the way the manifest publishes
    it: the SHA-256 of the characters sent, as UTF-8."""
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def what_it_stands_on(answer: dict, why: str) -> dict:
    stands_on = answer.get("stands_on")
    assert isinstance(stands_on, dict), (
        f"WHAT: the answer {why} does not say what it stands on: "
        f"{sorted(answer)}. "
        "WHY: a reader of an answer has to know which revision of a source "
        "and which versions of the tool it stands on, or evidence of one kind "
        "is read as evidence of another. "
        "HOW: carry a 'stands_on' object beside the claim of every completed "
        "answer."
    )
    return stands_on


def versions_of(answer: dict, why: str) -> dict:
    named = what_it_stands_on(answer, why).get("versions")
    assert isinstance(named, dict), (
        f"WHAT: the answer {why} names no versions: "
        f"{what_it_stands_on(answer, why)}. "
        "WHY: an answer that does not say which compiler, encoding, solver and "
        "runtime it used cannot be reproduced or compared with another. "
        "HOW: carry a 'versions' object naming all four."
    )
    return named
