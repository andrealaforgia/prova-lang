"""R3.P1 -- the crash search of R1 and R2, widened by the four families
that still ended in a failure of the tool: an integer the evaluator
computes but cannot write, a budget variable holding a run of digits no
reader turns into a number, a request whose own JSON nests thousands of
arrays deep, and half a character anywhere a request carries text.

Every case goes through the surface R1's fuzz uses: the command's own
entry point, with standard input and standard output replaced, so the
exit code and the printed text are the ones a caller would see. The
corpus is fixed -- the same requests every run -- and the generated laws
are derandomised, so a crash found once is caught again.

still passes if: the tool answered every request with one constant
refusal. The last test sends the programs this repository ships, a
product the tool does write, a budget a caller may lower and a request
nested as deep as the tool reads, and requires all of them to be
answered as before.
"""

from __future__ import annotations

import contextlib
import json
import os

from hypothesis import HealthCheck, given, settings, strategies as st

from _r1_mangled_requests import ask, ask_text, shipped_programs

# The two numbers this delivery declares, read here as a caller reads
# them from the manifest: the digits of an integer the tool writes into
# an answer, and how many arrays or objects a request may nest inside
# one another, counting the request object itself.
WRITTEN_DIGITS_LIMIT = 4000
REQUEST_NESTING_LIMIT = 64
WRITTEN_DIGITS_EXCEEDED = "written_integer_digits_exceeded"

# What a caller lowers a budget with, and the number this tool declares
# for the source it reads.
BUDGET_VARIABLE = "PROVA_BUDGET_INPUT_SIZE"
DECLARED_INPUT_SIZE = 1024 * 1024

# Half a character, both halves of a pair, as a client that decoded
# bytes badly sends them.
LONE_SURROGATES = ("\udccc", "\ud800")

# At least this many requests must be sent for the fixed corpus to be
# evidence of anything. Smaller than R1's 500 because every case here
# carries a whole program the tool runs, a request of thousands of
# characters, or a process environment; the generated laws below widen
# each family far past the corpus.
A_FUZZ_WORTH_THE_NAME = 150

DERANDOMIZED = settings(
    derandomize=True,
    max_examples=40,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow],
)


@contextlib.contextmanager
def _environment(**variables):
    """The process environment with these variables set, put back
    afterwards, so one law's budget never reaches the next."""
    kept = {name: os.environ.get(name) for name in variables}
    os.environ.update(variables)
    try:
        yield
    finally:
        for name, before in kept.items():
            if before is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = before


def _answered(request: object, why: str, text: str | None = None) -> dict:
    """The one JSON answer a request gets, or the reason it is not one."""
    answer = ask(request) if text is None else ask_text(text)
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
    assert parsed["status"] != "tool_failure", (
        f"{why} was answered as a failure of the tool: {str(parsed)[:300]}. "
        "Every one of these inputs is a request a caller can repair, so the "
        "answer says which limit or which field stopped it."
    )
    return parsed


def _texts_of(value: object) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        found: list[str] = []
        for key, held in value.items():
            found.extend(_texts_of(key))
            found.extend(_texts_of(held))
        return found
    if isinstance(value, list):
        found = []
        for held in value:
            found.extend(_texts_of(held))
        return found
    return []


def _assert_writable(response: dict, why: str) -> None:
    for text in _texts_of(response):
        try:
            text.encode("utf-8")
        except UnicodeEncodeError as half:
            raise AssertionError(
                f"{why}: the answer carries a text whose character at "
                f"position {half.start} cannot be written as UTF-8. A client "
                "that writes this answer out fails where the tool did not."
            ) from None


def _refusals(response: dict, category: str) -> list[dict]:
    return [
        entry
        for entry in (response.get("diagnostics") or [])
        if entry.get("category") == category
    ]


# --- the programs, requests and environments of the four families ---------

def multiplying(literal: str, times: int) -> str:
    body = literal
    for _ in range(times - 1):
        body = f"(* {body} {literal})"
    return (
        "(defn big\n"
        "  (sig () -> Int ! pure)\n"
        "  (examples (example (big) => 1))\n"
        f"  {body})\n"
    )


