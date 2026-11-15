"""Shared fixtures for R1: the requests that used to end in a traceback,
and the answers a caller must get instead.

Every case here is paired with a control that the tool answers normally,
so a tool that refused everything would not pass: a refusal is only
evidence when the twin beside it is still accepted.

Not itself a test module (no `test_` prefix); pytest will not collect
it. The helpers drive only the `prova` command's real stdin/stdout
surface and read its exit code, because an exit code other than 0 and a
traceback on standard error are exactly what these tests exist to see.
No imports from src/prova.
"""

from __future__ import annotations

import json
import pathlib
import subprocess
from dataclasses import dataclass

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

# The fields of an answer a caller reads instead of the prose.
LOCATION = "location"
SYMBOL = "symbol"
EXPECTED = "expected"
ACTUAL = "actual"

INVALID_PROGRAM = "invalid_program"
INVALID_INPUT = "invalid_input"
UNAVAILABLE = "unavailable"
RESOURCE_EXHAUSTED = "resource_exhausted"

ARITY_MISMATCH = "arity_mismatch"
MALFORMED_REQUEST = "malformed_request"
NESTING_LIMIT_EXCEEDED = "nesting_limit_exceeded"
EVALUATION_DEPTH_EXCEEDED = "evaluation_depth_exceeded"
UNKNOWN_OPERATION = "unknown_operation"

# The name the manifest gives the limit on how deeply one form may stand
# inside another. A caller reads the number from the manifest under this
# name and meets the same name again in the refusal.
NESTING_LIMIT_NAME = "expression_nesting"

# The name the manifest gives the limit on how far a run of a program
# may stand inside itself.
EVALUATION_LIMIT_NAME = "evaluation_depth"


@dataclass(frozen=True)
class ToolRun:
    exit_code: int
    stdout: str
    stderr: str

    def response(self) -> dict:
        try:
            return json.loads(self.stdout)
        except (json.JSONDecodeError, ValueError):
            raise AssertionError(
                "the tool's answer is not JSON a caller can read, so there is no "
                f"outcome in it: it exited {self.exit_code} and printed "
                f"{self.stdout!r} on standard output and "
                f"{self.stderr[-800:]!r} on standard error. Every request gets "
                "one JSON answer; a traceback is not one. Make the code that "
                "read the request refuse it in a published category instead of "
                "letting the exception out."
            ) from None

    def assert_answered(self, why: str) -> dict:
        assert self.exit_code == 0, (
            f"the tool exited {self.exit_code} for {why}, not 0: a caller that "
            "reads the exit code learns the tool broke rather than that its "
            f"input did. Standard error held {self.stderr[-800:]!r}. Answer the "
            "request with a refusal in a published category and exit 0."
        )
        assert self.stderr.strip() == "", (
            f"the tool wrote {self.stderr[-800:]!r} on standard error for {why}: "
            "a caller reading only standard output would miss it, and a "
            "traceback there means an input decided control flow by raising. "
            "Refuse the input in the answer instead."
        )
        return self.response()


def run_text(sent: str) -> ToolRun:
    """One run of the command over exactly this text.

    The one place a request becomes the characters the command reads, so
    a test about text that no client library would write -- a number
    longer than a reader turns into a number, say -- sends it through
    the same surface as every other test.
    """
    proc = subprocess.run(
        ["prova"],
        input=sent,
        capture_output=True,
        text=True,
        timeout=30.0,
        check=False,
    )
    return ToolRun(proc.returncode, proc.stdout, proc.stderr)


def run(request: object) -> ToolRun:
    return run_text(json.dumps(request))


def answered(request: object, why: str) -> dict:
    return run(request).assert_answered(why)


def discover() -> dict:
    return answered({"prova": "i1", "operation": "discover"}, "the manifest")


# --- the programs this repository ships -----------------------------------

def hour_clock_source() -> str:
    return (REPO_ROOT / "examples" / "hour-clock.prova").read_text(encoding="utf-8")


def add_one_source() -> str:
    return (REPO_ROOT / "conformance" / "add-one.prova").read_text(encoding="utf-8")


def reservation_source() -> str:
    """The worked example SPEC.md publishes, read from SPEC.md itself."""
    text = (REPO_ROOT / "SPEC.md").read_text(encoding="utf-8")
    start = text.index("## Core conformance example")
    opening = text.index("```", start)
    body = text.index("\n", opening) + 1
    return text[body : text.index("```", body)]


def shipped_programs() -> dict[str, str]:
    return {
        "the hour clock": hour_clock_source(),
        "add one": add_one_source(),
        "the reservation example": reservation_source(),
    }


