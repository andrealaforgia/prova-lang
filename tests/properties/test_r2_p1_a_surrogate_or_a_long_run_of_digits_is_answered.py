"""R2.P1 -- the crash search of R1, widened by the two families that
still ended in a traceback: a character that cannot be written as UTF-8
anywhere in a text the request carries, and a run of digits longer than
an integer literal this tool reads.

Both families are sent through the same surface R1's fuzz uses: the
command's own entry point, with standard input and standard output
replaced, so the exit code and the printed text are the ones a caller
would see. The corpus is fixed -- the same requests every run -- and the
generated laws are derandomised, so a crash found once is caught again.

still passes if: the tool answered every request with one constant
refusal. The last test sends the programs this repository ships and the
longest literal the tool does read, and requires both to be answered as
before, so a tool that refused everything would not pass.
"""

from __future__ import annotations

import json

from hypothesis import HealthCheck, given, settings, strategies as st

from _r1_mangled_requests import ask, ask_text, shipped_programs

# The longest run of digits this tool reads as one integer literal, and
# the words its refusal uses to say so.
DIGIT_LIMIT = 1000
NAMES_THE_LIMIT = f"at most {DIGIT_LIMIT} digits"

# Half a character: a low surrogate and a high surrogate, each standing
# alone, as a client that decoded bytes badly would send them.
LONE_SURROGATES = ("\udccc", "\ud800")

# At least this many mangled requests must be sent for the run to be
# evidence of anything, the number R1's own fuzz holds itself to.
A_FUZZ_WORTH_THE_NAME = 500

SOURCE_READING_OPERATIONS = ("check", "examples", "verify", "parse", "evaluate")

