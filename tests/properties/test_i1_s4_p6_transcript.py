"""I1.S4.P6 (whole-campaign claim inspection): the campaign transcript is
reconciled against the expected request inventory (30 calls: 6 + 18 + 6),
and every response, structured and free-text, stays confined to a per-input
runtime evaluation. No field, scope, diagnostic or summary presents the runs
as universal proof, induction, verification or a build.
"""

from __future__ import annotations

import json
import re

from _i1_s4_v4 import ALL_SIX, campaign

UNIVERSAL_PATTERNS = [
    r"\bverified\b", r"\bproved\b", r"\bproven\b", r"\bproof\b", r"\buniversal(ly)?\b", r"\bfor all\b",
    r"\bfor every\b", r"\balways holds\b", r"\bguarantee[sd]?\b", r"\binduct(ion|ive)\b", r"\bbuilt\b",
    r"\ball inputs\b", r"\bany input\b", r"\bnever violated\b", r"\bcorrect(ness)?\b", r"\bsafe\b", r"\bexhaustive\b",
]


def _strings(node):
    if isinstance(node, str):
        yield node
    elif isinstance(node, dict):
        for k, v in node.items():
            yield k
            yield from _strings(v)
    elif isinstance(node, list):
        for v in node:
            yield from _strings(v)


def test_p6_transcript_reconciles_with_the_request_inventory():
    calls = campaign()
    assert len(calls) == 30
    expected = ([("protected", c, e) for c, e in ALL_SIX]
                + [(m, c, e) for m in ("missing-guard", "flipped-flag", "always-reject") for c, e in ALL_SIX]
                + [("protected", c, e) for c, e in ALL_SIX])
    assert [(c.source_id, c.count, c.event) for c in calls] == expected
    for c in calls:
        assert c.returncode == 0 and c.response is not None, f"missing or malformed response: {c.stdout!r}"
        assert c.response["operation"] == "evaluate"


def test_p6_every_response_claims_only_evaluation_of_this_input():
    for c in campaign():
        assert c.response["claim"] == {"kind": "evaluation", "scope": "this input"}, c.response["claim"]
        assert c.response["source_digest"] == c.source_digest, "response detached from its concrete source"
        assert set(c.response) <= {"operation", "status", "claim", "source_digest", "diagnostics", "result"}, (
            f"unexpected response field(s) in {sorted(c.response)}"
        )


def test_p6_no_text_anywhere_upgrades_the_evidence_kind():
    for c in campaign():
        text = " ".join(_strings(c.response)).lower() + " " + c.stdout.lower() + " " + c.stderr.lower()
        for pattern in UNIVERSAL_PATTERNS:
            assert not re.search(pattern, text), f"{pattern!r} in report for {c.source_id} ({c.count}, {c.event}): {c.stdout}"


def test_p6_reports_do_not_grow_stronger_across_the_campaign():
    # aggregation must not strengthen: repeated controls report the same kind/scope as one-off mutant calls
    claims = {json.dumps(c.response["claim"], sort_keys=True) for c in campaign()}
    assert len(claims) == 1
    verdicts = {(c.source_id, c.response["status"]) for c in campaign()}
    assert all(status == "completed" for _, status in verdicts)


def test_p6_inspection_is_capable_of_flagging_an_upgraded_claim():
    # positive control: the scan must fire on wording that would upgrade the evidence kind
    for sample in ("Verified for all inputs", "the invariant is proven by induction", "build succeeded; built artefact"):
        assert any(re.search(p, sample.lower()) for p in UNIVERSAL_PATTERNS), sample
