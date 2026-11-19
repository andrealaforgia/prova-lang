"""Shared helpers for F23's acceptance tests: the table of refusals the
Owner reads from a built artefact, how one artefact is built and asked,
and the two shipped programs F23 is read over.

Not a test module (no `test_` prefix); pytest will not collect it.
Drives only the `prova` command's real JSON stdin/stdout surface, the
artefact file it writes, and that artefact run by a plain interpreter.
No imports from src/prova.

The six refusal words and their exit statuses below are the decision
this delivery records, not something read back out of the tool: the
tests compare what the tool publishes and what an artefact does against
this table, so a change of either is seen here. The statuses themselves
are read from _f22_fixtures, which the tests of the build already read
them from, so one table stands test-side.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
import sys

from _f22_fixtures import (
    ANSWERED,
    ASSURANCE_FAILURE,
    A_FAILURE_OF_THE_FILE,
    ILL_TYPED,
    MALFORMED,
    PRECONDITION_UNMET,
    RESOURCE_EXHAUSTED,
    artefact_of,
    build,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# What an artefact's own exit status says, and the word its first line
# carries. 0 is an answer; every other status is a refusal of its own
# kind, and none of them is a traceback. The numbers themselves stand in
# _f22_fixtures, which the tests of the build already read them from.
THE_REFUSALS = (
    ("MALFORMED", MALFORMED, "text that cannot be read as a value"),
    ("ASSURANCE", ASSURANCE_FAILURE, "a contract of the program did not hold"),
    ("ARTEFACT", A_FAILURE_OF_THE_FILE, "a failure of the generated file"),
    ("ILL-TYPED", ILL_TYPED, "a value of a type the entry does not declare"),
    ("PRECONDITION", PRECONDITION_UNMET, "the entry's precondition does not hold"),
    ("RESOURCE", RESOURCE_EXHAUSTED, "a limit of this artefact was reached"),
)

THE_WORD_OF = {status: word for word, status, _ in THE_REFUSALS}


def reservation_source() -> str:
    """The reservation component SPEC.md writes as its core conformance
    example, read from the document rather than copied."""
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    heading = "## Core conformance example"
    assert heading in text, (
        "WHAT: SPEC.md no longer writes a core conformance example. "
        "WHY: the Owner is promised that the component that document "
        "defines is built and answers its table, so the source is read "
        "from the document. "
        "HOW: read SPEC.md around the reservation example."
    )
    start = text.index(heading)
    opening = text.index("```lisp", start) + len("```lisp\n")
    return text[opening : text.index("```", opening)]


def an_artefact_of(source: str, entry: str, destination: pathlib.Path):
    """One artefact of `source` for `entry`, built by the real command
    and left at a path inside `destination`."""
    target = destination / f"{entry.replace('-', '_')}.py"
    artefact_of(build(source, entry, target), f"the program built for {entry}")
    return target


def first_line_word(ran: subprocess.CompletedProcess) -> str:
    """The category word the first line of a refusal opens with, which is
    what a reader sorting refusals reads before any prose."""
    lines = (ran.stderr or "").splitlines()
    if not lines:
        return ""
    return lines[0].split(":", 1)[0].strip()


def read_as_data(path: pathlib.Path, expression: str):
    """One value the artefact holds as data, read by running the file as
    a module and asking it, not by parsing its characters."""
    ran = subprocess.run(
        [
            sys.executable,
            "-I",
            "-c",
            "import json,runpy,sys;"
            "m=runpy.run_path(sys.argv[1]);"
            f"print(json.dumps({expression}))",
            str(path),
        ],
        capture_output=True,
        text=True,
        timeout=30.0,
    )
    assert ran.returncode == 0, (
        f"WHAT: the artefact at {path} does not hold {expression} as data: "
        f"exit {ran.returncode}. "
        "WHY: a reader must be able to look up what this artefact answers "
        "and what each of its refusals means without parsing prose. "
        f"HOW: read the failure: {ran.stderr[-600:]!r}"
    )
    return json.loads(ran.stdout)


def the_published_table() -> dict:
    """What the tool publishes about the statuses a built artefact
    answers with, read from `discover`."""
    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"operation": "discover"}),
        capture_output=True,
        text=True,
        timeout=60.0,
    )
    assert proc.returncode == 0, f"tool failure: stderr={proc.stderr[-400:]!r}"
    manifest = json.loads(proc.stdout).get("result") or {}
    return manifest.get("artefact_statuses") or {}


def with_the_upper_guard_relaxed(text: str) -> str:
    """The same artefact with the guard that stops a reserve at the full
    count changed, so the program it carries answers a state its own
    promise forbids.

    SPEC.md asks for exactly this case: a missing upper guard must be
    detected although the declared examples visit only non-full states.
    The one line of the translated program that both adds one to the
    count and tests it against the capacity is the body of the reserve
    branch; the count of matching lines is asserted, so a translation
    that no longer writes it fails here instead of quietly proving
    nothing.
    """
    lines = text.splitlines(keepends=True)
    found = [
        place
        for place, line in enumerate(lines)
        if "+ 1" in line and "< 2" in line
    ]
    assert len(found) == 1, (
        f"WHAT: {len(found)} lines of the artefact both add one to the count "
        f"and test it against the capacity of 2, and this change needs the "
        "one line that is the body of the reserve branch. "
        "WHY: a probe that cannot find what it changes proves nothing about "
        "what the artefact does when a contract fails. "
        "HOW: read the translated program in the artefact and name the body "
        "of the reserve branch in tests/acceptance/_f23_fixtures.py."
    )
    lines[found[0]] = lines[found[0]].replace("< 2", "< 3", 1)
    return "".join(lines)
