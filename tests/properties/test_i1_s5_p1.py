"""I1.S5.P1 / I1.S5.B1: `check` accepts the unmodified reservation source as
a whole-program static check with no diagnostics.

Given the complete, unmodified reservation source (three type declarations,
`valid-state`, `initial` and `step`, with their contracts and all seven
declared examples), when the real public `check` operation runs against it
at the candidate revision, then the response reports completion with no
error diagnostics and identifies its result as whole-program static
checking, not contract proof or a runtime evaluation.
"""

from __future__ import annotations

from _i1_s5_fixtures import assert_accepted, protected_source, run_check


def test_p1_check_accepts_the_unmodified_reservation_source():
    source = protected_source()
    returncode, response, stdout, stderr = run_check(source)
    assert_accepted(returncode, response, stdout, stderr)


def test_p1_check_claim_does_not_overclaim_proof_or_runtime_correctness():
    source = protected_source()
    returncode, response, stdout, stderr = run_check(source)
    assert_accepted(returncode, response, stdout, stderr)
    claim = response.get("claim") or {}
    kind = str(claim.get("kind", ""))
    assert kind not in {"evaluation", "examples"}, (
        f"check must not report an evaluation-shaped claim: {claim}"
    )
    import json

    text = json.dumps(response).lower()
    for forbidden in ("proved", "proven", "verified", "guarantee"):
        assert forbidden not in text, f"check response overclaims ({forbidden!r}): {response}"
