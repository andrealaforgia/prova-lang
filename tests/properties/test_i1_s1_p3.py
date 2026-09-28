"""I1.S1.P3: evaluation output never claims verified, proved or built.

Given all six direct-evaluation runs over the reservation source's `step`
function, when the owner inspects every field of the structured response
(keys and values, at any depth) and the accompanying stdout and stderr, then
none of it affirmatively asserts that the source or result is verified,
proved, certified, guaranteed or built, while the response does positively
identify itself as an evaluation of that input.

An affirmative claim is told apart from a quotation or an explicit denial:
a sentence that negates the word ("not verified", "no proof", "never built",
"does not prove") or puts it inside quotation marks is not a claim. The
inspection is shown to reach nested fields, keys and stderr by controlled
mutations of a real response that inject false claims there, and shown not to
over-fire by benign and denial controls.
"""

from __future__ import annotations

import copy
import re

import pytest

from _prova_client import load_reservation_source, run_prova

ASSURANCE = re.compile(
    r"\b(verifi\w*|verif\w*|prov(?:e|es|ed|en|ing)|proofs?|proved|certif\w*|guarantee\w*"
    r"|built|builds?|compiled|executable|correct(?:ness)?|sound)\b",
    re.IGNORECASE,
)
NEGATION = re.compile(r"\b(not|no|never|neither|nor|without|cannot|isn't|doesn't|does not|is not|unverified)\b|n't", re.IGNORECASE)
QUOTED = re.compile(r"([\"'`“”‘’])(.*?)\1")

SIX_PAIRS = [
    (0, "Reserve"), (1, "Reserve"), (2, "Reserve"),
    (0, "Release"), (1, "Release"), (2, "Release"),
]


def claims_in_text(text: str) -> list[str]:
    hits = []
    for sentence in re.split(r"(?<=[.;!?])\s+|\n", text):
        unquoted = QUOTED.sub(" ", sentence)
        if NEGATION.search(unquoted):
            continue
        hits.extend(m.group(0) for m in ASSURANCE.finditer(unquoted))
    return hits


def claims_in(node, path="$") -> list[str]:
    hits: list[str] = []
    if isinstance(node, str):
        hits.extend(f"{path}: {h}" for h in claims_in_text(node))
    elif isinstance(node, dict):
        for key, value in node.items():
            if ASSURANCE.search(str(key)) and value not in (False, None, 0, "", [], {}):
                hits.append(f"{path}.{key} (key with affirmative value)")
            hits.extend(claims_in(value, f"{path}.{key}"))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            hits.extend(claims_in(value, f"{path}[{index}]"))
    return hits


def _evaluate(before: int, event: str):
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": load_reservation_source(),
        "function": "step",
        "arguments": [f"(Reservation {before})", f"({event})"],
    }
    return run_prova(request)


@pytest.mark.parametrize("before,event", SIX_PAIRS)
def test_p3_evaluate_output_has_no_verification_claim(before, event):
    returncode, response, stdout, stderr = _evaluate(before, event)
    assert returncode == 0, f"tool failure evaluating step({before}, {event}): stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("operation") == "evaluate", response
    assert response.get("status") == "completed", response
    claim = response.get("claim") or {}
    assert claim.get("kind") == "evaluation", (
        f"response does not identify itself as an evaluation: {response}"
    )
    assert "input" in str(claim.get("scope", "")), f"claim scope is not this input: {response}"

    assert claims_in(response) == [], f"assurance claim in response for step({before}, {event}): {claims_in(response)}"
    assert claims_in_text(stdout) == [], f"assurance claim on stdout: {claims_in_text(stdout)}"
    assert claims_in_text(stderr) == [], f"assurance claim on stderr: {claims_in_text(stderr)}"


def _real_response():
    _, response, _, _ = _evaluate(2, "Reserve")
    assert response is not None and response["status"] == "completed"
    return response


@pytest.mark.parametrize(
    "mutate",
    [
        lambda r: r["claim"].update(kind="verification"),
        lambda r: r["claim"].update(scope="the source is verified"),
        lambda r: r.setdefault("diagnostics", []).append({"category": "note", "reason": "step is proved correct"}),
        lambda r: r["result"].update(note={"deep": [{"text": "this executable was built"}]}),
        lambda r: r.update(verified=True),
        lambda r: r["result"].update(status_line="Guaranteed by the solver"),
    ],
    ids=["kind", "scope", "diagnostic", "deeply-nested", "key", "guarantee-wording"],
)
def test_p3_inspection_detects_injected_false_claims(mutate):
    mutated = copy.deepcopy(_real_response())
    assert claims_in(mutated) == []
    mutate(mutated)
    assert claims_in(mutated), f"the inspection missed an injected claim: {mutated}"


@pytest.mark.parametrize("stderr", ["the result is verified", "build succeeded", "proved."])
def test_p3_inspection_detects_a_false_claim_on_stderr(stderr):
    assert claims_in_text(stderr)


@pytest.mark.parametrize(
    "text",
    [
        "this input was evaluated",
        "not verified",
        "no proof is offered; this is an evaluation",
        'the words "verified" and "built" are not claimed',
        "the result was never built",
        "evaluation only, it does not prove anything",
    ],
)
def test_p3_inspection_accepts_denials_quotations_and_plain_evaluation(text):
    assert claims_in_text(text) == []
