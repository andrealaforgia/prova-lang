"""I1.S4.P6 / I1.S4.B4: every report from the S4 campaign stays honest about
its scope.

Given the complete set of tool responses produced for the missing-guard
boundary call, all six flipped-flag calls, all four always-reject
accepted-input calls, and the paired positive-control calls, when each
response is inspected, then none describes these runtime checks as universal
proof (no "verified", "proved"/"proven", "universal", "holds" or "guarantee"
wording), even though every one of those responses is itself a genuine,
successful or failing, concrete evaluation.
"""

from __future__ import annotations

from _i1_s4_fixtures import (
    COUNTS,
    EVENTS,
    MUTANTS,
    assert_no_universal_claim,
    evaluate_step,
    mutated_source,
    protected_source,
)

ACCEPTED_CASES = [(0, "Reserve"), (1, "Reserve"), (1, "Release"), (2, "Release")]
ALL_SIX_CASES = [(count, event) for count in COUNTS for event in EVENTS]

MISSING_GUARD = next(m for m in MUTANTS if m.id == "missing-guard")
FLIPPED_FLAG = next(m for m in MUTANTS if m.id == "flipped-flag")
ALWAYS_REJECT = next(m for m in MUTANTS if m.id == "always-reject")


def _collect_campaign_responses() -> list[dict]:
    responses = []

    _, response, _, _ = evaluate_step(mutated_source(MISSING_GUARD), 2, "Reserve")
    responses.append(response)

    flipped_source = mutated_source(FLIPPED_FLAG)
    for count, event in ALL_SIX_CASES:
        _, response, _, _ = evaluate_step(flipped_source, count, event)
        responses.append(response)

    reject_source = mutated_source(ALWAYS_REJECT)
    for count, event in ACCEPTED_CASES:
        _, response, _, _ = evaluate_step(reject_source, count, event)
        responses.append(response)

    control_source = protected_source()
    for count, event in ALL_SIX_CASES:
        _, response, _, _ = evaluate_step(control_source, count, event)
        responses.append(response)

    return responses


def test_p6_no_response_in_the_full_campaign_claims_universal_proof():
    responses = _collect_campaign_responses()
    assert len(responses) == 1 + 6 + 4 + 6
    for response in responses:
        assert response is not None, "a campaign call produced no parseable response"
        assert_no_universal_claim(response)
