"""R1.B4 -- a program this tool cannot run to the end is refused with
the depth it reached, instead of ending in a traceback.

A chain of functions, each calling the next, breaks no rule of core-0:
the one thing that would make such a chain endless, a cycle, is already
refused. The tool simply runs out of its own room part way down. It used
to do that by raising, so a caller asking for the examples of a long but
perfectly legal program got nothing on standard output and an exit code
saying the tool had broken.

still passes if: the tool refused every program. Two tests below send a
chain exactly as long as the published limit allows, and the programs
this repository ships, and require them to be run.
"""

from __future__ import annotations

from _r1_robustness_fixtures import (
    ACTUAL,
    EVALUATION_DEPTH_EXCEEDED,
    EVALUATION_LIMIT_NAME,
    EXPECTED,
    RESOURCE_EXHAUSTED,
    SYMBOL,
    answered,
    assert_accepted,
    assert_located,
    chained_functions,
    discover,
    hour_clock_source,
    published_evaluation_limit,
    the_refusal,
)

# The length the review found: long enough to run out of room, short
# enough that a generator emits it without trying.
A_CHAIN_THAT_USED_TO_CRASH = 600


def _run(operation: str, source: str, why: str, **fields) -> dict:
    request = {"prova": "i1", "operation": operation, "source": source}
    request.update(fields)
    return answered(request, why)


def _limit() -> int:
    return published_evaluation_limit(discover())


def test_the_manifest_says_how_far_the_tool_runs_a_program():
    """Given a caller reading the manifest before it generates a
    program, when it looks at the limits, then it finds how many
    evaluation steps may stand inside one another, with the status and
    the category an exceeded limit carries.
    """
    declared = discover()["result"]["resource_limits"]["limits"][EVALUATION_LIMIT_NAME]

    assert declared["status"] == RESOURCE_EXHAUSTED, (
        f"the manifest says a program too deep to run is answered "
        f"{declared.get('status')!r}: {declared}. A caller reads the status it "
        "will meet from here."
    )
    assert declared["category"] == EVALUATION_DEPTH_EXCEEDED, (
        f"the manifest says the refusal carries {declared.get('category')!r}: "
        f"{declared}. The category a caller matches on is read from here."
    )
    assert declared.get("reason"), (
        f"the manifest publishes the limit with no reason for its value: "
        f"{declared}. A caller that must shorten its chain is owed the reason "
        "the number is what it is."
    )


def test_a_chain_of_six_hundred_functions_is_refused_rather_than_crashing():
    """Given a legal program of 600 functions where each one calls the
    next, when a caller asks for its examples, then the answer says the
    tool ran out of what it allows and says where, rather than ending in
    a traceback.
    """
    source = chained_functions(A_CHAIN_THAT_USED_TO_CRASH)

    response = _run("examples", source, "a chain of 600 functions")

    why = f"a chain of {A_CHAIN_THAT_USED_TO_CRASH} functions"
    assert response.get("status") == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: "
        f"{str(response)[:400]}. The program breaks no rule of core-0; it "
        "passes a budget this tool declares, and calling it an invalid "
        "program would make the budget a rule about what may be written."
    )
    refusal = the_refusal(response, EVALUATION_DEPTH_EXCEEDED, why)
    assert refusal.get(SYMBOL) == EVALUATION_LIMIT_NAME, (
        f"the refusal for {why} names {refusal.get(SYMBOL)!r}: {refusal}. It "
        "names the limit the manifest publishes the number under, so a caller "
        "meeting it can look the number up."
    )
    assert refusal.get(EXPECTED) == _limit(), (
        f"the refusal for {why} says {refusal.get(EXPECTED)!r} steps were "
        f"allowed while the manifest publishes {_limit()}: {refusal}. One "
        "number, in one place."
    )
    assert_located(refusal, why)


def test_the_same_program_is_refused_the_same_way_when_a_function_is_called():
    """Given the same chain, when a caller asks the tool to evaluate its
    first function rather than run its examples, then it is refused the
    same way: the limit belongs to running a program, not to one
    operation.
    """
    source = chained_functions(A_CHAIN_THAT_USED_TO_CRASH)

    response = _run(
        "evaluate",
        source,
        "evaluating the head of a chain of 600 functions",
        function="f0",
        arguments=[],
    )

    why = "evaluating the head of a chain of 600 functions"
    assert response.get("status") == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: "
        f"{str(response)[:400]}."
    )
    the_refusal(response, EVALUATION_DEPTH_EXCEEDED, why)


