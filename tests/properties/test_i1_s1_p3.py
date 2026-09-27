"""I1.S1.P3: evaluation output never claims verified, proved or built.

Given all six direct-evaluation runs over the reservation source's `step`
function, when the owner inspects every field of the structured response and
the accompanying stdout/stderr, then none of it asserts that the source or
result is verified, proved or built (or an equivalent claim), even though the
response does classify the run as a positive evaluation.
"""

from __future__ import annotations

import re

import pytest

from _prova_client import load_reservation_source, run_prova

FORBIDDEN_CLAIM = re.compile(r"\b(verifie[sd]|verify|verification|prove[nd]?|proves|built|build|holds)\b", re.IGNORECASE)

SIX_PAIRS = [
    (0, "Reserve"), (1, "Reserve"), (2, "Reserve"),
    (0, "Release"), (1, "Release"), (2, "Release"),
]


def _find_forbidden(value) -> list[str]:
    hits: list[str] = []

    def walk(node):
        if isinstance(node, str):
            hits.extend(m.group(0) for m in FORBIDDEN_CLAIM.finditer(node))
        elif isinstance(node, dict):
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(value)
    return hits


@pytest.mark.parametrize("before,event", SIX_PAIRS)
def test_p3_evaluate_output_has_no_verification_claim(before, event):
    source = load_reservation_source()
    request = {
        "prova": "i1",
        "operation": "evaluate",
        "source": source,
        "function": "step",
        "arguments": [f"(Reservation {before})", f"({event})"],
    }
    returncode, response, stdout, stderr = run_prova(request)
    assert returncode == 0, f"tool failure evaluating step({before}, {event}): stderr={stderr!r}"
    assert response is not None, f"non-JSON response: {stdout!r}"
    assert response.get("status") == "completed", response
    assert response.get("claim", {}).get("kind") == "evaluation", (
        f"response does not classify itself as a positive evaluation: {response}"
    )

    body_hits = _find_forbidden(response)
    stderr_hits = FORBIDDEN_CLAIM.findall(stderr)
    assert not body_hits, f"forbidden claim wording in response body for step({before}, {event}): {body_hits}; response={response}"
    assert not stderr_hits, f"forbidden claim wording on stderr for step({before}, {event}): {stderr_hits}"
