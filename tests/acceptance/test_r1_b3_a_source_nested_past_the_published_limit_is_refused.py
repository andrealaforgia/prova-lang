"""R1.B3 -- a source nested deeper than the tool reads is refused at the
form that went too deep, and the limit is published so a caller never
has to meet it to learn it.

A generator that writes an expression inside an expression without
counting used to drive the tool past the depth it can follow, and the
tool ended in a traceback with nothing on standard output. The tool now
declares how deep it reads, refuses the first form past that depth, and
says where it stands.

still passes if: the tool refused every program, or published a limit so
small that no real program fits under it. Two tests below send a program
nested exactly at the published limit and the programs this repository
ships, and require them to be answered as they are today.
"""

from __future__ import annotations

from _r1_robustness_fixtures import (
    ACTUAL,
    EXPECTED,
    NESTING_LIMIT_EXCEEDED,
    NESTING_LIMIT_NAME,
    RESOURCE_EXHAUSTED,
    SYMBOL,
    answered,
    assert_accepted,
    assert_located,
    deepest_nesting,
    discover,
    hour_clock_source,
    program_nested,
    published_nesting_limit,
    shipped_programs,
    the_refusal,
)

# How much room a caller needs above the deepest program this repository
# ships before the limit starts to be a rule about correct programs
# rather than a budget.
ROOM_OVER_WHAT_IS_SHIPPED = 4


def _check(source: str, why: str) -> dict:
    return answered({"prova": "i1", "operation": "check", "source": source}, why)


def _limit() -> int:
    return published_nesting_limit(discover())


def test_the_manifest_says_how_deeply_the_tool_reads():
    """Given a caller reading the manifest before it writes a program,
    when it looks for the limits the tool enforces, then it finds the
    greatest nesting the tool reads, the status an answer carries when
    that is exceeded and the category of the refusal.
    """
    manifest = discover()
    published_nesting_limit(manifest)
    declared = manifest["result"]["resource_limits"]["limits"][NESTING_LIMIT_NAME]

    assert declared["status"] == RESOURCE_EXHAUSTED, (
        f"the manifest says a source past the nesting limit is answered "
        f"{declared.get('status')!r}: {declared}. A caller reads the status it "
        "will meet from the manifest; one that is not the status the tool "
        "answers with sends it to handle the wrong case."
    )
    assert declared["category"] == NESTING_LIMIT_EXCEEDED, (
        f"the manifest says the refusal carries {declared.get('category')!r}: "
        f"{declared}. The category a caller matches on is read from here."
    )
    assert declared.get("reason"), (
        f"the manifest publishes the nesting limit with no reason for its "
        f"value: {declared}. A caller that must change its generator is owed "
        "the reason the number is what it is."
    )


def test_a_source_nested_one_form_past_the_limit_is_refused_where_it_went_too_deep():
    """Given a program whose body nests one form deeper than the
    published limit, when a caller checks it, then the answer says the
    tool ran out of what it allows, names the nesting limit, reports the
    limit beside the depth reached, and says where the form that went
    too deep stands.
    """
    limit = _limit()
    source = program_nested(limit + 1)
    assert deepest_nesting(source) == limit + 1, (
        f"the program built for this test nests {deepest_nesting(source)} deep, "
        f"not {limit + 1}: the test would observe the wrong boundary."
    )

    response = _check(source, "a program nested one form past the limit")

    why = f"a program nested {limit + 1} forms deep against a limit of {limit}"
    assert response.get("status") == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: {response}. "
        "The program breaks no rule of core-0; it exceeds a budget this tool "
        "declares, and saying it is an invalid program would turn that budget "
        "into a rule about what programs may mean."
    )
    refusal = the_refusal(response, NESTING_LIMIT_EXCEEDED, why)
    assert refusal.get(SYMBOL) == NESTING_LIMIT_NAME, (
        f"the refusal for {why} names {refusal.get(SYMBOL)!r}: {refusal}. It "
        f"names {NESTING_LIMIT_NAME!r}, the same name the manifest publishes "
        "the number under, so a caller meeting the refusal can look the limit up."
    )
    assert refusal.get(EXPECTED) == limit, (
        f"the refusal for {why} says {refusal.get(EXPECTED)!r} was allowed, but "
        f"the manifest publishes {limit}: {refusal}. One number, in one place; "
        "two disagreeing numbers leave a caller unable to pick a depth."
    )
    assert refusal.get(ACTUAL) == limit + 1, (
        f"the refusal for {why} says the source reached "
        f"{refusal.get(ACTUAL)!r}, expected {limit + 1}: {refusal}. A caller "
        "reads how far past the limit it went from this number."
    )
    assert str(limit) in refusal.get("reason", ""), (
        f"the refusal for {why} does not say the limit in its sentence: "
        f"{refusal.get('reason')!r}. A person reading the message is told the "
        "number to stay under without opening the manifest."
    )
    assert_located(refusal, why)
    assert "result" not in response, (
        f"the answer for {why} carries a result: {response}. The tool stopped "
        "reading the text, so there is nothing it checked."
    )


def test_a_source_nested_exactly_at_the_limit_is_answered_as_before():
    """Given a program whose body nests exactly as deep as the published
    limit allows, when a caller checks it, then it is accepted, so the
    limit refuses only what is past it.
    """
    limit = _limit()
    source = program_nested(limit)

    response = _check(source, "a program nested exactly at the limit")

    assert_accepted(response, "a program nested exactly at the published limit")


def test_the_limit_leaves_room_for_the_programs_this_repository_ships():
    """Given the programs this repository ships, when their nesting is
    compared with the published limit, then every one of them stands
    well under it and is still answered.
    """
    limit = _limit()
    shipped = shipped_programs()
    deepest = {name: deepest_nesting(text) for name, text in shipped.items()}
    worst = max(deepest.values())

    assert limit >= worst * ROOM_OVER_WHAT_IS_SHIPPED, (
        f"the published nesting limit is {limit} and the deepest program this "
        f"repository ships nests {worst}: {deepest}. A limit that close to real "
        "programs is no longer a budget against a runaway generator; it is a "
        f"rule about how people may write. Publish at least "
        f"{worst * ROOM_OVER_WHAT_IS_SHIPPED}."
    )
    for name, text in shipped.items():
        assert_accepted(_check(text, name), name)


def test_an_argument_nested_past_the_limit_is_refused_the_same_way():
    """Given an evaluate request whose argument text nests past the
    published limit, when the tool answers it, then it is refused for
    the nesting, not crashed: the limit holds for every text the tool
    reads, not only for a program.
    """
    limit = _limit()
    argument = "(" * (limit + 1) + "Clock" + ")" * (limit + 1)

    response = answered(
        {
            "prova": "i1",
            "operation": "evaluate",
            "source": hour_clock_source(),
            "function": "valid-state",
            "arguments": [argument],
        },
        "an argument nested past the limit",
    )

    why = "an argument nested one form past the limit"
    refusal = the_refusal(response, NESTING_LIMIT_EXCEEDED, why)
    assert refusal.get(EXPECTED) == limit, (
        f"the refusal for {why} says {refusal.get(EXPECTED)!r} was allowed "
        f"against a published {limit}: {refusal}. The text in a request and the "
        "text of a program are read by the same reader, so one limit covers both."
    )
    assert refusal.get("points_into") == "argument", (
        f"the refusal for {why} says its place stands in "
        f"{refusal.get('points_into')!r}: {refusal}. A caller is told which "
        "text to open, and this place is in the argument it sent, not in the "
        "program."
    )
    assert_located(refusal, why)
