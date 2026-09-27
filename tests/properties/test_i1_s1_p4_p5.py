"""I1.S1.P4 and I1.S1.P5: build/verify are refused, not attempted.

Given a well-formed `build` or `verify` request against the protected
reservation source, when either is sent to the real public interface, then
the response explicitly names the requested operation and reports it as an
unavailable structured failure rather than a successful result (P4); and
that refusal is reached without creating any file in the requested output
location or taking noticeably longer than an immediate refusal, so the
result is not merely a build/verify attempt that happened to fail (P5).

P5's non-attempt evidence is a filesystem-and-timing proxy appropriate to a
black-box CLI candidate: this test observes the subprocess's own visible
effects (files written, wall-clock elapsed), not internal syscalls. It
cannot see a build/verify entry point that starts and is aborted internally
without touching the filesystem or taking noticeable time; that would need
in-process instrumentation once an implementation exists.
"""

from __future__ import annotations

import time

import pytest

from _prova_client import load_reservation_source, run_prova, snapshot_tree

OPERATIONS = ["build", "verify"]


@pytest.mark.parametrize("operation", OPERATIONS)
def test_p4_operation_is_refused_as_unavailable(tmp_path, operation):
    source = load_reservation_source()
    request = {
        "prova": "i1",
        "operation": operation,
        "source": source,
        "output_directory": str(tmp_path),
    }
    returncode, response, stdout, stderr = run_prova(request)
    assert response is not None, f"non-JSON response refusing {operation}: {stdout!r}"
    assert response.get("operation") == operation, response
    assert response.get("status") == "unavailable", response
    assert not response.get("result"), f"{operation} refusal carried a result: {response}"

    diagnostics = response.get("diagnostics") or []
    categories = {d.get("category") for d in diagnostics}
    assert "operation_unavailable" in categories, (
        f"{operation} refusal did not report the operation_unavailable diagnostic "
        f"category that distinguishes a deliberate scope refusal from an accidental "
        f"failure: categories={categories}, response={response}"
    )
    assert "tool_failure" not in categories, (
        f"{operation} refusal reported a tool_failure diagnostic alongside status "
        f"'unavailable', suggesting a crashed attempt rather than a clean refusal: {response}"
    )


@pytest.mark.parametrize("operation", OPERATIONS)
def test_p5_refusal_does_not_attempt_the_work(tmp_path, operation):
    source = load_reservation_source()
    before = snapshot_tree(tmp_path)
    started = time.monotonic()
    request = {
        "prova": "i1",
        "operation": operation,
        "source": source,
        "output_directory": str(tmp_path),
    }
    returncode, response, stdout, stderr = run_prova(request, timeout=10.0)
    elapsed = time.monotonic() - started
    after = snapshot_tree(tmp_path)

    assert response is not None, f"non-JSON response refusing {operation}: {stdout!r}"
    assert response.get("status") == "unavailable", response
    assert after == before, (
        f"{operation} refusal changed the output directory's contents: before={before} after={after}"
    )
    assert elapsed < 5.0, (
        f"{operation} refusal took {elapsed:.2f}s, which is consistent with an attempted "
        f"build/verify rather than an immediate structured refusal"
    )