def without_character(text: str, index: int) -> str:
    return text[:index] + text[index + 1 :]


# --- nesting --------------------------------------------------------------

def deepest_nesting(text: str) -> int:
    """How deeply a form stands inside another in `text`, counted the way
    a reader counts it: the most parentheses open at once."""
    depth = most = 0
    for character in text:
        if character == "(":
            depth += 1
            most = max(most, depth)
        elif character == ")":
            depth = max(0, depth - 1)
    return most


def program_nested(depth: int) -> str:
    """A program whose deepest form stands `depth` forms inside the text.

    The body is a run of `not` around `true`, which the tool accepts at
    any depth it can read: nothing but the nesting makes it hard.
    """
    assert depth >= 5, "the wrapper alone already nests 4 deep"
    body = "(not " * (depth - 1) + "true" + ")" * (depth - 1)
    return (
        "(defn deeply-nested\n"
        "  (sig () -> Bool ! pure)\n"
        "  (examples (example (deeply-nested) => true))\n"
        f"  {body})\n"
    )


def chained_functions(count: int) -> str:
    """A legal program of `count` functions where each one calls the
    next and the last answers 1.

    Nothing in it is recursive: the calls run one way, down the chain,
    and every function declares the example that calls it. Only its
    length makes it hard to run.
    """
    written = []
    for place in range(count):
        body = f"(f{place + 1})" if place < count - 1 else "1"
        written.append(
            f"(defn f{place}\n"
            "  (sig () -> Int ! pure)\n"
            f"  (examples (example (f{place}) => 1))\n"
            f"  {body})"
        )
    return "\n".join(written) + "\n"


def published_evaluation_limit(manifest: dict) -> int:
    """How far the manifest says a run of a program may stand inside
    itself."""
    declared = (
        manifest["result"]
        .get("resource_limits", {})
        .get("limits", {})
        .get(EVALUATION_LIMIT_NAME)
    )
    assert isinstance(declared, dict) and isinstance(declared.get("maximum"), int), (
        f"the manifest publishes no {EVALUATION_LIMIT_NAME!r} limit with a "
        f"whole number maximum: {manifest['result'].get('resource_limits')}. A "
        "caller that generates a long chain of calls has no number to stay "
        "under, so it learns the limit by crashing into it."
    )
    return declared["maximum"]


def published_nesting_limit(manifest: dict) -> int:
    """The greatest nesting the manifest says the tool reads."""
    limits = manifest["result"].get("resource_limits", {})
    assert limits.get("enforced") is True, (
        f"the manifest says no resource limit is enforced: {limits}. A caller "
        "writing a generator has no number to stay under, so it learns the "
        "limit by meeting it. Publish the limit the tool enforces."
    )
    declared = limits.get("limits", {}).get(NESTING_LIMIT_NAME)
    assert isinstance(declared, dict) and isinstance(declared.get("maximum"), int), (
        f"the manifest publishes no {NESTING_LIMIT_NAME!r} limit with a whole "
        f"number maximum: {limits}. Publish the nesting limit as a number under "
        f"{NESTING_LIMIT_NAME!r}, the same name the refusal carries."
    )
    return declared["maximum"]


# --- reading an answer back -----------------------------------------------

def diagnostics(response: dict) -> list:
    return list(response.get("diagnostics") or [])


def categories(response: dict) -> list:
    return [entry.get("category") for entry in diagnostics(response)]


def the_refusal(response: dict, category: str, why: str) -> dict:
    """The single refusal of `category` the answer carries."""
    found = [e for e in diagnostics(response) if e.get("category") == category]
    assert len(found) == 1, (
        f"the answer for {why} carries {len(found)} refusals of category "
        f"{category!r}, expected exactly one: {response}. A caller acts on one "
        "named cause; none leaves it with nothing to repair and several leave "
        "it guessing which one it broke."
    )
    return found[0]


def assert_located(entry: dict, why: str) -> tuple[int, int]:
    place = entry.get(LOCATION)
    assert isinstance(place, dict) and place.get("line") and place.get("column"), (
        f"the refusal for {why} says where nowhere: {entry}. A reader of it has "
        "no line to open, so the refusal cannot be acted on. Carry the line and "
        "column the refusal stands at."
    )
    return place["line"], place["column"]


def assert_accepted(response: dict, why: str) -> dict:
    assert response.get("status") == "completed", (
        f"the control for {why} was refused: {response}. It differs from the "
        "refused case only in the one defect under observation, so a tool that "
        "refuses it refuses everything and the refusal beside it proves nothing."
    )
    return response
