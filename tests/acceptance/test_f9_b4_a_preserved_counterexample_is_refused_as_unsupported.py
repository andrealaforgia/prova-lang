"""F9.B4 -- the preserved counterexamples in `evidence/cases/` reach the
real command, and the one checked here is refused for the construct
core-0 does not have, while its adaptation to core-0 is answered by the
ordinary rules.

The whole family of fourteen is walked by the law in
`tests/properties/test_f9_out_of_profile_source.py`, which asks the
service in process. This test proves the same answer comes out of the
command a reader actually runs.

Drives only the `prova` command's real JSON stdin/stdout surface for the
answer; it reads the preserved file from the repository, as a reader
would.

still passes if: the file had been edited to contain anything at all.
The test requires the refusal to name the construct that stands in the
preserved text, and its adaptation is derived from that same text.
"""

from __future__ import annotations

from _f9_profile_fixtures import (
    EVIDENCE_CASES,
    PRESERVED_CASES,
    assert_answered_without_the_unsupported_status,
    assert_unsupported_naming,
    check,
)

CASE = "false-contract"


def test_the_fourteen_preserved_counterexamples_are_all_present():
    """Given the repository, when the preserved cases are listed, then
    the 14 files the evidence note records are there to be checked."""
    present = sorted(path.stem for path in EVIDENCE_CASES.glob("*.prova"))

    assert present == sorted(PRESERVED_CASES), (
        f"the preserved counterexamples on disk are {present}, which is not the "
        f"{len(PRESERVED_CASES)} this feature wires into the checks: "
        f"{sorted(PRESERVED_CASES)}. They are provenance: a file added or "
        "removed must be recorded here with what its refusal should say."
    )


def test_a_preserved_counterexample_is_refused_by_the_command_as_out_of_profile():
    """Given the preserved file `false-contract.prova`, which ends with
    the call `(wrong 1)`, when the command checks it, then it is refused
    as unsupported naming the top-level expression, and the same case
    with that call removed is accepted."""
    case = PRESERVED_CASES[CASE]

    assert_unsupported_naming(
        check(case.source(CASE)),
        naming=case.naming,
        why=f"the preserved counterexample {CASE!r}",
    )

    assert_answered_without_the_unsupported_status(
        check(case.adaptation(CASE)),
        expected_status=case.adapted_status,
        why=f"{CASE!r} written with only what core-0 has",
    )
