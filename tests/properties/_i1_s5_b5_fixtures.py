"""Shared fixtures for I1.S5.B5 property tests (P7, P8, P9): declarations
that omit the mandatory `examples` clause, their repaired counterparts, and
the response assertions common to all three properties.

Not a test module (no `test_` prefix); pytest will not collect it.
"""

from __future__ import annotations

import itertools
import json
import re

from _prova_client import run_prova

OPERATIONS = ("check", "examples", "evaluate")

# The two sources named verbatim by I1.S5.B5.
P7_PLAIN = "(defn f (sig ((n Int)) -> Int ! pure) (+ n 1))"
P7_ENSURES = (
    "(defn f (sig ((n Int)) -> Int ! pure) (ensures (= result (+ n 1))) (+ n 1))"
)
P7_PLAIN_REPAIRED = (
    "(defn f (sig ((n Int)) -> Int ! pure) (examples (example (f 0) => 1)) (+ n 1))"
)
P7_ENSURES_REPAIRED = (
    "(defn f (sig ((n Int)) -> Int ! pure) (ensures (= result (+ n 1)))"
    " (examples (example (f 0) => 1)) (+ n 1))"
)

SIG = "(sig ((n Int)) -> Int ! pure)"
HELPER = "(defn helper " + SIG + " (examples (example (helper 0) => 0)) n)"

CONTRACTS = {
    "neither": (),
    "requires-only": ("(requires (>= n 0))",),
    "ensures-only": ("(ensures (>= result n))",),
    "requires-then-ensures": ("(requires (>= n 0))", "(ensures (>= result n))"),
}
BODIES = {
    "n": ("n", 0),
    "n-plus-1": ("(+ n 1)", 1),
    "if-true": ("(if true (+ n 1) n)", 1),
}
PLACEMENTS = ("sole", "before-helper", "after-helper")


def declaration(contract: str, body: str, *, with_examples: bool) -> str:
    """One `f` declaration; the examples clause is the only thing `with_examples` toggles."""
    text, delta = BODIES[body]
    clauses = list(CONTRACTS[contract])
    if with_examples:
        clauses.append(f"(examples (example (f 0) => {delta}))")
    return f"(defn f {SIG} {' '.join(clauses)} {text})".replace("  ", " ")


def place(decl: str, placement: str) -> str:
    return {
        "sole": decl,
        "before-helper": f"{decl}\n{HELPER}",
        "after-helper": f"{HELPER}\n{decl}",
    }[placement]


def matrix() -> list[tuple[str, str, str, str]]:
    return list(itertools.product(CONTRACTS, BODIES, PLACEMENTS, OPERATIONS))


def case_id(case) -> str:
    return "-".join(case)


def request(operation: str, source: str, placement: str, arg: int = 0, function: str | None = None):
    """A public-surface request. Multi-function evaluate selects the valid helper."""
    req = {"prova": "i1", "operation": operation, "source": source}
    if operation == "evaluate":
        req["function"] = function or ("f" if placement == "sole" else "helper")
        req["arguments"] = [str(arg)]
    return req


def call(req: dict):
    returncode, response, stdout, stderr = run_prova(req)
    return returncode, response, stdout, stderr


def assert_missing_examples_rejection(operation, returncode, response, stdout, stderr, where=""):
    assert returncode == 0, f"{where}: non-zero/crash exit {returncode}, stderr={stderr!r}"
    for stream in (stdout, stderr):
        assert "Traceback" not in stream, (
            f"{where}: traceback text in output: {stream[:300]!r}"
        )
    assert response is not None, f"{where}: stdout is not one JSON response: {stdout!r}"
    assert response.get("operation") == operation, f"{where}: {response}"
    assert response.get("status") == "invalid_program", f"{where}: {response}"
    assert not response.get("result"), f"{where}: rejection carried a result: {response}"
    diagnostics = response.get("diagnostics") or []
    assert diagnostics, f"{where}: no diagnostics: {response}"
    assert any(
        d.get("category") == "syntax"
        and "examples" in str(d.get("reason", "")).lower()
        and re.search(r"\bf\b", str(d.get("reason", "")))
        for d in diagnostics
    ), f"{where}: no syntax diagnostic naming the missing examples clause and function f: {diagnostics}"
    assert "verified" not in json.dumps(response).lower(), f"{where}: {response}"


def assert_accepted_check(response, returncode, where=""):
    assert returncode == 0 and response is not None, f"{where}: {response}"
    assert response.get("status") == "completed", f"{where}: {response}"
    assert not response.get("diagnostics"), f"{where}: {response}"
    assert (response.get("claim") or {}).get("kind") == "static_check", f"{where}: {response}"
