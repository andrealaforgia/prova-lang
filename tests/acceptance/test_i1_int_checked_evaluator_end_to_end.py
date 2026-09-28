"""Acceptance test for I1.INT: the integrated increment of I1 -- a checked
evaluator -- is demonstrable end to end through the product's real surface.

One Owner session, each request its own fresh `prova` process: check the
reservation program; run `step` on a fresh input; run its declared examples;
see an invalid input, a wrong body and an invalid program each rejected under
its own distinct category; and see `build` and `verify` refused as
unavailable. No response in the session claims verification, proof or a build.

Drives only the `prova` command's JSON stdin/stdout surface. No imports from
src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

FORBIDDEN_WORDS = ("verified", "proved", "built", "holds")

RESERVE_OLD = "(Outcome (Reservation (+ (.reserved current) 1)) true)"
RESERVE_TYPE_ERROR = (
    "(Outcome (Reservation (if (= (.reserved current) 1) "
    "(+ true 1) (+ (.reserved current) 1))) true)"
)
ALWAYS_REJECT_BODY_OLD_START = "  (match event\n    ((Reserve)\n"


def _reservation_source() -> str:
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    start = text.index("## Core conformance example")
    fence_start = text.index("```lisp", start) + len("```lisp\n")
    return text[fence_start:text.index("```", fence_start)]


def _wrong_body_source(source: str) -> str:
    """The reservation source whose `step` always rejects its event."""
    body_start = source.index(ALWAYS_REJECT_BODY_OLD_START)
    body_end = source.index("\n\n", body_start) if "\n\n" in source[body_start:] else len(source)
    assert body_end > body_start
    return source[:body_start] + "  (Outcome current false))" + source[body_end:]


def _session_request(request: dict) -> tuple[dict, str]:
    proc = subprocess.run(
        ["prova"],
        input=json.dumps({"prova": "i1", **request}),
        capture_output=True,
        text=True,
        timeout=10.0,
    )
    assert proc.returncode == 0, f"tool failure on {request.get('operation')}: {proc.stderr!r}"
    try:
        return json.loads(proc.stdout), proc.stdout
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(f"non-JSON response: {proc.stdout!r}")


def _categories(response: dict) -> set[str]:
    return {d.get("category") for d in (response.get("diagnostics") or [])}


def test_int_owner_checks_evaluates_examples_and_sees_rejections_and_refusals():
    """Given the reservation program, when the Owner checks it, evaluates
    `step` on a fresh input, runs its declared examples, and then submits an
    invalid entry state, a wrong `step` body and an ill-typed program, and
    finally asks for build and verify, then: the good program is accepted and
    evaluated correctly with every example passing; each bad case is rejected
    under its own category with no successful result; build and verify are
    refused as unavailable; and nothing claims verification or a build."""
    source = _reservation_source()
    raw_outputs: list[str] = []

    def call(request: dict) -> dict:
        response, raw = _session_request(request)
        raw_outputs.append(raw)
        return response

    # 1. The program is checked and accepted with no diagnostics.
    checked = call({"operation": "check", "source": source})
    assert checked.get("operation") == "check", checked
    assert checked.get("status") == "completed", checked
    assert not checked.get("diagnostics"), checked

    # 2. `step` evaluates on a fresh input, with the table's expected result.
    evaluated = call({
        "operation": "evaluate", "source": source, "function": "step",
        "arguments": ["(Reservation 1)", "(Reserve)"],
    })
    assert evaluated.get("status") == "completed", evaluated
    assert (evaluated.get("result") or {}).get("value") == "(Outcome (Reservation 2) true)", evaluated

    # 3. Every declared example runs and passes.
    examples = call({"operation": "examples", "source": source})
    assert examples.get("status") == "completed", examples
    entries = (examples.get("result") or {}).get("examples") or []
    assert entries, f"no per-example results: {examples}"
    assert all(e.get("passed") is True for e in entries), entries

    # 4. An invalid entry state is rejected before the body runs.
    bad_input = call({
        "operation": "evaluate", "source": source, "function": "step",
        "arguments": ["(Reservation 3)", "(Reserve)"],
    })
    assert not (bad_input.get("result") or {}).get("value"), bad_input
    assert "precondition_violation" in _categories(bad_input), bad_input

    # 5. A wrong body is caught by the postcondition on a valid input.
    wrong_source = _wrong_body_source(source)
    assert wrong_source != source
    wrong_body = call({
        "operation": "evaluate", "source": wrong_source, "function": "step",
        "arguments": ["(Reservation 0)", "(Reserve)"],
    })
    assert not (wrong_body.get("result") or {}).get("value"), wrong_body
    assert "postcondition_violation" in _categories(wrong_body), wrong_body

    # 6. An invalid program is rejected by the whole-program check.
    assert source.count(RESERVE_OLD) == 1
    invalid_program = call({
        "operation": "check",
        "source": source.replace(RESERVE_OLD, RESERVE_TYPE_ERROR, 1),
    })
    assert invalid_program.get("status") == "invalid_program", invalid_program
    assert "type_mismatch" in _categories(invalid_program), invalid_program

    # The three rejections are distinguishable by category.
    assert len({"precondition_violation", "postcondition_violation", "type_mismatch"}) == 3

    # 7. Build and verify are refused as unavailable, never attempted.
    for operation in ("build", "verify"):
        refused = call({"operation": operation, "source": source})
        assert refused.get("operation") == operation, refused
        assert refused.get("status") == "unavailable", refused

    # 8. Nothing in the whole session claims verification, proof or a build.
    for raw in raw_outputs:
        lowered = raw.lower()
        for word in FORBIDDEN_WORDS:
            assert word not in lowered, f"response claims {word!r}: {raw}"