# Derandomised and small: every draw sends a whole request through the
# command, so the laws are worth more cases than they are worth seconds.
DERANDOMIZED = settings(
    derandomize=True,
    max_examples=60,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


def _clock() -> str:
    return shipped_programs()["hour-clock"]


def _answered(request: object, why: str) -> dict:
    """The one JSON answer `request` gets, or the reason it is not one."""
    answer = ask(request)
    assert answer.crash is None, (
        f"{why} came back as {type(answer.crash).__name__}: {answer.crash}. An "
        "exception is not an answer: the client reads nothing on standard "
        "output and cannot tell whether its request or the tool was at fault."
    )
    assert answer.exit_code == 0, (
        f"{why} left the tool exiting {answer.exit_code}: a non-zero exit says "
        "the tool failed, not that the request was refused."
    )
    try:
        parsed = json.loads(answer.stdout)
    except (json.JSONDecodeError, ValueError):
        raise AssertionError(
            f"{why} printed {answer.stdout[:300]!r}, which is not JSON a "
            "client can act on."
        ) from None
    assert isinstance(parsed, dict) and "status" in parsed, (
        f"{why} printed an answer with no status: {parsed}."
    )
    return parsed


def _names_the_limit(response: dict) -> bool:
    return any(
        NAMES_THE_LIMIT in (entry.get("reason") or "")
        for entry in (response.get("diagnostics") or [])
    )


# --- the two families, as fixed requests ----------------------------------

def _with_a_surrogate_at(text: str, position: int, half: str) -> str:
    place = position % (len(text) + 1)
    return text[:place] + half + text[place:]


def _surrogate_family() -> list[tuple[str, object]]:
    """A lone surrogate put at twenty places in every string a request
    carries, for both halves of a pair and for two operations."""
    clock = _clock()
    places = [round(index * len(clock) / 19) for index in range(20)]
    cases: list[tuple[str, object]] = []
    for half in LONE_SURROGATES:
        for position in places:
            dented = _with_a_surrogate_at(clock, position, half)
            for operation in ("check", "evaluate"):
                cases.append(
                    (f"{operation} with a surrogate at {position} of the source",
                     {"operation": operation, "source": dented,
                      "function": "step", "arguments": ["(Clock 1)"]})
                )
                cases.append(
                    (f"{operation} with a surrogate at {position} of the function",
                     {"operation": operation, "source": clock,
                      "function": _with_a_surrogate_at("step", position, half),
                      "arguments": ["(Clock 1)", "(Tick)"]})
                )
                cases.append(
                    (f"{operation} with a surrogate at {position} of an argument",
                     {"operation": operation, "source": clock, "function": "step",
                      "arguments": ["(Clock 1)",
                                    _with_a_surrogate_at("(Tick)", position, half)]})
                )
                cases.append(
                    (f"{operation} with a surrogate at {position} of the operation",
                     {"operation": _with_a_surrogate_at(operation, position, half),
                      "source": clock})
                )
                cases.append(
                    (f"{operation} with a surrogate at {position} of a field it "
                     "does not read",
                     {"operation": operation, "source": clock, "function": "step",
                      "arguments": ["(Clock 1)", "(Tick)"],
                      "prova": _with_a_surrogate_at("i1", position, half)})
                )
    return cases


# Lengths around every limit in sight: this tool's own, the
# interpreter's 4300, and the lengths a program is really written with.
DIGIT_RUNS = (1, 19, 20, 999, 1000, 1001, 2000, 4299, 4300, 4301, 9000)


def _body_literal(literal: str) -> str:
    return (
        "(defn big\n  (sig () -> Int ! pure)\n"
        "  (examples (example (big) => 1))\n"
        f"  {literal})\n"
    )


def _example_literal(literal: str) -> str:
    return (
        "(defn big\n  (sig () -> Int ! pure)\n"
        f"  (examples (example (big) => {literal}))\n"
        "  1)\n"
    )


def _pattern_literal(literal: str) -> str:
    return (
        "(defn big\n  (sig ((n Int)) -> Int ! pure)\n"
        "  (examples (example (big 1) => 1))\n"
        f"  (match n ({literal} 1) (_ 0)))\n"
    )


def _digit_family() -> list[tuple[str, object]]:
    """A run of digits in every integer position a request has: the
    body, an example, a pattern, a bare source and an argument."""
    cases: list[tuple[str, object]] = []
    for length in DIGIT_RUNS:
        literal = "9" * length
        for shape, source in (
            ("the body", _body_literal(literal)),
            ("an example", _example_literal(literal)),
            ("a pattern", _pattern_literal(literal)),
            ("a bare source", literal),
        ):
            for operation in ("check", "examples", "parse"):
                cases.append(
                    (f"{operation} with {length} digits in {shape}",
                     {"operation": operation, "source": source})
                )
        cases.append(
            (f"an argument written as {length} digits",
             {"operation": "evaluate", "source": _clock(),
              "function": "valid-state", "arguments": [literal]})
        )
    return cases


def _json_number_family() -> list[tuple[str, str]]:
    """A run of digits written as a number of the request itself, in
    every place the request writes one.

    Sent as text rather than as an object, because a client library
    that wrote the object would meet the same limit before the command
    ever did.
    """
    texts: list[tuple[str, str]] = []
    for length in DIGIT_RUNS:
        number = "9" * length
        texts.extend(
            [
                (f"a field of the request written as {length} digits",
                 '{"operation":"check","source":"x","n":' + number + "}"),
                (f"an operation written as {length} digits",
                 '{"operation":' + number + "}"),
                (f"an argument written as the number {length} digits long",
                 '{"operation":"evaluate","source":"x","arguments":['
                 + number + "]}"),
                (f"a number of {length} digits one object deep",
                 '{"operation":"check","source":"x","deep":{"n":'
                 + number + "}}"),
            ]
        )
    return texts


def mangled_requests() -> list[tuple[str, object]]:
    return _surrogate_family() + _digit_family()


def test_every_request_of_the_two_families_is_answered_and_the_rest_still_works():
    """Given a lone surrogate at twenty places in every string a request
    carries, and a run of 1 to 9000 digits in every integer position a
    request has, when each request is sent, then each comes back as one
    JSON answer carrying a status and the tool exits 0 -- and the
    programs this repository ships, and the longest literal the tool
    does read, are still answered completed.
    """
    cases = mangled_requests()
    texts = _json_number_family()
    assert len(cases) + len(texts) >= A_FUZZ_WORTH_THE_NAME, (
        f"the families hold {len(cases) + len(texts)} requests, fewer than "
        f"the {A_FUZZ_WORTH_THE_NAME} a fuzz needs to say anything."
    )

    broken = []
    for why, sent in texts:
        answer = ask_text(sent)
        if answer.crash is not None or answer.exit_code != 0:
            broken.append((why, repr(answer.crash)[:200], answer.exit_code))
            continue
        try:
            parsed = json.loads(answer.stdout)
        except (json.JSONDecodeError, ValueError):
            broken.append((why, "the answer was not JSON", answer.exit_code))
            continue
        if not isinstance(parsed, dict) or "status" not in parsed:
            broken.append((why, f"the answer carried no status: {parsed}", 0))

    for why, request in cases:
        answer = ask(request)
        if answer.crash is not None or answer.exit_code != 0:
            broken.append((why, repr(answer.crash)[:200], answer.exit_code))
            continue
        try:
            parsed = json.loads(answer.stdout)
        except (json.JSONDecodeError, ValueError):
            broken.append((why, "the answer was not JSON", answer.exit_code))
            continue
        if not isinstance(parsed, dict) or "status" not in parsed:
            broken.append((why, f"the answer carried no status: {parsed}", 0))

    assert not broken, (
        f"{len(broken)} of the {len(cases) + len(texts)} requests were not "
        "answered. The "
        f"first ten: {broken[:10]}. Every one of them is a client that reads a "
        "traceback instead of a refusal it can act on."
    )

    _assert_what_the_tool_answered_before_is_still_answered()


@DERANDOMIZED
@given(
    position=st.integers(min_value=0, max_value=4000),
    half=st.sampled_from(LONE_SURROGATES),
    field=st.sampled_from(("source", "function", "arguments", "operation")),
    operation=st.sampled_from(SOURCE_READING_OPERATIONS),
)
def test_a_lone_surrogate_anywhere_in_a_request_is_answered(
    position, half, field, operation
):
    """LAW2: wherever a character that cannot be written as UTF-8 stands
    in a text a request carries, the tool answers with one JSON response
    and exits 0; and when it stands in the source of an operation that
    reads source, the answer names the source field and says which
    character position cannot be written.
    """
    clock = _clock()
    request = {
        "operation": operation,
        "source": clock,
        "function": "step",
        "arguments": ["(Clock 1)", "(Tick)"],
    }
    if field == "source":
        request["source"] = _with_a_surrogate_at(clock, position, half)
    elif field == "function":
        request["function"] = _with_a_surrogate_at("step", position, half)
    elif field == "arguments":
        request["arguments"] = [_with_a_surrogate_at("(Clock 1)", position, half)]
    else:
        request["operation"] = _with_a_surrogate_at(operation, position, half)

    why = f"a {half!r} at {position} in the {field} field of a {operation} request"
    response = _answered(request, why)

    if field == "source":
        _assert_named_with_its_position(response, "source", clock, position, why)
    elif field == "arguments" and operation == "evaluate":
        _assert_named_with_its_position(
            response, "arguments[0]", "(Clock 1)", position, why
        )


def _assert_named_with_its_position(
    response: dict, field: str, text: str, position: int, why: str
) -> None:
    """The answer refuses exactly the named text of the request, and
    says which character of it cannot be written."""
    assert response["status"] == "invalid_input", f"{why}: {str(response)[:300]}"
    named = [
        entry for entry in response["diagnostics"]
        if entry.get("category") == "malformed_request"
        and entry.get("symbol") == field
    ]
    assert len(named) == 1, (
        f"{why}: {str(response)[:400]} carries {len(named)} refusals naming "
        f"{field!r}, expected 1. A client repairs the text the refusal names."
    )
    place = position % (len(text) + 1)
    assert f"position {place}" in named[0]["reason"], (
        f"{why}: the refusal says {named[0]['reason'][:200]!r}, which does "
        f"not say that the character at position {place} of {field} is the "
        "one that cannot be written."
    )


@DERANDOMIZED
@given(
    length=st.integers(min_value=1, max_value=6000),
    shape=st.sampled_from(("the body", "an example", "a pattern", "an argument")),
)
def test_a_run_of_digits_meets_the_limit_only_when_it_passes_it(length, shape):
    """LAW3: a run of digits of any length is answered with one JSON
    response and exit 0; the answer names the digit limit when, and only
    when, the run is longer than the limit.
    """
    literal = "9" * length
    if shape == "an argument":
        request = {
            "operation": "evaluate",
            "source": _clock(),
            "function": "valid-state",
            "arguments": [literal],
        }
    else:
        written = {
            "the body": _body_literal,
            "an example": _example_literal,
            "a pattern": _pattern_literal,
        }[shape]
        request = {"operation": "check", "source": written(literal)}

    why = f"a run of {length} digits as {shape}"
    response = _answered(request, why)

    if length > DIGIT_LIMIT:
        assert _names_the_limit(response), (
            f"{why} was answered {str(response)[:300]}, which does not name "
            f"the {DIGIT_LIMIT}-digit limit. A caller that must shorten its "
            "number is told the length this tool reads."
        )
    else:
        assert not _names_the_limit(response), (
            f"{why} met the digit limit: {str(response)[:300]}. A literal of "
            f"{DIGIT_LIMIT} digits or fewer is read, not refused."
        )


def _assert_what_the_tool_answered_before_is_still_answered() -> None:
    """The programs this repository ships, and a literal of exactly the
    length the tool reads, are all still answered completed: the two
    refusals above are about the half character and the over-long run of
    digits, and about nothing else.
    """
    for name, text in shipped_programs().items():
        response = _answered({"operation": "check", "source": text}, f"{name}, untouched")
        assert response["status"] == "completed", f"{name}: {str(response)[:300]}"

    longest = _answered(
        {"operation": "check", "source": _body_literal("9" * DIGIT_LIMIT)},
        f"a literal of exactly {DIGIT_LIMIT} digits",
    )
    assert longest["status"] == "completed", str(longest)[:300]
