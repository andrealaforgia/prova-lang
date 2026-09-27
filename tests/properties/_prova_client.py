"""Shared oracle-side helpers for I1 property tests.

Not a test module (no `test_` prefix); pytest will not collect it. Talks to
the `prova` console script as a subprocess over stdin/stdout JSON, per the
I1 change plan's interface. Owns the value-syntax mini-parser used to read
back evaluation results without importing anything from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
# A history rewrite (rebase/force-push) that drops this commit turns
# `git show <sha>:SPEC.md` into a CalledProcessError, not a clean assertion
# failure; a P7 crash should be diagnosed against that possibility first.
BASELINE_SHA = "30fcbe9dda345d5b7283790023032c0145765428"
# The SPEC.md commit I1.S2's property questions pin as the reservation
# example's oracle -- the definition commit itself, not the S1 baseline
# above. Deliberately a different sha: S2's mutation-matrix and
# transition-table checks must trace back to where the example was first
# published, independent of anything S1 already guards.
SPEC_ORACLE_SHA = "ee5e1556b3a5e06945a02a61ef3a4cad51744b12"


def run_prova(request: dict, timeout: float = 10.0) -> tuple[int, dict | None, str, str]:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps(request),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    try:
        parsed = json.loads(proc.stdout)
    except (json.JSONDecodeError, ValueError):
        parsed = None
    return proc.returncode, parsed, proc.stdout, proc.stderr


def load_reservation_source() -> str:
    return _extract_reservation_source(_working_tree_spec_text())


def load_reservation_source_at(sha: str) -> str:
    return _extract_reservation_source(_spec_text_at(sha))


def protected_region(spec_text: str) -> str:
    """SPEC.md's "Core conformance example" section, header to header.

    Wider than the code block alone: also covers the six-row transition
    table and the surrounding prose, so a change to any of those (not just
    the source) is caught.
    """
    start = spec_text.index("## Core conformance example")
    end = spec_text.index("## Empirical evaluation", start)
    return spec_text[start:end]


def _working_tree_spec_text() -> str:
    return (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")


def _spec_text_at(sha: str) -> str:
    result = subprocess.run(
        ["git", "show", f"{sha}:SPEC.md"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def _extract_reservation_source(text: str) -> str:
    heading = "## Core conformance example"
    start = text.index(heading)
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    fence_end = text.index("```", fence_start)
    return text[fence_start:fence_end]


def _tokenize(text: str) -> list[str]:
    tokens: list[str] = []
    i, n = 0, len(text)
    while i < n:
        c = text[i]
        if c.isspace():
            i += 1
            continue
        if c in "()":
            tokens.append(c)
            i += 1
            continue
        j = i
        while j < n and not text[j].isspace() and text[j] not in "()":
            j += 1
        tokens.append(text[i:j])
        i = j
    return tokens


def parse_value(text: str):
    """Parse Prova's `value ::= integer | true | false | () | (Constructor value*)`.

    Returns int, bool, None (Unit) or (ctor_name, tuple_of_values) for a
    constructor application.
    """
    tokens = _tokenize(text)
    pos = [0]

    def parse_one():
        tok = tokens[pos[0]]
        if tok == "(":
            pos[0] += 1
            if tokens[pos[0]] == ")":
                pos[0] += 1
                return None
            ctor = tokens[pos[0]]
            pos[0] += 1
            args = []
            while tokens[pos[0]] != ")":
                args.append(parse_one())
            pos[0] += 1
            return (ctor, tuple(args))
        pos[0] += 1
        if tok == "true":
            return True
        if tok == "false":
            return False
        if tok == "()":
            return None
        return int(tok)

    value = parse_one()
    if pos[0] != len(tokens):
        raise ValueError(f"trailing tokens after parsing value: {text!r}")
    return value


def snapshot_tree(root: pathlib.Path) -> dict[str, bytes]:
    return {
        str(path.relative_to(root)): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
