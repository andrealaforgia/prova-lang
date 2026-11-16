"""Shared fixtures for R3: the four inputs that used to end in a failure
of the tool, and the answers a caller must get instead.

Not a test module (no `test_` prefix); pytest will not collect it. Every
helper drives the real `prova` command over its own stdin/stdout
surface, with the environment a caller would set, and reads its exit
code: a command that reports its own failure, or ends in a traceback, is
exactly what these tests exist to see. No imports from src/prova.
"""

from __future__ import annotations

import json
import os
import subprocess

from _r1_robustness_fixtures import ToolRun  # the same reading of one run

# What a caller reads about a value this tool will not write: the status
# every passed limit carries, the category of the refusal, and the name
# the limit is published and refused under.
RESOURCE_EXHAUSTED = "resource_exhausted"
INVALID_INPUT = "invalid_input"
MALFORMED_REQUEST = "malformed_request"
WRITTEN_DIGITS_EXCEEDED = "written_integer_digits_exceeded"
WRITTEN_DIGITS_NAME = "written_integer_digits"

# The numbers this delivery declares: the digits of an integer this tool
# writes into an answer, and how many arrays or objects a request may
# nest inside one another.
WRITTEN_DIGITS_LIMIT = 4000
REQUEST_NESTING_LIMIT = 64

# A literal of exactly the length this tool reads as one integer
# literal, so that every program below is inside R2's digit limit and
# only the value the tool computes is large.
A_THOUSAND_NINES = "9" * 1000
A_THOUSAND_NINES_VALUE = 10**1000 - 1

BUDGET_VARIABLE = "PROVA_BUDGET_INPUT_SIZE"
DECLARED_INPUT_SIZE = 1024 * 1024


BUDGET_TIME_VARIABLE = "PROVA_BUDGET_OPERATION_TIME"
DECLARED_OPERATION_TIME = 10_000


def product_of(literal: str, times: int) -> str:
    """The text of `literal` multiplied by itself `times` times."""
    body = literal
    for _ in range(times - 1):
        body = f"(* {body} {literal})"
    return body


def computing(body: str) -> str:
    """A program whose only function computes `body`, and nothing
    else."""
    return (
        "(defn big\n"
        "  (sig () -> Int ! pure)\n"
        "  (examples (example (big) => 1))\n"
        f"  {body})\n"
    )


def multiplying(literal: str, times: int) -> str:
    """A program whose only function multiplies `literal` by itself
    `times` times, and nothing else."""
    return computing(product_of(literal, times))


def send(request: object, environment: dict | None = None) -> ToolRun:
    """One request through the real command, with the environment a
    caller would have set."""
    return send_text(json.dumps(request), environment)


def send_text(text: str, environment: dict | None = None) -> ToolRun:
    """Exactly this text through the real command.

    The text is written as the bytes a client would send, surrogates
    passed through, so that a text no client library would write reaches
    the command as it stands.
    """
    running = dict(os.environ)
    running.update(environment or {})
    proc = subprocess.run(
        ["prova"],
        input=text.encode("utf-8", "surrogatepass"),
        capture_output=True,
        timeout=60.0,
        check=False,
        env=running,
    )
    return ToolRun(
        proc.returncode,
        proc.stdout.decode("utf-8", "surrogatepass"),
        proc.stderr.decode("utf-8", "replace"),
    )


def answered(request: object, why: str, environment: dict | None = None) -> dict:
    return send(request, environment).assert_answered(why)


def diagnostic_of(response: dict, category: str, why: str) -> dict:
    """The one refusal of `category` the answer carries."""
    found = [
        entry
        for entry in (response.get("diagnostics") or [])
        if entry.get("category") == category
    ]
    assert len(found) == 1, (
        f"{why}: the answer carries {len(found)} refusals of category "
        f"{category!r}, expected 1: {str(response)[:400]}. A caller reads what "
        "stopped the run from the category of the one refusal it gets."
    )
    return found[0]


def every_text_of(value: object) -> list[str]:
    """Every string anywhere inside an answer, keys and values alike."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        texts: list[str] = []
        for key, held in value.items():
            texts.extend(every_text_of(key))
            texts.extend(every_text_of(held))
        return texts
    if isinstance(value, list):
        texts = []
        for held in value:
            texts.extend(every_text_of(held))
        return texts
    return []


def assert_every_text_can_be_written(response: dict, why: str) -> None:
    """No text anywhere in the answer is one a client that decodes it
    cannot write out again."""
    for text in every_text_of(response):
        try:
            text.encode("utf-8")
        except UnicodeEncodeError as half_a_character:
            raise AssertionError(
                f"{why}: the answer carries a text whose character at "
                f"position {half_a_character.start} cannot be written as "
                f"UTF-8 ({half_a_character.reason}). A client that reads this "
                "answer and writes it to a file or sends it on fails where "
                "the tool did not: the tool must name the field that carried "
                "the text instead of copying it back."
            ) from None


def nesting(depth: int) -> str:
    """The text of a discover request carrying `depth` arrays or objects
    nested inside one another, counting the request object itself."""
    arrays = depth - 1
    if arrays == 0:
        return '{"operation": "discover"}'
    return '{"operation": "discover", "padding": ' + "[" * arrays + "]" * arrays + "}"