def nesting(depth: int) -> str:
    arrays = depth - 1
    if arrays == 0:
        return '{"operation": "discover"}'
    return '{"operation": "discover", "padding": ' + "[" * arrays + "]" * arrays + "}"


def _with_a_surrogate_at(text: str, position: int, half: str) -> str:
    place = position % (len(text) + 1)
    return text[:place] + half + text[place:]


BUDGET_TEXTS = (
    "1",
    "4096",
    "1048576",
    "1048577",
    "0001024",
    "",
    "nine",
    "9" * 8,
    "9" * 4299,
    "9" * 4300,
    "9" * 4301,
    "9" * 5000,
    "0" * 5000 + "5",
)


def _computed_integer_family() -> list[tuple[str, object]]:
    cases: list[tuple[str, object]] = []
    for digits in (1, 100, 1000):
        for times in range(1, 7):
            source = multiplying("9" * digits, times)
            cases.append(
                (f"evaluating a product of {digits * times} digits",
                 {"operation": "evaluate", "source": source, "function": "big",
                  "arguments": []})
            )
            cases.append(
                (f"running the examples of a product of {digits * times} digits",
                 {"operation": "examples", "source": source})
            )
    return cases


def _surrogate_family() -> list[tuple[str, object]]:
    clock = shipped_programs()["hour-clock"]
    places = [round(index * len(clock) / 9) for index in range(10)]
    cases: list[tuple[str, object]] = []
    for half in LONE_SURROGATES:
        for position in places:
            cases.append(
                (f"a surrogate at {position} of the source",
                 {"operation": "check",
                  "source": _with_a_surrogate_at(clock, position, half)})
            )
            cases.append(
                (f"a surrogate at {position} of the operation",
                 {"operation": _with_a_surrogate_at("check", position, half),
                  "source": clock})
            )
            cases.append(
                (f"a surrogate at {position} of the function",
                 {"operation": "evaluate", "source": clock,
                  "function": _with_a_surrogate_at("step", position, half),
                  "arguments": ["(Clock 1)", "(Tick)"]})
            )
            cases.append(
                (f"a surrogate at {position} of an argument",
                 {"operation": "evaluate", "source": clock, "function": "step",
                  "arguments": ["(Clock 1)",
                                _with_a_surrogate_at("(Tick)", position, half)]})
            )
            cases.append(
                (f"a surrogate at {position} of a field the tool does not read",
                 {"operation": "check", "source": clock,
                  "prova": _with_a_surrogate_at("i1", position, half)})
            )
    return cases


def test_every_request_of_the_four_families_is_answered_and_the_rest_still_works():
    """Given an integer of up to 6000 digits computed by a program, a
    budget variable holding up to 5001 characters, a request nesting up
    to 20000 arrays, and half a character at 10 places in every string a
    request carries, when each is sent through the command, then each
    comes back as one JSON answer carrying a status, the tool exits 0,
    and no answer carries a text a client cannot write -- and the
    programs this repository ships are still answered completed.
    """
    broken: list[tuple[str, str]] = []

    for why, request in _computed_integer_family() + _surrogate_family():
        try:
            response = _answered(request, why)
            _assert_writable(response, why)
        except AssertionError as refused:
            broken.append((why, str(refused)[:200]))

    for text in BUDGET_TEXTS:
        why = f"a budget variable holding {len(text)} characters"
        with _environment(**{BUDGET_VARIABLE: text}):
            try:
                _assert_writable(_answered({"operation": "discover"}, why), why)
            except AssertionError as refused:
                broken.append((why, str(refused)[:200]))

    for depth in (1, 2, 10, 63, 64, 65, 100, 1000, 20000):
        why = f"a request nesting {depth} arrays and objects"
        try:
            _answered(None, why, text=nesting(depth))
        except AssertionError as refused:
            broken.append((why, str(refused)[:200]))

    sent = (
        len(_computed_integer_family())
        + len(_surrogate_family())
        + len(BUDGET_TEXTS)
        + 9
    )
    assert sent >= A_FUZZ_WORTH_THE_NAME, (
        f"the four families hold {sent} requests, fewer than the "
        f"{A_FUZZ_WORTH_THE_NAME} a fuzz needs to say anything."
    )
    assert not broken, (
        f"{len(broken)} of the {sent} requests were not answered. The first "
        f"five: {broken[:5]}. Every one of them is a caller that reads a "
        "failure of the tool instead of a refusal it can act on."
    )

    _assert_what_the_tool_answered_before_is_still_answered()