def test_a_chain_exactly_as_long_as_the_limit_allows_is_still_run():
    """Given a chain of exactly as many functions as the published limit
    allows, when a caller asks for its examples, then every example runs
    and reports 1, so the number published is a depth a caller may
    really use.
    """
    limit = _limit()
    source = chained_functions(limit)

    response = _run("examples", source, "a chain exactly at the limit")

    assert_accepted(response, f"a chain of {limit} functions, exactly at the limit")
    entries = response["result"]["examples"]
    failed = [entry for entry in entries if not entry.get("passed")]
    assert len(entries) == limit and not failed, (
        f"{len(failed)} of the {len(entries)} examples of a chain of {limit} "
        f"functions did not pass, expecting {limit} entries and none failing. "
        "A limit a caller cannot reach is a limit published too high."
    )


def test_a_chain_one_function_longer_than_the_limit_is_refused():
    """Given a chain one function longer than the published limit, when
    a caller asks for its examples, then it is refused, so the boundary
    stands exactly where the manifest says it does.
    """
    limit = _limit()

    response = _run(
        "examples", chained_functions(limit + 1), "a chain one past the limit"
    )

    why = f"a chain of {limit + 1} functions against a limit of {limit}"
    assert response.get("status") == RESOURCE_EXHAUSTED, (
        f"the tool answered {response.get('status')!r} for {why}: "
        f"{str(response)[:400]}. One function more than the number published "
        "is one function too many; anything else means the published number "
        "is not the one being kept."
    )
    refusal = the_refusal(response, EVALUATION_DEPTH_EXCEEDED, why)
    assert refusal.get(ACTUAL) == limit + 1, (
        f"the refusal for {why} says the run reached {refusal.get(ACTUAL)!r} "
        f"steps, expected {limit + 1}: {refusal}. The tool stops at the first "
        "step past the limit."
    )


# A chain long enough that running it is far past the limit on how deep a
# run may go, and whose settled inventory a caller can still be given
# whole: 240 functions answer in about half a megabyte, where 600 answer
# in about 1.3 and are withheld by the budget on the size of an answer.
# Reading the chain is unaffected either way, which is what `check`
# below shows over the longer one.
A_CHAIN_WHOSE_ANSWER_FITS = 240


def test_a_long_chain_is_still_checked_and_its_obligations_still_listed():
    """Given the chain of 600 functions, when a caller checks it, then it
    is accepted: the limit is on running a program, and reading one is
    not running it. And given a chain of 240, when a caller asks what it
    owes, then that is answered too.

    Asking what a program owes now settles each obligation and says what
    became of it, so the answer carries more per entry than the list
    alone did. A chain of 600 functions owes about 3000 obligations and
    its answer passes the megabyte a caller may be given, which the
    budget on the size of an answer withholds whole. That is a limit on
    the size of an answer and not on how deep a run may go, which is
    what this test is about: the shorter chain is just as far past the
    depth limit and is answered.
    """
    assert_accepted(
        _run(
            "check",
            chained_functions(A_CHAIN_THAT_USED_TO_CRASH),
            "check over a chain of 600 functions",
        ),
        "a chain of 600 functions sent to check",
    )
    assert_accepted(
        _run(
            "verify",
            chained_functions(A_CHAIN_WHOSE_ANSWER_FITS),
            "verify over a chain of 240 functions",
        ),
        f"a chain of {A_CHAIN_WHOSE_ANSWER_FITS} functions sent to verify",
    )


def test_the_shipped_hour_clock_is_still_run():
    """Given the hour clock this repository ships, when a caller asks
    for its examples, then every one of them still passes: a budget on
    how deep a run may go is not a rule about ordinary programs.
    """
    response = _run("examples", hour_clock_source(), "the shipped hour clock")

    assert_accepted(response, "the hour clock this repository ships")
    failed = [e for e in response["result"]["examples"] if not e.get("passed")]
    assert not failed, (
        f"{len(failed)} example(s) of the shipped hour clock did not pass: "
        f"{failed}."
    )
