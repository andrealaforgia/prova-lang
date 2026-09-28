"""Acceptance test for I1.S5.B1: the unmodified reservation source is
accepted by whole-program static checking, with no errors.

Drives only the `prova` command's real JSON stdin/stdout surface, per the
I1 change plan. No imports from src/prova.
"""

from __future__ import annotations

import hashlib

from _reservation_fixtures import reservation_source, run_check


def test_b1_unmodified_reservation_source_is_accepted_with_no_errors():
    """Given the unmodified reservation source, when the Owner runs the
    check operation against it, then the tool reports the whole program as
    accepted with no errors, having actually processed that input."""
    source = reservation_source()
    response = run_check(source)

    assert response.get("operation") == "check", response
    assert response.get("status") == "completed", (
        f"expected the whole program to be accepted, got: {response}"
    )
    assert not response.get("diagnostics"), (
        f"acceptance carried diagnostics: {response}"
    )
    assert response.get("claim") == {"kind": "static_check", "scope": "this input"}, (
        f"unexpected claim block: {response}"
    )

    # A stub that unconditionally returns "completed, no diagnostics" for any
    # input could satisfy the assertions above without reading `source` at
    # all. Requiring the reported digest to match this specific source's own
    # hash forces the tool to have actually taken this input into account.
    expected_digest = hashlib.sha256(source.encode("utf-8")).hexdigest()
    assert response.get("source_digest") == expected_digest, (
        f"reported source digest does not match a hash of the actual input "
        f"source, so the response cannot be tied to this program: {response}"
    )