def _assert_what_the_tool_answered_before_is_still_answered() -> None:
    """The programs this repository ships, a product the tool does
    write, a budget a caller may lower and a request nested as deep as
    the tool reads are all still answered as they were.
    """
    for name, text in shipped_programs().items():
        response = _answered({"operation": "check", "source": text}, f"{name}, untouched")
        assert response["status"] == "completed", f"{name}: {str(response)[:300]}"

    product = _answered(
        {"operation": "evaluate", "source": multiplying("9" * 1000, 4),
         "function": "big", "arguments": []},
        "a product of exactly 4000 digits",
    )
    assert product["status"] == "completed", str(product)[:300]
    assert int(product["result"]["value"]) == (10**1000 - 1) ** 4, (
        "a product of exactly the digits the tool writes came back as some "
        "other number."
    )

    with _environment(**{BUDGET_VARIABLE: "4096"}):
        lowered = _answered({"operation": "discover"}, "a budget lowered to 4096")
    assert lowered["status"] == "completed", str(lowered)[:300]

    at_the_limit = _answered(
        None, "a request nested as deep as the tool reads",
        text=nesting(REQUEST_NESTING_LIMIT),
    )
    assert at_the_limit["status"] == "completed", str(at_the_limit)[:300]


@DERANDOMIZED
@given(
    digits=st.sampled_from((1, 2, 97, 500, 1000)),
    times=st.integers(min_value=1, max_value=6),
    operation=st.sampled_from(("evaluate", "examples")),
)
def test_an_integer_of_any_size_is_written_or_refused_by_its_digits(
    digits, times, operation
):
    """LAW1: a program multiplying a run of nines by itself is answered
    with the exact product when the product has at most 4000 digits, and
    refused with the written-digit limit and the digits it reached when
    it has more; either way one JSON answer and exit 0.

    A run of `digits` nines raised to `times` has exactly
    `digits * times` digits: it is below 10 to that power and above a
    tenth of it, for every count this law draws.
    """
    source = multiplying("9" * digits, times)
    request = (
        {"operation": "evaluate", "source": source, "function": "big",
         "arguments": []}
        if operation == "evaluate"
        else {"operation": "examples", "source": source}
    )
    reached = digits * times
    why = f"{operation} of a product of {reached} digits"
    response = _answered(request, why)

    if reached > WRITTEN_DIGITS_LIMIT:
        refusals = _refusals(response, WRITTEN_DIGITS_EXCEEDED)
        assert len(refusals) == 1, (
            f"{why} was answered {str(response)[:300]}, which carries no one "
            "refusal about the digits the tool writes. A caller whose program "
            "computes a number too long for an answer is told so."
        )
        assert response["status"] == "resource_exhausted", str(response)[:300]
        assert (refusals[0].get("expected"), refusals[0].get("actual")) == (
            WRITTEN_DIGITS_LIMIT,
            reached,
        ), (
            f"{why}: the refusal says {refusals[0].get('expected')!r} and "
            f"{refusals[0].get('actual')!r}, not {WRITTEN_DIGITS_LIMIT} and "
            f"{reached}."
        )
    else:
        assert response["status"] == "completed", (
            f"{why} was answered {str(response)[:300]}. A product of "
            f"{reached} digits is inside what the tool writes."
        )
        if operation == "evaluate":
            assert int(response["result"]["value"]) == (10**digits - 1) ** times, (
                f"{why} came back as some other number than the product."
            )


