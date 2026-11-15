"""R1.P1 -- law: whatever a client sends, the tool prints one JSON
answer and exits 0.

A client cannot tell a tool that broke from input that was wrong when
the tool answers a bad request by raising. The law covers every request
the corpus can build: fields holding the wrong kind of JSON value,
fields missing, requests that are not objects at all, texts nested far
past anything the tool reads, and the programs this repository ships cut
off and dented at every character and every token boundary.

still passes if: the tool answered every request with the same refusal.
The last test requires the untouched programs to be answered, and the
answer to say which operation it answers, so a single constant refusal
would not pass.
"""

from __future__ import annotations

import json

from hypothesis import HealthCheck, given, settings, strategies as st

from _r1_mangled_requests import (
    OPERATIONS,
    WRONG_KINDS,
    ask,
    corpus,
    nested,
    nested_program,
    shipped_programs,
)

# At least this many mangled requests must be sent for the run to be
# evidence of anything.
A_FUZZ_WORTH_THE_NAME = 500

DERANDOMIZED = settings(
    derandomize=True,
    max_examples=120,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow, HealthCheck.function_scoped_fixture],
)


def _assert_answered(answer, why: str) -> dict:
    assert answer.crash is None, (
        f"{why} came back as {type(answer.crash).__name__}: {answer.crash}. An "
        "exception is not an answer: the client reads nothing on standard "
        "output and cannot tell whether its request or the tool was at fault. "
        "Refuse the input in a published category instead."
    )
    assert answer.exit_code == 0, (
        f"{why} left the tool exiting {answer.exit_code}: a non-zero exit says "
        "the tool failed, not that the request was refused. Answer the request "
        "and exit 0."
    )
    try:
        parsed = json.loads(answer.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(
            f"{why} printed {answer.stdout[:400]!r}, which is not JSON: a client "
            "parses standard output and gets nothing to act on. Print one JSON "
            "answer per request."
        ) from None
    assert isinstance(parsed, dict) and "status" in parsed, (
        f"{why} printed an answer with no status: {parsed}. A client branches "
        "on the status; an answer without one cannot be acted on."
    )
    return parsed


def test_every_mangled_request_in_the_corpus_is_answered_and_exits_cleanly():
    """Given every mangled request the corpus builds, when each is sent
    to the tool, then each comes back as one JSON answer carrying a
    status and the tool exits 0.
    """
    cases = corpus()
    assert len(cases) >= A_FUZZ_WORTH_THE_NAME, (
        f"the corpus holds {len(cases)} requests, fewer than the "
        f"{A_FUZZ_WORTH_THE_NAME} a fuzz needs to say anything: a short corpus "
        "that passes has mostly not looked."
    )

    broken = []
    for why, request in cases:
        answer = ask(request)
        if answer.crash is not None or answer.exit_code != 0:
            broken.append((why, answer.crash, answer.exit_code))
            continue
        try:
            parsed = json.loads(answer.stdout)
        except (json.JSONDecodeError, ValueError):
            broken.append((why, "answer was not JSON", answer.exit_code))
            continue
        if not isinstance(parsed, dict) or "status" not in parsed:
            broken.append((why, f"answer carried no status: {parsed}", 0))

    assert not broken, (
        f"{len(broken)} of the {len(cases)} mangled requests were not answered. "
        f"The first ten: {broken[:10]}. Every one of them is a client that gets "
        "a traceback or a non-zero exit instead of a refusal it can read. "
        "Refuse each cause where the code reads the field or the text."
    )


@DERANDOMIZED
@given(
    operation=st.sampled_from(OPERATIONS),
    source_is_a_program=st.booleans(),
    source=st.sampled_from(WRONG_KINDS),
    function=st.sampled_from(WRONG_KINDS + ("step", "valid-state")),
    arguments=st.sampled_from(WRONG_KINDS + (["(Clock 1)", "(Tick)"],)),
    extra=st.sampled_from(WRONG_KINDS),
)
def test_no_generated_request_ever_comes_back_as_an_exception(
    operation, source_is_a_program, source, function, arguments, extra
):
    """LAW1: every request the tool can receive is answered with one
    JSON response carrying a status, and the tool exits 0.

    Half the draws carry a real program, so the fields the handlers read
    after the source are reached instead of being cut off by a source
    that holds no text.
    """
    request = {
        "operation": operation,
        "source": shipped_programs()["hour-clock"] if source_is_a_program else source,
        "function": function,
        "arguments": arguments,
        "prova": extra,
    }

    _assert_answered(ask(request), f"the request {str(request)[:200]!r}")


@DERANDOMIZED
@given(
    depth=st.integers(min_value=1, max_value=3000),
    shape=st.sampled_from(("bare text", "program", "argument")),
)
def test_no_generated_depth_ever_comes_back_as_an_exception(depth, shape):
    """LAW1 over nesting: a text nested to any depth is answered, not
    followed until the interpreter runs out of stack.
    """
    clock = shipped_programs()["hour-clock"]
    if shape == "bare text":
        request = {"operation": "check", "source": nested(depth)}
    elif shape == "program":
        request = {"operation": "examples", "source": nested_program(max(depth, 5))}
    else:
        request = {
            "operation": "evaluate",
            "source": clock,
            "function": "valid-state",
            "arguments": ["(" * depth + "Clock" + ")" * depth],
        }

    _assert_answered(ask(request), f"a {shape} nested {depth} deep")


def test_the_untouched_programs_are_still_answered_about_themselves():
    """Given each program this repository ships, when the tool is asked
    to check it, then the answer says it completed and says which
    operation it answers, so a tool refusing everything with one
    constant answer would not pass the law above.
    """
    for name, text in shipped_programs().items():
        answer = ask({"operation": "check", "source": text})
        parsed = _assert_answered(answer, f"{name}, untouched")

        assert parsed["status"] == "completed", (
            f"{name} was answered {parsed['status']!r}: {parsed}. This program "
            "is shipped as a correct one; a tool that refuses it has made a "
            "rule about correct programs."
        )
        assert parsed.get("operation") == "check", (
            f"the answer for {name} says it answers "
            f"{parsed.get('operation')!r}: {parsed}. Each answer says which "
            "request it is the answer to."
        )
