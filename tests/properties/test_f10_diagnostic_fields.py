"""Property tests for F10's laws about what a diagnostic carries.

LAW1 -- every diagnostic a source-reading operation answers with carries
the revision of the exact source the request submitted, and that
revision is the SHA-256 of its bytes. A client reads which text the
answer is about from the answer alone.

LAW2 -- every diagnostic carries exactly the fields the manifest
publishes for its category: nothing undeclared, nothing missing. The
prose is the only part that is free.

LAW3 -- a diagnostic of a category the manifest declares always placed
carries a place, and every place carried stands in the text: never line
0 and never a column before the first one.

The sources are the shipped hour-clock program mutated at a drawn
position -- a character deleted, a character inserted, the text cut
short -- crossed with the four operations that read source, so the laws
are walked over refusals of every kind the tool can produce, from a
reader refusal to a rule of the checker.

Exercises the service's public operation contract in process, as the
other property tests here do. The revision is computed here from the
submitted text, the way a client computes it; nothing about the shape of
a diagnostic is imported.
"""

from __future__ import annotations

import hashlib
import pathlib

from hypothesis import example, given, settings
from hypothesis import strategies as st

from prova import service

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BASE = (REPO_ROOT / "examples" / "hour-clock.prova").read_text(encoding="utf-8")

SOURCE_READING_OPERATIONS = ("check", "examples", "verify", "evaluate")
PROSE_AND_CATEGORY = {"category", "reason"}



def schemas() -> dict:
    """What the manifest publishes about the shape of each diagnostic
    category, read from the tool at the moment of the check."""
    manifest = service.handle({"operation": "discover"})["result"]
    published = manifest.get("diagnostic_schemas")
    assert isinstance(published, dict), (
        "the manifest publishes no diagnostic schemas, so a client cannot read "
        f"the shape of a refusal from the tool: {sorted(manifest)}"
    )
    return published


def _revision(source: str) -> str:
    return hashlib.sha256(source.encode("utf-8")).hexdigest()


def _answers(source: str) -> dict:
    """The answer of every operation that reads source, for one text."""
    answers = {}
    for operation in SOURCE_READING_OPERATIONS:
        request = {"operation": operation, "source": source}
        if operation == "evaluate":
            request.update({"function": "step", "arguments": ["(Clock 1)", "(Tick)"]})
        answers[operation] = service.handle(request)
    return answers


def _diagnostics(response: dict) -> list:
    return list(response.get("diagnostics") or [])


mutations = st.one_of(
    st.integers(min_value=0, max_value=len(BASE) - 1).map(lambda i: BASE[:i] + BASE[i + 1 :]),
    st.tuples(
        st.integers(min_value=0, max_value=len(BASE) - 1),
        st.sampled_from("()[]\"'#|,:;. "),
    ).map(lambda pair: BASE[: pair[0]] + pair[1] + BASE[pair[0] :]),
    st.integers(min_value=1, max_value=len(BASE)).map(lambda i: BASE[:i]),
)


@settings(max_examples=60, deadline=None)
@given(source=mutations)
@example(source=BASE)
@example(source="")
@example(source="(")
def test_law1_every_diagnostic_says_which_text_it_is_about(source: str):
    revision = _revision(source)
    for operation, response in _answers(source).items():
        for entry in _diagnostics(response):
            schema = schemas()[entry["category"]]
            if schema["source_revision"] == "never":
                assert "source_revision" not in entry, (
                    f"{entry['category']!r} is published as carrying no revision "
                    f"but carries one: {entry}"
                )
                continue
            assert entry.get("source_revision") == revision, (
                f"the {operation} answer for a mutated source carries "
                f"{entry.get('source_revision')!r} instead of the revision of "
                f"the submitted text {revision!r}: {entry}. A client decides "
                "which version the answer is about from this field."
            )


@settings(max_examples=60, deadline=None)
@given(source=mutations)
@example(source=BASE)
@example(source="")
@example(source="(deftype Loop (record (next Loop)))\n")
def test_law2_every_diagnostic_carries_the_fields_its_category_publishes(source: str):
    for operation, response in _answers(source).items():
        for entry in _diagnostics(response):
            category = entry["category"]
            assert category in schemas(), (
                f"the {operation} answer uses the category {category!r}, which "
                f"the manifest does not publish: {entry}"
            )
            schema = schemas()[category]
            named = set(schema["fields"])
            if schema["source_revision"] == "always":
                named.add("source_revision")
            if schema["location"] is not None:
                named.add("location")
            carried = set(entry) - PROSE_AND_CATEGORY
            assert carried == named, (
                f"the {operation} answer carries {sorted(carried)} for "
                f"{category!r}, which publishes {sorted(named)}: {entry}. A "
                "client reads the shape of a refusal from the manifest."
            )


@settings(max_examples=60, deadline=None)
@given(source=mutations)
@example(source=BASE)
@example(source="")
@example(source=")")
def test_law3_a_placed_diagnostic_stands_somewhere_in_the_text(source: str):
    for operation, response in _answers(source).items():
        for entry in _diagnostics(response):
            place = entry.get("location")
            published = schemas()[entry["category"]]["location"]
            if published is not None and published["present"] == "always":
                assert place is not None, (
                    f"{entry['category']!r} is published as always placed but "
                    f"the {operation} answer carries no place: {entry}"
                )
            if place is None:
                continue
            assert place["line"] >= 1 and place["column"] >= 1, (
                f"the {operation} answer is placed at {place}, which is not a "
                f"place in any text: {entry}. Line and column are counted from "
                "1, so 0 means the place was never found."
            )


def test_the_laws_are_capable_of_failing():
    """Positive control: the three laws above hold of the tool's own
    answers, and the same checks reject a diagnostic built without the
    fields they require."""
    forged = {"category": "type_mismatch", "reason": "something went wrong"}
    schema = schemas()["type_mismatch"]
    named = set(schema["fields"]) | {"source_revision", "location"}
    assert set(forged) - PROSE_AND_CATEGORY != named, (
        "a diagnostic carrying nothing but prose would satisfy LAW2, so LAW2 "
        "proves nothing"
    )
    assert _diagnostics(service.handle({"operation": "check", "source": "("})), (
        "the control source is accepted, so the laws above are walked over no "
        "diagnostic at all"
    )