@DERANDOMIZED
@given(text=st.sampled_from(BUDGET_TEXTS))
def test_a_budget_written_in_the_environment_is_read_or_refused(text):
    """LAW2: whatever a caller writes in a budget variable, the command
    answers one JSON response and exits 0; and it runs under that number
    only when the text writes a whole number no larger than the 1048576
    bytes this tool declares.
    """
    why = f"a budget variable holding {len(text)} characters"
    with _environment(**{BUDGET_VARIABLE: text}):
        response = _answered({"operation": "discover"}, why)

    significant = text.lstrip("0")
    a_number_the_tool_may_run_under = (
        text.isascii()
        and text.isdecimal()
        and len(significant) <= len(str(DECLARED_INPUT_SIZE))
        and int(significant or "0") <= DECLARED_INPUT_SIZE
    )
    if a_number_the_tool_may_run_under:
        assert response["status"] == "completed", (
            f"{why} ({text[:20]!r}) was answered {str(response)[:300]}: a "
            "number a caller may lower a budget to is read, not refused."
        )
    else:
        assert response["status"] == "invalid_input", (
            f"{why} ({text[:20]!r}) was answered {str(response)[:300]}: a text "
            "this tool cannot read as a budget leaves the caller believing it "
            "lowered one."
        )
        named = [
            entry for entry in _refusals(response, "malformed_request")
            if entry.get("symbol") == BUDGET_VARIABLE
        ]
        assert len(named) == 1, (
            f"{why}: {str(response)[:300]} names the variable to repair "
            f"{len(named)} times, expected 1."
        )


@DERANDOMIZED
@given(depth=st.integers(min_value=1, max_value=400))
def test_a_request_of_any_nesting_depth_is_answered(depth):
    """LAW3: a request is answered with one JSON response and exit 0
    however deeply its own JSON nests, and is refused for nesting when,
    and only when, it nests deeper than the 64 this tool reads.
    """
    why = f"a request nesting {depth} arrays and objects"
    response = _answered(None, why, text=nesting(depth))

    if depth > REQUEST_NESTING_LIMIT:
        assert response["status"] == "invalid_input", (
            f"{why} was answered {str(response)[:300]}."
        )
        named = [
            entry for entry in _refusals(response, "malformed_request")
            if "nest" in (entry.get("reason") or "")
        ]
        assert named, (
            f"{why} was answered {str(response)[:300]}, which does not say the "
            "request nests too deeply."
        )
    else:
        assert response["status"] == "completed", (
            f"{why} was answered {str(response)[:300]}: a request inside the "
            "nesting this tool reads is answered as any other."
        )


@DERANDOMIZED
@given(
    position=st.integers(min_value=0, max_value=4000),
    half=st.sampled_from(LONE_SURROGATES),
    field=st.sampled_from(("operation", "source", "function", "arguments")),
)
def test_a_surrogate_anywhere_leaves_an_answer_a_client_can_write(
    position, half, field
):
    """LAW4: wherever half a character stands in a text a request
    carries, the answer holds no text a client cannot write out again;
    and when it stands in the operation, the answer names the operation
    field and the character position.

    A budget variable holding such a character is observed by the
    acceptance tests through a real command: this process cannot hold
    one, because the environment of a running process is written in
    bytes and half a character has none.
    """
    clock = shipped_programs()["hour-clock"]
    request = {
        "operation": "evaluate",
        "source": clock,
        "function": "step",
        "arguments": ["(Clock 1)", "(Tick)"],
    }
    why = f"a {half!r} at {position} in the {field} of a request"

    if field == "operation":
        request["operation"] = _with_a_surrogate_at("evaluate", position, half)
    elif field == "source":
        request["source"] = _with_a_surrogate_at(clock, position, half)
    elif field == "function":
        request["function"] = _with_a_surrogate_at("step", position, half)
    else:
        request["arguments"] = [_with_a_surrogate_at("(Clock 1)", position, half)]

    response = _answered(request, why)
    _assert_writable(response, why)

    if field == "operation":
        assert response["status"] == "invalid_input", f"{why}: {str(response)[:300]}"
        named = [
            entry for entry in _refusals(response, "malformed_request")
            if entry.get("symbol") == "operation"
        ]
        assert len(named) == 1, (
            f"{why}: {str(response)[:400]} carries {len(named)} refusals naming "
            "the operation field, expected 1."
        )
        place = position % (len("evaluate") + 1)
        assert f"position {place}" in named[0]["reason"], (
            f"{why}: the refusal says {named[0]['reason'][:200]!r}, which does "
            f"not say that the character at position {place} is the one that "
            "cannot be written."
        )
