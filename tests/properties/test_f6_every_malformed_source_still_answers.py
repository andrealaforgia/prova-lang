"""Property tests for F6's totality law and for one answer per source.

LAW4 -- every source, however truncated or mangled, gets one answer from
every operation that reads source: a refusal with a place, never a
traceback and never a half-built result.

LAW5 -- the source that declares nothing gets the identical refusal from
every operation that reads source, because one rule decides it at the
boundary they share.

The malformed family below is a closed, enumerated set of the shapes a
reader can write: every grammar position core-0 fixes, left empty or
filled with the wrong kind of form. A closed set is walked, not sampled.

Exercises the service's public operation contract in process, as the
other property tests here do.
"""

from __future__ import annotations

from prova import service

SOURCE_READING_OPERATIONS = ("check", "examples", "verify", "evaluate")
SYNTAX_CATEGORY = "syntax"


def _body(expression: str) -> str:
    return (
        "(defn f\n"
        "  (sig () -> Int ! pure)\n"
        "  (examples (example (f) => 1))\n"
        f"  {expression})\n"
    )


def _signature(signature: str) -> str:
    return (
        "(defn f\n"
        f"  {signature}\n"
        "  (examples (example (f) => 1))\n"
        "  1)\n"
    )


# Every shape below leaves one grammar position core-0 fixes either empty
# or filled with the wrong kind of form.
MALFORMED_SOURCES = {
    "a bare defn": "(defn)",
    "a defn with only a name": "(defn f)",
    "a defn whose signature is a symbol": "(defn f sig (examples (example (f) => 1)) 1)",
    "a signature with nothing after sig": _signature("(sig)"),
    "a signature with no parameter list": _signature("(sig -> Int ! pure)"),
    "a signature carrying a form after its effect": _signature("(sig () -> Int ! pure extra)"),
    "a parameter with no type": _signature("(sig ((n)) -> Int ! pure)"),
    "a parameter list written as one symbol": _signature("(sig (n) -> Int ! pure)"),
    "a parameter with nothing in it": _signature("(sig (()) -> Int ! pure)"),
    "a parameter whose type is a form": _signature("(sig ((n (Int))) -> Int ! pure)"),
    "a bare deftype": "(deftype)",
    "a deftype with only a name": "(deftype T)",
    "a deftype with an empty body": "(deftype T ())",
    "a deftype whose body is a symbol": "(deftype T record)",
    "a record field with no type": "(deftype T (record (x)))",
    "a record field with nothing in it": "(deftype T (record ()))",
    "a union with an empty variant": "(deftype T (union ()))",
    "a variant field with no type": "(deftype T (union (Mk (x))))",
    "a bare if": _body("(if)"),
    "an if with no else-branch": _body("(if true 1)"),
    "a bare let": _body("(let)"),
    "a let whose bindings are a symbol": _body("(let x 1)"),
    "a let binding with no value": _body("(let ((x)) x)"),
    "a let binding naming a form": _body("(let (((a b) 2)) 1)"),
    "a bare match": _body("(match)"),
    "a match with no clause": _body("(match 1)"),
    "a match clause with only a pattern": _body("(match 1 ((x)))"),
    "a bare selector": _body("(.hr)"),
}


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
            "WHY: a source the tool cannot read is an answer, not a crash: a "
            "caller reads one JSON response from every request. "
            "HOW: refuse the form where it stands, with a reason that says what "
            f"is missing and how to write it. Source:\n{source}"
        ) from error


def test_every_malformed_source_is_refused_by_every_operation_that_reads_source():
    """LAW4: for each of the enumerated malformed sources, each of the four
    operations that read source answers one refusal, in the published
    syntax category, carrying no result."""
    for described, source in MALFORMED_SOURCES.items():
        for operation in SOURCE_READING_OPERATIONS:
            response = _answer_for(operation, source, described)

            assert response.get("status") == "invalid_program", (
                f"WHAT: {operation!r} answered {response.get('status')!r} for "
                f"{described}. "
                "WHY: a source core-0 does not define is an invalid program. "
                f"HOW: inspect the answer: {response}"
            )
            assert {d.get("category") for d in response.get("diagnostics") or []} == {
                SYNTAX_CATEGORY
            }, (
                f"WHAT: the refusal of {described} by {operation!r} is not reported "
                f"as {SYNTAX_CATEGORY!r} alone: {response}. "
                "WHY: a source the reader cannot read carries that category and no "
                "other. "
                "HOW: report the reader's refusal unchanged."
            )
            assert "result" not in response, (
                f"WHAT: {operation!r} refused {described} and still carried a "
                f"result: {response}. "
                "WHY: nothing was read, so nothing can be reported about it. "
                "HOW: return the refusal alone."
            )


def test_every_malformed_source_says_where_it_went_wrong():
    """LAW4, the part a reader uses: each refusal is placed at a line of
    the source, so a reader is sent to the form to repair."""
    placed = 0
    for described, source in MALFORMED_SOURCES.items():
        response = _answer_for("check", source, described)
        location = (response["diagnostics"][0].get("location") or {}).get("line")
        assert location is not None and 1 <= location <= len(source.splitlines()) + 1, (
            f"WHAT: the refusal of {described} is placed at {location!r}, which is "
            f"no line of a source of {len(source.splitlines())} line(s): {response}. "
            "WHY: a reader repairs a form by going to the line it stands on. "
            "HOW: carry the place the reader already holds into the diagnostic."
        )
        placed += 1
    assert placed == len(MALFORMED_SOURCES), (
        f"{placed} of the {len(MALFORMED_SOURCES)} malformed sources were placed."
    )


def test_the_source_that_declares_nothing_gets_one_refusal_everywhere():
    """LAW5: the empty source is refused identically by check, examples,
    verify and evaluate, because one rule at the boundary they share
    decides it."""
    answers = {
        operation: _answer_for(operation, "", "the empty source")
        for operation in SOURCE_READING_OPERATIONS
    }
    diagnostics = {
        operation: answer.get("diagnostics")
        for operation, answer in answers.items()
    }
    expected = diagnostics["check"]

    assert expected and expected[0].get("category") == SYNTAX_CATEGORY, answers["check"]
    assert all(carried == expected for carried in diagnostics.values()), (
        f"WHAT: the four operations that read source answer the empty source "
        f"differently: {diagnostics}. "
        "WHY: one rule decides it at the boundary they share, so a caller that "
        "moves between operations must not meet two answers. "
        "HOW: build the refusal in the one place every operation that reads source "
        "calls."
    )
    assert all(
        answer.get("status") == "invalid_program" for answer in answers.values()
    ), answers
