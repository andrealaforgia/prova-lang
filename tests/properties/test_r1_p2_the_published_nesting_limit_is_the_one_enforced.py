"""R1.P2 -- law: the nesting the manifest publishes is exactly the
nesting the tool reads.

A caller that reads a limit from the manifest and writes a generator
against it must meet the same boundary in practice. If the published
number were larger than the enforced one the generator would still be
driven into a refusal it did not expect; if it were smaller the caller
would stay needlessly shallow and could not tell which number is real.

still passes if: the tool refused everything. The first property
requires every depth at or under the limit to be answered normally.
"""

from __future__ import annotations

import json

from hypothesis import HealthCheck, given, settings, strategies as st

from _r1_mangled_requests import ask, nested_program

DERANDOMIZED = settings(
    derandomize=True,
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)

NESTING_LIMIT_NAME = "expression_nesting"
RESOURCE_EXHAUSTED = "resource_exhausted"
NESTING_LIMIT_EXCEEDED = "nesting_limit_exceeded"


def _manifest() -> dict:
    answer = ask({"operation": "discover"})
    assert answer.crash is None and answer.exit_code == 0, (
        f"the manifest could not be read: {answer.crash!r}, exit "
        f"{answer.exit_code}. Everything below reads the limit from it."
    )
    return json.loads(answer.stdout)["result"]


def _published_limit() -> int:
    limits = _manifest().get("resource_limits", {})
    declared = limits.get("limits", {}).get(NESTING_LIMIT_NAME)
    assert isinstance(declared, dict) and isinstance(declared.get("maximum"), int), (
        f"the manifest publishes no whole-number {NESTING_LIMIT_NAME!r} limit: "
        f"{limits}. A caller cannot write a generator against a limit it must "
        "discover by crashing into it."
    )
    return declared["maximum"]


def _answer_to(depth: int) -> dict:
    answer = ask({"operation": "check", "source": nested_program(depth)})
    assert answer.crash is None, (
        f"a program nested {depth} deep came back as "
        f"{type(answer.crash).__name__}: {answer.crash}. "
        "Every depth is answered."
    )
    return json.loads(answer.stdout)


@DERANDOMIZED
@given(room=st.integers(min_value=0, max_value=120))
def test_every_depth_up_to_the_published_limit_is_accepted(room):
    """LAW2, the side under the limit: a program nested at or under the
    published limit is checked and accepted, so the number published is
    a depth a caller may really use.
    """
    limit = _published_limit()
    depth = max(5, limit - room)

    answer = _answer_to(depth)

    assert answer["status"] == "completed", (
        f"a program nested {depth} deep was answered {answer['status']!r} "
        f"against a published limit of {limit}: {answer}. Everything at or "
        "under the published number is read as before; a tool that refuses it "
        "publishes a limit a caller cannot use."
    )


@DERANDOMIZED
@given(over=st.integers(min_value=1, max_value=400))
def test_every_depth_past_the_published_limit_is_refused_for_its_nesting(over):
    """LAW2, the side past the limit: a program nested past the
    published limit is refused for the nesting, with the published limit
    and the depth it reached, however far past it goes.
    """
    limit = _published_limit()
    depth = limit + over

    answer = _answer_to(depth)

    assert answer["status"] == RESOURCE_EXHAUSTED, (
        f"a program nested {depth} deep against a limit of {limit} was answered "
        f"{answer['status']!r}: {answer}. Past the published limit the tool "
        "stops reading, and says so as a budget, not as a rule of the language."
    )
    refusals = [
        entry
        for entry in answer.get("diagnostics", [])
        if entry.get("category") == NESTING_LIMIT_EXCEEDED
    ]
    assert len(refusals) == 1, (
        f"a program nested {depth} deep carries {len(refusals)} nesting "
        f"refusals: {answer}. A caller reads one cause."
    )
    refusal = refusals[0]
    assert refusal.get("expected") == limit, (
        f"the refusal at depth {depth} says {refusal.get('expected')!r} was "
        f"allowed while the manifest publishes {limit}: {refusal}. The number a "
        "caller reads and the number the tool enforces are the same number."
    )
    assert refusal.get("actual") == limit + 1, (
        f"the refusal at depth {depth} says the text reached "
        f"{refusal.get('actual')!r}: {refusal}. The tool stops at the first "
        "form past the limit, so the depth it reports is one past it however "
        "deep the text goes."
    )
    assert refusal.get("location", {}).get("line"), (
        f"the refusal at depth {depth} says where nowhere: {refusal}. A reader "
        "of it has no line to open."
    )
