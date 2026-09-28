"""I1.S1.P4 and I1.S1.P5: build/verify are refused, not attempted.

P4: given a well-formed `build` or `verify` request against the protected
reservation source, the real public command returns a parseable structured
refusal that names the requested operation, reports it unavailable, carries
no successful result, and is a deliberate refusal of that named operation:
the diagnostic identity differs from the response to an unrecognised
operation name, and the execution trace shows the request reached the
service dispatch.

P5: the same two requests run under execution tracing (audit events for
process spawn and filesystem mutation, plus every Python function entered
in the candidate). The trace must show zero entries into build/verify/
solver-style work, the checked-evaluation stages, child processes and file
writes. The detector itself is shown to fire by running it on control
scripts that really do attempt the work: entering a build function, writing
an executable and deleting it again, spawning a child process, and calling a
verifier that fails and whose failure is then concealed by an "unavailable"
answer.

Evidence limit: the trace sees Python function entries and CPython audit
events; native code that mutates files without an audit event is not seen.
"""

from __future__ import annotations

import textwrap

import pytest

from _prova_client import load_reservation_source
from _trace_client import attempted_work, run_traced

OPERATIONS = ["build", "verify"]
STATUS_VOCABULARY = {
    "completed", "unsupported", "invalid_input", "invalid_program",
    "resource_exhausted", "tool_failure", "unavailable",
}


def _request(operation: str, output_directory) -> dict:
    return {
        "prova": "i1",
        "operation": operation,
        "source": load_reservation_source(),
        "output_directory": str(output_directory),
    }


def _categories(response: dict) -> set:
    return {d.get("category") for d in (response.get("diagnostics") or [])}


def _reasons(response: dict) -> list:
    return [d.get("reason") for d in (response.get("diagnostics") or [])]


@pytest.mark.parametrize("operation", OPERATIONS)
def test_p4_operation_is_refused_as_unavailable(tmp_path, operation):
    run = run_traced(_request(operation, tmp_path))
    response = run.response
    assert response is not None, f"non-JSON response refusing {operation}: {run.stdout!r}"
    assert "Traceback" not in run.stderr, f"{operation} crashed rather than refusing: {run.stderr!r}"

    # Declared response shape: operation, a status from the closed vocabulary,
    # and diagnostics each carrying a string category and a string reason.
    assert response.get("operation") == operation, response
    assert response.get("status") in STATUS_VOCABULARY, response
    assert response.get("status") == "unavailable", response
    diagnostics = response.get("diagnostics")
    assert isinstance(diagnostics, list) and diagnostics, f"no diagnostics: {response}"
    for diagnostic in diagnostics:
        assert isinstance(diagnostic, dict), response
        assert isinstance(diagnostic.get("category"), str) and diagnostic["category"], response
        assert isinstance(diagnostic.get("reason"), str) and diagnostic["reason"], response
    assert not response.get("result"), f"{operation} refusal carried a result: {response}"
    assert "tool_failure" not in _categories(response), f"crash disguised as refusal: {response}"

    # Deliberate refusal of the *named* operation, not the unrecognised-operation
    # fallback: diagnostic identity differs from the control, and the refusal
    # names the operation.
    control = run_traced(_request("no-such-operation-p4", tmp_path)).response
    assert control is not None
    assert _categories(response) != _categories(control), (
        f"{operation} refusal is indistinguishable from the unrecognised-operation "
        f"fallback: refusal={response} control={control}"
    )
    assert any(operation in (r or "") for r in _reasons(response)), (
        f"{operation} refusal does not name the operation in any reason: {response}"
    )
    assert not any("no-such-operation-p4" in (r or "") for r in _reasons(response))

    # Dispatch evidence: the request went through the service's dispatch.
    assert ("prova.service", "handle") in run.calls, (
        f"trace shows no entry into the dispatch, so the refusal is unobserved: {run.calls}"
    )

    # Stable identity across identical requests.
    again = run_traced(_request(operation, tmp_path)).response
    assert again is not None and _categories(again) == _categories(response)


@pytest.mark.parametrize("operation", OPERATIONS)
def test_p5_refusal_does_not_attempt_the_work(tmp_path, operation):
    (tmp_path / "pre-existing.txt").write_bytes(b"keep")
    run = run_traced(_request(operation, tmp_path))
    assert run.response is not None and run.response.get("status") == "unavailable", run.stdout
    # Coverage sanity: the tracer really observed candidate code, including dispatch.
    assert ("prova.service", "handle") in run.calls, run.calls
    assert any(module.startswith("prova") for module, _ in run.calls)
    work = attempted_work(run)
    assert not work, f"{operation} refusal attempted work: {work}"


CONTROLS = {
    "enters-a-build-function": """
        def build_executable(path):
            return path
        def main():
            build_executable("out")
            print('{"operation": "build", "status": "unavailable", "diagnostics": []}')
        main()
    """,
    "enters-a-verifier-that-fails-then-conceals": """
        def run_verifier():
            raise RuntimeError("solver crashed")
        def main():
            try:
                run_verifier()
            except RuntimeError:
                pass
            print('{"operation": "verify", "status": "unavailable", "diagnostics": []}')
        main()
    """,
    "creates-then-deletes-an-executable": """
        import os
        def main():
            with open("program-p5-control", "wb") as handle:
                handle.write(b"x")
            os.remove("program-p5-control")
            print('{"operation": "build", "status": "unavailable", "diagnostics": []}')
        main()
    """,
    "spawns-a-child-process": """
        import subprocess, sys
        def main():
            subprocess.run([sys.executable, "-c", "pass"])
            print('{"operation": "build", "status": "unavailable", "diagnostics": []}')
        main()
    """,
}


@pytest.mark.parametrize("name", sorted(CONTROLS))
def test_p5_controlled_attempted_work_is_detected(tmp_path, monkeypatch, name):
    monkeypatch.chdir(tmp_path)
    script = tmp_path / "control.py"
    script.write_text(textwrap.dedent(CONTROLS[name]), encoding="utf-8")
    run = run_traced({"operation": "build"}, entry=str(script))
    assert run.response is not None and run.response.get("status") == "unavailable"
    assert attempted_work(run), f"the tracer missed attempted work in control {name!r}: {run.calls} {run.events}"


def test_p5_benign_control_is_not_flagged(tmp_path):
    script = tmp_path / "control.py"
    script.write_text(
        'def handle():\n    print(\'{"operation": "build", "status": "unavailable"}\')\nhandle()\n',
        encoding="utf-8",
    )
    run = run_traced({"operation": "build"}, entry=str(script))
    assert run.response is not None
    assert attempted_work(run) == []
