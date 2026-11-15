"""Property tests for F9's laws about source the `core-0` profile does
not define.

LAW1 -- for every construct core-0 does not have and every operation
that reads source, the answer is the `unsupported` status carrying one
out-of-profile refusal, no claim and no result: the boundary is decided
once, where every operation reads the source, so a caller meets the same
answer whichever operation it asked.

LAW2 -- every out-of-profile refusal names the construct and stands at
the line and column the construct occupies, so a reader is sent to it.

LAW3 -- each of the fourteen counterexamples preserved in
`evidence/cases/` is refused for the construct core-0 does not have, and
the same case written with only what core-0 has is answered by the
ordinary rules instead.

LAW4 -- the answer changes for exactly those sources: everything core-0
already accepted is still accepted, and every mistake core-0 already
refused keeps the status and the categories its own rule owns.

The families below are closed, enumerated sets: every construct SPEC.md
names as outside the profile, crossed with the four operations that read
source. The laws are over the cross product, so the pair under
observation is drawn rather than written out.

Exercises the service's public operation contract in process, as the
other property tests here do. The family itself is shared with the
acceptance tests that drive the real command, so one description of each
case serves both.
"""

from __future__ import annotations

import pathlib
import sys

from hypothesis import given, settings
from hypothesis import strategies as st

from prova import service

# One description of the out-of-profile family serves both the command
# tests and these laws; it lives beside the command tests that read it
# most, and is loaded from there rather than copied.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "acceptance"))

from _f9_profile_fixtures import (  # noqa: E402
    MISSPELLED_DECLARATION_WORD,
    OUT_OF_PROFILE,
    PRESERVED_CASES,
    SHIPPED_PROGRAMS,
    UNBOUND_NAME_IN_PROFILE,
    UNSUPPORTED_CATEGORY,
    UNSUPPORTED_STATUS,
    shipped_source,
)

SOURCE_READING_OPERATIONS = ("check", "examples", "verify", "evaluate")


def _ask(operation: str, source: str) -> dict:
    request = {"prova": "i1", "operation": operation, "source": source}
    if operation == "evaluate":
        request["function"] = "f"
        request["arguments"] = []
    return service.handle(request)


def _answer_for(operation: str, source: str, described: str) -> dict:
    try:
        return _ask(operation, source)
    except Exception as error:  # noqa: BLE001 - the law is that none escapes
        raise AssertionError(
            f"WHAT: asking {operation!r} about {described} ended in "
            f"{type(error).__name__}: {error}. "
            "WHY: a source the profile does not define is an answer, not a "
            "crash: a caller reads one JSON response from every request. "
            "HOW: refuse the construct where it stands, naming it and the "
            f"profile it is outside of. Source:\n{source}"
        ) from error


@settings(max_examples=120, derandomize=True, deadline=None)
@given(
    described=st.sampled_from(sorted(OUT_OF_PROFILE)),
    operation=st.sampled_from(SOURCE_READING_OPERATIONS),
)
def test_every_out_of_profile_source_is_refused_the_same_way_by_every_operation(
    described, operation
):
    """LAW1: for any construct core-0 does not have and any operation
    that reads source, the answer is the unsupported status with that
    category alone, and it carries neither a claim nor a result."""
    source = OUT_OF_PROFILE[described].source
    response = _answer_for(operation, source, described)

    assert response.get("status") == UNSUPPORTED_STATUS, (
        f"WHAT: {operation!r} answered {response.get('status')!r} for "
        f"{described}. "
        "WHY: a source using what core-0 does not have is outside the profile, "
        "whichever operation was asked to read it. "
        f"HOW: inspect the answer: {response}"
    )
    assert {d.get("category") for d in response.get("diagnostics") or []} == {
        UNSUPPORTED_CATEGORY
    }, (
        f"WHAT: the refusal of {described} by {operation!r} is not reported as "
        f"{UNSUPPORTED_CATEGORY!r} alone: {response}. "
        "WHY: the tool stopped at the construct, so it has no other finding to "
        "report. "
        "HOW: answer the profile boundary and nothing else."
    )
    assert "result" not in response and "claim" not in response, (
        f"WHAT: {operation!r} refused {described} and still carried a claim or "
        f"a result: {response}. "
        "WHY: nothing was read past the construct, so nothing can be reported "
        "about the program. "
        "HOW: return the refusal alone."
    )


@settings(max_examples=60, derandomize=True, deadline=None)
@given(described=st.sampled_from(sorted(OUT_OF_PROFILE)))
def test_every_out_of_profile_refusal_names_its_construct_and_where_it_stands(
    described,
):
    """LAW2: each refusal says which construct is outside the profile and
    stands at the line the construct occupies, so a reader goes to it."""
    case = OUT_OF_PROFILE[described]
    response = _answer_for("check", case.source, described)
    diagnostic = (response.get("diagnostics") or [{}])[0]
    reason = diagnostic.get("reason", "")

    for word in (*case.naming, "core-0"):
        assert word in reason, (
            f"WHAT: the refusal of {described} does not say {word!r}: {reason!r}. "
            "WHY: a reader repairs the construct the refusal names. "
            "HOW: name the construct and the profile it is outside of."
        )
    location = diagnostic.get("location") or {}
    assert location.get("line") == case.line, (
        f"WHAT: {described} is refused at {location or 'nowhere'}, but the "
        f"construct stands on line {case.line}: {response}. "
        "WHY: a reader goes to the line to repair it. "
        "HOW: carry the place the reader already holds into the diagnostic."
    )
    assert isinstance(location.get("column"), int) and location["column"] >= 1, (
        f"WHAT: {described} is refused with no column: {response}. "
        "WHY: a line can hold several forms. "
        "HOW: carry the column the reader already holds."
    )


@settings(max_examples=60, derandomize=True, deadline=None)
@given(name=st.sampled_from(sorted(PRESERVED_CASES)))
def test_every_preserved_counterexample_is_refused_for_the_construct_it_uses(name):
    """LAW3: each of the fourteen preserved files is refused as outside
    the profile, naming the construct that stands in it, and the same
    case written with only what core-0 has is answered by the ordinary
    rules -- never as out of profile."""
    case = PRESERVED_CASES[name]
    response = _answer_for("check", case.source(name), name)

    assert response.get("status") == UNSUPPORTED_STATUS, (
        f"WHAT: the preserved counterexample {name!r} was answered "
        f"{response.get('status')!r}: {response}. "
        "WHY: every one of the fourteen uses something core-0 does not have, so "
        "under this profile each is refused at the boundary. "
        "HOW: refuse the construct the file uses, naming it."
    )
    reason = (response.get("diagnostics") or [{}])[0].get("reason", "")
    for word in case.naming:
        assert word in reason, (
            f"WHAT: the refusal of {name!r} does not say {word!r}: {reason!r}. "
            "WHY: the refusal must name the construct that is outside the "
            "profile, not merely report that something is. "
            "HOW: name the construct the file uses."
        )

    adapted = case.adaptation(name)
    answer = _answer_for("check", adapted, f"{name} written for core-0")
    assert answer.get("status") == case.adapted_status, (
        f"WHAT: {name!r} written with only what core-0 has was answered "
        f"{answer.get('status')!r}, not {case.adapted_status!r}: {answer}. "
        "WHY: the adaptation keeps the question the case asks, so the ordinary "
        "rules decide it. "
        f"HOW: inspect the adapted source:\n{adapted}"
    )
    assert UNSUPPORTED_CATEGORY not in [
        d.get("category") for d in answer.get("diagnostics") or []
    ], (
        f"WHAT: {name!r} written with only what core-0 has is still refused as "
        f"out of profile: {answer}. "
        "WHY: an answer given to every source proves nothing about the ones it "
        "is meant for. "
        "HOW: refuse only the constructs core-0 does not have."
    )


# Sources that core-0 already answers, with the answer each one has
# today: the two shipped programs, a program that breaks an in-profile
# rule, and a declaration word the reader cannot place.
UNCHANGED_SOURCES = {
    **{path: ("completed", set()) for path in SHIPPED_PROGRAMS},
    "a program naming something undeclared": (
        "invalid_program",
        {"unbound_name"},
    ),
    "a misspelled declaration word": ("invalid_program", {"syntax"}),
}


def _unchanged_source(described: str) -> str:
    if described in SHIPPED_PROGRAMS:
        return shipped_source(described)
    if described == "a misspelled declaration word":
        return MISSPELLED_DECLARATION_WORD
    return UNBOUND_NAME_IN_PROFILE


EVERY_SOURCE = sorted(UNCHANGED_SOURCES) + sorted(OUT_OF_PROFILE)


@settings(max_examples=80, derandomize=True, deadline=None)
@given(described=st.sampled_from(EVERY_SOURCE))
def test_the_new_answer_is_given_to_out_of_profile_sources_and_to_nothing_else(
    described,
):
    """LAW4: drawn from every source this feature knows -- the ones
    core-0 already answered and the ones it does not define -- a source
    gets the unsupported status exactly when it uses a construct core-0
    does not have. So a source core-0 already accepted is still
    accepted, and a mistake it already refused keeps the status and the
    categories its own rule owns."""
    out_of_profile = described in OUT_OF_PROFILE
    source = (
        OUT_OF_PROFILE[described].source
        if out_of_profile
        else _unchanged_source(described)
    )
    response = _answer_for("check", source, described)
    answered = {d.get("category") for d in response.get("diagnostics") or []}

    if out_of_profile:
        assert response.get("status") == UNSUPPORTED_STATUS, (
            f"WHAT: {described} is answered {response.get('status')!r}, not "
            f"{UNSUPPORTED_STATUS!r}: {response}. "
            "WHY: it uses a construct core-0 does not have. "
            "HOW: refuse it at the profile boundary."
        )
        return

    expected_status, expected_categories = UNCHANGED_SOURCES[described]
    assert response.get("status") == expected_status, (
        f"WHAT: {described} is now answered {response.get('status')!r}, not "
        f"{expected_status!r}: {response}. "
        "WHY: naming a boundary must not move it. "
        "HOW: refuse only the constructs core-0 does not have."
    )
    assert answered == expected_categories, (
        f"WHAT: {described} is now reported as {answered or 'nothing'}, not "
        f"{expected_categories or 'nothing'}: {response}. "
        "WHY: each rule owns the category it answers with. "
        "HOW: leave the other rules' answers alone."
    )
